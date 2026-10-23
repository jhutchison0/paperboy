# Gate Review: topic/infra-doctrine-picture-20261022

**Verdict: GO WITH FIXES.** Critical 0, Warnings 3, Suggestions 5. Before merge: fix W2 (one word) and amend the refuted tactics-game detail in W3; W1 takes a recorded exception, not a history rewrite.

Reviewer: code-reviewer, 2026-10-22, on Nidhogg. Base `3ddde2d`, head `177adf7`, nine commits. Suite at head: `274 passed in 1.12s`. Suite at base, in a throwaway worktree with the same venv: `180 passed in 1.19s`. Every probe edit in Answer 3 was reverted with `git checkout --` (the hook with `chmod +x`); `git status --short` printed nothing after each probe and at the end. The worktree was removed.

## Critical

None.

## Warnings

### W1. 11ac109 bundles a gate surface with a test (pcc check 6)

`git show --name-only --format= 11ac109` lists `.claude/hooks/post-tool-shift-left-audit.sh` and `tests/test_audit_hook.py`. Check 6 counts 2 staged, 1 gate, and WARNs: "gate surfaces staged with other files". The intent of the rule holds: the test pins the hook's mode, and the hook judges writes under `src/`, not `tests/`. The letter does not. Do not rewrite: `docs/tasks.md` and `.claude/upstream-update.md` cite the four later shas (`dbed92e`, `bf037e8`, `e011fef`, `177adf7`), and a rebase would falsify every one. Fix: record the exception in the session doc (the `[gate][test]` tag already discloses it), and in a later `[gate]` commit add to check 6's note: "a test that pins a gate surface may ride with it; nothing else may."

### W2. Focus step 5 carries a relative date

`docs/tasks.md:11`: "reconciled against today's early adoption of `verifying-claims`". Slice 2 row 1 requires absolute dates in the Focus, and the section's own preamble says "as of 2026-10-22"; "today's" is false tomorrow. Rewrite: "reconciled against the 2026-10-22 early adoption of `verifying-claims`".

### W3. Claims with no `Evidence:` line, re-run

Per the Success claims line (e011fef), one Warning listing the claims in the commit messages and new docs that carry neither `Evidence:` nor `UNVERIFIED:`. Each re-run is below; two details are refuted, and nothing at a gate rests on either.

| Claim (where) | Re-run | Result |
|---|---|---|
| "both identical to d4ac4e4 after the src/ substitution" (fe719bf, ENFORCEMENT.md and SCRIPTS.md) | `diff` against `git -C ../tacsop archive d4ac4e4` | **Partly refuted.** ENFORCEMENT.md: four `src/myproject` to `src/` lines only. SCRIPTS.md: the same, plus its intro paragraph rewritten for paperboy and the hub's "asymmetry worth stating" sentence dropped (hub lines 135-137). Both pre-date the branch (untouched since 3ddde2d). |
| "as propter, fist and tactics-game did" (fe719bf) and "kept the held 2.2.x content out, as propter, fist and tactics-game did" (LESSON 4, `.claude/upstream-lesson.md`) | `diff -q` of each repo's `shift-left-testing/CI.md` against the d4ac4e4 copy | **Refuted for tactics-game.** propter and fist: identical. tactics-game: 3 lines carry `uv pip install --python .venv`, the 2.2.x pin that Focus step 5 itself names as held. hallmark at 2.2.1 as the lesson says. |
| "byte-identical to the hub at 7d9009d" (171b868, COP skill) | `diff -rq` against `git archive 7d9009d` | Holds: no output. |
| "it said 156 tests while the suite ran 180 at 3ddde2d" (74a14f2) | `git show 3ddde2d:CONTEXT.md`; worktree suite | Holds: `38:- **Tests**: 156 passing.`; `180 passed`. |
| "byte-identical to hub HEAD 2750d33" and "26 pins" (bf037e8) | `git -C ../tacsop diff --stat 2750d33 ff0d8b2 -- .claude/skills/verifying-claims`; `pytest --collect-only` | Holds: empty diff; `26 tests collected`. |
| "fails at 644 on disk or in the index" (11ac109) | probe h below | Disk half holds (1 failed). Index half read from the assertion (`startswith("100755")`), not probed: the probe writes the index. |
| "written first, red, then green" (11ac109); "written first (RED at import)" (171b868) | none possible | UNVERIFIABLE: process claims; the audit log cannot see Bash-made edits (gap G2). |
| "17 headings offered to this repo" (f7085c9) | `diff` mark against `../tacsop/docs/doctrine-updates.md` `^## 20` lines | Holds: same 17, same order. |
| "7 failed before e011fef, 0 after" (LESSON 3) | probe i below | Holds: `7 failed, 19 passed`; head suite 274 passed. |
| "this box's log was silent since 2026-07-20" (11ac109, LESSON 1) | `tail .claude/audits/shift-left-violations.log` | Consistent: last entry before today `2026-07-20T16:20:13`. |

