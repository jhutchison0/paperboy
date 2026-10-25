# Review: CONOP COURIER, challenge round

**Reviewer**: code-reviewer. **Date**: 2026-10-22. **Under review**: `docs/plans/conop_COURIER_daily_run_slack_delivery.md` (untracked draft, 225 lines), with `docs/plans/20261022_courier_proposal.md` and `docs/reviews/20261022_courier_claude_cli_headless_check.md` as inputs. Tree at cfde101, three untracked docs, no code changed. Sister repo read at `/home/jhutchison/projects/github/daily_weather`.

## Verdict: GO WITH FIXES

Approach A, the API backend, the Slack shape and the run record stand. Three facts the plan rests on are wrong or unresolved: the configured distill model is retired, the server's `health` gate cannot exit 0, and the run line and the Slack post have no agreed owner. Fix those in the draft before the lead approves; none changes the approach.

| Severity | Count | IDs |
|---|---|---|
| Critical | 3 | C1 retired model, C2 health gate, C3 record and Slack owner |
| Warning | 5 | W1 Pillar 4 lever, W2 A2 falsifier, W3 Wave 1 gate, W4 refuted line claims, W5 assumptions table |
| Suggestion | 6 | S1 seam, S2 cuts, S3 exit code, S4 weekends, S5 D8 passes, S6 untestable rows |

## Critical

### C1. The distill model is retired; A4's kill criterion cannot fire
Claim (Enemy Forces, D3, A4): the configured IDs are "unverified"; "the old IDs stay until A4 passes"; on a worse briefing, "keep Sonnet 4 while it resolves".
Checked: `config/paperboy.yaml:101` names `claude-sonnet-4-20250514`. The deprecations page lists it Retired on June 15, 2026, replacement `claude-sonnet-5-5`. `claude-haiku-4-5-20251001` (line 102) is Active with retirement "Not sooner than October 15, 2026", a floor already passed.
Evidence: fetched https://platform.claude.com/docs/en/about-claude/model-deprecations → `claude-sonnet-4-20250514 | Retired | April 14, 2026 | June 15, 2026`; `claude-haiku-4-5-20251001 | Active | N/A | Not sooner than October 15, 2026`.
Why: the API path produces no briefing today on any box. Task 1.0 is a precondition, not scope creep, and the ID change cannot wait behind A4.
Fix: Enemy Forces says "retired", not "unverified". 1.0's `[config]` commit sets both IDs. A4's kill criterion becomes "Sonnet 5.5 if Opus 5.5 reads worse; the agent backend on a workstation if both do". The run record carries `model` per call so the Haiku floor is visible when it bites.

### C2. Task 2.3's Standard cannot pass: `health` exits 1 on a box without the CLI
Claim (2.3, D12): `python main.py health` exits 0 on the server; "every health line OK".
Checked: `src/pipeline.py` `health_check()` sets `results["claude_cli"] = runner.is_available()` unconditionally; `src/agent_runner.py:206-212` returns False when `claude --version` fails; `main.py:244-254` exits 1 when any line is FAILED. D2 puts no CLI on the server.
Fix: in 1.5, `health` reports `claude_cli` as skipped when the roster backend is `api`, and the slack line as skipped when no token is set; or D12's proof drops `health` and keeps `source` plus the dev-channel `run`. Add the CliRunner test: roster `api`, no CLI, exit 0.

### C3. Two Standards cannot both hold: who writes the run line, and when
Claim: 1.1 "`DailyPipeline.run` appends one line on every path, including the `except` path"; 1.4 "success: `slack_ts` in the run line"; D5 "written last"; `--slack` is a `main.py` flag; D6 exits with `Configuration error:` before sourcing.
Checked: `main.py:82-116` builds the pipeline and calls `pipeline.run()`; `src/pipeline.py:357-435` has no delivery hook and returns before anything in `main.py` runs. A Slack call in `main.py` runs after the line is written, so `slack_ts` cannot be in it. The D6 exit happens before `DailyPipeline` exists, so that path writes no line.
Fix: `DailyPipeline(config, backend="auto", deliverer=None)`. `run()` calls `deliverer(result)` after `_save_briefing` and `history.record` (`pipeline.py:395-399`), inside try/except, sets `result.slack_ts` or `result.slack_error`, then writes the record in a `finally`. `main.py --slack` builds the Slack deliverer. D6 states that a configuration error writes no line. This is also S1's seam.

## Warnings

