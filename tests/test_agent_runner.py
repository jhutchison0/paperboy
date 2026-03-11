"""
Unit tests for src/agent_runner.py.

All subprocess calls are mocked — no real 'claude' CLI is invoked.
Tests cover:
  1. _invoke() basics: timeout, env stripping, stdin, output truncation
  2. _strip_preamble_json(): clean JSON, JSON with preamble, no JSON
  3. _strip_preamble_markdown(): clean markdown, markdown with preamble
  4. score_paper(): valid response → dict, malformed → None
  5. distill_paper(): valid markdown → str, missing sections → None
  6. is_available(): claude on PATH → True, not on PATH → False
  7. _build_clean_env(): ANTHROPIC_API_KEY stripped, PATH preserved
  8. Config loading: agent_runner section loads from YAML correctly
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure project root is on sys.path so src.* imports resolve
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent_runner import AgentRunner
from src.config import AgentRunnerConfig, FocusAreas, PipelineConfig
from src.models import Paper


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def config():
    """Minimal PipelineConfig with agent_runner defaults."""
    cfg = PipelineConfig()
    cfg.agent_runner = AgentRunnerConfig(
        enabled=True,
        score_timeout=30,
        distill_timeout=120,
        max_retries=0,        # no retries in most tests — keeps them deterministic
        max_output_bytes=51200,
        batch_size=1,
    )
    cfg.focus_areas = FocusAreas(
        primary=["LLMs for decision support", "Knowledge graphs"],
        keywords=["llm", "transformer", "knowledge graph"],
    )
    return cfg


@pytest.fixture
def runner(config):
    """AgentRunner instance built from the test config."""
    return AgentRunner(config)


@pytest.fixture
def sample_paper():
    """A minimal Paper for testing."""
    return Paper(
        id="2603.99999",
        title="Test Paper on LLM Reasoning",
        authors=["Alice Test", "Bob Example"],
        abstract="We test how well LLMs reason about knowledge graphs.",
        published_date=datetime(2026, 3, 10, tzinfo=timezone.utc),
        url="https://arxiv.org/abs/2603.99999",
        categories=["cs.AI", "cs.CL"],
        pdf_url="https://arxiv.org/pdf/2603.99999",
        source="arxiv",
    )


@pytest.fixture
def focus_areas():
    return FocusAreas(
        primary=["LLMs for decision support", "Knowledge graphs and reasoning"],
        keywords=["llm", "knowledge graph", "reasoning"],
    )


def _make_completed_process(stdout: str = "", returncode: int = 0, stderr: str = "") -> MagicMock:
    """Build a mock subprocess.CompletedProcess-like object."""
    mock = MagicMock()
    mock.returncode = returncode
    mock.stdout = stdout.encode("utf-8")
    mock.stderr = stderr.encode("utf-8")
    return mock


# ---------------------------------------------------------------------------
# 1. _invoke() basics
# ---------------------------------------------------------------------------

class TestInvoke:
    def test_invoke_returns_stdout_on_success(self, runner):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _make_completed_process(stdout="hello world")
            result = runner._invoke("some prompt", timeout=30)
        assert result == "hello world"

    def test_invoke_returns_none_on_nonzero_exit(self, runner):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _make_completed_process(returncode=1, stderr="error msg")
            result = runner._invoke("some prompt", timeout=30)
        assert result is None

    def test_invoke_returns_none_on_timeout(self, runner):
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="claude", timeout=30)):
            result = runner._invoke("some prompt", timeout=30)
        assert result is None

    def test_invoke_returns_none_when_claude_not_found(self, runner):
        with patch("subprocess.run", side_effect=FileNotFoundError("claude not found")):
            result = runner._invoke("some prompt", timeout=30)
        assert result is None

    def test_invoke_truncates_output_at_max_bytes(self, runner):
        long_output = "x" * 1000
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _make_completed_process(stdout=long_output)
            result = runner._invoke("some prompt", timeout=30, max_output_bytes=100)
        assert result is not None
        assert len(result) == 100

    def test_invoke_uses_devnull_stdin(self, runner):
        """subprocess.run must be called with stdin=subprocess.DEVNULL."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _make_completed_process(stdout="ok")
            runner._invoke("some prompt", timeout=30)
        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs.get("stdin") == subprocess.DEVNULL

    def test_invoke_passes_timeout_to_subprocess(self, runner):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _make_completed_process(stdout="ok")
            runner._invoke("some prompt", timeout=42)
        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs.get("timeout") == 42

    def test_invoke_passes_clean_env_to_subprocess(self, runner):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _make_completed_process(stdout="ok")
            runner._invoke("some prompt", timeout=30)
        call_kwargs = mock_run.call_args.kwargs
        env = call_kwargs.get("env", {})
        assert "ANTHROPIC_API_KEY" not in env

    def test_invoke_builds_correct_command(self, runner):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _make_completed_process(stdout="ok")
            runner._invoke("my test prompt", timeout=30)
        call_args = mock_run.call_args.args[0]
        assert call_args == ["claude", "-p", "my test prompt"]

    def test_invoke_handles_os_error(self, runner):
        with patch("subprocess.run", side_effect=OSError("permission denied")):
            result = runner._invoke("some prompt", timeout=30)
        assert result is None


