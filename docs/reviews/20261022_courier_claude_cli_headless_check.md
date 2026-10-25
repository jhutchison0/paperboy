# Check: `claude -p` headless on a home server under a subscription

**Author**: claude-code-guide agent, briefed by the lead
**Date**: 2026-10-22
**Type**: Documentation check (read-only; no command run)
**For**: CONOP COURIER, the backend decision

Scope: running `claude -p` from cron inside a container on the home server, as an unprivileged account with `HOME` on a bind mount, under a personal Max subscription, through `src/agent_runner.py` (which strips `ANTHROPIC_API_KEY` and every `CLAUDE*` variable before the call and sets cwd to the temp dir). Every answer below names the page it came from. Quotes passed through a fetch summarizer; check the exact wording before citing them outside this repo.

**Summary**: `claude setup-token` plus `CLAUDE_CODE_OAUTH_TOKEN` is the documented headless route. The wrapper's `CLAUDE*` strip removes that variable, so as written it breaks subscription auth unless a stored login exists. The docs do not say whether unattended cron use is permitted under a consumer plan, nor whether `-p` draws from the same limits as interactive use.

## 1. Headless authentication

- `claude setup-token` exists. It runs the browser login flow and prints a long-lived OAuth token ("one-year OAuth token"); it requires a Pro, Max, Team or Enterprise plan; it can only make model requests. It does not save the token. Source: https://code.claude.com/docs/en/authentication.md (Generate a long-lived token); https://code.claude.com/docs/en/cli-reference.md.
- The token is consumed via `CLAUDE_CODE_OAUTH_TOKEN`. Precedence: below `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_API_KEY` and `apiKeyHelper`; above the stored `/login` credential. Source: authentication.md (Authentication precedence).
- The docs do not say whether `setup-token` works over SSH with no browser; they describe only the browser flow. Test on the server first.
- Stored credentials: `/login` and `claude auth login` store `~/.claude/.credentials.json` (mode 0600), or under `CLAUDE_CONFIG_DIR` when set. A one-time SSH login persists if `~/.claude` sits on the bind mount. The docs describe pasting a login code in SSH and container sessions. Stored logins expire; unattended runs then stop and "can't recover until you sign in again". Source: authentication.md (Credential management; Renew an expiring login).
- Copying a credentials file from a workstation: not addressed. The legal page says developers "may not collect, store, or intermediate Claude.ai credentials or session tokens". Source: https://code.claude.com/docs/en/legal-and-compliance.md (Authentication and credential use).

## 2. The wrapper's `CLAUDE*` strip

