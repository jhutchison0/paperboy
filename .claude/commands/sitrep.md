# SITREP — Status Report

Generate a team-facing status report summarizing what was built, what was found, and what's next. Unlike `/task brief` (internal task inventory), a SITREP is a narrative outbrief for teammates — concrete details, delivered state, no internal planning jargon.

**Military origin**: SITREP — Situation Report. The field update you send up the chain so leadership knows where you stand without asking.

**User's scope filter**: $ARGUMENTS

## Sources to Read

Read ALL of these to build the report:

1. `config/project.yaml` — `project.current_phase`, `project.version`, `build_phases` status for each phase
2. `docs/tasks.md` — active, blocked, and recently completed items
3. Most recent file in `docs/sessions/` — last session details (sort by filename date, take the highest)
4. `git log --oneline -10` — recent commit messages
5. `git log --oneline main..HEAD` — commits not yet on main (if on a dev branch)

## Scope Filtering

If the user provided a scope argument, filter all sections to only include items related to that scope. Paperboy's domain scopes are:

| Scope | Covers |
|-------|--------|
| `sources` | ArXiv fetching, RSS/blog sourcing, SourceManager, sourcer.py |
| `selection` | Keyword scoring, Claude semantic scoring, hybrid ranking, selector.py |
| `distillation` | Briefing structure, Claude prompts, 8-section output, distiller.py |
| `pipeline` | DailyPipeline orchestration, stage handoffs, pipeline.py |
| `config` | YAML loading, validation, paperboy.yaml, project.yaml, config.py |
| `cli` | main.py CLI commands, flags, output messaging |
| `tts` | TTS interface stubs, future audio export, tts_interface.py |

When a scope is given, search the relevant source file(s) for concrete details — function signatures, config keys, thresholds — before writing the report.

If no scope argument, report on everything since the last session (or last merge to main).

## Filling in Concrete Details

A good SITREP has specifics, not summaries. Before writing each section:

- **Functions**: Find the actual function or class name and include it (e.g., `PaperSelector.score()`, `AgentRunner._invoke()`)
- **Config**: Pull actual values from `config/paperboy.yaml` — thresholds, weights, limits (e.g., `keyword_weight: 0.3`, `max_papers: 5`)
- **Test results**: Run `.venv/bin/pytest -q 2>&1 | tail -5` for current counts
- **Pipeline metrics**: From session docs — papers sourced, papers selected, briefing word count, scoring pass rate
- **Known issues**: Include the specific symptom and its scope, not just "there's a problem"

## Output Format

```
SITREP — [Date] — [Scope or "Full Project"]
============================================

PERIOD:       [Date range covered, e.g., "2026-03-10 to 2026-03-12" or "since last session"]
PHASE:        [current_phase from project.yaml, e.g., "Phase 2 — Configuration & Polish"]
VERSION:      [version from project.yaml]
BRANCH:       [current git branch]
MERGE STATUS: [e.g., "on main" or "3 commits ahead of main"]

COMPLETED:
  - [Capability with concrete details: function name, config key, what it does]
  - [Another item — include the specific file or module it lives in]

KEY FINDINGS:
  - [What was validated, discovered, or disproved — with numbers where available]
  - [e.g., "Live E2E test: 5 papers sourced, 2 selected, briefing 1,840 words"]

TEST STATUS:
  - [X passed, Y failed, Z errors — from pytest -q output]
  - [Note any collection errors and their cause]

KNOWN ISSUES:
  - [Issue name]: [specific symptom and affected module — e.g., "Distiller raises RuntimeError on agent failure instead of returning None (distiller.py:~L120)"]

BLOCKED:
  - [Item]: [what's blocking it, or "none"]

NEXT:
  - [Top priority active tasks from docs/tasks.md, with priority tag]

OPEN DECISIONS:
  - [Decisions that need input, if any — e.g., "Batch scoring: target batch_size=5, current=1, design not started"]
```

## Style Guidelines

- **Lead with what was delivered**, not what was attempted
- **Include function and config specifics** — teammates should be able to find and use what was built
- **Numbers over adjectives** — "48 tests passing, 0 failures" not "tests are in good shape"
- **Pipeline metrics anchor the report** — if a live run was done, lead KEY FINDINGS with sourced/selected/word-count numbers
- **Known issues get the same specificity as completed items** — include the module, line range if known, and the exact failure mode
- **Keep it to one screen** — if it scrolls, cut the least important items
- **No internal planning framework jargon** — teammates don't need to know about TCS/CONOP/OPORD levels; just tell them what was done and what's next
