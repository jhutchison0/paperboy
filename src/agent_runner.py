"""
Claude Code CLI backend for pipeline tasks.

Invokes `claude -p "prompt"` as a subprocess, giving users without an
ANTHROPIC_API_KEY a path to run semantic scoring and briefing distillation
using their existing Max subscription.

The AgentRunner is a TOOL, not an operator. The pipeline calls it with
specific prompts and validates its output. It never self-directs.

Design constraints:
- prompt-only invocations (no worktree, no file I/O) for scoring
- distill_paper() accepts a pre-built prompt from the distiller layer
- malformed output → return None → caller falls back gracefully
- sensitive env vars stripped before every subprocess call
"""

import json
import logging
import os
import subprocess
from typing import Optional

from src.config import FocusAreas, PipelineConfig
from src.models import Paper

logger = logging.getLogger(__name__)

# Sections that must be present in a valid briefing (matches distiller.py checks)
_REQUIRED_BRIEFING_SECTIONS = [
    "Why Should You Care",
    "Core Intuition",
    "Technical Sketch",
    "Evidence",
    "Challenger",
    "Decision Support",
    "Open Questions",
    "Key Takeaways",
]


class AgentRunner:
    """
    Invokes Claude Code CLI as a subprocess for pipeline tasks.

    Covers two pipeline tasks:
      - score_paper(): returns {"score": float, "reasoning": str} or None
      - distill_paper(): returns markdown string or None

    Both methods follow the same contract: valid output is returned as-is;
    any failure (timeout, bad JSON, missing sections) returns None so the
    caller can fall back cleanly.
    """

    def __init__(self, config: PipelineConfig):
        self.config = config
        ar = config.agent_runner
        self.score_timeout = ar.score_timeout
        self.distill_timeout = ar.distill_timeout
        self.max_retries = ar.max_retries
        self.max_output_bytes = ar.max_output_bytes

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def score_paper(self, paper: Paper, focus_areas: FocusAreas) -> Optional[dict]:
        """
        Score a paper via Claude Code CLI.

        Args:
            paper: The paper to score.
            focus_areas: Research interests used to calibrate the score.

        Returns:
            Dict with keys "score" (float 0.0-1.0) and "reasoning" (str),
            or None if the invocation fails or returns malformed output.
        """
        prompt = self._build_scoring_prompt(paper, focus_areas)
        attempts = 0
        while attempts <= self.max_retries:
            attempts += 1
            raw = self._invoke(prompt, timeout=self.score_timeout)
            if raw is None:
                logger.warning(
                    f"AgentRunner: score_paper invocation returned None "
                    f"(attempt {attempts}/{self.max_retries + 1})"
                )
                continue

            cleaned = self._strip_preamble_json(raw)
            result = self._validate_score(cleaned)
            if result is not None:
                return result

            logger.warning(
                f"AgentRunner: score_paper output invalid "
                f"(attempt {attempts}/{self.max_retries + 1}): {cleaned[:200]!r}"
            )

        logger.warning(
            f"AgentRunner: score_paper failed after {attempts} attempt(s) "
            f"for '{paper.title[:60]}' — returning None"
        )
        return None

    def distill_paper(
        self,
        paper: Paper,
        distiller_config,
        system_prompt: str,
        user_prompt: str,
    ) -> Optional[str]:
        """
        Generate a briefing via Claude Code CLI.

        The prompt is built by the distiller layer (distiller-dev owns that).
        This method only handles subprocess invocation and output validation.

        Args:
            paper: Source paper (used for validation logging).
            distiller_config: DistillerConfig (used for word count bounds).
            system_prompt: System context (incorporated into the full prompt).
            user_prompt: The main distillation prompt built by the distiller.

        Returns:
            Validated markdown string, or None on failure.
        """
        # Combine system + user prompt for CLI invocation (no separate system arg in CLI)
        combined_prompt = f"{system_prompt}\n\n---\n\n{user_prompt}"

        attempts = 0
        while attempts <= self.max_retries:
            attempts += 1
            raw = self._invoke(combined_prompt, timeout=self.distill_timeout)
            if raw is None:
                logger.warning(
                    f"AgentRunner: distill_paper invocation returned None "
                    f"(attempt {attempts}/{self.max_retries + 1})"
                )
                continue

            cleaned = self._strip_preamble_markdown(raw)
            errors = self._validate_briefing(cleaned, distiller_config)
            if not errors:
                return cleaned

            logger.warning(
                f"AgentRunner: distill_paper output has validation issues "
                f"(attempt {attempts}/{self.max_retries + 1}): {errors}"
            )

        logger.warning(
            f"AgentRunner: distill_paper failed after {attempts} attempt(s) "
            f"for '{paper.title[:60]}' — returning None"
        )
        return None

    def is_available(self) -> bool:
        """
        Check whether the claude CLI is on PATH and responsive.

        Returns:
            True if `claude --version` exits cleanly, False otherwise.
        """
        try:
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                timeout=10,
                env=self._build_clean_env(),
                stdin=subprocess.DEVNULL,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            return False

    # ------------------------------------------------------------------
    # Low-level invocation
    # ------------------------------------------------------------------

    def _invoke(self, prompt: str, timeout: int, max_output_bytes: int = 0) -> Optional[str]:
        """
        Run `claude -p <prompt>` as a subprocess with guardrails.

        Guardrails:
          - Sensitive env vars stripped (API keys, CLAUDE* vars)
          - stdin routed to /dev/null (non-interactive)
          - Hard timeout via subprocess.run(..., timeout=N)
          - stdout truncated at max_output_bytes

        Args:
            prompt: The full prompt string to pass to claude -p.
            timeout: Seconds before the process is killed.
            max_output_bytes: Output size cap. Defaults to self.max_output_bytes.

        Returns:
            stdout as a string, or None on any failure.
        """
        if max_output_bytes == 0:
            max_output_bytes = self.max_output_bytes

        clean_env = self._build_clean_env()

        try:
            result = subprocess.run(
                ["claude", "-p", prompt],
                capture_output=True,
                timeout=timeout,
                env=clean_env,
                stdin=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            logger.error("AgentRunner: 'claude' not found on PATH — install Claude Code CLI")
            return None
        except subprocess.TimeoutExpired:
            logger.warning(f"AgentRunner: invocation timed out after {timeout}s")
            return None
        except OSError as exc:
            logger.error(f"AgentRunner: OS error during invocation: {exc}")
            return None

        if result.returncode != 0:
            stderr_snippet = result.stderr[:500].decode("utf-8", errors="replace") if result.stderr else ""
            logger.warning(
                f"AgentRunner: claude exited with code {result.returncode}. "
                f"stderr: {stderr_snippet!r}"
            )
            return None

        raw_bytes = result.stdout
        if len(raw_bytes) > max_output_bytes:
            logger.warning(
                f"AgentRunner: output truncated from {len(raw_bytes)} to {max_output_bytes} bytes"
            )
            raw_bytes = raw_bytes[:max_output_bytes]

        return raw_bytes.decode("utf-8", errors="replace")

    # ------------------------------------------------------------------
    # Output cleaning
    # ------------------------------------------------------------------

    def _strip_preamble_json(self, output: str) -> str:
        """
        Strip non-JSON preamble from Claude CLI output.

        The CLI sometimes prints preamble text before the JSON payload.
        Find the first '{' and last '}' and return that substring.

        Args:
            output: Raw stdout from the CLI.

        Returns:
            The JSON substring, or the original string if no braces found.
        """
        start = output.find("{")
        end = output.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return output
        return output[start : end + 1]

    def _strip_preamble_markdown(self, output: str) -> str:
        """
        Strip non-markdown preamble from Claude CLI output.

        Find the first occurrence of a markdown heading ('#') or a YAML
        front-matter delimiter ('---') and return from that point onward.

        Args:
            output: Raw stdout from the CLI.

        Returns:
            The markdown substring, or the original string if no marker found.
        """
        lines = output.split("\n")
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("#") or stripped == "---":
                return "\n".join(lines[i:])
        return output

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    def _validate_score(self, text: str) -> Optional[dict]:
        """
        Parse and validate a scoring JSON response.

        Expected format: {"score": <float 0-1>, "reasoning": <str>}

        Returns:
            Validated dict, or None if parsing or validation fails.
        """
        try:
            data = json.loads(text.strip())
            score = float(data["score"])
            reasoning = data["reasoning"]
            if not (0.0 <= score <= 1.0):
                logger.warning(f"AgentRunner: score {score} out of [0, 1] range")
                return None
            if not isinstance(reasoning, str):
                logger.warning("AgentRunner: reasoning field is not a string")
                return None
            return {"score": round(score, 3), "reasoning": reasoning}
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            logger.debug(f"AgentRunner: score validation failed: {exc}")
            return None

    def _validate_briefing(self, content: str, distiller_config) -> list[str]:
        """
        Validate that a briefing has required sections and acceptable word count.

        Mirrors the checks in distiller.py._validate_briefing() but returns
        a list of error strings instead of just logging warnings, so the
        caller can decide whether to retry.

        Args:
            content: Generated markdown string.
            distiller_config: DistillerConfig providing target_word_count.

        Returns:
            List of error strings. Empty list means the briefing is valid.
        """
        errors: list[str] = []

        content_lower = content.lower()
        for section in _REQUIRED_BRIEFING_SECTIONS:
            if section.lower() not in content_lower:
                errors.append(f"Missing section: '{section}'")

        word_count = len(content.split())
        target = distiller_config.target_word_count
        min_words = int(target * 0.5)   # 50% lower bound (lenient for CLI output)
        max_words = int(target * 1.5)   # 50% upper bound

        if word_count < min_words:
            errors.append(f"Too short: {word_count} words (min {min_words})")
        elif word_count > max_words:
            errors.append(f"Too long: {word_count} words (max {max_words})")

        return errors

    # ------------------------------------------------------------------
    # Prompt construction
    # ------------------------------------------------------------------

    def _build_scoring_prompt(self, paper: Paper, focus_areas: FocusAreas) -> str:
        """
        Build the paper scoring prompt.

        Follows the Task 1 input format from the CONOP Section 4.
        Instructs the model to return only a JSON object.
        """
        primary_areas = "\n".join(f"  - {area}" for area in focus_areas.primary)
        keywords = ", ".join(focus_areas.keywords)
        authors_str = ", ".join(paper.authors[:5])
        abstract_excerpt = paper.abstract[:1500]

        return f"""Score this paper's relevance to the research interests below.
Return ONLY a JSON object with no other text, no markdown fencing, no preamble.

Paper:
  Title: {paper.title}
  Authors: {authors_str}
  Abstract: {abstract_excerpt}
  Categories: {", ".join(paper.categories)}

Research interests:
  Primary areas:
{primary_areas}
  Keywords: {keywords}

Output format (JSON only):
{{"score": <float 0.0-1.0>, "reasoning": "<1-3 sentence explanation>"}}"""

    # ------------------------------------------------------------------
    # Environment helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_clean_env() -> dict:
        """
        Build an environment dict with sensitive variables removed.

        Strips ANTHROPIC_API_KEY and any CLAUDE* variables so the subprocess
        cannot access credentials or alter Claude Code's own configuration.
        PATH and all other system variables are preserved.

        Returns:
            A copy of os.environ with sensitive keys removed.
        """
        env = dict(os.environ)
        keys_to_remove = [
            key for key in env
            if key == "ANTHROPIC_API_KEY" or key.startswith("CLAUDE")
        ]
        for key in keys_to_remove:
            del env[key]
        return env
