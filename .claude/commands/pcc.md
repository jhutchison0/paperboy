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
       - test_pipeline.py::test_selector_scoring - AssertionError
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
