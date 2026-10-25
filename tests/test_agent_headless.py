"""AgentRunner headless hardening (COURIER task 1.2, D13): the OAuth token
survives the env strip, Anthropic credentials do not, and the invocation
runs without session files or tools."""

from unittest.mock import MagicMock, patch

import pytest

from src.config import PipelineConfig
from src.agent_runner import AgentRunner


@pytest.fixture
def runner():
    return AgentRunner(PipelineConfig())


def _capture(runner, monkeypatch, **env):
    for name in list(__import__("os").environ):
        if name.startswith(("CLAUDE", "ANTHROPIC")):
            monkeypatch.delenv(name)
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    proc = MagicMock(returncode=0)
    proc.communicate.return_value = (b"ok", b"")
    with patch("subprocess.Popen", return_value=proc) as popen:
        runner._invoke("a prompt", timeout=5)
    return popen.call_args.args[0], popen.call_args.kwargs["env"]


class TestCleanEnv:
    def test_oauth_token_survives(self, runner, monkeypatch):
        _, env = _capture(runner, monkeypatch, CLAUDE_CODE_OAUTH_TOKEN="tok")
        assert env["CLAUDE_CODE_OAUTH_TOKEN"] == "tok"

    def test_anthropic_credentials_and_claude_config_are_stripped(self, runner, monkeypatch):
        _, env = _capture(
            runner, monkeypatch,
            ANTHROPIC_API_KEY="k", ANTHROPIC_AUTH_TOKEN="t",
            CLAUDE_CONFIG_DIR="/x", CLAUDE_CODE_OAUTH_TOKEN="tok",
        )
        assert "ANTHROPIC_API_KEY" not in env
        assert "ANTHROPIC_AUTH_TOKEN" not in env
        assert "CLAUDE_CONFIG_DIR" not in env

    def test_headless_variables_are_set(self, runner, monkeypatch):
        _, env = _capture(runner, monkeypatch)
        assert env["CLAUDE_CODE_DISABLE_CLAUDE_MDS"] == "1"
        assert env["DISABLE_AUTOUPDATER"] == "1"

    def test_no_token_means_no_token_in_env(self, runner, monkeypatch):
        _, env = _capture(runner, monkeypatch)
        assert "CLAUDE_CODE_OAUTH_TOKEN" not in env


class TestArgv:
    def test_no_session_persistence_and_tools_off(self, runner, monkeypatch):
        argv, _ = _capture(runner, monkeypatch)
        assert "--no-session-persistence" in argv
        i = argv.index("--tools")
        assert argv[i + 1] == ""
