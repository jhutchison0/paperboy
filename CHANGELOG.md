# Changelog

All notable changes to this project are documented here. This is the canonical timeline of project versions.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for pre-1.0 development.

---

## [Unreleased]

### Daily Run and Delivery (CONOP COURIER Wave 1, 2026-10-24)
- **`--slack` on `run`**: one summary post per run to `PAPERBOY_SLACK_CHANNEL` (title, link, Claude's reasoning, the abstract trimmed, the day's top five, the briefing's filename, a reaction legend, one telemetry line); partial and failed runs post their error. Exit 1 with `Configuration error:` when `SLACK_BOT_TOKEN` or the channel is missing; exit 3 when the post fails after a saved briefing
- **`src/slack.py`**: NEW: `post_message`, `auth_test`, `build_message`, `SlackError`; stdlib `urllib` only, one retry on HTTP 429, no retry on timeout, mrkdwn escaping
- **Run record** (`src/pipeline.py`): one JSON line per run appended to `run_history.jsonl` beside the briefings, written after delivery: date, start, duration, status, backend, machine, the models that ran, the selected paper and the day's top candidates, counts fetched, briefing path and words, error, the Slack receipt, git sha, a SHA-256 of the effective config. Gap G8's collector
- **Delivery seam**: `DailyPipeline(config, backend, deliverer=None)`; a raising deliverer never rolls back the briefing or the dedup record
- **`PipelineResult`**: gains `backend`, `machine`, `scoring_model`, `distill_model`, `started_at`, `duration_s`, `top_candidates`, `slack_ts`, `slack_error`; selection returns the Claude-scored top candidates and the pipeline keeps the first
- **Headless `AgentRunner`** (`src/agent_runner.py`): `CLAUDE_CODE_OAUTH_TOKEN` from `claude setup-token` survives the environment strip; `ANTHROPIC_AUTH_TOKEN` joins `ANTHROPIC_API_KEY` in it; `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` and `DISABLE_AUTOUPDATER=1` are set; `claude -p` runs with `--output-format json --no-session-persistence --tools ""`, the text read from the JSON `result` and the model name from `modelUsage`
- **`HOME_BRIEFINGS_ROOT`**: the first `HOME_*` variable; when set it replaces `pipeline.output_dir` for the briefings, the dedup history and the run record; unset, the YAML default stands
- **API fallback on current models** (`config/paperboy.yaml`, `src/config.py`, `src/selector.py`, `src/distiller.py`): distill on `claude-opus-5-5`, scoring on `claude-haiku-5-5` with thinking disabled and low effort; no sampling parameter on either call; both call sites read the first `text` block by type; a leftover `claude.temperature` key warns
- **`health`**: an unconfigured backend prints SKIPPED and does not fail the check; a `slack` line via `auth.test` when the token is set
- **`deploy/`**: NEW: `README.md` (the Custom App runbook, placeholders only), `crontab` (one tick at 05:30, `run --slack`), `update-server.sh` (push, pull, reinstall when `requirements.txt` changed, `health` and `source` as the proof; prints the CLI version, the token's renewal comment and the gap G5 line)
- **`tests/test_boundary_line.py`**: no tracked file names a UNC path, an `smb://` host or an IPv4 literal outside the allowlist
- **`requirements.txt`**: `anthropic<1` for this cycle
- **Removed**: the retired `claude-sonnet-4-20250514` and `claude-haiku-4-5-20251001` IDs and the `claude.temperature` key; `_strip_preamble_json` and `_strip_preamble_markdown`; the dead `OUTPUT_DIR` and `CONFIG_PATH` lines in `.env.example`

### Server Deploy (CONOP COURIER Wave 2, 2026-10-25)
- **`config/project.yaml`**: `paperboy` joins the roster (role server, backend agent), the name the container reports as its hostname
- **`deploy/update-server.sh`**: the proof string exports PATH, since `ssh <alias> 'cmd'` is a non-login shell with no `~/.local/bin`; the file carries its executable bit in the index. `tests/test_update_server_script.py` (4 tests) pins both
- **`.gitignore`**: `.env.server`, the server's env file built on the workstation and sent by one `scp`
- **`deploy/README.md`**: the `model` key in the server's CLI settings, the `.env.server` staging steps, the second dataset's two ACL entries, the login-shell note for the host proof, four traps met 2026-10-25

### First Tick (CONOP COURIER Wave 2, 2026-10-26)
- **Run record** (`src/pipeline.py`): `git_sha` is read from `.git/HEAD` and the ref it names, loose or packed, not from a `git` binary the App image lacks; the first tick's line had read `None`. `tests/test_run_record.py`: four `_git_sha` tests and a no-binary record test
- **`deploy/README.md`**: `SSL_CERT_FILE` in the App YAML names the venv's certifi bundle, since `debian:bookworm-slim` has no CA store and `urllib` (the Slack post, the feed fetch) reads it; the first tick posted nothing (`CERTIFICATE_VERIFY_FAILED`) and fetched 0 articles. `tests/test_deploy_readme.py` pins the line. Two traps dated 2026-10-26

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