### W1. Task 1.0 removes the API path's only determinism lever and does not say so
Claim (1.0, D3): drop `temperature` from both call sites; raise scoring `max_tokens` with `effort: low` "because thinking is on by default".
Checked: `src/selector.py:228` `temperature=0.0` is the Pillar 4 control gap G4 names. The platform confirms the premise: on Opus 5.5, Sonnet 5.5 and Haiku 5.5, "non-default `temperature`, `top_p`, or `top_k` values return a 400 error on every request, regardless of whether thinking is used", and from API version 2026-10-21 any value does. It also offers the replacement: "Claude Haiku 5.5 also has thinking on by default and accepts `thinking: {type: "disabled"}` at effort `high` or below." Sonnet 5.5 "rejects `thinking: {type: "disabled"}` with a 400 error"; Opus 5.5 cannot turn thinking off.
Evidence: fetched https://platform.claude.com/docs/en/build-with-claude/thinking, sentences quoted; `grep -n temperature src/*.py` → `selector.py:228`, `distiller.py:360`; no `top_p` or `top_k` anywhere.
Fix: the scoring call sends `thinking={"type": "disabled"}` and `output_config={"effort": "low"}`; `max_tokens` stays 200 and `content[0]` stays text. Read blocks by type anyway at `selector.py:232` and `distiller.py:364`. Make the thinking mode a validated config key (`claude.scoring_thinking`, default `disabled`) because a Sonnet scoring model would 400. D3 records that distill determinism stays unmeasured (G4 open). D14's pin holds: SDK 0.120.2 accepts both parameters.
Evidence: `inspect.signature(anthropic.resources.messages.Messages.create)` → parameters include `['output_config', 'temperature', 'thinking', 'top_k', 'top_p']`.

### W2. A2's falsifier writes, and its kill criterion is an unknown dressed as a fact
Claim (A2): falsifier "call `files.getUploadURLExternal` once"; kill criterion "adding scopes rotates the shared token".
Checked: `getUploadURLExternal` allocates an upload slot, so the probe writes (verifying-claims rule 6). Slack's lifecycle page says existing installs "keep their current tokens with the old scopes" and must reinstall for new ones; it does not say whether the `xoxb-` value changes. `auth.test` needs no scope and lists none.
Evidence: fetched https://docs.slack.dev/app-management/distribution/ and https://docs.slack.dev/reference/methods/auth.test; quotes as above.
Fix: A2a "the app holds `files:write` now": read the Scopes page in the Slack admin UI. A2b "a reinstall keeps the token value": reinstall right after a `daily_weather` hourly tick and watch the next one; blast radius names `daily_weather`'s three crontab lines. Drop `reactions:read` from Wave 1's question (Wave 3 only). Add `not_in_channel` to 1.2's `ok:false` tests: the bot must be invited to both channels.

### W3. Wave 1's gate posts to an unknown channel on the wrong backend
Claim (exit criterion, open decision 3): "one `--slack` run from this workstation posts to the dev channel".
Checked: both rostered workstations are `backend: agent` (`config/project.yaml:44-52`), so auto mode runs AgentRunner and the gate proves the Slack path, not D2's API path. The channel is whatever `.env` names. `load_dotenv` defaults `override=False`, so a shell variable wins.
Evidence: `inspect.signature(load_dotenv)` → `override: bool = False`.
Fix: the gate command is `PAPERBOY_SLACK_CHANNEL=<dev id> .venv/bin/python main.py run --slack --backend api`. Open decision 3 closes.

### W4. Two line claims the plan rests on are off
`daily_weather`'s Slack client is 81 lines, not 69. `SelectionHistory` starts at `src/pipeline.py:40`, not 42. The other code claims hold (Focus questions, item 1).
Evidence: `wc -l src/daily_weather/utils/slack.py` → `81`; `sed -n '40p' src/pipeline.py` → `class SelectionHistory:`.

