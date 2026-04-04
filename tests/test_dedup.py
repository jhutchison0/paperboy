"""
Tests for cross-run paper deduplication.

Covers:
- Paper ID normalization (ArXiv URLs, prefixed, bare, blog URLs)
- SelectionHistory persistence and cooldown window
- Selector integration with exclude_ids
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import Paper, normalize_paper_id
from src.pipeline import SelectionHistory
from src.selector import PaperSelector
from src.config import PipelineConfig


# ── Fixtures ──────────────────────────────────────────────────────


@pytest.fixture
def config():
    return PipelineConfig.load()


@pytest.fixture
def history_file(tmp_path):
    return tmp_path / ".selection_history.json"


@pytest.fixture
def sample_paper():
    return Paper(
        id="http://arxiv.org/abs/2604.02091v1",
        title="Optimizing RAG Rerankers with LLM Feedback",
        authors=["Alice"],
        abstract="A paper about RAG rerankers.",
        published_date=datetime(2026, 4, 2, tzinfo=timezone.utc),
        url="http://arxiv.org/abs/2604.02091v1",
        categories=["cs.CL"],
        pdf_url="http://arxiv.org/pdf/2604.02091v1",
        source="arxiv",
    )


@pytest.fixture
def mock_papers():
    """Three papers with different ID formats."""
    return [
        Paper(
            id="http://arxiv.org/abs/2604.00001v1",
            title="Paper One about LLM reasoning",
            authors=["A"],
            abstract="LLM reasoning and decision making with knowledge graphs.",
            published_date=datetime(2026, 4, 1, tzinfo=timezone.utc),
            url="http://arxiv.org/abs/2604.00001v1",
            categories=["cs.AI"],
            pdf_url="",
            source="arxiv",
        ),
        Paper(
            id="http://arxiv.org/abs/2604.00002v1",
            title="Paper Two about transformer scaling",
            authors=["B"],
            abstract="Transformer scaling laws for large language models.",
            published_date=datetime(2026, 4, 1, tzinfo=timezone.utc),
            url="http://arxiv.org/abs/2604.00002v1",
            categories=["cs.LG"],
            pdf_url="",
            source="arxiv",
        ),
        Paper(
            id="http://arxiv.org/abs/2604.00003v1",
            title="Paper Three about attention mechanisms",
            authors=["C"],
            abstract="Novel attention mechanism for deep learning.",
            published_date=datetime(2026, 4, 1, tzinfo=timezone.utc),
            url="http://arxiv.org/abs/2604.00003v1",
            categories=["cs.LG"],
            pdf_url="",
            source="arxiv",
        ),
    ]


# ── normalize_paper_id ────────────────────────────────────────────


class TestNormalizePaperId:

    def test_arxiv_url(self):
        assert normalize_paper_id("http://arxiv.org/abs/2604.02091v1") == "2604.02091v1"

    def test_arxiv_https_url(self):
        assert normalize_paper_id("https://arxiv.org/abs/2604.02091v1") == "2604.02091v1"

    def test_arxiv_prefix(self):
        assert normalize_paper_id("arXiv:2604.02091v1") == "2604.02091v1"

    def test_bare_id(self):
        assert normalize_paper_id("2604.02091v1") == "2604.02091v1"

    def test_blog_url_unchanged(self):
        url = "https://example.com/blog/my-post"
        assert normalize_paper_id(url) == url

    def test_all_formats_match(self):
        """All ArXiv ID formats should normalize to the same value."""
        expected = "2604.02091v1"
        assert normalize_paper_id("http://arxiv.org/abs/2604.02091v1") == expected
        assert normalize_paper_id("https://arxiv.org/abs/2604.02091v1") == expected
        assert normalize_paper_id("arXiv:2604.02091v1") == expected
        assert normalize_paper_id("2604.02091v1") == expected


# ── SelectionHistory ──────────────────────────────────────────────


class TestSelectionHistory:

    def test_empty_history(self, history_file):
        h = SelectionHistory(history_file)
        assert h.get_excluded_ids() == set()

    def test_record_and_exclude(self, history_file, sample_paper):
        h = SelectionHistory(history_file)
        h.record(sample_paper)
        excluded = h.get_excluded_ids()
        assert "2604.02091v1" in excluded

    def test_persistence(self, history_file, sample_paper):
        """History survives reload from disk."""
        h1 = SelectionHistory(history_file)
        h1.record(sample_paper)

        h2 = SelectionHistory(history_file)
        assert "2604.02091v1" in h2.get_excluded_ids()

    def test_cooldown_expiry(self, history_file, sample_paper):
        """Papers older than cooldown window are not excluded."""
        h = SelectionHistory(history_file, cooldown_days=7)
        h.record(sample_paper)

        # Backdate the entry to 10 days ago
        h._history["2604.02091v1"]["selected_at"] = (
            datetime.now(timezone.utc) - timedelta(days=10)
        ).isoformat()
        h._save()

        h2 = SelectionHistory(history_file, cooldown_days=7)
        assert "2604.02091v1" not in h2.get_excluded_ids()

    def test_cooldown_zero_disables(self, history_file, sample_paper):
        """cooldown_days=0 disables dedup."""
        h = SelectionHistory(history_file, cooldown_days=0)
        h.record(sample_paper)
        assert h.get_excluded_ids() == set()

    def test_corrupted_file_graceful(self, history_file):
        """Corrupted JSON file doesn't crash — starts fresh."""
        history_file.write_text("not valid json{{{", encoding="utf-8")
        h = SelectionHistory(history_file)
        assert h.get_excluded_ids() == set()

    def test_normalizes_arxiv_url_on_record(self, history_file):
        """Recording a paper with a URL-style ID normalizes it."""
        paper = Paper(
            id="http://arxiv.org/abs/2604.99999v1",
            title="Test",
            authors=[],
            abstract="",
            published_date=datetime.now(timezone.utc),
            url="",
            categories=[],
            pdf_url="",
        )
        h = SelectionHistory(history_file)
        h.record(paper)
        assert "2604.99999v1" in h._history

    def test_multiple_papers(self, history_file):
        """Multiple papers tracked independently."""
        h = SelectionHistory(history_file)
        for i in range(3):
            paper = Paper(
                id=f"http://arxiv.org/abs/2604.0000{i}v1",
                title=f"Paper {i}",
                authors=[],
                abstract="",
                published_date=datetime.now(timezone.utc),
                url="",
                categories=[],
                pdf_url="",
            )
            h.record(paper)
        excluded = h.get_excluded_ids()
        assert len(excluded) == 3


