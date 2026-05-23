# TESTING-AND-PATTERNS — Testing, Common Patterns, Troubleshooting

Sidecar to `SKILL.md`. Three sections combined for readability: testing the config loader, common config-driven patterns (feature flags, environment detection, graceful degradation, YAML inheritance), and the standard troubleshooting issues.

## Testing the Config Loader

### Pytest Fixtures

`conftest.py`:

```python
import pytest

from core.config import ConfigLoader


@pytest.fixture
def test_config():
    """Base test configuration."""
    return ConfigLoader.load(profile='testing')


@pytest.fixture
def isolated_config(request):
    """Test configuration with unique DB name per test."""
    return ConfigLoader.load(
        profile='testing',
        overrides={
            'database': {
                'name': f'test_db_{request.node.name}',
            },
        },
    )


@pytest.fixture
def mock_api_config(test_config):
    """Test config with API pointed at the mock server."""
    test_config['api_client']['base_url'] = 'http://mock-api:8080'
    return test_config
```

### Tests for the Loader

```python
import os

import pytest

from core.config import ConfigLoader


def test_config_loading():
    """Basic load with profile."""
    config = ConfigLoader.load(profile='testing')
    assert config['system']['mode'] == 'testing'
    assert 'database' in config
    assert 'logging' in config


def test_config_merging():
    """Hierarchical merging — default + profile."""
    config = ConfigLoader.load(profile='development')
    assert config['logging']['backup_count'] == 5      # Default
    assert config['logging']['level'] == 'DEBUG'       # Profile override


def test_env_var_substitution():
    """${VAR} expansion."""
    os.environ['TEST_DB_HOST'] = 'test.example.com'

    config_data = {'database': {'host': '${TEST_DB_HOST}'}}
    loader = ConfigLoader()
    result = loader._substitute_env_vars(config_data)

    assert result['database']['host'] == 'test.example.com'


def test_required_env_var_missing():
    """Required ${VAR} without value raises."""
    os.environ.pop('MISSING_VAR', None)

    config_data = {'setting': '${MISSING_VAR}'}
    loader = ConfigLoader()

    with pytest.raises(ValueError, match="Required environment variable not set"):
        loader._substitute_env_vars(config_data)


def test_env_var_with_default():
    """${VAR:default} returns default when unset."""
    os.environ.pop('UNSET_VAR', None)

    config_data = {'setting': '${UNSET_VAR:fallback}'}
    loader = ConfigLoader()
    result = loader._substitute_env_vars(config_data)

    assert result['setting'] == 'fallback'


def test_config_overrides():
    """Programmatic overrides win."""
    config = ConfigLoader.load(
        profile='testing',
        overrides={'database': {'name': 'custom_test_db'}},
    )
    assert config['database']['name'] == 'custom_test_db'


def test_deep_merge_preserves_unrelated_keys():
    """Override of one nested key doesn't wipe sibling keys."""
    config = ConfigLoader.load(
        profile='testing',
        overrides={'database': {'name': 'override'}},
    )
    # Override changed name, but pool settings from base survive
    assert 'pool' in config['database']
```

## Common Patterns

### Pattern 1: Feature Flags

```yaml
features:
  new_algorithm: false
  legacy_api: true
  beta_feature: false
```

```python
if config['features']['new_algorithm']:
    result = new_algorithm(data)
else:
    result = legacy_algorithm(data)
```

Flags should be **explicit**: `enable_X`, `legacy_Y`, `beta_Z`. Never `flag1: true`. The name should tell you what flipping it does.

### Pattern 2: Environment Detection

```python
def is_development() -> bool:
    return config['system']['mode'] == 'development'

def is_production() -> bool:
    return config['system']['mode'] == 'production'

# Usage
if is_development():
    app.debug = True
```

Helpers like these centralize the convention. Resist sprinkling `config['system']['mode'] == 'production'` all over the codebase.

### Pattern 3: Graceful Degradation

```yaml
cache:
  backend: "redis"
  redis:
    host: "${REDIS_HOST:localhost}"
  fallback_to_memory: true
```

```python
try:
    cache = RedisCache(config['cache']['redis'])
except ConnectionError:
    if config['cache']['fallback_to_memory']:
        logger.warning("Redis unavailable, using memory cache")
        cache = MemoryCache()
    else:
        raise
```

Config tells the code *whether* fallback is acceptable. The code decides *how*.

### Pattern 4: YAML Anchors for Config Inheritance

`config/base/common.yaml`:

```yaml
api_defaults: &api_defaults
  timeout_seconds: 30
  retry_attempts: 3
  headers:
    User-Agent: "MyApp/1.0"

services:
  user_api:
    <<: *api_defaults                    # Inherit defaults
    base_url: "https://users.example.com"

  data_api:
    <<: *api_defaults
    base_url: "https://data.example.com"
    timeout_seconds: 60                  # Override one field
```

`&name` defines an anchor; `*name` references it; `<<:` merges the referenced map into the current one with explicit overrides.

Use anchors for **repeated structural defaults** across siblings. Don't use them to reduce typing in unrelated places — they make YAML harder to grep.

## Troubleshooting

### Environment variable not substituted

**Symptom**: config contains literal `${VAR}` string.

**Cause**: env var not set, no default provided.

**Fix**:

```bash
echo $VAR                         # Verify
export VAR=value                  # Set
```

Or provide a default in YAML: `${VAR:default_value}`.

### Configuration not loading

**Symptom**: `FileNotFoundError` or empty config.

**Cause**: wrong `config_dir` path.

**Fix**:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
config = load_config()
# Logger prints each file it tries to load
```

### Profile not applied

**Symptom**: profile settings don't override defaults.

**Cause**: profile name wrong or file missing.

**Fix**:

```bash
ls config/profiles/
cat config/profiles/development.yaml
export PROJECT_CONFIG_PROFILE=development
python -c "from core.config import load_config; print(load_config()['system']['mode'])"
```

### Secrets exposed in logs

**Symptom**: API keys or passwords visible in log files.

**Cause**: logging the config object directly.

**Fix**: see `SECRETS.md` sanitization. Short version:

```python
# Bad
logger.debug(f"Config: {config}")

# Good
logger.debug(f"Config: {sanitize_config(config)}")
```

### Type confusion from env vars

**Symptom**: `config['port']` is the string `"5432"` instead of int `5432`.

**Cause**: `${VAR}` always produces a string from env; only `_convert_type` tries to coerce it.

**Fix**: use Pydantic schema (`VALIDATION.md`) to enforce types, or write `int(config['database']['port'])` at the call site.

## Migration: Hardcoded → Config

When refactoring an existing codebase, work in phases:

1. **Add the config system.** Create `config/default.yaml`, implement `ConfigLoader`, add `.env.example`.
2. **Migrate non-sensitive settings.** Move timeouts, limits, flags to YAML. Update code to read from config. Tests should still pass.
3. **Migrate secrets.** Move API keys, passwords to `.env`. Update code to read from config. Verify locally.
4. **Add profiles.** Create `profiles/development.yaml` and `profiles/production.yaml`. Test profile switching.
5. **Clean up.** Remove all hardcoded values. Add startup validation. Document each setting.

Don't try to do all five phases in one PR. Each phase is independently shippable.

## See Also

- `STRUCTURE-AND-FILES.md` — the files being tested.
- `LOADER.md` — the loader being tested.
- `SECRETS.md` — the sanitization pattern referenced in troubleshooting.
- `VALIDATION.md` — schema validation that complements the type-conversion troubleshooting note.
