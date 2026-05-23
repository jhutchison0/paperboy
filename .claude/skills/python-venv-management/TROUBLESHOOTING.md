# TROUBLESHOOTING — Conflicts, Secrets, Common Failures, Best-Practices Checklist

Sidecar to `SKILL.md`. The seven most common venv failure modes with diagnoses and fixes, plus dependency-conflict resolution and a do/don't checklist.

## Dependency Conflict Resolution

### Diagnosing Conflicts

**Symptom**: `pip install` fails with a version-conflict message.

```bash
# What's currently installed
pip list

# Specific package
pip show package-name

# Full dependency tree
pip install pipdeptree
pipdeptree

# Find conflicts in the tree
pipdeptree --warn fail
```

### Common Conflict Patterns

#### Pattern 1: Direct Version Conflict

```
ERROR: package-a 1.0 requires lib>=2.0, but you have lib 1.5
```

**Fix**: upgrade or downgrade one package.

```bash
pip install "lib>=2.0"
# OR
pip install "package-a==0.9"   # Older package with lower lib requirement
```

#### Pattern 2: Transitive Dependency Conflict

```
package-a requires lib>=2.0
package-b requires lib<2.0
```

Two of your direct deps disagree about a shared transitive. Three fixes:

1. **Find compatible versions** — usually possible if you go back far enough:
   ```bash
   pip install "package-a==X.Y" "package-b==A.B"
   ```

2. **Use separate environments** (see `SETUP.md` "Multiple Environments"):
   ```bash
   python -m venv .venv-a
   python -m venv .venv-b
   ```

3. **Find an alternative package** — sometimes the cleanest fix.

### Resolution Workflow

When you've inherited a broken environment:

```bash
# 1. Start fresh
deactivate
rm -rf .venv
python -m venv .venv
source .venv/bin/activate

# 2. Install one package at a time to find the culprit
pip install package-a
pip install package-b
# ... continue, observing which install introduces the conflict

# 3. Check available versions of the conflicting package
pip index versions package-name

# 4. Try compatible versions
pip install "package-a>=1.0,<2.0" "package-b>=2.0"
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

### Issue 1: "Command not found" after activation

**Symptom**: `python` or `pip` not found after activating the venv.

**Cause**: environment not properly activated, or its files are corrupted.

**Fix**:
```bash
which python                # Should show .venv/bin/python
# If not, or path is wrong:
deactivate
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
```

### Issue 2: Wrong Python version in venv

**Symptom**: `python --version` shows a different version than expected.

**Cause**: venv was created with the wrong interpreter.

**Fix**:
```bash
rm -rf .venv
python3.11 -m venv .venv    # Or whatever version you want
source .venv/bin/activate
python --version            # Verify
```

If you use pyenv, run `pyenv local 3.11.5` before creating the venv so the right interpreter is in `PATH`.

### Issue 3: "No module named pip"

**Symptom**: `pip` is not available in a freshly-created venv.

**Cause**: venv was created with `--without-pip`, or the system Python's `ensurepip` is broken.

**Fix**:
```bash
# Try recreating with explicit upgrade
rm -rf .venv
python3 -m venv .venv --upgrade-deps

# Or bootstrap pip manually
python -m ensurepip --upgrade
```

### Issue 4: Permission denied on install

**Symptom**: `pip install` fails with a permission error.

**Cause**: pip is installing to system Python, not the venv (because the venv isn't activated).

**Fix**:
```bash
which pip                   # Should show .venv/bin/pip
# If it shows /usr/bin/pip or similar:
source .venv/bin/activate
# Try again

# NEVER use sudo with pip in a venv
```

### Issue 5: SSL certificate errors

**Symptom**: `pip install` fails with SSL errors.

**Fix**:
```bash
# Upgrade certifi first
pip install --upgrade certifi

# If that's not possible (e.g., behind a corporate proxy), use trusted-host as a
# temporary workaround — NOT for long-term use
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org package-name
```

For corporate environments, configure pip's index in `~/.pip/pip.conf`:

```ini
[global]
index-url = https://your-internal-pypi.corp/simple/
trusted-host = your-internal-pypi.corp
```

### Issue 6: Packages installed but not importable

**Symptom**: `ModuleNotFoundError` despite `pip list` showing the package.

**Causes and fixes**:

1. **Wrong environment active**:
   ```bash
   which python    # Verify path
   pip list        # Verify package is listed in THIS env
   ```

2. **Package name differs from import name**:
   ```bash
   pip install python-dotenv    # Package name
   ```
   ```python
   import dotenv                # Import name (different!)
   ```
   Check the package's docs for the correct import name.

3. **Editable install needed for in-repo code**:
   ```bash
   pip install -e .             # Install current project as editable
   ```

### Issue 7: Slow `pip install`

**Symptom**: `pip install` takes minutes per package.

**Causes**:
- Slow PyPI mirror.
- pip resolving deeply nested transitive deps.
- Building from source for packages without wheels.

**Fixes**:
```bash
# Use a faster mirror
pip install --index-url https://pypi.org/simple/ package-name

# Use uv (much faster pip replacement)
pip install uv
uv pip install -r requirements.txt   # 10-100x faster

# Cache wheels for faster re-installs
pip install --cache-dir ~/.cache/pip package-name
```

## Best Practices Summary

**Do** ✅:
- Use one venv per project.
- Pin production dependencies in `requirements.txt`.
- Include `requirements-dev.txt` (or `[dev]` extras in `pyproject.toml`) for dev tools.
- Use `.env` for secrets, gitignored.
- Provide `.env.example` template.
- Document the required Python version (`.python-version` or `requires-python`).
- Automate setup with a script, Makefile, or `pyproject.toml`.

**Don't** ❌:
- Commit `.venv/` to git.
- Use `sudo` with pip.
- Mix system and venv packages.
- Install in system Python.
- Commit secrets in `.env`.
- Share a single venv across multiple projects.

## See Also

- `SKILL.md` — entry point and quick reference.
- `SETUP.md` — how to set up venvs and requirements files properly.
- `configuration-management` skill — for hierarchical config and profile-based environments beyond simple `.env`.
