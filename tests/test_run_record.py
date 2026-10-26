"""Run record (D5) and delivery seam (D12): one JSON line per run in
<output_dir>/run_history.jsonl, written after delivery."""

import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.config import PipelineConfig
from src.machine import Machine
from src.models import BriefingDocument, Paper, ScoredPaper
from src.pipeline import DailyPipeline, SelectionHistory, _config_sha256, _git_sha

FIELDS = {
    "date", "started_at", "duration_s", "status", "backend", "machine",
    "scoring_model", "distill_model", "selected_id", "score", "top_candidates",
    "briefing_path", "words", "papers_fetched", "articles_fetched", "error",
    "slack_ts", "slack_error", "git_sha", "config_sha256",
}


def _paper(n: int = 1) -> Paper:
    return Paper(
        id=f"2610.0000{n}v1",
        title=f"Paper {n}",
        authors=["A"],
        abstract="Abstract.",
        published_date=datetime(2026, 10, 20),
        url=f"http://arxiv.org/abs/2610.0000{n}",
        categories=["cs.AI"],
        pdf_url="",
    )


def _briefing(paper: Paper) -> BriefingDocument:
    return BriefingDocument(
        title="Briefing", source_paper=paper,
        generated_at=datetime.now(timezone.utc), content="word " * 100,
    )


@pytest.fixture(autouse=True)
def fixed_machine(monkeypatch):
    monkeypatch.setattr(
        "src.pipeline.resolve_machine",
        lambda: Machine(name="testbox", role="w", scope=("personal",),
                        references={}, known=True, backend=None),
    )


@pytest.fixture
def config(tmp_path):
    cfg = PipelineConfig.load()
    cfg.anthropic_api_key = ""
    cfg.output_dir = str(tmp_path)
    return cfg


def _pipeline(config, distiller="ok", **kwargs) -> DailyPipeline:
    pipeline = DailyPipeline(config, backend="keyword-only", **kwargs)
    if distiller == "ok":
        pipeline.distiller = MagicMock()
        pipeline.distiller.last_error = None
        pipeline.distiller.distill.side_effect = lambda p: _briefing(p)
    elif distiller == "fail":
        pipeline.distiller = MagicMock()
        pipeline.distiller.last_error = "timed out"
        pipeline.distiller.distill.return_value = None
    return pipeline


def _records(config) -> list[dict]:
    path = Path(config.output_dir) / "run_history.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()]


class TestRunRecord:
    def test_success_line_has_every_field(self, config):
        paper = _paper()
        result = _pipeline(config).run(paper_override=paper)

        (rec,) = _records(config)
        assert set(rec) == FIELDS
        assert rec["status"] == "success" == result.status
        assert rec["selected_id"] == paper.id
        assert rec["score"] == 1.0
        assert rec["words"] == 100
        assert rec["briefing_path"] == str(result.briefing_path)
        assert rec["error"] is None
        assert rec["slack_ts"] is None and rec["slack_error"] is None
        assert rec["machine"] == "testbox"
        assert rec["date"] == rec["started_at"][:10]
        assert rec["started_at"].endswith("+00:00")
        assert rec["duration_s"] >= 0
        assert len(rec["config_sha256"]) == 64

    def test_appends_one_line_per_run(self, config):
        pipeline = _pipeline(config)
        pipeline.run(paper_override=_paper(1), dedup=False)
        pipeline.run(paper_override=_paper(2), dedup=False)
        assert len(_records(config)) == 2

    def test_partial_line(self, config):
        _pipeline(config, distiller="fail").run(paper_override=_paper())
        (rec,) = _records(config)
        assert rec["status"] == "partial"
        assert rec["error"] == "timed out"
        assert rec["briefing_path"] is None
        assert rec["words"] is None

    def test_error_line_from_except_path(self, config):
        pipeline = _pipeline(config)
        pipeline.source_manager = MagicMock()
        pipeline.source_manager.fetch_all.return_value = ([], [])
        result = pipeline.run()
        (rec,) = _records(config)
        assert result.status == "error"
        assert rec["status"] == "error"
        assert "No papers or articles" in rec["error"]
        assert rec["selected_id"] is None and rec["score"] is None
        assert rec["top_candidates"] == []

    def test_unwritable_record_path_warns_and_keeps_status(self, config, caplog):
        (Path(config.output_dir) / "run_history.jsonl").mkdir()
        with caplog.at_level("WARNING"):
            result = _pipeline(config).run(paper_override=_paper())
        assert result.status == "success"
        assert any("run record" in r.message.lower() for r in caplog.records)

    def test_top_candidates_up_to_five_and_first_is_selected(self, config):
        papers = [_paper(n) for n in range(1, 6)]
        scored = [ScoredPaper(p, 0.9 - i / 10, "why") for i, p in enumerate(papers)]
        pipeline = _pipeline(config)
        pipeline.source_manager = MagicMock()
        pipeline.source_manager.fetch_all.return_value = (papers, [])
        pipeline.selector = MagicMock()
        pipeline.selector.select_best.return_value = scored

        result = pipeline.run()

        assert pipeline.selector.select_best.call_args.kwargs["top_k"] == config.selector.top_k_for_claude
        assert result.selected_paper is scored[0]
        assert result.top_candidates == scored
        (rec,) = _records(config)
        assert len(rec["top_candidates"]) == 5
        assert rec["top_candidates"][0] == {"id": papers[0].id, "title": "Paper 1", "score": 0.9}
        assert rec["selected_id"] == papers[0].id
        assert rec["papers_fetched"] == 5

    def test_top_candidates_defaults_to_independent_empty_lists(self):
        from src.pipeline import PipelineResult
        a, b = PipelineResult(status="error"), PipelineResult(status="error")
        a.top_candidates.append("x")
        assert b.top_candidates == []

    def test_git_sha_needs_no_git_binary(self, config, monkeypatch):
        # The App image has no git; the sha must still reach the record.
        if not (Path(__file__).resolve().parents[1] / ".git").is_dir():
            pytest.skip("no .git directory here")
        monkeypatch.setenv("PATH", "")
        _pipeline(config).run(paper_override=_paper())
        sha = _records(config)[0]["git_sha"]
        assert sha and len(sha) == 7 and set(sha) <= set("0123456789abcdef"), sha

    def test_git_sha_is_short_hash_in_repo(self, config):
        _pipeline(config).run(paper_override=_paper())
        sha = _records(config)[0]["git_sha"]
        assert sha is None or (4 <= len(sha) <= 40 and sha.isalnum())


