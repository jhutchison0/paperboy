# Task — Project Work Tracker

Manage the project task list and escalate work items through the planning framework.

**Military origin**: Task Organization — structuring work into manageable units with clear ownership, conditions, and standards. Small work stays a task. Complex work gets promoted to a plan.

## How To Use

Read the current task file and the user's request, then take the appropriate action.

**Current tasks**:
Read `docs/tasks.md` to see all current tasks.

**User's request**: $ARGUMENTS

## Subcommands

Interpret the user's arguments as one of these actions:

### `add <description>` — Add a new task
- Add to the appropriate section (Active, or under a CONOP heading if specified)
- Assign a priority: `P1` (do now), `P2` (do soon), `P3` (backlog)
- If no priority given, default to `P2`
- Format: `- [ ] [P2] Description — owner: unassigned`

### `list` or no arguments — Show current tasks
- Read and display `docs/tasks.md`
- Summarize: X active, Y blocked, Z completed recently
- Flag any tasks that look stale (no update in 3+ sessions)

### `done <task description or number>` — Complete a task
- Move from Active/Blocked to Completed with today's date
- Format: `- [x] 2026-03-11: Description`

### `block <task> — <reason>` — Mark a task as blocked
- Move to Blocked section with the blocking reason
- Format: `- [ ] [P2] Description — blocked: reason`

### `unblock <task>` — Move a blocked task back to Active

### `promote <task>` — Escalate a task to a planning document
- Evaluate the task against the Escalation Ladder (below)
- Recommend the appropriate document type
- If the user agrees, create a skeleton document in `docs/plans/`
- Link the task to the new document

### `update <task> — <note>` — Add a status note to a task
- Append a brief status update inline

### `assign <task> — <owner>` — Assign ownership
- Owner can be a person or an agent name from the roster

### `brief` or `backbrief` — Generate a backbrief
- Summarize what's been accomplished since last session
- List open decisions and blocked items
- Recommend next actions
- Format follows military backbrief: situation, actions taken, results, recommendations

### `plan <task>` — Get a planning recommendation
- Evaluate the task's complexity
- Recommend: stay as task, promote to TCS/CONOP/OPORD
- Suggest team composition from the agent roster
- Identify decision points

## Escalation Ladder

Use this to determine when work should be promoted from one level to the next:

### Level 1: Task (single item in `docs/tasks.md`)
**When**: One person, one session, clear action.
- "Fix the import error in config.py"
- "Add a new RSS feed to paperboy.yaml"
- "Update MEMORY.md with new file paths"

**Indicators it should stay a Task**:
- Can explain in one sentence
- No design decisions needed
- Touches 1-3 files
- No dependencies on other work

### Level 2: TCS — Task, Condition, Standard
**When**: Multi-step task with measurable acceptance criteria. Still scoped to one component.
- "Implement HuggingFace Daily Papers sourcer with error handling, deduplication, and rate limit tests"
- "Add --backend flag to CLI with backward compatibility"

TCS is also the **universal task specification unit** — every task within a CONOP or OPORD is written at TCS detail level. The document type escalates the frame; the task granularity stays consistent.

**Promote from Task when**:
- Needs explicit pass/fail criteria (not just "done")
- Multiple files across 2+ directories
- Has preconditions that must be verified
- Someone else needs to validate it
- A template exists: use `/implement-source` for new content sources

**Format**: Add TCS table to the task entry or create a standalone TCS doc:
```
| Task | Condition | Standard |
|------|-----------|----------|
| Fetch HuggingFace papers | Given valid API response with 10 papers | Returns list[Paper] with all fields populated |
| Handle network failure | Given timeout or HTTP 500 | Returns empty list, logs warning, pipeline continues |
```

**Team**: Usually 1-2 agents (e.g., `python-prototyper` + `test-runner`)

### Level 3: CONOP — Concept of Operations
**When**: Multi-wave plan with design decisions, parallel tracks, or multiple agents.
- "Dual-backend architecture — AgentRunner + SDK fallback + CLI integration + validation"
- "Multi-paper briefing — selection, thematic grouping, comparative prompts"

**Promote from TCS when**:
- Multiple parallel waves of work
- Design decisions that need to be made before coding
- Touches 4+ components or introduces new architecture
- Needs a team of 3+ agents
- Has open questions that affect implementation
- Will span multiple sessions

Every task within the CONOP is specified at TCS detail level.

