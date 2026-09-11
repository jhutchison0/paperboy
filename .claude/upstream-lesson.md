# Upstream Lessons

**Direction**: paperboy → `tacsop` hub (the mirror of `.claude/upstream-update.md`: append mode, never gitignored, opposite flow). Per hub CONOP WHETSTONE D10, fleet-scope lessons recorded in session docs are also appended here; the hub harvests this file on a machine visit or consolidation session, and a harvested lesson enters the hub loop at OBSERVED with provenance naming this repo and the session doc.

**Schema** (hub D9): `LESSON (<status>): <claim> | evidence: <path or command> | scope: <repo|fleet> | owner: <artifact path or PARKED(n)> | verdict: <ADD|UPDATE|SUPERSEDE|NOOP>`

---

## 2026-09-10 — session: docs/sessions/20260910_doctrine_catchup_five_entries.md

LESSON (OBSERVED): The machines: roster works as a config dimension for runtime behavior, not just identity: an optional `machines.<host>.backend` (api | agent) key, honored by auto-mode backend resolution ahead of the detection chain, makes at-work-API / at-home-subscription an explicit committed intent instead of an accident of which box lacks an .env key. Advisory (unavailable preference falls through with a logged warning); explicit flag outranks roster. Candidate extension to the hub's machine.py template — the field is marked as a paperboy extension in-code. | evidence: paperboy src/machine.py + src/pipeline.py _resolve_backend + tests/test_pipeline_backend.py (commit 808eaea) | scope: fleet | owner: paperboy src/machine.py (hub template candidate) | verdict: ADD

LESSON (OBSERVED): The moment machines: carries a behavior-affecting key, any test that exercises the behavior's auto path is hermetic only if it pins resolve_machine (autouse fixture returning a no-preference Machine); otherwise the suite passes or fails depending on which box runs it — the same trap class as a developer's real .env leaking into tests (paperboy USER_CONTEXT, 2026-07-20). Ship the pin in the same commit as the first roster-read. | evidence: paperboy tests/test_pipeline_backend.py no_machine_preference fixture (commit 808eaea) | scope: fleet | owner: paperboy tests/test_pipeline_backend.py (pattern for any roster-behavior adopter) | verdict: ADD

LESSON (OBSERVED): Second consumer confirms the single-entry propagation gap: paperboy received no notification for the five hub entries 2026-08-03 through 2026-08-30 and caught up only by direct hub read on a machine visit. Matches the hub's open P1 (propagate_doctrine.py emits only the most recent entry; first observed downstream in ffskg 2026-08-13). The direct-read workaround costs a session-start detour and only fires when a human thinks to ask. | evidence: paperboy .claude/upstream-update.md "Five-entry catch-up cycle" disposal record; docs/sessions/20260910_doctrine_catchup_five_entries.md Upstream Note | scope: fleet | owner: hub propagate_doctrine.py (open hub P1) | verdict: UPDATE
