# LANGUAGE.md — Project Glossary

A glossary of project-specific domain terms for paperboy. One-line definitions, no synonyms.

This file follows the pattern from Matt Pocock's `grill-with-docs` skill (`CONTEXT-FORMAT.md`), adapted for paperboy's domains: the research-pipeline data model, the dual-backend Claude integration, the agent framework, the military-inspired escalation ladder, and the doctrine relationship with upstream `utils`.

**Rules** (verbatim from the source pattern):
- Keep definitions tight. One sentence max.
- Define what it IS, not what it does.
- Each term gets a bold name, one-line definition, and `_Avoid:_` list of synonyms (when ambiguity exists).
- This is a glossary and nothing else. Not a spec, not a scratch pad.

When a term is missing or contested, invoke the `maintaining-ubiquitous-language` skill.

---

## Pipeline Data Model

**Paper**: A research paper sourced from ArXiv (`src/models.py:Paper`) with title, authors, abstract, categories, and ID. _Avoid:_ article (reserve for RSS items), document.

**Article**: A blog post sourced from an RSS feed (`src/models.py:Article`). Structurally similar to Paper but with feed metadata instead of ArXiv metadata. _Avoid:_ post, item.

**ScoredPaper**: A Paper or Article wrapped with selector output — keyword score, Claude score, hybrid score, reasoning. The unit selection operates on. _Avoid:_ candidate (ambiguous: pre- or post-score?).

**Briefing**: The final distilled markdown document for one paper, optimized for NotebookLM two-voice podcast generation, structured in the canonical eight sections (see **Eight-Section Structure**). _Avoid:_ summary, digest, report.

**Eight-Section Structure**: The fixed briefing layout produced by `BriefingDistiller`: (1) Opening Hook, (2) Why Should You Care, (3) The Problem, (4) Core Idea, (5) How It Works, (6) Results, (7) Limitations & Open Questions, (8) Key Takeaways. Each section steers a specific phase of the two-voice podcast dialogue. _Avoid:_ briefing template (the structure is enforced by the distillation prompt, not a template engine).

**BriefingDocument**: The in-memory dataclass (`src/models.py:BriefingDocument`) carrying the briefing's structured content before serialization. _Avoid:_ briefing object — say BriefingDocument when you mean the dataclass.

**PipelineResult**: The outcome record (`src/pipeline.py`) of one `DailyPipeline.run()` carrying status (`success` / `partial` / `error`), the briefing path if produced, and the failure reason if not. _Avoid:_ run record.

---

## Pipeline Stages

**Source Stage**: The fetch phase — `SourceManager` queries every configured `ContentSourcer` and returns deduplicated Papers and Articles. _Avoid:_ ingest.

**Selection Stage**: The score-and-rank phase — `PaperSelector` applies keyword scoring then Claude semantic scoring, then ranks against the configured threshold. _Avoid:_ filter (selection is rank-based, not predicate-based).

**Distillation Stage**: The briefing-production phase — `BriefingDistiller` prompts Claude with the chosen paper and produces the eight-section markdown. _Avoid:_ summarization (the briefing is more than a summary).

**Hybrid Scoring**: The two-phase selection design — cheap keyword scoring filters the candidate set, then Claude semantic scoring ranks the shortlist. Configured by selector weights in `paperboy.yaml`. _Avoid:_ two-stage scoring (overloaded), ML scoring (not ML).

---

## Sources

**ContentSourcer**: The abstract base (`src/sourcer.py`) every concrete source implements: `fetch(days_back) -> list[Paper|Article]` and `health_check() -> bool`. _Avoid:_ provider, adapter.

**ArxivSourcer**: The concrete sourcer for ArXiv categories (e.g., `cs.AI`, `cs.LG`, `cs.CL`). Uses the `arxiv` library.

**BlogSourcer**: The concrete sourcer for RSS feeds. Currently configured for Anthropic Research, Google AI, Lilian Weng, The Gradient, Distill.pub, and Hugging Face Daily Papers.

**SourceManager**: The orchestrator that runs every configured sourcer in parallel, normalizes outputs, and deduplicates against `SelectionHistory`. _Avoid:_ source registry.

**SelectionHistory**: The cross-run deduplication record (`output/.selection_history.json`) tracking paper IDs selected in the last 30 days. Prevents the same paper being briefed twice. _Avoid:_ dedup cache.

