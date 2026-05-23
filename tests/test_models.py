"""
Unit tests for src/models.py public behaviors.

Covers Article→Paper conversion (used by the selector to normalize blog
articles into the Paper type) and BriefingDocument auto-counted word count
(used by the distiller for length validation).
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import Article, BriefingDocument, Paper


def _sample_article() -> Article:
    return Article(
        title="Building Reliable AI Agents",
        url="https://example.com/agents-blog",
        published_date=datetime(2026, 3, 9, tzinfo=timezone.utc),
        source="AI Research Blog",
        summary="A practical guide to building AI agents with tool use.",
    )


class TestArticleToPaper:
    def test_to_paper_preserves_title(self):
        paper = _sample_article().to_paper()
        assert paper.title == "Building Reliable AI Agents"

    def test_to_paper_maps_summary_to_abstract(self):
        """The Paper type uses 'abstract'; Article uses 'summary'. Conversion
        must map summary→abstract so downstream scoring sees the same field."""
        article = _sample_article()
        paper = article.to_paper()
        assert paper.abstract == article.summary

    def test_to_paper_returns_paper_instance(self):
        assert isinstance(_sample_article().to_paper(), Paper)


class TestBriefingDocumentWordCount:
    def test_word_count_auto_computed_from_content(self):
        """When word_count is not provided, __post_init__ counts whitespace-
        separated tokens in `content`."""
        doc = BriefingDocument(
            title="Test",
            source_paper=_sample_article().to_paper(),
            generated_at=datetime.now(timezone.utc),
            content="This is a test briefing with exactly ten words in it.",
        )
        assert doc.word_count == 11

    def test_word_count_respects_explicit_override(self):
        """If word_count is passed explicitly (non-zero), __post_init__ leaves
        it alone — the distiller can supply a curated count when needed."""
        doc = BriefingDocument(
            title="Test",
            source_paper=_sample_article().to_paper(),
            generated_at=datetime.now(timezone.utc),
            content="ignored ignored ignored",
            word_count=4500,
        )
        assert doc.word_count == 4500
