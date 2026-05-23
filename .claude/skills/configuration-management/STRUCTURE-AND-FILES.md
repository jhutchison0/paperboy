# STRUCTURE-AND-FILES — Directory Layout and Config File Types

Sidecar to `SKILL.md`. The four file types in a hierarchical config system, what they contain, and how they're organized on disk.

## Directory Layout

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
│   │   ├── development.yaml
│   │   ├── testing.yaml
│   │   ├── staging.yaml
│   │   └── production.yaml
│   │
│   └── .env.example              # Template for secrets (committed)
│
├── .env                          # Actual secrets (NEVER COMMIT)
├── .gitignore                    # Must exclude .env
└── src/
    └── core/
        └── config.py             # Configuration loader (see LOADER.md)
```

## What Gets Committed vs Ignored

**Commit to git** ✅:
- `config/default.yaml`
- `config/components/*.yaml`
- `config/profiles/*.yaml`
- `.env.example` (template showing required variables)

**Never commit** ❌:
- `.env` (contains real secrets)
- `.env.local`, `.env.production`, any `.env.*`
- `config/local/*.yaml` (machine-specific overrides)
- Anything matching the `.gitignore` patterns in `SECRETS.md`

## File Type 1: Default Configuration

**Purpose**: system-wide defaults that apply to all environments unless overridden.

`config/default.yaml`:

```yaml
# Default Configuration
# These values apply to all environments unless overridden.

system:
  name: "my-application"
  version: "1.0.0"
  mode: "development"      # Default mode; profile typically overrides

logging:
  level: "INFO"            # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "json"           # json or text
  output: "stdout"         # stdout, file, or both
  file:
    path: "logs/app.log"
    max_bytes: 10485760    # 10MB
    backup_count: 5
    rotation: true

performance:
  worker_threads: 4
  max_connections: 100
  timeout_seconds: 30
  retry_attempts: 3
  retry_backoff_seconds: 1

features:
  enable_caching: true
  enable_telemetry: false
  enable_debug_endpoints: false   # Always false here; never override true at base
  enable_rate_limiting: true

security:
  require_authentication: true
  session_timeout_minutes: 60
  max_login_attempts: 5
  password_min_length: 12
```

**Best practices**:
- Comments explaining each section.
- **Conservative defaults** — values safe for production. Override down for dev, never up for prod.
- Group related settings.
- Clear naming. No abbreviations that aren't obvious.

## File Type 2: Component Configuration

**Purpose**: settings for one component, independent of environment.

`config/components/database.yaml`:

```yaml
database:
  driver: "postgresql"
  host: "${DB_HOST:localhost}"      # Env var with default
  port: ${DB_PORT:5432}
  name: "${DB_NAME:myapp}"
  user: "${DB_USER:postgres}"
  password: "${DB_PASSWORD}"        # Required from .env

  pool:
    min_connections: 2
    max_connections: 10
    connection_timeout_seconds: 5
    idle_timeout_seconds: 300

  query:
    default_timeout_seconds: 30
    enable_query_logging: false
    slow_query_threshold_ms: 1000

  migrations:
    auto_migrate: false             # Override true ONLY in non-prod profiles
    migration_path: "migrations/"
```

`config/components/api_client.yaml`:

```yaml
api_client:
  base_url: "${API_BASE_URL:https://api.example.com}"
  api_key: "${API_KEY}"             # Required from .env
  api_secret: "${API_SECRET}"       # Required from .env

  timeout_seconds: 10
  retry_attempts: 3
  retry_backoff_seconds: 2
  max_retries: 5

  rate_limit:
    requests_per_second: 10
    burst_size: 20

  headers:
    User-Agent: "MyApp/1.0"
    Accept: "application/json"

  endpoints:
    users: "/v1/users"
    data: "/v1/data"
    health: "/health"
```

`config/components/cache.yaml`:

```yaml
cache:
  backend: "redis"                   # redis, memcached, or memory

  redis:
    host: "${REDIS_HOST:localhost}"
    port: ${REDIS_PORT:6379}
    db: ${REDIS_DB:0}
    password: "${REDIS_PASSWORD:}"   # Optional
    socket_timeout_seconds: 5

  default_ttl_seconds: 3600
  key_prefix: "myapp:"

  strategies:
    user_data:
      ttl_seconds: 600
      max_size_mb: 100
    session_data:
      ttl_seconds: 1800
      max_size_mb: 50
```

**Best practices**:
- One file per component (database, api_client, cache, logging).
- All secrets via `${VAR}`. No raw values for anything sensitive.
- Defaults for development; production profile overrides what production needs.

## File Type 3: Profile Configuration

**Purpose**: environment-specific overrides (dev, test, staging, prod).

`config/profiles/development.yaml`:

```yaml
# Development Profile
# Verbose logging, debug features on, conservative resource use.

system:
  mode: "development"

logging:
  level: "DEBUG"                  # Verbose
  format: "text"                  # Human-readable
  output: "stdout"

performance:
  worker_threads: 2               # Lower for dev
  timeout_seconds: 60             # Longer for debugging

features:
  enable_debug_endpoints: true    # /debug, /metrics endpoints
  enable_telemetry: false         # No external tracking in dev
  enable_caching: false           # Fresh data for testing
  enable_rate_limiting: false

database:
  pool:
    max_connections: 5            # Lower pool for dev
  query:
    enable_query_logging: true    # Log all queries
  migrations:
    auto_migrate: true            # Auto-run migrations in dev only

api_client:
  base_url: "http://localhost:8080"  # Local mock server
  timeout_seconds: 30
  retry_attempts: 1               # Fail fast in dev

cache:
  backend: "memory"               # In-memory (no Redis needed)
```

`config/profiles/testing.yaml`:

```yaml
# Testing Profile
# Used in CI/CD pipelines and automated tests.

system:
  mode: "testing"

logging:
  level: "WARNING"                # Quiet logs for tests
  format: "json"
  output: "file"
  file:
    path: "logs/test.log"

performance:
  worker_threads: 1               # Single-threaded for determinism
  timeout_seconds: 5              # Fast failure

features:
  enable_debug_endpoints: false
  enable_telemetry: false
  enable_caching: false
  enable_rate_limiting: false

database:
  name: "myapp_test"              # Separate test database
  pool:
    max_connections: 2
  migrations:
    auto_migrate: true            # Fresh DB each test run

api_client:
  base_url: "http://mock-api:8080"
  timeout_seconds: 5
  retry_attempts: 0               # No retries in tests

cache:
  backend: "memory"
```

`config/profiles/production.yaml`:

```yaml
# Production Profile
# Optimized for performance, security, reliability.

system:
  mode: "production"

logging:
  level: "WARNING"
  format: "json"                  # Structured for log aggregation
  output: "both"
  file:
    path: "/var/log/myapp/app.log"
    max_bytes: 52428800
    backup_count: 10

performance:
  worker_threads: 8
  max_connections: 500
  timeout_seconds: 15
  retry_attempts: 5

features:
  enable_debug_endpoints: false   # NEVER expose in prod
  enable_telemetry: true
  enable_caching: true
  enable_rate_limiting: true

security:
  require_authentication: true
  session_timeout_minutes: 30
  max_login_attempts: 3

database:
  pool:
    min_connections: 5
    max_connections: 50
    connection_timeout_seconds: 3
  query:
    default_timeout_seconds: 10
    enable_query_logging: false
  migrations:
    auto_migrate: false           # NEVER auto-migrate in prod

api_client:
  timeout_seconds: 10
  retry_attempts: 5
  retry_backoff_seconds: 2

cache:
  backend: "redis"
  default_ttl_seconds: 3600
```

## File Type 4: Environment Variables (.env)

**Purpose**: secrets, credentials, and machine-specific settings.

`.env.example` (template, committed):

```bash
# Environment Variables Template
# Copy to .env and fill in actual values.
# NEVER commit .env to git!

# System
PROJECT_MODE=development           # development, testing, staging, production
PROJECT_CONFIG_PROFILE=development

# Database (REQUIRED)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp_dev
DB_USER=postgres
DB_PASSWORD=your_secure_password_here

# External API (REQUIRED)
API_BASE_URL=https://api.example.com
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here

# Redis (Optional for development)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Security
SECRET_KEY=generate_a_random_secret_key_here
JWT_SECRET=another_random_secret_for_jwt

# Optional override flags
ENABLE_DEBUG_ENDPOINTS=false
ENABLE_TELEMETRY=false

# Logging
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/app.log
```

See `SECRETS.md` for `.env` handling, `.gitignore` patterns, and secret rotation.

## See Also

- `LOADER.md` — how these files get loaded and merged.
- `SECRETS.md` — `.env` management and security.
- `VALIDATION.md` — schema validation at startup.
- `TESTING-AND-PATTERNS.md` — testing the layered config and common usage patterns.
