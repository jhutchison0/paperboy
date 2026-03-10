---
name: configuration-management
description: Hierarchical configuration systems with profiles, secrets management, and environment-based overrides
version: "1.0.0"
---

# Configuration Management

**When to use**: Setting up config systems, managing secrets, switching environments, refactoring hardcoded values, or auditing configuration architecture.

---

## Overview

Configuration management is the practice of externalizing application behavior into structured, version-controlled files that can be changed without code modifications. This skill covers hierarchical YAML-based configuration with profile support, secrets management, and testing strategies.

**Philosophy**: "Configuration is code. Version it, test it, document it, and never commit secrets."

---

## Quick Reference

### Configuration Priority (Last Wins)

```
1. default.yaml          (system-wide defaults)
2. components/*.yaml     (component-specific settings)
3. profiles/{mode}.yaml  (environment/mode overrides)
4. .env                  (secrets and hardware-specific values)
```

### Common Operations

| Task | Command/Pattern |
|------|----------------|
| Load config | `config = ConfigLoader.load(profile='development')` |
| Override for testing | `config = ConfigLoader.load(overrides={'debug': True})` |
| Access nested value | `value = config['component']['subsystem']['setting']` |
| Environment variable | `export PROJECT_MODE=production` |
| Validate config | `ConfigLoader.validate(schema)` |

---

## The Hierarchical Configuration Pattern

### Why Hierarchical?

**Problem**: Need different settings for development, staging, production without code changes.

**Solution**: Layer configurations from general to specific:

```
Default Settings (all environments)
    ↓
Component Settings (component-specific)
    ↓
Profile Settings (environment overrides)
    ↓
Environment Variables (secrets, local overrides)
```

