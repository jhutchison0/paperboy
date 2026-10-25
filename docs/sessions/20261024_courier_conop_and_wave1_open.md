# Session: CONOP COURIER Planned, Approved, Wave 1 Built and Merged; Phase 3 Opened; the Doctrine File Removed

**Date**: 2026-10-24 (the session opened 2026-10-22 after the doctrine cycle and ran across three calendar days)
**Branch**: main; Wave 1 on `topic/pipeline-courier-wave1-20261024`, merged at `d16503b` and deleted per branching doctrine
**Tags**: #session #infra #config #cli #docs #feature #complete #pillar-2 #pillar-4 #pillar-5

**Documents**: [CONTEXT.md](../../CONTEXT.md) — the upstream-file convention line | [docs/tasks.md](../tasks.md) — Focus steps 2 to 6 rewritten | [docs/design/roadmap.md](../design/roadmap.md) — Phase 3 lines marked | [docs/design/pillars.md](../design/pillars.md) — Pillar 4 sentences | [LANGUAGE.md](../../LANGUAGE.md) — four terms | [docs/gaps.md](../gaps.md) — G4's arm
**Implements**: [conop_COURIER_daily_run_slack_delivery.md](../plans/conop_COURIER_daily_run_slack_delivery.md) — approved 2026-10-24; Wave 1 merged; its exit criterion's live post is the lead's
**References**: [20261022_courier_proposal.md](../plans/20261022_courier_proposal.md) — proposer | [20261022_courier_conop_review.md](../reviews/20261022_courier_conop_review.md) — plan challenge | [20261022_courier_sme_alignment.md](../reviews/20261022_courier_sme_alignment.md) — plan alignment | [20261022_courier_claude_cli_headless_check.md](../reviews/20261022_courier_claude_cli_headless_check.md) — auth and terms, with the 2026-10-23 addendum | [20261024_courier_wave1_gate.md](../reviews/20261024_courier_wave1_gate.md) — code gate | [20261024_courier_wave1_sme.md](../reviews/20261024_courier_wave1_sme.md) — mission check of the code
**Follows**: [20261022_doctrine_picture_cycle.md](20261022_doctrine_picture_cycle.md)
**Cites**: the sister repo `daily_weather` (`docs/runbooks/home-server-custom-app.md`, `deploy/`, CONOP HERALD D4, D9, D14); https://code.claude.com/docs/en/authentication.md, https://code.claude.com/docs/en/legal-and-compliance.md, https://code.claude.com/docs/en/headless.md (fetched 2026-10-23); https://platform.claude.com/docs/en/about-claude/model-deprecations and https://platform.claude.com/docs/en/build-with-claude/thinking (fetched by the code-reviewer 2026-10-22)

---

## Summary

