# SME Alignment Review: CONOP COURIER Wave 1

**Verdict: SUPPORTING WITH CHANGES.** Blocker 0, Major 2, Minor 8. Wave 1 builds what D4, D5, D12 and D13 say and nothing past them; the record is G8's collector and the post carries G9's input. Fix MA1 and MA2 before the merge; the Minors are one-line edits or Status Log sentences.

Reviewer: pipeline-sme, 2026-10-24, read-only, on `topic/pipeline-courier-wave1-20261024` with the tree uncommitted. Read: the CONOP (D4, D5, D12, D17, Wave 1, Status Log), `docs/design/roadmap.md` Phase 3, `docs/design/pillars.md` Pillar 4, `config/project.yaml`, `docs/gaps.md` G8 and G9, my 2026-10-22 review, the diffs of every modified file, the new files under `src/`, `tests/` and `deploy/`. Suite this turn: `.venv/bin/pytest -q` → `348 passed in 1.83s`. The posts below were rendered by `/tmp/claude-1000/-home-jhutchison-projects-github-paperboy/f4514856-26aa-491c-be34-1dbf0b6feb4b/scratchpad/render_slack.py`, which builds a `PipelineResult` from `src/models.py` dataclasses (five authors, a 1,200-character abstract, five scored candidates, `backend="agent"`, `distill_model="claude-fable-5-1"`, `duration_s=412.3`, 4,600 words) and never touches the network.

## Findings

| # | Severity | Finding | Fix |
|---|---|---|---|
| MA1 | Major | `build_message` raises on a `success` with no briefing. Keyword-only degradation reports `success` with `briefing=None` (`src/pipeline.py:531-535`), and auto mode on the server falls to keyword-only when `claude` is not on `PATH` (assumption A4) or the token fails (A0). The deliverer catches the exception, so the first morning the plan is most likely to fail produces no post at all. Probe output: `build_message raised AttributeError: 'NoneType' object has no attribute 'word_count'`. | A success-without-briefing branch in `_success`: title, link, top five, "No briefing: the Claude backend was unavailable (keyword-only)", telemetry with `0 words`. One table-driven test. |
| MA2 | Major | `.env.example` ships `CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-your-token-here` and `SLACK_BOT_TOKEN=xoxb-your-token-here` uncommented; `cp .env.example .env` is the quickstart (`README.md:43`, `CLAUDE.md:108`). The strip now keeps the token, and it outranks the stored login (headless check, line 15), so a fresh workstation `.env` sends a bogus token to `claude -p` and the agent backend fails on a box that worked yesterday; `health` exits 1 on the placeholder Slack token. The API key placeholder is guarded (`src/config.py:250`); these two are not. | Comment both lines out, as `HOME_BRIEFINGS_ROOT` already is, or guard the two placeholders where the API key's is guarded. |
| m1 | Minor | The 600-character cut is a character slice. Probe: `_trim_abstract` on fixed-width words ends `antidisestablishmen…` (600 chars). The three-sentence cut leaves a period before the ellipsis: `recommendations.…` in the success post. | Cut at the last space inside the budget; when the cut lands on a sentence end, write ` …` or nothing. |
| m2 | Minor | `scoring_model` and `distill_model` are `"cli-default"` when the CLI reported no model (`src/pipeline.py`, the agent branch of `__init__`). After task 1.9 that happens only when no call succeeded, so the word stands where rule 8 wants no value. | `None` in the record; the post may say `model not reported`. |
| m3 | Minor | `config_sha256` hashes `dataclasses.asdict(config)`, which includes `output_dir` and `log_level`, so the server's hash never equals a workstation's for the same YAML and the same `USER_CONTEXT`. | Decide before the first server line: exclude the two (the hash means "same briefing inputs") or keep them and say so in D5's Status Log. |
| m4 | Minor | `claude.max_tokens` moved from 8000 to 16000 with the comment "thinking shares the output cap on current models". D3 names no number. | One Status Log sentence under 2026-10-24 naming the change and its reason. |
| m5 | Minor | The sentence splitter `(?<=[.!?])\s+` splits on `et al. ` and `e.g. `. It never invents text, so the trim stays honest; it may hand the reader two sentences where three were promised. | Leave until a post shows it. |
| m6 | Minor | The legend does not say "react to this message"; the Wave 3 probe reads the parent `slack_ts` only, and task 3.4 adds thread replies. | `Reactions on this message:` now, or at 3.4. |
| m7 | Minor | `.claude/README.md` has no scope-matrix rows for `src/slack.py` and `deploy/`, which the CONOP's Agent and Team Design section asked for when Wave 1 started. | Two rows. |
| m8 | Minor | Three orientation lines predate D4 or Wave 1: `docs/tasks.md` Active P1 says "each run posted to Slack with the briefing attached"; `LANGUAGE.md` `PipelineResult` says `_Avoid:_ run record`, which now names a different thing; `SelectionHistory` is placed at `output/.selection_history.json`. | Edit the three with the roadmap commit; section 5 drafts the glossary lines. |

