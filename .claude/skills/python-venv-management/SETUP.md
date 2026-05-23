# SETUP — Single vs Multiple Environments, Setup Patterns, Requirements, Pinning, Python Versions

Sidecar to `SKILL.md`. The how-to for getting an environment from zero to ready.

## Single vs Multiple Environments

### Single Environment (Default)

Use one `.venv/` per project for most cases:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

**When this is right**:
- Standard web/API projects.
- CLI tools.
- Most data science projects.
- General Python development.

### Multiple Environments

Create separate environments when one of these applies:

1. **Conflicting dependencies.** Two tools in the project need incompatible versions of the same library.
2. **Isolated testing.** Testing against multiple Python versions (3.11, 3.12, 3.13).
3. **Deployment simulation.** Matching production environment exactly while keeping a faster dev environment.
4. **Heavy optional deps.** ML libraries (torch, tensorflow) that aren't needed for every workflow.

```bash
# Main development environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# Separate environment for heavy ML deps
python -m venv .venv-ml
source .venv-ml/bin/activate
pip install -r requirements-ml.txt
```

Naming convention: `.venv-{suffix}/` (matches the `.gitignore` glob `.venv-*/`).

## Setup Patterns

### Pattern 1: Bash Setup Script

`scripts/setup.sh`:

```bash
#!/bin/bash
# Basic environment setup script
set -e   # Exit on error

echo "Setting up Python environment..."

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Python version: $PYTHON_VERSION"

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing dependencies..."
pip install -r requirements.txt

if [ -f "requirements-dev.txt" ]; then
    echo "Installing development dependencies..."
    pip install -r requirements-dev.txt
fi

echo "Setup complete!"
echo "Activate with: source .venv/bin/activate"
```

Make it executable: `chmod +x scripts/setup.sh`.

### Pattern 2: Makefile

`Makefile`:

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

Usage:

```bash
make dev-install    # Full development setup
make clean          # Remove environment and caches
```

### Pattern 3: pyproject.toml (Modern, Preferred)

`pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my-project"
version = "1.0.0"
description = "Project description"
readme = "README.md"
requires-python = ">=3.11"
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

Usage:

```bash
python -m venv .venv
source .venv/bin/activate

pip install -e .                # Install project
pip install -e ".[dev]"         # Install with dev deps
pip install -e ".[test]"        # Install with test deps
pip install -e ".[dev,test]"    # Multiple extras
```

**When to use pyproject.toml over requirements files**:
- Building a distributable package.
- Using modern Python tooling (most cases since Python 3.11).
- Want optional dependency groups (`[dev]`, `[test]`, `[ml]`).
- Want `pip install -e .` for editable installs of the project itself.

`requirements.txt` and `pyproject.toml` can coexist — many projects keep `requirements.txt` for deployment lockfiles and `pyproject.toml` for development.

## Requirements File Organization

Standard structure:

```
project/
├── requirements.txt          # Production only (minimal)
├── requirements-dev.txt      # Development tools
└── requirements-test.txt     # Test dependencies (optional)
```

### `requirements.txt` (Production)

```
# Core dependencies — pinned for reproducibility
requests==2.31.0
pyyaml==6.0.1
python-dotenv==1.0.0

# Or with version ranges (more flexible, less reproducible)
requests>=2.28.0,<3.0.0
pyyaml>=6.0
```

### `requirements-dev.txt`

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

The `-r requirements.txt` line includes production deps transitively — so `pip install -r requirements-dev.txt` installs everything.

## Pinning Strategy

| Approach | Syntax | When to use |
|---|---|---|
| Exact pin | `requests==2.31.0` | Production, reproducible builds. |
| Compatible release | `requests~=2.31.0` | Allow patch updates, block minor/major. |
| Minimum version | `requests>=2.28.0` | Development, want flexibility. |
| Range | `requests>=2.28.0,<3.0.0` | Stability with bounded updates. |

### Generating Exact Pins from Current Environment

```bash
pip freeze > requirements-lock.txt
```

This captures **all** transitive dependencies at exact versions. Use it alongside (not instead of) your hand-curated `requirements.txt` — the freeze file is the lockfile.

Better still: use `pip-tools`:

```bash
pip install pip-tools
pip-compile requirements.in    # Produces requirements.txt with pinned transitives
pip-sync requirements.txt      # Installs exactly what's in the file (no more, no less)
```

## Python Version Management with pyenv

Recommended when you work on multiple projects with different Python versions, or test against a matrix.

```bash
# Install pyenv (Linux/Mac)
curl https://pyenv.run | bash

# List available versions
pyenv install --list

# Install a specific version
pyenv install 3.11.5

# Pin a project to a Python version
cd my-project
pyenv local 3.11.5            # Writes .python-version

# Create venv using that version
python -m venv .venv          # Uses pyenv-managed python
```

`.python-version` file:

```
3.11.5
```

Commit `.python-version` so contributors get the same Python.

### Without pyenv

Use the system's versioned binaries directly:

```bash
python3.11 -m venv .venv      # Use Python 3.11 specifically

# Or full path
/usr/bin/python3.11 -m venv .venv
```

This works fine for single-version projects.

## See Also

- `SKILL.md` — entry point and quick reference.
- `TROUBLESHOOTING.md` — what to do when this setup fails or produces unexpected behavior.
