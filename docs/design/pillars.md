# Design Pillars

**Tags**: #design #meta #pillar-1 #pillar-2 #pillar-3 #pillar-4 #pillar-5

**Defines**: Content Quality First, Source Diversity & Resilience, Relevance Through Hybrid Scoring, Pipeline Idempotency, Extensibility by Design

**References**: [project.yaml](../../config/project.yaml) — Project identity and phase tracking | [roadmap.md](roadmap.md) — Implementation roadmap

---

These are the non-negotiable truths that guide every decision in this project. When in doubt, return here.

## 1. Content Quality First

**The core principle**: Briefings are optimized for NotebookLM's two-voice podcast dialogue. Structure, tone, and depth serve listener comprehension during exercise or commute.

Paperboy does not exist to summarize papers. It exists to produce briefings that become excellent podcast episodes. Every decision about structure, length, terminology, and narrative flow must be evaluated through this lens: will this sound good when two AI voices discuss it?

**Why this matters**: The end product is audio consumed while the listener's hands and eyes are busy. Dense academic prose, long equations, and laundry lists of results are useless in this medium. Briefings must tell a story: what problem exists, what was tried, why it matters, and what the listener should take away. NotebookLM's dialogue format rewards briefings that pose questions, present tensions, and offer clear takeaways.

**How it's enforced in the codebase**:
- The distiller prompt specifies an 8-section structure designed for narrative flow
- Challenger sections present counterarguments, creating natural dialogue material
- Target word count (4,500 words) is calibrated for ~20-minute podcast episodes
- Style parameter ("3blue1brown") enforces conversational, curiosity-driven tone
- User context in the distiller config personalizes relevance framing

**What violating this looks like**: A briefing that reads like an abstract collection. Bullet-point summaries with no narrative thread. Technical jargon without explanation. Missing the "so what?" that makes a listener care.

**Connection to other pillars**: Quality depends on Pillar 3 (selecting relevant papers) and is enabled by Pillar 5 (extensible output formats for future TTS).

---

## 2. Source Diversity & Resilience

**The core principle**: ArXiv + blog RSS with graceful degradation. If one source fails, the pipeline continues. Pluggable source architecture (ContentSourcer ABC).

Good briefings require good inputs. ArXiv alone misses industry perspectives, practical insights, and timely commentary. Blog feeds from research labs and independent ML writers provide complementary coverage. But no external source is reliable: APIs rate-limit, feeds go stale, servers go down. The pipeline must handle failure gracefully.

**Why this matters**: A pipeline that crashes when one RSS feed times out is useless for daily automation. A pipeline that only reads ArXiv misses half the interesting work in AI. Source diversity ensures breadth; resilience ensures the pipeline runs every day regardless of which sources are having a bad day.

**How it's enforced in the codebase**:
- `ContentSourcer` is an ABC; `ArxivSourcer` and `BlogSourcer` are independent implementations
- `SourceManager` aggregates results from all sourcers, catching and logging failures per source
- Each sourcer has its own timeout and rate-limit settings
- Failed sources produce warnings, not exceptions; the pipeline continues with whatever succeeded
- New source types can be added by implementing the `ContentSourcer` interface

**What violating this looks like**: A single try/except around the entire source phase that aborts on any failure. Hard-coded feed URLs in Python instead of config. A monolithic function that mixes ArXiv API calls with RSS parsing.

**Connection to other pillars**: Diverse sources feed Pillar 3 (more candidates for scoring). Resilience supports Pillar 4 (the pipeline runs reliably every day). The ABC pattern embodies Pillar 5 (extensibility).

---

## 3. Relevance Through Hybrid Scoring

**The core principle**: Two-phase scoring. Fast keyword matching followed by Claude semantic scoring, with configurable weights, thresholds, and focus areas.

Not every paper matters to every researcher. Paperboy's value comes from filtering 50+ daily candidates down to the one or two that are genuinely relevant to the user's work. Keyword matching is fast and cheap but misses semantic connections. Claude scoring understands meaning but costs money and time. The hybrid approach uses keywords as a fast filter, then applies Claude's judgment only to the top candidates.

**Why this matters**: Without scoring, the pipeline is just a random paper summarizer. With only keywords, it misses papers that are relevant but use different terminology. With only Claude scoring on every paper, API costs explode. The hybrid approach delivers high relevance at reasonable cost.

