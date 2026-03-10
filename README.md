# Paperboy

**Daily AI research briefings, delivered as podcasts.**

Paperboy is an end-to-end pipeline that sources academic papers from ArXiv and blog posts from RSS feeds, scores them for relevance to your research interests, and distills the best into structured markdown briefings optimized for [Google NotebookLM](https://notebooklm.google.com/)'s two-voice podcast generation.

The target user is a research scientist who wants daily AI briefings tailored to their work, consumed during exercise or commute.

### Why "Paperboy"?

You're literally on a bike, getting papers delivered. It's the 1985 arcade game but instead of throwing newspapers at houses, you're absorbing ArXiv papers on an exercise bike. The name is a nod to that image, but the repo's real job is straightforward: source, score, and deliver a daily academic briefing — like a real paperboy, rain or shine.

## How It Works

```
ArXiv API + RSS Feeds  -->  Source  -->  Score & Select  -->  Distill  -->  Podcast
```

1. **Source** — Pulls recent papers from ArXiv categories (cs.AI, cs.LG, cs.CL, stat.ML) and blog posts from configurable RSS feeds (Anthropic, Google Research, OpenAI, Lilian Weng, The Gradient, Distill.pub). Graceful degradation: if one source fails, the pipeline continues with the rest.

2. **Score & Select** — Two-phase hybrid scoring. Fast keyword matching filters candidates, then Claude semantic scoring evaluates relevance to your configured focus areas. Configurable weights (keyword vs. Claude), thresholds, and top-k limits keep API costs predictable.

3. **Distill** — Claude generates a structured 8-section markdown briefing from the top-scoring paper. The briefing is written in a conversational style (inspired by 3Blue1Brown) optimized for NotebookLM's two-voice podcast dialogue. Includes challenger sections that present counterarguments and limitations.

4. **Podcast** — Upload the generated markdown to Google NotebookLM, which converts it into a natural two-voice podcast episode. (Manual step today; automated upload is on the roadmap.)

## Quick Start

```bash
# Clone and install
git clone https://github.com/your-org/paperboy.git
cd paperboy
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Edit focus areas (optional)
# config/default_config.yaml — adjust ArXiv categories, RSS feeds, keywords

# Run the full pipeline
python main.py run

# Or run individual stages
python main.py source              # Fetch papers and blog posts
python main.py select              # Score and select top candidates
python main.py distill             # Generate briefing from top selection

# Run tests
pytest
```

## Configuration

All configuration lives in `config/default_config.yaml`. Key settings:

| Section | What It Controls |
|---------|-----------------|
| `pipeline` | Output directory, max papers to fetch/score, lookback window |
| `arxiv` | ArXiv categories, max results per category, sort order |
| `blogs` | RSS feed URLs and categories |
| `focus_areas` | Primary research interests and keyword lists |
| `claude` | Model selection for scoring and distillation |
| `selector` | Keyword vs. Claude weight, score threshold, top-k |
| `distiller` | Target word count, style, user context for personalization |

API keys go in `.env` (never committed). See `.env.example` for required variables.

## Repository Structure

```
paperboy/
├── main.py                    # CLI entry point (click)
├── src/
│   ├── __init__.py
│   ├── config.py              # YAML config loader + validation
│   ├── models.py              # Paper, Article, ScoredPaper, BriefingDocument
│   ├── sourcer.py             # ContentSourcer ABC, ArxivSourcer, BlogSourcer, SourceManager
│   ├── selector.py            # PaperSelector (keyword + Claude scoring)
│   ├── distiller.py           # BriefingDistiller (Claude-powered, 8-section output)
│   ├── pipeline.py            # DailyPipeline orchestrator, PipelineResult
│   └── tts_interface.py       # TTSProvider ABC, stubs for future TTS
├── config/
│   ├── default_config.yaml    # ArXiv categories, blogs, keywords, Claude settings
│   └── project.yaml           # Project identity, version, phases
├── tests/                     # pytest suites
├── test_pipeline.py           # Integration tests
├── docs/
│   ├── design/                # Pillars, roadmap
│   ├── sessions/              # Session documentation
│   └── plans/                 # Implementation plans
├── output/                    # Generated briefings (gitignored)
├── requirements.txt
├── .env.example
└── CLAUDE.md                  # Development guidance for Claude Code
```

## Current Status

**Phase 1 (Core Pipeline) is complete.** The full Source, Select, Distill, Save pipeline works end-to-end. Phase 2 (Configuration & Polish) is in progress.

### Roadmap

| Phase | Name | Status |
|-------|------|--------|
| 1 | Core Pipeline | Complete |
| 2 | Configuration & Polish | In Progress |
| 3 | Scheduling & Automation | Planned |
| 4 | TTS Integration | Planned |
| 5 | Distribution | Planned |
| 6 | Multi-Paper Briefings | Planned |

See [docs/design/roadmap.md](docs/design/roadmap.md) for full details.

## Design Pillars

1. **Content Quality First** — Briefings optimized for NotebookLM's two-voice podcast dialogue.
2. **Source Diversity & Resilience** — ArXiv + blog RSS with graceful degradation and pluggable sources.
3. **Relevance Through Hybrid Scoring** — Fast keyword matching + Claude semantic scoring with configurable weights.
4. **Pipeline Idempotency** — Same date + config = same output. Deterministic, reproducible briefings.
5. **Extensibility by Design** — Pluggable sources, scorers, output formats. NotebookLM today, TTS tomorrow.

See [docs/design/pillars.md](docs/design/pillars.md) for the full design philosophy.