### W5. The assumption that collapses the most is not in the table
Open decision 5 says: no dedicated key, "no server backend and stops at Wave 1". That is the load-bearing belief, above A3 and A4; give it a row (A0: falsifier "the lead answers today"; blast radius D2, Waves 2 and 3). Missing too: tzdata in `debian:bookworm-slim` for `TZ` (daily_weather's 06:30 post lands at 06:30 local, so it holds there; name it), and the Haiku 4.5 floor (C1). A8 is misframed: with no `env_file`, the container sets only `HOME` and `TZ`; the real question is whether `load_dotenv()` finds the clone's `.env` from `src/config.py` upward, which python-dotenv's frame walk does. Keep the falsifier, fix the sentence.

## Suggestions

### S1. The seam: a `deliverer` parameter, not a boolean
`--slack` on `run` is the right user switch. Inside the pipeline the seam is a callable `(PipelineResult) -> receipt` injected at construction (C3's fix). Phase 4 adds `audio_path` to the result; Phase 5 adds a feed deliverer beside the Slack one. `src/tts_interface.py` is synthesis, not delivery; leave it. No ABC module, no registry, no config section until a second deliverer exists.

### S2. Cuts
1.5 and `auth_test` go if C2 is fixed by dropping `health` from the proof. `src/report.py` folds into `slack.py` (the plan already allows it under 80 lines). `config_sha256` is undefined (the YAML bytes miss `USER_CONTEXT`; the resolved config includes it): define it as canonical JSON of `PipelineConfig` minus secrets, or cut it. `reactions:read` leaves Wave 1.

### S3. D11's exit 1 collides with "no briefing"
A saved briefing with a failed post and a run with no briefing both exit 1; only the record tells them apart, and its reader is Wave 3. Exit 3 for delivery failure, or state the collision as accepted.

### S4. A5 is nearly moot; the weekend is the timing fact
`src/sourcer.py:92-98` sorts by `SubmittedDate` with a 7-day cutoff, so a 05:30 run sees a week whatever the announcement hour. arXiv posts no new announcements on Friday and Saturday nights (UNVERIFIED this turn; https://info.arxiv.org/help/availability.html), so Saturday and Sunday runs choose from Friday's pool minus dedup. Read `score` by weekday from the record; consider five ticks a week.

### S5. D8 and D13 pass the boundary line
`paperboy` is a name the App YAML assigns and resolves nowhere; HOME-STORAGE.md's own roster sentence is keyed by hostname (`machines.<host>.references`), and `Muninn` and `Nidhogg` are tracked already. daily_weather's HERALD D14 reached the same verdict. `output/` and `.env` are ignored, so the record and the secrets stay out. `~/paperboy` in `update-server.sh` is tilde-relative, which the doctrine allows. One sentence in D8 citing HERALD D14 closes it.
Evidence: `git check-ignore -v output/briefings/run_history.jsonl .env` → `.gitignore:210:output/`, `.gitignore:138:.env`.

### S6. Rows that are not test-first-able, and the gate
2.1 to 2.5 are hand steps (UI, ssh); A1 is device handling; 1.0's "A4 run read by the lead" is a human read inside a code task's Standard, so move it to A4's row. 1.3's "no em dash in any template" and 1.6's plant are grep-checkable. Wave 1's gate is right: a live post is the one check of the Slack shape that can fail; pin it per W3.

## Focus questions, with what held

1. **Pillar 4**: every cited line holds. `src/selector.py:228` `temperature=0.0`; `src/distiller.py:360` `temperature=self.config.claude.temperature`; `src/selector.py:232` `response.content[0].text` (also `distiller.py:364`, which the plan omits); `src/pipeline.py:397-399` records on the keyword-only path; `src/config.py:119-121` `load_dotenv()` with no `override`; `src/agent_runner.py:521-524` `key.startswith("CLAUDE")`; `src/sourcer.py:98` UTC cutoff; `src/distiller.py:306` UTC `generated_at`, which `_save_briefing` formats into the filename; `main.py:54` `date.today()`. Same date and config gives the same selection on the keyword path; the API path loses its lever (W1).
2. **Pillar 2**: the briefing and the dedup record precede any delivery (`pipeline.py:395-399`) and nothing rolls them back; D5 and D11 are sound once C3 names the owner. Silent: the D6 config-error path (no line), a crash between the dedup write and the run line (reads as "no run"), and OOM (acknowledged).
3. **Pillar 5**: S1.
4. **Boundary line**: S5.
5. **D2, D3**: C1, W1. D2's facts match the headless check; the API key is right for the server. 1.0 is a precondition.
6. **Assumptions**: W2, W5, S4.
7. **Waves**: C2, W3, S6.
8. **Simplicity**: S2.

## Checks this review ran
- Suite: `.venv/bin/pytest -q; echo "exit=$?"` → `274 passed in 1.54s`, `exit=0`; `.venv/bin/python -V` → `Python 3.12.13`.
- Tree: `git status --porcelain` → three untracked docs only, at cfde101.
- Plan prose: em dashes outside headings and tables → 0; LANGUAGE.md banned words → 0. No prose findings.
- `.github/workflows`: `ls` → No such file or directory. `requirements.txt` → `anthropic>=0.40.0`; installed `0.120.2`.