---

## Backends

**Backend**: The Claude integration mode for selection and distillation. Three values: `api` (Anthropic SDK), `agent` (Claude Code CLI subprocess), `keyword-only` (no Claude at all). _Avoid:_ provider.

**API Backend**: Uses the `anthropic` SDK with `ANTHROPIC_API_KEY` from `.env`. Charges per token.

**Agent Backend**: Subprocess-invokes `claude -p ...` to use a Claude Max subscription instead of API billing. Implemented in `src/agent_runner.py:AgentRunner`. _Avoid:_ CLI backend (true, but say agent backend for symmetry with the config value).

**Auto Mode**: The default `--backend` value — try API, fall back to Agent, fall back to keyword-only. _Avoid:_ fallback mode.

**Keyword-Only Mode**: Selection runs keyword scoring only; distillation is skipped. The pipeline still reports `success` — the briefing is intentionally absent. _Avoid:_ dry-run (means something different).

---

## Pipeline Result Semantics

**Success**: A `PipelineResult` status indicating either a briefing was produced, or keyword-only mode ran as configured. CLI exits 0. _Avoid:_ ok, done.

**Partial**: A `PipelineResult` status indicating selection succeeded but distillation produced no briefing (Claude backend was expected). The selection is NOT recorded in `SelectionHistory` so the paper remains available for retry. CLI exits 2. _Avoid:_ degraded, soft-fail.

**Error**: A `PipelineResult` status indicating an exception was raised. CLI exits 1.

**Last Error**: The propagated failure reason string carried by `AgentRunner.last_error` → `BriefingDistiller.last_error` → `PipelineResult.error`. Surfaces specific causes (timeout, validation, subprocess) instead of generic messages.

---

## Agent Framework

**Agent**: A specialized worker with isolated context, a defined scope, and a model assignment, invoked via the `Agent` tool. Lives in `.claude/agents/<name>.md`. _Avoid:_ subagent (use only when contrasting with the lead in a multi-agent flow).

**Skill**: A self-loading capability defined in `.claude/skills/<name>/SKILL.md` (directory form, mandatory per [ADR-0001](docs/adr/0001-directory-form-mandatory-for-new-skills.md)), invoked by name or auto-triggered when the description matches. _Avoid:_ procedure, playbook.

**Command**: A user-invoked workflow defined in `.claude/commands/<name>.md`, executed only when the user types `/<name>`. Distinct from a skill in that timing is always user-controlled. _Avoid:_ slash command (redundant).

**Team**: A pre-composed agent roster for a class of work, defined in `.claude/teams/<name>.md`. Templates only; teams are instantiated at deployment time. _Avoid:_ squad.

**Roster**: The set of agents currently defined in `.claude/agents/`. Paperboy maintains eight: `pipeline-sme`, `proposer`, `content-curator`, `distiller-dev`, `python-prototyper`, `test-runner`, `code-reviewer`, `decision-scientist`.

---

## Escalation Ladder

**Task**: One person, one session, one clear action. The smallest unit in `docs/tasks.md`. Promote upward when the work exceeds one session or requires multi-step coordination.

**TCS**: Task, Condition, Standard — a structured task spec with pass/fail criteria. The universal task-detail unit inside all plan types (CONOP, OPORD). _Avoid:_ ticket, story.

**CONOP**: Concept of Operations — a multi-wave plan covering design decisions and parallel tracks. Lives in `docs/plans/`. _Avoid:_ design doc.

**OPORD**: Operations Order — the sequential execution form of a decided strategy, organized in waves. Lives in `docs/plans/`. _Avoid:_ runbook.

**Wave**: A tactical parallel-execution unit inside a CONOP or OPORD where agent teams deploy. Bounded by a shared exit criterion. _Avoid:_ sprint, batch.

**Phase**: A strategic roadmap milestone tracked in `config/project.yaml` under `build_phases`. Strictly distinct from wave. Paperboy has six phases; Phase 2 (Configuration & Polish) is current. _Avoid:_ stage, milestone.

**Pillar**: A foundational design principle. Paperboy has five: Content Quality First, Source Diversity & Resilience, Relevance Through Hybrid Scoring, Pipeline Idempotency, Extensibility by Design. Listed in `config/project.yaml` and `docs/design/pillars.md`. _Avoid:_ tenet, principle (use pillar when referencing the formal list).