The session removed the fully processed doctrine notification, planned Phase 3's first operation as CONOP COURIER, and built its Wave 1. COURIER puts one scheduled run a day on the home server as a TrueNAS Custom App on the lead's Max subscription, writes the briefing to a folder on the home share, posts a Slack summary as the reminder, and records one line per run (gap G8's collector) with a Slack reaction as gap G9's. Four agents fed the plan; the lead reversed its first backend choice from an API key to the subscription after a re-check of the source pages, chose Slack as the reminder rather than the store, and approved. Two implementers built Wave 1 on disjoint files; three gate agents reviewed it; every required fix landed; the branch merged with a merge commit and Phase 3 opened by predicate. Wave 1's exit criterion still wants the lead's one live post to the dev channel.

| Metric | Value |
|---|---|
| Commits on main this session | 10, including the merge; unpushed at this writing |
| Tests at the start (`85a30c8`) / at close | 274 / 356 |
| Agents | 9: proposer, claude-code-guide, code-reviewer (twice), pipeline-sme (twice), test-runner, two python-prototypers |
| Plan reviews: code-reviewer (Critical/Warning/Suggestion) | 3 / 5 / 6, all folded |
| Plan reviews: pipeline-sme (Blocker/Major/Minor) | 0 / 4 / 8, all folded |
| Gate reviews: code-reviewer (Critical/Warning/Suggestion); probes | 0 / 7 / 10; 14 of 14 mutation probes caught |
| Gate reviews: pipeline-sme (Blocker/Major/Minor) | 0 / 2 / 8 |
| Gate test run | GREEN WITH NOTES; `health` exit 0 with the Slack line OK; `source` 81 papers, 21 articles |
| Plan decisions | 17, none open at approval |
| `/pcc` check 5 at close | 30 paths, 0 MISSING |
| Lead corrections of the plan | 2 (the backend; Slack as reminder, not store) |

## Work Completed

### 1. The doctrine notification removed (`cfde101`)

Every one of the 17 headings in `.claude/doctrine-delivered` carried a `Processed` annotation in `.claude/upstream-update.md`, and the hub's protocol (tacsop `docs/propagation-protocol.md`, step 6) expects the downstream maintainer to delete the file once read. The user decided to remove it; `CONTEXT.md` now states the convention (annotate through the cycle, remove when every delivered entry is annotated; the delivery mark prevents redelivery and git keeps the annotations). `/pcc` check 5 already allowlisted the path. The memory note for upstream propagation was updated to match.

### 2. The plan (`cc07639`, `dca9a0b`)

The user asked for the sister repo's `daily_weather` pattern: an app on the NAS running paperboy daily, reporting to Slack, with alternatives welcome. The proposer weighed four hosts (the NAS Custom App; GitHub Actions; the workstation; a hybrid with a watchdog) and three backends (API key; subscription CLI headless; a local CPU model). A claude-code-guide agent checked the headless authentication and terms pages. The CONOP was drafted from both and challenged by the code-reviewer (GO WITH FIXES) and the pipeline-sme (SUPPORTING WITH CHANGES). What the reviews changed: the configured distill model `claude-sonnet-4-20250514` is Retired (2026-06-15), so the API path produced no briefing anywhere, and both SDK call sites sent `temperature`, which current models reject; the server's `health` could not exit 0; the run line and the Slack post had no agreed owner (now a `deliverer` callable); gap G9's rank verdict needs the day's top five in the post; MOE 2 needed a collector (a `headphones` reaction); Phase 3 must close by predicate against the roadmap's lines.

### 3. The backend reversal (Status Log 2026-10-23)

The first draft chose a dedicated API key for the server, citing the Consumer Terms. The user objected to paying for API calls on top of the subscription and asked for a re-check. The source pages, fetched directly: `claude setup-token` is documented "for CI pipelines, scripts, or other environments where interactive browser login isn't available"; the legal page's restrictions name third-party developers and products, and it says the policy does not "prevent an end user from signing in to the unmodified Claude Code binary with their own Claude subscription". D2 reversed to the subscription, which also matches the repo's own roster convention for home boxes ("no API spend"). Three residual risks stay named with containments: the `CLAUDE*` strip in `AgentRunner` (fixed in task 1.2), the one-year token renewal (loud under the plan), and Anthropic's announced bare-mode default for `-p` (the server's CLI is pinned at 2.1.310). A feedback memory records the correction.

### 4. The lead's decisions and approval (Status Log 2026-10-24)

`paperboy` is the app's name on the NAS and its roster key. Slack carries a summary (title and link, Claude's "why this paper", the abstract trimmed, the day's top five, the filename, a reaction legend, one telemetry line) and never the briefing, which lives on the home share under the first `HOME_*` variable, `HOME_BRIEFINGS_ROOT`; the file-upload assumptions and the Slack scope question fell away. Thread replies that expand the post, `daily_weather`'s newer pattern, are sketched as Wave 3 task 3.4. Wave 1 first; the v0.3.0 CHANGELOG entry names it. The Focus in `docs/tasks.md` carries the three waves as steps 4 to 6.

### 5. Wave 1 built (`c4f734d`, `52cd60d`)

