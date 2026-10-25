# Proposal: COURIER, an unattended daily run reported to Slack

Status: proposal for debate, 2026-10-22. Proposer output; no code written. Facts I fetched carry an `Evidence:` line. Everything else about the future is marked **Inference**.

## Problem

Nothing runs paperboy unattended, nothing records a run, and no failure is visible (gaps G8 and G9 in `docs/gaps.md`). The pipeline is a one-shot CLI that exits 0, 2 (partial) or 1 (`main.py:82-116`). COURIER adds a scheduler, a Slack report of every run, and the run record that closes G8. It touches the save stage and what follows it; sourcing, selection and distillation do not change.

## Approaches

| | Where it runs | Persistence of dedup history and briefings | Boundary line | Cost per month (hosting) | Main risk |
|---|---|---|---|---|---|
| A | Home NAS Custom App, as daily_weather | Clone's `output/` on the apps dataset | Clean if the roster key is a container name and no path is tracked | $0 marginal | Single box; crontab change needs the UI |
| B | GitHub Actions cron, no NAS | Awkward: cache, artifact or a state branch | Clean; but the repo is public, so logs and artifacts are public | $0 (public repo) | Briefing text and reading history leak; schedule auto-disables |
| C | Workstation Task Scheduler | Local `output/` | Clean | $0 | Asleep at 05:30 on some nights |
| D | A, plus a GitHub Actions watchdog | As A | As A, plus the bot token in GitHub secrets | $0 | More parts, wider secret blast radius |

**A, NAS Custom App.** Mirror daily_weather: a least-privilege account, bare repo plus clone, host-built uv venv, supercronic in a `debian:bookworm-slim` App with the home bind-mounted, one crontab line. It works today for a sibling app on this exact box. State stays on the box that already follows the home-storage rules. Cost is a one-time setup (the daily_weather runbook lists about 8 steps, `docs/runbooks/home-server-custom-app.md` sections 1 to 7) and a single point of failure.

**B, GitHub Actions (bold alternative).** No hardware, no UI-only restarts; deploy is a merge to `main`. It loses on state. `.selection_history.json` must survive between runs, and the three ways to keep it are poor. `actions/cache` entries may be evicted after 7 days unused (a secondary source says so; I could not confirm it on docs.github.com). An artifact in a public repo is readable by others (**Inference**) and the briefing carries `USER_CONTEXT` tailoring. A `state` branch in the public repo publishes which papers the reader was briefed on, daily. Also, scheduled workflows in a public repo are disabled after 60 days without repository activity, and the Focus order flips this repo public at step 3. Run logs of a public repo are public too (**Inference**), so every log line must be vetted. B is the right answer if the NAS is unreliable; it is the second choice here.

Evidence: https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows said "In a public repository, scheduled workflows are automatically disabled when no repository activity has occurred in 60 days" and "The `schedule` event can be delayed during periods of high loads."
Evidence: https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-actions/about-billing-for-github-actions said "The use of standard GitHub-hosted runners is free" in public repositories, and the Free plan has 2,000 minutes per month for private ones.

**C, workstation.** Free, and the only place the subscription backend is proven (both rostered workstations are `backend: agent`). It fails on the stated problem: daily_weather's gap G4 found the workstation asleep at 06:30 on some nights, and wake-from-sleep is exactly what daily_weather declined to build. A missed run is silent unless something else notices.

**D, hybrid.** Run on the NAS; a GitHub Actions cron reads the channel and pings if no post landed today. It closes the one failure A cannot report on itself (the box is down, so nobody posts). It costs a second Slack token in GitHub secrets and a `channels:history` scope. Defer it; see Assumptions row 7.

TrueNAS Cron Task instead of a supercronic App is rejected on daily_weather's own D4 grounds (configuration as code, not capability).

## Backend choice