# ---------------------------------------------------------------------------
# 2. _strip_preamble_json()
# ---------------------------------------------------------------------------

class TestStripPreambleJson:
    def test_clean_json_unchanged(self, runner):
        payload = '{"score": 0.8, "reasoning": "Highly relevant."}'
        assert runner._strip_preamble_json(payload) == payload

    def test_strips_leading_text(self, runner):
        output = 'Here is my response:\n\n{"score": 0.7, "reasoning": "relevant"}'
        result = runner._strip_preamble_json(output)
        assert result == '{"score": 0.7, "reasoning": "relevant"}'

    def test_strips_trailing_text(self, runner):
        output = '{"score": 0.5, "reasoning": "ok"}\n\nLet me know if you need more.'
        result = runner._strip_preamble_json(output)
        assert result == '{"score": 0.5, "reasoning": "ok"}'

    def test_strips_both_preamble_and_postamble(self, runner):
        output = 'Some preamble.\n{"score": 0.9, "reasoning": "great"}\nSome postamble.'
        result = runner._strip_preamble_json(output)
        assert result == '{"score": 0.9, "reasoning": "great"}'

    def test_no_braces_returns_original(self, runner):
        output = "No JSON here at all."
        assert runner._strip_preamble_json(output) == output

    def test_nested_json_preserved(self, runner):
        output = 'preamble {"score": 0.6, "meta": {"k": "v"}} postamble'
        result = runner._strip_preamble_json(output)
        # Should find first { and last }
        assert result == '{"score": 0.6, "meta": {"k": "v"}}'


# ---------------------------------------------------------------------------
# 3. _strip_preamble_markdown()
# ---------------------------------------------------------------------------

class TestStripPreambleMarkdown:
    def test_clean_markdown_unchanged(self, runner):
        md = "# My Title\n\nSome content."
        assert runner._strip_preamble_markdown(md) == md

    def test_strips_preamble_before_heading(self, runner):
        output = "Sure, here is the briefing:\n\n# My Title\n\nContent."
        result = runner._strip_preamble_markdown(output)
        assert result == "# My Title\n\nContent."

    def test_strips_preamble_before_yaml_frontmatter(self, runner):
        output = "Here you go:\n---\ntitle: Test\n---\n\n# Section"
        result = runner._strip_preamble_markdown(output)
        assert result == "---\ntitle: Test\n---\n\n# Section"

    def test_no_marker_returns_original(self, runner):
        output = "This has no heading or frontmatter."
        assert runner._strip_preamble_markdown(output) == output

    def test_heading_at_first_line(self, runner):
        output = "# Already starts with heading\n\nContent."
        assert runner._strip_preamble_markdown(output) == output


# ---------------------------------------------------------------------------
# 4. score_paper()
# ---------------------------------------------------------------------------

