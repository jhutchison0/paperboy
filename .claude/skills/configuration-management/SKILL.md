---
name: configuration-management
description: Hierarchical YAML configuration systems with profiles, secrets management, environment-based overrides, schema validation, and testing. Use when setting up config systems, managing secrets, switching environments, refactoring hardcoded values, or auditing configuration architecture.
version: "2.0.0"
---

# Configuration Management

> **Paperboy users**: Read [PAPERBOY-NOTES.md](PAPERBOY-NOTES.md) first. Several sections of this skill (profiles, `ConfigLoader` class, `${ENV_VAR}` substitution, multi-environment YAML layout) do **not** apply to paperboy and should not be adopted without explicit user approval.

Externalize application behavior into structured, version-controlled files that can be changed without code modifications. This SKILL.md is the entry point; deep procedural content lives in sidecar files loaded on demand.

**Philosophy**: *"Configuration is code. Version it, test it, document it, and never commit secrets."*

## When to Use

- Setting up a configuration system for a new project
- Managing secrets without committing them
- Adding profile-based environments (dev / test / staging / production)
- Refactoring hardcoded values out of code
- Auditing an existing config system for security or maintainability issues
- Designing config validation that catches misconfiguration at startup

## Core Principles

Four rules that govern everything else in this skill:

1. **Hierarchical, layered, last-wins.** Defaults at the base, environment overrides on top, secrets last via environment variables.
2. **Secrets never in config files.** `.env` (gitignored) for secrets; `.env.example` (committed) as the template. No exceptions.
3. **Validate at startup.** A config error at app launch is recoverable; a config error in production at 3am is not. See `VALIDATION.md`.
4. **Test configs like code.** Override-able for tests; loading and merging behavior covered by tests; secrets never logged.

## Quick Reference

### Priority Order (last wins)

```
1. default.yaml          (system-wide defaults)
2. components/*.yaml     (component-specific settings)
3. profiles/{mode}.yaml  (environment overrides)
4. Environment variables (secrets and local overrides)
5. Programmatic overrides (testing only)
```

### Common Operations

| Task | Pattern |
|---|---|
| Load config | `config = ConfigLoader.load(profile='development')` |
| Override for testing | `config = ConfigLoader.load(overrides={'debug': True})` |
| Access nested value | `value = config['component']['subsystem']['setting']` |
| Set profile via env var | `export PROJECT_CONFIG_PROFILE=production` |
| Validate against schema | See `VALIDATION.md` |

### Environment Variable Syntax in YAML

- `${VAR}` — required (error if not set)
- `${VAR:default}` — optional, defaults to literal value
- `${VAR:}` — optional, defaults to empty string

## Sidecar Files

Loaded on demand when this SKILL.md cites them.

- [STRUCTURE-AND-FILES.md](STRUCTURE-AND-FILES.md) — directory layout, what gets committed vs ignored, the four file types (default, component, profile, .env) with worked examples.
- [LOADER.md](LOADER.md) — Python `ConfigLoader` implementation, deep-merge logic, env-var expansion, usage examples.
- [SECRETS.md](SECRETS.md) — `.env` management, `.gitignore` patterns, secret rotation workflow, production secret stores.
- [VALIDATION.md](VALIDATION.md) — Pydantic schemas, runtime validation, the configuration audit checklist.
- [TESTING-AND-PATTERNS.md](TESTING-AND-PATTERNS.md) — testing the loader and overrides; common patterns (feature flags, environment detection, graceful degradation, YAML anchors); troubleshooting.

## Quick Anti-Pattern Reference

- **Hardcoded secrets in YAML.** Always `${API_KEY}` from environment.
- **Logging the whole config dict.** Secrets leak. See `SECRETS.md` for sanitization.
- **One giant `config.yaml`.** Split by component; merge hierarchically. See `STRUCTURE-AND-FILES.md`.
- **Production debug endpoints.** Profile-gate them: false in `default.yaml`, false in `profiles/production.yaml`, never overridden.
- **Auto-migrate in production.** `database.migrations.auto_migrate` must be `false` in production. Surprising data loss when this is wrong.

## References

- [12-Factor App: Config](https://12factor.net/config) — the foundational pattern this skill implements.
- [Pydantic](https://docs.pydantic.dev/) — schema validation, used in `VALIDATION.md`.
- [python-dotenv](https://github.com/theskumar/python-dotenv) — `.env` file loading, used in `LOADER.md`.
- [YAML Specification](https://yaml.org/spec/) — YAML reference (including anchors used in `TESTING-AND-PATTERNS.md`).

---

**Maintained by**: Configuration Management Skill
**Version**: 2.0.0 — restructured to directory form with sidecar progressive disclosure (2026-05-19)
**Previous version**: 1.0.0 single-file at `.claude/skills/configuration-management.md`, replaced by this directory.
