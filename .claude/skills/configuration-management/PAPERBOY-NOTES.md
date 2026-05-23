# Paperboy-Specific Notes for the configuration-management Skill

This skill was adopted verbatim from upstream `utils` on 2026-05-22. It documents a general-purpose hierarchical configuration system (profiles, validators, layered YAML, `ConfigLoader` class with `${ENV_VAR}` substitution).

**Paperboy does not have or want that full apparatus.** Paperboy uses a single flat YAML file plus a hand-rolled loader. When this skill is invoked in paperboy, treat its sections selectively per the table below.

## Section-by-Section Applicability

| Skill section | Paperboy applicability | Notes |
|---|---|---|
| `SKILL.md` — Core Principles (4 rules) | **Applies** | Hierarchy-of-defaults, no secrets in YAML, validate-at-startup, test-configs-like-code are all good practice paperboy honors. |
| `STRUCTURE-AND-FILES.md` — multi-file `config/` layout, `profiles/` directory | **Does NOT apply** | Paperboy has a single `config/paperboy.yaml` plus `config/project.yaml`. No profiles. No environment-specific files. Do not add `config/profiles/{dev,test,staging,production}.yaml` — that would contradict Simplicity First and the existing `PipelineConfig.from_yaml()` design. |
| `LOADER.md` — `ConfigLoader` class with deep-merge, `${ENV_VAR}` substitution, layered overrides | **Does NOT apply** | Paperboy reads YAML directly into `PipelineConfig` (see [src/config.py](../../../src/config.py)). No deep-merge. No env-var substitution in YAML. Environment overrides happen via `.env` for secrets only. **Do not introduce a ConfigLoader class** without explicit user approval — it would violate the Config-Driven pillar's "Python reads YAML directly" stance. |
| `SECRETS.md` — `.env` (gitignored), `.env.example` (committed), never log secrets | **Applies** | Paperboy follows this exact pattern. `ANTHROPIC_API_KEY` is the only secret today. `.env.example` placeholder detection exists in `PipelineConfig.validate()` (see `358521` commit). |
| `VALIDATION.md` — startup validation, schema checks, clear error messages | **Applies (in spirit)** | Paperboy's `PipelineConfig.validate()` returns `(errors, warnings)` tuples. CLI surfaces them before any pipeline stage runs. The skill's broader schema-validation patterns (jsonschema / pydantic) are NOT in use and should not be added without user approval. |
| `TESTING-AND-PATTERNS.md` — fixtures for test configs, override patterns | **Partially applies** | Paperboy uses `tests/test_config*.py` with literal YAML strings and `tmp_path` fixtures. The skill's broader override-pattern examples are aspirational here. |

## When to Invoke This Skill

**Good fits**:
- Auditing secret-handling (does anything new log `ANTHROPIC_API_KEY`?)
- Strengthening startup validation messages
- Adding test coverage for a new config field

**Bad fits**:
- "We need profiles for dev/staging/production" — no. Paperboy is a personal-use research pipeline. One config file.
- "Let's add a `ConfigLoader` class with deep-merge" — no. `PipelineConfig.from_yaml()` is the existing pattern.
- "Add `${VAR}` substitution to `paperboy.yaml`" — no. Use `.env` for secrets, hardcode tunables in YAML.

## If You Disagree

If the structure in `STRUCTURE-AND-FILES.md` or `LOADER.md` genuinely fits a future paperboy need (multi-user deployment, hosted service, etc.), open a discussion with the user before adopting. Write an ADR if the decision passes the triple filter. Do not silently expand the config system because the upstream skill prescribes it.
