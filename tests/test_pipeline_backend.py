"""
Tests for pipeline backend detection and fallback chain.

Verifies that DailyPipeline correctly resolves api/agent/keyword-only/auto
backends and wires them into the selector and distiller.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import PipelineConfig
from src.machine import Machine
from src.pipeline import DailyPipeline


def _machine(backend=None):
    """A roster entry as auto-mode sees it; backend is the only field it reads."""
    return Machine(
        name="testbox", role="workstation", scope=("personal",),
        references={}, known=True, backend=backend,
    )


@pytest.fixture(autouse=True)
def no_machine_preference(monkeypatch):
    """Pin the machine roster to no-preference so tests are hermetic against
    the host's real config/project.yaml (same principle as the USER_CONTEXT
    tests). Preference tests override with their own patch."""
    monkeypatch.setattr("src.pipeline.resolve_machine", lambda: _machine())


@pytest.fixture
def config():
    """Config with no API key (simulates Max-only user)."""
    cfg = PipelineConfig.load()
    cfg.anthropic_api_key = ""
    return cfg


@pytest.fixture
def config_with_key():
    """Config with a fake API key."""
    cfg = PipelineConfig.load()
    cfg.anthropic_api_key = "sk-test-key"
    return cfg


class TestResolveBackend:
    def test_keyword_only_returns_no_clients(self, config):
        pipeline = DailyPipeline(config, backend="keyword-only")
        assert pipeline.distiller is None
        assert pipeline._has_claude_backend is False

    def test_api_backend_with_key(self, config_with_key):
        pipeline = DailyPipeline(config_with_key, backend="api")
        assert pipeline._has_claude_backend is True
        assert pipeline.distiller is not None

    def test_api_backend_without_key_raises(self, config):
        with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
            DailyPipeline(config, backend="api")

    @patch("src.pipeline.AgentRunner")
    def test_agent_backend_available(self, MockRunner, config):
        mock_instance = MagicMock()
        mock_instance.is_available.return_value = True
        MockRunner.return_value = mock_instance

        pipeline = DailyPipeline(config, backend="agent")
        assert pipeline._has_claude_backend is True

    @patch("src.pipeline.AgentRunner")
    def test_agent_backend_not_available_raises(self, MockRunner, config):
        mock_instance = MagicMock()
        mock_instance.is_available.return_value = False
        MockRunner.return_value = mock_instance

        with pytest.raises(RuntimeError, match="claude.*CLI"):
            DailyPipeline(config, backend="agent")

    def test_auto_prefers_api_key(self, config_with_key):
        pipeline = DailyPipeline(config_with_key, backend="auto")
        assert pipeline._has_claude_backend is True

    @patch("src.pipeline.AgentRunner")
    def test_auto_falls_back_to_agent(self, MockRunner, config):
        mock_instance = MagicMock()
        mock_instance.is_available.return_value = True
        MockRunner.return_value = mock_instance

        pipeline = DailyPipeline(config, backend="auto")
        assert pipeline._has_claude_backend is True

    @patch("src.pipeline.AgentRunner")
    def test_auto_falls_back_to_keyword_only(self, MockRunner, config):
        mock_instance = MagicMock()
        mock_instance.is_available.return_value = False
        MockRunner.return_value = mock_instance

        pipeline = DailyPipeline(config, backend="auto")
        assert pipeline._has_claude_backend is False
        assert pipeline.distiller is None

    @patch("src.pipeline.AgentRunner")
    def test_placeholder_key_falls_through_to_agent(self, MockRunner):
        """Regression: .env.example placeholder must not trigger the SDK path.

        Mirrors the real user flow: cp .env.example .env leaves the key as
        sk-ant-your-key-here. validate() blanks it, auto-mode picks AgentRunner.
        """
        cfg = PipelineConfig.load()
        cfg.anthropic_api_key = "sk-ant-your-key-here"
        cfg.validate()

        mock_instance = MagicMock()
        mock_instance.is_available.return_value = True
        MockRunner.return_value = mock_instance

        pipeline = DailyPipeline(cfg, backend="auto")
        assert pipeline._has_claude_backend is True
        assert pipeline.selector.claude is None
        assert pipeline.selector.agent_runner is not None


class TestMachineBackendPreference:
    @patch("src.pipeline.AgentRunner")
    def test_auto_honors_agent_preference_over_api_key(self, MockRunner, config_with_key, monkeypatch):
        """The home-box case: an .env carrying a key (e.g. for USER_CONTEXT)
        must not silently switch a subscription box onto paid API."""
        monkeypatch.setattr("src.pipeline.resolve_machine", lambda: _machine("agent"))
        mock_instance = MagicMock()
        mock_instance.is_available.return_value = True
        MockRunner.return_value = mock_instance

        pipeline = DailyPipeline(config_with_key, backend="auto")

        assert pipeline.selector.claude is None
        assert pipeline.selector.agent_runner is not None

    def test_auto_honors_api_preference(self, config_with_key, monkeypatch):
        monkeypatch.setattr("src.pipeline.resolve_machine", lambda: _machine("api"))

        pipeline = DailyPipeline(config_with_key, backend="auto")

        assert pipeline.selector.claude is not None
        assert pipeline.selector.agent_runner is None

    @patch("src.pipeline.AgentRunner")
    def test_unavailable_preference_falls_through_to_chain(self, MockRunner, config_with_key, monkeypatch):
        """Preference is advisory: prefers agent, CLI absent, key present ->
        the detection chain still finds the SDK instead of erroring."""
        monkeypatch.setattr("src.pipeline.resolve_machine", lambda: _machine("agent"))
        mock_instance = MagicMock()
        mock_instance.is_available.return_value = False
        MockRunner.return_value = mock_instance

        pipeline = DailyPipeline(config_with_key, backend="auto")

        assert pipeline.selector.claude is not None

    def test_unknown_preference_is_ignored(self, config_with_key, monkeypatch):
        monkeypatch.setattr("src.pipeline.resolve_machine", lambda: _machine("carrier-pigeon"))

        pipeline = DailyPipeline(config_with_key, backend="auto")

        assert pipeline.selector.claude is not None

    @patch("src.pipeline.AgentRunner")
    def test_explicit_flag_outranks_preference(self, MockRunner, config_with_key, monkeypatch):
        """--backend api on an agent-preferring box uses the API: the flag wins."""
        monkeypatch.setattr("src.pipeline.resolve_machine", lambda: _machine("agent"))
        mock_instance = MagicMock()
        mock_instance.is_available.return_value = True
        MockRunner.return_value = mock_instance

        pipeline = DailyPipeline(config_with_key, backend="api")

        assert pipeline.selector.claude is not None
        assert pipeline.selector.agent_runner is None


class TestHealthCheck:
    @patch("src.pipeline.AgentRunner")
    def test_health_check_includes_cli_status(self, MockRunner, config):
        mock_instance = MagicMock()
        mock_instance.is_available.return_value = True
        MockRunner.return_value = mock_instance

        pipeline = DailyPipeline(config, backend="keyword-only")
        results = pipeline.health_check()
        assert "claude_cli" in results


class TestCLIBackendFlag:
    def test_run_command_has_backend_option(self):
        import main
        params = {p.name for p in main.run.params}
        assert "backend" in params
