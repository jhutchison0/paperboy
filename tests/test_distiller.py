"""
Tests for BriefingDistiller prompt content and output validation.

The prose-style rules in SYSTEM_PROMPT are the deliberate, code-owned
channel for the writing-simple-and-direct kernel. The pipeline runs
`claude -p` in a neutral cwd precisely so workspace skills cannot leak
in; anything the briefing style needs must live in this prompt.
"""

from datetime import datetime, timezone

from src.config import PipelineConfig
from src.distiller import SYSTEM_PROMPT, BriefingDistiller
from src.models import BriefingDocument, Paper


class TestSystemPromptProseRules:
    """SYSTEM_PROMPT carries the briefing-adapted prose kernel."""

    def test_prompt_has_prose_style_section(self):
        assert "Prose rules" in SYSTEM_PROMPT

    def test_prompt_bans_em_dashes(self):
        assert "em dash" in SYSTEM_PROMPT.lower()

    def test_prompt_bans_cruft_words(self):
        for word in ["leverage", "utilize", "seamless", "delve", "holistic"]:
            assert word in SYSTEM_PROMPT, f"banned word '{word}' not named in prompt"

    def test_prompt_keeps_hedging_rule(self):
        assert "Hedge with numbers" in SYSTEM_PROMPT


def _make_doc(content: str) -> BriefingDocument:
    paper = Paper(
        id="2507.00001",
        title="Test Paper",
        authors=["A. Author"],
        abstract="An abstract.",
        published_date=datetime(2026, 7, 20, tzinfo=timezone.utc),
        url="https://arxiv.org/abs/2507.00001",
        categories=["cs.AI"],
        pdf_url="https://arxiv.org/pdf/2507.00001",
    )
    return BriefingDocument(
        title="Test Briefing",
        source_paper=paper,
        generated_at=datetime(2026, 7, 20, tzinfo=timezone.utc),
        content=content,
    )


class TestValidateBriefingProseRules:
    """_validate_briefing surfaces prose-rule violations as warnings."""

    def _distiller(self):
        cfg = PipelineConfig()
        cfg.distiller.target_word_count = 10
        return BriefingDistiller(cfg, claude_client=object(), agent_runner=None)

    def test_em_dashes_trigger_warning(self, caplog):
        doc = _make_doc("Why Should You Care — a lot. " * 4)
        with caplog.at_level("WARNING"):
            self._distiller()._validate_briefing(doc)
        assert any("em dash" in r.message.lower() for r in caplog.records)

    def test_no_em_dashes_no_warning(self, caplog):
        doc = _make_doc("Why Should You Care: a lot. " * 4)
        with caplog.at_level("WARNING"):
            self._distiller()._validate_briefing(doc)
        assert not any("em dash" in r.message.lower() for r in caplog.records)
