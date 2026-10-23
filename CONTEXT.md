# CONTEXT.md — What Paperboy Is

A one-page narrative of paperboy's identity, mission, current state, and key constraints. Uses terms defined in [LANGUAGE.md](LANGUAGE.md). For machine-readable identity (version, phases, machines, paths), see [config/project.yaml](config/project.yaml).

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

This section names where each part of the current state lives and holds no snapshot, because a snapshot here reads as current after it stops being true. The `maintaining-the-common-operating-picture` skill says why.

- **Version and phase**: [config/project.yaml](config/project.yaml), `project.version` and `build_phases`. Identity; it changes only when someone edits it.
- **Campaign focus**: the `## Focus` section at the head of [docs/tasks.md](docs/tasks.md). Intent, not state.
- **Known unknowns**: [docs/gaps.md](docs/gaps.md), each with the collector that would close it and the decision it blocks.
- **Last session**: the newest file in [docs/sessions/](docs/sessions/) by name (names are date-first). A record, true as of its date.
- **The machine**: `.venv/bin/python -m src.machine`, against the `machines:` roster in `config/project.yaml`.
- **Which Claude backend a run uses**: resolved at run time from the `--backend` flag, then the machine roster's preference, then what the environment provides (an API key, the `claude` CLI, or neither); `python main.py run --help` and the README's "Claude Backend Options" table say how.
- **Source roster and selection tunables**: [config/paperboy.yaml](config/paperboy.yaml). Whether a feed is live is measured by a `python main.py source` run (gap G6), never read from this file.
- **Suite and branch**: measured by command at `/session-start`, never written down.

---

## Constraints

The hard rules. Violating these requires explicit user override per change.

**Pillars** (formally tracked in `config/project.yaml` and [docs/design/pillars.md](docs/design/pillars.md)):

1. **Content Quality First** — briefings optimized for two-voice podcast dialogue; structure, tone, and depth serve listener comprehension.
2. **Source Diversity & Resilience** — ArXiv + blog RSS with graceful degradation. If one source fails, the pipeline continues. Pluggable sources via `ContentSourcer` ABC.
3. **Relevance Through Hybrid Scoring** — two-phase keyword + Claude semantic scoring with configurable weights, thresholds, focus areas.
4. **Pipeline Idempotency** — same date + same config = same output, as intent. Date-stamped runs and a deterministic keyword stage by construction; the Claude stages are reproducible only as far as gap G4 measures, and distillation samples at `claude.temperature` on the API path.
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

**Upstream doctrine source**: `tacsop` (GitHub `jhutchison0/tacsop`, named `utils` until 2026-07-20) propagates doctrine updates via `.claude/upstream-update.md`. Paperboy reviews each entry and adopts/adapts/skips per artifact; each cycle's disposal is annotated in that file (annotated, never deleted) and recorded in the session doc of the day.

**Sister repo (pattern, not doctrine)**: `elephant-graveyard` (LED curtain digital twin) shares workspace patterns (agents, commands, skills, session docs) but is not a doctrine source. Paperboy was bootstrapped from elephant-graveyard's infrastructure; the pipeline code in `src/` was written fresh.

**Agent roster** (in `.claude/agents/`; `ls .claude/agents/` lists them):
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
4. [config/project.yaml](config/project.yaml) — machine-readable identity (version, phases, machines, paths).
5. [config/paperboy.yaml](config/paperboy.yaml) — pipeline tunables (sources, scoring weights, distiller settings).
6. [docs/design/pillars.md](docs/design/pillars.md) — the five design pillars in detail.
7. [.claude/README.md](.claude/README.md) — agent roster, scope matrix, team templates.
8. [docs/adr/](docs/adr/) — accepted architecture decisions; check before reopening any decision they cover.
9. [docs/sessions/](docs/sessions/) — the newest file by name for live context (names are date-first).
10. [docs/tasks.md](docs/tasks.md) — the `## Focus` section at its head: what comes next, in order.
11. [docs/gaps.md](docs/gaps.md) — what nobody can see yet, and the decision each gap blocks.
12. [.claude/skills/lake-conventions/HOME-STORAGE.md](.claude/skills/lake-conventions/HOME-STORAGE.md) — where bulk data goes if paperboy ever writes any (scope: personal, home storage, no address in git).

When navigating between these documents, walk the link graph rather than keyword-searching: [.claude/skills/traversing-the-knowledge-base/SKILL.md](.claude/skills/traversing-the-knowledge-base/SKILL.md) has the traversal recipes.

---

## Distinguishing This File from Adjacent Artifacts

| Artifact | What it answers |
|---|---|
| `CONTEXT.md` (this file) | *What is paperboy and what does it care about?* |
| [LANGUAGE.md](LANGUAGE.md) | *What do specific terms mean in this project?* |
| [config/project.yaml](config/project.yaml) | *What is the project's machine-readable identity: version, phases, machines, paths?* |
| [docs/tasks.md](docs/tasks.md) | *What comes next, and in what order?* |
| [docs/gaps.md](docs/gaps.md) | *What can nobody see yet, and what does that block?* |
| [config/paperboy.yaml](config/paperboy.yaml) | *What are the pipeline's tunable parameters?* |
| [CLAUDE.md](CLAUDE.md) | *What conventions and commands does the agent need at hand?* |
| [docs/design/pillars.md](docs/design/pillars.md) | *What are the five design pillars in detail?* |
| [docs/sessions/](docs/sessions/) | *What was just worked on?* |
| [docs/plans/](docs/plans/) | *What is planned next?* |

Do not duplicate content across these files. When tempted, ask: "Which one of these is this *really* about?" and put it there.

---

**Last Updated**: 2026-10-22
**Maintained by**: The `maintaining-project-context` skill, with human review.
