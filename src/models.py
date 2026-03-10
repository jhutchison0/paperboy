"""
Data models for the Research Podcast Pipeline.

Standardized dataclasses used across all pipeline stages:
sourcing, selection, distillation, and output.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Paper:
    """Represents a research paper (typically from ArXiv)."""
    id: str
    title: str
    authors: list[str]
    abstract: str
    published_date: datetime
    url: str
    categories: list[str]
    pdf_url: str
    source: str = "arxiv"

    def __str__(self) -> str:
        author_str = ", ".join(self.authors[:3])
        if len(self.authors) > 3:
            author_str += " et al."
        return f"{self.title} ({author_str}, {self.published_date.strftime('%Y-%m-%d')})"


@dataclass
class Article:
    """Represents a blog post or news article from an RSS feed."""
    title: str
    url: str
    published_date: datetime
    source: str  # e.g., "anthropic-blog", "google-research"
    summary: str
    content: str = ""
    authors: list[str] = field(default_factory=list)

    def to_paper(self) -> "Paper":
        """Convert to Paper for uniform downstream processing."""
        return Paper(
            id=self.url,
            title=self.title,
            authors=self.authors,
            abstract=self.summary,
            published_date=self.published_date,
            url=self.url,
            categories=[self.source],
            pdf_url="",
            source=self.source,
        )

    def __str__(self) -> str:
        return f"{self.title} ({self.source}, {self.published_date.strftime('%Y-%m-%d')})"


@dataclass
class ScoredPaper:
    """A Paper with a relevance score and reasoning."""
    paper: Paper
    score: float
    reasoning: str

    def __str__(self) -> str:
        return f"[{self.score:.2f}] {self.paper}"


@dataclass
class BriefingDocument:
    """The final output: a structured briefing ready for NotebookLM."""
    title: str
    source_paper: Paper
    generated_at: datetime
    content: str  # Full markdown briefing
    word_count: int = 0
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.word_count == 0:
            self.word_count = len(self.content.split())

    def __str__(self) -> str:
        return f"{self.title} ({self.word_count} words, {self.generated_at.strftime('%Y-%m-%d')})"
