"""
Briefing document distillation using Claude.

This is the heart of the pipeline. Takes a selected paper and produces
a structured markdown briefing optimized for:
  1. 3Blue1Brown-style intuition-first explanation
  2. Two-voice podcast format (guide + challenger)
  3. Steering Google NotebookLM toward engaging dialogue

The key insight: NotebookLM's AI hosts are driven entirely by the source
material. By structuring the briefing with narrative arc, analogies,
and pre-loaded counterarguments, we control the podcast's emphasis
without controlling its exact words. Think of it like writing a really
good briefing packet for a talk show host.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None  # SDK not required if using AgentRunner

from src.agent_runner import AgentRunner
from src.config import PipelineConfig
from src.models import Paper, BriefingDocument

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an expert at distilling complex research papers into compelling \
educational content. Your writing style is inspired by 3Blue1Brown: intuitive, visual, \
and focused on deep understanding over mathematical formalism.

Your philosophy:
- "I'm not here to tell you how to calculate — I want to give you a sense of what this means."
- Build intuition FIRST, then layer in technical depth.
- Use analogies relentlessly. If you can explain it with a physical metaphor, do.
- Prioritize clarity over completeness — a listener who understands one idea deeply learns more \
than one who's been shown five ideas superficially.
- Invite disagreement and hard questions. The best learning happens at the edges.

You're writing a briefing document that will be fed into Google NotebookLM to generate \
a ~30 minute podcast with two AI hosts. The hosts will riff on your document, so:
- Write conversationally, not formally
- Use "we" and "you" naturally
- Embed tensions and questions the hosts can explore
- Front-load "why should I care" before "how does it work"
- Include counterarguments so the hosts debate, not just agree

Your reader is a research scientist who values both rigor and intuitive understanding. \
They're not afraid of technical depth, but they want the intuition first."""


