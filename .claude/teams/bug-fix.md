# Bug Fix Team

**Goal**: Fix bugs with regression prevention — diagnose root cause, write a failing test, then fix the code. The regression test ensures the bug cannot silently reappear.

**When to use**: When fixing reported bugs, correcting logic errors, or addressing issues found during audits. Use this team for any defect where the root cause needs diagnosis before a fix is attempted.

## Composition

| Teammate | Role | Responsibility |
|----------|------|----------------|
| `python-prototyper` | Implementer | Diagnose the bug, write a regression test that fails, then implement the fix |
| `test-runner` | Validator | Confirm the regression test fails before the fix; confirm all tests pass after |

## Workflow

1. Lead describes the bug — observed behavior, expected behavior, and any reproduction steps or stack traces
2. `python-prototyper` reads the relevant source files to understand the logic and identify root cause; notes which pipeline stage is affected (source, select, distill, pipeline, config)
3. `python-prototyper` writes a regression test in `tests/` that captures the failure — the test should fail at this point, not pass
4. `test-runner` runs the new regression test in isolation to confirm it fails — this validates the test is correctly scoped to the bug
5. `python-prototyper` implements the fix in `src/`; follows the per-item error handling pattern (errors are caught and logged, not re-raised to stop the pipeline) unless the bug is in control flow rather than data processing
6. `test-runner` runs the full `pytest` suite to confirm the regression test now passes and no existing tests regress
7. Lead reviews the diff, commits with a descriptive message, and updates `docs/sessions/` if the bug surfaced a design issue worth noting

## Scaling Notes

- Add `code-reviewer` if the fix touches more than 3 files, changes a public API signature (function name, parameter types, return type), or involves external calls (ArXiv API, Anthropic API, file I/O).
- For config-only or YAML-only fixes (no logic change), the lead may handle alone without deploying this team.
- For bugs in source resilience (one feed failure breaking the pipeline), add `content-curator` to review the fix — source failure handling has domain-specific patterns that python-prototyper may not own.
- For bugs in briefing structure or distiller output, add `distiller-dev` to review the fix against prompt intent.
- `test-runner` must confirm the regression test fails *before* the fix is applied. Skipping this step defeats the purpose of regression testing — a test that was already passing is not a regression test.
