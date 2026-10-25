#!/usr/bin/env bash
# Update paperboy on the home server, in the one order that works:
# check the workstation, show what will change, push main to the server's
# bare repo, pull it into the app's clone, reinstall if requirements.txt
# changed, then prove the clone runs. Run it from the workstation's checkout.
#
#   deploy/update-server.sh <alias>             # do it, after one confirmation
#   deploy/update-server.sh <alias> --dry-run   # show the plan, change nothing
#
# <alias> is the git remote that points at the server's bare repo and the SSH
# host alias for the app's account. It lives in `git remote -v` and
# ~/.ssh/config, never in this repo.
set -euo pipefail

usage() {
    echo "usage: deploy/update-server.sh <alias> [--dry-run] [--yes] [--skip-ci]" >&2
    exit 2
}
die() {
    echo "update-server: $1" >&2
    exit "${2:-1}"
}

[ $# -ge 1 ] || usage
alias=$1
shift
dry=0 yes=0 skip_ci=0
for arg in "$@"; do
    case $arg in
        --dry-run) dry=1 ;;
        --yes) yes=1 ;;
        --skip-ci) skip_ci=1 ;;
        *) usage ;;
    esac
done

git remote get-url "$alias" >/dev/null 2>&1 ||
    die "no git remote named '$alias' here (see: git remote -v)" 2

# 1. The workstation: deploy only what CI has passed on GitHub's main.
[ "$(git rev-parse --abbrev-ref HEAD)" = main ] || die "check out main first"
[ -z "$(git status --porcelain --untracked-files=no)" ] ||
    die "uncommitted changes in tracked files; commit or stash them first"
git fetch -q origin main
head=$(git rev-parse HEAD)
[ "$head" = "$(git rev-parse origin/main)" ] ||
    die "main is not origin/main; merge through a PR and pull first"
if [ ! -d .github/workflows ]; then
    echo "no CI workflow here; skipping the CI check"
elif [ "$skip_ci" -eq 0 ]; then
    ci=$(gh run list --commit "$head" --limit 1 --json conclusion -q '.[0].conclusion' 2>/dev/null || true)
    [ "$ci" = success ] || die "CI on ${head:0:7} is '${ci:-unknown}', not success"
fi

# 2. The server: the clone must be clean, and its commit known here.
remote() { ssh "$alias" "$1"; }
[ -z "$(remote 'git -C ~/paperboy status --porcelain --untracked-files=no')" ] ||
    die "the server's clone has local edits; look at them before deploying"
was=$(remote 'git -C ~/paperboy rev-parse HEAD')
git cat-file -e "$was^{commit}" 2>/dev/null ||
    die "the server's clone is at ${was:0:7}, which this checkout lacks"
changed=$(git diff --name-only "$was" "$head")

# 3. The plan, and the steps only a person can do.
install=0 restart=0 env=0
grep -qx 'requirements.txt' <<<"$changed" && install=1
grep -qx 'deploy/crontab' <<<"$changed" && restart=1
grep -qx '.env.example' <<<"$changed" && env=1
echo "The server's clone: ${was:0:7} -> ${head:0:7}"
git log --oneline "$was..$head" | sed 's/^/  /'
echo "Steps:"
echo "  git push $alias main; pull into the clone"
[ "$install" -eq 1 ] && echo "  uv pip install -r requirements.txt (it changed)"
echo "  check: the clone's commit, then main.py health and main.py source (never run)"
hand=()
[ "$restart" -eq 1 ] && hand+=("restart the App in the TrueNAS UI (deploy/crontab changed; supercronic reads it once)")
[ "$env" -eq 1 ] && hand+=("compare the server's .env with .env.example (it changed)")
if [ ${#hand[@]} -gt 0 ]; then
    echo "After, by hand:"
    printf '  %s\n' "${hand[@]}"
fi
[ "$dry" -eq 0 ] || exit 0

if [ "$yes" -eq 0 ]; then
    read -r -p "Deploy ${head:0:7} to '$alias'? A canary window counts this as an intervention. [y/N] " answer || answer=
    [ "$answer" = y ] || [ "$answer" = Y ] || die "nothing pushed"
fi

# 4. The deploy. Every tick is a fresh process, so the next tick runs this.
git push -q "$alias" main
remote 'git -C ~/paperboy pull -q --ff-only'
if [ "$install" -eq 1 ]; then
    remote 'cd ~/paperboy && ~/.local/bin/uv pip install -q -r requirements.txt'
fi

# 5. The proof: the clone's commit, then health and source with .env loaded.
now=$(remote 'git -C ~/paperboy rev-parse HEAD')
[ "$now" = "$head" ] || die "the clone is at ${now:0:7}, not ${head:0:7}"
prove='cd ~/paperboy && set -a && . ./.env && set +a && .venv/bin/python main.py'
remote "$prove health" >/dev/null ||
    die "main.py health failed on the server; read it with the same command over ssh"
remote "$prove source" >/dev/null ||
    die "main.py source failed on the server; read it with the same command over ssh"
echo "Deployed ${head:0:7}; health and source passed."
remote '~/.local/bin/claude --version'
remote "grep -E '^#.*renew' ~/paperboy/.env" || echo "no renewal comment in the server's .env"
remote "git -C ~/paperboy cat-file -e 'c06e8ba^{commit}' && echo 'G5: clone is post-rewrite'" ||
    echo "G5: clone predates the history rewrite"
if [ ${#hand[@]} -gt 0 ]; then
    echo "Now, by hand:"
    printf '  %s\n' "${hand[@]}"
fi
