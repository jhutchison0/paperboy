---
name: verifying-claims
description: House rule for success claims. Six kernel rules, four claim states (written, tested, deployed, observed), one probe per claim type, and before/after examples. Use before reporting that something passed, landed, synced, exists, or is absent, and when writing or reviewing a session's Claims table.
version: "1.0.0"
---

# Verifying Claims

House rule for saying that work succeeded. It covers each claim a reader will act on: a statement that something works, landed, synced, exists, or is absent. A plan, an opinion, or an explanation of code is not a claim; the belief a plan rests on is one. A diff shown in the same message is its own evidence. The failure this skill counters: success reported because nothing errored, not because anything proved it.

Scope, stated once: `shift-left-testing` governs how code gets tested. This skill governs what a report may say about the result, in every final message, status report, commit message, review, and session doc. It also covers working narration that acts on an unchecked belief: "that was never built, so I will rebuild it" is a claim.

**Philosophy**: *Claim what the evidence reaches, and show the evidence.*

## When to Use

- Before any sentence that says something passed, landed, was pushed, merged, or deployed, or is live
- Before saying, or acting on the belief, that something is absent, unbuilt, or not done
- Before repeating a number measured earlier in the session
- Writing the `## Claims` table at `/session-end`
- Reviewing a report: the code reviewer checks each claim for its evidence

## The Kernel

Six rules. The ambient copy lives in CLAUDE.md.

1. Name the state: written, tested, deployed, or observed. Claim no higher than your evidence reaches. An absence is a claim too.
2. Evidence comes from this turn, after the last change to the thing claimed. Earlier output is stale: re-run the check, re-measure the number.
3. Check the outcome the claim names, with a check that can fail. A launcher's exit 0 is not the outcome; no error is not evidence.
4. Under each claim a reader will act on, put an `Evidence:` line with the command and its output, or `UNVERIFIED: <blocker>`. A skipped check is not a blocker; run it.
5. A checkout a timer or service runs from is deployed only when clean: `git status --porcelain` prints nothing.
6. Probes read; they never write to the system they check.

## The Four States (rule 1)

| State | Means | Evidence that reaches it |
|---|---|---|
| written | The change exists in a file | The diff, or the path |
| tested | A run exercised it and passed | This turn's summary line and exit status. An import or a compile does not reach it |
| deployed | It is delivered: pushed, merged, installed, or running from a checkout | The remote SHA equals the local one; for a checkout a timer or service runs from, a clean tree as well |
| observed | The live system, looked at: output it produced, or its present state | Output the run produced after the launch, or a read of the thing as it is now |

No state implies the next. Tested code might not be pushed yet, and pushed code might never have run. A report that says "live" claims observed, and needs output the run produced.

## Probes (rule 3)

One probe per claim type, read-only except the test run. Each can fail, which is the point: run it, then read the result against the last column.

