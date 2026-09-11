# Preflight: check the machine before it writes

`scripts/lake_preflight.py` answers six questions. Each one exists because
someone already paid for the answer.

```bash
python scripts/lake_preflight.py --target dev
python scripts/lake_preflight.py --target prod --fetch --strict \
  --leg "stage1 publish --lake-profile prod" \
  --leg "stage2 fetch --lake-profile prod"
```

Exit 0 clean, 1 on any FAIL. `--strict` makes a WARN fatal.

## The checks

| Check | Asks | Fails when |
|---|---|---|
| reference repo | Is the lakehouse SOP on this disk? | No path in the roster for this host, or nothing there |
| reference currency | How old is the local clone? | Never fails; warns past 30 days |
| target | Which tier is this writing to? | No target given, or a name that is not a target |
| leg threading | Does every process carry the target? | Any declared leg misses it |
| environment | Are credentials present? | Neither namespace is set |
| local data | Is bulk data squatting on this box? | Never fails; warns with a byte count |

## What each check cannot prove

State this plainly, because a green line invites more confidence than it earned.

- **reference currency reads the local clone only.** Without `--fetch` it cannot
  know whether origin has moved. A repo committed yesterday and forty commits
  behind reports one day old, and is right about the question it asked. During
  this skill's authoring, launch-control's own working tree sat 102 commits
  behind its origin while looking perfectly fresh.
- **environment checks presence, never reachability.** It opens no socket. A
  PASS means a client would find something to try, not that the lake is up, not
  that the credentials are valid, and not that they grant the prefix you want.
- **leg threading reads the strings you hand it.** It cannot discover processes
  you did not declare. Zero legs is a WARN, not a PASS, because "nothing was
  checked" and "nothing was wrong" must not print the same.
- **local data matches file extensions.** A 40 GB directory of `.bin` is
  invisible to it.

## A conservative gate is still a wrong gate

The rule this script is written against, learned downstream and worth stating
before anyone adds a check:

> When a preflight exists to predict what a run will do, its acceptance logic
> must mirror the run's, and that equivalence should be pinned by a test that
> reads the real function.

The failure that produced it: a probe asked a stricter question than the code it
gated and cut a batch from 34 runs to 27 on false negatives. Nothing errored.
The work simply did not happen.

So before adding a check, ask what a false "no" costs. If the answer is "work
silently does not happen," fail-safe reasoning does not apply, and a gate that
blocks good runs is worse than no gate. Prefer a WARN you can read over a FAIL
you will learn to bypass.

## Adding a check

1. Write the failing test first, in `tests/unit/test_lake_preflight.py`.
2. Return a `Result(name, status, detail)`. The detail is a sentence an operator
   can act on, not a restatement of the status.
3. If it touches the network, put it behind a flag and default it off.
4. Say in the detail what the check did not verify.
