---
name: maintaining-the-common-operating-picture
description: House rule for how a repo knows its own state. Two ideas and eight kernel rules, with the vocabulary (measurement, estimate, projection, horizon, surprise, gap) defined once. Mark every line as a measurement or an estimate; place every line by how it moves. Use when writing or reading any statement about what is true now, before measuring something that may already be measured, when designing a probe or a status report, and when deciding where a fact lives.
version: "0.1.2"
---

# Maintaining the Common Operating Picture

A statement about a repo's own state goes stale the moment it is written, and a stale
sentence reads exactly like a fresh one. This skill is how a repo keeps a picture of itself
that a reader, human or agent, can trust at a glance: what was measured, when, by what, how
it is expected to have moved since, and what nobody can see yet. The product is a common
operating picture: one display over the data every reader shares, never a paragraph
somebody maintains.

It counters two failures, and they are symmetric. An estimate used where a measurement was
needed: a plan said three hosts were unswept, the sweep was done, and a day went to arguing
a gate already met. A measurement made where one already existed: one quantity measured
four times in a day with no reference run, so four numbers competed and none was the
holding.

Scope, stated once. `verifying-claims` governs a claim about what this turn changed; this
skill governs standing facts this turn did not touch, and where they live. `shift-left-testing`
governs how code is tested; this skill governs how the repo's state is known.

**Philosophy**: *Mark where every line came from; place every line by how it moves.*

## When to Use

- Writing or reading any statement about what is true now: a host, a count, a schedule, a
  coverage figure, a version, a branch
- Before measuring anything, to check whether the picture already holds it
- Designing a probe, a status document, a status command, or the session-start summary
- Deciding where a fact lives: config, a plan, a task list, a record, or a generated report
- Reviewing a plan whose gate states a measurement instead of naming a command

## Vocabulary

Defined once, here and in `DOCTRINE.md`. A document that uses one of these words for
something else is wrong, not the glossary.

| Term | Means | Never means |
|---|---|---|
| assessment | the process: monitor, evaluate, recommend | a line in the picture |
| measurement | a line a collector produced at a time, carrying subject, universe and shape | a number without those fields |
| estimate | a line produced by judgment or projection, carrying a range and a basis | a point |
| projection | the estimate the picture derives from the last measurement and the quantity's motion | a measurement |
| horizon | the age at which a projection no longer serves the decision at hand | a fixed cadence |
| surprise | a measurement outside its projection, or an absence at the scheduled time | an error |
| gap | a known unknown, with the collector that would close it and the decision it blocks | a to-do |
| collector | whatever produces measurements: a command, a probe, a test run, a listing | a person's recollection |
| universe | what a collector enumerates; it is structurally blind to everything outside | the whole system |
| picture | the rendered join of every module, generated, never hand-edited | a status paragraph |

## The Kernel

Eight rules. The ambient copy lives in CLAUDE.md.

1. **The rendered picture is never hand-edited; its inputs may be.** It is one display over
   the data every reader shares. A paragraph someone maintains is an estimate wearing a
   measurement's clothes.
2. **Every line is a measurement or an estimate, and an input or an outcome, and says
   which.** A measurement carries its value, time, collector, the identity of what was
   measured, the universe searched, and its shape: exact, a bound with its direction, or an
   interval. An estimate carries a range, never a bare point, its basis, and the observation
   that would prove it wrong.
3. **Every quantity declares how it moves and what would be a surprise.** Constant until a
   change event, drifting in a known direction, or scheduled. The picture shows the last
   measurement, its age, and the projection from the two, and flags a surprise. A
   measurement past its horizon stays a measurement, marked stale, never relabelled an
   estimate.
4. **Supersede in place, never overwrite.** The old line keeps its place with a status mark
   and a pointer to what replaced it. Tests count unmarked lines only, so a superseded line
   cannot satisfy a never-empty rule.
5. **Gaps are listed, each naming its collector and the decision it blocks, and the list is
   never empty.** An empty gap list is a finding about the staff, not evidence the system is
   clean. An estimate no collector could falsify is a gap, not an estimate.
6. **Read the picture before you measure or assert state.** Re-measure when the projection's
   uncertainty exceeds what the decision needs, when the subject or the universe changed, or
   when a measurement surprised the projection; never for comfort. Two measurements that
   disagree with subject and universe named are a change event: record both, name the cause.
7. **One horizon per line, not per document.** Current operations are measured by command.
   The running estimate is maintained. Plans are intent, and a plan's gate names the command
   that evaluates it. A record (a session doc, a review, an issue log) keeps every horizon
   and is never rewritten.
8. **Never report clean.** Every declared quantity renders checked, with its fields, or
   unchecked, with a reason and no value, in one shape. A picture with no observations says
   so in its header. A row of zeros is the most reassuring rendering of the least
   informative fact.

## The two ideas behind the eight

