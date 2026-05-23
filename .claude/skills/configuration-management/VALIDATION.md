# VALIDATION — Schema Validation and Audit Checklist

Sidecar to `SKILL.md`. Catch misconfiguration at startup, not in production at 3am. Includes a Pydantic-based schema approach and a startup-validation function for when you don't want a schema dependency.

## Why Validate at Startup

A misconfigured app should fail loudly at startup, not silently at the first request that hits the broken setting. Startup validation is cheap (runs once) and high-value (turns 3am pages into immediate deploy-time failures).

The 12-Factor App principle: *"the app should fail to start in a misconfigured environment."*

## Schema-Based Validation (Pydantic)

For type-safe config with validation rules, define a Pydantic schema and validate after loading.

```python
from typing import Literal, Optional

from pydantic import BaseModel, Field, validator


class LoggingConfig(BaseModel):
    """Logging configuration schema."""
    level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = 'INFO'
    format: Literal['json', 'text'] = 'json'
    output: Literal['stdout', 'file', 'both'] = 'stdout'
    file_path: Optional[str] = 'logs/app.log'
    max_bytes: int = Field(default=10485760, gt=0)
    backup_count: int = Field(default=5, ge=0)


class DatabaseConfig(BaseModel):
    """Database configuration schema."""
    driver: str = 'postgresql'
    host: str
    port: int = Field(default=5432, gt=0, le=65535)
    name: str
    user: str
    password: str

    @validator('password')
    def password_not_empty(cls, v):
        if not v or v.strip() == '':
            raise ValueError('Database password cannot be empty')
        return v


class AppConfig(BaseModel):
    """Application configuration root schema."""
    system: dict
    logging: LoggingConfig
    database: DatabaseConfig
    features: dict


def load_validated_config(profile: Optional[str] = None) -> AppConfig:
    """
    Load and validate configuration.

    Raises:
        ValidationError: If configuration is invalid.

    Returns:
        Validated configuration object (typed).
    """
    raw_config = load_config(profile)  # See LOADER.md

    try:
        return AppConfig(**raw_config)
    except ValidationError as e:
        logger.error(f"Configuration validation failed: {e}")
        raise


# Usage
config = load_validated_config('production')
print(f"Log level: {config.logging.level}")
print(f"DB host: {config.database.host}")
```

**Benefits over dict access**:
- Type checking — `config.database.port` is an `int`, IDE knows it.
- Defaults — fields without values get the default.
- Validation — custom rules (port range, non-empty password) fire at startup.
- Documentation — the schema IS the config docs.

## Runtime Validation (No Schema Dependency)

When adding Pydantic isn't worth it, write an explicit validation function.

```python
def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration at startup.

    Raises:
        ValueError: If configuration is invalid (with all issues listed).

    Returns:
        True if valid.
    """
    errors = []

    # Required sections
    required_sections = ['system', 'logging', 'database']
    for section in required_sections:
        if section not in config:
            errors.append(f"Missing required section: {section}")

    # Database
    if 'database' in config:
        db = config['database']
        if not db.get('host'):
            errors.append("database.host is required")
        if not db.get('password'):
            errors.append("database.password is required (set DB_PASSWORD in .env)")

    # Production safety: debug endpoints must be off
    if config.get('system', {}).get('mode') == 'production':
        if config.get('features', {}).get('enable_debug_endpoints'):
            errors.append("Debug endpoints cannot be enabled in production")
        if config.get('database', {}).get('migrations', {}).get('auto_migrate'):
            errors.append("Auto-migrate cannot be enabled in production")

    # Security baseline
    if 'security' in config:
        sec = config['security']
        if sec.get('password_min_length', 0) < 8:
            errors.append("security.password_min_length must be at least 8")

    if errors:
        error_msg = (
            "Configuration validation failed:\n"
            + "\n".join(f"  - {e}" for e in errors)
        )
        raise ValueError(error_msg)

    return True


# Usage at app startup
config = load_config()
validate_config(config)
```

**Key design choices**:
- **Accumulate all errors, fail once.** Don't fail on the first issue — show the user every problem so they can fix all of them in one pass.
- **Production safety checks.** Settings that are dangerous in production (auto-migrate, debug endpoints) get explicit guards.
- **Reference the fix.** "Set `DB_PASSWORD` in .env" is more useful than "password missing."

## Configuration Audit Checklist

Run this checklist when auditing an existing config system or onboarding a new project.

### Structure
- [ ] Configuration files separated from code (in `config/`).
- [ ] Hierarchical structure: `default.yaml` → `components/` → `profiles/`.
- [ ] Clear directory organization, named consistently.
- [ ] Profile-based environments (at least dev + prod; typically dev/test/staging/prod).

### Secrets
- [ ] No secrets committed to git (grep the repo for known patterns).
- [ ] `.env` in `.gitignore` with the `!.env.example` exception.
- [ ] `.env.example` provided and current.
- [ ] All sensitive values via `${VAR}` in YAML, never hardcoded.
- [ ] Secrets meet a minimum strength (no `password123`, no defaults left in `.env`).

### Validation
- [ ] Configuration validated at app startup.
- [ ] Validation errors are clear and actionable (name the missing field, name the fix).
- [ ] Type checking for numeric values (port ranges, byte counts, timeouts).
- [ ] Required vs optional settings documented in `.env.example` or schema.
- [ ] Production-specific safety checks (no debug endpoints, no auto-migrate).

### Documentation
- [ ] Each component's settings have comments explaining purpose.
- [ ] README explains how to set up `.env` from `.env.example`.
- [ ] Examples for common operations (loading, overriding, switching profiles).
- [ ] Migration guide if config format has changed.

### Testing
- [ ] Test configurations separate from production (`config/profiles/testing.yaml`).
- [ ] Tests can override config with `overrides={...}`.
- [ ] Tests cover config loading, merging, and env-var expansion.
- [ ] Tests verify validation catches expected misconfigurations.

### Security
- [ ] Secrets never logged (see `SECRETS.md` sanitization).
- [ ] No hardcoded credentials anywhere in the codebase.
- [ ] Production config requires authentication.
- [ ] Debug endpoints disabled in production.
- [ ] Security settings (session timeout, max login attempts) reviewed against threat model.

## See Also

- `LOADER.md` — the loader whose output you're validating.
- `SECRETS.md` — the security side of validation (sanitization, store choice).
- `TESTING-AND-PATTERNS.md` — testing the validation logic itself.
