# SME Alignment Review: CONOP COURIER

**Verdict: SUPPORTING WITH CHANGES.** Blocker 0, Major 4, Minor 8. The plan is Phase 3 as the roadmap states it and stops where Phase 3 should. Before approval: fold M1 to M4 into the CONOP; the Minors are one-line edits or Wave 1 tasks.

Reviewer: pipeline-sme, 2026-10-22, read-only. Read: the CONOP, the proposal, the headless check, `docs/tasks.md`, `docs/gaps.md`, `docs/design/roadmap.md`, `docs/design/pillars.md`, `config/project.yaml`, `config/paperboy.yaml`, and the code lines the plan cites. Line numbers below were read this turn.

## Findings

| # | Severity | Finding | Fix |
|---|---|---|---|
| M1 | Major | G9 asks for the rank the reader would have picked from the day's top 5, and the post shows one paper. `src/pipeline.py:448` calls `select_best(top_k=1)` and keeps `scored[0]`; the Claude-scored alternatives (`src/selector.py:106`) are computed and dropped. | Task 1.1: `PipelineResult` and the D5 record gain `top_candidates` (id, title, score, up to `top_k_for_claude`). Task 1.3: the parent lists them, one line each. |
| M2 | Major | MOE 2 (G8's second half, episodes produced from the delivered file) has no collector. D5 has no listener field and no task writes "a listener line beside the run record". | Wave 3.2's encoding gains one reaction, `headphones` = episode produced and heard, read by the same probe; or name the file and the task that writes it. |
| M3 | Major | D3 removes `temperature` from both call sites, which deletes the "API at 0.0" arm of G4's design and makes the P3 temperature-control task moot on both paths. The plan names neither amendment. | At Wave 1 exit: amend G4's collector (arm becomes "API at the model default"), rewrite the P3 task, and edit Focus step 2's G4 clause. |
| M4 | Major | Phase 3 cannot close against `docs/design/roadmap.md:58-64` as written: three of six deliverables are declined in one line each and the roadmap keeps them as deliverables. | In the commit that sets `phase_3: in_progress`, mark each roadmap line built, or declined with its trigger (A6, A7) or reason. Close predicate: every line carries a mark. |
| m1 | Minor | D8 rosters `paperboy` in task 1.7, before its clone exists in Wave 2. Focus step 3's "close G5 for every rostered clone" then has a name with no report, and `/session-start` never runs on the server. | Roster the entry in Wave 2 with the clone. G5's collector for that box is `update-server.sh` (task 3.3), stated in the row. |
| m2 | Minor | D4's parent is telemetry. `ScoredPaper.reasoning` (`src/models.py:86`) is Claude's one-line "why this paper" and is absent. | Parent: title, link, reasoning, the top-5 list, then one telemetry line (status, backend, duration, words). |
| m3 | Minor | D3 has no falsifier that compares: A4 reads one model once. | A4 as a paired read, same paper, both models, about $0.21. Opus stays unless the lead cannot tell them apart. |
| m4 | Minor | `config_sha256` names no input. `USER_CONTEXT` changes the briefing and lives in `.env`, not the YAML. | Hash the effective `PipelineConfig` after env overrides, serialized deterministically; the text never enters the record. |
| m5 | Minor | D15 orders Wave 1 against the flip but not against the v0.3.0 tag; Wave 1 is Phase 3 work landing in a Phase 2 version. | Tag v0.3.0 at the Phase 2 close before Wave 1 merges, or list Wave 1 in its CHANGELOG entry. One or the other. |
| m6 | Minor | Pillar 4 says the design "enables backfilling" and `--date` widens `days_lookback` rather than targeting a date (`main.py:58`). Predates the plan. | Amend the Pillar 4 sentence when the backfill decline lands in the roadmap. |
| m7 | Minor | Task 3.1 puts an SSH read into `/session-start`. A dead server must not fail session start. | The step renders `unchecked` with the blocker and no value (rule 8). |
| m8 | Minor | G8's record is the server's file. A by-hand run on Muninn writes Muninn's `output/` and its own dedup history. "Manual runs included" is true per file only. | State the universe in the G8 row and in `src/runlog.py`'s docstring: the delivery box's file; blind to workstation runs and to days before the file existed. |

## 1. Mission

**SUPPORTING.** The chain is source, select, distill, export, listen. Phase 1 built the first four to a file; nothing carries the file. COURIER makes the run daily and puts the file where the phone is. The hand step that remains, Slack to NotebookLM, is Phase 4's job by the roadmap's own words ("bypassing manual NotebookLM upload", `roadmap.md:68`), and Phase 5 removes Slack as the display. Phase 3 stops at the right place.

What makes the stopping point honest is MOE 2: the record will say whether a delivered file becomes an episode, which is the measurement G8 names for the Phase 4 or Phase 5 decision. Without M2 the plan asserts that measurement and never takes it. Slack is a display, not the export. The seam is right: `report.py` builds, `slack.py` sends; Phase 5 adds `feed.py` beside `slack.py`, and Phase 4 attaches audio in place of the `.md`. No delivery ABC now (Simplicity First).

## 2. Phase and Focus order

**SUPPORTING WITH CHANGES** (m1, m5). D15 is right on two of three counts. Secrets: Wave 1 adds placeholders to `.env.example` and the boundary-line test the flip wants, so Wave 1 before the flip lowers the flip's risk. The CI check: no workflow exists either side of the flip; D12's reminder is the fix. G5 is the exception: m1. Phase 2's close is three commands (Focus step 3) and waits on nothing in Wave 1; close it first, tag v0.3.0, then merge Wave 1 (m5). The flip may land either side of Wave 2. After approval the Focus replaces step 4 with the three waves and their gates (section 6) and edits steps 2 and 3 where G4 and G5 change.

## 3. Roadmap Phase 3 deliverables

**SUPPORTING WITH CHANGES** (M4, m6). Each decline, judged:

- Output rotation: right. About 11 MB a year; `SelectionHistory._seed_from_briefings` scans the directory each run and 365 files is nothing.
- Backfill: right in substance. The mission is one briefing a day forward; dedup plus the 7-day window gives a missed day's papers their chance the next morning. The roadmap and Pillar 4 both promise it, so the decline goes in the roadmap with its reason (m6).
- Skip-if-done: right to wait for A7 with one tick a day. The roadmap line carries the trigger, not a deletion.
- Failure notification: built for every failure but a dead box; A6 names the escalation. Right.

A Phase 3 that closes with three lines unmarked closes by sentence. M4 makes it close by predicate.

## 4. The register

**SUPPORTING WITH CHANGES** (M1, M2, M3, m1, m8). Row by row:

- **G8**: D5 covers the row's first half (date, status, backend, selected id) and more. Task 3.1 printing missing days as rows is rule 8 done right; add the two-shape output and the universe (m8). The back period since 2026-07-20 stays with `ls output/briefings/`; the record cannot reach it. The second half is M2. Amend the collector cell to name `run_history.jsonl`, `src/runlog.py`, and the listener signal; Status stays `open` until the first reading in `docs/reviews/`.
- **G9**: the encoding yields a rank, exact, and agreements of N reacted of M posted, which is the row's shape. It fails on input: M1. Two more clauses for the row: the probe reads the parent `slack_ts` only, so the parent says "react to this message"; universe is posted days with a reaction, blind to unposted days and to candidates below the top 5.
- **G4**: M3. New arm text: "keyword-only as control, API at the model default (`temperature` removed by COURIER task 1.0), Agent". The "Decision it blocks" clause about the temperature-control task becomes "whether Pillar 4 can be claimed for the Claude stages at all, since neither path controls sampling". `effort` enters the config hash and so the probe's fixture.
- **G5**: m1. Universe grows by `paperboy` when D8 lands; that box's collector is `update-server.sh`, and its clone is post-rewrite by construction (cloned from origin after 2026-07-20).
- **G3**: no change to the collector. One clause: the D3 model change is outside the test's universe (both fixture briefings predate it), and A4 is read, not heard, so A4 does not close G3.
- No new row. The dead-box silence is A6, inside G8.

The P3 task "Record the backend in PipelineResult ... and a config hash" closes at task 1.1; `pillars.md` Pillar 4 may then name the record and the hash again.

## 5. Pillar 1

**SUPPORTING WITH CHANGES** (m2, m3, M1). Pillar 1 does not decide D3 on its own: nothing measures the two models as heard, and G3 says even the kernel's effect is unmeasured. The pillar's "when in doubt" rule points at Opus; the $0.07 a day is about $25 a year. Take Opus and give it the exit m3 names.

The Slack shape serves the mission once the parent serves its two readers. The listener deciding whether to make today's episode wants the "why this paper" (`reasoning`) and the link; G9 wants the alternatives (M1). Duration, backend and word count belong in the record and get one line in the post. The file in the thread is right; A1 tests it on both devices.

## 6. The `## Focus` rewrite

Replace step 4 with these three; renumber the rest. Edit step 2 to read "G4 and G7 together, after COURIER task 1.0 moves the API arm to the model default" and step 3's G5 clause to "for Muninn and Nidhogg; `paperboy` reports through `deploy/update-server.sh` at Wave 2".

4. Open Phase 3 under CONOP COURIER (`docs/plans/conop_COURIER_daily_run_slack_delivery.md`), Wave 1 first, on a topic branch merged at the code-reviewer's gate: the API path on current model IDs in one `[config]` commit before any scheduled run, the run record `output/briefings/run_history.jsonl` as gap G8's collector, `--slack`, and the boundary-line test the flip in step 3 also wants. Gate: `.venv/bin/pytest` green, `/pcc` clean, and one `python main.py run --slack` from a workstation posting the parent and the file to the dev channel. In the same session, mark every Phase 3 line in `docs/design/roadmap.md` built or declined with its trigger, and set `phase_3: in_progress` in `config/project.yaml`.
5. Wave 2, the lead by hand after the v0.3.0 tag and either side of the flip: the account, venv, `.env` and App per `deploy/README.md`; the `paperboy` roster entry lands with the clone and `deploy/update-server.sh` reports gap G5 for it. Gate: a week of consecutive run lines carrying `slack_ts`, read by `src/runlog.py` over the account's alias, and one NotebookLM episode made from a Slack-delivered file.
6. Wave 3, after Wave 2's first week: `src/runlog.py` at `/session-start` (rendering `unchecked` when the server is unreachable), the reaction probe over `slack_ts` with decision-scientist reading the encoding first, and the first G8 and G9 readings in `docs/reviews/`. Amend rows G4, G5, G8 and G9 as `docs/reviews/20261022_courier_sme_alignment.md` section 4 lists. Phase 3 closes when every roadmap line carries its mark and the two readings exist.

## 7. Drift check

Nothing in the plan is outside paperboy's business. Named for the record:

- The Consumer Terms question (D2) is the lead's with Anthropic, and the plan says so. Right.
- `daily_weather`'s Slack app is not ours. A2's kill criterion (make a second app) is the only correct move if scopes would rotate a shared token.
- Approach D's watchdog in GitHub Actions: deferred to A6. Right; it widens the secret blast radius for one failure mode.
- `tests/test_boundary_line.py` and the `.env.example` cleanup are repo hygiene for the flip, not pipeline. SUPPORTING; they ride here because `deploy/` is the first tracked directory that could carry an address.
- Tempting and declined: per-feed counts in the run record for G6. The record is G8's collector; keep D5's field list as it is.
- `src/slack.py` growing into a notification layer (channels, profiles). D6's one switch is the guard; hold it.
- No arcade, bike or fitness theming anywhere in the plan.
