"""
Tests for pipeline outcome reporting and dedup-history side effects.

The pipeline must report honest status:
  - success: briefing produced (or keyword-only mode where none was expected)
  - partial: distiller was configured but produced no briefing
  - error: an exception was raised

And it must NOT record a selection in the dedup history when distillation
failed — otherwise the paper gets blocked for the cooldown window despite
never producing a briefing.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import PipelineConfig
from src.distiller import BriefingDistiller
from src.models import BriefingDocument, Paper, ScoredPaper
from src.pipeline import DailyPipeline, PipelineResult, SelectionHistory


def _make_paper():
    return Paper(
        id="2605.18747v1",
        title="Code as Agent Harness",
        authors=["Author A"],
        abstract="Abstract.",
        published_date=datetime(2026, 5, 18),
        url="http://arxiv.org/abs/2605.18747",
        categories=["cs.AI"],
        pdf_url="",
    )


def _make_briefing(paper):
    return BriefingDocument(
        title="Research Briefing: Test",
        source_paper=paper,
        generated_at=datetime.now(timezone.utc),
        content="word " * 100,
    )


@pytest.fixture
def config(tmp_path):
    """Config pointing output to a temp dir so history files don't leak."""
    cfg = PipelineConfig.load()
    cfg.anthropic_api_key = ""
    cfg.output_dir = str(tmp_path)
    return cfg


class TestPipelineResultStatus:
    def test_success_status(self):
        r = PipelineResult(status="success")
        assert r.success is True
        assert r.partial is False

    def test_partial_status(self):
        r = PipelineResult(status="partial", error="distillation returned no content")
        assert r.success is False
        assert r.partial is True
        assert "PARTIAL" in str(r)
        assert "not recorded for dedup" in str(r)

    def test_error_status(self):
        r = PipelineResult(status="error", error="boom")
        assert r.success is False
        assert r.partial is False
        assert "FAILED" in str(r)


class TestPipelineRunOutcomes:
    """End-to-end: pipeline.run() returns the right status and side effects."""

    def _build_pipeline(self, config, has_distiller=True):
        pipeline = DailyPipeline(config, backend="keyword-only")
        # Skip sourcing — drive the run via paper_override
        if has_distiller:
            pipeline.distiller = MagicMock()
        else:
            pipeline.distiller = None
        return pipeline

    def test_success_when_distiller_produces_briefing(self, config):
        paper = _make_paper()
        pipeline = self._build_pipeline(config, has_distiller=True)
        pipeline.distiller.distill.return_value = _make_briefing(paper)

        result = pipeline.run(paper_override=paper)

        assert result.status == "success"
        assert result.success is True
        assert result.briefing is not None
        # Selection should be recorded
        history_path = Path(config.output_dir) / ".selection_history.json"
        assert SelectionHistory(history_path, 30).contains(paper.id)

    def test_partial_when_distiller_returns_none(self, config):
        paper = _make_paper()
        pipeline = self._build_pipeline(config, has_distiller=True)
        pipeline.distiller.distill.return_value = None  # simulate timeout/failure

        result = pipeline.run(paper_override=paper)

        assert result.status == "partial"
        assert result.partial is True
        assert result.success is False
        assert result.briefing is None
        assert result.briefing_path is None
        assert result.error is not None

    def test_partial_does_not_record_selection_in_history(self, config):
        """Critical bug fix: a failed distillation must not poison the dedup cache."""
        paper = _make_paper()
        pipeline = self._build_pipeline(config, has_distiller=True)
        pipeline.distiller.distill.return_value = None

        pipeline.run(paper_override=paper)

        # History file should either not exist or not contain the failed paper
        history_path = Path(config.output_dir) / ".selection_history.json"
        if history_path.exists():
            history = SelectionHistory(history_path, 30)
            assert not history.contains(paper.id), (
                "Failed distillation must NOT be recorded — paper should remain "
                "available for retry on the next run."
            )

    def test_keyword_only_mode_still_records_selection(self, config):
        """Keyword-only intentionally produces no briefing — record selection as normal."""
        paper = _make_paper()
        pipeline = self._build_pipeline(config, has_distiller=False)

        result = pipeline.run(paper_override=paper)

        assert result.status == "success"
        assert result.briefing is None
        history_path = Path(config.output_dir) / ".selection_history.json"
        assert history_path.exists()
        assert SelectionHistory(history_path, 30).contains(paper.id)

    def test_partial_error_surfaces_distiller_last_error(self, config):
        """PipelineResult.error must carry the distiller's specific failure
        reason (timeout / validation / SDK error), not a generic placeholder."""
        paper = _make_paper()
        pipeline = self._build_pipeline(config, has_distiller=True)
        # Simulate a distiller that captured a specific reason during distill()
        pipeline.distiller.distill.return_value = None
        pipeline.distiller.last_error = "distill_paper timed out after 2 attempt(s); final timeout was 900s"

        result = pipeline.run(paper_override=paper)

        assert result.status == "partial"
        assert result.error == "distill_paper timed out after 2 attempt(s); final timeout was 900s"

    def test_partial_error_falls_back_when_distiller_has_no_reason(self, config):
        """If the distiller doesn't set last_error, the pipeline uses a generic fallback."""
        paper = _make_paper()
        pipeline = self._build_pipeline(config, has_distiller=True)
        pipeline.distiller.distill.return_value = None
        pipeline.distiller.last_error = None

        result = pipeline.run(paper_override=paper)

        assert result.status == "partial"
        assert result.error == "distillation returned no content"


