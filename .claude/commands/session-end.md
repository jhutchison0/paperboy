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

## Step 4.5: Update Focus and Gaps
- **The `## Focus` section at the head of `docs/tasks.md`**: rewrite it when the order of the campaign changed. It is intent: what comes next, in order, with absolute dates. It holds no count and no status, because a kept number reads as current after it stops being true; a step that needs a number names the command that measures it. A repo without the section starts it here.
- **`config/project.yaml`** is identity (name, version, phases, machines, paths). Touch it only when one of those changed: bump `build_phases.*.status` if a phase advanced, `project.version` if a release was cut. Do not record the session there: the last session is the newest file in `docs/sessions/` by name, and the suite, branch, and tools are measured at `/session-start`.
- **`docs/gaps.md`, the gap register** (rule 5 of `.claude/skills/maintaining-the-common-operating-picture/SKILL.md`): add a row for each thing the session found that nobody can see yet, naming the collector that would close it and the decision it blocks. When a collector now covers a gap, or a measurement found it absent, set its Status to `closed YYYY-MM-DD by <pointer>`; when a newer row restates it, to `superseded YYYY-MM-DD by <pointer>`; never delete a row. A defect is a task, not a gap. Step 2 ran before this edit, so run the register's test again after it (here, `.venv/bin/pytest tests/test_gaps.py -q`).
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
