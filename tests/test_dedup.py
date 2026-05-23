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
        assert h.contains("2604.99999v1")

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

    # ── Public contains() membership API ───────────────────────────
    # Replaces direct access to the private _history dict so tests stay
    # decoupled from the in-memory representation.

    def test_contains_returns_true_for_recorded_paper(self, history_file, sample_paper):
        h = SelectionHistory(history_file)
        h.record(sample_paper)
        assert h.contains("2604.02091v1") is True

    def test_contains_returns_false_for_unrecorded_paper(self, history_file):
        h = SelectionHistory(history_file)
        assert h.contains("9999.99999v1") is False

    def test_contains_normalizes_input(self, history_file, sample_paper):
        """contains() accepts raw ArXiv URLs, prefixed IDs, or bare IDs."""
        h = SelectionHistory(history_file)
        h.record(sample_paper)
        assert h.contains("http://arxiv.org/abs/2604.02091v1") is True
        assert h.contains("arXiv:2604.02091v1") is True
        assert h.contains("2604.02091v1") is True

    def test_contains_returns_true_outside_cooldown_window(self, history_file, sample_paper):
        """Membership is independent of cooldown — only excluded_ids is cooldown-aware."""
        h = SelectionHistory(history_file, cooldown_days=7)
        h.record(sample_paper)
        h._history["2604.02091v1"]["selected_at"] = (
            datetime.now(timezone.utc) - timedelta(days=30)
        ).isoformat()
        # Outside cooldown — not excluded
        assert "2604.02091v1" not in h.get_excluded_ids()
        # ... but still recorded
        assert h.contains("2604.02091v1") is True


# ── Seeding from existing briefings ──────────────────────────────


class TestSeedFromBriefings:

    def _write_briefing(self, directory, filename, frontmatter):
        """Helper to write a mock briefing with YAML frontmatter."""
        lines = ["---"]
        for k, v in frontmatter.items():
            lines.append(f'{k}: "{v}"' if isinstance(v, str) else f"{k}: {v}")
        lines.append("---")
        lines.append("\n## Content\nSome briefing text.")
        path = directory / filename
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def test_seeds_from_arxiv_source_field(self, tmp_path):
        """Seeds history from briefing with source: arXiv:XXXX format."""
        self._write_briefing(tmp_path, "260403_test_briefing.md", {
            "title": "Test Paper",
            "source": "arXiv:2604.02091v1",
        })
        h = SelectionHistory(tmp_path / ".selection_history.json")
        assert "2604.02091v1" in h.get_excluded_ids()

    def test_seeds_from_source_with_author_prefix(self, tmp_path):
        """Seeds from source field that has author names before arXiv ID."""
        self._write_briefing(tmp_path, "260326_test_briefing.md", {
            "title": "MARCH Paper",
            "source": "Li et al., arXiv:2603.24579v1",
        })
        h = SelectionHistory(tmp_path / ".selection_history.json")
        assert "2603.24579v1" in h.get_excluded_ids()

    def test_seeds_from_paper_url_field(self, tmp_path):
        """Seeds from paper_url field with ArXiv URL."""
        self._write_briefing(tmp_path, "260312_test_briefing.md", {
            "title": "HeartAgent",
            "paper_url": "http://arxiv.org/abs/2603.10764v1",
        })
        h = SelectionHistory(tmp_path / ".selection_history.json")
        assert "2603.10764v1" in h.get_excluded_ids()

    def test_does_not_overwrite_existing_entries(self, tmp_path):
        """Seeding doesn't overwrite entries already in history."""
        self._write_briefing(tmp_path, "260403_test_briefing.md", {
            "title": "Test Paper",
            "source": "arXiv:2604.02091v1",
        })
        # Pre-populate history with a known timestamp
        history_file = tmp_path / ".selection_history.json"
        existing = {"2604.02091v1": {"title": "Original", "selected_at": "2026-04-03T10:00:00+00:00"}}
        history_file.write_text(json.dumps(existing), encoding="utf-8")

        h = SelectionHistory(history_file)
        assert h._history["2604.02091v1"]["title"] == "Original"  # Not overwritten

    def test_seeds_multiple_briefings(self, tmp_path):
        """Seeds all briefing files in the directory."""
        self._write_briefing(tmp_path, "260403_paper-a_briefing.md", {
            "title": "Paper A", "source": "arXiv:2604.00001v1",
        })
        self._write_briefing(tmp_path, "260404_paper-b_briefing.md", {
            "title": "Paper B", "source": "arXiv:2604.00002v1",
        })
        h = SelectionHistory(tmp_path / ".selection_history.json")
        excluded = h.get_excluded_ids()
        assert "2604.00001v1" in excluded
        assert "2604.00002v1" in excluded

    def test_ignores_non_briefing_files(self, tmp_path):
        """Only files matching *_briefing.md are scanned."""
        # This file has no _briefing suffix
        self._write_briefing(tmp_path, "260403_notes.md", {
            "title": "Notes", "source": "arXiv:9999.99999v1",
        })
        h = SelectionHistory(tmp_path / ".selection_history.json")
        assert "9999.99999v1" not in h.get_excluded_ids()

    def test_handles_no_frontmatter_gracefully(self, tmp_path):
        """Briefing files without YAML frontmatter are silently skipped."""
        (tmp_path / "260403_broken_briefing.md").write_text(
            "# No frontmatter here\nJust text.", encoding="utf-8"
        )
        h = SelectionHistory(tmp_path / ".selection_history.json")
        assert h.get_excluded_ids() == set()

    def test_persists_seeded_history(self, tmp_path):
        """Seeded entries are saved to disk so they survive reload."""
        self._write_briefing(tmp_path, "260403_test_briefing.md", {
            "title": "Test", "source": "arXiv:2604.02091v1",
        })
        h1 = SelectionHistory(tmp_path / ".selection_history.json")
        assert "2604.02091v1" in h1.get_excluded_ids()

        # Reload — should find it without re-scanning
        h2 = SelectionHistory(tmp_path / ".selection_history.json")
        assert "2604.02091v1" in h2.get_excluded_ids()

    def test_uses_frontmatter_date_not_mtime(self, tmp_path):
        """Seeded selected_at comes from frontmatter date, not file mtime."""
        self._write_briefing(tmp_path, "260403_test_briefing.md", {
            "title": "Test",
            "source": "arXiv:2604.02091v1",
            "date": "2026-04-03",
        })
        h = SelectionHistory(tmp_path / ".selection_history.json")
        entry = h._history["2604.02091v1"]
        assert "2026-04-03" in entry["selected_at"]

    def test_prefers_briefing_date_over_date(self, tmp_path):
        """briefing_date field takes precedence over date field."""
        self._write_briefing(tmp_path, "260404_test_briefing.md", {
            "title": "Test",
            "source": "arXiv:2604.02091v1",
            "date": "2026-04-02",
            "briefing_date": "2026-04-04",
        })
        h = SelectionHistory(tmp_path / ".selection_history.json")
        entry = h._history["2604.02091v1"]
        assert "2026-04-04" in entry["selected_at"]

    def test_falls_back_to_mtime_without_date(self, tmp_path):
        """Falls back to file mtime when frontmatter has no date field."""
        self._write_briefing(tmp_path, "260403_test_briefing.md", {
            "title": "Test",
            "source": "arXiv:2604.02091v1",
        })
        h = SelectionHistory(tmp_path / ".selection_history.json")
        entry = h._history["2604.02091v1"]
        # Should have a valid ISO timestamp (from mtime fallback)
        assert "selected_at" in entry
        datetime.fromisoformat(entry["selected_at"])  # Should not raise


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
