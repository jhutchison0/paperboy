"""
Tests for PipelineConfig validation.

Covers range checks, required fields, and warning vs. error separation
added in Phase 2 (Configuration & Polish).
"""

import pytest
from src.config import PipelineConfig


def _make_valid_config():
    """Create a valid PipelineConfig with required fields populated."""
    cfg = PipelineConfig(anthropic_api_key="test-key")
    cfg.arxiv.categories = ["cs.AI"]
    cfg.focus_areas.keywords = ["llm"]
    return cfg


class TestValidateReturnsStructure:
    """validate() returns (errors, warnings) tuple."""

    def test_valid_config_returns_empty_errors(self):
        cfg = _make_valid_config()
        errors, warnings = cfg.validate()
        assert errors == []

    def test_return_type_is_tuple_of_lists(self):
        cfg = _make_valid_config()
        result = cfg.validate()
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], list)
        assert isinstance(result[1], list)


class TestRequiredContent:
    """Missing required content produces errors."""

    def test_no_arxiv_categories(self):
        cfg = _make_valid_config()
        cfg.arxiv.categories = []
        errors, _ = cfg.validate()
        assert any("ArXiv categories" in e for e in errors)

    def test_no_keywords(self):
        cfg = _make_valid_config()
        cfg.focus_areas.keywords = []
        errors, _ = cfg.validate()
        assert any("keywords" in e for e in errors)


class TestApiKeyIsWarning:
    """Missing API key is a warning, not an error."""

    def test_missing_api_key_is_warning(self):
        cfg = _make_valid_config()
        cfg.anthropic_api_key = ""
        errors, warnings = cfg.validate()
        assert not any("ANTHROPIC_API_KEY" in e for e in errors)
        assert any("ANTHROPIC_API_KEY" in w for w in warnings)

    def test_present_api_key_no_warning(self):
        cfg = _make_valid_config()
        errors, warnings = cfg.validate()
        assert not any("ANTHROPIC_API_KEY" in w for w in warnings)


class TestPlaceholderApiKey:
    """Placeholder key from .env.example is caught and treated as unset."""

    def test_placeholder_emits_warning(self):
        cfg = _make_valid_config()
        cfg.anthropic_api_key = "sk-ant-your-key-here"
        _, warnings = cfg.validate()
        assert any("placeholder" in w.lower() for w in warnings)

    def test_placeholder_blanked_after_validate(self):
        cfg = _make_valid_config()
        cfg.anthropic_api_key = "sk-ant-your-key-here"
        cfg.validate()
        assert cfg.anthropic_api_key == ""

    def test_real_key_passes_through(self):
        cfg = _make_valid_config()
        cfg.anthropic_api_key = "sk-ant-real-key-abcdef"
        cfg.validate()
        assert cfg.anthropic_api_key == "sk-ant-real-key-abcdef"


class TestClaudeRangeChecks:
    """Claude config range validation."""

    @pytest.mark.parametrize("temp", [-0.1, 1.5, 2.0])
    def test_temperature_out_of_range(self, temp):
        cfg = _make_valid_config()
        cfg.claude.temperature = temp
        errors, _ = cfg.validate()
        assert any("temperature" in e for e in errors)

    @pytest.mark.parametrize("temp", [0.0, 0.5, 1.0])
    def test_temperature_valid(self, temp):
        cfg = _make_valid_config()
        cfg.claude.temperature = temp
        errors, _ = cfg.validate()
        assert not any("temperature" in e for e in errors)

    def test_max_tokens_zero(self):
        cfg = _make_valid_config()
        cfg.claude.max_tokens = 0
        errors, _ = cfg.validate()
        assert any("max_tokens" in e for e in errors)

    def test_max_tokens_negative(self):
        cfg = _make_valid_config()
        cfg.claude.max_tokens = -100
        errors, _ = cfg.validate()
        assert any("max_tokens" in e for e in errors)


class TestSelectorRangeChecks:
    """Selector config validation."""

    @pytest.mark.parametrize("threshold", [-0.1, 1.5])
    def test_min_score_threshold_out_of_range(self, threshold):
        cfg = _make_valid_config()
        cfg.selector.min_score_threshold = threshold
        errors, _ = cfg.validate()
        assert any("min_score_threshold" in e for e in errors)

    def test_top_k_for_claude_zero(self):
        cfg = _make_valid_config()
        cfg.selector.top_k_for_claude = 0
        errors, _ = cfg.validate()
        assert any("top_k_for_claude" in e for e in errors)

    def test_weight_sum_not_one_is_warning(self):
        cfg = _make_valid_config()
        cfg.selector.keyword_weight = 0.5
        cfg.selector.claude_weight = 0.8
        _, warnings = cfg.validate()
        assert any("keyword_weight" in w for w in warnings)

    def test_weight_sum_one_no_warning(self):
        cfg = _make_valid_config()
        cfg.selector.keyword_weight = 0.4
        cfg.selector.claude_weight = 0.6
        _, warnings = cfg.validate()
        assert not any("keyword_weight" in w for w in warnings)


class TestDistillerRangeChecks:
    """Distiller config validation."""

    def test_target_word_count_zero(self):
        cfg = _make_valid_config()
        cfg.distiller.target_word_count = 0
        errors, _ = cfg.validate()
        assert any("target_word_count" in e for e in errors)


class TestPipelineRangeChecks:
    """Pipeline-level config validation."""

    def test_days_lookback_zero(self):
        cfg = _make_valid_config()
        cfg.days_lookback = 0
        errors, _ = cfg.validate()
        assert any("days_lookback" in e for e in errors)

    def test_days_lookback_negative(self):
        cfg = _make_valid_config()
        cfg.days_lookback = -1
        errors, _ = cfg.validate()
        assert any("days_lookback" in e for e in errors)

    def test_dedup_cooldown_days_loaded_from_yaml(self):
        """dedup_cooldown_days is loaded from config YAML."""
        cfg = PipelineConfig.load()
        assert cfg.dedup_cooldown_days == 30

    def test_dedup_cooldown_days_default(self):
        """Default dedup_cooldown_days is 30."""
        cfg = PipelineConfig()
        assert cfg.dedup_cooldown_days == 30


class TestAgentRunnerRangeChecks:
    """AgentRunner config validation."""

    def test_score_timeout_zero(self):
        cfg = _make_valid_config()
        cfg.agent_runner.score_timeout = 0
        errors, _ = cfg.validate()
        assert any("score_timeout" in e for e in errors)

    def test_distill_timeout_zero(self):
        cfg = _make_valid_config()
        cfg.agent_runner.distill_timeout = 0
        errors, _ = cfg.validate()
        assert any("distill_timeout" in e for e in errors)

    def test_max_output_bytes_zero(self):
        cfg = _make_valid_config()
        cfg.agent_runner.max_output_bytes = 0
        errors, _ = cfg.validate()
        assert any("max_output_bytes" in e for e in errors)

    def test_max_retries_negative(self):
        cfg = _make_valid_config()
        cfg.agent_runner.max_retries = -1
        errors, _ = cfg.validate()
        assert any("max_retries" in e for e in errors)

    def test_max_retries_zero_is_valid(self):
        cfg = _make_valid_config()
        cfg.agent_runner.max_retries = 0
        errors, _ = cfg.validate()
        assert not any("max_retries" in e for e in errors)
