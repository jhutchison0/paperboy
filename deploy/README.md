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

Every `<placeholder>` below is a value that lives only on your machines, never in this repo. `<apps-dataset>` is the absolute mount path of the dataset that holds the app accounts' homes: read it from an existing app account with `dirname "$HOME"` over SSH, or in the web shell with `getent passwd <existing app> | cut -d: -f6 | xargs dirname`. `<alias>` is the one name you give the account in `~/.ssh/config` and as the git remote. Every `sudo` command runs in the TrueNAS web shell as the admin user (System, Shell); an app account over SSH has no sudo.

1. **The account (web shell, admin).** `home` is the parent folder, written absolute; `home_create` makes `<apps-dataset>/paperboy`:

   ```bash
   sudo midclt call user.create '{"username":"paperboy","full_name":"paperboy app","group_create":true,"home":"<apps-dataset>","home_create":true,"home_mode":"750","shell":"/usr/bin/bash","password_disabled":true,"smb":false}'
   ```

   The reply carries `"id": N` (a database id) and `"uid": U`; keep both, the uid for the App YAML. The key goes in a second call with the database id, never the uid; then the traverse entry, then the two checks:

   ```bash
   sudo midclt call user.update N '{"sshpubkey":"<the public key line your workstation deploys with>"}'
   sudo nfs4xdr_setfacl -a 'user:paperboy:rwxpDdaARWc--s:fd:allow' <apps-dataset>
   sudo nfs4xdr_getfacl <apps-dataset> | grep paperboy
   getent passwd paperboy
   ```

   `setfacl` echoes `ace_index: 0, mod_string: ...` when it adds the entry; one `paperboy` line from `getfacl` is the proof; `getent` shows the home under the dataset.

2. **The alias (workstation).** In `~/.ssh/config`, a block copied from an existing app account's block, with `Host <alias>` and `User paperboy`; `HostName` and `IdentityFile` unchanged. Test: `ssh <alias> 'id; ls -la ~'` prints the paperboy user and a `.ssh` folder.

3. **The repos (workstation, in the checkout).** A fresh bare repo points at `master`; the second command is why the clone is not empty:

   ```bash
   ssh <alias> 'git init -q --bare ~/paperboy.git && git -C ~/paperboy.git symbolic-ref HEAD refs/heads/main'
   git remote add <alias> <alias>:paperboy.git
   git push <alias> main
   ssh <alias> 'git clone -q ~/paperboy.git ~/paperboy && git -C ~/paperboy log --oneline -1'
   ```

4. **uv, the venv, supercronic and the Claude CLI (over SSH as the account).** The interpreter lands under `~/.local/share/uv/python/`, inside the home, so the container reaches it through the bind mount:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | UV_NO_MODIFY_PATH=1 sh
   cd ~/paperboy
   ~/.local/bin/uv venv --managed-python --python 3.12
   ~/.local/bin/uv pip install -r requirements.txt
   .venv/bin/python -c "import arxiv, feedparser, anthropic, click, yaml; print('ok')"
   mkdir -p ~/bin
   curl -fsSL -o ~/bin/supercronic https://github.com/aptible/supercronic/releases/download/v0.2.49/supercronic-linux-amd64
   echo "a53ae236602c7338aba3fbaff40bda6300eae3b9fedb8261eb06cfe3724430c1  $HOME/bin/supercronic" | sha256sum -c -
   chmod +x ~/bin/supercronic
   curl -fsSL https://claude.ai/install.sh | bash -s 2.1.310
   ~/.local/bin/claude --version
   mkdir -p ~/.claude && printf '{"model": "claude-opus-5-5", "env": {"DISABLE_AUTOUPDATER": "1"}}\n' > ~/.claude/settings.json
   ```

   Good looks like `ok`, `supercronic: OK`, and `2.1.310 (Claude Code)`. The `model` key names the model the daily run distills on, the lead's choice of 2026-10-25. Without it the CLI uses its own default, which that day was not the workstation's; the run record's `distill_model` field shows which model ran.

5. **The token.** On a workstation with a browser, `claude setup-token`; approve; copy the whole token it prints, from `sk-ant-oat01-` to the end. A copy taken from a wrapped terminal line loses the head and fails with `401 Invalid bearer token`. Build the server's file on the workstation and send it once; `.env.server` is gitignored:

   ```bash
   cp .env .env.server && chmod 600 .env.server
   ```

   Open `.env.server` in the editor and append:

   ```
   # CLAUDE_CODE_OAUTH_TOKEN generated YYYY-MM-DD; renew by YYYY-MM-DD
   CLAUDE_CODE_OAUTH_TOKEN=<the token>
   HOME_BRIEFINGS_ROOT=<briefings-folder>
   ```

   `PAPERBOY_SLACK_CHANNEL` carries over from the workstation's file; during the canary it holds the dev channel's id. `HOME_BRIEFINGS_ROOT` is the server's own absolute mount path on a shared dataset the desktop sees. A relative path lands inside the clone, where the desktop cannot reach it and a re-clone erases the record. Then prove the token here before it travels, and send the file:

   ```bash
   CLAUDE_CODE_OAUTH_TOKEN=<the token> claude -p "Reply with OK"
   scp .env.server <alias>:paperboy/.env
   ssh <alias> 'chmod 600 ~/paperboy/.env'
   ```

6. **The briefings folder.** It sits on a dataset the desktop mounts, not the apps dataset, so the account needs two entries there (web shell, admin): traverse on the dataset, and full rights with inheritance on the account's own folder. `sudo` asks for the admin password once; a missed prompt leaves every line unrun.

   ```bash
   sudo mkdir -p <share-dataset>/paperboy
   sudo nfs4xdr_setfacl -a 'user:paperboy:--x---a-R-c---:-------:allow' <share-dataset>
   sudo nfs4xdr_setfacl -a 'user:paperboy:rwxpDdaARWc--s:fd:allow' <share-dataset>/paperboy
   sudo nfs4xdr_getfacl <share-dataset>/paperboy | grep paperboy
   ```

   Then as the account: `mkdir -p <briefings-folder> && touch <briefings-folder>/.probe && rm <briefings-folder>/.probe`. The account creates `briefings` itself so the folder inherits its entry. Read a dataset's ACL type as admin, never as the account: `getfacl` on an NFSv4 dataset prints a trivial view of the mode bits, and `nfs4xdr_getfacl` as the account fails until the account holds the read-ACL right, so neither tells the account anything.

### Traps met on 2026-10-24, with their fixes

- `"Home Directory" must be an absolute path`: the `<apps-dataset>` placeholder was typed as written, or the path lacked its leading slash. Read the real path as the paragraph above says.
- `stx is not in the sudoers file`: the commands were run over SSH as an app account. Use the web shell as the admin.
- `[ENOENT] ALL: User <uid> does not exist` from `user.update`: the uid was passed where the database `id` belongs.
- `File/directory "mnt/..." could not be identified` from `setfacl`: the leading slash was missing.

### Traps met on 2026-10-25, with their fixes

- `claude: command not found`, or `health` printing `claude_cli FAILED`, in a shell where `~/.local/bin/claude --version` works: the shell is not a login shell. `.profile` adds `~/.local/bin` to PATH only at login and only if the folder exists then, so a session opened before the install, `su paperboy`, and `ssh <alias> 'command'` all lack it. `source ~/.profile`, or log in again. `deploy/update-server.sh` sets PATH inside its proof string for this reason.
- `401 Invalid bearer token` from a token that looks complete: the copy lost its `sk-ant-oat01-` head on a wrapped terminal line. Mint it again and prove it on the workstation before it travels (step 5).
- `nfs4xdr_getfacl: Failed to get NFSv4 ACL` as the account, while `getfacl` shows a plain `user::rwx group::rwx other::---`: not a POSIX dataset. The account lacked the read-ACL right; diagnose as admin (step 6).
- Inside the clone, `claude -p` warns that the workspace is untrusted and ignores the repo's `.claude/settings.json`. Run it from `~`. The pipeline runs the CLI from the system temp directory and never sees the warning.

### Traps met on 2026-10-26, with their fixes

- The first tick's record line reads `slack_error: ... CERTIFICATE_VERIFY_FAILED ...` and `articles_fetched: 0`, with `status: success` and a briefing on the share, where the host proof had posted and fetched 21 articles: the container has no CA store (`debian:bookworm-slim` ships none) and Python's `urllib` reads the OS store. arXiv came through because `requests` carries certifi; the CLI because Node bundles its own. Fix: `SSL_CERT_FILE` in the App YAML. Proved on the server as the account: `SSL_CERT_DIR=/nonexistent` reproduces both failures, and `SSL_CERT_FILE=<the venv's certifi bundle>` beside it recovers both.
- `git_sha: None` on the same line: the image has no `git`. Since 2026-10-26 the record reads `.git/HEAD` and the ref it names itself, so no binary is needed; deploy and the next tick carries the sha.

