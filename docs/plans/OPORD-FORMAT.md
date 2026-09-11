# OPORD Format

This is the template for Operations Orders in this repo. OPORDs live in `docs/plans/opord_<PROWORD>_<descriptive_name>.md`, usually inheriting the parent CONOP's proword. See `.claude/commands/task.md` for the escalation ladder and `CONOP-FORMAT.md` for the promotion gate.

An OPORD is the **execution form of a decided strategy**. It answers *how and in what order*, not *whether and which way*: those questions were closed in the CONOP. If you find yourself debating design decisions inside an OPORD, stop: the work belongs back at CONOP level.

The five-paragraph structure below is deliberately inherited from the doctrinal OPORD (Situation, Mission, Execution, Sustainment, Command & Signal). The paragraphs are the completeness checklist: an OPORD missing one is malformed, not stylistically different.

---

## When to Write an OPORD

Promote from an approved CONOP when **all** hold:

- CONOP design decisions are resolved
- Waves must run in a defined sequence
- Wave-by-wave completion needs tracked checkpoints

Every task inside an OPORD is specified at **TCS detail level**.

---

## Template

Copy into `docs/plans/opord_<PROWORD>_<slug>.md`.

```markdown
# OPORD <PROWORD> — <Descriptive Name>

**Status**: Active | Complete | Aborted
**Date**: YYYY-MM-DD
**Lead**: <name>
**Parent CONOP**: <link>

---

## 1. Situation

The delta since the CONOP was approved: what changed, what was
learned, what assumptions were invalidated. Reference the parent
CONOP's Situation rather than restating it. If nothing changed,
say so in one line.

---

## 2. Mission

The mission statement, restated final. One sentence, "in order to"
clause mandatory. If it differs from the CONOP's mission, explain
why in Situation.

---

## 3. Execution

### Commander's Intent
- **Purpose**: why this operation exists (expanded "in order to")
- **Key tasks**: the 2–4 things that must happen for success,
  independent of how
- **End state**: what done looks like in code, tests, docs, and config

Intent is the escape hatch when the plan meets reality: when a wave's
specified steps fail or become impossible, agents optimize for intent
and report, rather than improvising new strategy.

### Concept of Operations
The wave sequence in prose: what runs when, what depends on what,
where the checkpoints sit. A Mermaid diagram is preferred over ASCII
when the dependency graph is non-linear.

**First-contact rule**: the earliest feasible checkpoint exercises
the plan's riskiest assumption against the real target: real
payloads, real hardware, real platform, real data. Simulator-only
confidence defers every deployment discovery to the end, where they
all land at once.

### Wave N — <Name>
- **Team**: template from `.claude/teams/`, with modifications
- **Preconditions**: what must be true before this wave launches,
  including **baseline-health checks** ahead of expensive steps; do
  not run a costly matrix against a baseline a diagnostic has
  already flagged as degenerate
- **Tasks**: at TCS detail level

  | Task | Condition | Standard |
  |------|-----------|----------|
  |      |           |          |

- **Exit criterion**: the shared condition that closes the wave
- **Checkpoint**: a **commit-gate with a named owner**; the wave is
  not closed until its verifying commit exists and the owner has
  checked it (test counts, review findings addressed, artifacts
  written). Checkpoints that are prose rather than commit-gates are
  how a six-wave feature arrives as one uncommitted blob.

### Coordinating Instructions
- **Report-immediately conditions**: the CCIR of this operation.
  Inherit the escalation paths in `.claude/README.md` (agent
  deadlock without evidence, >5 files, destructive operations,
  Critical review findings) and add any operation-specific triggers.
  Always included: **a mid-wave finding that invalidates a wave's
  precondition**: halt the wave and report. A live diagnostic
  outranks the plan's momentum.
- **Branches**: pre-decided responses to anticipated contingencies
  ("if Wave 2 tests reveal the schema is wrong, revert to CONOP").
- **Standing constraints**: shift-left testing, scope matrix, and
  branching policy apply to all waves without restatement.

---

## 4. Sustainment

What keeps execution running: venv and dependency requirements,
fixtures and test data, config keys, API access, model assignments
for pinned agents. Anything an agent needs that is not code it
writes.

---

## 5. Command & Signal

- **Decision authority**: what the lead decides vs what agents
  decide on intent. Default: agents decide within a wave's TCS
  boundaries; the lead decides at checkpoints and on any
  report-immediately condition.
- **Reporting**: where artifacts land (reviews to `docs/reviews/`,
  proposals to `docs/plans/`, status via `/sitrep`, tasks in
  `docs/tasks.md`).
- **Session boundaries**: which waves are expected to span sessions;
  `/session-end` and `/session-start` carry state across.

---

## Completion

Closing an OPORD requires: final `/task backbrief`, session doc per
`docs/session-doc-format.md`, tasks moved to Completed, Status set
to Complete, the parent CONOP's status flipped to Superseded (or
its annotation verified), every plan checklist ticked or explicitly
annotated (a stale board that still reads "in progress" costs a
future session a status rediscovery) and the proword released for
reuse.
```

---

## Status Values

- **Active** — execution in progress.
- **Complete** — end state achieved, completion checklist done.
- **Aborted** — execution stopped short; the closing session doc records why. An aborted OPORD's proword is released, but reuse is discouraged for a while: the association lingers.

---

## The Five Paragraphs Are the Checklist

A reviewer (human or `code-reviewer`) can validate an OPORD mechanically: five paragraphs present, intent has purpose/key-tasks/end-state, every task carries a TCS row, every wave has an exit criterion and checkpoint, report-immediately conditions listed. This is the property that makes the format worth its ceremony: completeness is checkable before execution starts, which is shift-left applied to planning itself.

---

## Sources

- FM 5-0 / ADP 5-0 — the five-paragraph OPORD, commander's intent, CCIR.
- `.claude/README.md` — escalation paths inherited as baseline report-immediately conditions.
- `docs/adr/ADR-FORMAT.md` — the house pattern for pinned document schemas.
- `docs/reviews/20260717_planning_retrospective_*.md` — the four-repo retrospective behind the first-contact rule, commit-gate checkpoints, baseline-health preconditions, and the mid-wave halt condition.
