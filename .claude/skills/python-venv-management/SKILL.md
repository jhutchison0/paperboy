---
name: python-venv-management
description: Creating, managing, and troubleshooting Python virtual environments. Use when setting up isolated Python environments, resolving dependency conflicts, managing multiple project environments, automating setup with scripts or Makefiles, or migrating from system Python to per-project venvs.
version: "2.0.0"
---

# Python Virtual Environment Management

Isolate Python dependencies per project, prevent conflicts between projects requiring different package versions. This SKILL.md is the entry point; deep procedural content lives in two sidecar files loaded on demand.

**Philosophy**: *"One project, one environment. Isolate dependencies, document requirements, automate setup."*

## When to Use

- Setting up a new Python project (always)
- Resolving a `pip install` conflict between two packages
- Managing multiple environments for the same project (Python version matrix, optional heavy deps)
- Writing or auditing a project's setup script / Makefile
- Migrating an existing codebase off system Python
- Diagnosing "module not found" or "wrong Python version" errors

## Core Principles

1. **One venv per project.** Default; deviate only with a documented reason.
2. **Activate inside the venv.** All `pip` and `python` commands run inside the activated venv. Never use `sudo pip`.
3. **Pin production dependencies.** Reproducible builds beat flexibility-at-deploy-time.
4. **Never commit secrets or the venv directory.** `.venv/` and `.env` both belong in `.gitignore`.

## Quick Reference

### Essential Commands

| Task | Command |
|---|---|
| Create venv | `python -m venv .venv` |
| Activate (Linux/Mac) | `source .venv/bin/activate` |
| Activate (Windows) | `.venv\Scripts\activate` |
| Deactivate | `deactivate` |
| Install deps | `pip install -r requirements.txt` |
| Install project (editable) | `pip install -e .` |
| Install with dev deps | `pip install -e ".[dev]"` |
| Freeze deps to file | `pip freeze > requirements.txt` |
| Upgrade pip | `pip install --upgrade pip` |
| List packages | `pip list` |
| Show package info | `pip show <package>` |
| Check what's installed | `which python` (should show `.venv/bin/python`) |

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

- [SETUP.md](SETUP.md) — single-vs-multiple environments, setup patterns (bash script, Makefile, pyproject.toml), requirements file organization, pinning strategy, Python version management (pyenv).
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — dependency conflict resolution, environment variables and secrets, the seven most common venv failure modes with diagnoses and fixes, do/don't checklist.

## Quick Anti-Pattern Reference

- **`sudo pip install`** — never. Indicates you're installing to system Python, not your venv.
- **Committing `.venv/`** — adds gigabytes of OS-specific binaries to git.
- **`pip freeze > requirements.txt` as your only spec** — captures transitive deps and platform quirks; combine with hand-curated direct deps in `pyproject.toml`.
- **Sharing a venv across projects** — defeats the isolation that's the entire point.
- **Mixing system Python and venv** — `which python` should always point at your `.venv/bin/python` when activated.

## References

- [Python venv documentation](https://docs.python.org/3/library/venv.html)
- [pip documentation](https://pip.pypa.io/)
- [pyproject.toml specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
- [pyenv](https://github.com/pyenv/pyenv) — Python version management (see `SETUP.md`)
- [pipx](https://pipx.pypa.io/) — install CLI tools in isolation
- [pip-tools](https://github.com/jazzband/pip-tools) — pinned requirements from loose specs

---

**Maintained by**: Python Venv Management Skill
**Version**: 2.0.0 — restructured to directory form with sidecar progressive disclosure (2026-05-19)
**Previous version**: 1.0.0 single-file at `.claude/skills/python-venv-management.md`, replaced by this directory.