def build_user_prompt(paper: Paper, paper_text: str, user_context: str, target_words: int) -> str:
    """
    Build the main distillation prompt.

    This prompt is carefully structured to produce a briefing that
    NotebookLM will turn into engaging two-voice dialogue.
    """
    return f"""Please distill this research paper into a ~{target_words}-word briefing document \
that will be used to generate a 30-minute research podcast.

═══════════════════════════════════════════════════
PAPER INFORMATION
═══════════════════════════════════════════════════

Title: {paper.title}
Authors: {', '.join(paper.authors[:8])}
Published: {paper.published_date.strftime('%Y-%m-%d')}
URL: {paper.url}
Categories: {', '.join(paper.categories)}

═══════════════════════════════════════════════════
PAPER CONTENT
═══════════════════════════════════════════════════

{paper_text}

═══════════════════════════════════════════════════
BRIEFING STRUCTURE
═══════════════════════════════════════════════════

Follow this structure exactly. Each section has a purpose in shaping the podcast.

## 1. Opening Hook: Why Should You Care? (300-400 words)

This sets the tone for the entire podcast. Answer:
- What PROBLEM does this paper tackle? Frame it as a story, not a thesis statement.
- Why does it matter RIGHT NOW? What changed that makes this timely?
- Who benefits if this works? Paint a picture of the impact.

Use a concrete scenario or narrative. Think: "If I had 60 seconds in an elevator with a smart \
person who doesn't work in ML, how would I make them care about this?"

Start with something like "Imagine you're trying to..." or "Here's a question that's been \
keeping researchers up at night..." — make it visceral.

## 2. The Core Intuition (600-800 words)

This is the 3Blue1Brown section. NO equations yet. Pure intuition.

Build the BIG IDEA using 2-3 different analogies:
- A PHYSICAL analogy (how things move, interact, flow)
- An EVERYDAY analogy (cooking, navigation, conversation — something from daily life)
- A HISTORICAL analogy (how did we think about this before? what's the paradigm shift?)

Structure it as a progression: start with the simplest framing, then add nuance.
Use phrases like "Think of it this way...", "Now here's where it gets interesting...", \
"The insight is..."

The goal: someone listening on an exercise bike should nod and think "oh, THAT'S what \
they mean" — not reach for a pen.

## 3. The Technical Sketch (800-1000 words)

NOW we can get technical, but keep the intuition-first spirit.

Structure:
- What are the key components of their approach?
- How do the pieces fit together? (Think architecture, not proofs)
- What's genuinely NOVEL compared to prior work?
- Where does this sit in the landscape of recent advances?

If there's a key equation or algorithm, explain what each piece MEANS conceptually \
before presenting it. "The loss function is basically asking: how surprised should we be?"

Use comparisons to familiar techniques: "If you know how attention works in transformers, \
this is like adding a memory system on top of that..."

## 4. The Evidence: Did It Actually Work? (600-800 words)

Be concrete and honest here. This grounds the podcast in reality.

Cover:
- What experiments did they run? On what data?
- What were the headline results? (Actual numbers where they help)
- How does this compare to the state of the art?
- What's the "yeah, but..." caveat? (Every paper has one)
- How robust are the findings? Any concerns about the evaluation?

Frame this as "So we've heard the theory — now let's see the receipts."

## 5. The Challengers' Corner (600-800 words)

This section is CRITICAL for generating good podcast dialogue. NotebookLM's hosts \
will naturally debate these tensions.

Raise at least 4-5 hard questions:
- "But couldn't you achieve something similar with a much simpler approach?"
- "This assumes X — but what if X doesn't hold in practice?"
- "How does this scale to real-world data/systems?"
- "What are the failure modes they're NOT discussing?"
- "Is this actually a step forward, or is it incremental?"

For each challenge, give BOTH sides: the objection AND a reasonable response. \
Don't settle the debate — leave it open for the podcast hosts to explore.

Use language like "A skeptic might argue...", "On the other hand...", \
"The authors would likely respond that..."

## 6. Connection to Decision Support and Real-World Impact (400-500 words)

{user_context}

Connect this paper to practical applications:
- How could this advance be used in decision-support systems?
- What does this mean for organizations building with LLMs?
- How does it relate to knowledge graphs, structured reasoning, or interpretability?
- What would it take to move this from paper to production?
- Are there implications for trust, safety, or governance of AI systems?

Be specific. "This matters for decision support because..." not just "This is relevant."

## 7. Open Questions and Future Directions (400-500 words)

What's left unsolved? Where is this headed?

- What questions does this paper RAISE but not answer?
- What would the next paper in this line of research look like?
- Are there connections to other fields (cognitive science, economics, biology) \
  that might unlock new approaches?
- What needs to happen for this to reach its full potential?

Frame optimistically but realistically. End with something thought-provoking \
that the podcast hosts can close on.

## 8. Key Takeaways (200-300 words)

Distill everything into 5-7 crisp bullet points:
- The core insight in one sentence
- The main technical contribution
- The strongest evidence
- The biggest limitation
- Why it matters for the field
- The open question that keeps you thinking

═══════════════════════════════════════════════════
STYLE GUIDELINES
═══════════════════════════════════════════════════

- Write in first-person plural ("we") when discussing the field
- Use present tense for timeless concepts, past tense for the paper's work
- Conversational but rigorous — you're explaining to a brilliant colleague over coffee
- Use "Imagine...", "Think of...", "Here's the thing..." to build engagement
- Ask rhetorical questions throughout — the podcast AI will pick these up as conversation beats
- Include moments of genuine surprise or delight: "And here's the really clever part..."
- Don't be afraid to say "this is hard" or "we don't fully understand this yet"
- Write for someone listening on an exercise bike, not reading at a desk

═══════════════════════════════════════════════════
OUTPUT FORMAT
═══════════════════════════════════════════════════

Output clean markdown with:
- A YAML frontmatter block with title, source, date
- Clear section headers matching the structure above
- No code blocks unless absolutely necessary for a key algorithm
- Natural paragraph flow within each section

TARGET LENGTH: ~{target_words} words total

Begin the briefing now:"""


