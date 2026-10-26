"""
Daily pipeline orchestrator.

Chains together sourcing → selection → distillation → output.
Handles errors gracefully so the pipeline degrades rather than crashes.
"""

import dataclasses
import hashlib
import json
import logging
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Optional

import yaml

from slugify import slugify

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None  # SDK not required if using AgentRunner

from src.agent_runner import AgentRunner
from src.config import PipelineConfig
from src.distiller import BriefingDistiller
from src.machine import resolve_machine
from src.models import BriefingDocument, Paper, ScoredPaper, normalize_paper_id
from src.selector import PaperSelector
from src.sourcer import SourceManager

logger = logging.getLogger(__name__)


_ARXIV_ID_RE = re.compile(r"arXiv:(\d{4}\.\d{4,5}(?:v\d+)?)", re.IGNORECASE)


class SelectionHistory:
    """Tracks previously selected papers to prevent cross-run duplicates."""

    def __init__(self, history_path: Path, cooldown_days: int = 30):
        self.path = history_path
        self.cooldown_days = cooldown_days
        self._history: dict = self._load()
        self._seed_from_briefings()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Could not read selection history ({e}), starting fresh")
                return {}
        return {}

    def _seed_from_briefings(self) -> None:
        """Back-fill history from existing briefing files on disk.

        Scans YAML frontmatter for paper IDs so that briefings generated
        before dedup was implemented are still tracked.
        """
        briefing_dir = self.path.parent
        if not briefing_dir.exists():
            return

        seeded = 0
        for md_file in briefing_dir.glob("*_briefing.md"):
            try:
                meta = self._parse_briefing_frontmatter(md_file)
                if not meta:
                    continue
                paper_id = meta.get("paper_id")
                if paper_id and paper_id not in self._history:
                    selected_at = meta.get("date") or datetime.fromtimestamp(
                        md_file.stat().st_mtime, tz=timezone.utc
                    )
                    self._history[paper_id] = {
                        "title": meta.get("title", md_file.stem),
                        "selected_at": selected_at.isoformat(),
                        "seeded_from": md_file.name,
                    }
                    seeded += 1
            except Exception as e:
                logger.debug(f"Could not seed from {md_file.name}: {e}")

        if seeded:
            logger.info(f"Seeded {seeded} paper(s) into selection history from existing briefings")
            self._save()

    @staticmethod
    def _parse_briefing_frontmatter(md_file: Path) -> dict | None:
        """Parse YAML frontmatter from a briefing file, returning paper_id, title, and date.

        Returns None if the file has no valid frontmatter or no extractable paper ID.
        """
        text = md_file.read_text(encoding="utf-8")
        if not text.startswith("---"):
            return None

        end = text.find("---", 3)
        if end == -1:
            return None

        try:
            front = yaml.safe_load(text[3:end])
        except yaml.YAMLError:
            return None

        if not isinstance(front, dict):
            return None

        # Extract paper ID from 'source' or 'paper_url' field
        paper_id = None
        source = front.get("source", "")
        if source:
            m = _ARXIV_ID_RE.search(source)
            if m:
                paper_id = m.group(1)
            else:
                normalized = normalize_paper_id(source)
                if normalized != source:
                    paper_id = normalized

        if not paper_id:
            paper_url = front.get("paper_url", "")
            if paper_url:
                normalized = normalize_paper_id(paper_url)
                if normalized != paper_url:
                    paper_id = normalized

        if not paper_id:
            return None

        # Extract date — prefer briefing_date, then date, then None (caller uses mtime)
        selected_date = None
        for date_field in ("briefing_date", "date"):
            raw = front.get(date_field)
            if raw:
                try:
                    if isinstance(raw, datetime):
                        selected_date = raw.replace(tzinfo=timezone.utc)
                    elif isinstance(raw, date):
                        selected_date = datetime(raw.year, raw.month, raw.day, tzinfo=timezone.utc)
                    else:
                        selected_date = datetime.fromisoformat(str(raw)).replace(tzinfo=timezone.utc)
                    break
                except (ValueError, TypeError):
                    continue

        return {
            "paper_id": paper_id,
            "title": front.get("title", md_file.stem),
            "date": selected_date,
        }

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._history, indent=2, sort_keys=True), encoding="utf-8")

    def get_excluded_ids(self) -> set[str]:
        """Return normalized IDs of papers selected within the cooldown window."""
        if self.cooldown_days <= 0:
            return set()
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.cooldown_days)
        excluded = set()
        for paper_id, entry in self._history.items():
            try:
                selected_at = datetime.fromisoformat(entry["selected_at"])
                if selected_at > cutoff:
                    excluded.add(paper_id)
            except (KeyError, ValueError):
                excluded.add(paper_id)  # Malformed entry — exclude conservatively
        return excluded

    def record(self, paper: "Paper") -> None:
        """Record a paper as selected."""
        normalized = normalize_paper_id(paper.id)
        self._history[normalized] = {
            "title": paper.title,
            "selected_at": datetime.now(timezone.utc).isoformat(),
        }
        self._save()
        logger.info(f"Recorded selection: {normalized}")

    def contains(self, paper_id: str) -> bool:
        """Return True if a paper with this ID has ever been recorded.

        Normalizes the input so callers can pass raw ArXiv URLs, prefixed IDs,
        or bare IDs interchangeably. Membership is independent of the cooldown
        window — for cooldown-aware filtering use `get_excluded_ids()`.
        """
        return normalize_paper_id(paper_id) in self._history


