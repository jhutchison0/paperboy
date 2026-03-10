"""
Daily pipeline orchestrator.

Chains together sourcing → selection → distillation → output.
Handles errors gracefully so the pipeline degrades rather than crashes.
"""

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from anthropic import Anthropic
from slugify import slugify

from src.config import PipelineConfig
from src.distiller import BriefingDistiller
from src.models import BriefingDocument, Paper, ScoredPaper
from src.selector import PaperSelector
from src.sourcer import SourceManager

logger = logging.getLogger(__name__)


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
        return f"Pipeline FAILED: {self.error}"


class DailyPipeline:
    """
    Orchestrates the full research podcast pipeline.

    Usage:
        config = PipelineConfig.load()
        pipeline = DailyPipeline(config)
        result = pipeline.run()
    """

    def __init__(self, config: PipelineConfig):
        self.config = config
        self._setup_logging()

        # Initialize Claude client
        self.claude = Anthropic(api_key=config.anthropic_api_key)

        # Initialize pipeline stages
        self.source_manager = SourceManager(config)
        self.selector = PaperSelector(config, self.claude)
        self.distiller = BriefingDistiller(config, self.claude)

    def run(self, paper_override: Optional[Paper] = None) -> PipelineResult:
        """
        Execute the full pipeline.

        Args:
            paper_override: Skip sourcing/selection and distill this paper directly.
                           Useful for testing or manually choosing a paper.

        Returns:
            PipelineResult with status, outputs, and any errors.
        """
        logger.info("=" * 60)
        logger.info("Research Podcast Pipeline — Starting")
        logger.info(f"Time: {datetime.now(timezone.utc).isoformat()}")
        logger.info("=" * 60)

        try:
            if paper_override:
                # Skip sourcing and selection
                logger.info(f"Using paper override: {paper_override.title[:80]}")
                selected = ScoredPaper(paper=paper_override, score=1.0, reasoning="Manual override")
                papers_count, articles_count = 0, 0
            else:
                # Stage 1: Source
                selected, papers_count, articles_count = self._source_and_select()

            # Stage 2: Distill
            briefing = self._distill(selected.paper)

            # Stage 3: Save
            briefing_path = self._save_briefing(briefing)

            result = PipelineResult(
                status="success",
                selected_paper=selected,
                briefing=briefing,
                briefing_path=briefing_path,
                papers_fetched=papers_count,
                articles_fetched=articles_count,
            )

            logger.info("=" * 60)
            logger.info(str(result))
            logger.info("=" * 60)
            return result

        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            return PipelineResult(status="error", error=str(e))

    def _source_and_select(self) -> tuple[ScoredPaper, int, int]:
        """Source papers and select the best one."""
        logger.info("Stage 1: Sourcing papers and articles...")
        papers, articles = self.source_manager.fetch_all()

        if not papers and not articles:
            raise RuntimeError("No papers or articles found from any source. Check your network and config.")

        logger.info(f"Sourced {len(papers)} papers and {len(articles)} articles")

        logger.info("Stage 2: Selecting best paper...")
        scored = self.selector.select_best(papers, articles, top_k=1)

        if not scored:
            raise RuntimeError("No papers scored above threshold. Try broadening focus keywords.")

        return scored[0], len(papers), len(articles)

    def _distill(self, paper: Paper) -> BriefingDocument:
        """Generate the briefing document."""
        logger.info("Stage 3: Distilling briefing document...")
        return self.distiller.distill(paper)

    def _save_briefing(self, briefing: BriefingDocument) -> Path:
        """Save the briefing to the output directory."""
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Filename: YYYY-MM-DD_paper-slug.md
        date_str = briefing.generated_at.strftime("%Y-%m-%d")
        title_slug = slugify(briefing.source_paper.title[:60])
        filename = f"{date_str}_{title_slug}.md"

        filepath = output_dir / filename
        filepath.write_text(briefing.content, encoding="utf-8")

        logger.info(f"Briefing saved: {filepath}")
        return filepath

    def health_check(self) -> dict:
        """Check connectivity to all external services."""
        logger.info("Running health checks...")

        results = self.source_manager.health_check()

        # Check Claude API
        try:
            response = self.claude.messages.create(
                model=self.config.claude.scoring_model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}],
            )
            results["claude_api"] = True
        except Exception as e:
            results["claude_api"] = False
            logger.error(f"Claude API health check failed: {e}")

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
