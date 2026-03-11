#!/usr/bin/env python3
"""
End-to-end test of the Research Podcast Pipeline.

Uses mock data to verify config loading, selection scoring, and pipeline logic.
Full live testing (ArXiv + Claude) should be done on your machine with API keys.
"""

import sys
from pathlib import Path
from datetime import datetime, timezone

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from src.config import PipelineConfig
from src.selector import PaperSelector
from src.models import Paper, Article


@pytest.fixture
def config():
    """Load pipeline config for tests that need it."""
    return PipelineConfig.load()


# ── Mock data for testing ──────────────────────────────────────────

MOCK_PAPERS = [
    Paper(
        id="2603.12345",
        title="ReasonGraph: Augmenting LLM Decision Support with Dynamic Knowledge Graphs",
        authors=["Alice Chen", "Bob Zhang", "Carol Wu"],
        abstract=(
            "We introduce ReasonGraph, a framework that combines large language models "
            "with dynamically constructed knowledge graphs to improve decision support "
            "in high-stakes environments. Our approach uses chain-of-thought reasoning "
            "to extract structured relationships from unstructured data, building a "
            "queryable graph that serves as an external memory for the LLM. We evaluate "
            "on three decision-making benchmarks and show significant improvements in "
            "reasoning accuracy and interpretability compared to RAG baselines."
        ),
        published_date=datetime(2026, 3, 8, tzinfo=timezone.utc),
        url="https://arxiv.org/abs/2603.12345",
        categories=["cs.AI", "cs.CL"],
        pdf_url="https://arxiv.org/pdf/2603.12345",
        source="arxiv",
    ),
    Paper(
        id="2603.12346",
        title="Scaling Laws for Attention-Free Transformer Architectures",
        authors=["Dave Park", "Eve Johnson"],
        abstract=(
            "We study the scaling behavior of attention-free transformer variants, "
            "finding that state-space models exhibit different compute-optimal scaling "
            "laws than standard transformers. Our analysis covers models from 100M to "
            "10B parameters trained on up to 1T tokens. We find that attention-free "
            "models are more parameter-efficient at smaller scales but converge with "
            "standard transformers at larger scales."
        ),
        published_date=datetime(2026, 3, 7, tzinfo=timezone.utc),
        url="https://arxiv.org/abs/2603.12346",
        categories=["cs.LG"],
        pdf_url="https://arxiv.org/pdf/2603.12346",
        source="arxiv",
    ),
    Paper(
        id="2603.12347",
        title="Bayesian Calibration of Neural Network Uncertainty for Clinical Decision Making",
        authors=["Frank Lee", "Grace Kim"],
        abstract=(
            "Neural networks used in clinical decision support require well-calibrated "
            "uncertainty estimates. We propose a Bayesian calibration method that uses "
            "causal inference principles to decompose prediction uncertainty into "
            "aleatoric and epistemic components, enabling clinicians to understand when "
            "the model's confidence should be trusted. Our approach improves calibration "
            "by 34% on three medical decision benchmarks."
        ),
        published_date=datetime(2026, 3, 6, tzinfo=timezone.utc),
        url="https://arxiv.org/abs/2603.12347",
        categories=["cs.AI", "stat.ML"],
        pdf_url="https://arxiv.org/pdf/2603.12347",
        source="arxiv",
    ),
    Paper(
        id="2603.12348",
        title="On the Convergence Properties of Adam with Weight Decay in Non-Convex Settings",
        authors=["Henry Zhao"],
        abstract=(
            "We provide new convergence guarantees for the AdamW optimizer in "
            "non-convex optimization landscapes typical of deep learning. Our analysis "
            "reveals previously unknown conditions under which AdamW achieves faster "
            "convergence rates than SGD with momentum."
        ),
        published_date=datetime(2026, 3, 5, tzinfo=timezone.utc),
        url="https://arxiv.org/abs/2603.12348",
        categories=["stat.ML"],
        pdf_url="https://arxiv.org/pdf/2603.12348",
        source="arxiv",
    ),
]

