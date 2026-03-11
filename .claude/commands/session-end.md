# Session End Workflow

Guide me through ending this development session properly.

## Step 1: Review Changes
- Run `git status` to see all modified and untracked files
- Run `git diff` to review the actual changes
- Identify any files that shouldn't be committed (secrets, temp files, etc.)

## Step 2: Pre-Code Check (PCC)

Run the standardized PCC checklist before committing:

1. **Secrets check** - No API keys, passwords, tokens in staged files
2. **Tests pass** - Run `pytest`
3. **Debug artifacts** - No `print()`, `breakpoint()` left in code
4. **Git state** - Review what's staged vs unstaged

**If PCC fails**: Fix issues before proceeding to commit.

**If PCC passes but changes are significant** (new source, scoring changes, distiller modification): Consider running `/pci` for deeper inspection.

See `@pcc` for the full checklist and output format.

## Step 3: Commit
- Stage appropriate files
- Write a descriptive commit message using `[area]` tags:
  - `[source]` - sourcing changes (ArXiv, RSS, new feeds)
  - `[select]` - selection/scoring changes
  - `[distill]` - distiller/briefing changes
  - `[pipeline]` - pipeline orchestration
  - `[config]` - configuration changes
  - `[cli]` - CLI/main.py changes
  - `[tts]` - TTS/audio integration
  - `[doc]` - documentation updates
  - `[fix]` - bug fixes
  - `[refactor]` - code restructuring
  - `[test]` - test additions/changes
- Example: `[source] Add HuggingFace Daily Papers as content source`
- Push to the current branch

## Step 4: Update Task List
- Read `docs/tasks.md` and update based on this session's work:
  - Mark completed tasks with today's date: `- [x] 2026-03-11: Description`
  - Add any new tasks discovered during the session
  - Move blocked tasks if blockers were resolved
  - Flag any tasks that should be promoted (use the `/task promote` escalation ladder)
- Run `/task brief` mentally — does the backbrief make sense?

## Step 4.5: Update Project Status
- **config/project.yaml**: Update version, phase status
  - Update `build_phases` status as work progresses
  - Bump version number if appropriate
- Include these updates in the commit (amend if needed)

## Step 5: Session Documentation
- Create a session doc in `docs/sessions/` with format `YYYYMMDD_descriptive_name.md`
- Start with the standard header following the knowledge graph format:
  ```markdown
  # Session: Descriptive Title

  **Date**: YYYY-MM-DD
  **Branch**: main
  **Tags**: #session #domain #activity

  **Documents**: [pillars.md](../design/pillars.md) — Design principles this session touched
  **Implements**: [plan.md](../plans/plan_name.md) — Plan being followed (if any)
  **References**: [other.md](../background/other.md) — Docs consulted during work
  **Follows**: [prev_session.md](20260220_prev.md) — Previous session (if continuing)
  **Completes**: Phase N — Name (from project.yaml)
  **Requires**: [blocker.md](../design/blocker.md) — Unresolved dependency (if any)
  **Cites**: [source.md](../background/source.md) — External reference or algorithm source

  ---
  ```

- **Tags** — Use canonical taxonomy:

  | Category | Tags | Use for |
  |----------|------|---------|
  | **Type** | `#session` | Always include for session logs |
  | **Domain** | `#source` `#select` `#distill` `#pipeline` `#config` `#cli` `#tts` | What area |
  | **Status** | `#complete` `#in-progress` | Work completion state |
  | **Pillars** | `#pillar-1` through `#pillar-5` | Design principle relevance |

- **Relationships** — Session docs create edges to permanent docs, forming a navigable knowledge graph. Only include the relationship types that apply:

  | Relationship | When to Use |
  |--------------|-------------|
  | `**Documents**:` | Link to system/design docs this session touched (most common) |
  | `**Implements**:` | If following an implementation plan |
  | `**References**:` | Other docs consulted during work |
  | `**Follows**:` | If continuing a previous session |
  | `**Completes**:` | Phase or milestone this session finishes |
  | `**Requires**:` | Unresolved dependency blocking future work |
  | `**Cites**:` | External reference, algorithm source, or prior art |

- Include in the session body:
  - Summary of work completed
  - Key changes made (files, functions)
  - Any diagrams if helpful (ASCII for simple, Mermaid for complex)
  - Next steps / outstanding tasks

**Tip**: Search sessions with `grep -r "#source" docs/sessions/` or `grep -r "Documents.*pipeline" docs/sessions/` to find related work.

## Step 6: Evaluate Merge Readiness
- Is this a major functional milestone?
- If yes, consider merging to main
- If no, continue on current branch

Please walk me through each step, showing me the current state before asking what I want to do.
