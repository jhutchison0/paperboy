# Session: Config Rename and Repo Cleanup

**Date**: 2026-03-11
**Branch**: main
**Tags**: #session #config #refactor #complete #pillar-4 #pillar-5

**Documents**: [pillars.md](../design/pillars.md) — Pillar 4 (Idempotency), Pillar 5 (Extensibility)
**Follows**: [20260311_live_e2e_test.md](20260311_live_e2e_test.md)

---

## Summary

Renamed `config/default_config.yaml` to `config/paperboy.yaml` because "default" implied an override chain that does not exist. This is THE config, not a default. Moved `test_pipeline.py` from the repo root to `tests/test_pipeline.py` for a cleaner root directory. Updated all references across source code, agent docs, commands, skills, top-level docs, session docs, plans, and the CHANGELOG.

## Design Decision: Config Naming

The original name `default_config.yaml` implied a layered config system -- a default that could be overridden by `local_config.yaml`, environment-specific files, or user overrides. That pattern does not exist in paperboy and is not planned. There is one config file, it configures the pipeline, and its name should say that plainly.

Considered alternatives:

| Name | Verdict | Reason |
|------|---------|--------|
| `default_config.yaml` | REJECTED | Implies override chain that does not exist |
| `pipeline.yaml` | REJECTED | Too generic; personal preference against it |
| `paperboy.yaml` | CHOSEN | The product configures itself, like `.eslintrc` or `pyproject.toml` |

The chosen name follows the agent-eval pattern of descriptive config names (`config/{eval,tools,project}.yaml`). `project.yaml` stays as-is -- it handles project identity, phases, and dev environment reference. `paperboy.yaml` handles pipeline runtime: sources, scoring, distillation, agent runner settings.

**Pillar alignment**: Pillar 4 (Idempotency) benefits from a single, unambiguous config file. There is no confusion about which config was active for a given run. Pillar 5 (Extensibility) is neutral -- the rename has no architectural impact on pluggability.

## Design Decision: Root Cleanup

`test_pipeline.py` was the only test file in the repo root. All other tests live in `tests/`. The file was moved to `tests/test_pipeline.py` to match the project structure documented in `CLAUDE.md` and `config/project.yaml`.

`main.py` stays in the root for now. `python main.py run` is discoverable and follows standard Python convention. Moving it is a Phase 5 concern (see Future Work below).

## Files Changed

### Renames (staged)

| Old Path | New Path |
|----------|----------|
| `config/default_config.yaml` | `config/paperboy.yaml` |
| `test_pipeline.py` | `tests/test_pipeline.py` |

### Reference Updates (21 files)

**Source code**:
- `src/config.py` -- Default config path and docstring updated

**Top-level docs**:
- `CLAUDE.md` -- Project structure and config workflow sections
- `README.md` -- Quickstart, configuration section, project structure
- `CHANGELOG.md` -- Both v0.1.0 and v0.2.0 entries updated
- `.env.example` -- Config path comment

**Project config**:
- `config/project.yaml` -- `See also` comment and `test_integration` path
- `config/paperboy.yaml` -- (content unchanged, renamed)

**Agent docs**:
- `.claude/agents/README.md` -- File ownership table
- `.claude/agents/code-reviewer.md` -- Config reference
- `.claude/agents/content-curator.md` -- All config references (6 occurrences)
- `.claude/agents/distiller-dev.md` -- File ownership table
- `.claude/agents/pipeline-sme.md` -- Source of truth table
- `.claude/agents/python-prototyper.md` -- Config references (2 occurrences)

**Commands**:
- `.claude/commands/implement-source.md` -- Config checklist items
- `.claude/commands/pcc.md` -- Config path reference
- `.claude/commands/pci.md` -- Config path and file table
- `.claude/commands/session-start.md` -- Config file table

**Plans and session docs**:
- `docs/plans/20260310_agent_pipeline_conop.md` -- Config references (2 occurrences)
- `docs/sessions/20260310_agent_runner_implementation.md` -- Config path in files table
- `docs/sessions/20260310_identity_and_api_exploration.md` -- Config references
- `docs/sessions/20260311_live_e2e_test.md` -- Config path in bug table

## Test Results

94/94 passing after the rename. No test changes required -- tests use the config loader which resolves the path dynamically, and the integration test only moved directories without content changes.

## Future Work: CLI Entry Point Migration (Phase 5 CONOP)

**Current state**: `main.py` in repo root, invoked as `python main.py run`.

**Target state**: Proper Python packaging with `pyproject.toml` entry points. Users would run `paperboy run` after `pip install`.

**What this requires**:
1. Create `pyproject.toml` with `[project.scripts]` entry point: `paperboy = "src.cli:main"`
2. Rename `main.py` to `src/cli.py` (the click group and commands)
3. Add `__main__.py` to `src/` for `python -m paperboy` support
4. Update all documentation, CLAUDE.md, agent docs to reference new paths
5. Consider a `scripts/paperboy` bash wrapper for development (bypasses pip install)
6. Update test fixtures that import from `main`

**Why defer to Phase 5**:
- Current `main.py` in root works and is discoverable
- Proper packaging requires decisions about distribution (PyPI? GitHub releases?)
- Phase 5 (Distribution) is the natural home for this work
- Moving now adds complexity without user-facing benefit

**Trade-offs**:
- Pro: Cleaner root, proper Python packaging, `paperboy run` CLI
- Pro: Enables `pip install paperboy` distribution
- Con: More complex development setup (need `pip install -e .`)
- Con: All docs, agents, tests need path updates (large blast radius -- this session demonstrated the scope)

**Recommendation**: Implement as part of Phase 5 when distribution decisions are made. Tag as P5-PACKAGING in the roadmap.
