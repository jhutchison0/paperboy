# CONOP COURIER — Unattended Daily Run on the Home Server, Delivered to Slack

**Status**: Approved 2026-10-24 (append-only from here; changes land in the Status Log). Drafted 2026-10-22; code-reviewer GO WITH FIXES and pipeline-sme SUPPORTING WITH CHANGES folded the same day; D1 and D2 closed by the lead 2026-10-23; D4, D8, D15 and D17 closed by the lead 2026-10-24.
**Date**: 2026-10-22, amended 2026-10-23 and 2026-10-24
**Lead**: jhutchison0
**Parent task**: `docs/tasks.md` Focus steps 4 to 6 and the P1 task

---

## Problem

Nothing runs paperboy unattended, nothing records a run, and no failure is visible. Since the pipeline first produced a briefing, every episode has needed a person at a keyboard to run `python main.py run`, find the file under `output/briefings/`, and carry it to NotebookLM; the register says so in gap G8 (how many days produced a briefing, how many were heard) and gap G9 (whether the reader agreed with the selection). The mission's word is daily, and the roadmap's Phase 3 is "hands-off daily pipeline execution".

COURIER puts one scheduled run a day on the always-on home server, on the Max subscription the lead already pays for, writes the briefing to a folder on the home share, posts a short summary of the run to a Slack channel as the reminder to go read it, and writes one record line per run that `/session-start` can read. It touches the save stage and what follows it, plus two small changes to the Agent backend so it runs headless. Sourcing, selection and distillation do not change.

---

## Situation

### Friendly Forces (what we have)

- A one-shot CLI with meaningful exit codes: `python main.py run` exits 0 on success, 2 on partial (paper selected, briefing failed, not recorded for dedup), 1 on failure (`main.py:82-116`, `src/pipeline.py:357-435`). Each run is a fresh process, which is what a cron tick wants.
- The Agent backend, `src/agent_runner.py`: `claude -p` as a subprocess, with timeouts, one retry, partial-output capture and failure kinds. It has produced every briefing since June, including the 2026-07-20 kernel run, on both rostered workstations, which are `backend: agent` for the stated reason "subscription via Claude CLI, no API spend" (`config/project.yaml:44-52`). The workstation's CLI is 2.1.310.
- The documented headless route for a subscription: `claude setup-token` prints a one-year OAuth token "for CI pipelines, scripts, or other environments where interactive browser login isn't available", consumed through `CLAUDE_CODE_OAUTH_TOKEN`, requiring "a Pro, Max, Team, or Enterprise plan", able "only [to] make model requests". Source: https://code.claude.com/docs/en/authentication.md, "Generate a long-lived token" and "Authentication precedence" item 5, fetched 2026-10-23.
- Cross-run dedup in `output/briefings/.selection_history.json` with a 30-day cooldown (`SelectionHistory`, `src/pipeline.py:40-193`), so a daily schedule never repeats a paper. The history travels with the briefings folder.
- A machine roster with a per-box backend preference (`src/machine.py`, auto mode in `src/pipeline.py:277-355`), so the server states `backend: agent` without a flag on the cron line.
- `PipelineResult` already carries status, counts, the selected paper, the briefing path and the error. The selector already Claude-scores the keyword top five and returns them scored; the pipeline keeps only the first (`src/pipeline.py:448`), so listing the day's top five costs no extra call. `ScoredPaper.reasoning` (`src/models.py:86`) is Claude's one-line "why this paper".
- `.env` on this workstation already holds `SLACK_BOT_TOKEN` and `PAPERBOY_SLACK_CHANNEL` (set 2026-10-22 by the lead; values never printed). The bot posts for `daily_weather` today, so `chat:write` is in hand.
- Prior art in the sister repo `daily_weather`, running on the same server since 2026-10-03: the Custom App pattern (`docs/runbooks/home-server-custom-app.md`), the deploy script (`deploy/update-server.sh`), an 81-line Slack client, a 24-hour canary under a dev channel before the real one, and a newer pattern of replies in the morning post's thread that expand on it.
- The home-storage doctrine (`.claude/skills/lake-conventions/HOME-STORAGE.md`): a role-named `HOME_*` variable in `.env` carries the real folder on each machine, the server-side path on the device and the client path on a workstation, and nothing in git names either.
- The proposal, the headless check with its 2026-10-23 addendum, and the two reviews, each citing its page or line (References).
- 274 tests, the shift-left audit hook, `/pcc`, the gap register and `src/gaps.py`.

### Enemy Forces (what works against us)