---

## Governance & Doctrine Relationship

**Upstream**: The `utils` repository (`~/projects/github/utils`) that sources doctrine — agent definitions, skills, commands, command templates, and conventions — for paperboy and other downstream consumers.

**Doctrine**: A framework-level convention or pattern maintained in `utils` and intended for adoption across downstream consumer repos. Paperboy is a downstream; it consumes doctrine but does not propagate.

**Upstream Update**: A pending doctrine notification surfaced as `.claude/upstream-update.md` at session start. Reviewed and selectively adopted per artifact.

**Adoption Mode**: The disposition for one upstream artifact in one cycle: `ADOPT` (verbatim), `ADAPT` (modify for paperboy domain), `SKIP` (not applicable), or `CUSTOMIZE` (template + paperboy-specific content). Recorded in the upstream-update entry on disposal.

---

## Workflow Artifacts

**Session**: A bounded development working period, ideally a single Claude Code conversation, framed by `/session-start` and `/session-end`.

**Session Doc**: A dated record of one session in `docs/sessions/YYYYMMDD_<subject>.md`. Carries knowledge-graph edges to design docs, plans, and prior sessions. Format spec in [docs/session-doc-format.md](docs/session-doc-format.md).

**Review**: An agent-authored analysis output in `docs/reviews/YYYYMMDD_<subject>.md`. Used for code-reviewer, decision-scientist, and proposer outputs.

**LANGUAGE.md**: This file. The project's domain glossary. Maintained via the `maintaining-ubiquitous-language` skill.

**CONTEXT.md**: Paperboy's narrative identity, mission, current state, and key constraints. Companion to `LANGUAGE.md` and `config/project.yaml`. Maintained via the `maintaining-project-context` skill.

**ADR**: Architecture Decision Record — a numbered file in `docs/adr/NNNN-<slug>.md` capturing one decision that satisfies the triple filter: hard to reverse AND surprising without context AND result of a real trade-off. Maintained via the `recording-architecture-decisions` skill.

**Triple Filter**: The gate for whether a decision warrants an ADR. All three required: hard to reverse, surprising without context, real trade-off. Source: Matt Pocock's ADR format.

---

## Vocabulary Crosswalk (Military ↔ Civilian)

Used when externally-shared content (briefings, public docs) should not carry internal military framing. Keep military terms in this repo's internal docs; substitute civilian terms when the artifact crosses to an external audience.

| Internal (military) | External (civilian) |
|---|---|
| PCC | pre-commit-check |
| PCI | pre-merge-inspection |
| SITREP | status-report |
| OPORD | operations-order |
| CONOP | concept-of-operations |
| TCS | task-condition-standard |
| wave | execution-phase |
| backbrief | progress-summary |

The crosswalk is intentionally one-way: external content adopts civilian, internal content stays military. Do not rename internal files.

---

## Anti-Glossary (Terms We Deliberately Don't Use)

**"Module"** as a unit of organization: ambiguous (Python module? Pipeline stage? Component?). Use the specific term: `pipeline stage`, `package`, `file`, `function`, or `class`.

**"Component"**: not used in paperboy. If imported from external prose, translate to `agent`, `skill`, `sourcer`, or `pipeline stage` per context.

**"Plan"** unqualified: prefer `TCS`, `CONOP`, or `OPORD` — they signal scope. Reserve unqualified "plan" only for genuinely informal sketches.

**"Arcade"** / **"bike"** / **"fitness"** as themes: paperboy's name is a nod to the 1985 arcade game and the user's exercise-bike listening habit, but the codebase is a research-paper pipeline. Don't theme features or docs around the joke.

**"Stage"** in CONOP/OPORD contexts: ambiguous between phase and wave. Use one of those. (Pipeline stage is unambiguous because the pipeline has named stages.)

---

## Maintenance

Update LANGUAGE.md when:
- A new domain term emerges in conversation that risks being defined two ways.
- A pipeline-stage term is renamed or deprecated.
- A new source, scorer, or backend is added.
- An upstream doctrine cycle introduces vocabulary worth adopting.

Do not add a term just because it appeared once. The bar is recurrence + ambiguity.

When in doubt, invoke the `maintaining-ubiquitous-language` skill.

---

**Last Updated**: 2026-05-22
**Maintained by**: The `maintaining-ubiquitous-language` skill, with human review.
