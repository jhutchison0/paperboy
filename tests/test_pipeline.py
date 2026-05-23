"""
End-to-end integration test for DailyPipeline.

Exercises the source→select→record path through `DailyPipeline.run()` with
mocked sources. The selection stage runs for real (keyword scoring against
real config), and the dedup history is written for real to a tmp_path.

This complements `test_pipeline_outcomes.py`, which uses `paper_override=` to
bypass sourcing/selection and focus on outcome-status logic. Together they
cover both branches of `DailyPipeline.run()`.

Distillation is skipped (backend='keyword-only'); per Pillar 4 the pipeline
still reports `success` in that mode because no briefing was expected.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import PipelineConfig
from src.models import Article, Paper
from src.pipeline import DailyPipeline, SelectionHistory


# ── Mock data — papers chosen so the relevance scoring is unambiguous ──

MOCK_PAPERS = [
    Paper(
        id="2603.12345",
        title="ReasonGraph: Augmenting LLM Decision Support with Dynamic Knowledge Graphs",
        authors=["Alice Chen", "Bob Zhang"],
        abstract=(
            "We introduce ReasonGraph, a framework that combines large language "
            "models with dynamically constructed knowledge graphs to improve "
            "decision support. Our approach uses chain-of-thought reasoning to "
            "extract structured relationships, building a queryable graph that "
            "serves as external memory for the LLM."
        ),
        published_date=datetime(2026, 3, 8, tzinfo=timezone.utc),
        url="https://arxiv.org/abs/2603.12345",
        categories=["cs.AI", "cs.CL"],
        pdf_url="https://arxiv.org/pdf/2603.12345",
        source="arxiv",
    ),
    Paper(
        id="2603.12348",
        title="On the Convergence Properties of Adam with Weight Decay",
        authors=["Henry Zhao"],
        abstract=(
            "We provide new convergence guarantees for the AdamW optimizer in "
            "non-convex landscapes typical of deep learning."
        ),
        published_date=datetime(2026, 3, 5, tzinfo=timezone.utc),
        url="https://arxiv.org/abs/2603.12348",
        categories=["stat.ML"],
        pdf_url="https://arxiv.org/pdf/2603.12348",
        source="arxiv",
    ),
]

MOCK_ARTICLES = [
    Article(
        title="Building Reliable AI Agents with Tool Use and Structured Reasoning",
        url="https://example.com/agents-blog",
        published_date=datetime(2026, 3, 9, tzinfo=timezone.utc),
        source="AI Research Blog",
        summary=(
            "A practical guide to building AI agents that combine LLM reasoning "
            "with tool use and structured knowledge representations."
        ),
    ),
]


@pytest.fixture
def config(tmp_path):
    """Real config, but isolated output dir so history doesn't leak."""
    cfg = PipelineConfig.load()
    cfg.output_dir = str(tmp_path)
    cfg.anthropic_api_key = ""  # force keyword-only fallback path
    return cfg


class TestPipelineEndToEnd:
    """The source→select→record vertical slice with mocked sources."""

    def test_run_with_mocked_sources_returns_success_in_keyword_only_mode(self, config):
        """With keyword-only backend and mocked sources, the pipeline scores
        candidates, picks one, records the selection, and reports success."""
        pipeline = DailyPipeline(config, backend="keyword-only")

        with patch.object(
            pipeline.source_manager,
            "fetch_all",
            return_value=(MOCK_PAPERS, MOCK_ARTICLES),
        ):
            result = pipeline.run()

        assert result.success is True
        assert result.selected_paper is not None
        assert result.briefing is None  # keyword-only intentionally produces no briefing
        assert result.briefing_path is None
        assert result.papers_fetched == len(MOCK_PAPERS)
        assert result.articles_fetched == len(MOCK_ARTICLES)

    def test_run_records_selected_paper_in_history(self, config):
        """The selected paper must be persisted to .selection_history.json so
        the next day's run doesn't re-pick it."""
        pipeline = DailyPipeline(config, backend="keyword-only")

        with patch.object(
            pipeline.source_manager,
            "fetch_all",
            return_value=(MOCK_PAPERS, MOCK_ARTICLES),
        ):
            result = pipeline.run()

        history_path = Path(config.output_dir) / ".selection_history.json"
        assert history_path.exists()
        history = SelectionHistory(history_path, config.dedup_cooldown_days)
        assert history.contains(result.selected_paper.paper.id)

    def test_run_with_no_candidates_reports_error(self, config):
        """If sourcing returns nothing, the pipeline must not silently succeed."""
        pipeline = DailyPipeline(config, backend="keyword-only")

        with patch.object(
            pipeline.source_manager, "fetch_all", return_value=([], [])
        ):
            result = pipeline.run()

        assert result.success is False
        assert result.error is not None

    def test_run_respects_dedup_when_paper_already_recorded(self, config):
        """A paper recorded in history within the cooldown window must be
        excluded from selection on the next run."""
        # First run picks something and records it.
        pipeline = DailyPipeline(config, backend="keyword-only")
        with patch.object(
            pipeline.source_manager,
            "fetch_all",
            return_value=(MOCK_PAPERS, MOCK_ARTICLES),
        ):
            first = pipeline.run()
        first_pick_id = first.selected_paper.paper.id

        # Second run with the same candidate set: must pick something different.
        pipeline2 = DailyPipeline(config, backend="keyword-only")
        with patch.object(
            pipeline2.source_manager,
            "fetch_all",
            return_value=(MOCK_PAPERS, MOCK_ARTICLES),
        ):
            second = pipeline2.run()

        if second.success:
            assert second.selected_paper.paper.id != first_pick_id
