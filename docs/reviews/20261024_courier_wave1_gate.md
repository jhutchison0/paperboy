# Gate Review: CONOP COURIER Wave 1

**Verdict: GO WITH FIXES.** Merge after W1, W2 and W4 land (three small edits, no design change). W3, W5 and W6 may land with them or as the first follow-up; the rest are the lead's call.

**Reviewer**: code-reviewer | **Date**: 2026-10-24 | **Branch**: `topic/pipeline-courier-wave1-20261024`, uncommitted tree (12 modified, 13 untracked files) | **Spec**: `docs/plans/conop_COURIER_daily_run_slack_delivery.md` D3 to D7, D10 to D16, Wave 1 TCS table | **Method**: read every file the brief names; ran the suite on the real tree; 14 mutation probes in a scratch copy, never in the tree; no `main.py run`, no live CLI or Slack call.

Suite green on the tree (tested).
Evidence: `.venv/bin/pytest -q -p no:cacheprovider; echo "exit=$?"` → `348 passed in 2.34s`, `exit=0`; `.venv/bin/python -V` → `Python 3.12.13`; `anthropic 0.120.2` (`Messages.create` has `thinking` and `output_config`: `True True`).

| Severity | Count | Required before merge |
|---|---|---|
| Critical | 0 | |
| Warning | 7 | W1, W2, W4 |
| Suggestion | 10 | none |

## Findings

### Warnings

**W1 `.env.example:21-22,28`: live placeholders for the three new secrets.** `SLACK_BOT_TOKEN=xoxb-your-token-here`, `PAPERBOY_SLACK_CHANNEL=C0000000000` and `CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-your-token-here` are uncommented. CLAUDE.md's setup is `cp .env.example .env`. After that copy: (a) `main.py health` calls `auth_test()` with the placeholder (`main.py:250-257`) and exits 1 on a fresh box; (b) the placeholder OAuth token survives `_build_clean_env` (`src/agent_runner.py:511`) into every CLI call, so a workstation that copied the file sends a bogus token where it used the stored login. That breaks 1.2's Standard ("a workstation run with no token behaves as today") for anyone who followed the README. The API key placeholder has `_PLACEHOLDER_API_KEY` handling (`src/config.py:21,250-255`); these have none. Pillar 2. Fix: comment the three lines out, as `HOME_BRIEFINGS_ROOT` is at line 33, or add the same placeholder-as-unset handling. The CLI's env-over-keychain precedence is UNVERIFIED here: a live call would spend the usage pool.

**W2 `src/pipeline.py:429-449`: the record write is not in a `finally`.** D5 and TCS 1.1 both say "written in a `finally` after delivery". `_run()` never raises (it catches `Exception` at 565), and the deliverer is wrapped (442-446), so the only unguarded lines are the wrapper's own: `resolve_machine()` at 434 reads `config/project.yaml` and raises on a missing or empty file; a `BaseException` from the deliverer skips 448. No test covers a wrapper-level raise. Fix:
```python
result = self._run(paper_override, dedup)
try:
    ...metadata and delivery as now...
finally:
    self._write_run_record(result)
```

**W3 `src/slack.py:119,129`: `_success` dereferences `result.briefing` and `result.briefing_path`.** A keyword-only success has both `None` (`src/pipeline.py:521-526`), so `run --slack --backend keyword-only` raises inside the deliverer, lands in `slack_error` as `'NoneType' object has no attribute 'word_count'`, and exits 3. Contained, but a wrong diagnosis. Fix: guard (`words = result.briefing.word_count if result.briefing else 0`; filename line only when `briefing_path`), or refuse `--slack` with `keyword-only` at `main.py:90`.

**W4 `src/slack.py:161`: the partial message does not cut the error to 500.** Standard 1.4: "partial and error name the error cut to 500 characters"; only the error branch (166) cuts. `distiller.last_error` on the SDK path is `f"Claude SDK error: {e}"` with the API's JSON body. Fix: `f"Error: {(result.error or '')[:ERROR_CHARS]}"`.

**W5 `src/agent_runner.py:319-325`: a non-JSON stdout logs the exception only.** `json.loads` fails with `Expecting value: line 1 column 1 (char 0)` and the stdout head is gone; the timeout path keeps it (306) and the removed preamble path logged `cleaned[:200]`. In the canary this is the one line that says what the CLI printed. Fix: add `stdout_bytes[:200]!r` to the warning at 324.