Fix: amend LESSON 4 to "as propter and fist did; tactics-game at 2.1.1 carries the `--python .venv` pin". fe719bf's message is history; the session doc's Claims table carries the correction.

## Suggestions

### S1. G5's probe reads "behind" as "pre-rewrite"

`docs/gaps.md:15`: `git merge-base --is-ancestor origin/main HEAD` is true only when HEAD contains origin/main, so a post-rewrite clone that is merely behind reports as pre-rewrite. It is adequate only after Step 1's `git fetch && git pull` (session-start.md:60). A probe that asks the question directly: `git merge-base --is-ancestor c06e8ba HEAD` (any post-rewrite commit), or `! git cat-file -e <a pre-rewrite sha>`.

### S2. A state sentence in a YAML comment (propter M3)

`config/project.yaml:36`: "Roster of the boxes this repo is cloned on" states which boxes hold clones, and G5 says no box can know that. Pre-existing, but the branch edited this block (Nidhogg). Rewrite: "Roster of the boxes that have run this repo, keyed by hostname".

### S3. pcc check 1 fails on `.env.example` (hallmark's finding)

Both greps in check 1 match it: `.env.example:9` is `ANTHROPIC_API_KEY=sk-ant-your-key-here`, and `^\.env` matches the name. Any staged edit to the example FAILs twice. Pre-existing and untouched; dbed92e was the natural `[gate]` commit. Fix, in a `[gate]` commit: filter `grep -vE '^\.env\.example$'` before both greps.

### S4. Check 6's pattern omits the reviewer agent file

Entry B row 6 treats `.claude/agents/code-reviewer.md` as a gate surface; e011fef kept the rule by hand (1 file, 0 matched by the regex). Add `agents/code-reviewer\.md` to the check 6 alternation in a later `[gate]` commit, so the check sees what the entry says.

### S5. LANGUAGE.md Collector entry

Hallmark split the term because it has a `collectors/` package. Paperboy has no second sense (`grep -ri collector src/ main.py config/` finds nothing), so the pointer in the Common Operating Picture entry (LANGUAGE.md:147) is enough. Optional: a one-line **Collector** entry, since the register header carries the word and the glossary does not.

## Answers

### 1. Faithfulness of the annotations to the Adoption-Mode tables

**2026-09-18 (3 rows).** Row 1 N/A: `ls .github` fails, no workflows. Row 2 TEMPLATE-COPY: `diff -rq` against d4ac4e4 names only ENFORCEMENT.md and SCRIPTS.md, neither touched on the branch; the hub's last change to either (8797561) is an ancestor of d4ac4e4, so "the hub has not changed either since" holds. Row 3 N/A follows from row 1. Annotation true, with the W3 caveat on "after the src/ substitution".

**COP slice 1 (6 rows).** Row 1: four files identical to hub HEAD and to 7d9009d. Row 2: `## Picture Style` identical to the hub's CLAUDE.md section (awk-extracted diff empty), placed after Figure Style. Row 3: `docs/gaps.md` six rows, `src/gaps.py` at `parents[1]` with the extra `gap` key in REQUIRED, `tests/test_gaps.py` with `_keys` and the empty-Gap pin (diffs against the hub show only these and the import). Row 4 N/A: `git show 3ddde2d:config/project.yaml | grep -c known_issues` prints 0. Row 5: Step 4.5 matches the hub's text modulo the test path and the added phase/version bumps; `/sitrep` source 3 and the GAPS block match the hub's. Row 6 DEFER stated. Annotation true.