## The server's `.env`

Copy `.env.example` to `.env` in the clone. It is never committed, and the App reads no `env_file`: the run loads `.env` itself. The keys:

- `SLACK_BOT_TOKEN`: the bot token.
- `PAPERBOY_SLACK_CHANNEL`: the channel id; the dev channel during the canary.
- `CLAUDE_CODE_OAUTH_TOKEN` and its renewal comment.
- `HOME_BRIEFINGS_ROOT`: the briefings folder; it overrides `pipeline.output_dir`.

## First run on the host, before the App exists

As the account, in a login shell (an interactive `ssh <alias>`, or `bash -lc '...'`), in the clone, with `.env` loaded (`set -a && . ./.env && set +a`):

1. `cd ~ && claude -p "Reply with OK"` prints OK: the token authenticates. From `~`, not the clone, which prints a trust warning.
2. `.venv/bin/python main.py health` exits 0, every line OK or SKIPPED.
3. `.venv/bin/python main.py source` exits 0 and prints the counts.
4. `.venv/bin/python main.py run --slack` once, with the dev channel in `.env`; about six minutes. The post appears in the dev channel.
5. From the workstation, open the briefing in the shared folder by the filename in the post.
6. `~/bin/supercronic -test deploy/crontab` prints `crontab is valid`.

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
      SSL_CERT_FILE: <home>/paperboy/.venv/lib/python3.12/site-packages/certifi/cacert.pem
    command: ["<home>/bin/supercronic", "-passthrough-logs", "deploy/crontab"]
    restart: unless-stopped
    mem_limit: 512m
```

There is no `env_file`: the token must not appear in the App's environment or its YAML. `PATH` carries `<home>/.local/bin` so the run finds `claude`. If the form rejects `mem_limit`, drop it.

`SSL_CERT_FILE` names the venv's certifi bundle: the slim image ships no CA store, and `urllib`, which the Slack post and the feed fetch use, reads the OS store and finds nothing (the first tick, 2026-10-26). The path carries the venv's Python minor; change it when the venv is rebuilt on another. Saving a YAML edit restarts the App; the next tick is the proof. A YAML edit can also be read back the same minute, from the host as the account, without waiting for a tick: the container's processes run as the account's uid, so `pgrep -u "$(id -u)" -f bin/supercronic` finds the scheduler and `tr '\0' '\n' < /proc/<pid>/environ` prints its environment. On 2026-10-26 that read caught two wrong pastes of the `SSL_CERT_FILE` line (the `<home>` placeholder left in; then the clone folder dropped) before any tick ran on them.

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
