---
name: python-venv-management
description: Creating, managing, and troubleshooting Python virtual environments with uv. Use when setting up isolated Python environments, resolving dependency conflicts, managing multiple project environments, automating setup with scripts or Makefiles, or migrating off system Python, pyenv, or conda.
version: "3.0.0"
---

# Python Virtual Environment Management (uv)

Isolate Python dependencies per project, prevent conflicts between projects requiring different package versions. **uv** (Astral) is the engine for all of it: interpreters, environments, and packages. This SKILL.md is the entry point; deep procedural content lives in two sidecar files loaded on demand.

**Philosophy**: *"One project, one environment. Isolate dependencies, document requirements, automate setup."*

## When to Use

- Setting up a new Python project (always)
- Resolving a dependency conflict between two packages
- Managing multiple environments for the same project (Python version matrix, optional heavy deps)
- Writing or auditing a project's setup script / Makefile
- Migrating an existing codebase off system Python, pyenv, or conda/miniforge
- Diagnosing "module not found" or "wrong Python version" errors

## Core Principles

1. **One venv per project.** Default; deviate only with a documented reason.
2. **uv is the engine.** All environment and package operations go through `uv venv` and `uv pip`. Never `sudo pip`; never system pip.
3. **Managed interpreters.** `uv venv --managed-python` builds the venv on a uv-downloaded CPython. The venv then survives removal of pyenv, conda, or a system Python upgrade.
4. **Pin production dependencies.** Reproducible builds beat flexibility-at-deploy-time.
5. **Never commit secrets or the venv directory.** `.venv/` and `.env` both belong in `.gitignore`.

## Quick Reference

### Essential Commands

| Task | Command |
|---|---|
| Install uv | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Install an interpreter | `uv python install 3.12` |
| Create venv | `uv venv --managed-python` |
| Activate (Linux/Mac) | `source .venv/bin/activate` |
| Activate (Windows) | `.venv\Scripts\activate` |
| Deactivate | `deactivate` |
| Install deps | `uv pip install -r requirements.txt` |
| Install project (editable) | `uv pip install -e .` |
| Install with dev deps | `uv pip install -e ".[dev]"` |
| Freeze deps to file | `uv pip freeze > requirements.txt` |
| List packages | `uv pip list` |
| Show package info | `uv pip show <package>` |
| Check what's active | `which python` (should show `.venv/bin/python`) |

`uv pip` targets the project's `.venv` when run from the project root (or the activated venv if one is active). A uv venv does not bundle pip; `.venv/bin/pip` does not exist, and that is by design.

### Directory Conventions

```
project/
├── .venv/                  # Virtual environment (gitignored)
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── requirements-test.txt   # Test dependencies (optional)
└── pyproject.toml          # Modern Python project config (preferred)
```

### `.gitignore` Essentials

```gitignore
# Virtual environments
.venv/
venv/
ENV/
.venv-*/

# Environment files (secrets)
.env
.env.local
.env.*.local

# Keep templates
!.env.example
```

## Sidecar Files

Loaded on demand when this SKILL.md cites them.

- [SETUP.md](SETUP.md) — single-vs-multiple environments, setup patterns (bash script, Makefile, pyproject.toml), requirements file organization, pinning strategy, Python version management with `uv python`, migrating off pyenv/conda.
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — dependency conflict resolution, environment variables and secrets, the most common venv failure modes with diagnoses and fixes, do/don't checklist.

## Quick Anti-Pattern Reference

- **`sudo pip install`** — never. Indicates you're installing to system Python, not your venv.
- **Calling `.venv/bin/pip`** — it does not exist in a uv venv. Use `uv pip ...`. Seed pip only if a tool genuinely requires it (`uv venv --seed`).
- **Building the venv on an incumbent's interpreter** — a venv symlinked into `~/.pyenv/versions/` or a conda install breaks the day that incumbent is removed. Use `--managed-python`.
- **Committing `.venv/`** — adds gigabytes of OS-specific binaries to git.
- **`uv pip freeze > requirements.txt` as your only spec** — captures transitive deps and platform quirks; combine with hand-curated direct deps in `pyproject.toml`.
- **Sharing a venv across projects** — defeats the isolation that's the entire point.
- **Mixing system Python and venv** — `which python` should always point at your `.venv/bin/python` when activated.

## References

- [uv documentation](https://docs.astral.sh/uv/) — environments, `uv pip`, `uv python`, caching
- [Python venv documentation](https://docs.python.org/3/library/venv.html)
- [pyproject.toml specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
- Replaced by uv: pyenv (`uv python`), pipx (`uvx`), pip-tools (`uv pip compile` / `uv pip sync`)

---

**Maintained by**: Python Venv Management Skill
**Version**: 3.0.0 rebuilt on uv as the environment engine; pyenv/pip command surfaces replaced (2026-08-03)
**Previous versions**: 2.0.0 restructured to directory form with sidecar progressive disclosure (2026-05-19); 1.0.0 single-file at `.claude/skills/python-venv-management.md`.
