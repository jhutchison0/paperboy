# ENFORCEMENT — How Shift-Left-Testing Is Made to Stick

Sidecar to `SKILL.md`. Documents the deterministic mechanisms layered on top of the (probabilistic) skill itself, so the discipline survives contact with agents that may not read it.

## The Problem This Sidecar Solves

`VERTICAL-SLICING.md` states the discipline: write a failing test, then the minimum implementation that passes it, then move to the next slice. A skill describes; it does not enforce. Whether any agent invokes the skill on any given turn is decided by the model: probabilistic, not deterministic. The user framing: *"claude dice."* The dice often come up favorable. Not always. We layer mechanisms that fire on every relevant action so the discipline does not depend on a single roll.

## Enforcement Gradient

Doctrine is enforced at multiple layers. Each is either probabilistic or deterministic, and either blocking or non-blocking.

| # | Layer | Determinism | Blocking? | Source |
|---|---|---|---|---|
| 1 | The skill itself (`VERTICAL-SLICING.md`) | Probabilistic | No | Agent reads when relevant |
| 2 | `CLAUDE.md` Development Principle | Probabilistic | No | Agent reads at session start |
| 3 | `python-prototyper.md` workflow | Probabilistic | No | Agent definition prescribes order |
| 4 | **PostToolUse audit hook** | **Deterministic** | **No (logs + warns)** | Harness runs after every Write/Edit |
| 5 | Stop hook diff audit | Deterministic | No (logs + warns) | Harness runs at end of every turn |
| 6 | PreToolUse block hook | Deterministic | Yes (blocks) | Harness refuses Write/Edit before condition met |

Layers 1–4 are currently active in this repo. Layer 5 is a candidate for the next iteration. **Layer 6 is intentionally not configured** (see "Why not hard blocks" below).

## What the Audit Hook Does (Layer 4)

The PostToolUse hook at `.claude/hooks/post-tool-shift-left-audit.sh` fires after every `Write` or `Edit` tool call. It:

1. Exits silently for tools other than `Write` / `Edit`.
2. Exits silently for paths outside `src/*.py` (paperboy uses a flat `src/` layout — no `src/paperboy/` subdirectory).
3. Exits silently for `__init__.py`, `conftest.py`, and any file already matching `test_*.py` / `*_test.py`.
4. Infers the test partner: `tests/**/test_<basename>.py` via `find`; when that misses, any `tests/**/test_*.py` that imports the module (`from src.mod import`, `import src.mod`, or `from src import mod`) counts, so feature-named suites are partners too.
5. If the test partner does not exist, appends a `MISSING_TEST` line to `.claude/audits/shift-left-violations.log` and writes a one-line warning to stderr (which the harness surfaces back to the agent in the tool result).
6. If the test partner exists, appends an `OK_TEST_EXISTS` line for each match.

The hook never blocks. Output is evidence, not friction. The script `set -uo pipefail` (deliberately not `-e`) and always `exit 0` so a transient failure cannot suppress the tool call.

## Why Not Hard Blocks (Layer 6)

A `PreToolUse` hook on `Write|Edit` to `src/*.py` that refused the tool call when no test partner existed would be the strictest form of enforcement. It was MAUT-evaluated against soft-deterministic alternatives in `docs/reviews/20260519_pass4_enforcement_maut.md` and lost on three counts:

- **False positives**: legitimate refactors, renames, doc-string fixes, and exploratory prototyping have no immediate test-first need. A hard block would punish every one of them.
- **Bypass cost is too low**: an agent that wants to route around the block can write to a different path, then move the file. Or write to a tests file first as a stub. The friction lands on legitimate work; the workaround for bad behavior is trivial.
- **Educational vs punitive**: the goal is to teach the discipline, not to punish violations. Soft-deterministic mechanisms produce evidence (`MISSING_TEST` count over time) that informs a later decision about whether escalation is needed; hard blocks produce only resistance.

If the audit log shows persistent violations after the soft mechanism has been in place long enough to be unambiguous, the answer is to convene a review of the violations and decide whether to escalate or whether the violations are legitimate exceptions. The default direction is **add more evidence collection, not more refusal**.

## What the Hook Catches and What It Misses

**Catches**:
- New production code in `src/` with no test partner at all.
- Code that has fallen out of sync (test deleted, impl remains).
- Edits to legacy untested code (surfaces the existing gap without requiring a separate audit pass).

**Misses**:
- **Temporal vertical-slicing violations**: writing all tests first, then all impl. Both have test partners; the temporal discipline gap is invisible to a name-existence check.
- Test stubs that exist but contain no assertions.
- Tests outside `tests/`, or tests that reach the module without importing it by name (a fixture that imports it, an app factory that mounts it). The inference is name match, then import grep, nothing deeper.
- Commits made outside Claude Code (CI checks would catch some of these; see `CI.md`).
- Tests that exist but don't actually test the new code (e.g., a stale `test_foo.py` that doesn't cover the new `foo.bar()` function).

The "misses" list is what the (probabilistic) skill is for. Hooks reduce dependence on the dice; they do not eliminate it.

## Reading the Audit Log

```bash
# Count violations by type
grep -c MISSING_TEST .claude/audits/shift-left-violations.log
grep -c OK_TEST_EXISTS .claude/audits/shift-left-violations.log

# Recent violations (last 20)
grep MISSING_TEST .claude/audits/shift-left-violations.log | tail -20

# Per-file violation count
grep MISSING_TEST .claude/audits/shift-left-violations.log \
  | sed 's/.*file=\([^ ]*\).*/\1/' \
  | sort | uniq -c | sort -rn
```

The log is append-only. It is not committed (gitignore via `.claude/audits/`). Rotate or truncate manually if it grows unwieldy.

## When to Escalate to Hard Blocks (Layer 6)

Triggers that warrant a re-evaluation:

- More than 20 `MISSING_TEST` events in a single month in a single repo.
- A pattern where the same file appears repeatedly in `MISSING_TEST` over multiple sessions.
- A code-review consensus that the audit log shows discipline drift, not legitimate exceptions.

The re-evaluation should re-run the MAUT in `docs/reviews/20260519_pass4_enforcement_maut.md` with updated weights and write a new ADR if the recommendation flips.

## Propagation

This sidecar propagates downstream as part of the `shift-left-testing` skill bundle. The hook script (`.claude/hooks/post-tool-shift-left-audit.sh`) and the `settings.json` snippet propagate alongside as **template-copy** artifacts. Downstream repos may customize the `src/<project>/` and `tests/` path patterns inside the hook script to match their layout; the audit log path and behavior should remain unchanged.

The propagation entry must call out that adopting this enforcement layer is the consumer repo's choice: a `settings.local.json` override can disable the hook per developer without modifying the propagated `settings.json`.

## See Also

- [`SKILL.md`](SKILL.md) — entry point.
- [`VERTICAL-SLICING.md`](VERTICAL-SLICING.md) — the discipline this enforces.
- [`ANTIPATTERNS.md`](ANTIPATTERNS.md) — what hooks try to prevent.
- `../../hooks/post-tool-shift-left-audit.sh` — the audit script source.
- `../../settings.json` — hook configuration.
- `../../../docs/reviews/20260519_pass4_enforcement_maut.md` — MAUT that selected this design (A5).
- `../../../docs/reviews/20260519_pass4_enforcement_grill.md` — alternative designs considered.
