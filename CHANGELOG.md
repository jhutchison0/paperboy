# Changelog

All notable changes to this project are documented here. This is the canonical timeline of project versions.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for pre-1.0 development.

---

## [0.1.0] - 2026-03-10

**Milestone**: Core Pipeline — End-to-End Working

The research podcast pipeline is functional: sources papers from ArXiv and blog RSS feeds, scores them via hybrid keyword + Claude semantic scoring, distills the best paper into a structured markdown briefing optimized for Google NotebookLM podcast generation.

### Core Pipeline (`src/`)
- **`config.py`** — YAML configuration loader with validation, environment variable overrides for API keys
- **`models.py`** — Data models: `Paper`, `Article` (converts to Paper), `ScoredPaper` (with relevance score + reasoning), `BriefingDocument` (markdown output with word count tracking)
- **`sourcer.py`** — `ContentSourcer` ABC with two implementations:
  - `ArxivSourcer`: Queries ArXiv API by configurable categories (cs.AI, cs.LG, cs.CL, stat.ML), deduplicates across categories, respects rate limits
  - `BlogSourcer`: Parses RSS/Atom feeds from configured research blogs (Anthropic, Google Research, OpenAI, etc.), handles various date formats
  - `SourceManager`: Orchestrates both sources with graceful degradation
- **`selector.py`** — `PaperSelector` with two-phase hybrid scoring:
  - Phase 1: Fast keyword matching on title (0.5), abstract (0.35), categories (0.15)
  - Phase 2 (optional): Claude semantic scoring on top-K candidates
  - Configurable thresholds, weights, and focus areas
- **`distiller.py`** — `BriefingDistiller` using Claude to generate 8-section markdown briefings (~4500 words):
  - Opening Hook, Core Intuition (3 analogies), Technical Sketch, Evidence, Challengers' Corner, Decision Support Impact, Open Questions, Key Takeaways
  - 3Blue1Brown-inspired style (intuition-first, conversational, visual)
  - YAML frontmatter and section validation
- **`pipeline.py`** — `DailyPipeline` orchestrator chaining source → select → distill → save
  - `PipelineResult` with success/failure metadata
  - Health checks for ArXiv, blogs, and Claude API
- **`tts_interface.py`** — `TTSProvider` ABC and stubs for future TTS integration (ElevenLabs, NotebookLM exporter)

### CLI (`main.py`)
- Click-based CLI with `run`, `health-check`, and `show-config` commands
- Configurable via command-line options, YAML config, and environment variables

### Configuration
- **`config/default_config.yaml`** — ArXiv categories, blog feed URLs, focus keywords, Claude model settings, distiller parameters
- **`config/project.yaml`** — Project identity, version, build phases, design pillars

### Infrastructure
- **`.claude/agents/`** — 6 prepositioned agents: pipeline-sme, content-curator, distiller-dev, test-runner, python-prototyper, code-reviewer
- **`.claude/commands/`** — 5 workflow commands: session-start, session-end, pcc, pci, implement-source
- **`.claude/skills/`** — 4 Level 0 portable skills + SKILLS_FRAMEWORK.md
- **`docs/design/pillars.md`** — 5 design pillars (Content Quality, Source Diversity, Hybrid Scoring, Idempotency, Extensibility)
- **`docs/design/roadmap.md`** — 6-phase roadmap through TTS integration and distribution

### Testing
- **`test_pipeline.py`** — Integration tests for models, config, scoring, and pipeline flow

### How to Run

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your ANTHROPIC_API_KEY

# Run the pipeline
python main.py run

# Health check
python main.py health-check

# Show config
python main.py show-config

# Tests
pytest                           # All tests
pytest -k sourcer                # Sourcing tests
pytest -k selector               # Selection tests
pytest -k distiller              # Distiller tests
pytest -k pipeline               # Pipeline tests
```
