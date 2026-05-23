# FIXTURES — Shared Fixtures, conftest, Test Data Management

Sidecar to `SKILL.md`. How to set up the dependencies tests need. Three layers: shared fixtures in `conftest.py`, component-specific fixtures in nested `conftest.py`, and test data in `tests/fixtures/`.

## Shared Fixtures (`tests/conftest.py`)

Fixtures defined here are available to all tests in the suite.

```python
"""Root test configuration and shared fixtures."""

import pytest
import tempfile
import shutil
from datetime import datetime


@pytest.fixture
def temp_directory():
    """Temporary directory, cleaned up after test."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def current_timestamp():
    """Deterministic timestamp for tests."""
    return datetime(2026, 1, 1, 12, 0, 0)


@pytest.fixture
def mock_config():
    """Lightweight test configuration."""
    return {
        "debug": True,
        "database": {"url": "sqlite:///:memory:"},
        "api": {"timeout": 5, "retries": 1},
    }


@pytest.fixture
def test_database():
    """In-memory test database, torn down after test."""
    from myapp.database import create_engine, Base

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def sample_user_data():
    """Reusable sample user record."""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "age": 30,
        "role": "user",
    }


@pytest.fixture
def mock_external_api():
    """Pre-configured mock API client. See MOCKS.md Pattern 2."""
    from tests.fixtures.mock_api import MockAPIClient

    return MockAPIClient(responses={
        "/users/1": {"id": 1, "name": "John Doe"},
        "/users/2": {"id": 2, "name": "Jane Smith"},
    })
```

### Scope

By default, fixtures are function-scoped — torn down and rebuilt for each test. Override with `scope="module"` or `scope="session"` only when:
- The fixture is genuinely expensive to set up (real DB connection, large model load).
- The tests using the fixture don't mutate it.

A wrongly-scoped session fixture is a frequent source of cross-test contamination. When in doubt, function scope.

## Component-Specific Fixtures (nested `conftest.py`)

Nest a `conftest.py` inside a test subdirectory to add fixtures available only there.

`tests/integration/conftest.py`:

```python
"""Integration test fixtures (in addition to those from tests/conftest.py)."""

import pytest


@pytest.fixture
def integration_environment():
    """Full integration environment: DB + cache + queue."""
    db = setup_test_database()
    cache = setup_test_cache()
    queue = setup_test_queue()

    yield {"database": db, "cache": cache, "queue": queue}

    teardown_test_database(db)
    teardown_test_cache(cache)
    teardown_test_queue(queue)
```

Tests in `tests/integration/` get both root-level fixtures and these. Tests in `tests/unit/` only get root-level fixtures.

## Test Data Fixtures (`tests/fixtures/`)

For data that's too large or too structured for inline fixture functions.

`tests/fixtures/test_data.yaml`:

```yaml
users:
  - id: 1
    email: "alice@example.com"
    name: "Alice Anderson"
    role: "admin"
    created_at: "2026-01-01T00:00:00Z"

  - id: 2
    email: "bob@example.com"
    name: "Bob Brown"
    role: "user"
    created_at: "2026-01-02T00:00:00Z"

products:
  - id: 101
    name: "Widget"
    price: 19.99
    stock: 100

  - id: 102
    name: "Gadget"
    price: 49.99
    stock: 50
```

Load via fixture:

```python
import yaml
from pathlib import Path


@pytest.fixture
def test_data():
    """Load test data from YAML."""
    data_file = Path(__file__).parent / "fixtures" / "test_data.yaml"
    with open(data_file) as f:
        return yaml.safe_load(f)


def test_user_loading(test_data):
    users = test_data["users"]
    assert len(users) == 2
    assert users[0]["email"] == "alice@example.com"
```

## Generated Test Data

For tests that need realistic-looking data at scale, use `faker`:

```python
from faker import Faker


@pytest.fixture
def fake():
    """Faker instance — seeded for determinism."""
    f = Faker()
    f.seed_instance(42)
    return f


def test_with_generated_data(fake):
    """Test batch creation with realistic generated data."""
    users = [
        {
            "email": fake.email(),
            "name": fake.name(),
            "age": fake.random_int(18, 80),
        }
        for _ in range(100)
    ]

    result = batch_create_users(users)
    assert result.success_count == 100
```

**Always seed**. Unseeded Faker generates different data every run, which makes test failures hard to reproduce.

## Fixture Tips

- **Name fixtures by what they ARE, not what they do.** `test_database` not `setup_database`.
- **Yield for cleanup.** The `yield` keyword splits a fixture into "setup" and "teardown" — everything after `yield` runs after the test.
- **Compose fixtures.** A fixture can depend on other fixtures by taking them as parameters.
- **Parametrize at the test, not the fixture, when you need cartesian coverage.** Fixtures are for setup; `@pytest.mark.parametrize` is for varying inputs.

## See Also

- `MOCKS.md` — the mock classes you provide via these fixtures.
- `PATTERNS.md` — how fixtures connect to unit/integration/simulation tests.
- `TIERS.md` — where fixtures live for each tier.
