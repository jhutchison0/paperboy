# Changelog

All notable changes to this project are documented here. This is the canonical timeline of project versions.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for pre-1.0 development.

---

## [0.2.0] - 2026-03-11

**Milestone**: Dual-Backend Architecture & Live End-to-End Validation

The pipeline now supports two Claude backends: the Anthropic SDK (API key) and the Claude Code CLI (Max/Pro subscription). First successful live run against real ArXiv data produced a ~20-minute podcast episode via Google NotebookLM.

### Dual-Backend Architecture
- **`src/agent_runner.py`** — NEW: Claude Code CLI subprocess backend (`claude -p`)
  - `score_paper()`: Semantic scoring via CLI with JSON output parsing
  - `distill_paper()`: Briefing generation via CLI with section validation
  - `is_available()`: CLI detection for health checks
  - Preamble stripping for JSON and markdown output
  - Sensitive env var scrubbing (API keys, CLAUDE* vars)
  - Configurable timeouts, retries, and output size limits
- **`src/pipeline.py`** — `_resolve_backend()` with auto-detection fallback chain:
  - Auto mode: API key → Claude CLI → keyword-only
  - Explicit: `--backend api|agent|keyword-only`
- **`src/selector.py`** — AgentRunner as fallback scoring path
- **`src/distiller.py`** — AgentRunner as fallback distillation path, graceful degradation (returns None instead of raising on failure)

### CLI Improvements
- **`--backend` flag** on `run`, `select`, `distill` commands
- **`--date` flag** with strict YYYY-MM-DD parsing (mutually exclusive with `--days-back`)
- **`source` subcommand** — fetch papers/articles without scoring
- **`select` subcommand** — source + score + rank top candidates
- **`distill` subcommand** — full pipeline with distillation focus
- **`health` command** — checks ArXiv, blogs, Claude API, and Claude CLI
- **`info` command** — displays current configuration summary
- Accurate output messaging: distinguishes keyword-only mode from distillation failure

### Config Validation
- **`src/config.py`** — Structured validation returning `(errors, warnings)` tuple
  - Range checks: temperature (0-1), max_tokens (>0), min_score_threshold (0-1), top_k_for_claude (>0), weight sum (~1.0), target_word_count (>0), days_lookback (>0), max_retries (>=0)
  - Agent runner settings: timeout, output bytes, retry validation
- **`config/paperboy.yaml`** — Agent runner section with tunable timeouts and limits

### Testing
- **`tests/test_agent_runner.py`** — 48 tests: invocation, preamble stripping, score/briefing validation, env scrubbing, retry logic
- **`tests/test_config_validation.py`** — 27 tests: all config validation paths and range checks
- **`tests/test_pipeline_backend.py`** — 10 tests: backend resolution, fallback chain, health checks
- **`tests/test_cli_output.py`** — 5 tests: CLI output messaging for all run outcome branches
- Total: 94 tests passing

### Documentation
- **README.md** — Quickstart with venv, dual-backend docs, NotebookLM tips
- **CHANGELOG.md** — This entry
- Session docs for AgentRunner implementation, Phase 2 hardening, and live E2E test

### How to Run

```bash
# Setup
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Optional — not needed if using Claude CLI backend

# Run the pipeline
python main.py run                     # Auto-detect backend
python main.py run --backend agent     # Force Claude CLI
python main.py run --date 2026-03-10   # Specific date

# Individual stages
python main.py source                  # Fetch papers only
python main.py select --backend agent  # Score and rank
python main.py distill                 # Full pipeline with distillation

# Utilities
python main.py health                  # Service connectivity check
python main.py info                    # Show current config

# Tests
pytest                                 # All 94 tests
```

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
- Click-based CLI with `run`, `health`, and `info` commands
- Configurable via command-line options, YAML config, and environment variables

### Configuration
- **`config/paperboy.yaml`** — ArXiv categories, blog feed URLs, focus keywords, Claude model settings, distiller parameters
- **`config/project.yaml`** — Project identity, version, build phases, design pillars

### Infrastructure
- **`.claude/agents/`** — 6 prepositioned agents: pipeline-sme, content-curator, distiller-dev, test-runner, python-prototyper, code-reviewer
- **`.claude/commands/`** — 5 workflow commands: session-start, session-end, pcc, pci, implement-source
- **`.claude/skills/`** — 4 Level 0 portable skills + SKILLS_FRAMEWORK.md
- **`docs/design/pillars.md`** — 5 design pillars (Content Quality, Source Diversity, Hybrid Scoring, Idempotency, Extensibility)
- **`docs/design/roadmap.md`** — 6-phase roadmap through TTS integration and distribution

### Testing
- **`tests/test_pipeline.py`** — Integration tests for models, config, scoring, and pipeline flow

### How to Run

```bash
# Setup
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your ANTHROPIC_API_KEY

# Run the pipeline
python main.py run

# Health check
python main.py health

# Show config
python main.py info

# Tests
pytest                           # All tests
pytest -k sourcer                # Sourcing tests
pytest -k selector               # Selection tests
pytest -k distiller              # Distiller tests
pytest -k pipeline               # Pipeline tests
```
