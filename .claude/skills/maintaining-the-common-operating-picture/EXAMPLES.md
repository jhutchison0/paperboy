# The Cases That Earned Each Rule

Every rule in the kernel was paid for. These are the receipts, with the project's names
removed so the shape is what remains. Each case gives what happened, the rule it earned,
and what the picture shows instead.

## 1. The status paragraph in the config file

A repo's sole-source-of-truth config was 61.5 KB, and 57 KB of it was a `state:` block:
59 known issues and a 3,000-character `active_work` paragraph, each a hand-written sentence
about hosts, snapshots, schedules and counts. One sentence said the nightly timer ran a
checkout separate from the one being edited. On one box that was false, and the next session
built an assumption on it, because a false sentence in a config file reads exactly like a
true one.

**Rules 1 and 7.** The config zooms out to identity, scope, phases and paths, and links to
the picture by the command that renders it. A statement about a timer is current operations:
measured by `systemctl` or `crontab -l` when read, never stored as prose.

## 2. A measurement inside a gate

A wave's gate said "three hosts are still unswept." The sweep had completed the day before.
A session spent a day arguing an amendment to a gate that was already satisfied, reading the
stale line while the `[x]` sat thirteen lines above it. The correction written into the plan
was itself a dated fact that would age the same way.

**Rule 7.** A gate is a predicate that names the command evaluating it: `fleet-status
--target prod` reports `rostered but silent: (none)` and every host under 48 h. Reading the
plan re-evaluates the gate.

## 3. One number, two universes, then two shapes

Coverage was measured at 24.6% across two hosts, then 44.1% across five partitions once the
listing found three more. Both were correct inside their universes. Later the billing source
was understood to be a gateway monitor rather than an invoice, so 44.1% became an upper bound
with unmeasured slack. The number never changed; its universe changed once and its shape
changed once, and a line marked only "measured" could show neither.

**Rules 2 and 6.** A measurement carries its universe and its shape. The move from 24.6% to
44.1% is a change event: both lines kept, the earlier one marked "within universe: two
hosts," the newest shown with the widest universe. The move from point to bound is a
supersession in place (rule 4), not an edit.

## 4. A count measured four times in a day

A wave's acceptance criterion pinned a record count to a live directory. The count was
11,240, then 11,379, then 11,498, then 11,552 within the same day, while being measured.
Four numbers competed and none was the holding, because none named the subject it measured.

**Rule 2, subject identity; rule 6.** A measurement names the version of the thing it
measured. The fix was a fixed reference, the frozen snapshot's manifest; a count over a live
directory is an observation of a run, not a measurement of a quantity.

## 5. A suite counted 657 and 659

A gate reviewer counted the suite at 657 while the lead, committing tests on the same branch
during the review, counted 659. Both were right. Neither named the commit.

**Rule 2, subject identity; rule 6.** Two measurements that differ with subject named are a
change event, recorded as such. Two that differ with subject unnamed are not measurements.
Freeze the branch a gate reviews, and name the commit in the measurement.

## 6. Three run times, three code states

A nightly cycle on a tablet took 326 s, then 199 s after a change, then 55 s the next day.
The owner wrote "do not read it as a speedup until the probe says so." The three runs were
under three code states and two input sizes.

**Rules 2, 3 and 6.** The standing quantity "cycle time on a fixed input" had no measurement
at all. The picture holds three observations of runs, each with its subject and input, and a
gap: no probe on a fixed input exists. The quantity's motion is scheduled; the surprise is a
missing stamp, not a fast one.

## 7. A probe that publishes into its own universe

A design proposed that each host publish its status into the shared store the fleet probe
lists. The store's reader raised on any record type it did not declare and aborted the
whole listing. A new record type published by a newer clone would have blinded every older
clone's picture, in the loudest possible direction: not an under-report, a total refusal.

**`ADOPTION.md`, the generated half; rule 8.** A probe's record lands outside every probe's
universe, and a reader that meets an unknown record quarantines it and reports the count.

## 8. The never-empty list satisfied by `TBD`

A risk register's test asserted that its "suspected, not yet detectable" section was
non-empty. A single `- TBD` line passed it.

**Rule 5.** A gap names the collector that would close it and the decision it blocks. The
test asserts both fields, and counts unmarked lines only, so a superseded gap cannot keep
the section alive.

## 9. Three renderings of nothing as clean

A fetch that matched no object reported clean and exited 0. A view rendered `0 all-in
tokens across 0 days, 0 projects and 0 hosts` directly above its own banner reading "absent
is not zero," and exited 0. A mutation battery reported zero survivors three times in one
session, from three authors, and was wrong all three times.

**Rule 8.** A quantity renders checked with its fields or unchecked with a reason. Zero
rows is a refusal naming the path. A zero from the author of the change is unexamined until
someone else's probe says otherwise.

## 10. The convoy

A convoy's 0330 position, and what the staff does with it for the next hour, is in
`DOCTRINE.md`. It is the case that turned rule 3 from a staleness rule into a rule about
expectation: project from the last measurement and the motion, show the age, flag the
surprise.
