"""`run --slack`, exit codes (D11) and `health` skipped checks (COURIER task 1.5).

src/slack.py is another prototyper's file; these tests inject a stub so they
do not depend on it or on the network."""

import sys
import types
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from main import cli
from src.config import PipelineConfig
from src.machine import Machine
from src.models import Paper, ScoredPaper
from src.pipeline import DailyPipeline, PipelineResult


def _scored() -> ScoredPaper:
    paper = Paper(
        id="2610.00001", title="T", authors=["A"], abstract="x",
        published_date=datetime(2026, 10, 20), url="u", categories=["cs.AI"], pdf_url="",
    )
    return ScoredPaper(paper=paper, score=0.7, reasoning="r")


def _stub_slack(monkeypatch, **overrides):
    stub = types.SimpleNamespace(
        post_message=MagicMock(return_value="1.2"),
        build_message=MagicMock(return_value="text"),
        auth_test=MagicMock(return_value={"ok": True}),
    )
    for name, value in overrides.items():
        setattr(stub, name, value)
    monkeypatch.setitem(sys.modules, "src.slack", stub)
    monkeypatch.setattr("src.slack", stub, raising=False)
    return stub


@pytest.fixture
def slack_env(monkeypatch):
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
    monkeypatch.setenv("PAPERBOY_SLACK_CHANNEL", "C123")


def _invoke_run(*args, result: PipelineResult):
    with patch("main._load_and_validate", return_value=MagicMock()), \
         patch("main.DailyPipeline") as Pipeline:
        Pipeline.return_value.run.return_value = result
        out = CliRunner().invoke(cli, ["run", "--backend", "keyword-only", *args])
    return out, Pipeline


class TestSlackFlagConfig:
    @pytest.mark.parametrize("missing", ["SLACK_BOT_TOKEN", "PAPERBOY_SLACK_CHANNEL"])
    def test_missing_variable_exits_1_before_any_pipeline_exists(self, monkeypatch, slack_env, missing):
        monkeypatch.delenv(missing)
        _stub_slack(monkeypatch)
        out, Pipeline = _invoke_run("--slack", result=PipelineResult(status="success", selected_paper=_scored()))
        assert out.exit_code == 1
        assert "Configuration error:" in out.output
        assert missing in out.output
        Pipeline.assert_not_called()

    def test_flag_absent_passes_no_deliverer(self, monkeypatch, slack_env):
        stub = _stub_slack(monkeypatch)
        out, Pipeline = _invoke_run(result=PipelineResult(status="success", selected_paper=_scored()))
        assert out.exit_code == 0
        assert Pipeline.call_args.kwargs.get("deliverer") is None
        stub.post_message.assert_not_called()

    def test_deliverer_builds_message_and_posts_to_channel(self, monkeypatch, slack_env):
        stub = _stub_slack(monkeypatch)
        out, Pipeline = _invoke_run("--slack", result=PipelineResult(status="success", selected_paper=_scored()))
        deliver = Pipeline.call_args.kwargs["deliverer"]
        marker = PipelineResult(status="success")
        assert deliver(marker) == "1.2"
        stub.build_message.assert_called_once_with(marker)
        stub.post_message.assert_called_once_with("text", "C123")


class TestExitCodes:
    def test_success_with_slack_ts_exits_0(self, monkeypatch, slack_env):
        _stub_slack(monkeypatch)
        r = PipelineResult(status="success", selected_paper=_scored(), slack_ts="1.2")
        out, _ = _invoke_run("--slack", result=r)
        assert out.exit_code == 0

    def test_success_with_slack_error_exits_3(self, monkeypatch, slack_env):
        _stub_slack(monkeypatch)
        r = PipelineResult(status="success", selected_paper=_scored(), slack_error="not_in_channel")
        out, _ = _invoke_run("--slack", result=r)
        assert out.exit_code == 3
        assert "not_in_channel" in out.output
        assert "saved" in out.output and "recorded" in out.output

    def test_partial_stays_2_and_error_stays_1_even_with_slack_error(self, monkeypatch, slack_env):
        _stub_slack(monkeypatch)
        partial = PipelineResult(status="partial", selected_paper=_scored(), error="e", slack_error="x")
        assert _invoke_run("--slack", result=partial)[0].exit_code == 2
        error = PipelineResult(status="error", error="e", slack_error="x")
        assert _invoke_run("--slack", result=error)[0].exit_code == 1


def _machine(backend):
    return Machine(name="box", role="w", scope=("personal",), references={}, known=True, backend=backend)


class TestHealth:
    def _pipeline(self, monkeypatch, backend, cli_available):
        monkeypatch.setattr("src.pipeline.resolve_machine", lambda: _machine(backend))
        cfg = PipelineConfig()
        cfg.anthropic_api_key = ""
        with patch("src.pipeline.AgentRunner") as Runner:
            Runner.return_value.is_available.return_value = cli_available
            pipeline = DailyPipeline(cfg, backend="keyword-only")
            pipeline.source_manager = MagicMock()
            pipeline.source_manager.health_check.return_value = {"arxiv": True}
            return pipeline.health_check()

    def test_api_skipped_without_key(self, monkeypatch):
        assert self._pipeline(monkeypatch, "agent", True)["claude_api"] is None

    def test_cli_skipped_on_api_roster_box(self, monkeypatch):
        assert self._pipeline(monkeypatch, "api", False)["claude_cli"] is None

    def test_cli_checked_on_agent_box(self, monkeypatch):
        assert self._pipeline(monkeypatch, "agent", True)["claude_cli"] is True
        assert self._pipeline(monkeypatch, "agent", False)["claude_cli"] is False

    def _run_health(self, results):
        with patch("main.PipelineConfig.load", return_value=PipelineConfig()), \
             patch("main.DailyPipeline") as Pipeline:
            Pipeline.return_value.health_check.return_value = results
            return CliRunner().invoke(cli, ["health"])

    def test_skipped_prints_skipped_and_exits_0(self, monkeypatch):
        monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
        out = self._run_health({"arxiv": True, "claude_api": None, "claude_cli": True})
        assert out.exit_code == 0
        assert "SKIPPED" in out.output
        assert "slack" in out.output

    def test_false_still_exits_1(self, monkeypatch):
        monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
        assert self._run_health({"arxiv": False, "claude_api": None}).exit_code == 1

    def test_slack_ok(self, monkeypatch):
        monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
        stub = _stub_slack(monkeypatch)
        out = self._run_health({"arxiv": True})
        stub.auth_test.assert_called_once()
        assert out.exit_code == 0
        assert "SKIPPED" not in out.output

    def test_slack_failure_exits_1(self, monkeypatch):
        monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
        _stub_slack(monkeypatch, auth_test=MagicMock(side_effect=RuntimeError("invalid_auth")))
        out = self._run_health({"arxiv": True})
        assert out.exit_code == 1
        assert "FAILED" in out.output
