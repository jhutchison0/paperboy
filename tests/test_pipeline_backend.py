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
from src.pipeline import DailyPipeline


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
