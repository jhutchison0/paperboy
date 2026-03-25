# Code Review Team

**Goal**: Audit code quality and test health without modifying production code — purely investigative. Produces a findings report the lead can triage.

**When to use**: Pre-merge review, periodic quality audits, post-incident review, or evaluating code before a planned refactor. Use this team when you need an objective assessment of the current state before deciding what to change.

## Composition

| Teammate | Role | Responsibility |
|----------|------|----------------|
| `code-reviewer` | Reviewer | Read all target files, review against the 5 design pillars and the domain checklist below, write a findings report |
| `test-runner` | Validator | Run the full `pytest` suite, report total pass/fail counts, failing test names, and obvious coverage gaps |

## Workflow

1. Lead identifies the scope — a list of files, a pipeline stage, a recent set of commits, or the full `src/` tree
2. `code-reviewer` runs `git diff` (if reviewing recent changes) or reads the target files directly; applies the review checklist below
3. `test-runner` runs `pytest` across the full suite and reports: total pass/fail counts, names of any failing tests, and which source files have no corresponding test coverage
4. `code-reviewer` compiles a findings report organized by priority: Critical, Warning, Suggestion; includes specific file and line references for each finding
5. Lead triages the findings — decides which to fix now, defer, or accept as-is; escalates to the appropriate team if action is required

## Review Checklist

`code-reviewer` applies these domain-specific checks in addition to general code quality:

**Source Resilience (Pillar 2)**
- Does each source's `fetch()` catch per-item exceptions and continue rather than propagating?
- Is `health_check()` implemented and returning a meaningful result?
- If one feed or ArXiv category fails, does SourceManager continue with the rest?

**Scoring Integrity (Pillar 3)**
- Are keyword weights and scoring thresholds in `config/paperboy.yaml`, not hardcoded?
- Does the two-phase hybrid scoring (keyword filter → Claude semantic) degrade gracefully if Claude is unavailable?

**Briefing Structure (Pillar 1)**
- Do prompt templates reference the 8-section structure explicitly?
- Is the 3Blue1Brown style guidance (intuition first, analogies over equations) present in distillation prompts?
- Is output optimized for listening, not reading?

**Pipeline Idempotency (Pillar 4)**
- Does same date + same config produce the same output?
- Are there any sources of randomness not controlled by config?

**Extensibility (Pillar 5)**
- Do new sources extend ContentSourcer ABC rather than implementing ad-hoc fetch logic?
- Are new pipeline stages wired through `DailyPipeline` rather than called directly from `main.py`?
- Is config loaded from YAML with typed dataclasses, not read as raw dicts in business logic?

## Scaling Notes

- This is the smallest team. Keep it lean — the task is investigative, not implementation-heavy.
- Neither agent writes production code. If the review reveals issues that need fixing, escalate to the appropriate team: `bug-fix` for defects, `pipeline-feature` for structural improvements, `source-development` for source resilience gaps, `briefing-quality` for distillation issues.
- `code-reviewer` is read-only by design. If it identifies a Critical finding, it reports and stops — it does not attempt to fix.
- For pre-merge reviews on a specific set of changes, scope `code-reviewer` to the changed files only (`git diff main...HEAD`). For periodic audits, scope it to the full `src/` tree.
- For post-incident review (pipeline produced wrong output, missed papers), add `pipeline-sme` to assess mission impact alongside `code-reviewer`'s technical findings.
