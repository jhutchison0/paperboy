# Adopting the Picture

Where each kind of line lives, what a repo rewrites, what an agent is now required to do,
and the first slice. A repo adopts in slices; the whole picture on day one is the way to
adopt none of it.

## Where things live

| Kind of line | Lives in | Tracked in git | Why |
|---|---|---|---|
| measurement | a generated report under a root named in config, outside every checkout | no | a report in git is a measurement that ages in a document nobody re-runs; generated means it carries today's stamp or does not exist |
| estimate, gap | a maintained register under `docs/`, pinned by tests | yes | reasoning is history; a scheduled job cannot write "nothing enumerates harnesses" |
| intent | plans and the task list | yes | a gate names the command that evaluates it; the task list is a work list, not a state |
| identity | the sole-source config: name, scope, phases, paths | yes | the slowest-moving facts; nothing in it should be re-measured |
| history | records: session docs, reviews, issue logs | yes | every horizon as it stood when written; never rewritten |
| the rendered picture | the report root, regenerated | no | the join of the above; never hand-edited |

The report root is a configured path **outside every checkout**. A scheduled probe runs
from one checkout and an agent reads another, and a root inside either leaves one of them
blind. No path under the report root appears in any orientation surface (README, CLAUDE.md,
CONTEXT.md, the task list): a reference-integrity check that resolves paths against the
repo cannot see it, so a stale one would be invisible rather than reported.

## The degenerate cases, stated so the skill is adoptable anywhere

- **One box.** The local render is the picture, and its header says `local picture, one
  box`. A shared store is how a picture becomes common; it is not a condition of adoption.
- **No observations yet** (a fresh clone, a CI runner, a checkout before its first probe).
  Every measured line renders `unchecked: no observation`, and the header counts them:
  `measurements: 0 of N present, newest: none`. The estimates and gaps still render, marked
  as what they are. A test renders the picture over an empty root and asserts no line reads
  clean.
- **A second clone or box.** Its first render comes from the shared store or renders
  unchecked. A picture is never copied from another box: the copy would carry the other
  box's subject identities under this box's name.
- **The shared store is unreachable.** The picture renders `UNVERIFIED: <blocker>` in its
  header and every line that depends on the store unchecked. It does not substitute what the
  task list says.

## The generated half: three rules for probes and their readers

1. **A probe reads; it never writes into the universe of any probe.** Its record lands
   outside every probe's enumeration (a different root, a different prefix, a different
   bucket), or the next probe counts its own output as a finding.
2. **A reader that meets a record it does not recognise quarantines it and reports the
   count.** It never aborts the listing. A newer writer must not blind an older reader; the
   failure to prevent is a total refusal that reads as an empty fleet.
3. **Two shapes, one punctuation.** Every declared quantity renders either
   `{checked: true, value, measured_at, collector, subject, universe, shape}` or
   `{checked: false, reason}` with no value key. A typed loader ships with the writer. The
   test disables one collector and asserts its line renders `unchecked (reason)` with no
   digit, in the same punctuation the checked line uses, so a negative assertion can fire.
   Cadence is config; the renderer compares age to the quantity's horizon and prints the
   verdict beside the age.

## The maintained half: supersession in a tracked table

A register is a markdown table or list, pinned by a test, and git keeps its history. "Never
overwrite" in that setting means: the superseded line keeps its place, gains a status mark
(`superseded 2026-10-04 by <pointer>`), and points at what replaced it, a measurement in
the picture or a newer line. Tests count unmarked lines only. A gap closes in one of two
ways, a collector now covers it (it becomes a probe row) or it was measured and found absent
(it becomes a record), and never by deletion.

## What a repo rewrites, in order

| Surface | Today | After adoption |
|---|---|---|
| the sole-source config | carries a `state:` block of prose about hosts, counts and schedules | identity only; one line naming the command that renders the picture and the report root's config key |
| session-start | reads the task list for state; runs health checks | renders the picture; each summary line tagged with its horizon, each measured line with age and verdict; the task list read for intent only |
| session-end | writes the session's state into the config's prose block | promotes the session's `observed` and `tested` claims into the picture's inputs; writes the record |
| status report (`/sitrep`) and task brief | re-derive state from the task list and a fresh test run | read the picture first; a fresh measurement only where rule 6 fires |
| project context (CONTEXT.md) | a Current State section in prose | a pointer to the picture; the section states what moves slowly enough to be prose |
| the reference-integrity check | resolves paths against the repo | lists the report root as a declared blind spot |
| plans | gates that state measurements | gates as predicates in one of the three forms |

Each rewrite is its own slice with its own test. The order above is the order of pain
relieved per line changed.

## Measurement requirements for agents

Ambient in CLAUDE.md as the Picture Style kernel. In full:

1. Before asserting the state of a host, a schedule, a count, a coverage figure or a
   version, read the picture. Cite the holding with its age, or say why rule 6 fires and
   measure.
2. A statement of state in any message, review or record is a measurement with its fields
   or an estimate with its range and basis. A number without either is a defect.
3. A probe an agent writes ships with its universe and its blind spot in its docstring, a
   gap-register row, and the two-shape test.
4. An agent never edits the rendered picture, and never writes a measurement into the
   config, a plan or the task list.
5. A gate an agent writes is a predicate that names its command. A measurement inside a gate
   is a review finding.

## The first slice

One session, any repo, no store, no probe, no cadence:

1. A gap register under `docs/` with at least one entry, each naming the collector that
   would close it and the decision it blocks.
2. One test that fails when the file is empty, when an entry lacks either field, or when
   only superseded entries remain.
3. If the config already keeps a known-issues list, move it in the same slice, each entry
   to its one home (a known unknown to the register, a defect to the task list, a decision
   to its record, an operating note to the command it governs), delete the key, and point
   the commands that wrote and read it at the register. Two homes for one list drift, and
   only one of them is tested. The hub did this on 2026-10-04: eight entries, five gaps.

That is rule 5 alone, and it is the piece that makes refusing confirmation bias something a
repo can fail rather than something it intends.

The second slice takes every existing status line out of the orientation surfaces, or
marks it as a measurement (with its fields) or an estimate (with its range) where it must
stay. Most lines leave: a count becomes the command that measures it, a focus paragraph
becomes intent at the head of the task list, a known unknown becomes a gap row. That is
where the config's prose block goes. The hub removed its block on 2026-10-04 and kept no
marked line. The third is one probe with the two-shape contract and a
render over an empty root. Do not start with the join or the shared store.