## 1. The Slack post as the reader will see it

**SUPPORTING WITH CHANGES** (MA1, m1, m6). The three renders, verbatim:

```
===== SUCCESS (1486 chars, 13 lines) =====
*Preference-Grounded Retrieval for Analyst-in-the-Loop Decision Support*
http://arxiv.org/abs/2610.10001v1
Directly addresses preference elicitation inside a RAG loop for analyst decision support, with a benchmark that includes literature prioritization.
Large language models are increasingly deployed as components of decision-support systems, yet their recommendations are rarely calibrated against the preferences of the analyst who must act on them. We introduce Preference-Grounded Retrieval (PGR), a retrieval-augmented framework that conditions both the retriever and the generator on a compact, elicited preference profile rather than on the query alone. PGR learns the profile from fewer than twenty pairwise comparisons and updates it online as the analyst accepts or rejects recommendations.…
Top five today:
1. Preference-Grounded Retrieval for Analyst-in-the-Loop Decision Support (0.91)
2. Calibrating Retrieval Confidence with Conformal Risk Control (0.84)
3. When Do Agents Ask? Uncertainty-Triggered Clarification in Tool Use (0.79)
4. Scaling Laws for Evaluation Harnesses: How Many Items Is Enough? (0.73)
5. Sparse Autoencoders Recover Decision Features in Fine-Tuned Policy Models (0.68)
Briefing: 261024_preference-grounded-retrieval-for-analyst-in-the-loop-decision-support_briefing.md on the home share
Reactions: :white_check_mark: agree, :one: to :five: the rank you would have picked, :headphones: heard
success | agent | claude-fable-5-1 | 412s | 4600 words

===== PARTIAL (236 chars, 4 lines) =====
:warning: Paperboy ran partially.
*Preference-Grounded Retrieval for Analyst-in-the-Loop Decision Support* (0.91)
Error: timeout: claude -p exceeded 600s on distill (attempt 2 of 2)
Briefing not recorded for dedup; the next run retries.

===== ERROR (108 chars, 2 lines) =====
:x: Paperboy run failed.
No papers or articles sourced. Check network connectivity and source configuration.
```

The order is D4's order exactly: title, link, reasoning, abstract, top five, filename, legend, telemetry. The listener deciding whether to make today's episode gets the decision in the first three lines (title, link, the one-sentence "why"); the abstract is there if those do not settle it. The G9 reader gets the five ranks with scores and the legend that maps a reaction to a rank. Thirteen lines and 1,486 characters fit a phone screen in two swipes; the longest block is the abstract at three sentences. The filename line wraps, and should: it is what the reader searches for on the share. Nothing is surplus. The selected paper appears twice (the title and rank 1), which G9 needs so that `:one:` has a referent. Authors are absent; D4 did not ask for them and the link carries them, so this is an observation for task 3.4, not a finding. The trim is honest in what it keeps: the three-sentence cut is marked because a fourth sentence exists, and `test_short_abstract_has_no_ellipsis` pins the no-cut case. Its two blemishes are m1. The partial post names the paper, the error and the retry promise; the error post names the error. Both are right for a reader who will do nothing but glance. MA1 is the post that does not exist.

## 2. The record against G8 and G9

**SUPPORTING** (m2, m3). `_write_run_record` writes the twenty D5 fields and `test_success_line_has_every_field` asserts set equality on them. Each is a value, not a sentence: `date` and `started_at` as ISO strings in UTC (`test` pins `+00:00`), `duration_s` a float, `status` one of three words, `score` a float, `top_candidates` a list of `{id, title, score}` best-first, the counts integers, `briefing_path` and `words` null on a partial, `git_sha` a short hash or null, `config_sha256` 64 hex characters. `error` is a sentence by nature and is the one field that should be. G8's row asks for date, status, backend and selected id per run; the line carries them and the stamp, collector (`machine`) and subject (`selected_id`) rule 2 wants. Its universe is D5's, the delivery box's folder; the Wave 3 reader's docstring must say so (my 2026-10-22 m8). G9's input is the top five with ranks: `_source_and_select` now asks `select_best` for `top_k_for_claude` and the pipeline keeps the first; `test_top_candidates_up_to_five_and_first_is_selected` pins `top_k`, the identity of `selected_paper` and the record's five entries. The `headphones` reaction (MOE 2) has its legend entry; the probe is Wave 3. The P3 task "record the backend in `PipelineResult` and a config hash" closes at this merge.