Two python-prototyper instances under the one-owner-per-file rule, briefed with the interface contract. A (delivery) wrote `src/slack.py`, `tests/test_slack.py`, `tests/test_boundary_line.py`, `deploy/`, `.env.example`, `README.md`. B (pipeline) wrote the run record and the top five in `src/pipeline.py`, the `deliverer` seam, the headless `AgentRunner` with `--output-format json` and the model from `modelUsage`, `--slack` and `health` in `main.py`, `HOME_BRIEFINGS_ROOT` in `src/config.py`, the current-model fallback in the selector and distiller, the `anthropic<1` pin, and six test files. B ran one live `claude -p "Reply with OK" --output-format json` to capture the envelope fixture; the subscription's main model on this account reads `claude-fable-5-1`. The model-ID change landed alone as `[config]`.

### 6. The gate and the fixes (`00ffb50`, and the fixes inside `52cd60d`)

Test-runner GREEN WITH NOTES: 348 passed before the fixes; `/pcc` checks clean on the uncommitted tree; `health` exit 0 on this box with the Slack line OK (assumption A2 held); `source` fetched 81 papers and 21 articles with no feed warning; the only note, em dashes in four source files, all predating the wave. Code-reviewer GO WITH FIXES, 14 of 14 mutation probes caught in a scratch copy. Pipeline-sme SUPPORTING WITH CHANGES, with the three Slack posts rendered from realistic fixtures (success 1,486 characters). Fixed before the merge, each red first: the env example's token and channel placeholders commented out (a fresh `cp .env.example .env` would otherwise have fed a placeholder token to every CLI call and failed `health`); the record write in a `finally`; a success with no briefing renders (the keyword-only path, where auto mode lands if the CLI is off `PATH`); the partial post's error cut to 500 characters; the non-JSON warning keeps the stdout head; the score parser takes the outermost JSON object when the model fences it; the abstract cut falls on a word boundary and the ellipsis follows no period; the legend says "on this message"; the record writes null, not a placeholder, when the CLI has not named a model; the config hash leaves out `output_dir` and `log_level`.

### 7. Merge and Phase 3 opened (`d16503b` and the commit after it)

Merged with a merge commit at the code-reviewer's gate; the branch deleted locally (it was never pushed). On main, the boundary test then failed once: the code-reviewer's gate record named a literal UNC path as its probe example and had become tracked; the example is now a placeholder. The Phase 3 opening edits from the SME's drafts: every roadmap Phase 3 line marked built (tasks 1.1, 1.3 to 1.5, 1.8) or declined with its trigger (A6, A7) or reason; `phase_3: in_progress` beside `phase_2` until Focus step 3 closes Phase 2; Pillar 4 no longer promises backfill and names the record; a CHANGELOG `[Unreleased]` section; four glossary terms; two scope-matrix rows; the P3 record task closed; the temperature task rewritten; gap G4's API arm at the model default.

### 8. Found on the way

