# CONTEXT.md — What Paperboy Is

A one-page narrative of paperboy's identity, mission, current state, and key constraints. Uses terms defined in [LANGUAGE.md](LANGUAGE.md). For machine-readable state, see [config/project.yaml](config/project.yaml).

Maintained via the `maintaining-project-context` skill. Update when the project's mission, scope, or doctrine relationship materially changes, not for routine task progress.

---

## Identity

**Paperboy** is a Python pipeline that sources academic papers from ArXiv and blog articles from RSS feeds, scores them for relevance to a research scientist's interests, and distills the best into structured markdown briefings optimized for Google NotebookLM's two-voice podcast generation.

The name is a lighthearted nod to the 1985 arcade game: the image of riding an exercise bike while the day's papers arrive. The arcade and fitness angles are flavor only. The codebase is a research-paper curation and delivery system.

Paperboy is a **downstream consumer** of the `tacsop` template repo for doctrine (agent definitions, skills, commands, conventions). It does not propagate doctrine to other repos.

---

## Mission

- **Curate daily.** Deliver one (eventually multiple) high-relevance AI research briefing per day to a research scientist whose interests are tracked in `config/paperboy.yaml` (categories, focus keywords, weights).
- **Score for relevance.** Two-phase hybrid scoring (fast keyword filter, then Claude semantic ranking) is the path from a day's noisy candidate set to the one paper worth briefing. Weights and thresholds are tunable, not hardcoded.
- **Optimize for spoken consumption.** Briefings are structured for NotebookLM's two-voice podcast format: intuition first, technical depth second, written for listening during exercise or commute.
- **Stay honest about failure.** When sourcing succeeds but distillation fails, the pipeline reports `partial` and does NOT poison the dedup record. Same date + same config = same output. Idempotency is non-negotiable.
- **Adopt upstream doctrine selectively.** The agent framework, skills, command conventions, and doctrine artifacts come from `tacsop`. Adopt with intent; adapt or skip when paperboy's domain warrants.

This is a personal-use research tool with a working pipeline, not a product. Treat changes in the context of one user's daily research workflow.

---

## Current State

See [config/project.yaml](config/project.yaml) for canonical values. Snapshot at last update of this file:

- **Version**: 0.2.0
- **Active phase**: Phase 2 — Configuration & Polish (Phase 1 — Core Pipeline complete and working end-to-end).
- **Active work**: Public-repo preparation (prose sweep per `writing-simple-and-direct`), 2026-07-20 upstream doctrine cycle adopted (planning formats, prose style, shift-left-testing 2.1.0).
- **Tests**: 156 passing.
- **Backend support**: API (Anthropic SDK), Agent (Claude CLI subprocess for Max subscription), keyword-only fallback. Auto mode tries them in that order.
- **Known reliability concerns**: none open. The 2026-07-20 blog feed audit replaced the stale Google feedburner URL, updated OpenAI's redirect, and retired the dead Anthropic feed and archived Distill.pub (both commented out in `config/paperboy.yaml`).

---

## Constraints

The hard rules. Violating these requires explicit user override per change.

**Pillars** (formally tracked in `config/project.yaml` and [docs/design/pillars.md](docs/design/pillars.md)):

1. **Content Quality First** — briefings optimized for two-voice podcast dialogue; structure, tone, and depth serve listener comprehension.
2. **Source Diversity & Resilience** — ArXiv + blog RSS with graceful degradation. If one source fails, the pipeline continues. Pluggable sources via `ContentSourcer` ABC.
3. **Relevance Through Hybrid Scoring** — two-phase keyword + Claude semantic scoring with configurable weights, thresholds, focus areas.
4. **Pipeline Idempotency** — same date + same config = same output. Date-stamped runs, deterministic selection, reproducible briefings. No randomness.
5. **Extensibility by Design** — pluggable sources, scorers, output formats. NotebookLM today, TTS tomorrow.

**Hard rules**:

