# LOADER — Python ConfigLoader Implementation

Sidecar to `SKILL.md`. The Python class that loads, merges, and expands the four file types from `STRUCTURE-AND-FILES.md`. Drop into `src/core/config.py` (or equivalent) and adapt the import paths.

## Implementation

`src/core/config.py`:

```python
"""
Configuration loader with hierarchical YAML support.

Loads configuration in priority order (last wins):
  1. default.yaml
  2. components/*.yaml
  3. profiles/{profile}.yaml
  4. Environment variables (via ${VAR} or ${VAR:default} expansion)
  5. Programmatic overrides (testing only)
"""

import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Load and merge hierarchical YAML configurations."""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self._config: Dict[str, Any] = {}

    @classmethod
    def load(
        cls,
        config_dir: str = "config",
        profile: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Load configuration with hierarchical merging.

        Args:
            config_dir: Path to configuration directory.
            profile: Profile name (development, testing, production).
            overrides: Dict of override values (use sparingly; testing only).

        Returns:
            Merged configuration dictionary.

        Example:
            >>> config = ConfigLoader.load(profile='development')
            >>> db_host = config['database']['host']
        """
        loader = cls(config_dir)
        loader._load_default()
        loader._load_components()
        if profile:
            loader._load_profile(profile)
        loader._apply_env_vars()
        if overrides:
            loader._deep_merge(loader._config, overrides)
        return loader._config

    def _load_default(self):
        """Load default.yaml configuration."""
        default_path = self.config_dir / "default.yaml"
        if default_path.exists():
            logger.info(f"Loading default config: {default_path}")
            with open(default_path) as f:
                default_config = yaml.safe_load(f)
                if default_config:
                    self._config = default_config
        else:
            logger.warning(f"Default config not found: {default_path}")

    def _load_components(self):
        """Load all component configurations from components/."""
        components_dir = self.config_dir / "components"
        if not components_dir.exists():
            logger.warning(f"Components directory not found: {components_dir}")
            return

        for yaml_file in sorted(components_dir.glob("*.yaml")):
            logger.info(f"Loading component config: {yaml_file.name}")
            with open(yaml_file) as f:
                component_config = yaml.safe_load(f)
                if component_config:
                    self._deep_merge(self._config, component_config)

    def _load_profile(self, profile: str):
        """Load profile configuration."""
        profile_path = self.config_dir / "profiles" / f"{profile}.yaml"
        if profile_path.exists():
            logger.info(f"Loading profile config: {profile}")
            with open(profile_path) as f:
                profile_config = yaml.safe_load(f)
                if profile_config:
                    self._deep_merge(self._config, profile_config)
        else:
            logger.warning(f"Profile config not found: {profile_path}")

    def _apply_env_vars(self):
        """Apply environment variable substitution recursively."""
        self._config = self._substitute_env_vars(self._config)

    def _substitute_env_vars(self, obj: Any) -> Any:
        """Recursively substitute ${VAR} and ${VAR:default} in strings."""
        if isinstance(obj, dict):
            return {k: self._substitute_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_env_vars(item) for item in obj]
        elif isinstance(obj, str):
            return self._expand_env_var(obj)
        else:
            return obj

    def _expand_env_var(self, value: str) -> Any:
        """
        Expand env vars in a string.

        Supports:
          - ${VAR} — required; raises ValueError if not set
          - ${VAR:default} — optional with default literal
        """
        pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'

        def replacer(match):
            var_name = match.group(1)
            default_value = match.group(2)
            env_value = os.environ.get(var_name)
            if env_value is not None:
                return env_value
            elif default_value is not None:
                return default_value
            else:
                raise ValueError(
                    f"Required environment variable not set: {var_name}"
                )

        result = re.sub(pattern, replacer, value)
        return self._convert_type(result)

    def _convert_type(self, value: str) -> Any:
        """Convert string to int / float / bool when unambiguous."""
        if value.lower() in ('true', 'yes', 'on'):
            return True
        if value.lower() in ('false', 'no', 'off'):
            return False
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass
        return value

    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """
        Recursively merge `update` into `base` (base modified in place).

        Deep merge is essential for hierarchical configs — nested dicts
        merge recursively rather than being replaced wholesale.
        """
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
        return base


def load_config(profile: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience: load config with profile from env var if not supplied.

    Args:
        profile: Config profile. If None, reads PROJECT_CONFIG_PROFILE env var
                 or defaults to 'development'.
    """
    if profile is None:
        profile = os.environ.get('PROJECT_CONFIG_PROFILE', 'development')
    return ConfigLoader.load(profile=profile)
```

## Usage Examples

### Basic

```python
from core.config import load_config

config = load_config()

db_host = config['database']['host']
db_port = config['database']['port']
log_level = config['logging']['level']

if config['features']['enable_caching']:
    cache = setup_cache(config['cache'])
```

### Profile-Based

```python
dev_config = load_config(profile='development')
prod_config = load_config(profile='production')

# Or via env var:
#   export PROJECT_CONFIG_PROFILE=staging
config = load_config()  # Loads staging profile
```

### Testing with Overrides

```python
import pytest
from core.config import ConfigLoader


@pytest.fixture
def test_config():
    return ConfigLoader.load(
        profile='testing',
        overrides={
            'database': {
                'name': 'test_db_12345',
                'pool': {'max_connections': 1},
            },
            'api_client': {
                'base_url': 'http://mock-api:8080',
            },
        },
    )


def test_database_connection(test_config):
    db = Database(test_config['database'])
    assert db.connect()
```

### Component Initialization

```python
class DatabaseManager:
    def __init__(self, config: Dict[str, Any]):
        self.host = config['host']
        self.port = config['port']
        self.database = config['name']
        self.user = config['user']
        self.password = config['password']

        pool_config = config['pool']
        self.min_connections = pool_config['min_connections']
        self.max_connections = pool_config['max_connections']

        self._pool = None

    def connect(self):
        self._pool = create_pool(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password,
            min_size=self.min_connections,
            max_size=self.max_connections,
        )


# Usage
config = load_config()
db = DatabaseManager(config['database'])
db.connect()
```

## Implementation Notes

- **Sort component files.** `sorted(components_dir.glob("*.yaml"))` makes load order deterministic, which matters when two component files set the same key.
- **Type conversion is best-effort.** `_convert_type` tries bool → int → float → str. Strings like `"1e10"` will become floats. Use schema validation (see `VALIDATION.md`) if you need stricter typing.
- **`_deep_merge` mutates `base`.** This is intentional for performance; if you need to preserve the base, deep-copy it first.
- **Lists are replaced, not merged.** If `default.yaml` has `endpoints: [a, b]` and `profile.yaml` has `endpoints: [c]`, the result is `[c]`, not `[a, b, c]`. This matches most users' intuition but is worth flagging.

## See Also

- `STRUCTURE-AND-FILES.md` — the files this loader reads.
- `SECRETS.md` — how `${VAR}` values come from `.env` and what to do with them.
- `VALIDATION.md` — wrap the loader output in a Pydantic schema for type safety.
- `TESTING-AND-PATTERNS.md` — testing the loader itself.
