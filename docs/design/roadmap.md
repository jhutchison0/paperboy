# Roadmap — Paperboy Research Podcast Pipeline

**Tags**: #design #meta #roadmap
**References**: [pillars.md](pillars.md) — Design principles | [project.yaml](../../config/project.yaml) — Build phase status

---

## Where We Are

Paperboy's **core pipeline is complete** (Phase 1). The system sources papers from ArXiv and blog posts from RSS feeds, scores them using hybrid keyword + Claude semantic scoring, and distills the top selection into a structured markdown briefing optimized for Google NotebookLM's two-voice podcast generation.

**Phase 2 (Configuration & Polish) is in progress**, focusing on agent/command alignment, error handling, and CLI refinements.

### Current Capabilities

- ArXiv sourcing across configurable categories (cs.AI, cs.LG, cs.CL, stat.ML)
- RSS feed sourcing from 6 research blogs (Anthropic, Google Research, OpenAI, Lilian Weng, The Gradient, Distill.pub)
- Graceful degradation when individual sources fail
- Two-phase hybrid scoring (keyword matching + Claude semantic evaluation)
- Claude-powered 8-section briefing distillation
- Configurable focus areas, keywords, and scoring weights
- CLI with individual stage commands (source, select, distill) and full pipeline run
- Date-stamped output for idempotent runs

## Phase Breakdown

### Phase 1: Core Pipeline -- COMPLETE

**Goal**: End-to-end pipeline that produces a briefing from today's papers.

**Delivered**:
- `ArxivSourcer` and `BlogSourcer` implementing `ContentSourcer` ABC
- `SourceManager` with per-source error handling and aggregation
- `PaperSelector` with keyword scoring and Claude semantic scoring
- `BriefingDistiller` producing 8-section structured markdown
- `DailyPipeline` orchestrator with `PipelineResult` metadata
- Click-based CLI (`main.py`) with `run`, `source`, `select`, `distill` commands
- Data models: `Paper`, `Article`, `ScoredPaper`, `BriefingDocument`
- YAML config loader with validation
- Integration tests (`test_pipeline.py`)

### Phase 2: Configuration & Polish -- IN PROGRESS

**Goal**: Robust, well-documented system ready for daily use.

**Deliverables**:
- Agent roster and command structure aligned to project domains
- Improved error messages and logging throughout the pipeline
- CLI refinements (help text, validation, progress output)
- Config validation with clear error messages for missing/invalid settings
- Project identity files (CLAUDE.md, README, pillars, roadmap)
- Session documentation practices established

### Phase 3: Scheduling & Automation

**Goal**: Hands-off daily pipeline execution.

**Deliverables**:
- Cron job or scheduled task configuration for daily runs
- Date-based deduplication (skip if today's briefing already exists)
- Output rotation and cleanup (keep last N briefings, archive older)
- Run history log with success/failure tracking
- Notification on failure (email, Slack webhook, or similar)
- Backfill command for generating missed briefings

### Phase 4: TTS Integration

**Goal**: Generate audio directly, bypassing manual NotebookLM upload.

**Deliverables**:
- `TTSProvider` ABC implementation (stub already in `tts_interface.py`)
- ElevenLabs API integration for two-voice synthesis
- Voice configuration (speaker profiles, pacing, tone)
- Briefing-to-script conversion (markdown to dialogue format)
- Audio file output alongside markdown briefings
- Cost tracking and budget controls for TTS API usage

### Phase 5: Distribution

**Goal**: Subscribable podcast feed with automated publishing.

**Deliverables**:
- Podcast RSS feed generation (RSS 2.0 with iTunes extensions)
- Episode metadata (title, description, date, duration)
- Audio file hosting (S3, Cloudflare R2, or similar)
- Automated upload after successful pipeline + TTS run
- Feed validation and testing with podcast apps
- Episode archive and back-catalog management

### Phase 6: Multi-Paper Briefings

**Goal**: Episodes covering multiple related papers with cross-paper analysis.

**Deliverables**:
- Multi-paper selection (top N papers instead of top 1)
- Thematic grouping (cluster related papers into themes)
- Comparative analysis prompts (how do selected papers relate?)
- Extended briefing format for multi-paper episodes
- Episode length management (target duration per paper count)
- Weekly digest mode (best papers of the week in one episode)

## Near-Term Priorities (Phase 2-3)

The immediate focus is making paperboy reliable and pleasant for daily use:

1. **Polish the CLI** — Clear help text, progress indicators, informative error messages
2. **Validate config** — Catch misconfiguration early with actionable error messages
3. **Stabilize agent roster** — Ensure each agent has a clear domain and the team templates work
4. **Automate scheduling** — The pipeline should run daily without manual intervention
5. **Add deduplication** — Don't regenerate briefings that already exist for a given date

## Future Vision (Phase 4-6)

The long arc of paperboy is a fully automated, personalized research podcast:

- **Phase 4** removes the manual NotebookLM step. The pipeline produces audio directly using ElevenLabs or equivalent TTS. Two distinct voices discuss the research, with natural pacing and emphasis.
- **Phase 5** makes the podcast subscribable. A generated RSS feed with hosted audio files means the briefing appears in your podcast app alongside your other subscriptions. No manual steps at all.
- **Phase 6** elevates the content. Instead of one paper per episode, briefings cover multiple related papers, draw comparisons, identify trends, and provide the kind of synthesis that makes a daily podcast genuinely valuable to a working researcher.

## Beyond Phase 6

Potential future directions once the core vision is realized:

- **Multi-topic feeds** — Separate podcast feeds for different research areas (NLP, RL, computer vision), each with its own focus keywords and scoring config
- **User preference learning** — Track which episodes get listened to, which get skipped, and adjust scoring weights automatically
- **Community sharing** — Share config profiles ("here's my focus areas for robotics research") so others can bootstrap their own tailored feeds
- **Conference coverage** — Special episodes covering paper batches from NeurIPS, ICML, ACL, etc.
- **Paper discussion threads** — Generated follow-up episodes when a paper sparks significant community discussion
- **Citation network analysis** — Source papers that cite or are cited by papers the user found valuable, creating a personalized recommendation graph

## Design Questions (Open)

1. **TTS provider**: ElevenLabs is the leading option, but cost-per-episode may favor alternatives. Evaluate when Phase 4 begins.
2. **Multi-paper scoring**: How many papers per episode? Fixed count or dynamic based on quality threshold?
3. **Dialogue format**: Should the TTS script be a direct conversion from the briefing, or a separate dialogue-optimized format?
4. **Hosting**: Self-hosted vs. podcast hosting platform for Phase 5 distribution?
5. **Feedback loop**: How to capture listener preference signals for future recommendation tuning?