SHA = "0ea43f1" + "c" * 33  # 40 hex characters


def _git_dir(tmp_path, head: str) -> Path:
    git = tmp_path / ".git"
    git.mkdir()
    (git / "HEAD").write_text(head + "\n")
    return git


class TestGitSha:
    """git_sha is read from .git's own files, never a git binary: the App image
    (debian:bookworm-slim) has none, and the first tick's record line read
    git_sha: None (2026-10-26)."""

    def test_reads_the_loose_ref_head_names(self, tmp_path):
        git = _git_dir(tmp_path, "ref: refs/heads/main")
        (git / "refs" / "heads").mkdir(parents=True)
        (git / "refs" / "heads" / "main").write_text(SHA + "\n")
        assert _git_sha(tmp_path) == SHA[:7]

    def test_falls_back_to_packed_refs(self, tmp_path):
        # After a gc the loose file is gone and the ref lives in packed-refs.
        git = _git_dir(tmp_path, "ref: refs/heads/main")
        (git / "packed-refs").write_text(
            "# pack-refs with: peeled fully-peeled sorted \n"
            f"{'a' * 40} refs/heads/other\n"
            f"{SHA} refs/heads/main\n"
        )
        assert _git_sha(tmp_path) == SHA[:7]

    def test_detached_head_holds_the_sha_itself(self, tmp_path):
        _git_dir(tmp_path, SHA)
        assert _git_sha(tmp_path) == SHA[:7]

    def test_none_without_a_git_dir(self, tmp_path):
        assert _git_sha(tmp_path) is None


class TestRunMetadata:
    def test_keyword_only(self, config):
        result = _pipeline(config).run(paper_override=_paper())
        assert result.backend == "keyword-only"
        assert result.machine == "testbox"
        assert result.scoring_model is None and result.distill_model is None
        assert result.started_at.tzinfo is not None
        assert result.duration_s >= 0

    def test_api_backend_records_config_model_ids(self, config):
        config.anthropic_api_key = "sk-test"
        pipeline = DailyPipeline(config, backend="api")
        pipeline.distiller = MagicMock()
        pipeline.distiller.distill.side_effect = lambda p: _briefing(p)
        result = pipeline.run(paper_override=_paper())
        assert result.backend == "api"
        assert result.scoring_model == config.claude.scoring_model
        assert result.distill_model == config.claude.model

    def _agent_pipeline(self, config, score_model, distill_model):
        with patch("src.pipeline.AgentRunner") as Runner:
            runner = Runner.return_value
            runner.is_available.return_value = True
            runner.last_score_model = score_model
            runner.last_distill_model = distill_model
            pipeline = DailyPipeline(config, backend="auto")
        pipeline.distiller = MagicMock()
        pipeline.distiller.distill.side_effect = lambda p: _briefing(p)
        return pipeline

    def test_auto_records_the_resolved_backend(self, config):
        result = self._agent_pipeline(config, None, None).run(paper_override=_paper())
        assert result.backend == "agent"

    def test_agent_path_records_the_models_the_cli_reported(self, config):
        result = self._agent_pipeline(config, "claude-a", "claude-b").run(paper_override=_paper())
        assert (result.scoring_model, result.distill_model) == ("claude-a", "claude-b")
        rec = _records(config)[0]
        assert (rec["scoring_model"], rec["distill_model"]) == ("claude-a", "claude-b")

    def test_agent_path_records_null_when_no_model_seen(self, config):
        """Rule 8: a value or null in the record, never a placeholder sentence (gate SME m2)."""
        result = self._agent_pipeline(config, None, None).run(paper_override=_paper())
        assert (result.scoring_model, result.distill_model) == (None, None)