class TestScorePaper:
    def test_valid_json_response_returns_dict(self, runner, sample_paper, focus_areas):
        payload = json.dumps({"score": 0.85, "reasoning": "Highly relevant to LLM reasoning."})
        with patch.object(runner, "_invoke", return_value=payload):
            result = runner.score_paper(sample_paper, focus_areas)
        assert result is not None
        assert result["score"] == pytest.approx(0.85)
        assert "reasoning" in result

    def test_valid_json_with_preamble_returns_dict(self, runner, sample_paper, focus_areas):
        payload = 'Claude says:\n{"score": 0.72, "reasoning": "Good match."}'
        with patch.object(runner, "_invoke", return_value=payload):
            result = runner.score_paper(sample_paper, focus_areas)
        assert result is not None
        assert result["score"] == pytest.approx(0.72)

    def test_malformed_json_returns_none(self, runner, sample_paper, focus_areas):
        with patch.object(runner, "_invoke", return_value="not valid json at all"):
            result = runner.score_paper(sample_paper, focus_areas)
        assert result is None

    def test_score_out_of_range_returns_none(self, runner, sample_paper, focus_areas):
        payload = json.dumps({"score": 1.5, "reasoning": "Too high."})
        with patch.object(runner, "_invoke", return_value=payload):
            result = runner.score_paper(sample_paper, focus_areas)
        assert result is None

    def test_missing_reasoning_key_returns_none(self, runner, sample_paper, focus_areas):
        payload = json.dumps({"score": 0.5})
        with patch.object(runner, "_invoke", return_value=payload):
            result = runner.score_paper(sample_paper, focus_areas)
        assert result is None

    def test_invoke_failure_returns_none(self, runner, sample_paper, focus_areas):
        with patch.object(runner, "_invoke", return_value=None):
            result = runner.score_paper(sample_paper, focus_areas)
        assert result is None

    def test_score_rounded_to_three_decimals(self, runner, sample_paper, focus_areas):
        payload = json.dumps({"score": 0.123456789, "reasoning": "ok"})
        with patch.object(runner, "_invoke", return_value=payload):
            result = runner.score_paper(sample_paper, focus_areas)
        assert result is not None
        assert result["score"] == pytest.approx(0.123, abs=1e-3)

    def test_retries_on_failure(self, config, sample_paper, focus_areas):
        """With max_retries=1, a bad first response is retried once."""
        config.agent_runner.max_retries = 1
        runner = AgentRunner(config)

        good_payload = json.dumps({"score": 0.9, "reasoning": "great"})
        responses = [None, good_payload]  # first fails, second succeeds

        with patch.object(runner, "_invoke", side_effect=responses):
            result = runner.score_paper(sample_paper, focus_areas)
        assert result is not None
        assert result["score"] == pytest.approx(0.9)


# ---------------------------------------------------------------------------
# 5. distill_paper()
# ---------------------------------------------------------------------------

def _make_valid_briefing(distiller_config) -> str:
    """Generate a briefing stub that passes all validation checks."""
    target = distiller_config.target_word_count
    # Each section header + filler words to hit the target
    sections = [
        "# Research Briefing\n\n---\ntitle: Test\n---\n\n",
        "## 1. Opening Hook: Why Should You Care?\n\n",
        "## 2. The Core Intuition\n\n",
        "## 3. The Technical Sketch\n\n",
        "## 4. The Evidence: Did It Actually Work?\n\n",
        "## 5. The Challengers' Corner\n\n",
        "## 6. Connection to Decision Support and Real-World Impact\n\n",
        "## 7. Open Questions and Future Directions\n\n",
        "## 8. Key Takeaways\n\n",
    ]
    content = "".join(sections)
    # Pad word count to within acceptable range
    current_words = len(content.split())
    words_needed = target - current_words
    if words_needed > 0:
        content += " filler" * words_needed
    return content