**Benefits**:
- ✅ DRY (Don't Repeat Yourself) - defaults defined once
- ✅ Easy environment switching (`--profile production`)
- ✅ Safe secrets (never commit .env)
- ✅ Testable (override configs in tests)
- ✅ Documentable (configs explain system behavior)

---

## Directory Structure

### Recommended Layout

```
project/
├── config/
│   ├── default.yaml              # System-wide defaults (committed)
│   │
│   ├── components/               # Component-specific configs (committed)
│   │   ├── database.yaml
│   │   ├── api_client.yaml
│   │   ├── cache.yaml
│   │   └── logging.yaml
│   │
│   ├── profiles/                 # Environment/mode overrides (committed)
│   │   ├── development.yaml     # Local dev settings
│   │   ├── testing.yaml         # CI/CD test settings
│   │   ├── staging.yaml         # Pre-production
│   │   └── production.yaml      # Production optimizations
│   │
│   └── .env.example             # Template for secrets (committed)
│
├── .env                         # Actual secrets (NEVER COMMIT)
├── .gitignore                   # Must exclude .env
└── src/
    └── core/
        └── config.py            # Configuration loader
```

### What Gets Committed vs Ignored

**Commit to Git** ✅:
- `config/default.yaml`
- `config/components/*.yaml`
- `config/profiles/*.yaml`
- `.env.example` (template showing required variables)

**NEVER Commit** ❌:
- `.env` (contains secrets)
- `.env.local`
- `.env.production`
- `config/local/*.yaml` (machine-specific overrides)

---

## Configuration Files

### 1. Default Configuration

**Purpose**: System-wide defaults that apply to all environments.

**File**: `config/default.yaml`

```yaml
# Default Configuration
# These values apply to all environments unless overridden

system:
  name: "my-application"
  version: "1.0.0"
  mode: "development"  # Default mode

# Logging configuration
logging:
  level: "INFO"        # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "json"       # json or text
  output: "stdout"     # stdout, file, or both
  file:
    path: "logs/app.log"
    max_bytes: 10485760      # 10MB
    backup_count: 5
    rotation: true

# Performance settings
performance:
  worker_threads: 4
  max_connections: 100
  timeout_seconds: 30
  retry_attempts: 3
  retry_backoff_seconds: 1

# Feature flags (global defaults)
features:
  enable_caching: true
  enable_telemetry: false
  enable_debug_endpoints: false
  enable_rate_limiting: true

# Security defaults
security:
  require_authentication: true
  session_timeout_minutes: 60
  max_login_attempts: 5
  password_min_length: 12
```

**Best Practices**:
- ✅ Comprehensive comments explaining each section
- ✅ Conservative defaults (safe for production)
- ✅ Group related settings together
- ✅ Use clear naming conventions

---

### 2. Component Configuration

**Purpose**: Component-specific settings that are independent of environment.

**File**: `config/components/database.yaml`

```yaml
database:
  # Connection settings (secrets in .env)
  driver: "postgresql"
  host: "${DB_HOST:localhost}"           # Env var with default
  port: ${DB_PORT:5432}
  name: "${DB_NAME:myapp}"
  user: "${DB_USER:postgres}"
  password: "${DB_PASSWORD}"             # Required from .env

  # Connection pool
  pool:
    min_connections: 2
    max_connections: 10
    connection_timeout_seconds: 5
    idle_timeout_seconds: 300

  # Query settings
  query:
    default_timeout_seconds: 30
    enable_query_logging: false
    slow_query_threshold_ms: 1000

  # Migrations
  migrations:
    auto_migrate: false
    migration_path: "migrations/"
```

**File**: `config/components/api_client.yaml`

```yaml
api_client:
  # External API configuration
  base_url: "${API_BASE_URL:https://api.example.com}"
  api_key: "${API_KEY}"                  # Required from .env
  api_secret: "${API_SECRET}"            # Required from .env

  # Request settings
  timeout_seconds: 10
  retry_attempts: 3
  retry_backoff_seconds: 2
  max_retries: 5

  # Rate limiting
  rate_limit:
    requests_per_second: 10
    burst_size: 20

  # Headers
  headers:
    User-Agent: "MyApp/1.0"
    Accept: "application/json"

  # Endpoints
  endpoints:
    users: "/v1/users"
    data: "/v1/data"
    health: "/health"
```

**File**: `config/components/cache.yaml`

```yaml
cache:
  # Cache backend
  backend: "redis"                       # redis, memcached, or memory

  # Redis configuration
  redis:
    host: "${REDIS_HOST:localhost}"
    port: ${REDIS_PORT:6379}
    db: ${REDIS_DB:0}
    password: "${REDIS_PASSWORD:}"       # Optional
    socket_timeout_seconds: 5

  # Cache behavior
  default_ttl_seconds: 3600              # 1 hour
  key_prefix: "myapp:"

  # Cache strategies
  strategies:
    user_data:
      ttl_seconds: 600                   # 10 minutes
      max_size_mb: 100
    session_data:
      ttl_seconds: 1800                  # 30 minutes
      max_size_mb: 50
```

**Environment Variable Syntax**:
- `${VAR}` - Required variable (error if not set)
- `${VAR:default}` - Optional with default value
- `${VAR:}` - Optional, defaults to empty string

---

### 3. Profile Configuration

**Purpose**: Environment-specific overrides (dev, test, staging, prod).

**File**: `config/profiles/development.yaml`

```yaml
# Development Profile
# Optimized for local development with verbose logging and debug features

system:
  mode: "development"

logging:
  level: "DEBUG"                        # Verbose logging
  format: "text"                        # Human-readable
  output: "stdout"                      # Console output

performance:
  worker_threads: 2                     # Lower resource usage
  timeout_seconds: 60                   # Longer timeouts for debugging

features:
  enable_debug_endpoints: true          # /debug, /metrics endpoints
  enable_telemetry: false               # No external tracking
  enable_caching: false                 # Fresh data for testing
  enable_rate_limiting: false           # No rate limits in dev

# Component overrides
database:
  pool:
    max_connections: 5                  # Lower pool for dev
  query:
    enable_query_logging: true          # Log all queries
  migrations:
    auto_migrate: true                  # Auto-run migrations

api_client:
  base_url: "http://localhost:8080"     # Local mock server
  timeout_seconds: 30                   # Longer timeout
  retry_attempts: 1                     # Fail fast in dev

cache:
  backend: "memory"                     # In-memory cache (no Redis needed)
```

**File**: `config/profiles/testing.yaml`

```yaml
# Testing Profile
# Used in CI/CD pipelines and automated tests

system:
  mode: "testing"

logging:
  level: "WARNING"                      # Quiet logs for tests
  format: "json"
  output: "file"
  file:
    path: "logs/test.log"

performance:
  worker_threads: 1                     # Single-threaded for determinism
  timeout_seconds: 5                    # Fast failure

features:
  enable_debug_endpoints: false
  enable_telemetry: false
  enable_caching: false                 # No caching in tests
  enable_rate_limiting: false

database:
  name: "myapp_test"                    # Separate test database
  pool:
    max_connections: 2
  migrations:
    auto_migrate: true                  # Fresh DB each test run

api_client:
  base_url: "http://mock-api:8080"      # Mock server
  timeout_seconds: 5
  retry_attempts: 0                     # No retries in tests

cache:
  backend: "memory"                     # In-memory only
```

**File**: `config/profiles/production.yaml`

```yaml
# Production Profile
# Optimized for performance, security, and reliability

system:
  mode: "production"

logging:
  level: "WARNING"                      # Only warnings and errors
  format: "json"                        # Structured for log aggregation
  output: "both"                        # Console + file
  file:
    path: "/var/log/myapp/app.log"
    max_bytes: 52428800                 # 50MB
    backup_count: 10

performance:
  worker_threads: 8                     # Higher concurrency
  max_connections: 500
  timeout_seconds: 15                   # Shorter timeouts
  retry_attempts: 5

features:
  enable_debug_endpoints: false         # NEVER expose in prod
  enable_telemetry: true                # Production monitoring
  enable_caching: true                  # Full caching
  enable_rate_limiting: true            # Protect from abuse

security:
  require_authentication: true
  session_timeout_minutes: 30           # Shorter sessions
  max_login_attempts: 3                 # Stricter limits

database:
  pool:
    min_connections: 5
    max_connections: 50                 # Large pool
    connection_timeout_seconds: 3       # Fail fast
  query:
    default_timeout_seconds: 10         # Strict timeout
    enable_query_logging: false         # No query logging
  migrations:
    auto_migrate: false                 # NEVER auto-migrate in prod

api_client:
  timeout_seconds: 10
  retry_attempts: 5
  retry_backoff_seconds: 2

cache:
  backend: "redis"                      # Production Redis
  default_ttl_seconds: 3600
```

---

### 4. Environment Variables (.env)

**Purpose**: Secrets, credentials, and machine-specific settings.

**File**: `.env.example` (template, committed to git)

```bash
# Environment Variables Template
# Copy to .env and fill in actual values
# NEVER commit .env to git!

# System Configuration
PROJECT_MODE=development                 # development, testing, staging, production
PROJECT_CONFIG_PROFILE=development       # Override config profile

# Database Credentials (REQUIRED)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp_dev
DB_USER=postgres
DB_PASSWORD=your_secure_password_here

# External API Keys (REQUIRED)
API_BASE_URL=https://api.example.com
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here

# Redis (Optional for development)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Security Secrets
SECRET_KEY=generate_a_random_secret_key_here
JWT_SECRET=another_random_secret_for_jwt

# Optional: Feature Flags (override config)
ENABLE_DEBUG_ENDPOINTS=false
ENABLE_TELEMETRY=false

# Optional: Performance Tuning
WORKER_THREADS=4
MAX_CONNECTIONS=100

# Logging
LOG_LEVEL=INFO                          # DEBUG, INFO, WARNING, ERROR
LOG_FILE_PATH=logs/app.log
```

**File**: `.env` (actual secrets, NEVER commit)

```bash
# NEVER COMMIT THIS FILE TO GIT
# Add to .gitignore: .env

PROJECT_MODE=development

DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp_dev
DB_USER=postgres
DB_PASSWORD=MySecureP@ssw0rd123

API_BASE_URL=https://api.example.com
API_KEY=sk_live_abc123def456
API_SECRET=secret_xyz789

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
JWT_SECRET=b3BlbnNzaC1rZXktdjEAAAAACmFlczI1Ni1jdHI
```

**Best Practices**:
- ✅ Use `.env.example` as documentation
- ✅ Add `.env` to `.gitignore`
- ✅ Use strong random secrets (never "secret123")
- ✅ Document which variables are required vs optional
- ✅ Group related variables together
- ✅ Use UPPER_SNAKE_CASE for environment variables

---

## Configuration Loader Implementation

### Basic Python Implementation

**File**: `src/core/config.py`

```python
"""
Configuration loader with hierarchical YAML support.

Loads configuration in priority order:
1. default.yaml (base configuration)
2. components/*.yaml (component-specific settings)
3. profiles/{profile}.yaml (environment overrides)
4. Environment variables (secrets and overrides)

Educational Note:
This pattern is called "Configuration as Code" and follows the
12-Factor App methodology for config management.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
import logging
import re

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Load and merge hierarchical YAML configurations."""

    def __init__(self, config_dir: str = "config"):
        """
        Initialize configuration loader.

        Args:
            config_dir: Path to configuration directory
        """
        self.config_dir = Path(config_dir)
        self._config: Dict[str, Any] = {}

    @classmethod
    def load(
        cls,
        config_dir: str = "config",
        profile: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration with hierarchical merging.

        Args:
            config_dir: Path to configuration directory
            profile: Profile name (development, testing, production)
            overrides: Dictionary of override values

        Returns:
            Merged configuration dictionary

        Example:
            >>> config = ConfigLoader.load(profile='development')
            >>> db_host = config['database']['host']
        """
        loader = cls(config_dir)

        # 1. Load default configuration
        loader._load_default()

        # 2. Load component configurations
        loader._load_components()

        # 3. Load profile configuration
        if profile:
            loader._load_profile(profile)

        # 4. Apply environment variables
        loader._apply_env_vars()

        # 5. Apply overrides (for testing)
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
        """Load all component configurations from components/ directory."""
        components_dir = self.config_dir / "components"
        if not components_dir.exists():
            logger.warning(f"Components directory not found: {components_dir}")
            return

        for yaml_file in components_dir.glob("*.yaml"):
            logger.info(f"Loading component config: {yaml_file.name}")
            with open(yaml_file) as f:
                component_config = yaml.safe_load(f)
                if component_config:
                    self._deep_merge(self._config, component_config)

    def _load_profile(self, profile: str):
        """
        Load profile configuration.

        Args:
            profile: Profile name (e.g., 'development', 'production')
        """
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
        """
        Apply environment variable substitution.

        Supports syntax:
        - ${VAR} - Required variable
        - ${VAR:default} - Optional with default
        """
        self._config = self._substitute_env_vars(self._config)

    def _substitute_env_vars(self, obj: Any) -> Any:
        """
        Recursively substitute environment variables in config.

        Args:
            obj: Configuration object (dict, list, str, etc.)

        Returns:
            Object with environment variables substituted
        """
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
        Expand environment variable in string.

        Supports:
        - ${VAR} - Required variable (error if not set)
        - ${VAR:default} - Optional with default value

        Args:
            value: String potentially containing ${VAR} syntax

        Returns:
            Expanded value (string, int, float, or bool)
        """
        # Match ${VAR} or ${VAR:default}
        pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'

        def replacer(match):
            var_name = match.group(1)
            default_value = match.group(2)

            # Get environment variable
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

        # Try to convert to appropriate type
        return self._convert_type(result)

    def _convert_type(self, value: str) -> Any:
        """
        Convert string to appropriate type.

        Args:
            value: String value

        Returns:
            Converted value (int, float, bool, or str)
        """
        # Try boolean
        if value.lower() in ('true', 'yes', 'on', '1'):
            return True
        if value.lower() in ('false', 'no', 'off', '0'):
            return False

        # Try int
        try:
            return int(value)
        except ValueError:
            pass

        # Try float
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value

    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """
        Deep merge two dictionaries.

        Args:
            base: Base dictionary (modified in place)
            update: Update dictionary (merged into base)

        Returns:
            Merged dictionary (same as base)

        Educational Note:
        Deep merge is essential for hierarchical configs. It ensures
        nested dictionaries are merged recursively, not replaced.
        """
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                self._deep_merge(base[key], value)
            else:
                # Replace value
                base[key] = value
        return base


# Convenience function
def load_config(profile: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration with optional profile.

    Args:
        profile: Configuration profile (development, testing, production)
                 If None, uses PROJECT_CONFIG_PROFILE env var or default

    Returns:
        Merged configuration dictionary

    Example:
        >>> config = load_config('development')
        >>> db_name = config['database']['name']
    """
    # Determine profile from environment or argument
    if profile is None:
        profile = os.environ.get('PROJECT_CONFIG_PROFILE', 'development')

    return ConfigLoader.load(profile=profile)
```

---

## Usage Examples

### Basic Usage

```python
from core.config import load_config

# Load configuration (uses development profile by default)
config = load_config()

# Access nested values
db_host = config['database']['host']
db_port = config['database']['port']
log_level = config['logging']['level']

# Check feature flags
if config['features']['enable_caching']:
    cache = setup_cache(config['cache'])
```

### Profile-Based Loading

```python
# Load specific profile
dev_config = load_config(profile='development')
prod_config = load_config(profile='production')

# Profile from environment variable
# export PROJECT_CONFIG_PROFILE=staging
config = load_config()  # Loads staging profile
```

### Testing with Overrides

```python
import pytest
from core.config import ConfigLoader

@pytest.fixture
def test_config():
    """Test configuration with overrides."""
    return ConfigLoader.load(
        profile='testing',
        overrides={
            'database': {
                'name': 'test_db_12345',  # Unique test DB
                'pool': {'max_connections': 1}
            },
            'api_client': {
                'base_url': 'http://mock-api:8080'
            }
        }
    )

def test_database_connection(test_config):
    """Test with overridden config."""
    db = Database(test_config['database'])
    assert db.connect()
```

### Component Initialization

```python
class DatabaseManager:
    """Database manager using configuration."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize database manager.

        Args:
            config: Configuration dictionary (typically config['database'])
        """
        self.host = config['host']
        self.port = config['port']
        self.database = config['name']
        self.user = config['user']
        self.password = config['password']

        # Connection pool settings
        pool_config = config['pool']
        self.min_connections = pool_config['min_connections']
        self.max_connections = pool_config['max_connections']

        self._pool = None

    def connect(self):
        """Establish database connection."""
        # Use configuration to create connection pool
        self._pool = create_pool(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password,
            min_size=self.min_connections,
            max_size=self.max_connections
        )

# Usage
config = load_config()
db = DatabaseManager(config['database'])
db.connect()
```

---

## Configuration Validation

### Schema-Based Validation

**Using Pydantic for type-safe configuration:**

```python
from pydantic import BaseModel, Field, validator
from typing import Literal, Optional

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
    """Application configuration schema."""
    system: dict
    logging: LoggingConfig
    database: DatabaseConfig
    features: dict

# Validate configuration
def load_validated_config(profile: Optional[str] = None) -> AppConfig:
    """
    Load and validate configuration.

    Raises:
        ValidationError: If configuration is invalid

    Returns:
        Validated configuration object
    """
    raw_config = load_config(profile)

    try:
        validated_config = AppConfig(**raw_config)
        return validated_config
    except ValidationError as e:
        logger.error(f"Configuration validation failed: {e}")
        raise

# Usage
config = load_validated_config('production')
print(f"Log level: {config.logging.level}")
print(f"DB host: {config.database.host}")
```

### Runtime Validation

```python
def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration at startup.

    Args:
        config: Configuration dictionary

    Returns:
        True if valid, raises exception otherwise

    Raises:
        ValueError: If configuration is invalid
    """
    errors = []

    # Check required sections
    required_sections = ['system', 'logging', 'database']
    for section in required_sections:
        if section not in config:
            errors.append(f"Missing required section: {section}")

    # Validate database config
    if 'database' in config:
        db_config = config['database']
        if not db_config.get('host'):
            errors.append("Database host is required")
        if not db_config.get('password'):
            errors.append("Database password is required")

    # Validate feature flags
    if 'features' in config:
        features = config['features']
        if features.get('enable_debug_endpoints') and config['system']['mode'] == 'production':
            errors.append("Debug endpoints cannot be enabled in production")

    # Check for insecure defaults
    if 'security' in config:
        security = config['security']
        if security.get('password_min_length', 0) < 8:
            errors.append("Password minimum length must be at least 8")

    if errors:
        error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        raise ValueError(error_msg)

    return True

# Validate at startup
config = load_config()
validate_config(config)
```

---

## Secrets Management

### Best Practices

**DO** ✅:
- Use `.env` files for secrets (never commit)
- Provide `.env.example` as template (committed)
- Use environment variables for all secrets
- Rotate secrets regularly
- Use strong random secrets (not "password123")
- Use secret management services in production (AWS Secrets Manager, HashiCorp Vault)
- Encrypt secrets at rest
- Audit secret access

**DON'T** ❌:
- Never commit `.env` to git
- Never hardcode secrets in config files
- Never log secrets
- Never expose secrets in error messages
- Never use weak/default secrets
- Never share secrets via insecure channels

### .gitignore for Secrets

```gitignore
# Environment variables (secrets)
.env
.env.local
.env.*.local
.env.production
.env.staging

# Exception: Keep template
!.env.example

# Local configuration overrides
config/local/
config/*.local.yaml

# Secret files
secrets/
*.secret
*.key
*.pem
*.p12
api_key.txt
token.txt
```

### Secret Rotation

When rotating secrets:

1. **Generate new secret**:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Update `.env` file**:
   ```bash
   # Old
   API_KEY=old_key_abc123

   # New
   API_KEY=new_key_xyz789
   ```

3. **Rolling deployment**:
   - Deploy new version supporting both old and new secrets
   - Verify new secret works
   - Remove old secret support
   - Revoke old secret

4. **Audit**:
   - Log when secrets are rotated
   - Track secret age
   - Alert on old secrets

---

## Testing Strategies

### Test Configuration Files

**File**: `tests/fixtures/test_config.yaml`

```yaml
# Test configuration
# Used in automated tests

system:
  name: "test-app"
  mode: "testing"

logging:
  level: "ERROR"              # Quiet logs in tests
  output: "file"
  file:
    path: "/tmp/test.log"

database:
  host: "localhost"
  port: 5432
  name: "test_db"
  user: "test_user"
  password: "test_password"
  pool:
    max_connections: 1        # Single connection for tests

api_client:
  base_url: "http://mock-api:8080"
  timeout_seconds: 1          # Fast failure
  retry_attempts: 0           # No retries

features:
  enable_caching: false
  enable_telemetry: false
```

### Testing Configuration Loading

```python
import pytest
from core.config import ConfigLoader

def test_config_loading():
    """Test basic configuration loading."""
    config = ConfigLoader.load(profile='testing')

    assert config['system']['mode'] == 'testing'
    assert 'database' in config
    assert 'logging' in config

def test_config_merging():
    """Test hierarchical configuration merging."""
    config = ConfigLoader.load(profile='development')

    # Default value
    assert config['logging']['backup_count'] == 5

    # Development override
    assert config['logging']['level'] == 'DEBUG'

def test_env_var_substitution():
    """Test environment variable substitution."""
    import os

    # Set test environment variable
    os.environ['TEST_DB_HOST'] = 'test.example.com'

    config_data = {
        'database': {
            'host': '${TEST_DB_HOST}'
        }
    }

    loader = ConfigLoader()
    result = loader._substitute_env_vars(config_data)

    assert result['database']['host'] == 'test.example.com'

def test_required_env_var_missing():
    """Test error when required env var is missing."""
    import os

    # Ensure variable is not set
    os.environ.pop('MISSING_VAR', None)

    config_data = {
        'setting': '${MISSING_VAR}'
    }

    loader = ConfigLoader()

    with pytest.raises(ValueError, match="Required environment variable not set"):
        loader._substitute_env_vars(config_data)

def test_config_overrides():
    """Test configuration overrides for testing."""
    config = ConfigLoader.load(
        profile='testing',
        overrides={
            'database': {
                'name': 'custom_test_db'
            }
        }
    )

    assert config['database']['name'] == 'custom_test_db'
```

### Pytest Fixtures for Configuration

```python
# conftest.py
import pytest
from core.config import ConfigLoader

@pytest.fixture
def test_config():
    """Base test configuration."""
    return ConfigLoader.load(profile='testing')

@pytest.fixture
def isolated_config():
    """Isolated configuration for each test."""
    return ConfigLoader.load(
        profile='testing',
        overrides={
            'database': {
                'name': f'test_db_{pytest.current_test}'
            }
        }
    )

@pytest.fixture
def mock_api_config(test_config):
    """Configuration with mocked API."""
    test_config['api_client']['base_url'] = 'http://mock-api:8080'
    return test_config

# Usage in tests
def test_with_config(test_config):
    """Test using base test config."""
    assert test_config['system']['mode'] == 'testing'

def test_with_isolated_db(isolated_config):
    """Test with isolated database."""
    db = Database(isolated_config['database'])
    # Test has its own DB, won't interfere with others
```

---

## Migration Strategies

### Refactoring Hardcoded Values

**Before** (hardcoded):

```python
class APIClient:
    def __init__(self):
        self.base_url = "https://api.example.com"
        self.timeout = 10
        self.retries = 3
        self.api_key = "hardcoded_key_123"  # Bad!
```

**After** (configuration):

```python
class APIClient:
    def __init__(self, config: Dict[str, Any]):
        self.base_url = config['base_url']
        self.timeout = config['timeout_seconds']
        self.retries = config['retry_attempts']
        self.api_key = config['api_key']  # From .env
```

### Gradual Migration

**Phase 1**: Add configuration system
- Create `config/default.yaml`
- Implement `ConfigLoader`
- Add `.env.example`

**Phase 2**: Migrate non-sensitive settings
- Move timeouts, limits, flags to YAML
- Update code to use config
- Test with existing behavior

**Phase 3**: Migrate secrets
- Move API keys, passwords to `.env`
- Update code to read from config
- Test secret loading

**Phase 4**: Add profiles
- Create `profiles/development.yaml`
- Create `profiles/production.yaml`
- Test profile switching

**Phase 5**: Clean up
- Remove hardcoded values
- Add configuration validation
- Document all settings

---

## Common Patterns

### Pattern 1: Feature Flags

**Configuration**:

```yaml
features:
  new_algorithm: false        # A/B test new feature
  legacy_api: true            # Support old API
  beta_feature: false         # Beta features
```

**Usage**:

```python
if config['features']['new_algorithm']:
    result = new_algorithm(data)
else:
    result = legacy_algorithm(data)
```

### Pattern 2: Environment Detection

```python
def is_development() -> bool:
    """Check if running in development mode."""
    return config['system']['mode'] == 'development'

def is_production() -> bool:
    """Check if running in production mode."""
    return config['system']['mode'] == 'production'

# Usage
if is_development():
    # Enable debug features
    app.debug = True
```

### Pattern 3: Graceful Degradation

```yaml
cache:
  backend: "redis"
  redis:
    host: "${REDIS_HOST:localhost}"
  fallback_to_memory: true    # Fallback if Redis unavailable
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

### Pattern 4: Configuration Inheritance

**Base configuration** (`config/base/common.yaml`):

```yaml
api_defaults: &api_defaults
  timeout_seconds: 30
  retry_attempts: 3
  headers:
    User-Agent: "MyApp/1.0"

services:
  user_api:
    <<: *api_defaults          # Inherit defaults
    base_url: "https://users.example.com"

  data_api:
    <<: *api_defaults
    base_url: "https://data.example.com"
    timeout_seconds: 60        # Override timeout
```

---

## Troubleshooting

### Issue: Environment variable not substituted

**Symptom**: Configuration contains literal `${VAR}` string.

**Cause**: Environment variable not set and no default provided.

**Solution**:
1. Check if variable is set: `echo $VAR`
2. Set variable: `export VAR=value`
3. Or provide default: `${VAR:default_value}`

### Issue: Configuration not loading

**Symptom**: `FileNotFoundError` or empty configuration.

**Cause**: Incorrect config directory path.

**Solution**:
```python
# Debug configuration loading
import logging
logging.basicConfig(level=logging.DEBUG)
config = load_config()  # Will show which files are loaded
```

### Issue: Profile not applied

**Symptom**: Profile settings not overriding defaults.

**Cause**: Profile name incorrect or file not found.

**Solution**:
```bash
# List available profiles
ls config/profiles/

# Verify profile file exists
cat config/profiles/development.yaml

# Check profile is loaded
export PROJECT_CONFIG_PROFILE=development
python -c "from core.config import load_config; print(load_config()['system']['mode'])"
```

### Issue: Secrets exposed in logs

**Symptom**: API keys or passwords visible in log files.

**Cause**: Logging configuration object or using `repr()`.

**Solution**:
```python
# Bad - logs entire config including secrets
logger.debug(f"Config: {config}")

# Good - log only non-sensitive values
logger.debug(f"Database host: {config['database']['host']}")

# Good - sanitize config before logging
def sanitize_config(config):
    """Remove secrets from config for logging."""
    sanitized = config.copy()
    if 'database' in sanitized:
        sanitized['database'] = {**sanitized['database'], 'password': '***'}
    if 'api_client' in sanitized:
        sanitized['api_client'] = {**sanitized['api_client'], 'api_key': '***', 'api_secret': '***'}
    return sanitized

logger.debug(f"Config: {sanitize_config(config)}")
```

---

## Configuration Audit Checklist

Use this checklist to audit existing configuration systems:

**Structure** ✅:
- [ ] Configuration files separated from code
- [ ] Hierarchical structure (default → components → profiles)
- [ ] Clear directory organization (`config/` directory)
- [ ] Profile-based environments (dev, test, staging, prod)

**Secrets** ✅:
- [ ] No secrets committed to git
- [ ] `.env` file for secrets (in `.gitignore`)
- [ ] `.env.example` template provided
- [ ] Environment variables for all sensitive data
- [ ] Strong, random secrets (not defaults)

**Validation** ✅:
- [ ] Configuration validated at startup
- [ ] Clear error messages for misconfiguration
- [ ] Type checking for values
- [ ] Required vs optional settings documented

**Documentation** ✅:
- [ ] All settings documented with comments
- [ ] README explaining configuration system
- [ ] Examples for common use cases
- [ ] Migration guide for updating configs

**Testing** ✅:
- [ ] Test configurations separate from production
- [ ] Configuration overrides in tests
- [ ] Tests for configuration loading
- [ ] Tests for environment variable substitution

**Security** ✅:
- [ ] Secrets never logged
- [ ] No hardcoded credentials
- [ ] Production config requires authentication
- [ ] Debug endpoints disabled in production
- [ ] Security settings reviewed

---

## References

### Standards and Best Practices
- [12-Factor App: Config](https://12factor.net/config)
- [OWASP Configuration Best Practices](https://owasp.org/)
- [YAML Specification](https://yaml.org/spec/)

### Tools
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [python-dotenv](https://github.com/theskumar/python-dotenv) - .env file loading
- [dynaconf](https://www.dynaconf.com/) - Advanced config management

### Secret Management
- [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)
- [HashiCorp Vault](https://www.vaultproject.io/)
- [Azure Key Vault](https://azure.microsoft.com/en-us/services/key-vault/)

---

**Maintained by**: Configuration Management Skill
**Version**: 1.0.0
**Last Updated**: 2025-11-14