- **The strip.** `src/agent_runner.py:521-524` deletes every environment variable that starts with `CLAUDE`, so `CLAUDE_CODE_OAUTH_TOKEN` never reaches the subprocess and headless auth fails until that one name is kept. `ANTHROPIC_AUTH_TOKEN` survives the strip and outranks the OAuth token (precedence item 2), so it must be stripped explicitly.
- **The token expires after one year**, and "Once the stored login expires and can't be refreshed, each model request fails" (authentication.md, "Renew an expiring login"). The failure is loud under this plan (a failure post and a run line), not silent; the renewal date is a comment beside the token in the server's `.env`, and the deploy script prints it.
- **Anthropic's stated direction for scripts is bare mode with an API key.** "`--bare` is the recommended mode for scripted and SDK calls, and will become the default for `-p` in a future release", and "In bare mode, Claude Code never reads OAuth credentials" (https://code.claude.com/docs/en/headless.md, fetched 2026-10-23). A CLI update that flips that default would break the server's auth at the next tick. Containment: the server's CLI is pinned to a version and does not auto-update (`DISABLE_AUTOUPDATER=1`, a native-installer version pin), and a failure post names the day it happens.
- **One usage pool.** The subscription's five-hour and weekly limits are shared between the lead's interactive work and the 05:30 run; "Advertised usage limits for Pro and Max plans assume ordinary, individual usage of Claude Code and the Agent SDK" (https://code.claude.com/docs/en/legal-and-compliance.md). One run is about six model calls a day. A week that exhausts the weekly cap fails the run loudly.
- **The CLI must be on the container's `PATH`.** The native installer puts the binary at `~/.local/bin/claude`; `debian:bookworm-slim`'s default `PATH` does not include it, and the app account cannot install anywhere else. Auto mode's `is_available()` runs `claude --version` and falls through to detection with a warning when it fails.
- **The API fallback path produces no briefing today, on any box.** `config/paperboy.yaml:101` names `claude-sonnet-4-20250514`, Retired on June 15, 2026; `:102` names `claude-haiku-4-5-20251001`, Active with a retirement floor that has passed (https://platform.claude.com/docs/en/about-claude/model-deprecations, fetched by the code-reviewer 2026-10-22). Both call sites also send `temperature` (`src/selector.py:228`, `src/distiller.py:360`), which current models reject with a 400, and read `response.content[0].text` (`:232`, `distiller.py:364`), which a thinking-first response breaks. The fallback is repaired in Wave 1 (task 1.0) but is not on the server's path.
- **One box, no self-report when dead.** The app account has no sudo and no Docker; it cannot restart the App; supercronic skips a run missed during a restart; a container killed by the OOM killer posts nothing.
- **`health` exits 1 on a box where one check fails.** `health_check()` sets `claude_api` False without a key and `main.py:244-254` exits 1 when any line is FAILED, so `health` is not a proof step on the server until task 1.5 reports an unconfigured backend as skipped.
- **Slack's shape limits.** `chat.postMessage` text is recommended under 4,000 characters and truncated above 40,000. The briefing never goes to Slack (D4), so no new scope is needed; the bot must be a member of any channel it posts to (`not_in_channel`).
- **The clock is split.** The arXiv cutoff (`src/sourcer.py:98`) and the filename date (`src/distiller.py:306`) use UTC; `--date` uses the local date (`main.py:54`). An evening run in a US zone names the file for tomorrow. arXiv posts no new announcements on Friday and Saturday nights (UNVERIFIED; https://info.arxiv.org/help/availability.html), so weekend runs choose from Friday's pool minus dedup.
- **A proof run can burn a paper.** `run --backend keyword-only` records the selection for dedup (`src/pipeline.py:397-399`).
- **The repo goes public at Focus step 3.** Secrets, logs and artifacts in GitHub are then public; the deploy script's CI check (`gh run list`) has no workflow to read here (`.github/workflows` does not exist).
- **Dependency drift between boxes.** `requirements.txt` pins `anthropic>=0.40.0`; this workstation runs 0.120.2; a fresh install on the server would take the 1.x line, which changed its HTTP layer.

### Terrain (the ground we operate on)

- TrueNAS SCALE 25.10 on a Pentium Gold 8505 with 14 GB RAM and Docker 28, CPU only; apps run as least-privilege accounts under Custom Apps defined in the UI; `daily_weather`'s Ollama service already holds up to 8 GB there. Paperboy's process is small: Python, arxiv, feedparser, one CLI subprocess at a time. The lead's workstation mounts the home share; NotebookLM uploads happen there.
- The terms, as the docs state them. OAuth "is intended exclusively for purchasers of Claude Free, Pro, Max, Team, and Enterprise subscription plans and is designed to support ordinary use of Claude Code"; the restrictions name "developers building products or services", third parties offering Claude.ai login "into their own applications", and routing "requests through Free, Pro, or Max plan credentials on behalf of their users"; and the same section says the policy does not "prevent an end user from signing in to the unmodified Claude Code binary with their own Claude subscription" (legal-and-compliance.md, "Authentication and credential use", fetched 2026-10-23). One person's daily job, on their own subscription, through the unmodified CLI, by the documented `setup-token` route, is inside that text. This is the plan's reading, not legal advice; the lead owns it.
- The boundary line: no hostname, IP, UNC path, share or dataset path in any tracked file; `.env` holds the real values per machine. The roster is tracked and keyed by hostname; `Nidhogg` and `Muninn` already sit in it. `output/` and `.env` are gitignored (`.gitignore:210`, `:138`), so the record, the token and the secrets stay out.
- The Focus order: step 3 closes Phase 2 and flips the repo public; step 4 opens Phase 3 with the run-history log. COURIER's Wave 1 is step 4's log.
- Gap G5's universe is the rostered boxes; the server's clone joins it in Wave 2, post-rewrite by construction. G8 and G9 are the gaps this plan collects for; G4's API arm text changes when task 1.0 lands.
- Pillar 4: same date and config, same output. The Agent path's model is the subscription's default and is recorded per run; the API fallback's IDs change once, in a commit before any fallback run.

### Assumptions

| # | Assumption | Cheapest falsifier | Blast radius if wrong | Kill-criterion |
|---|---|---|---|---|
| A0 | A `setup-token` token in the server's `.env` authenticates `claude -p` unattended, as the account, inside the container | Generate the token on the workstation, put it in the server's `.env`, run `claude -p "Reply with OK"` as the account on the host, then watch the first tick (Wave 2 tasks 2.2 and 2.5) | D2; Waves 2 and 3 | Auth fails on the host or in the container: the API fallback (task 1.0) with a dedicated key, the lead's decision at that point |
| A1 | The lead opens the day's briefing from the desktop by the filename in the post, from the shared folder `HOME_BRIEFINGS_ROOT` names on the server | The first canary morning: find the file named in the post and upload it to NotebookLM (2 minutes) | D4, D15 | Not reachable or over a minute of handling a day: post the file to the Slack thread after all (one scope, one call) |
| A2 | The bot token posts to the dev channel and the real channel | `auth.test` once, then the first dev post | D4 | `not_in_channel`: invite the bot; another error: a second Slack app for paperboy |
| A3 | The container reaches arXiv, the four feed hosts, Anthropic's endpoints and Slack | `python main.py source` and, after task 1.5, `python main.py health` as the account, before the App exists | Approach A whole | Any host blocked: Approach B |
| A4 | The CLI binary installed by the account on the host runs inside `debian:bookworm-slim` through the bind mount, with `PATH` set in the App YAML | `claude --version` on the host as the account, then the first tick's log line naming the backend | D2 on the container side | It does not run: an `apt`-repository install in the App image is the fallback, or Approach B |
| A5 | Weekend runs select papers the reader values | `score` and the G9 reaction by weekday after four weeks of record | D9 | Saturday and Sunday rank lower on both: five ticks a week |
| A6 | The server and the container stay up | Days with no run line in 30 | Approach A | 2 silent days in 30: build the watchdog (Approach D) or move to B |
| A7 | Transient failures are rare | Share of `error` and `partial` lines over 30 days | D9 | Over 3 of 30: add the skip-if-done guard and a 06:15 retry tick |
| A8 | `load_dotenv()` finds the clone's `.env` from `src/config.py` upward when the App sets only `HOME`, `TZ` and `PATH`, so an `.env` edit is live at the next tick | Edit the channel in the server's `.env`, wait one tick, read the channel | D7 | Not found or not live: add `env_file` to the App and accept the restart |
| A9 | `TZ` works in `debian:bookworm-slim` (tzdata present) | The first tick's `started_at` in the record against the crontab's 05:30 | D9 | Off by the UTC offset: install tzdata in the App or write the crontab in UTC |
| A10 | One daily run fits inside the Max plan's limits beside the lead's interactive use | `error` lines whose text names a rate or usage limit, over 30 days | D2's economics | 2 of 30 runs limited: move the tick to a quieter hour, or the API fallback for the distill only |
| A11 | A reaction on the post is a verdict the reader will give | Reacted posts in 14 days | G9 only | Fewer than 7 of 14: replace with a one-line file entry at `/session-start` |

A0's host half and A4 run at the start of Wave 2, before the App exists; A0's container half is the first tick. A2 runs at Wave 1's gate. A1, A3 and A9 run at the start of Wave 2; A5 through A7 and A10 read the record Wave 2 produces; A8 runs on the first canary day. A11 is Wave 3's gate. `daily_weather`'s 06:30 post lands at 06:30 local on the same image, which is A9's prior evidence.

---

## Mission

Paperboy runs once a day on the home server, on the lead's subscription, writes the briefing to the home share, and posts a summary to Slack as the reminder, writing one record line per run, **in order to** deliver the daily briefing without a person at a keyboard and give the register its first measurements of cadence and reach (G8) and reader agreement (G9).

---

## Approaches Considered

| | Where it runs | State (dedup history, briefings) | Boundary line | Monthly cost | Main risk |
|---|---|---|---|---|---|
| A | Home server Custom App, as `daily_weather` | A folder on the home share, named by `HOME_BRIEFINGS_ROOT` in the server's `.env` | Clean: roster key is a name we assign, no path tracked | $0 (subscription already paid) | One box; a crontab change needs the UI |
| B | GitHub Actions on a cron schedule | Cache, artifact or a state branch, all weak | Clean, but the repo is public: logs and artifacts are readable | $0 hosting, plus an API key ($2 to $8): bare mode and Actions cannot use the subscription | Reading history and the tailored briefing leak; schedules auto-disable after 60 idle days |
| C | Workstation Task Scheduler | Local `output/` | Clean | $0 | Asleep at 05:30 on some nights (`daily_weather` gap G4) |
| D | A, plus an Actions watchdog that pings when no post landed | As A | As A, plus the bot token in GitHub secrets | $0 | More parts, wider secret blast radius |

### Approach A: Home server Custom App

Mirror `daily_weather`: a least-privilege account, a bare repo and a clone in its home, a host-built uv venv, the Claude CLI installed by the account, supercronic in a `debian:bookworm-slim` App with the home bind-mounted, one crontab line. Proven on this server by a sibling app; state stays on the box that already follows the home-storage rules; a code change is live at the next tick after a pull. Cost: a one-time setup of about nine lead-only steps and a single point of failure with no self-report.

### Approach B: GitHub Actions (bold alternative)

No hardware, no UI restarts, deploy is a merge. It loses on state, on privacy, and on cost: a hosted runner has no subscription login, so B needs the API key the lead does not want to pay for. `.selection_history.json` must survive between runs, and the three ways to keep it are poor: a cache that may be evicted, an artifact or a `state` branch that publishes which papers the reader was briefed on, daily, in a repo about to go public. Public-repo schedules are disabled after 60 days without activity, and the `schedule` event "can be delayed during periods of high loads" (GitHub docs, fetched by the proposer). B is the fallback if A3 or A6 fails.

### Approach C: Workstation

Free, and the only place the subscription backend is proven today. It fails the stated problem: the workstation sleeps, and a missed run is silent.

### Approach D: Hybrid

A, plus an Actions cron that reads the channel and pings when no post landed today. It closes the one failure A cannot report on itself. Deferred until A6 says it is needed.

**Recommendation**: Approach A. With the subscription as the backend, B's one advantage (no box) costs money every month, and the margin widens. The lead chose A on 2026-10-23.

---

## Design Decisions

Resolved 2026-10-22 unless dated otherwise. None is open.

- **D1 — Host: Approach A.** Closed by the lead 2026-10-23. Trigger to switch: A3 fails, or A6's kill criterion.
- **D2 — Backend on the server: the Max subscription through `claude -p`, authenticated by a `claude setup-token` token in the server's `.env` as `CLAUDE_CODE_OAUTH_TOKEN`, rostered `backend: agent`.** Closed by the lead 2026-10-23, reversing the first draft. The first draft chose an API key for three reasons; on re-reading the source pages two were overstated. The terms: the Claude Code docs document `setup-token` for "CI pipelines, scripts", and the legal page protects "an end user ... signing in to the unmodified Claude Code binary with their own Claude subscription" (Terrain). The expiry: one year, dated, and loud under this plan. The third reason, the `CLAUDE*` strip, is a one-line code change (task 1.2). The server's roster entry then matches the two workstations' stated convention, no API spend. The API path stays as the documented fallback, repaired in task 1.0, and needs no key until A0 or A10 fails. Residual risks, each named in Enemy Forces with its containment: the bare-mode default change, the shared usage pool, the yearly renewal.
- **D3 — The Agent path uses the subscription's default model and records it per run; the API fallback moves to current IDs in task 1.0.** The CLI picks the model; `AgentRunner` reads `--output-format json` and records the model name from the response's usage block (task 1.9), so Pillar 4 has the model per run without a `--model` flag. For the fallback: scoring on `claude-haiku-5-5` with `thinking: {type: "disabled"}` and `output_config: {effort: "low"}` (so `max_tokens: 200` stands); distill on `claude-opus-5-5`, the claude-api skill's default, with no temperature. The `claude.temperature` key goes. Both call sites read the first `text` block by type. The retired ID cannot stay in a tracked config that is about to go public. G4's API arm becomes "API at the model default".
- **D4 — Slack carries a summary and the reminder; the briefing stays on the home share.** Closed by the lead 2026-10-24. One `chat.postMessage` per run. The post, in order: title and arXiv link; Claude's one-line reasoning (the "why this paper"); the abstract trimmed to three sentences or 600 characters, whichever is shorter; the day's top five, one line each with rank, title and score; the briefing's filename and "on the home share"; the reaction legend (`:white_check_mark:` agree, `:one:` to `:five:` the rank you would have picked, `:headphones:` heard); one telemetry line (status, backend, model, duration, words). Under 4,000 characters, readable on a phone. Partial (exit 2) posts a warning, the title, the error, and "not recorded for dedup; the next run retries". Failure (exit 1) posts the error cut to 500 characters. Replies in the post's thread that expand on it, `daily_weather`'s newer pattern, are a later amendment; the parent's `slack_ts` in the record is the hook. Rejected for the briefing itself: a file upload to Slack (the lead's call: Slack is the reminder, not the store), per-section thread replies (eight messages to reassemble), one inline message (over the recommended length).
- **D5 — The run record is `run_history.jsonl` beside the briefings, one JSON line per run, written in a `finally` after delivery.** Fields: `date` (UTC, as the filename), `started_at`, `duration_s`, `status`, `backend`, `machine`, `scoring_model`, `distill_model`, `selected_id`, `score`, `top_candidates` (id, title, score; up to `top_k_for_claude`), `briefing_path`, `words`, `papers_fetched`, `articles_fetched`, `error`, `slack_ts`, `slack_error`, `git_sha`, `config_sha256`. `config_sha256` is the SHA-256 of the effective `PipelineConfig` after env overrides, serialized as canonical JSON with `anthropic_api_key` removed; `user_context` is hashed, never written. A Slack failure never suppresses the line; a record-write failure logs and never changes the exit code. A configuration error under `--slack` (D6) exits before the pipeline exists and writes no line. The file is the record and Slack is the display. A day with no line is itself the finding. About 500 bytes a day; no rotation. Universe: the delivery box's folder; blind to runs that write elsewhere, and to days before the file existed.
- **D6 — One switch, `--slack`; no profiles.** Without the flag no run posts. With it and no token or channel, the run exits 1 with `Configuration error:` before sourcing. "Dry unless the channel is set" is rejected because this workstation's `.env` already names a channel, so every test run would post. The canary posts to a dev channel by the value of `PAPERBOY_SLACK_CHANNEL` in the server's `.env`; a shell variable wins over `.env` (`load_dotenv` defaults `override=False`), which is how a workstation gate run names the dev channel.
- **D7 — The app reads `.env`; the App YAML sets only `HOME`, `TZ` and `PATH`.** `src/config.py:119-121` calls `load_dotenv()`, which finds `.env` by walking up from `src/config.py` and does not override variables already set, so an `.env` edit on the server (the channel, the token at renewal, the folder) is live at the next tick with no restart (A8 checks it). `PATH` is in the YAML because the CLI lives under the account's `~/.local/bin` (A4).
- **D8 — The server enters the tracked roster under the container's hostname, `paperboy`, in Wave 2 with its clone.** Closed by the lead 2026-10-24: `paperboy` is the app's name on the NAS and the roster key. The App YAML sets `hostname: paperboy`; the entry carries `role: delivery`, `scope: [personal]`, `backend: agent`, no references. The name is ours, resolves nowhere on the LAN, and the server's own hostname is never written; `Nidhogg` and `Muninn` are already tracked, HOME-STORAGE.md's own roster sentence is keyed by hostname, and `daily_weather`'s HERALD D14 reached the same verdict.
- **D9 — Schedule: one tick at 05:30 local, seven days a week, `TZ` in the App YAML, no `--date`.** Morning only, so the UTC date and the local date agree, and a quiet hour for the shared usage pool (A10). The 7-day cutoff sorted by submission date sees the week whatever the announcement hour; the weekend question is A5's. One attempt; a retry tick needs the skip-if-done guard first and waits for A7.
- **D10 — HTTP for Slack: stdlib `urllib.request`, no new dependency.** One call per run (`chat.postMessage`), a 10-second timeout, one retry on 429 honoring `Retry-After`, no retry on timeout (the post may have landed), `& < >` escaped for mrkdwn at the boundary. The token is read from the environment at call time and never enters a config object. `auth.test` serves `health`.
- **D11 — Exit codes.** 0 success; 2 partial; 1 failure; 3 delivery failed after a saved briefing, with the run line keeping `status: success` and `slack_error` set. The briefing and the dedup record are never rolled back for a delivery failure. Exit 3 is new so a saved-but-undelivered run never reads as a failed one.
- **D12 — The delivery seam is a callable, not a flag inside the pipeline.** `DailyPipeline(config, backend="auto", deliverer=None)`; `run()` calls `deliverer(result)` after `_save_briefing` and `history.record` (`src/pipeline.py:395-399`) inside try/except, sets `result.slack_ts` or `result.slack_error`, then writes the record. `main.py --slack` builds the Slack deliverer. Phase 4 adds `audio_path` to the result; Phase 5 adds a feed deliverer beside the Slack one; thread replies are a second call inside the same deliverer. No ABC, no registry, no config section until a second deliverer exists. `src/tts_interface.py` is synthesis, not delivery, and stays as it is.
- **D13 — The headless hardening of `AgentRunner` (task 1.2).** The clean environment keeps `CLAUDE_CODE_OAUTH_TOKEN` and strips `ANTHROPIC_AUTH_TOKEN` as well as `ANTHROPIC_API_KEY`; it sets `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` and `DISABLE_AUTOUPDATER=1` for the subprocess. The invocation adds `--no-session-persistence` and a tools-off flag (the headless check names `--tools ""` and `--disallowedTools "*"`; the implementer confirms the exact spelling against `claude --help` on 2.1.310 and pins it with a test that reads the argv). `--bare` is not used: it does not read OAuth credentials. cwd stays the temp dir.
- **D14 — Deploy: `daily_weather`'s `update-server.sh` shape, adapted.** Clone name; `uv pip install -r requirements.txt` when `requirements.txt` changed; the CI check skipped while no workflow exists (print a reminder instead); the proof step is `python main.py health` (after task 1.5) plus `python main.py source`, never `run --backend keyword-only`. The script prints `claude --version` on the clone and the token's renewal comment from the server's `.env`, and runs `git cat-file -e 'c06e8ba^{commit}'`, G5's collector for this box. A crontab change still needs the App restarted in the UI.
- **D15 — The first `HOME_*` variable arrives now: `HOME_BRIEFINGS_ROOT`.** Closed by the lead 2026-10-24. When set, it replaces `pipeline.output_dir`: the briefings, the dedup history and the run record live there. On the server it names a folder on the shared dataset the lead's workstation mounts; on a workstation it may name the client path for a manual run against the same folder, or stay unset. One deviation from HOME-STORAGE.md's "no default" rule, stated here: when the variable is unset the YAML default `./output/briefings` applies, because that is the workstations' existing behavior and a 30 KB briefing is not bulk data. `.env.example` carries the name with a placeholder; nothing tracked names a folder.
- **D16 — Pin `anthropic` below 1.0 in `requirements.txt` for this cycle**, so the server installs the line the workstation runs (0.120.2 accepts `thinking` and `output_config`); the 1.x upgrade is its own task. Pin the Claude CLI on the server to the workstation's version (2.1.310 on 2026-10-24) with the native installer's version argument.
- **D17 — Order against the Focus.** Closed by the lead 2026-10-24 ("let's roll"): Wave 1 first, on a topic branch merged at the code-reviewer's gate; the v0.3.0 CHANGELOG entry names it when Phase 2 closes. Wave 2 may run either side of the public flip. The commit that sets `phase_3: in_progress` also marks every Phase 3 line in `docs/design/roadmap.md` built or declined with its trigger, so Phase 3 can close by predicate; it amends Pillar 4's backfill sentence (`docs/design/pillars.md:83`) at the same time.

ADR filter: D1 and D2 are each reversible by one roster line and one `.env` line, so neither passes "hard to reverse". No ADR.

---

## Measures of Success

- **MOP**: suite green on this box and on the server's venv; `/pcc` clean; the boundary-line test passes on the tree and fails on a planted UNC path (calibration rule); every code-reviewer Critical and Warning addressed or answered in the review record; one pinned gate run from the workstation (`PAPERBOY_SLACK_CHANNEL=<dev id> .venv/bin/python main.py run --slack`, the agent backend by roster) posts the summary to the dev channel.
- **MOE 1** (measurable 30 days after Wave 2 exits): a `success` line with a `slack_ts` by 06:00 local on at least 27 of 30 days.
- **MOE 2** (measurable 14 days after Wave 2 exits): a `headphones` reaction (episode produced and heard) on at least 10 of 14 posts. This is G8's second half; the Wave 3 probe reads it.
- **MOE 3** (measurable 14 days after Wave 3 exits): a verdict reaction on at least 7 of 14 posts, and the agreement rate reported in G9's shape (a rank, exact; agreements of N reacted of M posted).

**Calibration**: the run record is a measurement, not a gate. The one gate, the boundary-line test, must catch a planted UNC path (`\\<host>\<share>`, written here as a placeholder so this sentence does not trip it) and a planted IPv4 literal in a fixture before it guards a commit.

---

## Wave Breakdown

Wave 1 is at TCS level. Wave 2 is at TCS level because the runbook already exists and worked twice; its rows are hand steps (UI, SSH) and are checked by command, not by test. Wave 3 stays at sketch level until the first run lines exist.

### Wave 1 — The record and the delivery (code, on `topic/pipeline-courier-wave1-20261024`)

- **Team**: `feature-development.md` with `pipeline-sme` added (a new stage follows save): two python-prototyper instances with disjoint files, test-runner, code-reviewer, pipeline-sme. The proposer's work is done.
- **Ownership**: prototyper A (delivery) owns `src/slack.py`, `tests/test_slack.py`, `tests/test_boundary_line.py`, `deploy/`, `.env.example`, `README.md`. Prototyper B (pipeline) owns `src/pipeline.py`, `src/agent_runner.py`, `main.py`, `src/config.py`, `src/selector.py`, `src/distiller.py`, `config/paperboy.yaml`, `requirements.txt`, and every other file under `tests/`. The lead owns `config/project.yaml` and commits.
- **Tasks**, each test-first per the shift-left skill:

  | Task | Condition | Standard |
  |---|---|---|
  | 1.0 (B) API fallback on current models: both IDs per D3 in their own `[config]` commit; `temperature` and the `claude.temperature` key removed; scoring sends `thinking: disabled` and `effort: low`; both call sites read the first `text` block by type | Tests with mocked responses whose `content` begins with a thinking block, for the selector and the distiller; the config validation test for the removed key; a test that greps the two files for `temperature` | Both call sites parse a thinking-first response; no sampling parameter in any SDK call; `max_tokens: 200` stands for scoring; the YAML comment names the Haiku-class constraint on the scoring model |
  | 1.1 (B) Run record and the top five: `PipelineResult` gains `backend`, `machine`, `scoring_model`, `distill_model`, `started_at`, `duration_s`, `top_candidates`, `slack_ts`, `slack_error`; `_source_and_select` returns the scored top five and selects the first; `run()` writes one D5 line in a `finally` after delivery | Unit tests on a tmp output dir for success, partial, error, the `except` path, and an unwritable record path; a determinism test on `config_sha256` | One line per run with D5's fields; `top_candidates` has up to five entries; a record-write failure logs a warning and the exit code is unchanged. Closes the P3 task "record the backend in PipelineResult and a config hash" |
  | 1.2 (B) `AgentRunner` headless (D13): `_build_clean_env` keeps `CLAUDE_CODE_OAUTH_TOKEN`, strips `ANTHROPIC_API_KEY` and `ANTHROPIC_AUTH_TOKEN`, sets `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` and `DISABLE_AUTOUPDATER=1`; `_invoke` adds `--no-session-persistence` and the tools-off flag | Tests with a fake `Popen` that captures `env` and argv: the token survives, the two Anthropic names do not, the flags are present; the existing `test_agent_runner.py` stays green | A headless token reaches the subprocess; a workstation run with no token behaves as today (the stored login) |
  | 1.3 (B) Delivery seam: `DailyPipeline(..., deliverer=None)` calls `deliverer(result)` after save and record, inside try/except (D12) | Tests with a deliverer that returns a receipt, one that raises, and none | The briefing and the dedup record are untouched by a raising deliverer; `slack_error` holds its message; the record line still has `slack_ts` when it returns |
  | 1.4 (A) `src/slack.py`: `post_message(text, channel, thread_ts=None) -> ts`, `auth_test() -> dict`, `SlackError`; the token read from the environment at call time; `build_message(result) -> str` for success, partial and error per D4 | Tests with a fake `urlopen` (no network): `ok:false` with `not_in_channel`, HTTP 429 with `Retry-After`, a timeout; table-driven tests over three result fixtures for the texts | `ok:false` raises `SlackError` with Slack's error string; one retry on 429 then raise; no retry on timeout; mrkdwn escaping of `& < >`; the success text under 4,000 characters in D4's order with the trimmed abstract, the top five, the filename and the reaction legend; partial and error name the error cut to 500 characters; no em dash in any template (grep) |
  | 1.5 (B) `--slack` on `run` (builds the Slack deliverer from `src.slack`; exit codes per D11) and `health` (an unconfigured backend reported skipped, not FAILED; a `slack` line via `auth_test` when the token is set) | CliRunner tests with the pipeline and the client mocked; `health` on a roster `agent` box with the CLI present and no API key exits 0 | Flag absent: no Slack call; flag present with no token or channel: exit 1 with `Configuration error:` before sourcing and no record line; success: exit 0 and `slack_ts` in the line; delivery failure after a saved briefing: exit 3, `slack_error` in the line, briefing and dedup untouched; `health` is a usable proof step on the server (A3) |
  | 1.6 (A) `tests/test_boundary_line.py`: tracked files hold no UNC path, no IPv4 literal outside an allowlist, no `smb://` | The test, with a planted fixture that must fail | Passes on the tree; fails on the plant; runs with the suite under `/pcc` check 2 |
  | 1.7 (A docs, B code) `.env.example` gains `PAPERBOY_SLACK_CHANNEL`, `SLACK_BOT_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN` with the `setup-token` note, and `HOME_BRIEFINGS_ROOT` with a placeholder, and loses the dead `OUTPUT_DIR` and `CONFIG_PATH`; README gains a Scheduling section and the headless note under Claude Backend Options; `src/config.py` reads `HOME_BRIEFINGS_ROOT` over `pipeline.output_dir` (D15); `requirements.txt` pins `anthropic<1` (D16) | `tests/test_state_block.py` green; `/pcc` check 5 at 0 MISSING; a config test for the override and for the unset default | No count or address added to any orientation file; the override is exact and the default unchanged |
  | 1.8 (A) `deploy/`: `README.md` (the paperboy instance of the runbook, placeholders only, with the CLI install pinned to a version, the `setup-token` step and the renewal comment's shape, `HOME_BRIEFINGS_ROOT` on the shared folder, the App YAML with `PATH`), `crontab` (one line: `30 5 * * * .venv/bin/python main.py run --slack`), `update-server.sh` per D14 | `test_boundary_line` passes; `bash -n deploy/update-server.sh` | No address in any file; the script refuses a dirty tree, a branch other than `main`, a clone with local edits; it prints the G5 line, the CLI version and the renewal comment |
  | 1.9 (B, recommended, not on the gate) `AgentRunner` reads `--output-format json`: the text from `.result`, the model from the usage block, replacing `_strip_preamble_json` and `_strip_preamble_markdown` | Tests with captured JSON fixtures from one local `claude -p "Reply with OK" --output-format json` | `distill_model` and `scoring_model` in the record name the CLI's model on the Agent path; the preamble heuristics are gone |

- **Exit criterion**: the suite is green; `/pcc` is clean; the pinned gate run (MOP) posts the summary to the dev channel on the agent backend (A2). The branch merges at the code-reviewer's gate.

### Wave 2 — The server (the lead by hand; checked by command)

- **Team**: the lead at the TrueNAS UI and over SSH. No agent touches the server.
- **Tasks**:

  | Task | Condition | Standard |
  |---|---|---|
  | 2.1 The account, alias, bare repo and clone, uv venv on Python 3.12 from `requirements.txt`, supercronic; the Claude CLI by the native installer pinned to the workstation's version (`curl -fsSL https://claude.ai/install.sh \| bash -s 2.1.310`), `DISABLE_AUTOUPDATER=1` in the account's `~/.claude/settings.json`; the briefings folder on the shared dataset | Runbook sections 1 to 5, adapted per `deploy/README.md` | `ssh <alias> 'id'` works; `supercronic -test deploy/crontab` prints "crontab is valid"; `~/.local/bin/claude --version` prints the pinned version; the clone is at `main`'s sha; the folder is visible from the workstation's mount |
  | 2.2 The token: `claude setup-token` on the workstation (it needs a browser), the value into the server's `.env` as `CLAUDE_CODE_OAUTH_TOKEN` with a comment naming its renewal date, beside the Slack token, the dev channel, `USER_CONTEXT` and `HOME_BRIEFINGS_ROOT`, mode 600 | A0's host half: `cd ~/paperboy && set -a && . ./.env && set +a && ~/.local/bin/claude -p "Reply with OK"` as the account | Prints OK; `claude -p` with the token unset and no stored login fails, which proves the token is what authenticates |
  | 2.3 The roster entry `paperboy` (D8) committed with the clone's first deploy | `tests/test_machine.py` green | `.venv/bin/python -m src.machine` on the host prints the host's own line (unrostered) and, inside the App, `paperboy (delivery, personal, backend: agent)` |
  | 2.4 Falsifiers A1, A3, A4 and A9 on the host, before the App exists | `.venv/bin/python main.py health` exits 0; `python main.py source` prints counts; one `run --slack` to the dev channel as the account; the briefing opened from the workstation by the filename in the post | Every health line OK or skipped; a summary in the dev channel; the file in the shared folder; the run line names `backend: agent` and the model; `started_at` agrees with the local clock |
  | 2.5 The App: `debian:bookworm-slim`, `user: <uid>:<uid>`, `hostname: paperboy`, `working_dir` the clone, the home bind-mounted (and the briefings dataset, if it is outside the home), `environment: {HOME, TZ, PATH: <home>/.local/bin:/usr/local/bin:/usr/bin:/bin}`, no `env_file` (D7), `command` supercronic with `deploy/crontab`, `restart: unless-stopped`, `mem_limit: 512m` | Saved in the UI outside 05:30 | `pgrep -u <account> -a` shows supercronic with the crontab; the first morning posts to the dev channel with `backend: agent` on its telemetry line (A0's container half, A4) |
  | 2.6 Canary, 7 mornings to the dev channel | The run record and the channel | 7 run lines, each `success` or `partial` with a `slack_ts`; A8 checked once by editing the channel value and reading the next post; then `PAPERBOY_SLACK_CHANNEL` set to the real channel in `.env`, no restart; the bot invited to both channels first |

- **Exit criterion**: seven consecutive run lines with a `slack_ts`, and the lead has produced one NotebookLM episode from a briefing fetched off the share.

### Wave 3 — Reading the record (sketch; detailed after Wave 2's first week)

- **Team**: python-prototyper + test-runner; decision-scientist reads the reaction encoding and the agreement rule before they are operationalized (a weighted decision is not in scope; a verdict scale is).
- 3.1 `src/runlog.py`: reads `run_history.jsonl` (a path, or stdin over SSH) and prints the last N days with status, missing days, and the newest briefing, in rule 8's two shapes; its docstring states D5's universe. `/session-start` gains a step that runs it over the account's alias from a workstation and renders `unchecked` with the blocker when the server is unreachable. G8 closes on its first reading, recorded in `docs/reviews/`.
- 3.2 The reaction probe: `reactions.get` on each parent `slack_ts`; encoding `white_check_mark` = agree, `one` to `five` = the rank the reader would have picked, `headphones` = episode produced and heard; no reaction is "no verdict", never "agree"; report agreements of N reacted of M posted, and heard of M posted. Needs `reactions:read`, the one new scope this plan ever asks for; its reinstall question is answered here, not in Wave 1.
- 3.3 Register amendments, per the SME review's section 4: G4's API arm and blocked decision; G5's universe and this box's collector; G8's collector cell and universe; G9's input, the "react to this message" clause and universe; one clause on G3 that the fixtures predate this plan and nothing here is heard. The P3 temperature-control task is rewritten: neither path controls sampling now.
- 3.4 (optional, the lead's call after a week of posts) thread replies that expand the summary, `daily_weather`'s pattern: a second `chat.postMessage` with `thread_ts`, inside the same deliverer.
- **Exit criterion**: the first G8 and G9 readings are recorded and the register rows carry their collectors' first dates. Phase 3 closes when every roadmap line carries its mark (D17) and the two readings exist.

---

## What We Do NOT Build

- **An API key for the server**: D2; the subscription is paid for and documented for this. The key is the fallback if A0 or A10 fails, and the lead's decision then.
- **A file upload to Slack**: D4; Slack is the reminder, the share is the store. A1's kill criterion reopens it.
- **TTS or audio**: Phase 4; the first bulk data.
- **A podcast or RSS feed**: Phase 5; Slack is the display until then.
- **Output rotation**: 150 KB of record and about 11 MB of briefings a year need none; the roadmap line is marked declined with that reason.
- **A backfill command**: dedup and the 7-day window give a missed day's papers their chance the next morning; the roadmap line and Pillar 4's sentence are amended (D17).
- **A retry tick and the skip-if-done guard**: wait for A7; the roadmap line carries the trigger.
- **The watchdog (Approach D)**: wait for A6.
- **Profiles or `config/local.yaml`**: one switch is enough (D6, D8).
- **A `--model` flag or config key for the Agent path**: the subscription's default, recorded per run, is enough until a reading says otherwise.
- **Thread replies in Wave 1**: a later amendment (3.4), once a week of summaries says what they should expand on.
- **A Slack Events endpoint or Socket Mode**: polling `reactions.get` from a probe needs neither.
- **A delivery ABC, registry or config section**: a callable is the seam until a second deliverer exists (D12).
- **A configurable scoring thinking mode**: scoring is pinned to a Haiku-class model by a comment; a key arrives with a second scoring model.
- **Per-feed counts in the run record**: the record is G8's collector; G6 has its own task.
- **The `anthropic` 1.x upgrade**: its own task after this cycle (D16).

---

## Agent and Team Design

None new; the existing roster covers it. Wave 1 is `feature-development.md` plus `pipeline-sme` per its scaling note for a new stage, with two python-prototyper instances under the README's one-owner-per-file rule. Wave 2 is the lead's. Wave 3 adds `decision-scientist` for the reaction scale only. The scope matrix needs two rows when Wave 1 starts: `src/slack.py` (python-prototyper writes; code-reviewer, test-runner read) and `deploy/` (python-prototyper writes; code-reviewer reads).

---

## Status Log

- **2026-10-23**: the lead chose Approach A, the home server (D1 closed), and asked for the backend to be re-checked against the subscription. The source pages (authentication.md, legal-and-compliance.md, headless.md, fetched that day) document `setup-token` for scripts and protect an end user's own subscription on the unmodified binary; D2 reversed to the subscription, task 1.2 added, A0 and A4 rewritten, A10 retargeted at usage limits, the cost column set to $0. The addendum to `docs/reviews/20261022_courier_claude_cli_headless_check.md` holds the quotes.
- **2026-10-24**: the lead closed the rest. `paperboy` is the app's name and the roster key (D8). Slack carries a summary and the reminder, never the briefing, which lives on the home share under the first `HOME_*` variable, `HOME_BRIEFINGS_ROOT` (D4, D15); the file-upload assumptions A2a and A2b fall away and the Slack permission question with them. Thread replies that expand the post, `daily_weather`'s newer pattern, are sketched as Wave 3 task 3.4. Wave 1 first, the v0.3.0 CHANGELOG naming it (D17). Approved; the Focus in `docs/tasks.md` carries the three waves as steps 4 to 6. Wave 1 opened on `topic/pipeline-courier-wave1-20261024`. Same day, two wording fixes: the Focus names the run-log reader by task number until the file exists (`/pcc` check 5 had flagged the path), and the calibration literal above is written as a placeholder.

---

## References

- Proposal: `docs/plans/20261022_courier_proposal.md` (proposer, 2026-10-22; the Slack and GitHub facts with their URLs)
- Challenge review: `docs/reviews/20261022_courier_conop_review.md` (code-reviewer, 2026-10-22; GO WITH FIXES, 3 Critical, 5 Warning, 6 Suggestion, all folded)
- Alignment review: `docs/reviews/20261022_courier_sme_alignment.md` (pipeline-sme, 2026-10-22; SUPPORTING WITH CHANGES, 4 Major, 8 Minor, all folded; the Focus draft in its section 6)
- Authentication and terms: `docs/reviews/20261022_courier_claude_cli_headless_check.md` (claude-code-guide, 2026-10-22; the lead's re-check addendum 2026-10-23 with verbatim quotes from https://code.claude.com/docs/en/authentication.md, https://code.claude.com/docs/en/legal-and-compliance.md and https://code.claude.com/docs/en/headless.md)
- Sister repo pattern: `daily_weather` `docs/runbooks/home-server-custom-app.md`, `deploy/README.md`, `deploy/update-server.sh`, CONOP HERALD D4, D9 and D14
- Doctrine: `.claude/skills/lake-conventions/HOME-STORAGE.md`; `docs/plans/CONOP-FORMAT.md`; `docs/gaps.md` G3, G4, G5, G8, G9; `docs/design/roadmap.md` Phase 3; `docs/design/pillars.md`
- Model facts for the fallback: https://platform.claude.com/docs/en/about-claude/model-deprecations and https://platform.claude.com/docs/en/build-with-claude/thinking (fetched by the code-reviewer 2026-10-22); prices from the claude-api skill's model table (cached 2026-10-06)
