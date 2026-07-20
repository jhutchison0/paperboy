---
name: shift-left-testing
description: Multi-tier testing strategy with vertical-slicing (tracer-bullet) TDD, mocks, fixtures, simulation, property-based invariants, numeric tolerances, legacy characterization, script/CLI testing, CI integration, and explicit anti-patterns. Use when setting up test infrastructure, designing test strategy, implementing mocks, or driving feature work via test-first one-cycle-at-a-time TDD.
version: "2.1.0"
---

# Shift-Left Testing

Move testing earlier in the development cycle: test components before integration, test with mocks before hardware, test logic before dependencies exist. This SKILL.md is the entry point; deep procedural content lives in sidecar files loaded on demand.

**Philosophy**: *"Never skip tests because dependencies aren't ready. Mock what you don't have, test what you build, validate continuously."*

## When to Use

- Setting up test infrastructure for a new project or component
- Designing the test strategy for a feature before writing code
- Implementing mocks for external dependencies
- Driving feature work via test-first TDD (the vertical-slicing rhythm)
- Reviewing test coverage, quality, or detecting anti-patterns
- Testing numeric, stochastic, or invariant-bearing code (scorers, pipelines, graph metrics)
- Wrapping legacy code or scripts in tests before changing them

## Core Principles

Four rules that govern everything else in this skill:

1. **Test independence.** Every test runs in isolation. No shared mutable state between tests, no execution-order dependencies.
2. **Mock external dependencies.** Never let tests depend on APIs, databases, hardware, or other services you don't fully control.
3. **Test early, test often.** Write tests before or alongside code, never after. Vertical slicing (one test → one implementation → repeat) is the rhythm; see `VERTICAL-SLICING.md`.
4. **Fail fast, fail clear.** Tests should fail quickly with messages that name what's wrong, not just that something is wrong.

## Quick Reference

### Test Pyramid

```
         /\
        /  \   E2E / External (few, slow, complete system)
       /____\
      /      \
     / System  \  (few, slow, end-to-end)
    /__________\
   /            \
  /  Integration  \  (medium quantity, medium speed)
 /__________________\
/                    \
/    Unit Tests        \  (many, fast, isolated)
/______________________\
```

### Test Tiers

| Tier | Speed | Scope | Dependencies | Share of total |
|---|---|---|---|---|
| Unit | <1s | Single component | Mocked | 60–70% |
| Integration | 1–10s | Component interaction | Some real, some mocked | 20–30% |
| System | 10–60s | End-to-end | Real or simulated | 5–10% |
| External | >60s | With real external systems | Real APIs/hardware | Optional |

### Test Directory Layout

```
tests/
├── fixtures/           # Shared test data, mock objects
├── golden/             # Golden files for snapshot comparisons (see REGRESSION.md)
├── unit/               # Fast, isolated component tests
├── integration/        # Multi-component interaction tests
├── simulation/         # Digital twin / simulated environment tests
├── scripts/            # Script and CLI tests (see SCRIPTS.md)
└── external/           # Real external system tests (optional)
```

### Naming Conventions

- Test files: `test_*.py` or `*_test.py`
- Test functions: `test_*`
- Test classes: `Test*`

Anything else won't be auto-discovered by pytest.

## Sidecar Files

Loaded on demand when this SKILL.md cites them. Read only the ones relevant to the task at hand.

- [TIERS.md](TIERS.md) — test pyramid expanded, tier strategy, root-level vs component-level test layouts, decision rule for which to use.
- [PATTERNS.md](PATTERNS.md) — unit, integration, and simulation testing patterns with worked examples.
- [MOCKS.md](MOCKS.md) — three mock patterns: simple, configurable, realistic-with-behavior.
- [FIXTURES.md](FIXTURES.md) — shared fixtures, conftest patterns, test data management (YAML, Faker, generated).
- [VERTICAL-SLICING.md](VERTICAL-SLICING.md) — tracer-bullet TDD discipline: rules, pre-code planning checklist, core principle. Adapted from Pocock.
- [PROPERTY-BASED.md](PROPERTY-BASED.md) — invariant testing with Hypothesis: strategies, monotonicity and round-trip properties, oracle tests, CI settings. Read for scorers, normalizers, parsers, and graph transforms.
- [NUMERIC.md](NUMERIC.md) — float comparison and tolerance selection, numpy and pandas assertions, injectable randomness, testing stochastic code. Read whenever a test touches computed numbers.
- [REGRESSION.md](REGRESSION.md) — characterization tests for legacy code and the golden-file workflow (normalization, bless discipline, churn control). Read when the audit hook fires on untested code.
- [SCRIPTS.md](SCRIPTS.md) — testing CLIs and filesystem scripts: thin main, tmp_path repo factories, dry-run contracts, the subprocess tier, and widening the enforcement perimeter to scripts/.
- [ENFORCEMENT.md](ENFORCEMENT.md) — enforcement gradient (probabilistic → deterministic), the PostToolUse audit hook, why we don't hard-block, when to escalate.
- [CI.md](CI.md) — GitHub Actions example, coverage thresholds, marker-based test selection.
- [ANTIPATTERNS.md](ANTIPATTERNS.md) — four anti-patterns to avoid, examples by domain (web API, data pipeline, ML), and the pre-commit testing checklist.

## References

- Martin Fowler, ["The Practical Test Pyramid"](https://martinfowler.com/articles/practical-test-pyramid.html)
- Kent Beck, *Test-Driven Development by Example* — foundational TDD pattern
- Matt Pocock, [`mattpocock/skills/skills/engineering/tdd/SKILL.md`](https://github.com/mattpocock/skills) — vertical slicing rules adapted into VERTICAL-SLICING.md
- Michael Feathers, *Working Effectively with Legacy Code* (2004): the characterization discipline in REGRESSION.md
- [Hypothesis documentation](https://hypothesis.readthedocs.io/): property-based testing library used in PROPERTY-BASED.md
- [pytest documentation](https://docs.pytest.org/)
- [numpy.testing](https://numpy.org/doc/stable/reference/routines.testing.html) and [pandas.testing](https://pandas.pydata.org/docs/reference/testing.html): assertion helpers used in NUMERIC.md
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html) — Python's built-in mocking
- [pytest-cov](https://pytest-cov.readthedocs.io/) — coverage plugin

---

**Maintained by**: Shift-Left Testing Skill
**Version**: 2.1.0 adds four sidecars: PROPERTY-BASED (Hypothesis invariants), NUMERIC (tolerances and determinism), REGRESSION (characterization and golden files), SCRIPTS (CLI testing and perimeter widening). New sidecars follow writing-simple-and-direct (2026-07-17).
**Prior**: 2.0.0, restructured to directory form with sidecar progressive disclosure, vertical-slicing discipline added, ENFORCEMENT sidecar describes deterministic hooks (2026-05-19)
**Replaces**: prior single-file at `.claude/skills/shift-left-testing.md` (deleted in the same commit).
