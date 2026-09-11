# TROUBLESHOOTING — Conflicts, Secrets, Common Failures, Best-Practices Checklist

Sidecar to `SKILL.md`. The most common venv failure modes with diagnoses and fixes, plus dependency-conflict resolution and a do/don't checklist. Command surfaces assume uv.

## Dependency Conflict Resolution

### Diagnosing Conflicts

**Symptom**: `uv pip install` fails with a version-conflict message. uv's resolver reports the full conflict chain in the error, which is usually diagnosis enough.

```bash
# What's currently installed
uv pip list

# Specific package
uv pip show package-name

# Full dependency tree
uv pip install pipdeptree
.venv/bin/pipdeptree

# Find conflicts in the tree
.venv/bin/pipdeptree --warn fail
```

### Common Conflict Patterns

#### Pattern 1: Direct Version Conflict

```
error: Because package-a==1.0 depends on lib>=2.0 and you require lib==1.5, ...
```

**Fix**: upgrade or downgrade one package.

```bash
uv pip install "lib>=2.0"
# OR
uv pip install "package-a==0.9"   # Older package with lower lib requirement
```

#### Pattern 2: Transitive Dependency Conflict

```
package-a requires lib>=2.0
package-b requires lib<2.0
```

Two of your direct deps disagree about a shared transitive. Three fixes:

1. **Find compatible versions** — usually possible if you go back far enough:
   ```bash
   uv pip install "package-a==X.Y" "package-b==A.B"
   ```

2. **Use separate environments** (see `SETUP.md` "Multiple Environments"):
   ```bash
   uv venv .venv-a --managed-python
   uv venv .venv-b --managed-python
   ```

3. **Find an alternative package** — sometimes the cleanest fix.

### Resolution Workflow

When you've inherited a broken environment:

```bash
# 1. Start fresh
deactivate
rm -rf .venv
uv venv --managed-python

# 2. Install one package at a time to find the culprit
uv pip install package-a
uv pip install package-b
# ... continue, observing which install introduces the conflict

# 3. Try compatible versions (uv resolves the full set together)
uv pip install "package-a>=1.0,<2.0" "package-b>=2.0"
```

## Environment Variables and Secrets

### .env Pattern

Two files: `.env.example` (committed template) and `.env` (gitignored, real values).

`.env.example`:

```bash
# Environment Configuration Template
# Copy to .env and fill in values
# NEVER commit .env to git!

# Application
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# API Keys
API_KEY=your_api_key_here
SECRET_KEY=generate_random_secret
```

`.env`:

```bash
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql://dev:dev@localhost:5432/myapp_dev
API_KEY=sk_test_abc123
SECRET_KEY=dev_secret_not_for_production
```

### Loading in Python

```python
from dotenv import load_dotenv
import os

load_dotenv()

debug = os.getenv("DEBUG", "false").lower() == "true"
api_key = os.getenv("API_KEY")
```

For deeper config management (profiles, hierarchical configs, validation), see the `configuration-management` skill.

### .gitignore for Environments

```gitignore
# Virtual environments
.venv/
venv/
ENV/
.venv-*/

# Environment files
.env
.env.local
.env.*.local

# Keep template
!.env.example
```

## Common Failures and Fixes

### Issue 1: `uv: command not found`

**Symptom**: uv was just installed but the shell can't find it.

**Cause**: the installer puts uv in `~/.local/bin`, which isn't on `PATH` in the current shell.

**Fix**:
```bash
export PATH="$HOME/.local/bin:$PATH"   # Current shell
# The installer adds this to your shell profile; restart the shell for permanence.
```

### Issue 2: "No module named pip" / `.venv/bin/pip` missing

**Symptom**: `pip` is not available inside the venv.

**Cause**: this is uv's default, not a defect. uv venvs don't bundle pip; `uv pip` fills that role from outside.

**Fix**:
```bash
uv pip install <package>       # The normal path — no in-venv pip needed

# Only if a tool genuinely requires pip inside the venv:
uv venv --seed --managed-python
```