Recommendation: the **API key** on the NAS. Cost per day on current IDs (prices from the lead's brief): scoring is 5 calls at about 1.5k in and 0.2k out on `claude-haiku-5-5`, so 7.5k x $0.10/M + 1k x $0.50/M = $0.00125. Distill is 2.5k in and 6.5k out on `claude-sonnet-5-5`, so $0.005 + $0.065 = $0.070. Total about $0.071 per day, **$2.14 per 30 days**; with one distill retry every day, $4.2.

**Subscription CLI headless.** **Assumption**: a logged-in `claude -p` can run unattended on the server and the terms allow it; a separate report decides. One repo fact bears on it: `AgentRunner` deletes every environment variable that starts with `CLAUDE` (`src/agent_runner.py:521-524`), so a token passed as `CLAUDE_CODE_OAUTH_TOKEN` would be stripped before the subprocess starts (**Inference** that this is how such a token is supplied). Only a credentials file under the account's home would survive without a code change. The saving is at most $2 to $4 a month, so I would not accept an unattended auth that can expire silently for it. If the report clears it, the switch is one roster line, `backend: agent`.

**Local model on the NAS CPU.** Argued, not dismissed. Time is free at 05:30, so slowness is not the objection (**Inference**: 6.5k output tokens at 3 to 6 tokens per second on 6 Pentium threads is 18 to 36 minutes; I did not measure it). The objection is Pillar 1. daily_weather's local model writes 200 words from a record that holds every number; paperboy needs 4,600 words, eight sections, a prose kernel, from an abstract. A 4B to 9B model has no measured evidence on that task, and even Claude's style effect is unmeasured (G3). The gain is $2.14 a month. It also shares 14 GB of RAM with daily_weather's 8 GB Ollama service. The cheap test is one distill of a saved paper on the two candidate models, read by the lead. If the lead cannot tell the briefings apart, reopen it.

Before cutover, decide the model IDs. `config/paperboy.yaml:100-104` names previous-generation dated IDs. Moving to `claude-sonnet-5-5` changes the output, which Pillar 4 allows as a one-time config commit made before the first scheduled run, not during it. Whether the old IDs still resolve is unverified.

## Slack shape

Two calls per run, in one process, after the result exists:

1. `chat.postMessage` with a summary (title, first three authors, arXiv link, score, word count, backend, duration, status line) as the parent. Its `ts` goes into the run record.
2. The briefing `.md` uploaded as a reply in that thread: `files.getUploadURLExternal` (filename, length), POST the bytes, then `files.completeUploadExternal` with `channel_id` and the parent `thread_ts`.

Scopes: `chat:write`, `files:write`, and `reactions:read` for G9. Rejected shapes:

- **Per-section thread replies.** Eight replies break the 3,000-character section block cap, and the 4,000-character recommended `text` length. A 30k-character briefing is 7.5 times the recommended length and 75 percent of the hard truncation point. Pasting into NotebookLM from eight messages also needs reassembly.
- **A path on a share.** A phone needs a VPN to read it, and a path is an address that cannot go in git.
- **Inline in one message.** Under the 40,000 limit, but over the recommended length, and Slack markdown mangles the headings.

The file is the NotebookLM source. **Assumption**: Slack on a phone or desktop can save a `.md` to a place NotebookLM's upload reads, in a few taps. Test it on day one (Assumptions row 1).

Evidence: https://docs.slack.dev/reference/methods/chat.postMessage said "limit the number of characters in the `text` field to 4,000 characters" and "Slack will truncate messages containing more than 40,000 characters"; scope `chat:write`; about 1 message per second per channel.
Evidence: https://docs.slack.dev/reference/block-kit/blocks/section-block said the section `text` maximum is 3000 characters and each `fields` item 2000.
Evidence: https://docs.slack.dev/reference/methods/files.getUploadURLExternal said it needs `files:write`, takes required `length` and `filename`, and the file is POSTed to the returned URL.
Evidence: https://docs.slack.dev/reference/methods/files.completeUploadExternal said it needs `files:write`, takes `channel_id`, `initial_comment` and `thread_ts` ("Provide another message's `ts` value to upload this file as a reply"), and names no file size limit.

**Exit 2 (partial)** posts one message with no file: a warning line, the selected title and score, the `error` text, and "not recorded for dedup; the next run retries". **Exit 1 (failure)** posts the error text cut to 500 characters and the stage if known. **A Slack failure** (bad token, 429) cannot post, so it writes the run line with `slack_error` and exits non-zero; the container log keeps it. A process killed by the OOM killer posts nothing; that is the residual silence (row 7).

**Reaction as G9's collector.** Yes, without an Events endpoint. The probe calls `reactions.get` for each stored `ts` and reads the emoji. **Inference** for the encoding: `white_check_mark` means agree, `one` to `five` means "I would have picked rank N". No reaction is "no verdict", never "agree"; report agreements of N reacted, with M posted. The method needs `reactions:read` and is Tier 3 (50+ per minute), plenty for 30 calls. Socket Mode would push events with no public URL, but it holds a connection open and adds an app-level token; polling needs neither.

Evidence: https://docs.slack.dev/reference/methods/reactions.get said bot scope `reactions:read`, returns the item with its reactions, Tier 3.
Evidence: https://docs.slack.dev/apis/events-api/using-socket-mode said Socket Mode works "without exposing a public HTTP Request URL" using an `xapp-` app-level token.

## Run record (gap G8)

One JSON-lines file, `output/briefings/run_history.jsonl`, beside `.selection_history.json`. The pipeline appends one line per run, manual runs included, so G8's count is not scheduler-only. Fields: `date` (UTC, as the filename uses), `started_at`, `duration_s`, `status` (success, partial, error), `backend`, `selected_id`, `score`, `briefing_path`, `words`, `error`, `slack_ts`, `slack_error`, `git_sha`. The file is the record and Slack is the display. A day with no line is itself the finding.

Reader: a probe that reads the last N lines and prints days with a success, partial, error, or no line. `/session-start` runs it over SSH with the account's alias (kept in `~/.ssh/config`, not in git). A second probe joins `slack_ts` to reactions for G9. Both are read-only.

Cost: about 400 bytes a day, 150 KB a year. No rotation.

## Config and roster

No profiles. daily_weather needed four because it had a narrator, a canary and two channels; paperboy has one tracked YAML and `.env`.

- **One switch: `--slack`.** Without it, no run posts, ever. With it and no `SLACK_BOT_TOKEN` or `PAPERBOY_SLACK_CHANNEL`, the run exits with an error before sourcing. The cron line carries `--slack`; a by-hand run does not.
- **Fact that rules out "dry unless the channel is set"**: this workstation's `.env` already holds both Slack variables, so that design would post from every test run.
- **Test posting** is deliberate: `--slack` on a workstation whose `.env` names a dev channel. The lead says which channel the workstation's value points at (Open questions).
- **Roster.** Add one tracked entry keyed by the container's hostname, set in the App YAML to a plain name such as `paperboy`: `role: delivery`, `scope: [personal]`, `backend: api`. That name resolves nowhere on the LAN, so it is not an address (**Inference**; the lead's D8 analogue decides). The NAS's own hostname is never written. If the lead rejects this, the fallback is daily_weather's gitignored `config/local.yaml`, which costs a loader.
- **No `HOME_*` variable in the first cut.** `CLAUDE.md` says add one with the first bulk write. A briefing is 30 KB a day; `output/` in the clone is already on the apps dataset. The first variable arrives with Phase 4 audio.
- **`.env` is read by the app, not by the container.** `src/config.py:119-121` calls `load_dotenv`, which does not override variables already set (**Inference**, python-dotenv default). If the App YAML also used `env_file`, an `.env` edit would need an App restart. So omit `env_file`; set only `HOME` and `TZ` in the App YAML. Then a channel change or a key rotation is live at the next tick.
- Delete or wire the dead `OUTPUT_DIR` and `CONFIG_PATH` in `.env.example`.