| Claim | State | Probe | Holds when |
|---|---|---|---|
| The run landed | observed | The run's own exit status; `tail <log>`; `ls -l <output>` | Exit 0, the log ends with the run's completion line, and the output is newer than the launch (its time is in the log's first line or the scheduler) |
| Pushed | deployed | `git rev-parse HEAD`; `git ls-remote origin refs/heads/<branch>`; `git status --porcelain` | The second prints one line with the first's SHA, and the third lists no file the claim covers |
| Mirror synced | deployed | `git ls-remote <mirror> refs/heads/<branch>`; `git ls-remote origin refs/heads/<branch>` | Each prints one line, and the two SHAs match |
| Tests pass | tested | `.venv/bin/pytest; echo "exit=$?"`; `.venv/bin/python -V` | The summary line shows no failures and no skip or deselection you cannot explain; `exit=0`; on the Python the CI config names (with no CI, say which Python ran) |
| The venv exists, or does not | observed | `find . -maxdepth 3 -name pyvenv.cfg`; `cat <venv>/pyvenv.cfg`; `<venv>/bin/python -V` | The cfg prints and Python runs: usable. The cfg prints and Python fails: there, but broken. `find` prints nothing: none within three levels of this directory, which is less than "absent" |
| Merged | deployed | `git merge-base --is-ancestor <sha> main; echo "exit=$?"`; `git rev-parse main`; `git ls-remote origin refs/heads/main` | `exit=0`, and the last two print the same SHA |
| Deployed: running from a checkout | deployed | In that checkout: `git status --porcelain`; `git rev-parse HEAD`; `git ls-remote origin refs/heads/<branch>` | The first prints nothing; the third prints one line with the second's SHA |

Five traps the table cannot hold:

- **Empty output is not a match.** `git ls-remote` prints nothing and exits 0 for a branch the remote lacks; with `--exit-code` it exits 2. A bare `<branch>` also matches `feature/<branch>`, so write `refs/heads/<branch>`.
- **An exit status after a pipe belongs to the pipe's last command.** `pytest | tail -1; echo $?` reports `tail`.
- **A probe with a silent default proves nothing.** `systemctl show <unit> -p ExecMainStatus` prints 0 for a unit that does not exist. Try a probe on a name you know is wrong.
- **A long-running process** must have started after the code arrived: `ps -o lstart= -p <pid>` against `git reflog -1 --date=iso`.
- **Tests are the one probe that runs code**, so rule 6 does not hold for them. The test tripwire (`shift-left-testing/ISOLATION.md`), where a repo arms it, stops deletes and outbound connections; it does not stop overwrites. Run tests only where their writes cannot reach real data.

A probe that cannot run here (no auth, no network, another machine) is a blocker. So is a check the user or the harness declined: do not retry it another way. Say so under rule 4; do not substitute a weaker check and keep the stronger claim.

## The Evidence Line (rule 4)

One line under each claim. Paste the command and the output lines that decide it; do not paraphrase them. Claims that share a check share the line.

```
Tests pass (tested).
Evidence: `.venv/bin/pytest; echo "exit=$?"` → `403 passed, 1 warning in 4.56s`, `exit=0`; `.venv/bin/python -V` → `Python 3.12.13`

UNVERIFIED: the mirror sync. `git ls-remote mirror refs/heads/main` → `fatal: unable to access: Could not resolve host`; this machine is off the VPN.
```

Make the blocker checkable too: paste its error when there is one, and name the machine or the access when there is not. A line is true of the moment it was taken; name the commit or the time when a reader will re-run it later.

`/session-end` gathers the session's claims into a `## Claims` table in the session doc, with two counts below it: `Overclaims the user caught this session: N` and `Overclaims a reviewer caught this session: M`. `/session-end` defines what each counts; the format lives in `docs/session-doc-format.md`.

## What This Skill Is Not

- **Not a hedge.** `UNVERIFIED` names the blocker for a check you could not run. It is not a softener for a check you skipped. A report that marks every claim `UNVERIFIED` fails the kernel as surely as one that shows evidence for none.
- **Not a line under every sentence.** Evidence goes under what a reader will act on. Saying what you did not do ("I have not run the tests") is a true report, not an unverified claim.
- **Not proof.** A weak check honestly labeled passes the letter, and so does invented output. The line makes a claim checkable; a reader or a second agent re-running it does the checking.
- **Not a test strategy.** What to test and how lives in `shift-left-testing`. This skill starts where a result gets reported.
- **Not a gate, and not retroactive.** Nothing blocks; a missing line is a defect a reader or `grep` can find. Docs already written are records; leave them.

## Sidecar Files

- [EXAMPLES.md](EXAMPLES.md): seven before/after pairs, one per failure shape (the state overclaimed, the check skipped, the absence asserted, the stale number), and one clean report that needs nothing added. Read when a rule feels abstract.

## References

- `.claude/skills/shift-left-testing/ISOLATION.md`: the deterministic twin. A tripwire stops what a test must not do; this skill covers what a report must not say.
- `docs/session-doc-format.md`: the `## Claims` table.
- The writing-simple-and-direct skill, rule 6: hedge with numbers or not at all. An `Evidence:` line is that rule applied to success.

---

**Maintained by**: Verifying Claims Skill
**Version**: 1.0.0, first committed version: directory form with one sidecar (2026-10-01)