class BriefingDistiller:
    """
    Transforms a research paper into a NotebookLM-optimized briefing.

    The distiller is the most important component in the pipeline.
    Its output quality directly determines podcast quality.
    """

    def __init__(
        self,
        config: PipelineConfig,
        claude_client: Optional[Anthropic] = None,
        agent_runner: Optional[AgentRunner] = None,
    ):
        self.config = config
        self.claude = claude_client
        self.agent_runner = agent_runner
        if not self.claude and not self.agent_runner:
            raise ValueError(
                "BriefingDistiller requires either a Claude API client or an AgentRunner"
            )
        # Populated by distill() when it returns None — lets the pipeline
        # surface a specific reason in PipelineResult.error instead of a
        # generic "no content" message.
        self.last_error: Optional[str] = None

    def distill(self, paper: Paper) -> Optional[BriefingDocument]:
        """
        Generate a full briefing document from a paper.

        Args:
            paper: The selected Paper to distill.

        Returns:
            BriefingDocument with markdown content ready for NotebookLM,
            or None if generation failed (graceful degradation per Pillar 2).
        """
        self.last_error = None
        logger.info(f"Distilling: {paper.title[:80]}...")

        # Get paper text (abstract as primary source — PDF extraction is future work)
        paper_text = self._get_paper_text(paper)

        # Generate the briefing via Claude
        briefing_content = self._generate_briefing(paper, paper_text)

        if briefing_content is None:
            if self.last_error is None:
                self.last_error = "briefing generation returned no content"
            logger.error(f"Briefing generation failed — {self.last_error}")
            return None

        # Validate and wrap in document
        doc = BriefingDocument(
            title=self._generate_title(paper),
            source_paper=paper,
            generated_at=datetime.now(timezone.utc),
            content=briefing_content,
            metadata={
                "model": self.config.claude.model,
                "target_words": self.config.distiller.target_word_count,
                "style": self.config.distiller.style,
            },
        )

        logger.info(f"Briefing generated: {doc.word_count} words")
        self._validate_briefing(doc)

        return doc

    def _get_paper_text(self, paper: Paper) -> str:
        """
        Get the best available text for a paper.

        Currently uses abstract + metadata. Future versions could
        fetch and extract PDF text for fuller context.
        """
        parts = [
            f"Title: {paper.title}",
            f"\nAuthors: {', '.join(paper.authors)}",
            f"\nAbstract:\n{paper.abstract}",
        ]

        # If this is a blog article with full content, include it
        if paper.source != "arxiv" and hasattr(paper, 'content'):
            parts.append(f"\nFull Content:\n{paper.content}")

        return "\n".join(parts)

    def _generate_briefing(self, paper: Paper, paper_text: str) -> Optional[str]:
        """
        Call Claude API or AgentRunner to generate the briefing markdown.

        Returns None on failure instead of raising — the caller handles
        graceful degradation (Pillar 2: Source Diversity & Resilience).
        """
        user_prompt = build_user_prompt(
            paper=paper,
            paper_text=paper_text,
            user_context=self.config.distiller.user_context,
            target_words=self.config.distiller.target_word_count,
        )

        # Path 1: SDK (preferred)
        if self.claude:
            logger.info(f"Calling Claude SDK ({self.config.claude.model})...")
            try:
                response = self.claude.messages.create(
                    model=self.config.claude.model,
                    max_tokens=self.config.claude.max_tokens,
                    temperature=self.config.claude.temperature,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                content = response.content[0].text
                usage = response.usage
                logger.info(
                    f"Claude response: {usage.input_tokens} input tokens, "
                    f"{usage.output_tokens} output tokens"
                )
                return content
            except Exception as e:
                self.last_error = f"Claude SDK error: {e}"
                logger.error(f"Claude SDK distillation failed: {e}")
                return None

        # Path 2: AgentRunner (CLI fallback)
        if self.agent_runner:
            logger.info("Calling Claude via AgentRunner (CLI backend)...")
            result = self.agent_runner.distill_paper(
                paper=paper,
                distiller_config=self.config.distiller,
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
            )
            if result is None:
                # AgentRunner records a specific reason (timeout / validation / subprocess);
                # forward it so the pipeline can surface it to the user.
                self.last_error = self.agent_runner.last_error or "AgentRunner returned no content"
                logger.error(f"AgentRunner distillation failed — {self.last_error}")
                return None
            logger.info(f"AgentRunner response: {len(result.split())} words")
            return result

        self.last_error = "no Claude backend available"
        logger.error("No Claude backend available for distillation")
        return None

    def _generate_title(self, paper: Paper) -> str:
        """Generate a podcast-friendly title from the paper title."""
        # Keep it readable — truncate very long academic titles
        title = paper.title
        if len(title) > 100:
            title = title[:97] + "..."
        return f"Research Briefing: {title}"

    def _validate_briefing(self, doc: BriefingDocument) -> None:
        """
        Log warnings if the briefing doesn't meet quality expectations.
        Doesn't raise errors — better to deliver an imperfect briefing
        than no briefing at all.
        """
        target = self.config.distiller.target_word_count
        tolerance = 0.3  # 30% tolerance

        if doc.word_count < target * (1 - tolerance):
            logger.warning(
                f"Briefing is short: {doc.word_count} words "
                f"(target: {target}, min: {int(target * (1 - tolerance))})"
            )
        elif doc.word_count > target * (1 + tolerance):
            logger.warning(
                f"Briefing is long: {doc.word_count} words "
                f"(target: {target}, max: {int(target * (1 + tolerance))})"
            )

        # Check that key sections are present
        expected_sections = [
            "Why Should You Care",
            "Core Intuition",
            "Technical Sketch",
            "Evidence",
            "Challenger",
            "Decision Support",
            "Open Questions",
            "Key Takeaways",
        ]
        content_lower = doc.content.lower()
        for section in expected_sections:
            if section.lower() not in content_lower:
                logger.warning(f"Missing expected section: '{section}'")