## Schedule

One cron line at 05:30 in the lead's zone, `TZ` set in the App YAML (cron reads it; the app does not). Do not pass `--date`: unattended means today. The clock is split in the code. The cutoff and the filename date use UTC (`src/sourcer.py:98`, `src/distiller.py:306`), while `--date` uses the local `date.today()` (`main.py:54`). For a morning run in a US zone both give the same date. An evening run after about 19:00 local would name the file for tomorrow. So: morning only, no `--date`. arXiv's announcement lands the evening before (**Inference**), so a 05:30 run sees it.

One attempt only. A second 06:15 tick needs a skip-if-done guard (Phase 3 lists "skip if today's briefing exists", `docs/design/roadmap.md:60`), or the dedup history would make it pick a second paper. Add the guard and the retry tick if the run record shows transient failures (row 8).

## Deploy

Reuse `deploy/update-server.sh` from daily_weather, with three changes: the clone name; `uv pip install -r requirements.txt` when `requirements.txt` changed, in place of `pyproject.toml`; and a different proof step. **Do not prove with `run --backend keyword-only`**: that path records the selection for dedup (`src/pipeline.py`, the `not briefing_expected` branch), burning a paper. Prove with `python main.py source`, which reads and writes nothing, plus `--help`. Keep the checks (on `main`, clean tree, CI green, clone clean, `pull --ff-only`). A crontab change still needs the App restarted in the UI; the script prints that reminder. First week: run `--slack` against a dev channel by editing `PAPERBOY_SLACK_CHANNEL` in the server's `.env` (live at the next tick, no restart), then switch it.

## Cost table (per 30 days, USD)

| Approach | Hosting | API, Sonnet 5.5 distill | API, one daily retry | API, Opus 5.5 distill | Subscription CLI |
|---|---|---|---|---|---|
| A NAS | 0 marginal | 2.14 | 4.2 | 4.2 | 0 marginal (pending report) |
| B Actions | 0 public, 0 private under 2,000 min | 2.14 | 4.2 | 4.2 | not recommended |
| C Workstation | 0 | 2.14 | 4.2 | 4.2 | 0 marginal |
| D NAS + watchdog | 0 | 2.14 | 4.2 | 4.2 | as A |

