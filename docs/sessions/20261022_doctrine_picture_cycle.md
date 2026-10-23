# Session: Doctrine Cycle: Picture Slices 1 and 2, the CI Fix, and Claims Ahead of Release

**Date**: 2026-10-22
**Branch**: main (topic branch `topic/infra-doctrine-picture-20261022`, merged at `b0c27b0` and deleted per branching doctrine)
**Tags**: #session #doctrine #infra #config #docs #test #complete #pillar-4

**Documents**: [CONTEXT.md](../../CONTEXT.md) — Current State as pointers | [docs/gaps.md](../gaps.md) — the gap register, started this session | [CLAUDE.md](../../CLAUDE.md) — Claim Style and Picture Style kernels
**Implements**: [.claude/upstream-update.md](../../.claude/upstream-update.md) — the 2026-09-18 entry and both 2026-10-04 entries, annotated with disposal; the hub's held draft entry B (verifying-claims), ahead of release
**References**: [docs/reviews/20261022_doctrine_picture_gate.md](../reviews/20261022_doctrine_picture_gate.md) — code-reviewer gate | [docs/reviews/20261022_gap_register_ds_review.md](../reviews/20261022_gap_register_ds_review.md) — decision-scientist review of the register
**Follows**: [20260910_doctrine_catchup_five_entries.md](20260910_doctrine_catchup_five_entries.md)
**Cites**: [tacsop](https://github.com/jhutchison0/tacsop) `docs/doctrine-updates.md`, and the sister repos hallmark, propter, fist, assay and tactics-game, read by survey agents before anything was written

---

## Summary

Paperboy adopted the three hub entries delivered since its last cycle (the 2026-09-18 CI fix to shift-left-testing; the 2026-10-04 common operating picture, slices 1 and 2) and, by the user's decision, the verifying-claims skill the hub still holds, after five sister repos were read first. The repo now keeps a gap register (`docs/gaps.md`, nine rows) checked by `src/gaps.py`, a `## Focus` section as intent at the head of the task list, a config that is identity only, a `/session-start` whose every summary line says where it came from, and Claim Style and Picture Style kernels in CLAUDE.md. Found on the way: the shift-left audit hook never had its executable bit in the index and had fired only where a box chmod'ed it. Eleven commits on a topic branch through a three-agent gate (code-reviewer GO WITH FIXES; decision-scientist; pipeline-sme SUPPORTING), merged at `b0c27b0`.

| Metric | Value |
|---|---|
| Tests on main at start (`3ddde2d`) | 180 passed |
| Tests on main at close (`b0c27b0`) | 274 passed (`test_gaps.py` 15, `test_state_block.py` 31, `test_verifying_claims.py` 46, `test_audit_hook.py` 2) |
| Commits on the topic branch / on main after the merge | 11 / 12, this doc's commit excluded |
| Files changed `3ddde2d..b0c27b0` | 36; 2,170 insertions, 89 deletions |
| Gap register rows at close | 9, all open |
| Sister repos read first | 5 (hallmark, propter, fist, assay, tactics-game) |
| Subagents | 10: five surveys, one prototyper, four at the gate |
| Subagent tokens, as reported at each completion | about 1.25M (surveys 0.78M, gate 0.43M, prototyper 0.04M) |
| Gate findings: code-reviewer (Critical/Warning/Suggestion) | 0 / 3 / 5; nine probe edits, nine caught by their pins |
| Gate findings: decision-scientist (Major/Minor) | 8 / 9 |
| Gate findings: pipeline-sme (Blocker/Major/Minor) | 0 / 0 / 10 |
| `/pcc` check 5 at close | 0 MISSING over 27 paths; directory pass clean |
| Lead claims a reviewer refuted | 3 (the Claims table) |

## Context: how the cycle arrived

Session start found the hub's propagation run had appended eight doctrine entries to `.claude/upstream-update.md` on this box and written the delivery mark `.claude/doctrine-delivered`, while the remote already carried Muninn's 2026-09-10 adoption of five of those eight with a condensed disposal. The pull refused the conflict. The file was rebuilt as the remote version plus the three entries no machine had processed, verified byte-for-byte against the delivery, and the mark was committed as the hub's protocol asks (`f7085c9`). Step 1.5 then reported this box, Nidhogg, as not in the roster.

## Work Completed

### 1. Five sister repos read first

One read-only agent per repo (hallmark, propter, fist, assay, tactics-game) reported how each had adopted the same entries. What changed the plan:

- **Copy from the commit the entry names, not hub HEAD.** Hub HEAD carries CONOP OVERWATCH content the hub holds unreleased (shift-left-testing 2.2.x with the isolation tripwire; the Claims table). propter and fist copied 2.1.1 from the hub's staging commit `d4ac4e4`; tactics-game labelled its copy 2.1.1 but took `CI.md` with the held install pin; hallmark, bootstrapped from the template, carries 2.2.1 without an entry. The hub's own task list records the rule.
- **The Picture Style kernel assumes Claim Style.** Three of five sisters carry verifying-claims; fist and assay reworded the kernel's closing line instead. The user chose adoption under propter's conditions (section 5).
- **The register pins have known survivors.** agent-eval's 2026-10-06 gate ran twenty mutants against the hub's pins; its `_keys` YAML walk and the empty-Gap-cell check were taken here.
- **Config stamps are state.** tactics-game's reviewer called `last_updated` and `updated_by` a Major; paperboy carried the same two keys.

### 2. 2026-09-18: shift-left-testing 2.1.1 (`fe719bf`)

`SKILL.md` and `CI.md` copied from `d4ac4e4`. `ENFORCEMENT.md` and `SCRIPTS.md` keep the flat-layout adaptation, and `SCRIPTS.md` also carries a paperboy intro and omits a hub-only sentence; the commit message overstated the two as identical after the substitution, which the gate caught. No workflows here, so the PATCH row had nothing to patch.

### 3. 2026-10-04 slice 1: the gap register (`171b868`)

- The skill copied whole, byte-identical; the Picture Style kernel verbatim in CLAUDE.md after Figure Style.
- `docs/gaps.md`, six rows at first, nine after the gate (section 7), every number dated: test-first order the audit hook cannot see (G1), changes the hook never sees at all (G2), the prose kernel as heard (G3), Claude-stage determinism (G4), which rostered clones are post-rewrite (G5), feed liveness between sessions (G6), keyword-gate recall (G7), daily cadence and reach (G8), reader agreement with the selection (G9).
- `tests/test_gaps.py` first (red at import), then `src/gaps.py` at `parents[1]`, the hub's checker with the Gap cell added to the required fields. The known_unknowns pin walks parsed YAML keys so a comment naming the removed key cannot fail it.
- `/session-end` Step 4.5 is now Update Focus and Gaps; `/sitrep` reads the register and reports a GAPS block. LANGUAGE.md gained Focus, Gap Register and Common Operating Picture; the skills index gained the skill's block and a tree regenerated from the directory, which had listed seven of twelve shift-left sidecars and lacked five skills.

### 4. 2026-10-04 slice 2: the state leaves the config (`74a14f2`, `dbed92e`)

- `config/project.yaml` is identity: `last_updated` and `updated_by` left, the hub's comment in their place; Nidhogg rostered (workstation, personal, backend agent) by the user's decision at Step 1.5.
- `## Focus` at the head of `docs/tasks.md`: the campaign's order as intent, absolute dates, no counts; seven steps after the gate.
- `/session-start`: newest session doc by name; the Focus read at 3.5; the register at 3.7; every Step 5 line tagged measured, identity, record, intent, register or unchecked. The hub's Step 4 tool checks are held OVERWATCH 1c content and were not taken.
- CONTEXT.md Current State names where state lives. It had said 156 tests while the suite ran 180 at `3ddde2d`, and described a backend order the 2026-09-10 roster preference had changed.
- Counts to commands in README.md, .claude/README.md and CONTEXT.md; `tests/test_state_block.py` pins all of it, with the two config stamps added to the forbidden keys.
- `/pcc` check 5 scans the task list from its first line and reads `docs/gaps.md`; landed alone as `[gate]` per check 6.

### 5. verifying-claims 1.0.0 ahead of its entry (`bf037e8`, `e011fef`)

The hub holds entry B under the OVERWATCH release; the user adopted it under propter's three conditions: one named source commit (`ff0d8b2`, identical at hub HEAD), all of entry B's surfaces with its 26 pins, and a revert path in `docs/tasks.md` with no heading added to the delivery mark. The code-reviewer's Success claims line landed alone, tagged `[gate]`. Ride-along: the KB-graph capture point in `/session-end` and the format doc, so the traversal window opened 2026-09-10 has somewhere to write its metric.

### 6. Found on the way: the audit hook never had its executable bit (`11ac109`)

An Edit-tool change to `src/gaps.py` logged nothing. The hook is run by path from `settings.json`, and `git log --summary` shows it created at mode 100644 on 2026-05-22 and never changed: it fired only where a box had chmod'ed it locally, and today's pull rewrote the file at 644 here. The 2026-09-10 port verified it by pipe test through `bash`, which cannot see the mode. `tests/test_audit_hook.py` was written first (two failures), then the bit restored on disk and in the index; `/pcc` check 4 reads hook modes now, and after the fix two Edit-tool edits each logged a line. The same session confirmed gap G2 the day it was written: the prototyper created `src/gaps.py` through a Python script run from Bash, and the log recorded nothing.

### 7. The gate

Four agents, read-only but for their review files. The code-reviewer's gate (GO WITH FIXES, 0 Critical, 3 Warnings, 5 Suggestions) ran nine probe edits against the new pins and each was caught; it re-ran eleven claims and refuted two of the lead's. The decision-scientist found the register real but unsound: three collectors measured a different quantity than their row named (G2 log coverage, G5 a clone that was merely behind, G6 a feed that dies without a warning); the two-run G4 design would call a backend that differs three times in ten deterministic about half the time; and the register held no outcome line. It supplied the ten-run three-arm determinism design and the paired listening design now cited from the cells, and two selector defects for the task list (the category sub-criterion is structurally zero; failures are scored differently on the two backends). The pipeline-sme (SUPPORTING) added the two mission gaps the register lacked, keyword-gate recall and daily cadence and reach, and dated the one episode-length measurement the README restated three times. The test-runner's independent run matched: 274 passed, PCC checks per commit, every Detect grep silent. All fixes landed in `a070aa9`; the pcc changes alone in `f275003`. One Warning stands recorded rather than fixed: the hook fix and its pin share a commit, and four later shas cited in living docs made a rebase the worse trade.

KB-graph: `/pcc` check 5 (file + directory passes) → 0 MISSING over 27 paths, run after the fix pass and again after the merge (M2 count: 0).

**Two process slips, corrected before the merge.** Twice a `&&` chain with a heredoc commit message continued past a failed check: once the verifying-claims commit was skipped (the reviewer line was still missing, so seven pins failed) and landed next; once the secrets check hit the gate review's quoted placeholder and the fix pass was swept into a `[gate]` commit, split by a soft reset before anything was merged. Commit messages now come from files, so a failed check stops the chain.

## Claims

| Claim | State | Evidence |
|---|---|---|
| The suite passes on main after the merge | tested | `.venv/bin/pytest -q` → `274 passed in 1.13s`, `exit=0`; `.venv/bin/python -V` → `Python 3.12.13`; at `b0c27b0` |
| The topic branch is merged into main and deleted | deployed, locally | `git merge-base --is-ancestor f275003 main` → `exit=0`; `git rev-parse --short main` → `b0c27b0`; `git branch -d topic/infra-doctrine-picture-20261022` → `Deleted branch topic/infra-doctrine-picture-20261022 (was f275003)` |
| main is not pushed | stated, not claimed | `git log --oneline origin/main..main \| wc -l` → `12`; `origin/main` at `3ddde2d`. The push is the user's call |
| The working tree is clean | observed | `git status --porcelain` → empty, at `b0c27b0` and again after the hook round trip |
| The three new skill directories match the hub, and verifying-claims matches hub `ff0d8b2` | observed | `diff -rq` → no output, `exit=0`, for each of the three; `git -C ../tacsop diff --quiet ff0d8b2 HEAD -- .claude/skills/verifying-claims` → `exit=0` |
| shift-left-testing `SKILL.md` and `CI.md` match hub `d4ac4e4`; `ENFORCEMENT.md` and `SCRIPTS.md` differ by design | observed | `git show d4ac4e4:<path> \| diff -q - <path>` → `exit=0` for both. The message of `fe719bf` called the other two "identical after the src/ substitution"; the gate re-ran it: `SCRIPTS.md` also carries a paperboy intro and omits a hub sentence. Corrected in the annotation (`a070aa9`) |
| The audit hook is executable in the index and fires from the Edit tool | observed | `git ls-files -s .claude/hooks/post-tool-shift-left-audit.sh` → `100755 075fe972 0`; two Edit-tool edits to `src/gaps.py` at 21:37:19 and 21:37:22 each appended an `OK_TEST_EXISTS` line to `.claude/audits/shift-left-violations.log`. Before the fix, the only new line (21:10:54) came from a pipe test through `bash` |
| The register holds rule 5 | tested | `gaps.problems(gaps.REGISTER.read_text())` → `[]` |
| Reference integrity | measured | `/pcc` check 5 file pass: 27 paths, 0 MISSING; directory pass: 0 MISSING-DIR; at `b0c27b0` |
| The delivery mark carries the hub's 17 headings and none for verifying-claims | observed | `wc -l < .claude/doctrine-delivered` → `17`; `grep -ci 'verifying\|claim' .claude/doctrine-delivered` → `0`; `git diff f7085c9..main -- .claude/doctrine-delivered` → empty. The brief to the test-runner expected `git diff 3ddde2d..HEAD` on the file to be empty; it is 17 insertions, because `f7085c9` created the file. Refuted by the runner |
| This box is post-rewrite (gap G5) | observed | `git cat-file -e 'c06e8ba^{commit}'` → `exit=0`. G5's first wording also said the pre-rewrite sha `c61b79d` is absent here; `git cat-file -t c61b79d` → `commit`, because this box performed the rewrite and keeps the unreachable objects. Caught by the probe before anyone relied on it; the cell now says so |
| tactics-game copied 2.1.1 clean | refuted | Its `CI.md` carries the 2.2.1 `--python .venv` pin on three lines (gate W3). LESSON 4 in `.claude/upstream-lesson.md` corrected in place (`a070aa9`) |
| Nidhogg resolves from the roster with its backend preference | observed | `.venv/bin/python -m src.machine` → `Nidhogg (workstation, personal, backend: agent)` |
| The gate's verdict | record | `docs/reviews/20261022_doctrine_picture_gate.md`: GO WITH FIXES, 0 Critical, 3 Warnings, 5 Suggestions; nine probes, nine caught |

Overclaims the user caught this session: 0

Overclaims a reviewer caught this session: 3

The three: `SCRIPTS.md` identical after the substitution; tactics-game among the clean 2.1.1 copies; the delivery-mark diff from `3ddde2d` expected empty. The G5 "absent" claim was refuted by a tool before anyone relied on it and sits in neither count; its row shows the correction.

## Key Decisions

| Decision | Rationale |
|---|---|
| Rebuild the doctrine file as remote version + unprocessed entries, rather than carry the five already-adopted entries' raw text | Muninn's condensed disposal already records them; the hub file holds the full text; the delivery is backed up in the session's scratchpad and a stash |
| Copy 2.1.1 from `d4ac4e4`, not hub HEAD | HEAD is 2.2.1, held under OVERWATCH; propter and fist did the same; the hub's task list names the rule |
| Adopt verifying-claims ahead of its entry | The Picture Style kernel's closing line names Claim Style; three sisters carry it; the user decided, under propter's conditions, so the release reconciles by entry B's Detect block |
| Remove `last_updated` and `updated_by` from the config | A prose session summary rewritten every session is the state block in another name (tactics-game's reviewer, Major 5); the newest session doc by name is the record |
| Leave the hub's session-start tool checks and the isolation tripwire out | Both are held OVERWATCH content without an entry; paperboy also has no pyproject for `addopts` |
| Add the Gap cell to the checker's required fields | An empty Gap cell survived the hub's pins (agent-eval M16); two lines and one test close it |
| Fix the hook's bit on this branch, as `[gate]` with a test | A defect found while adopting is still a defect; a gate surface changes alone, and a test that pins the gate may ride with it (now written into check 6) |
| Take the reviews' register rewrites rather than defer them | Three collectors would have closed their gap on the wrong quantity; a register that closes on the wrong measurement is the failure the skill exists for |
| Keep the default weights visible in the README | Defaults in a tracked YAML are identity, not drift (pipeline-sme F10); the regex's `%` branch had forced them out |

## Pillar Compliance

| Pillar | Status | Notes |
|---|---|---|
| **Content Quality First** | UNCHANGED | No distiller change; G3 names the unmeasured half of the prose kernel, with a paired design |
| **Source Diversity & Resilience** | UNCHANGED | No sourcing change; G6 names what nobody measures between sessions, per feed |
| **Relevance Through Hybrid Scoring** | UNCHANGED | No scoring change; G4, G7 and G9 name the unmeasured inputs and the first outcome; the dead category sub-criterion is a P2 task |
| **Pipeline Idempotency** | PASS | The config carries no state; what moves is measured by command at session start; the pillar now reads as intent with G4 named |
| **Extensibility by Design** | PASS | `src/gaps.py` follows the flat-module pattern; the register is a markdown table any tool can read |

## Commits

| Hash | Subject |
|---|---|
| `f7085c9` | [infra] Sync hub delivery: three unprocessed doctrine entries + delivery mark |
| `fe719bf` | [infra] Adopt hub 2026-09-18: shift-left-testing 2.1.1 (uv venv --clear in CI.md) |
| `171b868` | [infra][test] Adopt hub 2026-10-04 picture slice 1: gap register, checker, Picture Style kernel |
| `74a14f2` | [infra][config][test] Adopt hub 2026-10-04 picture slice 2: the state leaves the config |
| `e011fef` | [gate] code-reviewer: the Success claims checklist line (verifying-claims entry B, row 6) |
| `11ac109` | [gate][test] Audit hook: restore the executable bit, pinned by a test |
| `dbed92e` | [gate] pcc: check 5 scans the task list from its first line; check 4 reads hook modes |
| `bf037e8` | [infra][test] Adopt verifying-claims 1.0.0 ahead of its entry (hub ff0d8b2) |
| `177adf7` | [doc] Annotate the three entries' disposals; task list; four upstream lessons |
| `a070aa9` | [doc] Gate fixes from three reviews: register G1 to G9, Focus, pointers, counts; the two review records |
| `f275003` | [gate] pcc: check 1 excludes .env.example; check 6 names the reviewer file and the gate-pinning-test exception |
| `b0c27b0` | Merge topic/infra-doctrine-picture-20261022: hub entries 2026-09-18 and 2026-10-04, verifying-claims ahead of release |

The commit that carries this doc is reported in the session's final message.

## Next Steps

- [ ] The `## Focus` section of `docs/tasks.md` carries the order: the register's collectors G6, G3, then G4 with G7; the Phase 2 close by command, v0.3.0 and the public flip; Phase 3's run-history log (G8's collector); the selector findings; the hub's held entries; the traversal window.
- [ ] Push `main` (12 commits ahead of `origin/main` at close, this doc's commit excluded).
- [ ] Hub harvest: `.claude/upstream-lesson.md` carries seven lessons, four from today (the hook index-mode lesson, G2's same-day confirmation, the eager-dict pin, the copy-from-the-entry's-commit rule).
- [ ] On Muninn: pull, then `/session-start` (the hook's bit arrives through the index; G5 wants that box's `git cat-file -e 'c06e8ba^{commit}'`).
