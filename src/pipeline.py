"""
Daily pipeline orchestrator.

Chains together sourcing → selection → distillation → output.
Handles errors gracefully so the pipeline degrades rather than crashes.
"""

import json
import logging
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import yaml

from slugify import slugify

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None  # SDK not required if using AgentRunner

from src.agent_runner import AgentRunner
from src.config import PipelineConfig
from src.distiller import BriefingDistiller
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
    ):
        self.status = status
        self.selected_paper = selected_paper
        self.briefing = briefing
        self.briefing_path = briefing_path
        self.papers_fetched = papers_fetched
        self.articles_fetched = articles_fetched
        self.error = error

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

    def __init__(self, config: PipelineConfig, backend: str = "auto"):
        self.config = config
        self.backend = backend
        self._setup_logging()

        # Resolve backend: api, agent, keyword-only, or auto
        claude_client, agent_runner = self._resolve_backend(backend)

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
          1. API key available → Anthropic SDK
          2. Claude CLI available → AgentRunner
          3. Neither → keyword-only scoring, no distillation

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

        # auto: try API first, then agent, then keyword-only
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
        Execute the full pipeline.

        Args:
            paper_override: Skip sourcing/selection and distill this paper directly.
                           Useful for testing or manually choosing a paper.
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
            else:
                # Stage 1: Source and select
                exclude_ids = history.get_excluded_ids() if dedup else set()
                selected, papers_count, articles_count = self._source_and_select(exclude_ids)

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
            )

            logger.info("=" * 60)
            logger.info(str(result))
            logger.info("=" * 60)
            return result

        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            return PipelineResult(status="error", error=str(e))

    def _source_and_select(self, exclude_ids: set[str] | None = None) -> tuple[ScoredPaper, int, int]:
        """Source papers and select the best one."""
        logger.info("Stage 1: Sourcing papers and articles...")
        papers, articles = self.source_manager.fetch_all()

        if not papers and not articles:
            raise RuntimeError("No papers or articles found from any source. Check your network and config.")

        logger.info(f"Sourced {len(papers)} papers and {len(articles)} articles")

        logger.info("Stage 2: Selecting best paper...")
        scored = self.selector.select_best(papers, articles, top_k=1, exclude_ids=exclude_ids)

        if not scored:
            raise RuntimeError("No papers scored above threshold. Try broadening focus keywords.")

        return scored[0], len(papers), len(articles)

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
        """Check connectivity to all external services."""
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
            results["claude_api"] = False
            logger.info("Claude API: skipped (no API key)")

        # Check AgentRunner (Claude Code CLI)
        runner = AgentRunner(self.config)
        results["claude_cli"] = runner.is_available()
        if results["claude_cli"]:
            logger.info("Claude CLI: available")
        else:
            logger.info("Claude CLI: not available")

        for service, healthy in results.items():
            status = "OK" if healthy else "FAILED"
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