# ── Selector with exclude_ids ────────────────────────────────────


class TestSelectorDedup:

    def test_exclude_ids_filters_candidates(self, config, mock_papers):
        """Excluded paper is never in results, regardless of its score."""
        selector = PaperSelector(config, claude_client=None)
        exclude = {"2604.00001v1"}  # Exclude Paper One (highest scorer)

        scored = selector.select_best(mock_papers, top_k=5, exclude_ids=exclude)
        selected_ids = {normalize_paper_id(sp.paper.id) for sp in scored}

        assert "2604.00001v1" not in selected_ids
        assert len(scored) >= 1  # At least one non-excluded paper returned

    def test_exclude_changes_top_pick(self, config, mock_papers):
        """Excluding the top-scoring paper changes which paper is selected."""
        selector = PaperSelector(config, claude_client=None)

        without_exclude = selector.select_best(mock_papers, top_k=1)
        top_id = normalize_paper_id(without_exclude[0].paper.id)

        with_exclude = selector.select_best(mock_papers, top_k=1, exclude_ids={top_id})
        new_top_id = normalize_paper_id(with_exclude[0].paper.id)

        assert new_top_id != top_id

    def test_no_exclude_ids_returns_top_scorer(self, config, mock_papers):
        """Without exclude_ids, top scorer is returned."""
        selector = PaperSelector(config, claude_client=None)
        scored = selector.select_best(mock_papers, top_k=1)
        assert len(scored) == 1
        # Paper One has the most keyword hits — should be top
        assert normalize_paper_id(scored[0].paper.id) == "2604.00001v1"

    def test_empty_exclude_ids_same_as_none(self, config, mock_papers):
        """Empty exclude_ids set behaves same as None."""
        selector = PaperSelector(config, claude_client=None)
        without = selector.select_best(mock_papers, top_k=1)
        with_empty = selector.select_best(mock_papers, top_k=1, exclude_ids=set())
        assert normalize_paper_id(without[0].paper.id) == normalize_paper_id(with_empty[0].paper.id)

    def test_exclude_all_returns_empty(self, config, mock_papers):
        """If all candidates are excluded, returns empty list."""
        selector = PaperSelector(config, claude_client=None)
        exclude = {normalize_paper_id(p.id) for p in mock_papers}
        scored = selector.select_best(mock_papers, top_k=5, exclude_ids=exclude)
        assert len(scored) == 0
