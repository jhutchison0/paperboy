# Doctrine Behind the Picture

The skill borrows its vocabulary from two US Army publications, because they solved this
problem for a staff before any repo had it: ADP 5-0, *The Operations Process*, and ADP 6-0,
*Mission Command*. This file defines each term once, names its source, and says what it
means in a repo. A reader who carries the doctrine will recognise the lineage; a reader who
does not needs nothing beyond this page.

## What this skill is not

It is not intelligence preparation of the battlefield. IPB (ATP 2-01.3) describes the
enemy and the terrain: define the environment, evaluate the threat, predict its courses of
action. The picture this skill keeps is the friendly half of the staff's triad, *see
yourself, see the enemy, see the terrain*, and its doctrine is the running estimate and the
common operating picture, not IPB. A repo that wants the other two thirds (its dependencies,
its users, its hosting environment) extends the picture with modules; it does not change
the rules.

## The terms

| Term | Source | In doctrine | In a repo |
|---|---|---|---|
| common operating picture | ADP 6-0 | a single display of relevant information within a commander's area of interest, tailored to the user, based on common data shared by more than one command | one rendered display over the data every reader shares; views per consumer (agent, human) over one set of inputs; never a maintained paragraph |
| running estimate | ADP 5-0 | the continuous assessment of the current situation, used to determine whether the current operation is proceeding according to intent and whether planned future operations are supportable; each staff section keeps one | the maintained half of the picture: measurements with their ages, estimates with their bases, gaps; one per module, integrated by the picture |
| assessment | ADP 5-0 | the determination of progress toward accomplishing a task; it is a process, monitor then evaluate then recommend | the process. Never the name of a line |
| monitoring | ADP 5-0 | collecting relevant information, particularly that information addressed by the commander's critical information requirements | producing measurements: a command, a probe, a listing, a test run |
| evaluating | ADP 5-0 | using indicators to judge progress toward desired conditions | producing estimates: judgment applied to measurements |
| facts and assumptions | ADP 5-0, mission analysis | a fact is a verifiable statement; an assumption is a supposition about the current or future situation, assumed true in the absence of facts, kept only while necessary and likely, and replaced by facts as they arrive | a measurement and an estimate. An estimate names the observation that would replace it; one that nothing could replace is a gap |
| commander's critical information requirements | ADP 5-0 | the information the commander needs to make a decision, split into priority intelligence requirements (the enemy) and friendly force information requirements (ourselves) | the gap list. Each gap names the decision it blocks, which is what makes it a requirement rather than a curiosity |
| friendly force information requirements | ADP 5-0 | information the commander needs about friendly forces and supporting capabilities | the "see ourselves" view: hosts, schedules, coverage, counts, versions |
| collection management | ATP 2-01 | matching requirements to collectors, checking existing holdings before tasking new collection | rule 6: read the picture before you measure |
| negative reporting | field practice | "nothing to report" is reported, with what was observed and by whom; silence is not a report | rule 8: checked or unchecked, never blank, never clean |
| measure of performance, measure of effectiveness | ADP 5-0 | a MOP asks "are we doing things right?"; a MOE asks "are we doing the right things?" | an input line against an outcome line. A picture of inputs with every line green is not success; the header counts its outcome lines, and zero is a gap |
| current operations, future operations, plans | FM 6-0, the integrating cells | the fight now; the next phase, hours to days out; the operation after that | the three horizons: measured by command; maintained; intent with gates as predicates |
| decision point | ADP 5-0 | a point in time and space where the commander anticipates making a key decision | the surprise condition: the deviation from projection that demands attention |

## The convoy, which fixes the decay model

A convoy reports its position at 0330. The report is a measurement at 0330 and an estimate
every minute after, because the convoy is still moving. How good an estimate depends on
what the staff knows about the motion: heading, speed, the route. For twenty minutes the
projection answers "where are they" well enough to act on. For an hour it answers "where
will they be" well enough to plan a linkup. After that the uncertainty exceeds what either
decision can bear, and the picture shows the last known position with its age and a
widening ring, not a point.

The staff is not surprised that the 0330 position is wrong at 0331. It is surprised by a
report off the route, or by no report at the next scheduled time plus a tolerance. Those
two are the surprise conditions, and they are what the picture flags.

Three motions cover everything a repo has had to track:

| Motion | Example | Projection | Horizon | Surprise |
|---|---|---|---|---|
| constant until a change event | a roster, a config version, a branch | the last value, flat | until the change event, which the subject's identity detects | the value differs at the next measurement with no change event recorded |
| drifting in a known direction | a cumulative count, a disk's free space | the last value plus the known rate, with a widening interval | when the interval exceeds the decision's tolerance | a value outside the interval, or in the wrong direction |
| scheduled | a nightly job, a weekly reset | the next stamp expected at time T plus a tolerance | T plus the tolerance | no new stamp by then, or a stamp with a failure field |

A quantity whose motion is none of these is declared as such and gets a motion of its own
when a second quantity shares it. The three are in config, not in code, because the horizon
belongs to the decision that reads the quantity, and one quantity serves several decisions.

## The three horizons in a repo

| Horizon | Doctrine | What lives there | Refresh | Where |
|---|---|---|---|---|
| current operations | the current operations integrating cell | what is running now: jobs, timers, branches checked out, the newest stamp per host | by command, every time it is read; never stored as prose | a probe's output, rendered |
| running estimate | the staff running estimates, integrated into the COP | standing facts with ages and projections; estimates with bases; gaps | measurements regenerate on their schedule; estimates are reviewed against their horizon; gaps close by collection | the generated report, joined to the maintained gap and estimate registers |
| plans | the plans and future operations cells | intent; gates as predicates that name the command evaluating them | when intent changes | plans and the task list |

A record (a session doc, a review, an issue log) is history: it keeps every horizon as it
stood when written and is never rewritten, because rewriting it destroys the reasoning it
carries. The test, from the house rule that gates are predicates: a statement a reader would
act on today is a predicate or a dated measurement; a statement a reader would learn from is
prose.

## Why the picture is generated and the registers are authored

Doctrine draws the same line. The COP is built from common data by the systems that hold it;
the running estimate is the staff's judgment over that data. A staff officer does not retype
the position of every unit onto the map by hand each morning, and a staff officer's
assessment is not something a system can produce. In a repo: measurements come from
collectors on a schedule, and the rendered picture is never hand-edited (rule 1); estimates
and gaps are authored, tracked, and pinned by tests, because they are reasoning and reasoning
is history.
