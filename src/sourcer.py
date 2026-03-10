"""
Research paper and blog article sourcing.

Fetches recent papers from ArXiv and articles from AI research blog RSS feeds.
Uses the strategy pattern so new sources can be added easily.
"""

import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Union

import arxiv
import feedparser
import requests
from dateutil import parser as date_parser

from src.config import PipelineConfig, BlogFeed
from src.models import Paper, Article

logger = logging.getLogger(__name__)


class ContentSourcer(ABC):
    """Abstract base for all content sourcing strategies."""

    @abstractmethod
    def fetch(self, days_back: int = 7) -> list[Union[Paper, Article]]:
        """Fetch recent content from this source."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Verify the source is accessible. Returns True if healthy."""
        pass


class ArxivSourcer(ContentSourcer):
    """
    Fetches recent papers from ArXiv using the official API.

    Queries configured categories (cs.AI, cs.LG, etc.), deduplicates
    papers that appear in multiple categories, and respects rate limits.
    """

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.client = arxiv.Client(
            page_size=config.arxiv.max_results_per_category,
            delay_seconds=config.arxiv.rate_limit_seconds,
        )

    def fetch(self, days_back: int = 7) -> list[Paper]:
        """
        Fetch recent papers across all configured ArXiv categories.

        Args:
            days_back: How many days back to search.

        Returns:
            Deduplicated list of Papers sorted by date (newest first).
        """
        all_papers: dict[str, Paper] = {}  # id -> Paper, for dedup

        for category in self.config.arxiv.categories:
            try:
                logger.info(f"Fetching ArXiv papers from {category}...")
                papers = self._fetch_category(category, days_back)
                for paper in papers:
                    if paper.id not in all_papers:
                        all_papers[paper.id] = paper
                    else:
                        # Merge categories from duplicate entries
                        existing = all_papers[paper.id]
                        for cat in paper.categories:
                            if cat not in existing.categories:
                                existing.categories.append(cat)
                logger.info(f"  {category}: found {len(papers)} papers")
            except Exception as e:
                logger.warning(f"  {category}: failed to fetch — {e}")
                continue

        # Sort newest first
        result = sorted(all_papers.values(), key=lambda p: p.published_date, reverse=True)
        logger.info(f"ArXiv total: {len(result)} unique papers across {len(self.config.arxiv.categories)} categories")
        return result

    def _fetch_category(self, category: str, days_back: int) -> list[Paper]:
        """Fetch papers from a single ArXiv category."""
        search = arxiv.Search(
            query=f"cat:{category}",
            max_results=self.config.arxiv.max_results_per_category,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )

        cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
        papers = []

        for result in self.client.results(search):
            # Stop if we've gone past our lookback window
            pub_date = result.published.replace(tzinfo=timezone.utc) if result.published.tzinfo is None else result.published
            if pub_date < cutoff:
                break

            papers.append(Paper(
                id=result.entry_id,
                title=result.title.strip().replace("\n", " "),
                authors=[str(a) for a in result.authors],
                abstract=result.summary.strip().replace("\n", " "),
                published_date=pub_date,
                url=result.entry_id,
                categories=[cat.term if hasattr(cat, 'term') else str(cat) for cat in result.categories]
                           if hasattr(result, 'categories') and result.categories
                           else [category],
                pdf_url=result.pdf_url or "",
                source="arxiv",
            ))

        return papers

    def health_check(self) -> bool:
        """Quick test query to verify ArXiv API is responding."""
        try:
            search = arxiv.Search(query="cat:cs.AI", max_results=1)
            results = list(self.client.results(search))
            return len(results) > 0
        except Exception as e:
            logger.error(f"ArXiv health check failed: {e}")
            return False