**Provenance** (rules 2, 3, 4, 8): a line says where it came from, when, by what, over what
universe, how it is expected to have moved, and what replaced it. A reader never has to
parse prose to know whether a number was measured or guessed, or how old it is.

**Placement by motion** (rules 1 and 7, and the layout in `ADOPTION.md`): a fact lives with
things that age at its rate. A measured fact lives in a generated report with a time on it.
An estimate lives in a maintained document with a basis and a replacing observation. Intent
lives in a plan. History lives in a record. A document that mixes them ages at the rate of
its fastest line, and its slowest line then reads as stale or its fastest reads as current.

Rules 5 and 6 are what a reader does with the picture: name what it cannot show, and
consult it before adding to it.

## Procedure

**For a statement you are about to write or read.** Ask which horizon it belongs to. If a
reader would act on it today, it is a measurement or an estimate and must carry the fields
in rule 2; if it is history, it is prose and stays where it is. Then ask whether the picture
already holds it (rule 6). If it does and nothing in rule 6 has fired, cite the holding with
its age. If it does not, measure, and the measurement enters the picture through its module.

**For a probe.** Declare its universe in its own docstring, and the one thing it is
structurally blind to. It reads; it never writes into the universe of any probe, including
its own. Its output takes the two-shape contract of rule 8: `checked` with every field, or
`unchecked` with a reason and no value key, same punctuation either way, so a test can assert
the absence by name. Ship it with a gap-register row (rule 5) and a test that fails when the
probe disappears or the row does.

**For a quantity entering the picture.** Declare in config, not in code: its motion
(constant, drifting, scheduled), its horizon per decision that reads it, and its surprise
condition. The renderer compares age to horizon and prints the verdict beside the age.

**For a plan.** A gate is a predicate in one of three forms, in order of preference:
executable (the command and the output that satisfies it), observable (the artifact and the
property, when no command exists), or blocked (nothing can evaluate it; name the instrument
that would have to exist, which is a gap by rule 5). A measurement inside a gate is a
defect: it started ageing the moment the plan was written.

**For the session-start summary.** It is the picture's human view. Each line is tagged with
its horizon, and each measured line carries its age and its verdict. A line the renderer
could not produce renders `unchecked` with the blocker, never blank and never copied from
the previous session.

## What makes this skill decorative

Each of these has been observed in a repo that had the rules on paper.

- The mark exists but nobody reads it: agents copy the line and drop the mark.
- Marks are applied by the author after the fact, to a line already acted on.
- Every estimate names a replacing observation that is never collected, so rule 4 holds on
  paper and nothing ever moves.
- The gap list is padded with trivia to stay non-empty. Rule 5's two required fields are the
  defence: a gap with no collector and no blocked decision is not a gap.
- The picture renders but no command reads it; the reporting commands stay sources.
- The skill's own `EXAMPLES.md` is the only place the marks appear.

## Success criterion

**OPEN.** The shape is `traversing-the-knowledge-base`'s five-session bet, and the window
opens when the first repo renders a picture through this skill; the numbers are set then,
not now. The candidate measures:

- **M1 uptake**: at least 3 of 5 session docs carry a `COP:` line naming the picture command
  run, the newest measurement's age, and the count of `unchecked` or stale lines.
- **M2 integrity**: the join test stays green and each run's result is recorded: a picture
  with no observations renders no clean line; the gap list is non-empty with both fields; every
  estimate names a replacing observation.
- **M3 value**: at least one case where the picture prevented either failure in the opening
  paragraph, verified at window close by someone other than the line's author.

The outcome matrix and the human decision each cell triggers are copied from that skill
once the window opens. No cell triggers automatically.

## Sidecar Files

- `DOCTRINE.md`: the terms, their doctrinal sources, the three horizons, the convoy
  example that fixes the decay model, and what this skill is not.
- `EXAMPLES.md`: the cases that earned each rule, with the specifics removed.
- `ADOPTION.md`: where things live, the degenerate cases (one box, fresh clone, no
  observations), the commands and documents a repo rewrites, the first slice, and the
  measurement requirements for agents.

## Version History

- **0.1.2** (2026-10-04): `ADOPTION.md`'s second slice says most status lines leave the
  orientation surfaces rather than gain marks, as the hub's slice 2 found: every one it had
  moved to a command, the task list's Focus section, or the gap register.
- **0.1.1** (2026-10-04): `ADOPTION.md`'s first slice moves an existing known-issues list
  into the register in the same slice, so the list has one home. Learned from the hub's own
  first slice the same day (`docs/gaps.md`), whose gate review also found that a filler
  such as `None exists.` passed the two-field check until punctuation was stripped.
- **0.1.0** (2026-10-04): Draft. Kernel, vocabulary and procedure after a three-agent
  pre-draft review (proposer, code-reviewer, decision-scientist) of an earlier eight-rule
  draft; the decay model from the owner's convoy example. Success criterion open.
