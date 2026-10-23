# Session Start - Load Context

Load project context and prepare for a new development session.

## Step 1: Read Project Configuration

Read `config/project.yaml` - the central source of truth containing:
- Current phase and version
- Design pillars (content quality, source diversity, hybrid scoring, idempotency, extensibility)
- Build phases with status tracking
- Directory structure

## Step 1.5: Identify the Machine

    .venv/bin/python -m src.machine

Prints one line. Report it. If the host is not in the roster, say so and offer
to add it. Do not add it silently.

## Step 2: Check Current Phase

Read `config/project.yaml` build_phases section:
- Find the current active phase (status: "in_progress")
- Understand what's being built
- What's the deliverable for this phase?
- What phases are completed vs pending?

## Step 3: Load Recent Session

Find the newest session doc by name, `ls docs/sessions/*.md | sort | tail -1`, and read it to understand what was done last session. Names are date-first; modification times are not, and a fresh clone gives every file the same one. When that date has two docs, read both.

## Step 3.5: Check Task List

Read `docs/tasks.md` and report:
- The `## Focus` section at its head: the campaign's order, as intent
- Active tasks (count and list)
- Blocked tasks (count and reasons)
- Any stale tasks (no update in 3+ sessions)
- Suggest which active tasks align with today's work

## Step 3.6: Check Upstream Doctrine Updates

Check if `.claude/upstream-update.md` exists. If it does:
- Read and surface the contents to the user
- Flag it prominently: **"Upstream doctrine update available — review before proceeding"**
- Do NOT delete the file — the user decides when to act on it

`.claude/doctrine-delivered` beside it is the hub's delivery mark: the headings the hub has offered this repo, one per line. It is committed so a clone on another box knows what this repo has been sent. Leave it alone; the hub maintains it.

## Step 3.7: Read the Gap Register

Read `docs/gaps.md` and report each open gap with the decision it blocks. A gap is
something nobody can see yet; if today's work rests on one of them, say so before
starting.

## Step 4: Verify Health

Run these commands:
```bash
git fetch && git pull # Sync with remote before anything else
pytest                # Verify all tests pass
git status            # Check for uncommitted changes
git branch -v         # Current branch state
```

## Step 5: Summarize and Ready

Provide a brief summary. Each line ends with a tag saying where it came from, so a
reader can tell what was measured this turn from what a document held when it was
written:

- `[measured: <command>]`: run this turn; true now.
- `[identity: config/project.yaml]`: slow-moving; changes only when someone edits it.
- `[record: <file>, <date>]`: history; true as of that date, not now.
- `[intent: <file>]`: what is planned; not a state.
- `[register: <file>]`: maintained estimates and gaps.
- `[unchecked: <reason>]`: could not be measured this turn; give the reason and no value.

Never restate a count or a status from a record or the task list as if it were
current. If a decision today rests on it, run the command that measures it (Picture
Style rule 6) and report that instead.

1. **Machine**: Which box this is, from Step 1.5 `[measured: .venv/bin/python -m src.machine]`
2. **Version**: Current version `[identity: config/project.yaml]`
3. **Phase**: Current build phase and its deliverable `[identity: config/project.yaml]`
4. **Recent Work**: Last session summary `[record: <newest docs/sessions/ file by name>, <its date>]`
5. **Focus**: The campaign's next steps, in order `[intent: docs/tasks.md]`
6. **Tasks**: Active and blocked counts as the list stands, and the top priority items `[intent: docs/tasks.md]`
7. **Gaps**: Open gaps and the decision each blocks, from Step 3.7 `[register: docs/gaps.md]`
8. **Pending**: Key items remaining in current phase `[intent: docs/tasks.md]`
9. **Test Status**: All passing or failures? `[measured: .venv/bin/pytest]`
10. **Git State**: Branch, uncommitted changes? `[measured: git status, git branch -v]`

Then ask: **"What would you like to work on today?"**

---

## Quick Reference (Don't Read Unless Needed)

These docs exist for deeper dives - reference them when relevant:

| Topic | Location |
|-------|----------|
| Design philosophy | `docs/design/pillars.md` |
| Project roadmap | `docs/design/roadmap.md` |
| Pipeline config | `config/paperboy.yaml` |
| Phase tracking | `config/project.yaml` -> `build_phases:` section |
