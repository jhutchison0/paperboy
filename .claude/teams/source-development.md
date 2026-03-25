# Source Development Team

**Goal**: Integrate new content sources into the pipeline — ArXiv categories, RSS blog feeds, or new API-backed source types — with resilience and extensibility gates at each step.

**When to use**: When adding new content sources, whether a trivial config addition (new RSS URL) or a full new ContentSourcer implementation. Scale the team to match the complexity (see Scaling Notes).

## Composition

| Teammate | Role | Responsibility |
|----------|------|----------------|
| `proposer` | Analyst | Survey the source landscape, assess fit against existing coverage, write integration proposal to `docs/plans/` |
| `content-curator` | Implementer | Implement the source (extend ContentSourcer ABC in `src/sourcer.py`), update `config/paperboy.yaml` with feeds/categories |
| `test-runner` | Validator | Run `pytest` after each implementation step, report pass/fail counts and coverage gaps |
| `code-reviewer` | Quality gate | Challenge proposals before implementation; review finished code against Pillar 2 (Source Diversity & Resilience) and Pillar 5 (Extensibility) |

## File Ownership

| File | Owner |
|------|-------|
| `src/sourcer.py` | content-curator |
| `src/models.py` | content-curator (if model changes needed) |
| `config/paperboy.yaml` | content-curator |
| `tests/` | content-curator (writes), test-runner (runs) |
| `docs/plans/` | proposer (writes), code-reviewer (reads) |

No file may have two owners. If a source addition requires changes to `src/pipeline.py` or `src/config.py`, transfer those files to python-prototyper and keep content-curator on sourcer + config.

## Workflow

1. Lead assigns the source addition with scope: what source, why it fits, any constraints
2. `proposer` reads `src/sourcer.py`, `config/paperboy.yaml`, and existing source tests to understand current coverage; writes a proposal to `docs/plans/` that includes: source name, data format, fetch strategy, failure mode, and how it extends ContentSourcer ABC
3. `code-reviewer` challenges the proposal — focuses on: does the failure mode degrade gracefully? does the fetch contract match the ABC? does this overlap with existing sources?
4. Lead decides to proceed, revise, or reject
5. `content-curator` implements: extends ContentSourcer ABC in `src/sourcer.py`, registers the source in SourceManager, adds feed URLs or ArXiv categories to `config/paperboy.yaml`, writes tests in `tests/`
6. `test-runner` runs `pytest` and confirms new tests pass and no existing tests regress
7. If tests fail, `content-curator` fixes and `test-runner` re-validates
8. `code-reviewer` reviews the implementation: checks `health_check()` is implemented, errors are caught per-item and do not stop the loop, config is YAML-driven (no hardcoded URLs), and the ABC contract is satisfied
9. `content-curator` addresses any Critical or Warning findings
10. `test-runner` does a final validation pass
11. Lead reviews, commits, and updates `docs/sessions/` per session documentation policy

## Scaling Notes

- For simple additions (new RSS feed URL, new ArXiv category ID in `paperboy.yaml`), `proposer` and `code-reviewer` may be omitted — content-curator + test-runner is sufficient.
- For a new ContentSourcer subclass (new API, new data format), use the full 4-agent composition — the propose-then-challenge cycle catches interface mismatches before implementation begins.
- `test-runner` must never be removed. Source resilience is only verifiable through tests.
- The key review criteria: does one source's failure prevent others from running? If yes, it is a Critical finding.