## 3. Roadmap, pillar and phase, ready to apply

Apply after the merge, in the commit D17 names. Line 54's heading gains ` -- IN PROGRESS` to match Phase 2's. Replacement for `docs/design/roadmap.md` lines 58 to 64:

```markdown
**Deliverables** (each line marked 2026-10-24 under CONOP COURIER, `docs/plans/conop_COURIER_daily_run_slack_delivery.md`; the phase closes when every line carries a mark and gaps G8 and G9 have their first readings in `docs/reviews/`):
- Cron job or scheduled task configuration for daily runs: built, COURIER task 1.8 (`deploy/crontab`, `deploy/README.md`, `deploy/update-server.sh`); the server itself is Wave 2
- Date-based deduplication (skip if today's briefing already exists): declined 2026-10-24; one tick a day needs no guard and `SelectionHistory` already prevents a repeated paper. Trigger to build: COURIER assumption A7
- Output rotation and cleanup (keep last N briefings, archive older): declined 2026-10-24; a year of briefings and record lines is small enough to keep (the estimate is in COURIER, What We Do NOT Build)
- Run history log with success/failure tracking: built, COURIER task 1.1 (`run_history.jsonl` beside the briefings, one JSON line per run, gap G8's collector); its reader is Wave 3 task 3.1
- Notification on failure (email, Slack webhook, or similar): built, COURIER tasks 1.3 to 1.5 (`run --slack` posts success, partial and error; exit 3 when the post fails after a saved briefing). A dead box posts nothing; trigger to build the watchdog: COURIER assumption A6
- Backfill command for generating missed briefings: declined 2026-10-24; the dedup history and the lookback window give a missed day's papers their chance at the next morning's run, and `--date` widens the window rather than targeting a day. Pillar 4's sentence amended the same day
```

Replacement for the fourth sentence of `docs/design/pillars.md:83` ("It enables backfilling: running the pipeline for past dates to generate briefings you missed."):

```markdown
A missed day needs no backfill: the dedup history and the lookback window give that day's papers their chance at the next morning's run, and `--date` widens the window to include a past date rather than re-creating that day's briefing (declined in the roadmap's Phase 3, 2026-10-24).
```

Companion, `docs/design/pillars.md:90`, which the merge makes false:

```markdown
- `PipelineResult` carries the run's outcome and its inputs (status, counts fetched, the selected paper and the day's top candidates, the briefing path, the backend and the models that ran, a SHA-256 of the effective config, any error), and `run_history.jsonl` keeps one line per run (COURIER task 1.1)
```

`config/project.yaml` `phase_3` block. `phase_2` stays `in_progress` and `current_phase` stays Phase 2 until Focus step 3 closes it; two phases open for that window is the honest picture, and `CLAUDE.md` "Current Phase" moves with `current_phase`:

```yaml
  phase_3:
    name: "Scheduling & Automation"
    status: "in_progress"
    description: "One scheduled run a day on the home server, a Slack summary as the reminder, one record line per run; CONOP COURIER (docs/plans/conop_COURIER_daily_run_slack_delivery.md), opened 2026-10-24"
    deliverable: "Automated daily runs with deduplication, a run history and failure notification; closes when every Phase 3 roadmap line carries its mark and gaps G8 and G9 have their first readings"
```

## 4. CHANGELOG

For the `## [0.3.0]` entry Focus step 3 cuts; the entry's Milestone line is the lead's. The head's bullets use an em dash after the bold name; these use a colon per Prose Style rule 8, and carry no test counts per Picture Style.

