# Paperboy

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

**Daily AI research briefings, delivered as podcasts.**

Paperboy is an end-to-end pipeline that sources academic papers from ArXiv and blog posts from RSS feeds, scores them for relevance to your research interests, and distills the best into structured markdown briefings optimized for [Google NotebookLM](https://notebooklm.google.com/)'s two-voice podcast generation.

The target user is a research scientist who wants daily AI briefings tailored to their work, consumed during exercise or commute.

### Why "Paperboy"?

You're literally on a bike, getting papers delivered. It's the 1985 arcade game but instead of throwing newspapers at houses, you're absorbing ArXiv papers on an exercise bike. The name is a nod to that image, but the repo's real job is straightforward: source, score, and deliver a daily academic briefing, like a real paperboy, rain or shine.

## How It Works

```
ArXiv API + RSS Feeds  -->  Source  -->  Score & Select  -->  Distill  -->  Podcast
     (97 candidates)        (all)        (top 5 scored)    (1 briefing)    (NotebookLM)
```

1. **Source** — Pulls recent papers from ArXiv categories (cs.AI, cs.LG, cs.CL, stat.ML) and blog posts from configurable RSS feeds (Google Research, OpenAI, Lilian Weng, The Gradient). Graceful degradation: if one source fails, the pipeline continues with the rest.

2. **Score & Select** — Two-phase hybrid scoring. Fast keyword matching filters all candidates, then Claude semantic scoring evaluates the top 5 against your configured focus areas. Configurable weights (40% keyword + 60% Claude), thresholds, and top-k limits keep API costs predictable.

3. **Distill** — Claude generates a structured 8-section markdown briefing (~4500 words) from the top-scoring paper. The briefing is written in a conversational style (inspired by 3Blue1Brown) optimized for NotebookLM's two-voice podcast dialogue. Includes challenger sections that present counterarguments and limitations.

4. **Podcast** — Upload the generated markdown to Google NotebookLM, which converts it into a natural two-voice podcast episode (~20 minutes). See [NotebookLM Tips](#notebooklm-tips) for how to get the best results.

## Quick Start

```bash
# Clone and set up
git clone https://github.com/jhutchison0/paperboy.git
cd paperboy
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

# Configure (pick one)
# Option A: Anthropic API key (direct API access)
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Option B: Claude Code CLI (uses your existing Max/Pro subscription)
# Just have `claude` installed and on PATH — no API key needed.
# The pipeline auto-detects and uses whichever is available.

# Edit focus areas to match your research interests (optional)
# config/paperboy.yaml — adjust ArXiv categories, RSS feeds, keywords

# Run the full pipeline
python main.py run

# Output lands in output/briefings/ — upload to NotebookLM for your podcast!
```

### Claude Backend Options

The pipeline needs Claude for semantic scoring and briefing distillation. It supports two backends:

| Backend | How It Works | Flag |
|---------|-------------|------|
| **API** (SDK) | Uses `ANTHROPIC_API_KEY` from `.env` | `--backend api` |
| **Agent** (CLI) | Invokes `claude -p` subprocess, uses your Max/Pro subscription | `--backend agent` |
| **Auto** (default) | Tries API first, falls back to CLI, then keyword-only | `--backend auto` |
| **Keyword-only** | No Claude — keyword scoring only, no distillation | `--backend keyword-only` |

```bash
# Explicit backend selection
python main.py run --backend agent          # Force Claude CLI
python main.py run --backend api            # Force API key
python main.py run --backend keyword-only   # Score only, no briefing

# Check what's available
python main.py health
```

### CLI Commands

```bash
python main.py run                     # Full pipeline (source + select + distill + save)
python main.py run --date 2026-03-10   # Run for a specific date
python main.py source                  # Fetch papers and blog posts only
python main.py select                  # Source + score and rank top candidates
python main.py distill                 # Source + select + generate briefing
python main.py distill --paper-id 1904.12787  # Distill a specific ArXiv paper by ID
python main.py health                  # Check connectivity to all services
python main.py info                    # Show current configuration
```

## NotebookLM Tips

After the pipeline produces a briefing in `output/briefings/`, upload it to [NotebookLM](https://notebooklm.google.com/) to generate a podcast episode. Here's how to get the best results.

### Sources

Add **two sources** to your notebook:

1. **The Paperboy briefing** (the `.md` file from `output/briefings/`) — This is the structured narrative that drives the conversation's arc, analogies, and challenger arguments.
2. **The original paper** — Find the ArXiv link in the briefing's frontmatter and add it as a URL or PDF. This gives the hosts deeper technical detail to draw from when they riff beyond the briefing's structure.

The briefing provides the story; the paper provides the depth. Together they produce episodes where the hosts move fluently between intuition and technical detail.

### Audio Overview Settings

Before generating, click **Customize** on the Audio Overview to tune the output:

**Duration**: Set to **Long** (~20-30 minutes). The briefing has ~4500 words across 8 sections, enough material for a substantial conversation. Short episodes tend to skim the most interesting parts (Challengers' Corner, Open Questions).

**Style prompt**: This is where you steer the hosts' tone. Some prompts that work well with Paperboy's briefing structure:

| Goal | Prompt |
|------|--------|
| **Intuition-first** (default recommendation) | "Focus on building intuition rather than showing how processes work. Explain the 'why' before the 'how', like a 3Blue1Brown video. Prioritize clarity — one idea understood deeply is worth more than five skimmed." |
| **Debate-heavy** | "Spend extra time on the counterarguments and limitations. Really dig into the Challengers' Corner — don't let the authors off easy. Play devil's advocate." |
| **Practical focus** | "Emphasize the real-world applications and what this means for practitioners. Less theory, more 'what would I actually do with this on Monday morning?'" |
| **Accessible** | "Assume the listener is smart but not a specialist. Explain jargon when it first appears. Use the analogies from the briefing and add your own." |

You can combine these: "Intuition-first, but spend extra time debating the limitations."

### Iteration

NotebookLM generates different episodes each time from the same sources. If an episode doesn't land right, try:
- Adjusting the style prompt
- Regenerating (you'll get a different conversation)
- Adding or removing the original paper as a source to change the depth level

## Configuration

All configuration lives in `config/paperboy.yaml`. Key settings:

| Section | What It Controls |
|---------|-----------------|
| `pipeline` | Output directory, max papers to fetch/score, lookback window |
| `arxiv` | ArXiv categories, max results per category, sort order |
| `blogs` | RSS feed URLs and categories |
| `focus_areas` | Primary research interests and keyword lists |
| `claude` | Model selection for scoring and distillation |
| `selector` | Keyword vs. Claude weight, score threshold, top-k |
| `distiller` | Target word count, style, user context for personalization |
| `agent_runner` | CLI backend timeouts, retries, output limits |

API keys go in `.env` (never committed). See `.env.example` for variables.

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
│   ├── agent_runner.py        # Claude Code CLI subprocess backend
│   └── tts_interface.py       # TTSProvider ABC, stubs for future TTS
├── config/
│   ├── paperboy.yaml          # ArXiv categories, blogs, keywords, Claude settings
│   └── project.yaml           # Project identity, version, phases
├── tests/                     # pytest suites
│   └── test_pipeline.py       # Integration tests
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

**Phase 2 (Configuration & Polish) is in progress.** The pipeline runs end-to-end with both API and CLI backends. It is live-tested against real ArXiv data; the runs produce ~20-minute podcast episodes via NotebookLM.

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
