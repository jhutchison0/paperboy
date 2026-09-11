# Session: Five-Entry Doctrine Catch-Up from the tacsop Hub

**Date**: 2026-09-10
**Branch**: main
**Tags**: #session #infra #doctrine #config #docs #complete #pillar-4

**Documents**: [CLAUDE.md](../../CLAUDE.md) — Figure Style kernel, Bulk Data Storage, KB Traversal, uv setup | [CONTEXT.md](../../CONTEXT.md) — Reading Order entries 10 and traversal pointer | [SKILLS_FRAMEWORK.md](../../.claude/skills/SKILLS_FRAMEWORK.md) — index caught up with the directory
**References**: [.claude/upstream-update.md](../../.claude/upstream-update.md) — disposal record appended this session
**Follows**: [20260720_public_release_prep.md](20260720_public_release_prep.md)
**Cites**: [tacsop](https://github.com/jhutchison0/tacsop) `docs/doctrine-updates.md` — the five entries adopted

---

## Summary

Paperboy sat five doctrine entries behind the tacsop hub (last adoption 2026-07-20; the hub had published 2026-08-03 through 2026-08-30). This session discovered the gap by direct hub read, since no push notification had arrived, and adopted all five in dependency order: uv environments first (they change the ground everything else runs on), records last. Along the way it surfaced that this machine is a fresh clone with a broken venv, named the machine (`Muninn`) under the new identity doctrine, and caught the skills index four entries behind its own directory. Eight commits; suite grew 166 to 172 tests, all passing; `/pcc` gained two checks and both run clean.

## Context: a fresh box

Session start found `.venv/` an empty shell built on system Python 3.10.12 (below the 3.11 minimum, no pip, no packages) and every file mtime stamped today: this is a re-clone, consistent with the 2026-07-20 next-step "re-clone any other machine's clone" after the history rewrites. The first rebuild used `python3.12 -m venv` + pip; the uv doctrine adopted an hour later retroactively blessed the interpreter (it was already uv-managed) and replaced the build method.

## Work Completed

### 1. uv environment doctrine (hub 2026-08-03, drop-in level) — `bfc8871`

- Froze the morning venv, rebuilt with `uv venv --clear --managed-python` on uv-managed CPython 3.12.13, reinstalled from `requirements.txt` via `uv pip`. Parity exact: 166 passed before and after.
- `python-venv-management` 2.0.0 → 3.0.0 and `shift-left-testing/CI.md` re-copied verbatim (diff confirmed no local customizations existed to preserve).
- Setup blocks in CLAUDE.md, README.md, and `config/project.yaml` switched to uv commands; `python.package_manager: "uv"` declared; the ElevenLabs stub docstring hint updated.
- Machine sweep found no pyenv/conda incumbents, so the destructive removal step was N/A. `requirements.txt` (not pyproject extras) remains the install spec, per repo shape.

### 2. Machine identity (hub 2026-08-29 Part 1) — `f610fb9`

- `machines:` roster added to `config/project.yaml`: `Muninn` (workstation, personal) and the verbatim `unknown` fallback. No usernames, per the entry's rule.
- `src/machine.py` adapted from the hub template for the flat layout: import path `src.machine`, config resolution `parents[1]`. Test written first (`tests/test_machine.py`, 6 tests, RED confirmed before the module existed, then GREEN).
- `/session-start` gains Step 1.5 (print the machine line, never add a host silently) and **Machine** as summary item 1. Live check: `Muninn (workstation, personal)`.
- Part 2 (lake conventions for work repos) skipped: paperboy's remote is github.com.

### 3. Audit-hook fallback + agent research tools (hub 2026-08-27 Parts 2–3) — `9d9834d`

- The shift-left audit hook gains the import-grep fallback: when `tests/**/test_<module>.py` misses by name, any `test_*.py` that imports the module counts as a partner. One deliberate adaptation: dotted module names keep the `src.` prefix, because flat-layout imports are `from src import X` (the hub strips to the package under `src/`). Windows path normalization ported alongside.
- Pipe-test verified both stages: `src/machine.py` matches by name; `src/config.py`, previously a standing false `MISSING_TEST` (its partner is `test_config_validation.py` plus three feature-named suites), now logs `OK_TEST_EXISTS` four times.
- `ENFORCEMENT.md` updated to describe the two-stage lookup and its honest limits.
- `proposer` and `code-reviewer` gain `WebSearch, WebFetch`; `.claude/README.md` records the capability-versus-knowledge distinction in paperboy's own vocabulary (upstream-template agents, since the repo has no Level 0 concept).
- `CONOP-FORMAT.md`, `OPORD-FORMAT.md`, and `session-doc-format.md` re-copied verbatim: the hub's 2026-08-27 rule-8 sweep went further than the `5f70a48` stragglers re-merged on 2026-07-20. All three now byte-identical to the hub. `SCRIPTS.md` line 3 needed no fix; our copy is locally adapted and clean.

### 4. Knowledge-graph traversal (hub 2026-08-21, amended 08-22) — `7ae51ce` + `7da681f`

- `traversing-the-knowledge-base` 1.0.0 installed with the required customizations: edge table recounted for this corpus (15 of 15 session docs carry typed headers, 108 markdown links, 875 bare path mentions, ratio 8:1), five-session evaluation window reset to open 2026-09-10, hub-local March allowlist dropped from traversal 5.
- CLAUDE.md and the CONTEXT.md Reading Order now point at the skill (a skill nothing references is a skill nobody loads).
- `/pcc` checks 5 (reference integrity, file + directory passes) and 6 (gate-surface separation) wired **after** the by-hand first run the amendments insist on. First run: 3 findings, each dispositioned rather than suppressed:

  | Finding | Disposition |
  |---|---|
  | `output/.selection_history.json` (file pass) | Allowlisted: gitignored runtime artifact LANGUAGE.md legitimately names |
  | `.claude/agent-memory/` (dir pass) | Allowlisted: gitignored per-machine agent state |
  | `docs/reviews/` (dir pass) | Created with `.gitkeep`: it is the review-output convention LANGUAGE.md names |

- The shipped `sed` task-range was verified against paperboy's actual headings before trusting it: captures Active + Blocked (12 lines), stops at Completed. Baseline recorded: **0 MISSING on both passes**.
- The amendment's `.claude/`-versioning mandate was already satisfied: Mode A, 57 tracked files, exactly the three blessed ignores.
- Check 6's first exercise was its own installation: the `pcc.md` change landed alone as the `[gate]` commit `7da681f`, separate from the `[doc]` commit it graded.
- KB-graph: `/pcc` check 5 first run (file + directory passes) → 3 findings dispositioned, 0-MISSING baseline recorded (M2 count: 0).

### 5. Figure style doctrine (hub 2026-08-27 Part 1) — `688878a`

- `designing-clear-data-displays` 1.1.0 copied whole (5 files, verified byte-identical). ADOPTION.md run: CLAUDE.md gains the eight-rule Figure Style kernel beside Prose Style; `code-reviewer` gains the figure checklist line; `writing-simple-and-direct` bumped to 1.0.1 (the chart-or-table hand-off sentence).
- No UX override to state: briefings are prose and the docs already prefer Mermaid. No sweep of existing figures, per the grandfathering rule.
- Rode along, prompted by the entry's check-yours note: `SKILLS_FRAMEWORK.md` was four skills behind its own directory (`using-topic-branches`, `writing-simple-and-direct`, `traversing-the-knowledge-base`, `designing-clear-data-displays` unlisted) and the shift-left sidecar list was stale at 7 of 12. All caught up. Paperboy has no `.claude/README.md` skills tree; the framework file is the single index.

### 6. Home storage (hub 2026-08-30, lake-conventions 1.1.0) — `bc8d4dc`

- Skill copied whole (4 files, identical); paperboy is exactly its personal-repo audience (git remote on github.com).
- `scope: personal` declared under `project:`; Muninn already rostered personal, so the `HOME-STORAGE.md` gate can open when needed.
- CLAUDE.md Bulk Data Storage section, CONTEXT.md Reading Order entry 10, and the skills index wired.
- `HOME_*` env plumbing **deferred** until the first bulk-data write: today the pipeline writes only small gitignored markdown to `output/`, and role-named variables nothing reads would be inert. Phase 4 audio is the expected trigger.

### 7. Records — `d9a7eda`

Disposal record for all five entries appended to `.claude/upstream-update.md` (annotate, never delete); `docs/tasks.md` updated; final verification run.

## Key Decisions

| Decision | Rationale |
|---|---|
| Adoption order: uv → machine → hook/tools → traversal → figure → storage | The environment changes what everything else runs in; records depend on everything before them; the rest ordered small-to-careful |
| Import-grep fallback keeps the `src.` prefix in dotted names | Paperboy's tests import `from src import X`; the hub's prefix-stripping assumes a package under `src/`, which would make the fallback inert here |
| `docs/reviews/` created rather than allowlisted | LANGUAGE.md names it as the review-output convention; creating it makes the reference true instead of excused |
| `HOME_*` variables deferred | An env variable no code reads is dead config; the doctrine's loud-failure pattern only means something when a reader exists |
| Muninn rostered `scope: [personal]` | Norse-named boxes in the hub roster are personal-scoped; the home-storage gate requires the machine rostered personal; adjust if the box also does work-scoped writes |
| `pcc.md` landed as its own `[gate]` commit | Check 6's rule applied to check 6's own installation; a gate and the work it grades must not move together |

## Pillar Compliance

| Pillar | Status | Notes |
|---|---|---|
| **Content Quality First** | UNCHANGED | No distiller or briefing changes; figure kernel governs docs, not briefings |
| **Source Diversity & Resilience** | UNCHANGED | No sourcing changes |
| **Relevance Through Hybrid Scoring** | UNCHANGED | No scoring changes |
| **Pipeline Idempotency** | PASS | uv-managed interpreter decouples the venv from system Python drift; machine identity makes the box an explicit, readable input instead of ambient prose |
| **Extensibility by Design** | PASS | `src/machine.py` follows the existing flat-module pattern; storage doctrine pre-positions the Phase 4 seam without building it |

## Commits

| Hash | Subject |
|---|---|
| `bfc8871` | [infra] Adopt uv environment doctrine (hub 2026-08-03, drop-in level) |
| `f610fb9` | [infra][test] Adopt machine identity doctrine (hub 2026-08-29 Part 1) |
| `9d9834d` | [infra][gate] Adopt hub 2026-08-27 Parts 2-3: hook fallback, agent research tools |
| `7ae51ce` | [doc] Adopt knowledge-graph traversal doctrine (hub 2026-08-21, amended 08-22) |
| `7da681f` | [gate] pcc checks 5-6: reference integrity and gate-surface separation |
| `688878a` | [doc] Adopt figure style doctrine (hub 2026-08-27 Part 1) |
| `bc8d4dc` | [infra] Adopt home storage doctrine (hub 2026-08-30, lake-conventions 1.1.0) |
| `d9a7eda` | [doc] Annotate five-entry doctrine catch-up; task list updated |

Plus this session-end commit (project.yaml stamp, session doc).

## Upstream Note

Nothing in the hub artifacts was broken during adoption, so no correction routes upstream this cycle. One fleet observation worth carrying to the hub: no push notification ever arrived for these five entries, which matches the hub's own recorded known issue that its propagation script emits only the most recent entry — a consumer that misses a cycle stays missed. This session's direct-read discovery is the workaround; the hub fix is theirs.

## Next Steps

- [ ] Push this branch (the push was blocked by the session's permission classifier; run `git push` by hand or approve it)
- [ ] Re-create local `.env` on this box (`ANTHROPIC_API_KEY`, `USER_CONTEXT`): a re-clone does not carry it, and live pipeline runs need it
- [ ] KB-traversal window is open: next five sessions record `KB-graph:` lines and check-5 counts (M1/M2/M3 close-out per the skill's matrix)
- [ ] Standing P3s unchanged: listen-test the prose kernel (distiller-dev), CLI temperature control, batch scoring 1 → 5, CONOP checklist status
- [ ] First property test still pending (selector scoring invariants; Hypothesis plumbing arrives with it)
- [ ] Flip the repo public (user action, carried from 2026-07-20); v0.3.0 cut remains a natural release boundary