class BlogSourcer(ContentSourcer):
    """
    Fetches recent articles from AI research blog RSS/Atom feeds.

    Handles per-feed errors gracefully — one broken feed doesn't
    stop the others from being processed.
    """

    def __init__(self, config: PipelineConfig):
        self.config = config

    def fetch(self, days_back: int = 7) -> list[Article]:
        """
        Fetch articles from all configured blog feeds.

        Args:
            days_back: How many days back to include articles.

        Returns:
            List of Articles sorted by date (newest first).
        """
        all_articles: list[Article] = []
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)

        for feed_config in self.config.blogs.feeds:
            try:
                articles = self._fetch_feed(feed_config, cutoff)
                all_articles.extend(articles)
                logger.info(f"Blog '{feed_config.name}': found {len(articles)} recent articles")
            except Exception as e:
                logger.warning(f"Blog '{feed_config.name}': failed — {e}")
                continue

        all_articles.sort(key=lambda a: a.published_date, reverse=True)
        logger.info(f"Blog total: {len(all_articles)} articles from {len(self.config.blogs.feeds)} feeds")
        return all_articles

    def _fetch_feed(self, feed_config: BlogFeed, cutoff: datetime) -> list[Article]:
        """Parse a single RSS/Atom feed."""
        parsed = feedparser.parse(
            feed_config.url,
            request_headers={"User-Agent": "ResearchPodcastPipeline/1.0"},
        )

        if parsed.bozo and not parsed.entries:
            raise RuntimeError(f"Feed parse error: {parsed.bozo_exception}")

        articles = []
        for entry in parsed.entries:
            # Parse published date — feeds use various formats
            pub_date = self._parse_date(entry)
            if pub_date is None or pub_date < cutoff:
                continue

            # Extract content — prefer full content, fall back to summary
            content = ""
            if hasattr(entry, "content") and entry.content:
                content = entry.content[0].get("value", "")
            summary = entry.get("summary", entry.get("description", ""))

            articles.append(Article(
                title=entry.get("title", "Untitled").strip(),
                url=entry.get("link", ""),
                published_date=pub_date,
                source=feed_config.name,
                summary=summary[:1000],  # Cap summary length
                content=content[:5000],  # Cap content length
                authors=[a.get("name", "") for a in entry.get("authors", [])],
            ))

        return articles

    def _parse_date(self, entry) -> datetime | None:
        """Try to parse a date from an RSS entry, handling various formats."""
        for date_field in ["published_parsed", "updated_parsed"]:
            parsed = entry.get(date_field)
            if parsed:
                try:
                    dt = datetime(*parsed[:6], tzinfo=timezone.utc)
                    return dt
                except (TypeError, ValueError):
                    continue

        # Fall back to string parsing
        for date_field in ["published", "updated"]:
            date_str = entry.get(date_field)
            if date_str:
                try:
                    return date_parser.parse(date_str).replace(tzinfo=timezone.utc)
                except (ValueError, TypeError):
                    continue

        return None

    def health_check(self) -> bool:
        """Try to fetch from at least one feed."""
        for feed_config in self.config.blogs.feeds:
            try:
                parsed = feedparser.parse(feed_config.url)
                if parsed.entries:
                    return True
            except Exception:
                continue
        return False


class SourceManager:
    """
    Orchestrates all content sources.

    Combines results from ArXiv and blogs, handling per-source
    failures so the pipeline continues even if one source is down.
    """

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.arxiv_sourcer = ArxivSourcer(config)
        self.blog_sourcer = BlogSourcer(config)

    def fetch_all(self, days_back: int | None = None) -> tuple[list[Paper], list[Article]]:
        """
        Fetch from all sources.

        Returns:
            Tuple of (papers, articles). Either list may be empty if that source failed.
        """
        if days_back is None:
            days_back = self.config.days_lookback

        papers: list[Paper] = []
        articles: list[Article] = []

        # Fetch ArXiv
        try:
            papers = self.arxiv_sourcer.fetch(days_back)
        except Exception as e:
            logger.error(f"ArXiv sourcing failed entirely: {e}")

        # Fetch blogs
        try:
            articles = self.blog_sourcer.fetch(days_back)
        except Exception as e:
            logger.error(f"Blog sourcing failed entirely: {e}")

        if not papers and not articles:
            logger.warning("No content fetched from any source!")

        return papers, articles

    def health_check(self) -> dict[str, bool]:
        """Check health of all sources."""
        return {
            "arxiv": self.arxiv_sourcer.health_check(),
            "blogs": self.blog_sourcer.health_check(),
        }