RUN_RECORD_FILE = "run_history.jsonl"
_REPO_ROOT = Path(__file__).resolve().parent.parent


def _config_sha256(config: PipelineConfig) -> str:
    """Hash the effective config as canonical JSON, without the API key, the output folder and the log level."""
    data = dataclasses.asdict(config)
    for key in ("anthropic_api_key", "output_dir", "log_level"):  # a secret, a place, a volume: none shapes the briefing
        data.pop(key, None)
    return hashlib.sha256(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()


def _git_sha(root: Path = _REPO_ROOT) -> Optional[str]:
    """Short HEAD sha read from .git's own files, or None on any failure.

    No git binary: the App image has none, and the first tick's record read None.
    """
    try:
        git = root / ".git"
        head = (git / "HEAD").read_text().strip()
        if head.startswith("ref: "):
            ref = head[5:]
            if (git / ref).exists():
                head = (git / ref).read_text().strip()
            else:  # packed after a gc
                head = next(
                    line.split()[0]
                    for line in (git / "packed-refs").read_text().splitlines()
                    if line.endswith(" " + ref)
                )
        return head[:7] or None
    except Exception:
        return None


class PipelineResult:
    """Encapsulates the outcome of a pipeline run."""

    def __init__(
        self,
        status: str,
        selected_paper: Optional[ScoredPaper] = None,
        briefing: Optional[BriefingDocument] = None,
        briefing_path: Optional[Path] = None,
        papers_fetched: int = 0,
        articles_fetched: int = 0,
        error: Optional[str] = None,
        backend: str = "",
        machine: str = "",
        scoring_model: Optional[str] = None,
        distill_model: Optional[str] = None,
        started_at: Optional[datetime] = None,
        duration_s: float = 0.0,
        top_candidates: Optional[list[ScoredPaper]] = None,
        slack_ts: Optional[str] = None,
        slack_error: Optional[str] = None,
    ):
        self.status = status
        self.selected_paper = selected_paper
        self.briefing = briefing
        self.briefing_path = briefing_path
        self.papers_fetched = papers_fetched
        self.articles_fetched = articles_fetched
        self.error = error
        self.backend = backend
        self.machine = machine
        self.scoring_model = scoring_model
        self.distill_model = distill_model
        self.started_at = started_at
        self.duration_s = duration_s
        self.top_candidates = top_candidates if top_candidates is not None else []
        self.slack_ts = slack_ts
        self.slack_error = slack_error

    @property
    def success(self) -> bool:
        return self.status == "success"

    @property
    def partial(self) -> bool:
        return self.status == "partial"

    def __str__(self) -> str:
        if self.success:
            return (
                f"Pipeline SUCCESS\n"
                f"  Papers fetched: {self.papers_fetched}\n"
                f"  Articles fetched: {self.articles_fetched}\n"
                f"  Selected: {self.selected_paper}\n"
                f"  Briefing: {self.briefing}\n"
                f"  Saved to: {self.briefing_path}"
            )
        if self.partial:
            return (
                f"Pipeline PARTIAL — paper selected but briefing failed\n"
                f"  Papers fetched: {self.papers_fetched}\n"
                f"  Articles fetched: {self.articles_fetched}\n"
                f"  Selected: {self.selected_paper}\n"
                f"  Briefing: None (not recorded for dedup — paper remains available for retry)\n"
                f"  Reason: {self.error or 'distillation returned no content'}"
            )
        return f"Pipeline FAILED: {self.error}"


class DailyPipeline:
    """
    Orchestrates the full research podcast pipeline.

    Usage:
        config = PipelineConfig.load()
        pipeline = DailyPipeline(config)
        result = pipeline.run()
    """

    def __init__(
        self,
        config: PipelineConfig,
        backend: str = "auto",
        deliverer: Optional[Callable[[PipelineResult], Optional[str]]] = None,
    ):
        self.config = config
        self.backend = backend
        self.deliverer = deliverer
        self._agent_runner: Optional[AgentRunner] = None
        self._setup_logging()

        # Resolve backend: api, agent, keyword-only, or auto
        claude_client, agent_runner = self._resolve_backend(backend)
        if claude_client is not None:
            self.resolved_backend = "api"
            self.scoring_model, self.distill_model = config.claude.scoring_model, config.claude.model
        elif agent_runner is not None:
            self.resolved_backend = "agent"
            self._agent_runner = agent_runner
            self.scoring_model = self.distill_model = None  # the CLI reports the model per run (task 1.9)
        else:
            self.resolved_backend = "keyword-only"
            self.scoring_model = self.distill_model = None

        # Initialize pipeline stages
        self.source_manager = SourceManager(config)
        self.selector = PaperSelector(config, claude_client=claude_client, agent_runner=agent_runner)

        # Distiller requires at least one Claude backend; keyword-only mode skips distillation
        self._has_claude_backend = claude_client is not None or agent_runner is not None
        if self._has_claude_backend:
            self.distiller = BriefingDistiller(config, claude_client=claude_client, agent_runner=agent_runner)
        else:
            self.distiller = None
            logger.warning("No Claude backend available — distillation will be skipped")

    def _resolve_backend(self, backend: str) -> tuple[Optional["Anthropic"], Optional[AgentRunner]]:
        """
        Resolve which Claude backend to use.

        Fallback chain (auto mode):
          0. Machine roster preference (machines.<host>.backend in
             config/project.yaml), when that backend is available
          1. API key available → Anthropic SDK
          2. Claude CLI available → AgentRunner
          3. Neither → keyword-only scoring, no distillation

        The roster preference is advisory: an unavailable or unknown
        preference logs a warning and falls through to the chain. An
        explicit --backend flag never reaches this branch and so outranks
        the roster.

        Args:
            backend: One of "auto", "api", "agent", "keyword-only".

        Returns:
            Tuple of (claude_client or None, agent_runner or None).
        """
        if backend == "keyword-only":
            logger.info("Backend: keyword-only (no Claude scoring or distillation)")
            return None, None

        if backend == "api":
            if not self.config.anthropic_api_key:
                raise RuntimeError("--backend api requires ANTHROPIC_API_KEY to be set")
            logger.info("Backend: Anthropic SDK (API key)")
            return Anthropic(api_key=self.config.anthropic_api_key), None

        if backend == "agent":
            if not self.config.agent_runner.enabled:
                raise RuntimeError("--backend agent requested but agent_runner.enabled is false in config")
            runner = AgentRunner(self.config)
            if not runner.is_available():
                raise RuntimeError("--backend agent requires 'claude' CLI on PATH")
            logger.info("Backend: AgentRunner (Claude Code CLI)")
            return None, runner

        # auto: machine roster preference first, then API, then agent, then keyword-only
        machine = resolve_machine()
        if machine.backend == "api":
            if self.config.anthropic_api_key:
                logger.info(f"Backend (auto): Anthropic SDK (machine roster: {machine.name})")
                return Anthropic(api_key=self.config.anthropic_api_key), None
            logger.warning(
                f"Backend (auto): machine roster ({machine.name}) prefers api but "
                "ANTHROPIC_API_KEY is not set; falling through to detection"
            )
        elif machine.backend == "agent":
            if self.config.agent_runner.enabled:
                runner = AgentRunner(self.config)
                if runner.is_available():
                    logger.info(f"Backend (auto): AgentRunner (machine roster: {machine.name})")
                    return None, runner
            logger.warning(
                f"Backend (auto): machine roster ({machine.name}) prefers agent but "
                "the Claude CLI is unavailable; falling through to detection"
            )
        elif machine.backend:
            logger.warning(
                f"Backend (auto): machine roster ({machine.name}) names unknown backend "
                f"'{machine.backend}' (expected api or agent); ignoring"
            )

        if self.config.anthropic_api_key:
            logger.info("Backend (auto): Anthropic SDK (API key found)")
            return Anthropic(api_key=self.config.anthropic_api_key), None

        if self.config.agent_runner.enabled:
            runner = AgentRunner(self.config)
            if runner.is_available():
                logger.info("Backend (auto): AgentRunner (Claude Code CLI detected)")
                return None, runner

        logger.warning("Backend (auto): No Claude backend available — keyword-only mode")
        return None, None

    def run(self, paper_override: Optional[Paper] = None, dedup: bool = True) -> PipelineResult:
        """
        Execute the full pipeline, deliver the result, and write the run record.

        Args:
            paper_override: Skip sourcing/selection and distill this paper directly.
            dedup: If True, skip papers that were selected in recent runs.

        Returns:
            PipelineResult with status, outputs, run metadata, and any errors.
        """
        started_at = datetime.now(timezone.utc)
        result = self._run(paper_override, dedup)
        result.started_at = started_at
        result.backend = self.resolved_backend
        try:
            result.duration_s = round((datetime.now(timezone.utc) - started_at).total_seconds(), 3)
            result.machine = resolve_machine().name
            result.scoring_model = self.scoring_model
            result.distill_model = self.distill_model
            if self._agent_runner is not None:
                result.scoring_model = self._agent_runner.last_score_model or self.scoring_model
                result.distill_model = self._agent_runner.last_distill_model or self.distill_model

            if self.deliverer is not None:
                try:
                    result.slack_ts = self.deliverer(result)
                except Exception as e:
                    result.slack_error = str(e)
                    logger.warning(f"Delivery failed: {e}")
        finally:
            # D5: one record line per run, whatever happened above it.
            self._write_run_record(result)
        return result

    def _write_run_record(self, result: PipelineResult) -> None:
        """Append one JSON line to run_history.jsonl; a failure only warns."""
        sel = result.selected_paper
        record = {
            "date": result.started_at.strftime("%Y-%m-%d"),
            "started_at": result.started_at.isoformat(),
            "duration_s": result.duration_s,
            "status": result.status,
            "backend": result.backend,
            "machine": result.machine,
            "scoring_model": result.scoring_model,
            "distill_model": result.distill_model,
            "selected_id": sel.paper.id if sel else None,
            "score": sel.score if sel else None,
            "top_candidates": [
                {"id": c.paper.id, "title": c.paper.title, "score": c.score}
                for c in result.top_candidates
            ],
            "briefing_path": str(result.briefing_path) if result.briefing_path else None,
            "words": result.briefing.word_count if result.briefing else None,
            "papers_fetched": result.papers_fetched,
            "articles_fetched": result.articles_fetched,
            "error": result.error,
            "slack_ts": result.slack_ts,
            "slack_error": result.slack_error,
            "git_sha": _git_sha(),
            "config_sha256": _config_sha256(self.config),
        }
        try:
            output_dir = Path(self.config.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            with open(output_dir / RUN_RECORD_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            logger.warning(f"Could not write run record: {e}")

    def _run(self, paper_override: Optional[Paper] = None, dedup: bool = True) -> PipelineResult:
        """
        Run the stages and build the result.

        Args:
            paper_override: Skip sourcing/selection and distill this paper directly.
            dedup: If True, skip papers that were selected in recent runs.

        Returns:
            PipelineResult with status, outputs, and any errors.
        """
        logger.info("=" * 60)
        logger.info("Research Podcast Pipeline — Starting")
        logger.info(f"Time: {datetime.now(timezone.utc).isoformat()}")
        logger.info("=" * 60)

        # Load selection history for dedup
        history_path = Path(self.config.output_dir) / ".selection_history.json"
        history = SelectionHistory(history_path, self.config.dedup_cooldown_days)

        try:
            if paper_override:
                # Skip sourcing and selection
                logger.info(f"Using paper override: {paper_override.title[:80]}")
                selected = ScoredPaper(paper=paper_override, score=1.0, reasoning="Manual override")
                papers_count, articles_count = 0, 0
                candidates: list[ScoredPaper] = []
            else:
                # Stage 1: Source and select
                exclude_ids = history.get_excluded_ids() if dedup else set()
                candidates, papers_count, articles_count = self._source_and_select(exclude_ids)
                selected = candidates[0]

            # Stage 2: Distill (skipped in keyword-only mode)
            briefing = self._distill(selected.paper)

            # Stage 3: Save (only if briefing was generated)
            briefing_path = None
            if briefing:
                briefing_path = self._save_briefing(briefing)

            # Determine outcome:
            #   - briefing produced → success, record for dedup
            #   - no distiller configured (keyword-only) → success, record for dedup
            #     (selection was intentional even though no briefing was expected)
            #   - distiller configured but no briefing → partial, do NOT record
            #     (paper stays available for retry on the next run)
            briefing_expected = self.distiller is not None
            if briefing is not None or not briefing_expected:
                history.record(selected.paper)
                status = "success"
                error_reason = None
            else:
                status = "partial"
                # Surface the specific reason the distiller captured (timeout,
                # validation failure, SDK error) instead of a generic message.
                error_reason = (
                    self.distiller.last_error
                    if self.distiller and self.distiller.last_error
                    else "distillation returned no content"
                )

            result = PipelineResult(
                status=status,
                selected_paper=selected,
                briefing=briefing,
                briefing_path=briefing_path,
                papers_fetched=papers_count,
                articles_fetched=articles_count,
                error=error_reason,
                top_candidates=candidates,
            )

            logger.info("=" * 60)
            logger.info(str(result))
            logger.info("=" * 60)
            return result

        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            return PipelineResult(status="error", error=str(e))

    def _source_and_select(self, exclude_ids: set[str] | None = None) -> tuple[list[ScoredPaper], int, int]:
        """Source papers and return the scored top candidates, best first."""
        logger.info("Stage 1: Sourcing papers and articles...")
        papers, articles = self.source_manager.fetch_all()

        if not papers and not articles:
            raise RuntimeError("No papers or articles found from any source. Check your network and config.")

        logger.info(f"Sourced {len(papers)} papers and {len(articles)} articles")

        logger.info("Stage 2: Selecting best paper...")
        scored = self.selector.select_best(papers, articles, top_k=self.config.selector.top_k_for_claude, exclude_ids=exclude_ids)

        if not scored:
            raise RuntimeError("No papers scored above threshold. Try broadening focus keywords.")

        return scored, len(papers), len(articles)

    def _distill(self, paper: Paper) -> Optional[BriefingDocument]:
        """Generate the briefing document. Returns None if no Claude backend."""
        if self.distiller is None:
            logger.warning("Skipping distillation — no Claude backend available")
            return None
        logger.info("Stage 3: Distilling briefing document...")
        return self.distiller.distill(paper)

    def _save_briefing(self, briefing: BriefingDocument) -> Path:
        """Save the briefing to the output directory."""
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Filename: YYMMDD_paper-slug.md (format configurable via pipeline.date_format)
        date_str = briefing.generated_at.strftime(self.config.date_format)
        title_slug = slugify(briefing.source_paper.title[:60])
        filename = f"{date_str}_{title_slug}_briefing.md"

        filepath = output_dir / filename
        filepath.write_text(briefing.content, encoding="utf-8")

        logger.info(f"Briefing saved: {filepath}")
        return filepath

    def health_check(self) -> dict:
        """Check connectivity to all external services.

        Returns a dict of service to True, False, or None when the check is skipped.
        """
        logger.info("Running health checks...")

        results = self.source_manager.health_check()

        # Check Claude API (only if API key is available)
        if self.config.anthropic_api_key and Anthropic is not None:
            try:
                client = Anthropic(api_key=self.config.anthropic_api_key)
                client.messages.create(
                    model=self.config.claude.scoring_model,
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hello"}],
                )
                results["claude_api"] = True
            except Exception as e:
                results["claude_api"] = False
                logger.error(f"Claude API health check failed: {e}")
        else:
            results["claude_api"] = None  # skipped
            logger.info("Claude API: skipped (no API key)")

        # Check AgentRunner (Claude Code CLI); skipped on a box the roster puts on the API
        if resolve_machine().backend == "api":
            results["claude_cli"] = None
            logger.info("Claude CLI: skipped (roster backend is api)")
        else:
            runner = AgentRunner(self.config)
            results["claude_cli"] = runner.is_available()
            if results["claude_cli"]:
                logger.info("Claude CLI: available")
            else:
                logger.info("Claude CLI: not available")

        for service, healthy in results.items():
            status = "SKIPPED" if healthy is None else "OK" if healthy else "FAILED"
            logger.info(f"  {service}: {status}")

        return results

    def _setup_logging(self) -> None:
        """Configure logging for the pipeline."""
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)

        # Root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        # Console handler
        if not root_logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(log_level)
            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%H:%M:%S",
            )
            handler.setFormatter(formatter)
            root_logger.addHandler(handler)