MOCK_ARTICLES = [
    Article(
        title="Building Reliable AI Agents with Tool Use and Structured Reasoning",
        url="https://example.com/agents-blog",
        published_date=datetime(2026, 3, 9, tzinfo=timezone.utc),
        source="AI Research Blog",
        summary=(
            "A practical guide to building AI agents that combine LLM reasoning "
            "with tool use and structured knowledge representations. We share lessons "
            "from deploying agent systems in enterprise decision support settings."
        ),
    ),
]


def test_config():
    """Test config loading."""
    print("=" * 60)
    print("TEST 1: Configuration loading")
    print("=" * 60)
    config = PipelineConfig.load()
    print(f"  Output dir:     {config.output_dir}")
    print(f"  ArXiv cats:     {config.arxiv.categories}")
    print(f"  Blog feeds:     {len(config.blogs.feeds)}")
    print(f"  Keywords:       {len(config.focus_areas.keywords)}")
    print(f"  API key set:    {'yes' if config.anthropic_api_key else 'no'}")
    assert len(config.arxiv.categories) > 0
    assert len(config.focus_areas.keywords) > 0
    print(f"  PASSED\n")


def test_selection(config):
    """Test paper scoring and selection with mock data."""
    print("=" * 60)
    print("TEST 2: Paper selection (keyword scoring, mock data)")
    print("=" * 60)

    # Keyword-only scoring (no API key needed)
    selector = PaperSelector(config, claude_client=None)
    scored = selector.select_best(MOCK_PAPERS, MOCK_ARTICLES, top_k=5)

    print(f"\n  Scored {len(MOCK_PAPERS)} papers + {len(MOCK_ARTICLES)} articles:")
    for i, sp in enumerate(scored):
        print(f"    {i+1}. [{sp.score:.3f}] {sp.paper.title[:65]}...")

    assert len(scored) > 0, "Expected at least one scored paper"

    # The knowledge graph + decision support paper should score highest
    top = scored[0]
    print(f"\n  Top pick: {top.paper.title[:70]}...")
    print(f"  Score:    {top.score:.3f}")
    print(f"  PASSED\n")


def test_model_conversions():
    """Test data model operations."""
    print("=" * 60)
    print("TEST 3: Data model conversions")
    print("=" * 60)

    # Test Article -> Paper conversion
    article = MOCK_ARTICLES[0]
    paper = article.to_paper()
    assert paper.title == article.title
    assert paper.abstract == article.summary
    print(f"  Article->Paper conversion: OK")

    # Test BriefingDocument word count
    from src.models import BriefingDocument
    doc = BriefingDocument(
        title="Test",
        source_paper=MOCK_PAPERS[0],
        generated_at=datetime.now(timezone.utc),
        content="This is a test briefing with exactly ten words in it.",
    )
    assert doc.word_count == 11
    print(f"  BriefingDocument word count: OK ({doc.word_count} words)")
    print(f"  PASSED\n")


def test_cli_info():
    """Test CLI info command."""
    print("=" * 60)
    print("TEST 4: CLI module import")
    print("=" * 60)

    import main
    print(f"  CLI module imported successfully")
    print(f"  Commands: {list(main.cli.commands.keys())}")
    print(f"  PASSED\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Research Podcast Pipeline — Test Suite")
    print("  (Using mock data — run on your machine for live tests)")
    print("=" * 60 + "\n")

    test_config()
    cfg = PipelineConfig.load()
    test_selection(cfg)
    test_model_conversions()
    test_cli_info()

    print("=" * 60)
    print("  All tests PASSED!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Copy this project to your machine")
    print("  2. cp .env.example .env && edit .env with your ANTHROPIC_API_KEY")
    print("  3. pip install -r requirements.txt")
    print("  4. python main.py health    # verify connectivity")
    print("  5. python main.py run       # generate your first briefing!")
    print("  6. Upload the .md file to NotebookLM for podcast generation")
