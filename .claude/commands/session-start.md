# Session Start - Load Context

Load project context and prepare for a new development session.

## Step 1: Read Project Configuration

Read `config/project.yaml` - the central source of truth containing:
- Current phase and version
- Design pillars (content quality, source diversity, hybrid scoring, idempotency, extensibility)
- Build phases with status tracking
- Directory structure

## Step 2: Check Current Phase

Read `config/project.yaml` build_phases section:
- Find the current active phase (status: "in_progress")
- Understand what's being built
- What's the deliverable for this phase?
- What phases are completed vs pending?

## Step 3: Load Recent Session

Find and read the most recently modified file in `docs/sessions/` to understand what was done last session.

## Step 3.5: Check Task List

Read `docs/tasks.md` and report:
- Active tasks (count and list)
- Blocked tasks (count and reasons)
- Any stale tasks (no update in 3+ sessions)
- Suggest which active tasks align with today's work

## Step 4: Verify Health

Run these commands:
```bash
pytest                # Verify all tests pass
git status            # Check for uncommitted changes
git branch -v         # Current branch state
```

## Step 5: Summarize and Ready

Provide a brief summary:

1. **Version**: Current version from project.yaml
2. **Phase**: Current build phase and its deliverable
3. **Recent Work**: Last session summary
4. **Tasks**: Active count, blocked count, top priority items
5. **Pending**: Key items remaining in current phase
6. **Test Status**: All passing or failures?
7. **Git State**: Branch, uncommitted changes?

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