- It strips `CLAUDE_CODE_OAUTH_TOKEN`. Without it, `claude -p` falls back to a stored `/login` credential if one exists; otherwise auth fails. Fix: re-add that one variable after the strip.
- Stripping `ANTHROPIC_API_KEY` is right: in `-p` mode the key "is always used when present", which would override the subscription. Source: https://code.claude.com/docs/en/env-vars.md.
- The strip also removes isolation knobs worth setting after it: `CLAUDE_CONFIG_DIR`, `CLAUDE_CODE_DISABLE_CLAUDE_MDS`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY`, `CLAUDE_CODE_MAX_TURNS`.
- `ANTHROPIC_AUTH_TOKEN` and `ANTHROPIC_BASE_URL` survive the strip; `ANTHROPIC_AUTH_TOKEN` outranks the OAuth token, so strip it explicitly.
- Named for headless runs: `DISABLE_AUTOUPDATER=1` (stops background checks; `claude update` still works), `DISABLE_UPDATES=1` (blocks every update path), `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`, `CLAUDE_CODE_MAX_TURNS`. Source: env-vars.md; https://code.claude.com/docs/en/setup.md.
- `HOME` is not documented as an override; paths are written as `~/.claude`. No minimal required environment is documented. Keep `PATH` and `HOME`; test the rest.

## 3. Terms and limits

- No page explicitly permits or forbids unattended, scheduled use of a consumer subscription.
- Consumer Terms, section 3, item 7 (fetched text): except "via an Anthropic API Key or where we otherwise explicitly permit it", users may not "access the Services through automated or non-human means, whether through a bot, script, or otherwise." Source: https://www.anthropic.com/legal/consumer-terms.
- Claude Code legal page: OAuth authentication "is intended exclusively for purchasers of Claude Free, Pro, Max, Team, and Enterprise subscription plans and is designed to support ordinary use of Claude Code and other native Anthropic applications"; "Advertised usage limits for Pro and Max plans assume ordinary, individual usage of Claude Code and the Agent SDK"; developers building products are told to use API keys. Source: legal-and-compliance.md (Usage policy).
- The `setup-token` section names "CI pipelines and scripts" as its use case, the closest explicit sanction for a script. The agent's reading: one personal, low-volume scheduled job sits in the documented zone; a multi-user service does not. Not legal advice.
- If the subscription or the output is tied to work, the Commercial Terms apply instead. Source: legal-and-compliance.md (License).
- Limits: "Every plan has usage limits that reset on a rolling five-hour session window"; "paid plans add weekly limits on top"; the terminal and chats "draw from one pool". Source: https://claude.com/pricing. No official weekly numbers found; the support article returned 404. Whether `-p` draws from the same window as interactive use is not stated; watch `/usage` after a test run. Source: https://code.claude.com/docs/en/costs.md.
- `--max-budget-usd` is a client-side list-price estimate, not billing: a runaway guard only.

## 4. Native installer on debian bookworm-slim

- `curl -fsSL https://claude.ai/install.sh | bash`; pin with `bash -s <version>` or `bash -s stable`. Binary at `~/.local/bin/claude`, a symlink into `~/.local/share/claude/versions/`; the installer keeps the two newest versions. Source: setup.md (Install a specific version; Auto-updates; Install on network storage).
- Native installs auto-update in the background. Disable with `"env": {"DISABLE_AUTOUPDATER": "1"}` in `~/.claude/settings.json`, or `DISABLE_UPDATES=1` to block every path; `autoUpdatesChannel: "stable"` and `minimumVersion` also exist. Source: setup.md (Update Claude Code).
- Requirements: Debian 10+, 4 GB RAM, x64 or ARM64; no glibc version stated. A fresh Debian may lack `curl`; `ca-certificates` on a slim image is the agent's inference. The apt repository (`downloads.claude.ai/claude-code/apt/stable`) updates only through `apt upgrade`. The npm route needs Node.js 22+; skip it. Verify with `claude --version` and `claude doctor`.

## 5. Flags for a scripted call

All from https://code.claude.com/docs/en/cli-reference.md unless noted.

- `--output-format json`: output has `result` and `session_id`; a failed run exits non-zero and in-run failures print as the result, so check the exit code. Source: https://code.claude.com/docs/en/headless.md.
- `--model`: alias or full name; use a full name to pin.
- `--max-turns`: print mode only; errors at the limit; no default. Env equivalent `CLAUDE_CODE_MAX_TURNS`.
- `--tools ""` disables all built-in tools; `--disallowedTools "*"` removes every tool from context; `--allowedTools` only auto-approves and does not forbid. `--tools` does not touch MCP tools, so add `--disallowedTools "mcp__*"`. `--restricted` (v2.1.248+) removes command-running tools and confines file tools.
- `--no-session-persistence`: print mode only; no transcript saved.
- `--settings`: a JSON file or inline JSON overriding keys; `--setting-sources` (`user`, `project`, `local`) drops whole sources.
- `--append-system-prompt` appends; `--system-prompt` replaces the whole prompt and drops the default guidance.
- `--max-budget-usd`: print mode only; estimate (section 3).
- `--permission-prompts none` (v2.1.259+) denies prompts instead of hanging. `--safe-mode` disables CLAUDE.md, hooks, skills, plugins, MCP and auto memory while leaving auth and built-in tools working. `--bare` is not usable with a subscription: it "never reads OAuth credentials or the system keychain". Source: headless.md (Start faster with bare mode).

## 6. CLAUDE.md in `-p` runs

