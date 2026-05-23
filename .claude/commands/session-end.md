# Session End Workflow

Guide me through ending this development session properly.

## Step 1: Review Changes
- Run `git status` to see all modified and untracked files
- Run `git diff` to review the actual changes
- Identify any files that shouldn't be committed (secrets, temp files, output briefings)

## Step 2: Pre-Code Check (PCC)

Run the standardized PCC checklist before committing:

1. **Secrets check** — No API keys, passwords, tokens in staged files
2. **Tests pass** — Run `pytest`
3. **Debug artifacts** — No `print()`, `breakpoint()` left in code
4. **Git state** — Review what's staged vs unstaged

**If PCC fails**: Fix issues before proceeding to commit.

**If PCC passes but changes are significant** (new source, scoring changes, distiller modification): Consider running `/pci` for deeper inspection.

See `/pcc` for the full checklist and output format.

## Step 3: Commit
- Stage appropriate files
- Write a descriptive commit message using `[area]` tags:
  - `[source]` — sourcing changes (ArXiv, RSS, new feeds)
  - `[select]` — selection/scoring changes
  - `[distill]` — distiller/briefing changes
  - `[pipeline]` — pipeline orchestration
  - `[config]` — configuration changes
  - `[cli]` — CLI/main.py changes
  - `[tts]` — TTS/audio integration
  - `[agent]` — AgentRunner / Claude CLI backend
  - `[doc]` — documentation updates
  - `[fix]` — bug fixes
  - `[refactor]` — code restructuring
  - `[test]` — test additions/changes
  - `[infra]` — project infrastructure (.claude/, hooks, CI, doctrine adoption)
- Example: `[source] Add HuggingFace Daily Papers as content source`
- Push to the current branch

## Step 4: Update Task List
- Read `docs/tasks.md` and update based on this session's work:
  - Mark completed tasks with today's date: `- [x] YYYY-MM-DD: Description`
  - Add any new tasks discovered during the session
  - Move blocked tasks if blockers were resolved
  - Flag any tasks that should be promoted (use the `/task promote` escalation ladder)
- Run `/task brief` mentally — does the backbrief make sense?

## Step 4.5: Update Project Status
- **config/project.yaml**: Update `last_updated` and `updated_by`; bump `build_phases.*.status` if a phase advanced; bump `project.version` if appropriate.
- Include these updates in the commit (amend if needed).

## Step 5: Session Documentation

Create a session doc in `docs/sessions/` with format `YYYYMMDD_descriptive_name.md`.

**Format reference**: [docs/session-doc-format.md](../../docs/session-doc-format.md) — header template, knowledge-graph relationship types, tag taxonomy, body structure, diagram guidelines.

Quick reminders:
- Date-first filename so sessions sort chronologically.
- Knowledge-graph header: only include relationship fields that actually apply.
- Body must include Summary and Next Steps. Other sections (Work Completed, Key Decisions, Pillar Compliance, Commits) are added as the session warrants.
- Prefer Mermaid over ASCII art for any non-trivial diagram (renders natively in GitHub).

Search related sessions with `grep -r "#pillar-3" docs/sessions/` or `grep -r "Follows" docs/sessions/`.

## Step 6: Evaluate Merge Readiness
- Is this a major functional milestone?
- If yes, consider merging to main
- If no, continue on current branch

Please walk me through each step, showing me the current state before asking what I want to do.
