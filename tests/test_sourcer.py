"""
Tests for ArxivSourcer.fetch_by_id().

Covers: happy path, paper not found, network error.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import PipelineConfig
from src.models import Paper
from src.sourcer import ArxivSourcer


@pytest.fixture
def config():
    return PipelineConfig.load()


def _make_arxiv_result(arxiv_id="1904.12787"):
    r = MagicMock()
    r.entry_id = f"http://arxiv.org/abs/{arxiv_id}v1"
    r.title = "Attention Is All You Need\n"
    r.authors = [MagicMock(__str__=lambda self: "Vaswani et al.")]
    r.summary = "The dominant sequence transduction models are based on complex RNNs."
    r.published = datetime(2019, 6, 12, tzinfo=timezone.utc)
    r.categories = [MagicMock(term="cs.CL"), MagicMock(term="cs.LG")]
    r.pdf_url = f"http://arxiv.org/pdf/{arxiv_id}v1"
    return r


class TestArxivSourcerFetchById:
    """Tests for ArxivSourcer.fetch_by_id()."""

    def test_fetch_by_id_returns_paper(self, config):
        sourcer = ArxivSourcer(config)
        sourcer.client = MagicMock()
        sourcer.client.results.return_value = iter([_make_arxiv_result()])

        paper = sourcer.fetch_by_id("1904.12787")

        assert isinstance(paper, Paper)
        assert "Attention Is All You Need" in paper.title
        assert paper.source == "arxiv"
        assert "cs.CL" in paper.categories
        assert "cs.LG" in paper.categories

    def test_fetch_by_id_raises_value_error_when_not_found(self, config):
        sourcer = ArxivSourcer(config)
        sourcer.client = MagicMock()
        sourcer.client.results.return_value = iter([])

        with pytest.raises(ValueError, match="not found"):
            sourcer.fetch_by_id("0000.00000")

    def test_fetch_by_id_propagates_network_error(self, config):
        sourcer = ArxivSourcer(config)
        sourcer.client = MagicMock()
        sourcer.client.results.side_effect = ConnectionError("ArXiv unreachable")

        with pytest.raises(ConnectionError):
            sourcer.fetch_by_id("1904.12787")