**How it's enforced in the codebase**:
- `PaperSelector` implements the two-phase pipeline: keyword pass, then Claude pass on top-k
- Weights are configurable: `keyword_weight: 0.4`, `claude_weight: 0.6`
- `min_score_threshold` prevents low-quality selections from reaching distillation
- `top_k_for_claude` controls how many papers get expensive Claude scoring
- Focus areas and keywords live in config, not code; the user tunes without touching Python
- The cheaper `claude-haiku` model handles scoring; the full model handles distillation

**What violating this looks like**: Scoring all 50 papers with Claude (expensive, slow). Using only title matching (misses relevant work). Hard-coding relevance criteria in the selector instead of reading from config. No threshold: always selecting the "best" even when nothing is relevant.

**Connection to other pillars**: Good selection directly enables Pillar 1 (quality briefings from quality inputs). Configurable scoring supports Pillar 5 (swappable scoring strategies). Deterministic scoring supports Pillar 4 (same inputs = same selections).

---

## 4. Pipeline Idempotency

**The core principle**: Same date + config = same output. Date-stamped runs, deterministic selection, reproducible briefings.

If you run the pipeline twice on the same day with the same config, you should get the same briefing. This is not a nice-to-have; it's essential for debugging, for trusting the output, and for avoiding duplicate work in automated scheduling.

**Why this matters**: Idempotency makes the pipeline debuggable. If a briefing looks wrong, you can re-run the same date and trace what happened. It prevents automated schedulers from creating duplicate episodes. It enables backfilling: running the pipeline for past dates to generate briefings you missed. And it builds trust: the pipeline does what you expect, every time.

**How it's enforced in the codebase**:
- Pipeline runs are keyed by date; output files include the date in their path
- ArXiv queries use date ranges, not "most recent"; same date = same query
- Selector scoring is deterministic given the same inputs and config
- Claude API calls use consistent prompts; while not bit-identical, the structure is reproducible
- `PipelineResult` captures metadata (date, config hash, sources, scores) for audit

**What violating this looks like**: Using "today" as a relative reference that shifts mid-run. Random sampling from candidates. Output files without dates in their names. No way to re-run a past date.

**Connection to other pillars**: Idempotency enables Pillar 3 (reproducible scoring for tuning). It requires Pillar 2 (resilient sources that return consistent results for date ranges). It supports Pillar 5 (scheduling and automation in Phase 3).

---

## 5. Extensibility by Design

**The core principle**: Pluggable sources, scorers, output formats. NotebookLM today, TTS tomorrow. New capabilities slot in without rewriting the pipeline.

Paperboy's roadmap extends well beyond the current pipeline: TTS integration, podcast RSS feeds, multi-paper episodes, new source types. Each of these should be additive. Adding a new source should mean implementing one class. Adding TTS should mean implementing one provider. The pipeline orchestrator should not need to change.

**Why this matters**: Rewriting the pipeline for every new feature is unsustainable. The ABC pattern for sources (`ContentSourcer`), the planned ABC for TTS (`TTSProvider`), and the stage-based pipeline architecture ensure that new capabilities compose with existing ones. This is not premature abstraction; it's the architecture that makes the roadmap achievable.

**How it's enforced in the codebase**:
- `ContentSourcer` ABC — implement `fetch()` to add a new source type
- `TTSProvider` ABC (in `tts_interface.py`) — stub ready for ElevenLabs or other providers
- `DailyPipeline` orchestrates stages without knowing implementation details
- Config-driven behavior — new feeds, categories, and keywords require zero code changes
- Each pipeline stage (source, select, distill) has a clean interface and can run independently

**What violating this looks like**: A pipeline function with `if source_type == "arxiv":` branches. Distiller code that assumes markdown output format. Hard-coded model names in the selector instead of reading from config. A monolithic `run()` function that cannot be decomposed.

**Connection to other pillars**: Extensibility enables all other pillars to scale. New sources (Pillar 2) plug in cleanly. New scoring strategies (Pillar 3) can be swapped. New output formats (Pillar 1) can target different media. Automation (Pillar 4) requires clean stage boundaries.

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-09 | Hybrid keyword + Claude scoring | Fast filtering + semantic understanding at reasonable API cost |
| 2026-03-09 | NotebookLM as initial podcast target | Best available two-voice podcast generation; no API needed |
| 2026-03-09 | 8-section briefing structure | Narrative flow optimized for dialogue-based podcast format |
| 2026-03-09 | ContentSourcer ABC pattern | Pluggable sources without pipeline rewrites |
| 2026-03-09 | YAML config as source of truth | User tunes behavior without touching Python code |
| 2026-03-09 | Date-keyed pipeline runs | Idempotency, backfilling, and deduplication |
