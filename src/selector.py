"""
Paper relevance scoring and selection.

Uses a hybrid approach:
  1. Fast keyword matching for initial filtering
  2. Optional Claude-powered semantic scoring for top candidates

Think of it like a hiring funnel — keywords screen resumes quickly,
then Claude does the "interviews" on the shortlist.
"""

import logging
import re
from typing import Optional

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None  # SDK not required if using AgentRunner

from src.agent_runner import AgentRunner
from src.config import PipelineConfig
from src.models import Paper, Article, ScoredPaper, normalize_paper_id

logger = logging.getLogger(__name__)


class PaperSelector:
    """
    Scores and ranks papers by relevance to configured focus areas.

    Two-phase scoring:
      Phase 1 (keyword): Fast text matching against title, abstract, categories.
      Phase 2 (Claude): Semantic relevance scoring for top-K candidates.
    """

    def __init__(self, config: PipelineConfig, claude_client: Optional[Anthropic] = None, agent_runner: Optional[AgentRunner] = None):
        self.config = config
        self.claude = claude_client
        self.agent_runner = agent_runner

        # Pre-compile keyword patterns for efficiency
        self.keyword_patterns = [
            re.compile(re.escape(kw), re.IGNORECASE)
            for kw in config.focus_areas.keywords
        ]
        self.focus_descriptions = config.focus_areas.primary

    def select_best(
        self,
        papers: list[Paper],
        articles: list[Article] | None = None,
        top_k: int = 1,
        exclude_ids: set[str] | None = None,
    ) -> list[ScoredPaper]:
        """
        Score all candidates and return the top-K most relevant.

        Args:
            papers: ArXiv papers to consider.
            articles: Blog articles (converted to Papers internally).
            top_k: Number of papers to return.
            exclude_ids: Normalized paper IDs to skip (previously selected).

        Returns:
            Top-K ScoredPapers, sorted by score descending.
        """
        # Combine papers and articles into a uniform list
        all_candidates = list(papers)
        if articles:
            all_candidates.extend(a.to_paper() for a in articles)

        # Filter out previously selected papers
        if exclude_ids:
            before = len(all_candidates)
            all_candidates = [
                p for p in all_candidates
                if normalize_paper_id(p.id) not in exclude_ids
            ]
            excluded_count = before - len(all_candidates)
            if excluded_count:
                logger.info(f"Excluded {excluded_count} previously selected paper(s)")

        if not all_candidates:
            logger.warning("No candidates to score!")
            return []

        logger.info(f"Scoring {len(all_candidates)} candidates...")

        # Phase 1: Keyword scoring (fast)
        keyword_scored = []
        for paper in all_candidates:
            kw_score = self._score_keywords(paper)
            keyword_scored.append(ScoredPaper(
                paper=paper,
                score=kw_score,
                reasoning=f"Keyword match score: {kw_score:.2f}",
            ))

        # Sort by keyword score
        keyword_scored.sort(key=lambda sp: sp.score, reverse=True)
        logger.info(f"Top keyword scores: {[f'{sp.score:.2f}' for sp in keyword_scored[:5]]}")

        # Phase 2: Claude scoring (optional, for top candidates)
        if self.config.selector.use_claude_scoring and (self.claude or self.agent_runner):
            top_candidates = keyword_scored[:self.config.selector.top_k_for_claude]
            logger.info(f"Claude-scoring top {len(top_candidates)} candidates...")

            for scored_paper in top_candidates:
                try:
                    claude_score, reasoning = self._score_with_claude(scored_paper.paper)
                    # Combine scores
                    kw_score = scored_paper.score
                    combined = (
                        self.config.selector.keyword_weight * kw_score
                        + self.config.selector.claude_weight * claude_score
                    )
                    scored_paper.score = combined
                    scored_paper.reasoning = (
                        f"Keyword: {kw_score:.2f}, "
                        f"Claude: {claude_score:.2f} → Combined: {combined:.2f}\n"
                        f"Claude reasoning: {reasoning}"
                    )
                except Exception as e:
                    logger.warning(f"Claude scoring failed for '{scored_paper.paper.title[:50]}': {e}")
                    # Keep keyword-only score
        else:
            top_candidates = keyword_scored
            if not self.claude and not self.agent_runner and self.config.selector.use_claude_scoring:
                logger.info("Claude scoring enabled but no API client or agent runner — using keywords only")

        # Re-sort after Claude scoring and filter by threshold
        top_candidates.sort(key=lambda sp: sp.score, reverse=True)
        filtered = [
            sp for sp in top_candidates
            if sp.score >= self.config.selector.min_score_threshold
        ]

        if not filtered:
            logger.warning(
                f"No papers above threshold ({self.config.selector.min_score_threshold}). "
                f"Returning top candidate anyway."
            )
            filtered = top_candidates[:1] if top_candidates else []

        result = filtered[:top_k]
        for sp in result:
            logger.info(f"Selected: [{sp.score:.2f}] {sp.paper.title[:80]}")

        return result

    def _score_keywords(self, paper: Paper) -> float:
        """
        Score a paper based on keyword matches in title, abstract, and categories.

        Scoring weights:
          - Title match:    0.5 (title relevance is high signal)
          - Abstract match: 0.35
          - Category match: 0.15

        Returns: Float between 0.0 and 1.0
        """
        title_text = paper.title.lower()
        abstract_text = paper.abstract.lower()
        category_text = " ".join(paper.categories).lower()

        title_hits = 0
        abstract_hits = 0
        category_hits = 0

        for pattern in self.keyword_patterns:
            if pattern.search(title_text):
                title_hits += 1
            if pattern.search(abstract_text):
                abstract_hits += 1
            if pattern.search(category_text):
                category_hits += 1

        total_keywords = len(self.keyword_patterns)
        if total_keywords == 0:
            return 0.0

        # Normalize each to 0-1 range, then weight
        title_score = min(title_hits / max(total_keywords * 0.15, 1), 1.0)
        abstract_score = min(abstract_hits / max(total_keywords * 0.25, 1), 1.0)
        category_score = min(category_hits / max(total_keywords * 0.1, 1), 1.0)

        weighted = (
            0.50 * title_score
            + 0.35 * abstract_score
            + 0.15 * category_score
        )

        return round(min(weighted, 1.0), 3)

    def _score_with_claude(self, paper: Paper) -> tuple[float, str]:
        """
        Use Claude to semantically assess paper relevance. Falls back to AgentRunner if no SDK client.

        Returns:
            Tuple of (score between 0-1, reasoning string).
        """
        # Path 1: SDK (preferred)
        if self.claude:
            prompt = f"""Score this research paper's relevance on a scale of 0 to 10.

CONTEXT: The reader is a research scientist at a U.S. national laboratory
who leads efforts in using LLMs as tools for decision support, knowledge
graphs, and deep learning. They want to stay at the cutting edge of
generative AI and be able to discuss recent advances with their division.

FOCUS AREAS:
{chr(10).join(f'- {area}' for area in self.focus_descriptions)}

PAPER:
Title: {paper.title}
Authors: {', '.join(paper.authors[:5])}
Abstract: {paper.abstract[:1500]}
Categories: {', '.join(paper.categories)}

Respond in this exact format (nothing else):
SCORE: [0-10]
REASONING: [1-2 sentences explaining why this score]"""

            response = self.claude.messages.create(
                model=self.config.claude.scoring_model,
                max_tokens=200,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}],
            )

            text = response.content[0].text.strip()

            # Parse score
            score = 5.0  # default
            reasoning = text
            for line in text.split("\n"):
                if line.strip().upper().startswith("SCORE:"):
                    try:
                        score_str = line.split(":", 1)[1].strip()
                        score = float(score_str)
                        score = max(0, min(10, score))  # clamp
                    except (ValueError, IndexError):
                        pass
                elif line.strip().upper().startswith("REASONING:"):
                    reasoning = line.split(":", 1)[1].strip()

            # Normalize to 0-1
            return round(score / 10.0, 3), reasoning

        # Path 2: AgentRunner (CLI fallback)
        if self.agent_runner:
            result = self.agent_runner.score_paper(paper, self.config.focus_areas)
            if result is not None:
                return result["score"], result["reasoning"]
            logger.warning(f"AgentRunner scoring returned None for '{paper.title[:50]}' — using default")
            return 0.5, "AgentRunner scoring failed; default score applied"

        raise RuntimeError("No Claude backend available for scoring")
