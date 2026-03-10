---
name: python-venv-management
description: Creating, managing, and troubleshooting Python virtual environments
version: "1.0.0"
---

# Python Virtual Environment Management

**When to use**: Setting up isolated Python environments, resolving dependency conflicts, managing multiple project environments, or creating setup scripts.

---

## Overview

Virtual environments isolate Python dependencies per project, preventing conflicts between projects that require different package versions. This skill covers environment creation, dependency management, and troubleshooting common issues.

**Philosophy**: "One project, one environment. Isolate dependencies, document requirements, automate setup."

---

## Quick Reference

### Essential Commands

| Task | Command |
|------|---------|
| Create venv | `python -m venv .venv` |
| Activate (Linux/Mac) | `source .venv/bin/activate` |
| Activate (Windows) | `.venv\Scripts\activate` |
| Deactivate | `deactivate` |
| Install deps | `pip install -r requirements.txt` |
| Freeze deps | `pip freeze > requirements.txt` |
| Upgrade pip | `pip install --upgrade pip` |
| List packages | `pip list` |
| Show package info | `pip show <package>` |

### Directory Conventions

```
project/
├── .venv/                 # Virtual environment (gitignored)
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── requirements-test.txt  # Test dependencies (optional)
└── pyproject.toml        # Modern Python project config
```

---

## When to Use Multiple Environments

### Single Environment (Recommended Default)

Use one `.venv/` for most projects:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

**When single environment works**:
- Standard web/API projects
- CLI tools
- Most data science projects
- General Python development

### Multiple Environments

Create separate environments when:

1. **Conflicting dependencies**: Two tools need incompatible versions
2. **Isolated testing**: Testing against multiple Python versions
3. **Deployment simulation**: Matching production environment exactly
4. **Heavy optional deps**: ML libraries that aren't always needed

**Example: Separate environments**

```bash
# Main development environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# Simulation/ML environment (heavy deps)
python -m venv .venv-ml
source .venv-ml/bin/activate
pip install -r requirements-ml.txt
```

---

## Environment Setup Patterns

### Pattern 1: Basic Setup Script

**File**: `scripts/setup.sh`

```bash
#!/bin/bash
# Basic environment setup script

set -e  # Exit on error

echo "Setting up Python environment..."

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate environment
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install dev dependencies if they exist
if [ -f "requirements-dev.txt" ]; then
    echo "Installing development dependencies..."
    pip install -r requirements-dev.txt
fi

echo "Setup complete!"
echo "Activate with: source .venv/bin/activate"
```

### Pattern 2: Makefile Integration

**File**: `Makefile`

```makefile
.PHONY: venv install dev-install clean

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

venv:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

install: venv
	$(PIP) install -r requirements.txt

dev-install: install
	$(PIP) install -r requirements-dev.txt

clean:
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
```

**Usage**:

```bash
make dev-install    # Full development setup
make clean          # Remove environment and caches
```

### Pattern 3: pyproject.toml (Modern Approach)

**File**: `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my-project"
version = "1.0.0"
description = "Project description"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}

dependencies = [
    "requests>=2.28.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "black>=23.0",
    "ruff>=0.1.0",
    "mypy>=1.0",
]
test = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
]

[project.scripts]
my-cli = "my_project.cli:main"
```

**Usage with pyproject.toml**:

```bash
# Create and activate venv
python -m venv .venv
source .venv/bin/activate

# Install project with dependencies
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"

# Install with test dependencies
pip install -e ".[test]"
```

---

## Requirements File Organization

### Standard Structure

```
project/
├── requirements.txt          # Production only (minimal)
├── requirements-dev.txt      # Development tools
└── requirements-test.txt     # Test dependencies (optional)
```

### requirements.txt (Production)

```
# Core dependencies - pinned for reproducibility
requests==2.31.0
pyyaml==6.0.1
python-dotenv==1.0.0

# With version ranges (more flexible)
requests>=2.28.0,<3.0.0
pyyaml>=6.0
```

### requirements-dev.txt

```
# Include production deps
-r requirements.txt

# Development tools
pytest>=7.0.0
pytest-cov>=4.0.0
black>=23.0.0
ruff>=0.1.0
mypy>=1.0.0
pre-commit>=3.0.0

# Documentation
mkdocs>=1.5.0
mkdocs-material>=9.0.0
```

### Pinning Strategy

| Approach | When to Use |
|----------|-------------|
| Exact pins (`==2.31.0`) | Production, reproducible builds |
| Compatible (`~=2.31.0`) | Allow patch updates only |
| Minimum (`>=2.28.0`) | Development, flexibility needed |
| Range (`>=2.28.0,<3.0.0`) | Balance stability and updates |

**Generate exact pins from current environment**:

```bash
pip freeze > requirements-lock.txt
```

---

## Dependency Conflict Resolution

### Diagnosing Conflicts

**Symptom**: `pip install` fails with version conflict

```bash
# Check what's installed
pip list

# Check specific package
pip show package-name

# Check dependency tree
pip install pipdeptree
pipdeptree

# Find conflicts
pipdeptree --warn fail
```

### Common Conflict Patterns

**Pattern 1: Direct version conflict**