- Claude Code loads `CLAUDE.md` and `CLAUDE.local.md` from the working directory and every directory above it, plus `~/.claude/CLAUDE.md` and `/etc/claude-code/CLAUDE.md`. If none exists in the cwd chain, `AGENTS.md` loads instead. Source: https://code.claude.com/docs/en/memory.md.
- With cwd in the temp dir, its ancestors (`/tmp`, `/`) are also checked; make sure neither holds a `CLAUDE.md`. `claudeMdExcludes` can skip ancestor files.
- Ways to keep a run clean: `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` (set after the strip); `--safe-mode` (untested here; auth intact); `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`; `--no-session-persistence`. Without `--bare`, `-p` still runs hooks from `~/.claude/settings.json` and `.claude/settings.json`: check the bind-mounted home for hooks.

## Not answered by the docs

Whether `setup-token` works headless; whether a copied credentials file is valid; whether `-p` shares the interactive limit pool; whether unattended consumer-plan use is permitted; a `HOME` override; the minimal environment. These go to Anthropic support or `/feedback`. Re-check the pages before production use.

## Addendum, 2026-10-23: the lead's re-check of the subscription path

The lead asked why the server could not run on the personal Max subscription. The lead (through the session) fetched three pages directly on 2026-10-23 and quotes them verbatim here. The first draft of CONOP COURIER weighed the Consumer Terms clause above these; on reading them, D2 reversed to the subscription.

**https://code.claude.com/docs/en/authentication.md**, "Generate a long-lived token": "For CI pipelines, scripts, or other environments where interactive browser login isn't available, generate a one-year OAuth token with `claude setup-token`"; "It does not save the token anywhere; copy it and set it as the `CLAUDE_CODE_OAUTH_TOKEN` environment variable wherever you want to authenticate"; "This token authenticates with your Claude subscription and requires a Pro, Max, Team, or Enterprise plan. It can only make model requests"; "Bare mode does not read `CLAUDE_CODE_OAUTH_TOKEN`." Same page, "Authentication precedence", item 5: "`CLAUDE_CODE_OAUTH_TOKEN` environment variable. A long-lived OAuth token generated by `claude setup-token`. Use this for CI pipelines and scripts where browser login isn't available." Item 2 (`ANTHROPIC_AUTH_TOKEN`) and item 3 (`ANTHROPIC_API_KEY`) outrank it; "In non-interactive mode (`-p`), the key is always used when present." "Renew an expiring login": "Once the stored login expires and can't be refreshed, each model request fails with `Login expired · Please run /login` until you sign in again."

**https://code.claude.com/docs/en/legal-and-compliance.md**, "Authentication and credential use": "OAuth authentication is intended exclusively for purchasers of Claude Free, Pro, Max, Team, and Enterprise subscription plans and is designed to support ordinary use of Claude Code and other native Anthropic applications." "Developers building products or services that interact with Claude's capabilities ... should use API key authentication ... Anthropic does not permit third-party developers to offer Claude.ai login into their own applications, or to route requests through Free, Pro, or Max plan credentials on behalf of their users. Moreover, developers may not collect, store, or intermediate Claude.ai credentials or session tokens." And: "Nor does it prevent an end user from signing in to the unmodified Claude Code binary with their own Claude subscription." "Acceptable use": "Advertised usage limits for Pro and Max plans assume ordinary, individual usage of Claude Code and the Agent SDK."

**https://code.claude.com/docs/en/headless.md**, "Start faster with bare mode": "`--bare` is the recommended mode for scripted and SDK calls, and will become the default for `-p` in a future release." "In bare mode, Claude Code never reads OAuth credentials or the system keychain." "Without `--bare`, a `-p` session runs the hooks in a project's `.claude/settings.json` and connects the servers in its `.mcp.json`, even in a folder you've never trusted." Same page: "With `--output-format json`, the response payload includes `total_cost_usd` and a per-model cost breakdown"; `--permission-prompts none` "when nobody is available to answer permission prompts, for example in a scheduled job" (v2.1.259 or later).

**What this changes.** The subscription route for a script is documented, and the restriction text names third-party developers and products, not an end user's own job on the unmodified binary. The first draft's three reasons for an API key reduce to one code change (keep `CLAUDE_CODE_OAUTH_TOKEN` through the strip) and two contained risks: the yearly renewal, and a future CLI default to bare mode, which a pinned CLI version holds off. Still not answered by the docs: whether `-p` draws from the same limit pool as interactive use (the record will show it), and the legal reading itself, which is the lead's.