```markdown
### Daily Run and Delivery (CONOP COURIER Wave 1)
- **`--slack` on `run`**: one summary post per run to `PAPERBOY_SLACK_CHANNEL` (title, link, Claude's reasoning, the abstract trimmed, the day's top five, the briefing's filename, a reaction legend, one telemetry line); partial and failed runs post their error. Exit 1 with `Configuration error:` when `SLACK_BOT_TOKEN` or the channel is missing; exit 3 when the post fails after a saved briefing
- **`src/slack.py`**: NEW: `post_message`, `auth_test`, `build_message`, `SlackError`; stdlib `urllib` only, one retry on HTTP 429, no retry on timeout, mrkdwn escaping
- **Run record** (`src/pipeline.py`): one JSON line per run appended to `run_history.jsonl` beside the briefings, written after delivery: date, start, duration, status, backend, machine, the models that ran, the selected paper and the day's top candidates, counts fetched, briefing path and words, error, the Slack receipt, git sha, a SHA-256 of the effective config. Gap G8's collector
- **Delivery seam**: `DailyPipeline(config, backend, deliverer=None)`; a raising deliverer never rolls back the briefing or the dedup record
- **`PipelineResult`**: gains `backend`, `machine`, `scoring_model`, `distill_model`, `started_at`, `duration_s`, `top_candidates`, `slack_ts`, `slack_error`; selection returns the Claude-scored top candidates and the pipeline keeps the first
- **Headless `AgentRunner`** (`src/agent_runner.py`): `CLAUDE_CODE_OAUTH_TOKEN` from `claude setup-token` survives the environment strip; `ANTHROPIC_AUTH_TOKEN` joins `ANTHROPIC_API_KEY` in it; `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` and `DISABLE_AUTOUPDATER=1` are set; `claude -p` runs with `--output-format json --no-session-persistence --tools ""`, the text read from the JSON `result` and the model name from `modelUsage`
- **`HOME_BRIEFINGS_ROOT`**: the first `HOME_*` variable; when set it replaces `pipeline.output_dir` for the briefings, the dedup history and the run record; unset, the YAML default stands
- **API fallback on current models** (`config/paperboy.yaml`, `src/config.py`, `src/selector.py`, `src/distiller.py`): distill on `claude-opus-5-5`, scoring on `claude-haiku-5-5` with thinking disabled and low effort; no sampling parameter on either call; both call sites read the first `text` block by type; a leftover `claude.temperature` key warns
- **`health`**: an unconfigured backend prints SKIPPED and does not fail the check; a `slack` line via `auth.test` when the token is set
- **`deploy/`**: NEW: `README.md` (the Custom App runbook, placeholders only), `crontab` (one tick at 05:30, `run --slack`), `update-server.sh` (push, pull, reinstall when `requirements.txt` changed, `health` and `source` as the proof; prints the CLI version, the token's renewal comment and the gap G5 line)
- **`tests/test_boundary_line.py`**: no tracked file names a UNC path, an `smb://` host or an IPv4 literal outside the allowlist
- **`requirements.txt`**: `anthropic<1` for this cycle
- **Removed**: the retired `claude-sonnet-4-20250514` and `claude-haiku-4-5-20251001` IDs and the `claude.temperature` key; `_strip_preamble_json` and `_strip_preamble_markdown`; the dead `OUTPUT_DIR` and `CONFIG_PATH` lines in `.env.example`
```

## 5. Drift

Nothing here is outside paperboy's business, and nothing reaches past Wave 1's rows. Checked: the `--tools ""` spelling D13 left to the implementer exists on this box's CLI (`claude --help` line 255, `--tools <tools...>`, version 2.1.310) and `test_agent_headless.py` pins the argv. `_main_model` picks the costliest entry in `modelUsage` because the fixture shows a small auxiliary model on every call; that is task 1.9's spirit, not an extra feature. The `deliverer` is a callable, as D12 says; no ABC, registry or config section appeared. `deploy/` mirrors `daily_weather` and names no address; `TZ: America/Chicago` is a zone, not a place on the LAN. No name smells of theme: `slack.py`, `deliverer`, `run_history.jsonl`, `HOME_BRIEFINGS_ROOT`, `paperboy` as the App's name. `:headphones:` marks the listening act G8 measures, not a fitness motif. The one deviation from the text is m4 (`max_tokens`).

`LANGUAGE.md` entries that earn a line (recurrence in the CONOP, the code, the tests and the Focus; ambiguity with an existing term):

```markdown
**Run Record**: The file `run_history.jsonl` beside the briefings, one JSON line per `DailyPipeline.run()` written after delivery; gap G8's collector. _Avoid:_ run log (the reader is `runlog.py`; the file is the record), PipelineResult (in memory; this is on disk).

**Deliverer**: The callable `DailyPipeline` calls with the `PipelineResult` after save and dedup, returning a receipt or raising; Slack today, audio and a feed later. _Avoid:_ notifier, exporter, delivery backend.

**Summary Post**: The one Slack message `build_message` renders per run: title, link, reasoning, trimmed abstract, top five, filename, reaction legend, telemetry. _Avoid:_ parent (say summary post; "parent" only when a thread reply is in view), notification.

**Home Share**: The shared folder on the home server that `HOME_BRIEFINGS_ROOT` names in `.env`, holding the briefings, the dedup history and the run record; its path is never tracked (lake-conventions `HOME-STORAGE.md`). _Avoid:_ output dir (the YAML default it replaces), NAS path.
```

And amend `PipelineResult`'s `_Avoid:_` to `run record (the on-disk line; see Run Record)`.
