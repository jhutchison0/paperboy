---
name: using-topic-branches
description: Branch by work shape, not by domain. Lead-only doc/ADR/small-refactor work lands directly on main; team-deployed or multi-agent code work with an audit gate uses a short-lived topic branch that is merged and then deleted (local + origin) immediately. Use when starting a unit of work, deciding whether to branch, merging at a gate, or auditing standing branches across a repo.
version: "1.0.0"
---

# Using Topic Branches

Branch on the **shape of the work**, not on a permanent partition of the codebase. The
goal is one logical change per branch (clean diff for review) without the standing cost
of long-lived branches (drift, resync ceremony, stale tracking remotes).

This replaces the older "one permanent branch per domain" convention. Permanent domain
branches (`dev-safety`, `dev-ui`, `dev-perception`, …) force constant resyncing against
`main` for **no review benefit** — the audit gate happens at merge time regardless of how
long the branch has existed. Short-lived topic branches keep the isolation and drop the
permanence.

## The Two Shapes

**1. Lead-only doc / ADR / small-refactor work → land directly on `main`.**

No branch overhead for changes that have no audit gate and no parallel contributors:
session docs, ADRs, changelog/roadmap updates, comment fixes, config-only tweaks, small
single-file refactors you are reviewing yourself. The branch would add ceremony and buy
nothing.

**2. Team-deployed or multi-agent code work with an audit gate → use a topic branch.**

When the work has an explicit review/test gate before it can land (a code-reviewer pass, a
safety audit, a test-runner gate) or multiple contributors are involved, isolate it:

- **Name it** `topic/<scope>-<slug>` — e.g. `topic/vram-coordinator`, `topic/c2-identity-evidence`, `topic/dashboard-wiring`. Scope is the wave/feature; slug is the one logical change.
- **Create it at the start of the work**, branch from current `main`.
- **Merge it via merge-commit at the gate** once the audit/tests pass.
- **Delete it local + origin immediately after merge.** Lifetime is hours to one session.

```bash
git switch -c topic/<scope>-<slug>          # at start of work
# ... work, review gate passes ...
git switch main && git merge --no-ff topic/<scope>-<slug>
git push origin main
git branch -d topic/<scope>-<slug>          # delete local
git push origin --delete topic/<scope>-<slug>  # delete remote
```

**Parallel contributors on independent files within one task share the same topic
branch.** Do not split into per-contributor branches — file ownership (each contributor
owns distinct files) prevents conflict, and a single branch keeps the change reviewable as
one diff.

## Hygiene Rules

- **Delete after merge.** A merged topic branch left standing becomes tomorrow's stale
  branch. Delete local + origin in the same step as the merge.
- **One logical change per branch.** If a branch grows a second unrelated change, that is a
  signal to merge what's done and branch again.
- **Don't resync long-lived branches.** If you find yourself repeatedly merging `main` into
  a topic branch to keep it current, the branch has outlived its shape — land it or close it.

## Auditing Standing Branches

Periodically check a repo (or a set of repos) for branch debt. For every non-`main` branch,
classify it by its commit position relative to the authoritative `origin/main`:

```bash
git fetch --quiet origin
for b in $(git for-each-ref --format='%(refname:short)' refs/heads refs/remotes/origin \
           | grep -vE '(^|/)(HEAD|main|master)$'); do
  ahead=$(git rev-list --count origin/main.."$b")   # unique commits on the branch
  behind=$(git rev-list --count "$b"..origin/main)  # commits main has that branch lacks
  printf '%-40s ahead=%-4s behind=%s\n' "$b" "$ahead" "$behind"
done
```

Then act by `ahead` count — **never delete on `behind` alone**:

| `ahead` | Meaning | Action |
|---|---|---|
| `0` | Fully merged; every commit is already in `main` | **Safe to delete** (local + origin). |
| `>0`, `behind == 0` | `main` is *behind* the branch — work never merged back | **Merge** branch → `main` (often fast-forward), *then* delete. |
| `>0`, `behind > 0` | Diverged — branch has unique work, `main` moved on too | **Investigate the unique commits** (`git log origin/main..<branch>`). Merge if still valuable; abandon-and-delete only if superseded. The user decides — never auto-delete a diverged branch. |

Dependabot / bot branches (`origin/dependabot/*`) are managed open PRs, not local branch
debt — merge or close them through the forge, don't `git push --delete` them blind.

## Anti-Patterns to Avoid

- **Permanent domain branches** (`dev-<domain>`) — the convention this skill replaces.
- **Deleting a branch because it is `behind`** — behind says nothing about unmerged work;
  only `ahead == 0` proves a branch is safe to drop.
- **Per-contributor branches within one task** — split by files, not by branches.
- **Leaving merged topic branches standing** — that is how a clean repo accrues debt.
- **Branching for lead-only doc/ADR work** — overhead with no gate to justify it.

## Sources

- Distilled from MEGAN's CONOP-002 §4.2 retrospective (2026-05-24), where six permanent
  `dev-*` branches were retired in favor of this policy after they were found to force
  resync ceremony for no review benefit.