The shift-left audit log's newest line is from 2026-10-22, while the two implementers edited six `src/` files. Either they wrote through Bash (gap G2's known blind spot) or the `PostToolUse` hook does not fire for a subagent's Write and Edit calls; the log alone cannot tell. Both implementers also reported writing each task's tests as a batch before the code, a horizontal slice per task rather than one test at a time; the code-reviewer judged the tests drive the code (every Standard's case exists as a test; 14 of 14 probes caught) and recorded the deviation.

## Claims

| Claim | State | Evidence |
|---|---|---|
| The doctrine notification is removed and committed | deployed, locally | `git log --oneline` → `cfde101 [infra] Remove the processed doctrine notification...`; no `.claude/upstream-update.md` in `git ls-files` |
| Wave 1 is merged into main and the branch is deleted | deployed, locally | `git merge --no-ff ... && git branch -d topic/pipeline-courier-wave1-20261024` → `Deleted branch topic/pipeline-courier-wave1-20261024 (was 00ffb50).`; `git log --oneline -5` → `d16503b Merge topic/pipeline-courier-wave1-20261024...` |
| The suite passes on main after the merge and the Phase 3 edits | tested | `.venv/bin/pytest -q` → `356 passed in 1.90s`, after the last edit of this session |
| Reference integrity of the orientation surfaces | measured | `/pcc` check 5 file pass → no MISSING line, after the Phase 3 edits |
| Phase 3 is open beside Phase 2 | observed | `yaml.safe_load(config/project.yaml)` → `phase_2: in_progress, phase_3: in_progress` |
| `health` passes on this box with the Slack token | observed, by the test-runner | `.venv/bin/python main.py health` → `arxiv OK, blogs OK, claude_api SKIPPED, claude_cli OK, slack OK`, exit 0 (gate test run) |
| The gate's mutation probes all fire | observed, by the code-reviewer | 14 probe edits in a scratch copy, 14 caught; `diff -rq` real tree against the copy → none (`docs/reviews/20261024_courier_wave1_gate.md`) |
| main is ahead of origin and not pushed | observed | `git rev-list --count origin/main..main` → the count printed in the session's final message; `git rev-parse --short origin/main` → `85a30c8` |
| The configured distill model was retired | observed, by the reviewer | fetched https://platform.claude.com/docs/en/about-claude/model-deprecations → `claude-sonnet-4-20250514 \| Retired \| April 14, 2026 \| June 15, 2026` |
| The subscription route for scripts is documented | observed | fetched authentication.md 2026-10-23 → "For CI pipelines, scripts, or other environments where interactive browser login isn't available, generate a one-year OAuth token with `claude setup-token`" |
| Wave 1's exit criterion is met | UNVERIFIED | the lead's pinned post to the dev channel has not run; the command is in Next Steps |
| Distillation through the JSON envelope works live | UNVERIFIED | the implementer ran one live `score_paper` (valid dict, model `claude-fable-5-1`); no live distill was run; covered by mocks until the gate post |

Overclaims the user caught this session: 1

Overclaims a reviewer caught this session: 3

The user's: the first draft's statement that the Consumer Terms ruled out the subscription on the server, which the Claude Code pages contradict for an end user's own job. The reviewers': `daily_weather`'s Slack client called 69 lines (81); `SelectionHistory` placed at `src/pipeline.py:42` (40); the configured model IDs called "unverified" (one was retired).

## Key Decisions

| Decision | Rationale |
|---|---|
| Remove `.claude/upstream-update.md` once every delivered entry is annotated | The hub's protocol expects it; the delivery mark prevents redelivery; git keeps the annotations |
| The NAS Custom App over GitHub Actions, the workstation, or a hybrid | Proven on the same box by `daily_weather`; state stays home; Actions needs an API key and leaks the reading history in a public repo; the workstation sleeps |
| The Max subscription over an API key on the server | The docs document `setup-token` for scripts and protect the end user's own subscription; the repo's home boxes already carry "no API spend"; three risks contained |
| Slack carries a summary; the share holds the briefing | The lead's reading of what Slack is for; no new Slack scope; the first `HOME_*` variable arrives with a stated deviation (the workstation default stays) |
| The delivery seam is a callable, not a flag or an ABC | One owner for the record line and the Slack post; Phase 4 and 5 slot in beside it |
| Two prototypers with disjoint files | Wall time; the one-owner rule holds; the contract was written in both briefs |
| `/session-end` deferred until the gate | Its commit step would have swept half-written agent files on the topic branch into a commit |
| Merge at the code-reviewer's gate with the live post still pending | The plan names the reviewer's gate as the merge point; the post needs the lead's dev channel id and is reversible evidence, not code |
| The config hash leaves out `output_dir` and `log_level` | The hash names the config that shapes the briefing; where it lands and how loudly do not, and server and workstation hashes should agree |

## Pillar Compliance

| Pillar | Status | Notes |
|---|---|---|
| **Content Quality First** | UNCHANGED | No prompt change; the API fallback's call shape changed (no sampling parameter, a larger output cap) |
| **Source Diversity & Resilience** | PASS | A raising deliverer never rolls back the briefing or the dedup record; a record-write failure only warns; a success without a briefing renders; `health` reports skipped checks without failing |
| **Relevance Through Hybrid Scoring** | UNCHANGED | The top five are surfaced, not re-weighted; the Claude-scored set is the same five as before |
| **Pipeline Idempotency** | PASS | No randomness added; the record carries backend, models and a config hash; the API path's only sampling lever went with `temperature`, and gap G4's arm says so |
| **Extensibility by Design** | PASS | A callable seam; `src/slack.py` beside the stages; no ABC until a second deliverer exists |

## Commits

| Hash | Subject |
|---|---|
| `cfde101` | [infra] Remove the processed doctrine notification; the delivery mark and session records carry the history |
| `cc07639` | [doc] CONOP COURIER approved: the plan, its proposal and three reviews; Focus steps 4 to 6 |
| `dca9a0b` | [doc] COURIER: name the run-log reader by task until its file exists; calibration literal as a placeholder |
| `c4f734d` | [config] API fallback on current models: claude-opus-5-5 and claude-haiku-5-5; temperature removed; max_tokens 16000 |
| `52cd60d` | [pipeline][cli][test] COURIER Wave 1: run record, Slack summary post, delivery seam, headless AgentRunner, HOME_BRIEFINGS_ROOT, deploy files |
| `00ffb50` | [doc] COURIER Wave 1 gate: the code-reviewer and pipeline-sme records; Status Log entry |
| `d16503b` | Merge topic/pipeline-courier-wave1-20261024: COURIER Wave 1, the run record and the Slack summary post |
| `2c14d28` | [doc][config] Open Phase 3: roadmap lines marked, phase_3 in_progress, Pillar 4 sentences, CHANGELOG Unreleased, glossary, scope matrix, G4 arm |

The commit that carries this doc is reported in the session's final message.

KB-graph: `/pcc` check 5 → 27 paths, 0 MISSING at the 10-22 close; 30 paths, 1 MISSING (`src/runlog.py`, a Wave 3 file named by the Focus) after the approval commit, fixed in `dca9a0b`; 0 MISSING after the merge and after the Phase 3 edits (M2 count: 1 caught, 1 fixed).

## Next Steps

- [ ] **The lead's gate post** (Wave 1's exit criterion): from this workstation, with the dev channel's id, `PAPERBOY_SLACK_CHANNEL=<dev id> .venv/bin/python main.py run --slack`. It runs the full pipeline on the agent backend, writes a briefing and the first `run_history.jsonl` line under `output/briefings/`, and posts the summary. Expect several minutes; exit 0 and a post in the channel close the wave. Then a Status Log entry.
- [ ] Wave 2, the lead by hand per `deploy/README.md`: the Slack dev channel and bot membership; the account, alias, bare repo and clone; uv venv on 3.12 from `requirements.txt`; supercronic; the Claude CLI pinned to 2.1.310 with auto-update off; `claude setup-token` on this workstation and the token into the server's `.env` with its renewal comment; `HOME_BRIEFINGS_ROOT` on the shared folder; `health` and `source` as the account; the `paperboy` roster entry with the clone; then the App.
- [ ] Resolve the audit-log question (section 8): subagent edits silent, Bash or hook scope; amend gap G2 if the hook does not see subagent tool calls. A cheap falsifier: one subagent Edit of a comment in a `src/` file while watching the log.
- [ ] Phase 2's close (Focus step 3) and the v0.3.0 tag, folding the CHANGELOG `[Unreleased]` section into the entry.
- [ ] Hub harvest into `.claude/upstream-lesson.md`: read the product's own docs pages before a terms conclusion; two prototypers on disjoint files with a written contract; a boundary test on tracked files trips on a review's own example.