```
ERROR: package-a 1.0 requires lib>=2.0, but you have lib 1.5
```

**Solution**: Upgrade or downgrade one package

```bash
pip install lib>=2.0
# or
pip install package-a==0.9  # older version with lower requirement
```

**Pattern 2: Transitive dependency conflict**

```
package-a requires lib>=2.0
package-b requires lib<2.0
```

**Solutions**:

1. **Find compatible versions**:
   ```bash
   pip install package-a==X.Y package-b==A.B  # specific versions that work
   ```

2. **Use separate environments**:
   ```bash
   python -m venv .venv-a
   python -m venv .venv-b
   ```

3. **Find alternative packages**

### Resolution Workflow

```bash
# 1. Start fresh
deactivate
rm -rf .venv
python -m venv .venv
source .venv/bin/activate

# 2. Install one package at a time
pip install package-a
pip install package-b
# ... identify which causes conflict

# 3. Check for version that works
pip index versions package-name

# 4. Try compatible versions
pip install "package-a>=1.0,<2.0" "package-b>=2.0"
```

---

## Python Version Management

### Using pyenv (Recommended)

```bash
# Install pyenv (Linux/Mac)
curl https://pyenv.run | bash

# List available versions
pyenv install --list

# Install specific version
pyenv install 3.11.5

# Set local version for project
pyenv local 3.11.5

# Create venv with specific version
~/.pyenv/versions/3.11.5/bin/python -m venv .venv
```

### Using python version directly

```bash
# Use specific Python version
python3.11 -m venv .venv

# Or specify full path
/usr/bin/python3.10 -m venv .venv
```

### .python-version file

```bash
# Create .python-version for pyenv
echo "3.11.5" > .python-version
```

---

## Environment Variables and Secrets

### .env Pattern

**File**: `.env.example` (committed to git)

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

**File**: `.env` (gitignored)

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

# Load .env file
load_dotenv()

# Access variables
debug = os.getenv("DEBUG", "false").lower() == "true"
api_key = os.getenv("API_KEY")
```

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

---

## Troubleshooting

### Issue: "Command not found" after activation

**Symptom**: `python` or `pip` not found after activating venv

**Cause**: Environment not properly activated or corrupted

**Solution**:
```bash
# Check if activated (should show .venv path)
which python

# Recreate environment
deactivate
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
```

### Issue: Wrong Python version in venv

**Symptom**: venv uses wrong Python version

**Cause**: Created with wrong Python interpreter

**Solution**:
```bash
# Recreate with specific version
rm -rf .venv
python3.11 -m venv .venv
source .venv/bin/activate
python --version  # Verify
```

### Issue: "No module named pip"

**Symptom**: pip not available in new venv

**Cause**: venv created with `--without-pip` or system issue

**Solution**:
```bash
# Method 1: Recreate
rm -rf .venv
python3 -m venv .venv --upgrade-deps

# Method 2: Bootstrap pip
python -m ensurepip --upgrade
```

### Issue: Permission denied on install

**Symptom**: `pip install` fails with permission error

**Cause**: Installing to system Python, not venv

**Solution**:
```bash
# Verify venv is active
which pip  # Should show .venv/bin/pip

# If not in venv, activate first
source .venv/bin/activate

# Never use sudo with pip in venv
```

### Issue: SSL certificate errors

**Symptom**: `pip install` fails with SSL errors

**Solution**:
```bash
# Upgrade certifi
pip install --upgrade certifi

# Or use trusted host (temporary workaround)
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org package-name
```

### Issue: Packages installed but not importable

**Symptom**: `ModuleNotFoundError` despite package being installed

**Causes and solutions**:

1. **Wrong environment active**:
   ```bash
   which python  # Check path
   pip list      # Verify package listed
   ```

2. **Package name vs import name differ**:
   ```bash
   # Some packages have different names
   pip install python-dotenv  # Package name
   import dotenv              # Import name
   ```

3. **Editable install needed**:
   ```bash
   pip install -e .  # Install current project as editable
   ```

---

## Best Practices Summary

### DO:
- Use one venv per project
- Pin production dependencies
- Include requirements-dev.txt for dev tools
- Use .env for secrets (gitignored)
- Provide .env.example template
- Document Python version requirements
- Automate setup with scripts/Makefile

### DON'T:
- Commit .venv/ to git
- Use sudo with pip
- Mix system and venv packages
- Install in system Python
- Commit secrets in .env

---

## References

### Official Documentation
- [Python venv](https://docs.python.org/3/library/venv.html)
- [pip documentation](https://pip.pypa.io/)
- [pyproject.toml](https://packaging.python.org/en/latest/specifications/pyproject-toml/)

### Tools
- [pyenv](https://github.com/pyenv/pyenv) - Python version management
- [pipx](https://pipx.pypa.io/) - Install CLI tools in isolation
- [pipdeptree](https://github.com/tox-dev/pipdeptree) - Dependency tree visualization
- [pip-tools](https://github.com/jazzband/pip-tools) - Pin dependencies

---

**Maintained by**: Python Venv Management Skill
**Version**: 1.0.0
**Last Updated**: 2025-12-07
