# SETUP — Single vs Multiple Environments, Setup Patterns, Requirements, Pinning, Python Versions, Migration

Sidecar to `SKILL.md`. The how-to for getting an environment from zero to ready, with uv.

## Single vs Multiple Environments

### Single Environment (Default)

Use one `.venv/` per project for most cases:

```bash
uv venv --managed-python
uv pip install -r requirements.txt -r requirements-dev.txt
source .venv/bin/activate
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
uv venv --managed-python
uv pip install -r requirements.txt -r requirements-dev.txt

# Separate environment for heavy ML deps
uv venv .venv-ml --managed-python
VIRTUAL_ENV=.venv-ml uv pip install -r requirements-ml.txt
```

Naming convention: `.venv-{suffix}/` (matches the `.gitignore` glob `.venv-*/`). `uv pip` targets `.venv` by default; point it at an alternate env with the `VIRTUAL_ENV` variable or by activating that env first.

## Setup Patterns

### Pattern 1: Bash Setup Script

`scripts/setup.sh`:

```bash
#!/bin/bash
# Basic environment setup script
set -e   # Exit on error

echo "Setting up Python environment..."

if ! command -v uv >/dev/null 2>&1; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv --managed-python
fi

echo "Installing dependencies..."
uv pip install -r requirements.txt

if [ -f "requirements-dev.txt" ]; then
    echo "Installing development dependencies..."
    uv pip install -r requirements-dev.txt
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

venv:
	uv venv --managed-python

install: venv
	uv pip install -r requirements.txt

dev-install: install
	uv pip install -r requirements-dev.txt

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
uv venv --managed-python

uv pip install -e .                # Install project
uv pip install -e ".[dev]"         # Install with dev deps
uv pip install -e ".[test]"        # Install with test deps
uv pip install -e ".[dev,test]"    # Multiple extras
```

**When to use pyproject.toml over requirements files**:
- Building a distributable package.
- Using modern Python tooling (most cases since Python 3.11).
- Want optional dependency groups (`[dev]`, `[test]`, `[ml]`).
- Want `uv pip install -e .` for editable installs of the project itself.

`requirements.txt` and `pyproject.toml` can coexist: many projects keep `requirements.txt` for deployment lockfiles and `pyproject.toml` for development.

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

The `-r requirements.txt` line includes production deps transitively, so `uv pip install -r requirements-dev.txt` installs everything.

## Pinning Strategy

| Approach | Syntax | When to use |
|---|---|---|
| Exact pin | `requests==2.31.0` | Production, reproducible builds. |
| Compatible release | `requests~=2.31.0` | Allow patch updates, block minor/major. |
| Minimum version | `requests>=2.28.0` | Development, want flexibility. |
| Range | `requests>=2.28.0,<3.0.0` | Stability with bounded updates. |

### Generating Exact Pins from Current Environment

```bash
uv pip freeze > requirements-lock.txt
```

This captures **all** transitive dependencies at exact versions. Use it alongside (not instead of) your hand-curated `requirements.txt`: the freeze file is the lockfile.

Better still: compile pins from loose specs (uv's built-in replacement for pip-tools):

```bash
uv pip compile requirements.in -o requirements.txt   # Pin all transitives
uv pip sync requirements.txt                         # Install exactly what's listed (no more, no less)
```

## Python Version Management with uv

uv downloads and manages CPython builds itself. This replaces pyenv.

```bash
# List installed and available versions
uv python list

# Install a specific version
uv python install 3.12

# Create the venv on a managed interpreter (ignores system/pyenv pythons)
uv venv --managed-python --python 3.12
```

Without `--managed-python`, `uv venv` discovers interpreters on `PATH` first, which on a machine with pyenv or conda silently couples the venv to the incumbent. Always pass `--managed-python` (or set `UV_PYTHON_PREFERENCE=only-managed`).

**`.python-version` caution during migration**: uv reads `.python-version` to pick a default interpreter, but pyenv reads the same file and errors on version specs it doesn't have installed (for example a bare `3.12`). Do not commit a `.python-version` until every machine that clones the repo is off pyenv. Until then, pin the version in the venv-creation command instead.

## Migrating Off pyenv / conda / miniforge

The incumbent's interpreters are load-bearing until every venv built on them is rebuilt. Order matters:

1. **Install uv** (see `SKILL.md`).
2. **Map the blast radius** — find every venv built on the incumbent. Search by the
   `pyvenv.cfg` marker, never by directory name; venvs hide under alternate names
   (`.venv-ml/`, bare `venv/`) and outside the main projects directory:
   ```bash
   find ~/projects -maxdepth 4 -name pyvenv.cfg | while read c; do
     echo "$(dirname "$c"): $(grep ^home "$c")"
   done
   ```
3. **Freeze each old venv** as insurance, then **rebuild it** on a managed interpreter:
   ```bash
   .venv/bin/pip list --format=freeze > /tmp/<repo>.freeze.txt
   uv venv --clear --managed-python && uv pip install -e ".[dev]"
   ```
   `--clear` is safer than `rm -rf`: uv refuses to replace a directory that is not a venv.
4. **Parity-test each repo** (run its test suite; compare pass counts before and after). A shortfall means the old venv held something the repo's spec never listed — diff the freeze against `uv pip list`, close the gap, and file the spec fix in that repo.
5. **Only then remove the incumbent** (`pyenv`: delete `~/.pyenv` and its shell-rc init lines; conda: `conda init --reverse` then delete the install directory).

Removing the incumbent first bricks every venv built on it.

## See Also

- `SKILL.md` — entry point and quick reference.
- `TROUBLESHOOTING.md` — what to do when this setup fails or produces unexpected behavior.
