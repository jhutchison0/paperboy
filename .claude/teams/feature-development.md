# Pipeline Feature Team

**Goal**: Build new pipeline capabilities — orchestration logic, CLI commands, config changes, new pipeline stages — with design review before implementation and quality gates after.

**When to use**: When adding features that touch `src/pipeline.py`, `main.py`, `src/config.py`, or `src/agent_runner.py`. Use this team for any change that affects how pipeline stages are sequenced, how results are passed between stages, or how the CLI exposes pipeline behavior.

## Composition

| Teammate | Role | Responsibility |
|----------|------|----------------|
| `proposer` | Analyst | Analyze feature requirements against current pipeline design, propose approach, write proposal to `docs/plans/` |
| `python-prototyper` | Implementer | Implement the approved approach in pipeline, CLI, and config files, alongside tests |
| `test-runner` | Validator | Run `pytest` after each implementation step, report pass/fail counts and coverage gaps |
| `code-reviewer` | Quality gate | Challenge proposals before implementation; review finished code against Pillar 4 (Pipeline Idempotency) and Pillar 5 (Extensibility) |

## File Ownership

| File | Owner |
|------|-------|
| `src/pipeline.py` | python-prototyper |
| `main.py` | python-prototyper |
| `src/config.py` | python-prototyper |
| `src/agent_runner.py` | python-prototyper |
| `config/paperboy.yaml` | python-prototyper (pipeline/config sections) |
| `tests/` | python-prototyper (writes), test-runner (runs) |
| `docs/plans/` | proposer (writes), code-reviewer (reads) |

If the feature also touches `src/sourcer.py` or `src/distiller.py`, assign those files to content-curator or distiller-dev respectively and coordinate ownership explicitly.

## Workflow

1. Lead assigns the feature with scope and acceptance criteria — include what stage(s) are affected and what the new behavior should be
2. `proposer` reads `src/pipeline.py`, `main.py`, `src/config.py`, and recent session docs to understand the current architecture; writes a proposal to `docs/plans/` that covers: approach, affected files, config changes, and how idempotency is preserved
3. `code-reviewer` challenges the proposal — focuses on: does same date + config still produce same output? does the new feature slot into the existing stage model without rewriting it? are config values in YAML, not hardcoded?
4. Lead decides to proceed, revise, or reject
5. `python-prototyper` implements the approved approach with tests in `tests/`; follows the sub-config pattern for any new config section (dataclass + YAML section + `load()` wiring)
6. `test-runner` runs `pytest` and confirms new tests pass and no existing tests regress
7. If tests fail, `python-prototyper` fixes and `test-runner` re-validates
8. `code-reviewer` reviews the implementation: checks idempotency is preserved, per-item errors don't stop the loop, public API signatures are clean, and new config keys have defaults
9. `python-prototyper` addresses any Critical or Warning findings
10. `test-runner` does a final validation pass
11. Lead reviews, commits, and updates `docs/sessions/` per session documentation policy

## Scaling Notes

- For trivial CLI additions (new flag on an existing command, minor config default change), `proposer` and `code-reviewer` may be omitted — python-prototyper + test-runner is sufficient.
- For new pipeline stages (new `src/` module wired into `DailyPipeline`), use the full 4-agent composition and consider adding `pipeline-sme` to validate mission alignment before implementation begins.
- For changes that touch both pipeline orchestration and a domain module (e.g., adding a new stage that calls distillation), add the relevant domain agent (distiller-dev or content-curator) with explicit file ownership.
- `test-runner` must never be removed. Pipeline idempotency is only verifiable through deterministic tests.