class TestConfigHash:
    def test_identical_across_two_loads(self, monkeypatch):
        monkeypatch.setenv("USER_CONTEXT", "context one")
        assert _config_sha256(PipelineConfig.load()) == _config_sha256(PipelineConfig.load())

    def test_changes_with_user_context(self, monkeypatch):
        monkeypatch.setenv("USER_CONTEXT", "context one")
        first = _config_sha256(PipelineConfig.load())
        monkeypatch.setenv("USER_CONTEXT", "context two")
        assert _config_sha256(PipelineConfig.load()) != first

    def test_ignores_api_key(self):
        a, b = PipelineConfig(anthropic_api_key="one"), PipelineConfig(anthropic_api_key="two")
        assert _config_sha256(a) == _config_sha256(b)

    def test_ignores_output_dir_and_log_level(self):
        """The hash names the config that shapes the briefing; where it lands and how loudly do not (gate SME m4)."""
        a, b = PipelineConfig(output_dir="/one", log_level="INFO"), PipelineConfig(output_dir="/two", log_level="DEBUG")
        assert _config_sha256(a) == _config_sha256(b)

    def test_user_context_text_never_written(self, config):
        config.distiller.user_context = "SECRET-PERSONA-TEXT"
        _pipeline(config).run(paper_override=_paper())
        assert "SECRET-PERSONA-TEXT" not in (Path(config.output_dir) / "run_history.jsonl").read_text()


class TestDeliverySeam:
    def test_deliverer_receipt_lands_in_result_and_record(self, config):
        seen = []
        pipeline = _pipeline(config, deliverer=lambda r: seen.append(r.status) or "123.456")
        result = pipeline.run(paper_override=_paper())
        assert seen == ["success"]
        assert result.slack_ts == "123.456" and result.slack_error is None
        assert _records(config)[0]["slack_ts"] == "123.456"

    def test_raising_deliverer_sets_slack_error_and_changes_nothing_else(self, config):
        def boom(result):
            raise RuntimeError("not_in_channel")

        paper = _paper()
        result = _pipeline(config, deliverer=boom).run(paper_override=paper)

        assert result.status == "success"
        assert result.slack_error == "not_in_channel" and result.slack_ts is None
        assert result.briefing_path.exists()
        assert SelectionHistory(Path(config.output_dir) / ".selection_history.json", 30).contains(paper.id)
        rec = _records(config)[0]
        assert rec["status"] == "success" and rec["slack_error"] == "not_in_channel"

    def test_no_deliverer_leaves_slack_fields_empty(self, config):
        result = _pipeline(config).run(paper_override=_paper())
        assert result.slack_ts is None and result.slack_error is None

    def test_partial_and_error_results_are_delivered(self, config):
        statuses = []
        _pipeline(config, distiller="fail", deliverer=lambda r: statuses.append(r.status)).run(paper_override=_paper())
        pipeline = _pipeline(config, deliverer=lambda r: statuses.append(r.status))
        pipeline.source_manager = MagicMock()
        pipeline.source_manager.fetch_all.return_value = ([], [])
        pipeline.run()
        assert statuses == ["partial", "error"]


class TestRecordAlwaysWritten:
    def test_record_written_even_when_metadata_raises(self, config, monkeypatch):
        """D5: the record is written in a finally; a raise in the wrapper still leaves one line (gate W2)."""
        def boom():
            raise RuntimeError("roster unreadable")
        monkeypatch.setattr("src.pipeline.resolve_machine", boom)
        with pytest.raises(RuntimeError):
            _pipeline(config).run(paper_override=_paper())
        lines = (Path(config.output_dir) / "run_history.jsonl").read_text().splitlines()
        assert len(lines) == 1
