# PCC - Pre-Code Check

Run a quick, standardized checklist before pushing code. Same checks every time - muscle memory.

**Military origin**: Pre-Combat Check - the quick gear check every soldier does before moving out. Ammo, water, weapon. No thinking required, just verify the basics.

## Philosophy

PCC is **fast and deterministic**. It answers: "Am I safe to push?"

- Same checklist every time
- Pass/fail, no judgment calls
- Takes seconds, not minutes
- Run before every push

For context-aware inspection based on what you changed, use `/pci` instead.

## Checklist

Run these checks and report results:

### 1. Secrets Check
```bash
# Check for staged secrets
git diff --cached --name-only | xargs grep -l -E "(API_KEY|SECRET|PASSWORD|TOKEN|PRIVATE_KEY)\s*=" 2>/dev/null || echo "clean"

# Check for .env files staged
git diff --cached --name-only | grep -E "^\.env" || echo "clean"
```
- FAIL if any secrets patterns found in staged files
- FAIL if .env files are staged

### 2. Tests Pass
```bash
# Run all tests
pytest
```
- FAIL if any tests fail
- Report count: "X tests passed"

### 3. No Debug Artifacts
```bash
# Check for common debug leftovers in staged files
git diff --cached | grep -E "^\+" | grep -E "(breakpoint\(\)|import pdb|print\(.*DEBUG)" || echo "clean"
```
- WARN if debug statements found (not a hard fail, but flag it)

### 4. Git State Check
```bash
# Check for uncommitted changes that might be forgotten
git status --short
```
- WARN if unstaged changes exist (might forget to include them)
- INFO showing current branch

### 5. Reference Integrity (living docs)
```bash
# Path-shaped references in orientation surfaces must resolve.
# Allowlist covers runtime artifacts that are legitimately absent
# (upstream-update.md, gitignored audit logs and output/).
{ cat CLAUDE.md CONTEXT.md README.md LANGUAGE.md .claude/README.md 2>/dev/null; \
  sed -n '/^## Active/,/^## Completed/p' docs/tasks.md; } \
  | grep -oE '(docs|src|tests|config|scripts|output|\.claude|\.github)/[A-Za-z0-9_./-]+\.[A-Za-z0-9]{2,4}' \
  | grep -vE '^\.claude/(upstream-update\.md|audits/)|^output/' \
  | sort -u | while read -r p; do [ -e "$p" ] || echo "MISSING: $p"; done
```
- The `sed` range assumes headings named exactly `## Active` and `## Completed` (paperboy's `docs/tasks.md` has both, with `## Blocked` between them — the range deliberately covers Active and Blocked). If the headings ever change, re-verify the captured range by hand; a prefix match with no end anchor silently runs to end of file.
- `output/` is allowlisted whole: everything under it is a gitignored runtime artifact (briefings, `.selection_history.json`) that LANGUAGE.md legitimately names while absent.
- Expected output: empty. First run 2026-09-10 found 3 findings, dispositioned to a 0-MISSING baseline: `output/.selection_history.json` allowlisted (runtime), `.claude/agent-memory/` allowlisted (runtime), `docs/reviews/` created with `.gitkeep` (convention dir LANGUAGE.md names). WARN on any MISSING line, and record the run's count in the session doc (it is metric M2 in `.claude/skills/traversing-the-knowledge-base/SKILL.md`; an unrecorded run is indistinguishable from an unrun check)
- Any MISSING line is caught drift and fires that skill's build trigger

**Three known blind spots. A clean run means clean only within them** (found in the field, 2026-08-21 `contract-knowledge-graph` and 2026-08-22 `aar_ai_pipeline`):
1. **Directory references are invisible.** The regex requires a file extension, so `.claude/agents/` never matches. Run the directory pass below alongside the file pass.
2. **No notion of a base directory.** Every path resolves against the repo root, so a cross-repo citation and a path inside a documented `cd subdir && ...` command both report MISSING while the file exists. Hand-verify before editing the doc.
3. **A missing surface costs coverage silently.** `cat` failures are swallowed by `2>/dev/null`; an absent `CONTEXT.md` reads the same as a clean one.

```bash
# Directory pass, covering blind spot 1. Same surfaces, no extension required.
{ cat CLAUDE.md CONTEXT.md README.md LANGUAGE.md .claude/README.md 2>/dev/null; } \
  | grep -oE '(docs|src|tests|config|scripts|output|\.claude|\.github)/[A-Za-z0-9_./-]*/' \
  | grep -vE '^(\.claude/audits/|\.claude/agent-memory/|output/)' \
  | sort -u | while read -r p; do [ -d "$p" ] || echo "MISSING-DIR: $p"; done
```

### 6. Gate-Surface Separation
```bash
# Gate surfaces (checks, hooks, settings) change alone:
# never bundled with work those gates judge.
staged=$(git diff --cached --name-only)
gates=$(echo "$staged" | grep -E '^\.claude/(hooks/|settings\.json|commands/(pcc|pci)\.md)' || true)
if [ -n "$gates" ] && [ "$(echo "$staged" | grep -c .)" -ne "$(echo "$gates" | grep -c .)" ]; then
  echo "WARN: gate surfaces staged with other files; split into a [gate] commit:"; echo "$gates"
fi
```
- WARN only; the fix is two commits, with the gate change isolated and tagged `[gate]`

## Output Format

```
PCC Results
===========
[PASS] No secrets in staged files
[PASS] Tests pass (12 tests in 0.8s)
[WARN] Debug statement found: src/sourcer.py:45
[INFO] Branch: main, 3 files staged

PCC Status: READY TO PUSH (1 warning)
```

Or on failure:
```
PCC Results
===========
[PASS] No secrets in staged files
[FAIL] Tests failing
       2 failed, 10 passed
       - tests/test_pipeline.py::test_selector_scoring - AssertionError
[PASS] No debug artifacts

PCC Status: NOT READY - 1 failure, resolve before pushing
```

## Quick Reference

| Check | Pass Condition | On Fail |
|-------|----------------|---------|
| Secrets | No API_KEY, SECRET, PASSWORD, TOKEN in diff | Block push |
| Tests | `pytest` all pass | Block push |
| Debug | No breakpoint/pdb/print in staged code | Warn only |
| Git state | Clean or intentional | Info only |
| Reference integrity | Zero MISSING paths in living docs (allowlist current) | Warn only |
| Gate separation | Gate surfaces staged alone (`[gate]` commit) | Warn only |

## This Repo's Test Commands

| Command | What it runs |
|---------|--------------|
| `pytest` | All tests |
| `pytest -k sourcer` | Source/fetch tests only |
| `pytest -k selector` | Selection/scoring tests only |
| `pytest -k distiller` | Distiller/briefing tests only |
| `pytest -k pipeline` | Pipeline orchestration tests only |
| `pytest -k config` | Configuration tests only |
| `pytest -k models` | Data model tests only |

## Integration

PCC is designed to be called:
- Manually before push: `/pcc`
- From session-end workflow (optional step)
- After completing a feature before PR

It does NOT:
- Analyze what you changed (that's PCI)
- Make judgment calls about code quality
- Take more than 60 seconds (test suite is fast)

## Escalation

If PCC passes but you want more confidence (big change, touching core systems, pre-merge):
```
/pci
```

If PCC fails repeatedly or you're unsure why:
```
/pci --verbose
```
