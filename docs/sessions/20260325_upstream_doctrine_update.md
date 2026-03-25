# Session: Upstream Doctrine Update — Proposer, Waves, Teams, Sitrep

**Date**: 2026-03-25
**Branch**: main
**Tags**: #session #config #infra #complete

**References**: [upstream-update.md](../../.claude/upstream-update.md) — Doctrine propagation from github/utils (deleted after processing)
**References**: [README.md](../../.claude/agents/README.md) — Agent roster and scope matrix
**Cites**: AgenticSciML paper (arxiv.org/html/2511.07262v2) — Inspiration for proposer agent's debate-before-implementation pattern

---

## Summary

Applied the first upstream doctrine update from `github/utils` (the shared workflow template repo). This establishes the propagation pattern: utils pushes `.claude/upstream-update.md` to downstream repos, and `/session-start` Step 3.6 surfaces it for review. Future updates will arrive the same way.

The update brought four major changes: a proposer agent, wave/phase terminology, team templates, and a /sitrep command. All were adapted from generic Level 0 templates to paperboy's pipeline domain.

## Changes Made

### New Agent: Proposer
- `.claude/agents/proposer.md` — Explores problem space, proposes bold approaches, writes proposals to `docs/`. Debates with code-reviewer before implementation begins.
- Adapted for paperboy: references 5 design pillars, pipeline flow, all architecture files. Adds "Pillar Impact" section to proposal format (paperboy enhancement over upstream).
- Inspired by AgenticSciML multi-agent framework — structured debate produces better solutions than jumping straight to code.

### Terminology Update: Waves vs Phases
- `.claude/commands/task.md` — "Phase" within CONOP/OPORD contexts replaced with "wave." Phase is now reserved for strategic roadmap milestones (`project.yaml` build_phases). Waves are tactical parallel execution units where agent teams deploy.
- TCS established as the universal task detail standard — every task within a CONOP or OPORD uses TCS-level specification regardless of document type.

### Team Templates (5 files)
- `.claude/teams/source-development.md` — proposer + content-curator + test-runner + code-reviewer
- `.claude/teams/pipeline-feature.md` — proposer + python-prototyper + test-runner + code-reviewer
- `.claude/teams/briefing-quality.md` — proposer + distiller-dev + test-runner + pipeline-sme
- `.claude/teams/bug-fix.md` — python-prototyper + test-runner (regression-first)
- `.claude/teams/code-review.md` — code-reviewer + test-runner (audit only)

All three domain-specific templates include the propose-then-challenge workflow. Bug-fix and code-review are lightweight 2-agent compositions adapted from utils.

### New Command: /sitrep
- `.claude/commands/sitrep.md` — Team-facing narrative status report with concrete details (function names, config values, test counts). Supports scope filtering (e.g., `/sitrep sources`, `/sitrep distiller`). Adapted from utils with paperboy-specific domain scopes and project.yaml key references.

### Infrastructure Updates
- `.claude/commands/session-start.md` — Added Step 3.6: check for `.claude/upstream-update.md` and surface to user. This is the doctrine propagation mechanism — utils can now push workflow updates to downstream repos.
- `CLAUDE.md` — Added proposer to agent roster (now 7 agents), updated team table (now 5 templates), added /sitrep to workflow commands, added wave terminology to planning escalation.
- `.claude/agents/README.md` — Added proposer to roster, added scope matrix showing read/write permissions per agent per path, updated team template references.

## Process

Deployed a 4-agent parallel implementation team (task-updater, proposer-creator, team-creator, sitrep-creator), followed by a code-reviewer audit pass. The audit found 0 critical issues and 5 warnings, all fixed before commit:
- W1: Stale "6 agents" count in README.md (fixed to 7)
- W2: Missing proposer agent-memory directory (created)
- W3: CLAUDE.md agent table ordering inconsistent with README.md (reordered)
- W4: Bug-fix and code-review teams missing from task.md recommendations (added)
- W5: Sitrep PERIOD field format ambiguity (minor, noted)

## Key Decisions

- **5 team templates instead of 3** — Utils has 3 generic templates. Paperboy splits into 3 domain-specific (source, pipeline, briefing) + 2 generic (bug-fix, code-review). The domain templates include proposer in the workflow; the generic ones stay lean.
- **Proposer gets Pillar Impact section** — Enhancement over upstream. Every proposal in paperboy must trace back to the 5 design pillars.
- **Upstream-update.md deleted after processing** — Per the file's own instructions. Future updates arrive the same way and get surfaced at session start.

## Upstream Doctrine Propagation

Going forward, `github/utils` is the upstream source of truth for Level 0 workflow infrastructure. When changes are made there:
1. Utils pushes `.claude/upstream-update.md` to downstream repos
2. `/session-start` Step 3.6 detects the file and surfaces it
3. User reviews and decides what to adopt, adapting for project domain
4. File is deleted after processing

This is a "so you know" mechanism — downstream repos adapt as they see fit, not a forced sync.

## Next Steps

- [ ] Agent backend temperature control (P3, Pillar 4)
- [ ] Distiller graceful degradation on agent failure (P3, Pillar 2)
- [ ] Batch scoring to 5 papers per invocation (P3)
- [ ] Update CONOP checklist phases with completion status (P3)