### Issue 3: Venv coupled to a doomed interpreter

**Symptom**: every command in the venv fails with "No such file or directory" for `python`.

**Cause**: the venv symlinks to an interpreter that no longer exists (removed pyenv/conda, upgraded system Python).

**Fix**:
```bash
rm -rf .venv
uv venv --managed-python       # Managed interpreter survives incumbent removal
uv pip install -e ".[dev]"
```

### Issue 4: Wrong Python version in venv

**Symptom**: `python --version` shows a different version than expected.

**Cause**: venv was created with whatever interpreter uv discovered first on `PATH`.

**Fix**:
```bash
rm -rf .venv
uv python install 3.11
uv venv --managed-python --python 3.11
source .venv/bin/activate
python --version               # Verify
```

### Issue 5: "No virtual environment found"

**Symptom**: `uv pip install` errors because it can't find an environment to target.

**Cause**: running outside the project root with no venv active.

**Fix**:
```bash
cd <project-root>              # uv pip discovers ./.venv
# OR
source .venv/bin/activate      # Explicit activation works from anywhere
# OR target an alternate env:
VIRTUAL_ENV=.venv-ml uv pip install -r requirements-ml.txt
```

### Issue 6: SSL / corporate index errors

**Symptom**: `uv pip install` fails with TLS errors or can't reach PyPI.

**Fix**: point uv at the internal index:
```bash
export UV_INDEX_URL=https://your-internal-pypi.corp/simple/
# Or per-invocation:
uv pip install --index-url https://your-internal-pypi.corp/simple/ package-name
```
For a self-signed corporate proxy, `export SSL_CERT_FILE=/path/to/corp-ca.pem` (uv honors the standard TLS env vars).

### Issue 7: Packages installed but not importable

**Symptom**: `ModuleNotFoundError` despite `uv pip list` showing the package.

**Causes and fixes**:

1. **Wrong environment active**:
   ```bash
   which python    # Verify path
   uv pip list     # Verify package is listed in THIS env
   ```

2. **Package name differs from import name**:
   ```bash
   uv pip install python-dotenv    # Package name
   ```
   ```python
   import dotenv                   # Import name (different!)
   ```
   Check the package's docs for the correct import name.

3. **Editable install needed for in-repo code**:
   ```bash
   uv pip install -e .             # Install current project as editable
   ```

### Issue 8: Stale or corrupted cache

**Symptom**: installs pick up a wheel you know is outdated, or fail mid-download.

**Fix**:
```bash
uv cache clean package-name    # Evict one package
uv cache clean                 # Nuclear option
```
(Slow installs themselves are mostly a pre-uv problem; uv resolves and installs 10-100x faster than pip.)

## Best Practices Summary

**Do** ✅:
- Use one venv per project.
- Create venvs with `uv venv --managed-python`.
- Run all package operations through `uv pip`.
- Pin production dependencies (`uv pip compile` for lockfiles).
- Include `requirements-dev.txt` (or `[dev]` extras in `pyproject.toml`) for dev tools.
- Use `.env` for secrets, gitignored; provide `.env.example` template.
- Document the required Python version (`requires-python` in `pyproject.toml`).
- Automate setup with a script, Makefile, or `pyproject.toml`.

**Don't** ❌:
- Commit `.venv/` to git.
- Use `sudo` with any installer.
- Build venvs on pyenv/conda interpreters you plan to remove.
- Mix system and venv packages.
- Install in system Python.
- Commit secrets in `.env`.
- Share a single venv across multiple projects.
- Commit `.python-version` while pyenv is still installed anywhere (see `SETUP.md`).

## See Also

- `SKILL.md` — entry point and quick reference.
- `SETUP.md` — how to set up venvs and requirements files properly, and the incumbent-migration order.
- `configuration-management` skill — for hierarchical config and profile-based environments beyond simple `.env`.