**W6 `src/agent_runner.py:356-378`: no fence tolerance in `_validate_score`.** 1.9's Standard retires the preamble heuristics, and `result` is now the model's final text verbatim. A fenced ```` ```json ```` block fails `json.loads`, the retry gets one more try, then the selector applies 0.5 with "AgentRunner scoring failed; default score applied" (`src/selector.py:124`). That reaches the post's reasoning line, so it is visible, but it silently flattens selection (Pillar 3). Either strip a leading and trailing fence before `json.loads` (three lines) or name it a canary watch item in the plan's Status Log.

**W7 Process claim, UNVERIFIABLE.** Both implementers say they wrote each task's tests in a batch, then the code. The audit log's newest line is `2026-10-22T21:37:22` (`tail .claude/audits/shift-left-violations.log`); nothing from Wave 1, so the hook saw none of these edits (gap G2, or subagent tool calls are outside its matcher; the session doc section 6 already asks which). The outcome is good: the Standards' cases exist as tests and 14 of 14 probes were caught (table below). The process as described is a per-task horizontal slice, which CLAUDE.md forbids; record it, do not re-do it.

### Suggestions

**S1 `src/agent_runner.py:340-350` `_main_model`.** Cost-max picks the auxiliary when it costs more than the main model; for a scoring call the main model's cached system prompt dominates (fixture: 0.0844 vs 0.00012), so it holds in practice, but the fixture offers a better key: the top-level `usage` counts (2, 4199, 649, 4) equal the main entry's `inputTokens`, `cacheCreationInputTokens`, `cacheReadInputTokens`, `outputTokens`. Match those first, cost as fallback, `None` when no entry has positive cost (today `max` returns the first key). A non-dict entry value raises `AttributeError` at 350, outside the `try` at 319.

**S2 `main.py:120-123`.** The exit-3 text says "The briefing was saved" for a keyword-only success too. Tie it to `result.briefing`.

**S3 `src/slack.py:123,154`.** `*{title}*`: a `*` in a title ends the bold span early (cosmetic; `_` mid-word is safe). The 4,000 fallback `text[: MAX_TEXT - 1]` cuts the tail (legend, telemetry) rather than the long field; unreachable with real titles.

**S4 `tests/test_boundary_line.py:15`.** The UNC pattern misses a UNC inside an escaped string literal (`"\\\\host\\share"` in `.py` or `.json`): the doubled backslashes defeat the lookbehind. Docs are the risk, so acceptable; note it beside the pattern.

**S5 Plan, Wave 1 row 1.6 and line 170.** The implementer's `smb://` needing a host (`:16`) is the right call: the row's own "no `smb://`" is a bare `smb://` in a tracked file. Append to the Status Log: the Standard reads "no `smb://<host>` with a literal host".

**S6 `README.md:97-99`.** "The daily run lives on the home server" states Wave 2 as present fact before Wave 2 runs. Rewrite: "The daily run is built for the home server: one container runs supercronic ...". Prose rule 1, Minor.

**S7 `requirements.txt:3`.** `anthropic>=0.40.0,<1`: the floor predates `thinking` and `output_config`; `uv` resolves to the newest 0.x so it works, but a pinned older install would `TypeError` at `src/selector.py:228`. Raise the floor to the version that carries `output_config`.

**S8 `docs/tasks.md:29`.** TCS 1.1 says it closes the P3 "record the backend and a config hash" task; the lead's commit should tick it.

**S9 `src/pipeline.py:454-478`.** The record dict is built outside the `try` (479); a field error would propagate where the spec wants a warning. Move the build inside.

**S10 `main.py:234`.** `distill` now writes a run line too (`papers_fetched: 0`, empty `top_candidates`), and the record has no field naming the command. Wave 3's reader should not count manual distills as daily runs; a `command` field or a Status Log note.

## Probe table

Scratch copy at `/tmp/claude-1000/-home-jhutchison-projects-github-paperboy/f4514856-26aa-491c-be34-1dbf0b6feb4b/scratchpad/mutants/repo`; baseline there `348 passed`; each mutation applied by exact-string replacement, the target test file run with the venv's pytest and `--rootdir` on the copy, the file restored from the real tree after. `diff -rq` real vs copy after the run: `none`.

