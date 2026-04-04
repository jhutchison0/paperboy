"""
Tests for CLI output messaging in main.py run command.

Covers the three output branches after a successful pipeline run:
  1. Briefing generated → shows word count, path, upload prompt
  2. Distiller is None (keyword-only) → shows "keyword-only mode"
  3. Distiller exists but briefing is None → shows failure warning
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import BriefingDocument, Paper, ScoredPaper
from src.pipeline import PipelineResult


def _make_paper():
    return Paper(
        id="2603.09909",
        title="Test Paper Title",
        authors=["Author A"],
        abstract="Abstract text",
        published_date=datetime(2026, 3, 10),
        url="http://arxiv.org/abs/2603.09909",
        categories=["cs.AI"],
        pdf_url="",
    )


def _make_scored():
    return ScoredPaper(paper=_make_paper(), score=0.75, reasoning="good match")


def _make_briefing():
    return BriefingDocument(
        title="Research Briefing: Test",
        source_paper=_make_paper(),
        generated_at=datetime.now(timezone.utc),
        content="word " * 4000,
    )


class TestRunOutputBranches:
    """Test the three output branches in main.py run command."""

    @patch("main.DailyPipeline")
    @patch("main._load_and_validate")
    def test_success_with_briefing_shows_words_and_path(self, mock_load, MockPipeline):
        mock_load.return_value = MagicMock()
        pipeline = MagicMock()
        pipeline.distiller = MagicMock()  # distiller exists
        pipeline.run.return_value = PipelineResult(
            status="success",
            selected_paper=_make_scored(),
            briefing=_make_briefing(),
            briefing_path=Path("output/briefings/260311_test.md"),
            papers_fetched=50,
            articles_fetched=10,
        )
        MockPipeline.return_value = pipeline

        from main import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["run", "--backend", "auto"])

        assert result.exit_code == 0
        assert "SUCCESS" in result.output
        assert "Words:" in result.output
        assert "Saved to:" in result.output
        assert "NotebookLM" in result.output

    @patch("main.DailyPipeline")
    @patch("main._load_and_validate")
    def test_keyword_only_shows_keyword_message(self, mock_load, MockPipeline):
        mock_load.return_value = MagicMock()
        pipeline = MagicMock()
        pipeline.distiller = None  # keyword-only mode
        pipeline.run.return_value = PipelineResult(
            status="success",
            selected_paper=_make_scored(),
            briefing=None,
            papers_fetched=50,
        )
        MockPipeline.return_value = pipeline

        from main import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["run", "--backend", "keyword-only"])

        assert result.exit_code == 0
        assert "SUCCESS" in result.output
        assert "keyword-only" in result.output
        assert "Briefing generation failed" not in result.output

    @patch("main.DailyPipeline")
    @patch("main._load_and_validate")
    def test_auto_resolving_to_keyword_only_shows_keyword_message(self, mock_load, MockPipeline):
        """When auto resolves to keyword-only (no API key, no CLI), the message
        should say 'keyword-only mode', not 'Briefing generation failed'."""
        mock_load.return_value = MagicMock()
        pipeline = MagicMock()
        pipeline.distiller = None  # auto resolved to keyword-only
        pipeline.run.return_value = PipelineResult(
            status="success",
            selected_paper=_make_scored(),
            briefing=None,
            papers_fetched=50,
        )
        MockPipeline.return_value = pipeline

        from main import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["run", "--backend", "auto"])

        assert result.exit_code == 0
        assert "keyword-only" in result.output
        assert "Briefing generation failed" not in result.output

    @patch("main.DailyPipeline")
    @patch("main._load_and_validate")
    def test_distillation_failure_shows_warning(self, mock_load, MockPipeline):
        """When distiller exists but returns no briefing, show failure warning."""
        mock_load.return_value = MagicMock()
        pipeline = MagicMock()
        pipeline.distiller = MagicMock()  # distiller exists (not keyword-only)
        pipeline.run.return_value = PipelineResult(
            status="success",
            selected_paper=_make_scored(),
            briefing=None,  # distillation failed
            papers_fetched=50,
        )
        MockPipeline.return_value = pipeline

        from main import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["run", "--backend", "agent"])

        assert result.exit_code == 0
        assert "SUCCESS" in result.output
        assert "Briefing generation failed" in result.output
        assert "keyword-only" not in result.output

    @patch("main.DailyPipeline")
    @patch("main._load_and_validate")
    def test_pipeline_failure_exits_nonzero(self, mock_load, MockPipeline):
        mock_load.return_value = MagicMock()
        pipeline = MagicMock()
        pipeline.run.return_value = PipelineResult(
            status="error",
            error="No papers found",
        )
        MockPipeline.return_value = pipeline

        from main import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["run", "--backend", "auto"])

        assert result.exit_code != 0
        assert "Pipeline failed" in result.output


class TestRunNoDedupFlag:
    """Tests for --no-dedup CLI flag."""

    @patch("main.DailyPipeline")
    @patch("main._load_and_validate")
    def test_no_dedup_passes_false_to_pipeline(self, mock_load, MockPipeline):
        mock_load.return_value = MagicMock()
        pipeline = MagicMock()
        pipeline.distiller = None
        pipeline.run.return_value = PipelineResult(
            status="success",
            selected_paper=_make_scored(),
            briefing=None,
            papers_fetched=50,
        )
        MockPipeline.return_value = pipeline

        from main import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["run", "--backend", "keyword-only", "--no-dedup"])

        assert result.exit_code == 0
        _, kwargs = pipeline.run.call_args
        assert kwargs["dedup"] is False

    @patch("main.DailyPipeline")
    @patch("main._load_and_validate")
    def test_default_dedup_is_true(self, mock_load, MockPipeline):
        mock_load.return_value = MagicMock()
        pipeline = MagicMock()
        pipeline.distiller = None
        pipeline.run.return_value = PipelineResult(
            status="success",
            selected_paper=_make_scored(),
            briefing=None,
            papers_fetched=50,
        )
        MockPipeline.return_value = pipeline

        from main import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["run", "--backend", "keyword-only"])

        assert result.exit_code == 0
        _, kwargs = pipeline.run.call_args
        assert kwargs["dedup"] is True


class TestDistillPaperId:
    """Tests for distill --paper-id CLI option."""

    @patch("src.sourcer.ArxivSourcer")
    @patch("main.DailyPipeline")
    @patch("main._load_and_validate")
    def test_paper_id_success(self, mock_load, MockPipeline, MockSourcer):
        mock_load.return_value = MagicMock()
        mock_sourcer = MagicMock()
        mock_sourcer.fetch_by_id.return_value = _make_paper()
        MockSourcer.return_value = mock_sourcer
        pipeline = MagicMock()
        pipeline.distiller = MagicMock()
        pipeline.run.return_value = PipelineResult(
            status="success",
            selected_paper=_make_scored(),
            briefing=_make_briefing(),
            briefing_path=Path("output/briefings/260311_test.md"),
        )
        MockPipeline.return_value = pipeline

        from main import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["distill", "--backend", "api", "--paper-id", "1904.12787"])

        assert result.exit_code == 0
        mock_sourcer.fetch_by_id.assert_called_once_with("1904.12787")
        _, kwargs = pipeline.run.call_args
        assert kwargs["paper_override"] is not None

    @patch("src.sourcer.ArxivSourcer")
    @patch("main.DailyPipeline")
    @patch("main._load_and_validate")
    def test_paper_id_not_found_exits_nonzero(self, mock_load, MockPipeline, MockSourcer):
        mock_load.return_value = MagicMock()
        mock_sourcer = MagicMock()
        mock_sourcer.fetch_by_id.side_effect = ValueError("ArXiv paper not found: 0000.00000")
        MockSourcer.return_value = mock_sourcer
        MockPipeline.return_value = MagicMock(distiller=MagicMock())

        from main import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["distill", "--backend", "api", "--paper-id", "0000.00000"])

        assert result.exit_code != 0

    @patch("src.sourcer.ArxivSourcer")
    @patch("main.DailyPipeline")
    @patch("main._load_and_validate")
    def test_paper_id_network_error_exits_nonzero(self, mock_load, MockPipeline, MockSourcer):
        mock_load.return_value = MagicMock()
        mock_sourcer = MagicMock()
        mock_sourcer.fetch_by_id.side_effect = ConnectionError("ArXiv unreachable")
        MockSourcer.return_value = mock_sourcer
        MockPipeline.return_value = MagicMock(distiller=MagicMock())

        from main import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["distill", "--backend", "api", "--paper-id", "1904.12787"])

        assert result.exit_code != 0
