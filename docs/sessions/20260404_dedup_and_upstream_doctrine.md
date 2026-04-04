# Session: Cross-Run Dedup and Upstream Doctrine Review

**Date**: 2026-04-04
**Branch**: main
**Tags**: #session #select #pipeline #config #infra #complete #pillar-4 #pillar-2

**Documents**: [pillars.md](../design/pillars.md) — Pillar 4 (idempotency), Pillar 2 (resilience)
**References**: `.claude/upstream-update.md` — upstream doctrine from utils
**Follows**: [20260326_upstream_doctrine_update.md](20260326_upstream_doctrine_update.md)

---

## Summary

Three items: (1) implemented cross-run paper deduplication to fix a bug where the same paper was selected on consecutive days, (2) reviewed the upstream decision science doctrine update (skip module/team, adopt agent), and (3) applied the upstream session-start git sync update.

## Bug: Duplicate Paper Selection

**Symptom**: Paper `arXiv:2604.02091v1` ("Optimizing RAG Rerankers...") was selected and distilled on both 2026-04-03 and 2026-04-04, producing near-identical briefings.

**Root cause**: The 7-day `days_lookback` window means a paper published on April 2 appears in both the April 3 and April 4 candidate pools. The pipeline had no memory of previous selections — each run was completely stateless.

**Existing dedup**: Within-run category dedup in `sourcer.py` (merges papers appearing in multiple ArXiv categories) worked correctly but only operates within a single run.

**Fix**: Added `SelectionHistory` class that persists selected paper IDs with timestamps to `.selection_history.json`. On each run, papers within the configurable cooldown window (default 30 days) are excluded from selection.

**Cold-start fix**: Initial implementation had an empty history file on first run. Added `_seed_from_briefings()` that back-fills history from existing briefing YAML frontmatter, handling three format variants found in production briefings.

### Changes

| File | Change |
|------|--------|
| `src/models.py` | `normalize_paper_id()` — normalizes ArXiv URL/prefix/bare forms |
| `src/pipeline.py` | `SelectionHistory` class — load/save/record/seed/get_excluded_ids |
| `src/selector.py` | `select_best()` accepts `exclude_ids`, filters before scoring |
| `src/config.py` | `dedup_cooldown_days` field (default 30) |
| `config/paperboy.yaml` | `dedup_cooldown_days: 30` |
| `main.py` | `--no-dedup` CLI flag |
| `tests/test_dedup.py` | 30 tests (normalization, history, seeding, selector) |
| `tests/test_config_validation.py` | 2 tests (config loading, default) |
| `tests/test_cli_output.py` | 2 tests (--no-dedup flag, default dedup=True) |

### Design decisions

- **History lives in output dir** (`.selection_history.json` alongside briefings) — not in config or a database. Simple, portable, gitignored with the rest of output.
- **Normalization in models.py** — shared by both pipeline and selector, avoids circular imports.
- **Cooldown, not permanent block** — papers expire from the exclusion list after 30 days, so a paper can resurface in a different context later.
- **Graceful degradation** — corrupted/missing history file starts fresh rather than crashing.
- **Frontmatter date over mtime** — seeding prefers `briefing_date` > `date` > file mtime for deterministic timestamps (Pillar 4). Caught by PCI.
- **Single file parse** — `_parse_briefing_frontmatter()` reads each briefing once, not twice. Caught by PCI.

## Upstream Doctrine: Decision Science Module

Reviewed the 2026-03-26 upstream update proposing a shared `decision_science` module, `decision-scientist` agent, and `decision-science` team template.

| Component | Decision | Rationale |
|-----------|----------|-----------|
| `decision_science` module | **SKIP** | 30 lines of linear scoring doesn't need a 4-module MAUT framework |
| `decision-scientist` agent | **ADAPT** | Advisory auditor for weights, fairness, bias — valuable alongside code-reviewer |
| `decision-science` team | **SKIP** | No dedicated team needed; agent joins existing teams when DS concerns arise |

The agent was adapted with paperboy-specific context (selector weights, keyword sub-scoring, thresholds) and added to the roster (now 8 agents), scope matrix, and CLAUDE.md.

## Session-Start Git Sync

Applied the 2026-03-31 upstream update: `git fetch && git pull` now runs as the first step in session-start health checks.

## PCI Findings (resolved)

PCI caught two issues in the seeding implementation:
1. File mtime used instead of frontmatter date — mtime drifts if files are touched (Pillar 4 violation)
2. Each briefing file read and parsed twice during seeding — merged into single `_parse_briefing_frontmatter()`

Both resolved in commit `4e44f25`.

## Test Results

134 tests pass (100 existing + 30 dedup + 2 config + 2 CLI).

## Next Steps

Active tasks carry forward:
- `[P3]` Agent backend temperature control (Pillar 4 — idempotency gap)
- `[P3]` Distiller graceful degradation on agent failure (Pillar 2)
- `[P3]` Batch scoring to 5 papers per invocation
- `[P3]` Update CONOP checklist wave statuses
