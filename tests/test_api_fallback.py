"""API fallback on current models (COURIER task 1.0): no sampling parameter,
thinking-first responses parse, scoring runs with thinking disabled."""

from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

from src.config import PipelineConfig
from src.distiller import BriefingDistiller
from src.models import Paper
from src.selector import PaperSelector

SRC = Path(__file__).resolve().parent.parent / "src"


def _paper() -> Paper:
    return Paper(
        id="2610.00001",
        title="A Paper",
        authors=["A. Author"],
        abstract="An abstract.",
        url="https://arxiv.org/abs/2610.00001",
        categories=["cs.AI"],
        pdf_url="https://arxiv.org/pdf/2610.00001",
        published_date=datetime(2026, 10, 20, tzinfo=timezone.utc),
    )


def _thinking_first(text: str):
    return SimpleNamespace(
        content=[
            SimpleNamespace(type="thinking", thinking="hmm"),
            SimpleNamespace(type="text", text=text),
        ],
        usage=SimpleNamespace(input_tokens=1, output_tokens=2),
    )


def _client(response):
    client = MagicMock()
    client.messages.create.return_value = response
    return client


class TestScoringCall:
    def test_parses_thinking_first_response(self):
        client = _client(_thinking_first("SCORE: 8\nREASONING: relevant"))
        selector = PaperSelector(PipelineConfig(), claude_client=client)
        score, reasoning = selector._score_with_claude(_paper())
        assert score == 0.8
        assert reasoning == "relevant"

    def test_sends_thinking_disabled_low_effort_no_temperature(self):
        client = _client(_thinking_first("SCORE: 5\nREASONING: ok"))
        selector = PaperSelector(PipelineConfig(), claude_client=client)
        selector._score_with_claude(_paper())
        kwargs = client.messages.create.call_args.kwargs
        assert kwargs["thinking"] == {"type": "disabled"}
        assert kwargs["output_config"] == {"effort": "low"}
        assert kwargs["max_tokens"] == 200
        assert "temperature" not in kwargs


class TestDistillCall:
    def test_parses_thinking_first_response(self):
        client = _client(_thinking_first("# Briefing body"))
        distiller = BriefingDistiller(PipelineConfig(), claude_client=client)
        assert distiller._generate_briefing(_paper(), "text") == "# Briefing body"
        assert "temperature" not in client.messages.create.call_args.kwargs


def test_no_temperature_in_sdk_call_sites():
    for name in ("selector.py", "distiller.py"):
        assert "temperature" not in (SRC / name).read_text(), name