class TestDistillerForwardsAgentRunnerError:
    """The distiller is the bridge between AgentRunner's specific failure
    reason and the pipeline's user-facing error message. It must forward
    the reason, not swallow it.
    """

    def test_distiller_forwards_agent_runner_last_error(self, config):
        paper = _make_paper()
        agent_runner = MagicMock()
        agent_runner.distill_paper.return_value = None
        agent_runner.last_error = "distill_paper timed out after 2 attempt(s); final timeout was 900s"

        distiller = BriefingDistiller(config, claude_client=None, agent_runner=agent_runner)
        result = distiller.distill(paper)

        assert result is None
        assert distiller.last_error == agent_runner.last_error

    def test_distiller_uses_fallback_when_agent_runner_silent(self, config):
        paper = _make_paper()
        agent_runner = MagicMock()
        agent_runner.distill_paper.return_value = None
        agent_runner.last_error = None  # AgentRunner didn't set a reason

        distiller = BriefingDistiller(config, claude_client=None, agent_runner=agent_runner)
        distiller.distill(paper)

        assert distiller.last_error is not None  # at minimum, distiller sets a placeholder

    def test_distiller_clears_last_error_on_subsequent_success(self, config):
        paper = _make_paper()
        agent_runner = MagicMock()

        valid_md = (
            "# Briefing\n\n"
            "## Why Should You Care\n\n"
            "## Core Intuition\n\n"
            "## Technical Sketch\n\n"
            "## Evidence\n\n"
            "## Challenger\n\n"
            "## Decision Support\n\n"
            "## Open Questions\n\n"
            "## Key Takeaways\n\n" + ("word " * config.distiller.target_word_count)
        )

        distiller = BriefingDistiller(config, claude_client=None, agent_runner=agent_runner)

        # First call: failure with a reason
        agent_runner.distill_paper.return_value = None
        agent_runner.last_error = "distill_paper timed out"
        distiller.distill(paper)
        assert distiller.last_error is not None

        # Second call: success — last_error must be cleared at start of distill()
        agent_runner.distill_paper.return_value = valid_md
        result = distiller.distill(paper)
        assert result is not None
        assert distiller.last_error is None

    def test_distiller_captures_sdk_exception_as_last_error(self, config):
        """When the Anthropic SDK raises, the exception text must surface in
        last_error so the pipeline can show the user what went wrong."""
        paper = _make_paper()
        claude_client = MagicMock()
        claude_client.messages.create.side_effect = RuntimeError("rate limited (429)")

        distiller = BriefingDistiller(config, claude_client=claude_client, agent_runner=None)
        result = distiller.distill(paper)

        assert result is None
        assert distiller.last_error is not None
        assert "Claude SDK error" in distiller.last_error
        assert "rate limited (429)" in distiller.last_error
