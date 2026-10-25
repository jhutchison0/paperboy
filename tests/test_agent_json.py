"""AgentRunner reads `--output-format json` (COURIER task 1.9): the text comes
from `result`, the model name from `modelUsage`. The fixture is a real
`claude -p "Reply with OK" --output-format json` capture from CLI 2.1.310;
its modelUsage holds two models, a small auxiliary one and the main one."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.agent_runner import AgentRunner
from src.config import PipelineConfig

FIXTURE = Path(__file__).parent / "fixtures" / "claude_p_ok.json"


@pytest.fixture
def runner():
    return AgentRunner(PipelineConfig())


def _invoke(runner, stdout: str, returncode: int = 0):
    proc = MagicMock(returncode=returncode)
    proc.communicate.return_value = (stdout.encode(), b"")
    with patch("subprocess.Popen", return_value=proc) as popen:
        outcome = runner._invoke("p", timeout=5)
    return outcome, popen.call_args.args[0]


def test_asks_for_json_output(runner):
    _, argv = _invoke(runner, FIXTURE.read_text())
    i = argv.index("--output-format")
    assert argv[i + 1] == "json"


def test_text_from_result_field_and_model_from_usage(runner):
    outcome, _ = _invoke(runner, FIXTURE.read_text())
    assert outcome.text == "OK"
    # the main model, not the cheaper auxiliary one that also appears
    assert outcome.model == "claude-fable-5-1"


def test_model_is_none_when_usage_block_is_missing(runner):
    outcome, _ = _invoke(runner, json.dumps({"is_error": False, "result": "hi"}))
    assert outcome.text == "hi"
    assert outcome.model is None


@pytest.mark.parametrize("stdout", ["not json", json.dumps({"is_error": True, "result": "limit"}), json.dumps({"is_error": False})])
def test_unusable_envelope_is_a_failure(runner, stdout):
    outcome, _ = _invoke(runner, stdout)
    assert outcome.text is None


def test_result_text_is_capped(runner):
    stdout = json.dumps({"is_error": False, "result": "x" * 1000})
    proc = MagicMock(returncode=0)
    proc.communicate.return_value = (stdout.encode(), b"")
    with patch("subprocess.Popen", return_value=proc):
        outcome = runner._invoke("p", timeout=5, max_output_bytes=100)
    assert len(outcome.text) == 100


class TestModelNamesExposed:
    def _ok(self, text, model):
        from src.agent_runner import _InvocationOutcome
        return _InvocationOutcome(text=text, model=model)

    def test_score_paper_records_model(self, runner):
        from src.config import FocusAreas
        from tests.test_run_record import _paper
        payload = json.dumps({"score": 0.5, "reasoning": "r"})
        with patch.object(runner, "_invoke", return_value=self._ok(payload, "claude-a")):
            runner.score_paper(_paper(), FocusAreas())
        assert runner.last_score_model == "claude-a"

    def test_distill_paper_records_model(self, runner):
        from tests.test_run_record import _paper
        from tests.test_agent_runner import _make_valid_briefing
        md = _make_valid_briefing(runner.config.distiller)
        with patch.object(runner, "_invoke", return_value=self._ok(md, "claude-b")):
            out = runner.distill_paper(_paper(), runner.config.distiller, "sys", "user")
        assert out is not None
        assert runner.last_distill_model == "claude-b"


def test_unusable_envelope_warning_names_the_stdout_head(runner, caplog):
    """Gate W5: a non-JSON stdout keeps its head in the warning for diagnosis."""
    import logging
    with caplog.at_level(logging.WARNING):
        _invoke(runner, "Sorry, I cannot do that right now because reasons")
    assert "Sorry, I cannot" in caplog.text


def test_score_tolerates_a_fenced_json_block(runner):
    """Gate W6: the model may fence its JSON; the parser finds the object inside."""
    fenced = '```json\n{"score": 0.4, "reasoning": "r"}\n```'
    assert runner._validate_score(fenced) == {"score": 0.4, "reasoning": "r"}