class TestDistillPaper:
    def test_valid_markdown_returns_string(self, runner, config, sample_paper):
        valid_md = _make_valid_briefing(config.distiller)
        with patch.object(runner, "_invoke", return_value=valid_md):
            result = runner.distill_paper(
                paper=sample_paper,
                distiller_config=config.distiller,
                system_prompt="You are an expert.",
                user_prompt="Distill this paper.",
            )
        assert result is not None
        assert isinstance(result, str)
        assert "Why Should You Care" in result

    def test_preamble_stripped_before_validation(self, runner, config, sample_paper):
        valid_md = _make_valid_briefing(config.distiller)
        output_with_preamble = "Sure, here is the briefing:\n\n" + valid_md
        with patch.object(runner, "_invoke", return_value=output_with_preamble):
            result = runner.distill_paper(
                paper=sample_paper,
                distiller_config=config.distiller,
                system_prompt="You are an expert.",
                user_prompt="Distill this paper.",
            )
        assert result is not None

    def test_missing_sections_returns_none(self, runner, config, sample_paper):
        # A briefing missing most required sections
        bad_md = "# Research Briefing\n\nThis is a very short and incomplete document." + " word" * 1000
        with patch.object(runner, "_invoke", return_value=bad_md):
            result = runner.distill_paper(
                paper=sample_paper,
                distiller_config=config.distiller,
                system_prompt="You are an expert.",
                user_prompt="Distill this paper.",
            )
        assert result is None

    def test_too_short_returns_none(self, runner, config, sample_paper):
        # Build a briefing with all required sections but too few words
        sections_text = (
            "# Research Briefing\n\n"
            "## Why Should You Care?\n\n"
            "## Core Intuition\n\n"
            "## Technical Sketch\n\n"
            "## Evidence\n\n"
            "## Challenger\n\n"
            "## Decision Support\n\n"
            "## Open Questions\n\n"
            "## Key Takeaways\n\n"
        )
        with patch.object(runner, "_invoke", return_value=sections_text):
            result = runner.distill_paper(
                paper=sample_paper,
                distiller_config=config.distiller,
                system_prompt="You are an expert.",
                user_prompt="Distill this paper.",
            )
        assert result is None

    def test_invoke_failure_returns_none(self, runner, config, sample_paper):
        with patch.object(runner, "_invoke", return_value=None):
            result = runner.distill_paper(
                paper=sample_paper,
                distiller_config=config.distiller,
                system_prompt="sys",
                user_prompt="usr",
            )
        assert result is None

    def test_system_and_user_prompts_combined(self, runner, config, sample_paper):
        """Both system_prompt and user_prompt are included in the final _invoke call."""
        valid_md = _make_valid_briefing(config.distiller)
        captured = {}

        def capture_invoke(prompt, timeout, **kwargs):
            captured["prompt"] = prompt
            return valid_md

        with patch.object(runner, "_invoke", side_effect=capture_invoke):
            runner.distill_paper(
                paper=sample_paper,
                distiller_config=config.distiller,
                system_prompt="SYSTEM_CONTEXT",
                user_prompt="USER_TASK",
            )

        assert "SYSTEM_CONTEXT" in captured["prompt"]
        assert "USER_TASK" in captured["prompt"]


# ---------------------------------------------------------------------------
# 6. is_available()
# ---------------------------------------------------------------------------

class TestIsAvailable:
    def test_returns_true_when_claude_on_path(self, runner):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _make_completed_process(stdout="claude 1.0.0", returncode=0)
            assert runner.is_available() is True

    def test_returns_false_when_claude_not_found(self, runner):
        with patch("subprocess.run", side_effect=FileNotFoundError("no claude")):
            assert runner.is_available() is False

    def test_returns_false_when_claude_times_out(self, runner):
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="claude", timeout=10)):
            assert runner.is_available() is False

    def test_returns_false_when_nonzero_exit(self, runner):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _make_completed_process(returncode=1)
            assert runner.is_available() is False


# ---------------------------------------------------------------------------
# 7. _build_clean_env()
# ---------------------------------------------------------------------------