- Python 3.11 minimum.
- All Python commands run inside the project venv (`.venv/`).
- API keys live in `.env`; never committed.
- Session docs write to `docs/sessions/YYYYMMDD_<subject>.md` per [docs/session-doc-format.md](docs/session-doc-format.md).
- Plans write to `docs/plans/`.
- ADRs write to `docs/adr/NNNN-<slug>.md` and must pass the triple filter.
- Internal docs may use the military escalation vocabulary (PCC, PCI, SITREP, OPORD, CONOP, TCS). Externally-shared content uses civilian equivalents per the [LANGUAGE.md crosswalk](LANGUAGE.md#vocabulary-crosswalk-military--civilian).
- Every new sourcer, scorer, or distillation feature ships with tests in `tests/` (the PostToolUse shift-left audit hook logs evidence to `.claude/audits/shift-left-violations.log`).

**Anti-rules** (do not do these):

- Do not theme features around the arcade/bike/fitness joke. Paperboy is a research pipeline; the name is flavor.
- Do not add abstractions for hypothetical future requirements.
- Do not add new agents until existing agents are demonstrably saturated on their intended problems.
- Do not bulk-install third-party skill packs. Cherry-pick patterns from upstream doctrine; never the whole catalog.
- Do not migrate side-effect-carrying commands (session-end, pcc) to auto-triggering skills.
- Do not record a selection in `SelectionHistory` when distillation fails. The paper must remain available for retry.

---

## Key Relationships

**Upstream doctrine source**: `tacsop` (GitHub `jhutchison0/tacsop`, named `utils` until 2026-07-20) propagates doctrine updates via `.claude/upstream-update.md`. Paperboy reviews each entry and adopts/adapts/skips per artifact. Major cycles adopted: 2026-05-19 (LANGUAGE.md, CONTEXT.md, ADR system, SKILLS_FRAMEWORK v2, shift-left audit hook) and 2026-07-20 (CONOP/OPORD plan formats, writing-simple-and-direct, shift-left-testing 2.1.0).

**Sister repo (pattern, not doctrine)**: `elephant-graveyard` (LED curtain digital twin) shares workspace patterns (agents, commands, skills, session docs) but is not a doctrine source. Paperboy was bootstrapped from elephant-graveyard's infrastructure; the pipeline code in `src/` was written fresh.

**Agent roster** (current, in `.claude/agents/`, eight total):
- `pipeline-sme` — mission alignment, roadmap, pillars
- `proposer` — solution-space exploration, pre-implementation debate
- `content-curator` — sources, selection, scoring
- `distiller-dev` — briefing quality, prompts
- `python-prototyper` — pipeline implementation
- `test-runner` — pytest execution
- `code-reviewer` — reviews against pillars
- `decision-scientist` — weights, scoring fairness, bias, statistical soundness

**Team templates** (in `.claude/teams/`): `source-development`, `feature-development`, `briefing-quality`, `bug-fix`, `code-review`.

**Skills inventory**: see `.claude/skills/SKILLS_FRAMEWORK.md` for the canonical list and conventions.

---

## Reading Order for New Agents and Contributors

When an agent or human is introduced to paperboy, point them at these files in this order:

1. **This file** (`CONTEXT.md`) — what paperboy is.
2. [LANGUAGE.md](LANGUAGE.md) — how we name things.
3. [CLAUDE.md](CLAUDE.md) — workflow conventions and quick commands.
4. [config/project.yaml](config/project.yaml) — current machine-readable state (version, phase, paths).
5. [config/paperboy.yaml](config/paperboy.yaml) — pipeline tunables (sources, scoring weights, distiller settings).
6. [docs/design/pillars.md](docs/design/pillars.md) — the five design pillars in detail.
7. [.claude/README.md](.claude/README.md) — agent roster, scope matrix, team templates.
8. [docs/adr/](docs/adr/) — accepted architecture decisions; check before reopening any decision they cover.
9. [docs/sessions/](docs/sessions/) — most recently modified file for live context.

---

## Distinguishing This File from Adjacent Artifacts

| Artifact | What it answers |
|---|---|
| `CONTEXT.md` (this file) | *What is paperboy and what does it care about?* |
| [LANGUAGE.md](LANGUAGE.md) | *What do specific terms mean in this project?* |
| [config/project.yaml](config/project.yaml) | *What is the machine-readable current state?* |
| [config/paperboy.yaml](config/paperboy.yaml) | *What are the pipeline's tunable parameters?* |
| [CLAUDE.md](CLAUDE.md) | *What conventions and commands does the agent need at hand?* |
| [docs/design/pillars.md](docs/design/pillars.md) | *What are the five design pillars in detail?* |
| [docs/sessions/](docs/sessions/) | *What was just worked on?* |
| [docs/plans/](docs/plans/) | *What is planned next?* |

Do not duplicate content across these files. When tempted, ask: "Which one of these is this *really* about?" and put it there.

---

**Last Updated**: 2026-07-20
**Maintained by**: The `maintaining-project-context` skill, with human review.