**Slice 2 (9 rows).** Row 1: no `state:` block existed; `last_updated` and `updated_by` removed; the hub's comment present with a dated sentence added; `## Focus` at the head of `docs/tasks.md`. Rows 2 to 4: Step 4.5, Steps 3, 3.5, 3.7 and 5 (identical to the hub's modulo the machine module path; the hub's item 11 Tools is the stated non-adoption), `/sitrep` sources 1 to 4; `.claude/README.md` had no Work Organization line at base (grep 0), so the Skills paragraph is the stated adaptation. Row 5: CONTEXT.md Current State is eight pointers, no snapshot. Row 6: `maintaining-project-context` identical to the hub, version 1.1.0. Row 7: README weights to config keys, `.claude/README.md` "7 agents" to "the whole roster", CONTEXT.md agent count to `ls .claude/agents/`; the ORIENTATION pin passes on all five surfaces. Row 8: `tests/test_state_block.py` differs from the hub only by the docstring, `parents[1]`, and the two added forbidden keys. Row 9: dbed92e, alone. Annotation true.

**Entry B (8 rows).** Row 1: skill identical to ff0d8b2 and to hub HEAD. Row 2: Step 5 "Summary, Claims, and Next Steps" and the Claims table identical to the hub's text. Row 3: `## Claims` section in the format doc with both count lines. Row 4: the SKILLS_FRAMEWORK block is verbatim the hub's; the tree line and sidecar count pass `test_skill_is_registered`. Row 5: `## Claim Style` identical to the hub's CLAUDE.md section. Row 6: e011fef, alone, line identical to the hub's. Row 7: `.claude/README.md` names `verifying-claims/`. Row 8: 26 tests collected; diff against the hub is the one `parents` line. The slice 2 annotation records the early adoption and the revert path. All eight adopted.

### 2. Layout adaptations

`parents[1]` in `src/gaps.py:13`, `tests/test_state_block.py:20`, `tests/test_verifying_claims.py:18`, and `tests/test_audit_hook.py:13`. `.venv/bin/python -c 'from src import gaps; print(gaps.REGISTER.exists())'` printed `/home/jhutchison/projects/github/paperboy/docs/gaps.md True`.

### 3. Can each pin fail

Each probe: edit, targeted test file, `git checkout --`, dirty count 0.

| Probe | Pin that caught it | Output |
|---|---|---|
| a. G1 status `Open` | `test_gaps.py::test_the_repo_register_holds_rule_5` | `1 failed, 31 passed` |
| b. G2 collector `TBD` | same | `1 failed, 31 passed` |
| c. G4 Gap cell emptied | same | `1 failed, 31 passed` |
| d. "The suite is 150 tests passing." under CONTEXT.md Current State | `test_state_block.py::test_no_orientation_surface_keeps_a_drifting_count[CONTEXT.md]` | `1 failed, 33 passed` |
| e. tag removed from Step 5 item 2 | `test_state_block.py::test_every_session_start_summary_line_says_where_it_came_from` | `1 failed, 33 passed` |
| f. `last_updated: x` appended to config/project.yaml | `test_state_block.py::test_the_config_has_no_state_block` | `1 failed, 65 passed` (with test_gaps.py) |
| g. `## Focus` renamed `## Direction` | `test_state_block.py::test_the_focus_lives_at_the_head_of_the_task_list` | `1 failed, 33 passed` |
| h. hook `chmod 644` on disk | `test_audit_hook.py::test_the_audit_hook_is_executable_on_disk` | `1 failed, 1 passed`; `git status --short` showed the mode change; after `chmod +x`: disk `755`, index `100755`, dirty 0 |
| i. (extra) Success claims line deleted from code-reviewer.md | six `test_every_surface_uses_one_bound[*]` plus `test_reviewer_checks_claims_for_evidence` | `7 failed, 19 passed` |

### 4. The register rows

All six are known unknowns: none has a known fix (G2's blind spot has no hook that can see a Bash edit; G3 and G4 are unmeasured, with tasks that build or run the collector, which is the register's division of labor). Collectors: G1 a Stop or PreToolUse hook; G2 a Bash or PreToolUse check or a post-commit audit; G3 a listening test recorded in `docs/reviews/`; G4 a two-pass scoring script; G5 a git probe per box at Step 1.5 (S1 on its form); G6 a `python main.py source` run read for warnings. Decisions: G1 and G2 whether the audit log is gate evidence; G3 whether the kernel stays in `SYSTEM_PROMPT`; G4 whether Pillar 4 can be claimed for the Agent backend; G5 whether the repo can go public; G6 whether Pillar 2's roster is live. Cells: `awk -F'|'` counts 7 separators on every row, so no `|` inside a cell, and `test_the_repo_register_holds_rule_5` passes. Numbers: G3 (49 to 0, 1 to 0, 8 of 8) dated 2026-07-20; G6 (82 papers, 10 articles) dated 2026-07-20; G1, G2, G4, G5 carry no measurement.

### 5. The Focus section