class TestBuildCleanEnv:
    def test_anthropic_api_key_stripped(self):
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-secret-key", "PATH": "/usr/bin"}):
            env = AgentRunner._build_clean_env()
        assert "ANTHROPIC_API_KEY" not in env

    def test_claude_vars_stripped(self):
        with patch.dict("os.environ", {
            "CLAUDE_API_KEY": "some-key",
            "CLAUDECODE_SESSION": "abc123",
            "PATH": "/usr/bin",
        }):
            env = AgentRunner._build_clean_env()
        assert "CLAUDE_API_KEY" not in env
        assert "CLAUDECODE_SESSION" not in env

    def test_path_preserved(self):
        with patch.dict("os.environ", {"PATH": "/usr/local/bin:/usr/bin", "ANTHROPIC_API_KEY": "key"}):
            env = AgentRunner._build_clean_env()
        assert env["PATH"] == "/usr/local/bin:/usr/bin"

    def test_other_vars_preserved(self):
        with patch.dict("os.environ", {"HOME": "/home/user", "LANG": "en_US.UTF-8"}):
            env = AgentRunner._build_clean_env()
        assert env.get("HOME") == "/home/user"
        assert env.get("LANG") == "en_US.UTF-8"

    def test_returns_copy_not_original(self):
        """Modifications to the returned dict must not affect os.environ."""
        env = AgentRunner._build_clean_env()
        env["INJECTED_KEY"] = "injected"
        import os
        assert "INJECTED_KEY" not in os.environ


# ---------------------------------------------------------------------------
# 8. Config loading
# ---------------------------------------------------------------------------

class TestConfigLoading:
    def test_agent_runner_defaults_on_empty_config(self):
        cfg = PipelineConfig()
        ar = cfg.agent_runner
        assert ar.enabled is True
        assert ar.score_timeout == 30
        assert ar.distill_timeout == 120
        assert ar.max_retries == 1
        assert ar.max_output_bytes == 51200
        assert ar.batch_size == 1

    def test_agent_runner_config_loaded_from_yaml(self, tmp_path):
        """Values in YAML override the dataclass defaults."""
        yaml_content = """
pipeline:
  output_dir: ./output
  max_papers_to_fetch: 10
  max_papers_to_score: 5
  days_lookback: 3
  log_level: INFO
arxiv:
  categories:
    - cs.AI
focus_areas:
  keywords:
    - llm
agent_runner:
  enabled: false
  score_timeout: 60
  distill_timeout: 240
  max_retries: 2
  max_output_bytes: 102400
  batch_size: 3
"""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(yaml_content)

        cfg = PipelineConfig.load(config_path=str(config_file))
        ar = cfg.agent_runner

        assert ar.enabled is False
        assert ar.score_timeout == 60
        assert ar.distill_timeout == 240
        assert ar.max_retries == 2
        assert ar.max_output_bytes == 102400
        assert ar.batch_size == 3

    def test_agent_runner_section_missing_uses_defaults(self, tmp_path):
        """YAML without agent_runner section still produces valid defaults."""
        yaml_content = """
pipeline:
  output_dir: ./output
  max_papers_to_fetch: 10
  max_papers_to_score: 5
  days_lookback: 3
  log_level: INFO
arxiv:
  categories:
    - cs.AI
focus_areas:
  keywords:
    - llm
"""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(yaml_content)

        cfg = PipelineConfig.load(config_path=str(config_file))
        ar = cfg.agent_runner

        assert ar.enabled is True
        assert ar.score_timeout == 30
        assert ar.distill_timeout == 120

    def test_validate_no_api_key_is_warning_not_hard_error(self, tmp_path):
        """
        Without ANTHROPIC_API_KEY the validate() list is non-empty,
        but the message is informational (warns about fallback).
        Critical: ArXiv + keywords errors still appear as hard errors.
        """
        yaml_content = """
pipeline:
  output_dir: ./output
  max_papers_to_fetch: 10
  max_papers_to_score: 5
  days_lookback: 3
  log_level: INFO
arxiv:
  categories:
    - cs.AI
focus_areas:
  keywords:
    - llm
"""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(yaml_content)

        import os
        env_without_key = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        with patch.dict("os.environ", env_without_key, clear=True):
            cfg = PipelineConfig.load(config_path=str(config_file))

        errors = cfg.validate()
        # The missing-API-key message should be present but framed as a fallback notice
        api_key_msgs = [e for e in errors if "ANTHROPIC_API_KEY" in e]
        assert len(api_key_msgs) == 1
        # Should NOT say "not set" alone — should mention fallback behavior
        assert "AgentRunner" in api_key_msgs[0] or "keyword-only" in api_key_msgs[0]