**Format**: `docs/plans/conop_NNN_descriptive_name.md` following the template:
1. SITUATION (background, terrain, constraints, assumptions)
2. MISSION (requirements, TCS table, acceptable risk)
3. EXECUTION (waves, wave details, concept diagram)
4. LOGISTICS (file ownership, data flow)
5. COMMAND AND SIGNAL (decision points, open questions)

**Team**: 3-5 agents. Use team templates from `.claude/teams/`:
- `source-development.md` for ArXiv/RSS sourcing work
- `pipeline-feature.md` for pipeline features and CLI
- `briefing-quality.md` for distillation and output quality

### Level 4: OPORD — Operations Order
**When**: Strategy is decided (CONOP approved), now executing a sequential multi-wave operation.
- "Execute Wave 3 automation: cron setup → deduplication → output rotation → notification → backfill"

**Promote from CONOP when**:
- CONOP's design decisions are resolved
- Waves must run in defined sequence
- External dependencies exist (hardware, data, human input)
- Resource costs are significant (GPU time, manual review)
- Need to track wave-by-wave completion with checkpoints

Every task within the OPORD is specified at TCS detail level.

**Format**: `docs/plans/opord_NNN_descriptive_name.md` — tighter execution focus:
- Waves run sequentially: Wave 1 → Wave 2 → Wave 3
- Each wave has a checkpoint/gate before proceeding
- Explicit resource requirements and timelines

**Team**: Full team from the relevant template, with lead coordinating wave transitions.

## Terminology: Phases vs Waves

- **Phase** — Strategic roadmap milestone (e.g., `build_phases` in `project.yaml`). Phases live outside CONOPs and OPORDs.
- **Wave** — Tactical parallel execution unit within a CONOP or OPORD. Agent teams deploy in waves.

A campaign-level OPORD may contain phases of waves, but this is deliberate and infrequent. Default to waves within orders; reserve phases for the roadmap.

## Decision Point Guidance

When evaluating whether to promote, ask:

```
1. Can I explain this in one sentence?          → Yes: Task
2. Do I need pass/fail criteria?                 → Yes: TCS minimum
3. Are there design decisions to make?           → Yes: CONOP
4. Are there multiple parallel tracks?           → Yes: CONOP
5. Is the strategy decided, just need to execute? → Yes: OPORD
6. Does it span multiple sessions?               → Yes: CONOP or OPORD
7. Does it need 3+ agents?                       → Yes: CONOP with team template
```

## Team Recommendations

When promoting or planning, recommend teams from the roster:

| Work Domain | Recommended Template | Core Agents |
|---|---|---|
| New content source | `source-development` | content-curator + test-runner + code-reviewer (+ proposer for design-heavy sources) |
| Scoring/selection tuning | `source-development` | content-curator + test-runner + code-reviewer |
| Pipeline feature / CLI | `pipeline-feature` | python-prototyper + test-runner + code-reviewer |
| Briefing quality / prompts | `briefing-quality` | distiller-dev + test-runner + pipeline-sme |
| New pipeline stage | `pipeline-feature` | python-prototyper + test-runner + code-reviewer + pipeline-sme + proposer |
| Cross-cutting (multi-domain) | `pipeline-feature` + `source-development` | python-prototyper + content-curator + test-runner + code-reviewer + proposer |
| Bug fix (any domain) | `bug-fix` | python-prototyper + test-runner |
| Quality audit (no code changes) | `code-review` | code-reviewer + test-runner |

**Scaling rule**:
- Mechanical fix (3 files or fewer): 2 agents (developer + tester)
- Schema/API change: 3 agents (+ reviewer)
- New subsystem: 4 agents (+ pipeline-sme + proposer for design exploration)
- Full CONOP: 5+ agents (+ pipeline-sme for mission alignment + proposer for design decisions)

## Backbrief Format

When `/task brief` or `/task backbrief` is called:

```
BACKBRIEF — [Date]
==================

SITUATION:
  Active tasks: X
  Blocked tasks: Y
  Completed this session: Z

ACTIONS TAKEN:
  - [What was done]
  - [What was done]

RESULTS:
  - [Outcome]
  - [Test status]

OPEN DECISIONS:
  - [Decision needed] — affects: [what]
  - [Decision needed] — affects: [what]

BLOCKED ITEMS:
  - [Task] — blocked by: [reason]

RECOMMENDATIONS:
  - Next priority: [task]
  - Consider promoting: [task] → [CONOP/TCS]
  - Team needed: [template] for [work]
```

## File Location

Task list: `docs/tasks.md`

If the file doesn't exist, create it with the initial template structure.