Six numbered steps, intent throughout. Dates: 2026-10-22, 2026-07-20, 2026-09-10 absolute; "today's" in step 5 is the one relative date (W2). No count (`DRIFTING_COUNT` finds none; "five sessions" and "both overclaim counts" name a window and a pair of lines, not a state) and no status.

### 6. Prose

Pass 1 (point): `docs/gaps.md` opens on "What this repo cannot see yet"; the Focus on "The order of the campaign"; CONTEXT.md Current State on "This section names where each part of the current state lives"; each annotation on its **Processed** line; each LESSON on its rule. All pass. Pass 2 (structure): the slice 2 annotation's first sentence packs four clauses with semicolons, the house pattern for these annotations since 2026-08-30; readable, not flagged. Pass 3 (words): a sweep of the new prose for the LANGUAGE.md cruft list and the hedge shapes found nothing. Pass 4 (em dashes): 0 in `docs/gaps.md`, the Focus, the annotations, the LESSON bodies, the Skills paragraph, and all nine commit messages; CONTEXT.md's five are Reading Order list-label separators and the lesson's one is a heading, both exempt by house convention. One Minor finding, W2 (rule 2, the concrete date).

### 7. Claims re-run, output pasted

```
$ diff -rq ../tacsop/.claude/skills/maintaining-the-common-operating-picture .claude/skills/maintaining-the-common-operating-picture && echo identical
identical                                            # also identical to git archive 7d9009d
$ diff -rq ../tacsop/.claude/skills/maintaining-project-context .claude/skills/maintaining-project-context && echo identical
identical
$ diff -rq <git archive d4ac4e4 shift-left-testing> .claude/skills/shift-left-testing
Files .../ENFORCEMENT.md and .claude/skills/shift-left-testing/ENFORCEMENT.md differ
Files .../SCRIPTS.md and .claude/skills/shift-left-testing/SCRIPTS.md differ   # CI.md, SKILL.md identical; see W3
$ diff -rq <git archive ff0d8b2 verifying-claims> .claude/skills/verifying-claims && echo identical
identical                                            # also identical to hub HEAD d51338e
$ .venv/bin/pytest -q 2>&1 | tail -1
274 passed in 1.12s
$ { cat CLAUDE.md CONTEXT.md README.md LANGUAGE.md .claude/README.md docs/gaps.md; sed -n '1,/^## Completed/p' docs/tasks.md; } | ... MISSING
(no output: 0 MISSING)                               # directory pass: 0 MISSING-DIR
$ git ls-files -s .claude/hooks/*.sh
100755 075fe972e1206cf224125dd56e5250b102e6b2e9 0	.claude/hooks/post-tool-shift-left-audit.sh
$ git diff 3ddde2d..HEAD -- .claude/doctrine-delivered | wc -l
23
```

The last probe, as the caller phrased it, is not empty: the file did not exist at 3ddde2d and f7085c9 created it with 17 lines. The branch's own claim is narrower, "no heading added for verifying-claims", and holds: `grep -c -i verifying .claude/doctrine-delivered` prints 0, and the 17 lines equal the hub's `docs/doctrine-updates.md` headings in order. The caller's probe should read `git diff f7085c9..HEAD -- .claude/doctrine-delivered`, which is empty.

### 8. Gate-surface separation

`e011fef`: `.claude/agents/code-reviewer.md` alone (S4 on the regex). `11ac109`: the hook and `tests/test_audit_hook.py` (W1). `dbed92e`: `.claude/commands/pcc.md` alone. The other six commits touch no file under `.claude/hooks/`, no `.claude/settings.json`, and neither `pcc.md` nor `pci.md` (grep over each `--name-only` listing: empty).

### 9. Sister-repo items

Collector sense split: N/A, no second sense here (S5). Dated numbers beside every measurement: yes, G3 and G6 (Answer 4). A state sentence in a YAML comment: one, pre-existing, `config/project.yaml:36` (S2). Reading Order rows 10 and 11 and artifact-table rows for `docs/tasks.md` and `docs/gaps.md`: present (CONTEXT.md:115-116, 130-131). pcc check 1 and `.env.example`: not fixed, pre-existing (S3); hallmark's and propter's check 1 read the same as paperboy's today.

## Counts

Critical 0. Warnings 3. Suggestions 5. Probes 9 run, 9 caught. Suite 274 passed (base 180). Claims re-run 11: 8 hold, 1 consistent, 2 partly or wholly refuted (W3), 2 UNVERIFIABLE.
