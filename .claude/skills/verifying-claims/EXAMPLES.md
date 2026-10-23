# EXAMPLES — Before and After

Sidecar to `SKILL.md`. Seven pairs, one per failure shape, then one clean report. Pairs 1 to 6 are shapes: the systems are generic and the output is illustrative. Pair 7 is real. In every Before, nothing errored; that is why the claim felt safe.

---

## 1. The state overclaimed

**Before**:
> The timer is installed and tonight's run landed. The pipeline is live.

**After**:
> Tonight's run failed (observed), so the pipeline is not live.
> Evidence: `tail -2 logs/run.log` → `OperationalError: no such column: run_id`, `nightly run FAILED, exit 1`
> The timer is scheduled (observed). I have not checked which commit its checkout holds.
> Evidence: `systemctl list-timers nightly.timer` → `1 timers listed.`
> The error points at the state database's schema. That is the next thing to check.

**Rules applied**: 1 (name the state), 3 (the outcome the claim names).
"Landed" and "live" claim observed, and only the run's own record of how it ended reaches that. The launcher exiting 0 says the launch worked. The After also stops short of "deployed": a listed timer is scheduled, and nothing here shows which code it runs.

---

## 2. The check skipped

**Before**:
> Pushed to origin. The mirror is in sync.

**After**:
> Pushed to origin (deployed).
> Evidence: `git rev-parse HEAD` → `4f2a91c`; `git ls-remote origin refs/heads/main` → `4f2a91c refs/heads/main`; `git status --porcelain` → no output
> The mirror is not at origin's SHA (observed).
> Evidence: `git ls-remote mirror refs/heads/main` → `9be07d3 refs/heads/main`

**Rules applied**: 3, 4 (show it).
The push was checked and the mirror was assumed. Two claims need two probes.

---

## 3. The absence asserted

**Before**:
> That environment was never built, so I'll create its venv from scratch.

**After**:
> The venv exists and its Python runs (observed), so I'll use it as built.
> Evidence: `find . -maxdepth 3 -name pyvenv.cfg` → `./.venv/pyvenv.cfg`, `./.venv-gpu/pyvenv.cfg`; `.venv-gpu/bin/python -V` → `Python 3.12.13`

**Rules applied**: 1 (an absence is a claim), 3.
The Before is not a report. It is a plan, and the belief under it is a claim nobody checked. One `find` could have disproved it, and acting on it would have rebuilt what was already there.

---

## 4. The fix not exercised

**Before**:
> Fixed: the scan now skips empty partitions.

**After**:
> The scan fix is tested: two new tests for empty partitions pass.
> Evidence: `.venv/bin/pytest -k empty_partition; echo "exit=$?"` → `2 passed, 61 deselected in 0.41s`, `exit=0`; `.venv/bin/python -V` → `Python 3.12.13`

**Rules applied**: 1, 3.
"Fixed" claims tested. Until a run exercised the change, the true sentence was "the fix is written". Whether those tests fail without the fix is a separate claim; test-first work shows it by running them red before the change.

---

## 5. The validation not run

**Before**:
> Production validation passed; the outputs match the reference.

**After**:
> The staging validation passed (tested).
> Evidence: `./validate --against staging; echo "exit=$?"` → `412 of 412 rows match`, `exit=0`
> UNVERIFIED: the production validation. `./validate --against prod --read-only; echo "exit=$?"` → `AccessDenied: this role cannot read the production store`, `exit=1`. Someone with read access can run the same command.

**Rules applied**: 4, 6 (probes read).
A weaker check that ran does not carry the stronger claim. The blocker is shown, not asserted: a read-only attempt was refused, and the refusal is pasted. "I have no access", with no error and no named credential, is a skipped check.

---

## 6. The stale number

**Before**:
> The cache is at 41 GB after the sweep.

**After**:
> The cache holds 58 GB (observed).
> Evidence: `du -sh cache/` → `58G	cache/`
> My earlier message said 41 GB. That figure came from before this turn.

**Rules applied**: 2 (this turn).
The number was true once. A figure carried forward from earlier in a session is a claim about then, reported as a claim about now.

---

## 7. The count from memory (real)

**Before**:
> The template `conftest.py` is 11 lines.

**After**:
> The template `conftest.py` is 12 lines (observed).
> Evidence: `wc -l tests/conftest.py` → `12 tests/conftest.py`, at the commit under review on 2026-09-30

**Rules applied**: 2, 3.
A plan's first draft made this claim, and a reviewer's `wc -l` caught it. A count typed from memory is stale on arrival. The file has grown since, which is why the line names its date: evidence is true of the moment it was taken. A number you will cite or act on gets the probe; a number nobody will use does not need one.

---

## A clean report

> Renamed `load_cfg` to `load_config` in `utils.py` and its two callers; the diff is above. I have not run the tests.

This report needs nothing added. It claims written, and the diff in the same message is its evidence. "I have not run the tests" is a true statement of what was not done, not an unverified claim, so it takes no `UNVERIFIED` line. The same holds for a plan, an opinion, or an explanation of how code works. An `Evidence:` line under each of those would be noise, and a reader trained on noise stops reading the lines that matter.