Opus column: distill only on `claude-opus-5-5` ($0.01 in + $0.13 out = $0.14 a day), scoring stays on Haiku; one retry doubles it to about $8.4. NAS electricity is unmeasured. B private-repo minutes: 30 runs x about 5 minutes is 150 (**Inference**).

## Assumptions

| # | Assumption | Cheapest falsifier | Blast radius | Kill criterion |
|---|---|---|---|---|
| 1 | A phone or desktop can take the Slack `.md` into NotebookLM in a few taps | Upload a sample briefing to a dev channel, try both devices (5 min) | Slack shape only | More than 1 minute of handling per day: post the text as a thread reply instead |
| 2 | The existing bot token has `chat:write`, adding `files:write` and `reactions:read` is a reinstall | Call `files.getUploadURLExternal` once | Slack shape; G9 collector | Reinstall rotates the token and daily_weather shares it: make a second app |
| 3 | The container reaches arXiv, the feed hosts, the Anthropic API and Slack | `python main.py source` as the account, then one `--backend api` run | Approach A | Any host blocked: choose B |
| 4 | The configured dated model IDs still resolve and give a briefing as good | One `api` run on the NAS with each ID set, read by the lead | Pillar 1 and 4 | Old IDs fail: move to current IDs before cutover |
| 5 | A reaction is used (G9) | Count reacted posts in 14 days | G9 only | Fewer than 7 of 14 reacted: replace with a one-line file entry |
| 6 | Subscription CLI is allowed and stable headless | The separate report; then 7 unattended days | Backend only | One silent expiry: back to API |
| 7 | The NAS and the container stay up | Count days with no run line in 30 | All of A | 2 silent days in 30: add watchdog D, or move to B |
| 8 | Transient failures are rare | Share of error or partial lines over 30 days | Schedule | Over 3 of 30: add the guard and the 06:15 retry |
| 9 | A local model cannot match Claude on the briefing | One distill on each daily_weather candidate, read blind | Pillar 1 | Lead cannot tell them apart: reopen the local backend |
| 10 | `load_dotenv` leaves container variables alone, so omitting `env_file` is right | Edit `.env`, wait one tick, check the channel | Config only | `.env` edits need a restart: accept it, re-add `env_file` |

## Recommendation

**Approach A** (NAS Custom App), **API backend** on current model IDs, **Slack shape**: a summary post, with the briefing `.md` uploaded in its thread, `reactions:read` for G9. The run line goes to `run_history.jsonl`, `--slack` is the only switch, and the NAS is rostered by container name. The NAS is the best fit and not by a wide margin: B is the credible alternative and wins if rows 3 or 7 fail. The tradeoffs I accept: one box with no self-report when dead, a crontab change that needs the UI, and a $2 to $4 monthly bill I could avoid.

## Open questions for the lead

1. Is a container hostname in the tracked roster acceptable, or do you want a gitignored `config/local.yaml`?
2. Which channel does the workstation's `PAPERBOY_SLACK_CHANNEL` name: dev or the real one?
3. Do you accept changing the model IDs in a commit before the first scheduled run?
4. Does the Slack app already hold `files:write`, and may it gain `reactions:read`?

## What not to build

- **TTS and audio**: Phase 4; the first bulk data, and the first `HOME_*` variable.
- **RSS or podcast feed**: Phase 5; Slack is the delivery for now.
- **Output rotation**: 150 KB of record and about 11 MB of briefings a year need none.
- **Backfill command**: dedup and the 7-day window already cover a missed day.
- **Retry tick and skip-if-done guard**: wait for row 8.
- **Watchdog**: wait for row 7.
- **Profiles and `local.yaml`**: one switch is enough.
- **Per-section Slack replies**: they fail the NotebookLM goal.

## References

Read: `main.py`, `src/pipeline.py`, `src/agent_runner.py`, `src/config.py`, `src/machine.py`, `src/sourcer.py`, `src/distiller.py`, `config/project.yaml`, `.env.example`, `docs/gaps.md`, `docs/tasks.md`, `docs/design/roadmap.md`, `.claude/skills/lake-conventions/HOME-STORAGE.md`. In daily_weather (read-only): `deploy/README.md`, `docs/runbooks/home-server-custom-app.md`, `deploy/crontab.prod`, `deploy/update-server.sh`, `src/daily_weather/utils/slack.py`, `config/default.yaml`, `config/profiles/`, `docs/plans/conop_HERALD_local_llm_weather_slack.md` (D4, D9).
Fetched: the five Slack pages and two GitHub pages quoted above. A web search for the Actions cache window returned only secondary sources (unverified).
