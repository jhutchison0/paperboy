# Session: Cross-Run Dedup and Upstream Doctrine Review

**Date**: 2026-04-04
**Branch**: main
**Tags**: #session #select #pipeline #config #infra #complete

**Documents**: [pillars.md](../design/pillars.md) — Pillar 4 (idempotency), Pillar 2 (resilience)
**References**: `.claude/upstream-update.md` — upstream doctrine from utils
**Follows**: [20260326_upstream_doctrine_update.md](20260326_upstream_doctrine_update.md)

---

## Summary

Two items: (1) implemented cross-run paper deduplication to fix a bug where the same paper was selected on consecutive days, and (2) reviewed the upstream decision science doctrine update, adopting just the decision-scientist agent.

## Bug: Duplicate Paper Selection

**Symptom**: Paper `arXiv:2604.02091v1` ("Optimizing RAG Rerankers...") was selected and distilled on both 2026-04-03 and 2026-04-04, producing near-identical briefings.

**Root cause**: The 7-day `days_lookback` window means a paper published on April 2 appears in both the April 3 and April 4 candidate pools. The pipeline had no memory of previous selections — each run was completely stateless.

**Existing dedup**: Within-run category dedup in `sourcer.py` (merges papers appearing in multiple ArXiv categories) worked correctly but only operates within a single run.

**Fix**: Added `SelectionHistory` class that persists selected paper IDs with timestamps to `.selection_history.json`. On each run, papers within the configurable cooldown window (default 30 days) are excluded from selection.

### Changes

| File | Change |
|------|--------|
| `src/models.py` | `normalize_paper_id()` — normalizes ArXiv URL/prefix/bare forms |
| `src/pipeline.py` | `SelectionHistory` class — load/save/record/get_excluded_ids |
| `src/selector.py` | `select_best()` accepts `exclude_ids`, filters before scoring |
| `src/config.py` | `dedup_cooldown_days` field (default 30) |
| `config/paperboy.yaml` | `dedup_cooldown_days: 30` |
| `main.py` | `--no-dedup` CLI flag |
| `tests/test_dedup.py` | 19 new tests |

### Design decisions

- **History lives in output dir** (`.selection_history.json` alongside briefings) — not in config or a database. Simple, portable, gitignored with the rest of output.
- **Normalization in models.py** — shared by both pipeline and selector, avoids circular imports.
- **Cooldown, not permanent block** — papers expire from the exclusion list after 30 days, so a paper can resurface in a different context later.
- **Graceful degradation** — corrupted/missing history file starts fresh rather than crashing.

## Upstream Doctrine: Decision Science Module

Reviewed the 2026-03-26 upstream update proposing a shared `decision_science` module, `decision-scientist` agent, and `decision-science` team template.

| Component | Decision | Rationale |
|-----------|----------|-----------|
| `decision_science` module | **SKIP** | 30 lines of linear scoring doesn't need a 4-module MAUT framework |
| `decision-scientist` agent | **ADAPT** | Advisory auditor for weights, fairness, bias — valuable alongside code-reviewer |
| `decision-science` team | **SKIP** | No dedicated team needed; agent joins existing teams when DS concerns arise |

The agent was adapted with paperboy-specific context (selector weights, keyword sub-scoring, thresholds) and added to the roster, scope matrix, CLAUDE.md.

## Session-Start Git Sync

Applied the 2026-03-31 upstream update: `git fetch && git pull` now runs as the first step in session-start health checks.

## Test Results

119 tests pass (100 existing + 19 new dedup tests).

## Next Steps

Active tasks carry forward:
- `[P3]` Agent backend temperature control (Pillar 4 — idempotency gap)
- `[P3]` Distiller graceful degradation on agent failure (Pillar 2)
- `[P3]` Batch scoring to 5 papers per invocation
- `[P3]` Update CONOP checklist wave statuses
