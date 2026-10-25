# Deploying paperboy (CONOP COURIER)

The runbook for the daily run: one briefing each morning, a summary posted to Slack. It runs on the home server as a TrueNAS Custom App over a bind-mounted clone, with no image build. The general procedure is the runbook in the sister repo `daily_weather` (`docs/runbooks/home-server-custom-app.md`); this file is paperboy's instance. Dataset paths, the account's uid and the server's name stay out of this repo.

## What runs where

One container named `paperboy` runs supercronic with `deploy/crontab`, which has one line: `main.py run --slack` at 05:30. Each tick is a fresh process that exits, so a code change is live at the next tick after a pull. A crontab change needs the App restarted, because supercronic reads the file once. The command is relative to the working directory, the clone.

The briefings, `.selection_history.json` (dedup) and `run_history.jsonl` (the run record) live under `HOME_BRIEFINGS_ROOT`, a folder on the shared dataset. The workstation reads the briefing from the same folder. Logs go to the container's log.

## Updating the app

From the workstation's checkout, after the change has merged on GitHub:

```bash
git switch main && git pull
deploy/update-server.sh <alias> --dry-run    # read the plan; nothing changes
deploy/update-server.sh <alias>              # deploy; answer y
```

The script refuses anything but `main`, uncommitted changes, a `main` that differs from GitHub's, a server clone with local edits, and a clone on a commit this checkout lacks. When `.github/workflows` does not exist it prints `no CI workflow here; skipping the CI check`. It pushes to the bare repo, pulls with `--ff-only`, and runs `uv pip install -r requirements.txt` if that file changed. The proof is `main.py health` then `main.py source` with `.env` loaded; both must exit 0. It never runs `run`, which would post and write dedup history. Last it prints the server's `claude --version`, the renewal comment from the server's `.env` (comment lines only, never a value), and the `G5: clone is post-rewrite` line.

It leaves three things to you:

- **`deploy/crontab` changed:** restart the App in the TrueNAS UI.
- **`.env.example` changed:** compare it with the server's `.env`.
- **An App YAML change** (memory limit, mounts): edit it in the UI.

During the canary, any deploy is an intervention: note the time in the session record.

## Server-side setup

1. **The account (TrueNAS UI, the lead).** A least-privilege user `paperboy`, next uid, home directory on the apps dataset, bash shell, the lead's SSH public key. The home directory must exist when the form is saved, and the dataset's ACL needs a traverse entry for the user. No sudo, no Docker.
2. **The alias (workstation).** One name, `<alias>`, for both the git remote and the SSH host in `~/.ssh/config`.
3. **The repos (as that account).** `git init --bare --initial-branch=main ~/paperboy.git` (HEAD on `main`), then from the workstation `git remote add <alias> <alias>:paperboy.git && git push <alias> main`, then `git clone ~/paperboy.git ~/paperboy`.
4. **uv and the venv.** Install uv for the account if absent, then `cd ~/paperboy && uv venv --managed-python --python 3.12 && uv pip install -r requirements.txt`. The container runs this venv through the bind mount, so the interpreter must stay under the home.
5. **supercronic.** Download the pinned linux-amd64 release to `~/bin/supercronic`, check its sha256, `chmod +x`.
6. **The Claude CLI.** `curl -fsSL https://claude.ai/install.sh | bash -s 2.1.310`, then write `~/.claude/settings.json` as `{"env": {"DISABLE_AUTOUPDATER": "1"}}` so the version stays pinned.
7. **The token.** On the workstation run `claude setup-token`, then paste the token into the server's `.env` as `CLAUDE_CODE_OAUTH_TOKEN` with the comment `# CLAUDE_CODE_OAUTH_TOKEN generated YYYY-MM-DD; renew by YYYY-MM-DD` beside it.
8. **The briefings folder.** Create `<briefings-folder>` on the shared dataset, give the account write access, and set `HOME_BRIEFINGS_ROOT` to it in `.env`.

## The server's `.env`

Copy `.env.example` to `.env` in the clone. It is never committed, and the App reads no `env_file`: the run loads `.env` itself. The keys:

- `SLACK_BOT_TOKEN`: the bot token.
- `PAPERBOY_SLACK_CHANNEL`: the channel id; the dev channel during the canary.
- `CLAUDE_CODE_OAUTH_TOKEN` and its renewal comment.
- `HOME_BRIEFINGS_ROOT`: the briefings folder; it overrides `pipeline.output_dir`.

## First run on the host, before the App exists

As the account, in the clone, with `.env` loaded (`set -a && . ./.env && set +a`):

1. `.venv/bin/python main.py health` exits 0.
2. `.venv/bin/python main.py source` exits 0.
3. `.venv/bin/python main.py run --slack` once, with the dev channel in `.env`. The post appears in the dev channel.
4. From the workstation, find the briefing in the shared folder by the filename in the post.

## The App YAML

TrueNAS UI, Apps, Discover Apps, Custom App, Install via YAML. Name `paperboy`, with `<home>` the account's home and `<uid>` its uid:

```yaml
services:
  paperboy:
    image: debian:bookworm-slim
    user: "<uid>:<uid>"
    hostname: paperboy
    working_dir: <home>/paperboy
    volumes:
      - <home>:<home>
      # - <apps-dataset>/<briefings-folder>:<apps-dataset>/<briefings-folder>   # only if outside the home
    environment:
      HOME: <home>
      TZ: America/Chicago
      PATH: <home>/.local/bin:/usr/local/bin:/usr/bin:/bin
    command: ["<home>/bin/supercronic", "-passthrough-logs", "deploy/crontab"]
    restart: unless-stopped
    mem_limit: 512m
```

There is no `env_file`: the token must not appear in the App's environment or its YAML. `PATH` carries `<home>/.local/bin` so the run finds `claude`. If the form rejects `mem_limit`, drop it.

## Canary

Seven mornings, posting to the dev channel. Check each morning:

- [ ] The post appears in the dev channel by 05:45.
- [ ] The briefing file named in the post exists in the shared folder.
- [ ] The post carries the title, link, reasoning, top five, filename, legend and telemetry line.
- [ ] A new line is in `run_history.jsonl` with `status: success`.
- [ ] No paper repeats across days.
- [ ] Memory stays under 512 MB.

## Switching to the real channel

Edit `PAPERBOY_SLACK_CHANNEL` in the server's `.env` to the real channel id. It is live at the next tick; no restart, because each tick reads `.env` fresh.