| Probe | Mutation | Target | Result |
|---|---|---|---|
| P1 | drop `_write_run_record` in `run()` | test_run_record | CAUGHT (12 failed) |
| P2 | invert `if result.slack_error` (exit 3) | test_cli_slack | CAUGHT (3 failed) |
| P3 | strip only `ANTHROPIC_API_KEY` | test_agent_headless | CAUGHT (1 failed) |
| P4 | `_main_model` returns first key | test_agent_json | CAUGHT (1 failed) |
| P5 | remove the 600-char abstract cap | test_slack | CAUGHT (1 failed) |
| P6 | remove `_escape` in `post_message` | test_slack | CAUGHT (1 failed) |
| P7 | SMB pattern never matches | test_boundary_line | CAUGHT (1 failed) |
| P8 | deliverer exception propagates | test_run_record | CAUGHT (1 failed) |
| P9 | record written before delivery | test_run_record | CAUGHT (7 failed) |
| P10 | tracked `docs/plant.md` with `\\nas01\media` (copy's index) | test_boundary_line::tracked_tree | CAUGHT (1 failed) |
| P11 | drop `--no-session-persistence` | test_agent_headless | CAUGHT (1 failed) |
| P12 | drop `thinking: disabled` on scoring | test_api_fallback | CAUGHT (1 failed) |
| P13 | hash keeps `anthropic_api_key` | test_run_record | CAUGHT (1 failed) |
| P14 | no 429 retry | test_slack | CAUGHT (2 failed) |

Tally: 14 caught, 0 survived. Gaps the probes cannot show: no test raises from the `run()` wrapper itself (W2); no test passes a keyword-only success to `build_message` (W3); no test measures the partial error length (W4).

## What held, by task

**1.0 API fallback.** Both call sites read the first `text` block by type (`src/selector.py:233`, `src/distiller.py:363`); scoring sends `thinking: disabled`, `effort: low`, `max_tokens: 200` and no sampling parameter (`selector.py:225-230`); distill sends `max_tokens` from config (16000, `config/paperboy.yaml:105`) and nothing else; the YAML comment names the Haiku-class constraint (`:102-103`). An old YAML with `temperature` loads and warns (`src/config.py:188-189`).
Evidence: `grep -rn temperature src/ config/ README.md main.py` → only `src/config.py:188-189`; `tests/test_api_fallback.py` 4 passed inside the 348; P12 caught.

**1.1 Record.** All 20 D5 fields, asserted as a set (`tests/test_run_record.py:16-21,85`); `config_sha256` drops the key (`pipeline.py:206`, P13) and moves with `user_context` (test `test_changes_with_user_context`), the text never written; `git_sha` tolerant (`:210-219`); `top_candidates` is `select_best`'s `filtered[:top_k]` with `top_k=top_k_for_claude` (`pipeline.py:580`, `selector.py:150`), sorted descending. `date` is `started_at`'s UTC date (`:455`); the filename uses `generated_at`, also UTC (`distiller.py:306`); they differ only for a run crossing 00:00 UTC, and 05:30 Chicago is 10:30 or 11:30 UTC. The record holds `briefing_path` with the `HOME_BRIEFINGS_ROOT` value: acceptable, the file is gitignored and lives in that folder; the post carries `.name` only (`slack.py:129`). One leak to watch: a save failure's `error` text can carry the path into the Slack error post, cut to 500 and inside the private channel.

**1.2 Headless env and argv.** `_build_clean_env` keeps `CLAUDE_CODE_OAUTH_TOKEN`, drops `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN` and every other `CLAUDE*` (including `CLAUDECODE`), sets the two headless variables (`agent_runner.py:507-517`). The argv is `["claude", "-p", prompt, "--output-format", "json", "--no-session-persistence", "--tools", ""]` (`:263`). `--tools <tools...>` is variadic, but `""` is the final argv element and the prompt is positional at index 2, so nothing can be swallowed; `Popen` without a shell passes the empty string intact. Other `ANTHROPIC_*` names (`ANTHROPIC_BASE_URL`, `ANTHROPIC_MODEL`) are not stripped; D13 did not name them.
Evidence: `claude --version` → `2.1.310 (Claude Code)`; `claude --help` → `--tools <tools...> ... Use "" to disable all tools`, `--no-session-persistence ... (only works with --print)`, `--output-format <format> ... "json" (single result)`; P3, P11 caught.

**1.3 Seam and D11 exit codes.** Trace of `run()`: `_run` returns success, partial or error (never raises, `:565-567`); metadata set (`:431-439`); deliverer inside try/except (`:441-446`); one record write (`:448`). Briefing and dedup record are written inside `_run` (`:526,536`) before the deliverer sees the result; nothing rolls back (test `test_raising_deliverer_sets_slack_error_and_changes_nothing_else`, P8). Unwritable record path: warning, status unchanged (`:479-485`, test). `main.py`: success → 0; success with `slack_error` → 3 (`:120-123`); partial → 2 (`:132`) and error → 1 (`:135`) regardless of `slack_error`. The `--slack` check at `main.py:90-94` runs after `.env` is loaded (`_load_and_validate` → `PipelineConfig.load` → `load_dotenv`) and before `DailyPipeline(...)` at 105; the record is written only in `run()`, so no line (test asserts `Pipeline.assert_not_called()`).

**1.4 Message and HTTP.** Order matches D4 (`slack.py:121-133`); abstract three sentences or 600 (`:100-108`, P5); success text under 4,000 by shrinking the abstract budget (`:148-154`); escaping once, at the boundary in `post_message` (`:74`), none in `build_message`, so no double-escape (P6); 429 retried once honoring `Retry-After` with `_sleep` stubbed (`:45-47`, P14); timeout and `URLError` raise without retry (`:49-52`); `ok:false` surfaces Slack's string (`:53-54`); the module has no `logging` import, so the token is never logged; no em dash in any new file (`grep` of the 11 new files → none).

**1.5 CLI.** `health` reports `None` as SKIPPED and exits 0 unless a check is `False` (`main.py:276-289`); Slack line via `auth_test` only when the token is set (`:248-257`); CLI check skipped on an `api` roster box (`pipeline.py:638-640`). P2 caught.

**1.6 Boundary line.** Passes on the tree, and on the 13 untracked files the test cannot see until `git add`.
Evidence: `scan()` run over `git ls-files --others --exclude-standard` → `hits: ['tests/test_boundary_line.py:52: smb url', 'tests/test_boundary_line.py:52: ipv4 literal']` (the plant line in the test itself, which the test excludes as `SELF`); P7 and P10 caught. Binary files skipped by `UnicodeDecodeError` (`:44-47`); `git ls-files -z` only (`:36-38`).

**1.7 Docs and config.** `HOME_BRIEFINGS_ROOT` overrides `output_dir`, blank and unset keep the YAML value (`config.py:221-224`, three tests); `anthropic<1` pinned; `.env.example` loses `OUTPUT_DIR` and `CONFIG_PATH`; placeholders only (but see W1); `tests/test_state_block.py` is in the 348.

**1.8 Deploy.** `deploy/update-server.sh` refuses a non-`main` branch (`:41`), a dirty tracked tree (`:42`), `main` off `origin/main` (`:46`), a dirty server clone (`:57`), a clone commit this checkout lacks (`:60`); CI skipped with a printed reminder when `.github/workflows` is absent (`:48-49`); reinstall on `requirements.txt` (`:66,92-94`); proof is `health` then `source`, never `run` (`:99-103`); renewal grep is `^#.*renew`, comment lines only, and prints a value only if someone puts the token on a comment line (`.env.example:27-28` keep them apart); G5 line (`:107-108`). `deploy/README.md` and `deploy/crontab`: `<home>`, `<uid>`, `<alias>`, `<briefings-folder>`, `<apps-dataset>`; `hostname: paperboy` per D8; `PATH` at `:77`; no address, hostname, path or channel id. One nit: at `:57` an SSH failure reads as a clean clone (empty substitution inside `[ ]`), but `:59`'s assignment then fails under `set -e`, so the script still stops.
Evidence: `bash -n deploy/update-server.sh; echo "exit=$?"` → `exit=0`.

**1.9 JSON envelope.** `_invoke` parses `result` and `is_error` (`:319-325`), caps `result` after parsing (`:327-332`, test `test_result_text_is_capped`), names the model from `modelUsage` (`:337`, fixture asserts `claude-fable-5-1` over the Haiku entry, P4); empty or missing `modelUsage` → `None`; non-JSON, `is_error`, or no `result` → `None` (parametrized test); `score_paper` still validates the JSON inside `result` (`:121,356-378`).

**README.** Adds the headless note (`:82`) and a Scheduling section (`:97-99`); no count, no state-block line, no `temperature` mention (S6 on tense).

## Memory

Patterns saved to `.claude/agent-memory/code-reviewer/wave-gate-reviews.md`: scan untracked files with the boundary test's own `scan()` before a gate; `.env.example` uncommented placeholders need placeholder handling or comments; the mutation-probe script shape.
