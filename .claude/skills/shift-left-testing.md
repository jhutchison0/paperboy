---
name: shift-left-testing
description: Comprehensive testing strategy with early validation, multi-tier tests, mocks, and simulated data
version: "1.0.0"
---

# Shift-Left Testing Strategy

**When to use**: Setting up test infrastructure, designing test strategy, implementing mocks, or ensuring comprehensive test coverage from day one.

---

## Overview

"Shift-left testing" means moving testing earlier in the development cycle - testing components before integration, testing with mocks before hardware, testing logic before dependencies exist. This skill provides a comprehensive testing strategy that enables development without waiting for external systems.

**Philosophy**: "Never skip tests because dependencies aren't ready. Mock what you don't have, test what you build, validate continuously."

---

## Quick Reference

### Test Pyramid

```
         /\
        /  \  E2E Tests (few, slow, complete system)
       /____\
      /      \
     / Integration \ (medium quantity, medium speed)
    /______________\
   /                \
  /   Unit Tests     \ (many, fast, isolated)
 /____________________\
```

### Test Tiers

| Tier | Speed | Scope | Dependencies | Quantity |
|------|-------|-------|--------------|----------|
| **Unit** | <1s | Single component | Mocked | Many (60-70%) |
| **Integration** | 1-10s | Component interaction | Some real, some mocked | Medium (20-30%) |
| **System** | 10-60s | End-to-end | Real or simulated | Few (5-10%) |
| **External** | >60s | With real external systems | Real APIs/hardware | Minimal (optional) |

### Test Organization

```
tests/
├── fixtures/           # Shared test data, mock objects
├── unit/              # Fast, isolated component tests
├── integration/       # Multi-component interaction tests
├── simulation/        # Digital twin / simulated environment tests
└── external/          # Real external system tests (optional)
```

---

## Core Principles

### 1. Test Independence

**Every test should be independent and isolated**:

✅ **Good**:
```python
def test_user_creation():
    """Test user creation in isolation."""
    db = create_test_database()  # Fresh DB
    user = create_user(db, "test@example.com")
    assert user.email == "test@example.com"
    cleanup_test_database(db)  # Clean up

def test_user_login():
    """Test user login in isolation."""
    db = create_test_database()  # Fresh DB
    user = create_user(db, "test@example.com")
    token = login_user(db, "test@example.com", "password")
    assert token is not None
    cleanup_test_database(db)
```

❌ **Bad**:
```python
# Shared state between tests!
TEST_DB = create_database()

def test_user_creation():
    user = create_user(TEST_DB, "test@example.com")  # Creates user
    assert user.email == "test@example.com"

def test_user_login():
    # Depends on previous test running first!
    token = login_user(TEST_DB, "test@example.com", "password")
    assert token is not None
```

### 2. Mock External Dependencies

**Never let tests depend on external systems** (APIs, databases, hardware):

```python
# Real implementation
class PaymentGateway:
    def charge(self, amount: float, card: str) -> str:
        # Makes actual API call to payment processor
        response = requests.post("https://api.stripe.com/charge", ...)
        return response.json()["transaction_id"]

# Mock for testing
class MockPaymentGateway:
    def charge(self, amount: float, card: str) -> str:
        # Simulates successful payment without API call
        return f"mock_txn_{random.randint(1000, 9999)}"

# Test uses mock
def test_purchase_flow():
    gateway = MockPaymentGateway()  # No real API calls
    order = create_order(items=[...], gateway=gateway)
    assert order.payment_status == "paid"
```

### 3. Test Early, Test Often

**Write tests BEFORE or ALONGSIDE code**:

```python
# 1. Write test first (TDD approach)
def test_calculate_discount():
    """Test discount calculation."""
    assert calculate_discount(100, 0.20) == 20.0
    assert calculate_discount(50, 0.10) == 5.0
    assert calculate_discount(100, 0.0) == 0.0

# 2. Then implement
def calculate_discount(price: float, discount_rate: float) -> float:
    """Calculate discount amount."""
    return price * discount_rate

# Test passes immediately!
```

### 4. Fail Fast, Fail Clear

**Tests should fail quickly with clear messages**:

✅ **Good**:
```python
def test_user_age_validation():
    """Test user age must be 18+."""
    with pytest.raises(ValueError, match="User must be at least 18 years old"):
        create_user(name="Test", age=17)
```

❌ **Bad**:
```python
def test_user_age():
    user = create_user(name="Test", age=17)
    assert user is not None  # Unclear what's being tested
```

---

## Test Directory Structure

### Root-Level Tests

**Structure**:

```
project/
├── src/
│   └── myapp/
│       ├── core/
│       ├── component_a/
│       └── component_b/
│
└── tests/                    # Root-level tests
    ├── __init__.py
    ├── conftest.py           # Shared pytest fixtures
    │
    ├── fixtures/             # Test data and mocks
    │   ├── __init__.py
    │   ├── mock_external_apis.py
    │   ├── mock_database.py
    │   ├── test_data.yaml
    │   └── sample_users.json
    │
    ├── unit/                 # Component unit tests
    │   ├── __init__.py
    │   ├── test_component_a.py
    │   ├── test_component_b.py
    │   └── test_core_utils.py
    │
    ├── integration/          # Multi-component tests
    │   ├── __init__.py
    │   ├── test_api_integration.py
    │   ├── test_database_operations.py
    │   └── test_end_to_end.py
    │
    ├── simulation/           # Simulated environment tests
    │   ├── __init__.py
    │   ├── test_simulated_workflow.py
    │   └── test_failure_scenarios.py
    │
    └── external/             # Real external system tests (optional)
        ├── __init__.py
        ├── test_live_api.py
        └── test_production_db.py
```

**When to use root-level tests**:
- ✅ Always use for unit tests
- ✅ Always use for integration tests
- ✅ Use for system-wide concerns
- ✅ Use when testing multiple components together

### Component-Level Tests

**Structure**:

```
src/myapp/component_a/
├── __init__.py
├── module1.py
├── module2.py
├── submodule/
│   ├── __init__.py
│   └── feature.py
│
└── tests/                    # Component-specific tests
    ├── __init__.py
    ├── test_module1.py
    ├── test_module2.py
    └── test_submodule_feature.py
```

**When to use component-level tests**:
- ✅ Large, complex component with many submodules
- ✅ Component developed by separate team
- ✅ Component with component-specific test fixtures
- ✅ Component that may be extracted into separate package

**Decision Rule**:
```
if component_size > 1000 lines OR
   component_complexity = high OR
   component_team = separate:
    use component-level tests
else:
    use root-level tests
```

---

## Unit Testing

### What to Test

**Test at the smallest possible unit**:

```python
# Component being tested
class OrderCalculator:
    def __init__(self, tax_rate: float = 0.08):
        self.tax_rate = tax_rate

    def calculate_total(self, subtotal: float, discount: float = 0.0) -> float:
        """Calculate order total with tax and discount."""
        discounted = subtotal - discount
        tax = discounted * self.tax_rate
        return discounted + tax

# Unit tests
def test_calculate_total_no_discount():
    """Test total calculation without discount."""
    calc = OrderCalculator(tax_rate=0.10)
    total = calc.calculate_total(subtotal=100.0)
    assert total == 110.0  # 100 + 10% tax

def test_calculate_total_with_discount():
    """Test total calculation with discount."""
    calc = OrderCalculator(tax_rate=0.10)
    total = calc.calculate_total(subtotal=100.0, discount=20.0)
    assert total == 88.0  # (100 - 20) + 10% tax = 80 + 8

def test_calculate_total_zero_subtotal():
    """Test edge case: zero subtotal."""
    calc = OrderCalculator()
    total = calc.calculate_total(subtotal=0.0)
    assert total == 0.0

def test_calculate_total_negative_discount():
    """Test edge case: negative discount (error)."""
    calc = OrderCalculator()
    with pytest.raises(ValueError, match="Discount cannot be negative"):
        calc.calculate_total(subtotal=100.0, discount=-10.0)
```

### Testing Strategy

**Cover these scenarios**:

1. **Happy path** - Normal, expected usage
2. **Edge cases** - Boundary conditions (0, empty, null)
3. **Error cases** - Invalid input, exceptions
4. **State transitions** - Object state changes
5. **Side effects** - Database writes, API calls (mocked)

### Mock External Dependencies

**Example: Testing a service that calls an API**:

```python
# Service implementation
class WeatherService:
    def __init__(self, api_client):
        self.api = api_client

    def get_temperature(self, city: str) -> float:
        """Get current temperature for city."""
        response = self.api.get(f"/weather/{city}")
        return response["temperature"]

# Mock API client
class MockAPIClient:
    def __init__(self, responses: dict):
        self.responses = responses

    def get(self, endpoint: str) -> dict:
        """Return mocked response."""
        if endpoint in self.responses:
            return self.responses[endpoint]
        raise ValueError(f"No mock response for {endpoint}")

# Unit test
def test_get_temperature():
    """Test temperature retrieval with mocked API."""
    mock_api = MockAPIClient(responses={
        "/weather/Seattle": {"temperature": 65.0, "conditions": "cloudy"}
    })

    service = WeatherService(api_client=mock_api)
    temp = service.get_temperature("Seattle")

    assert temp == 65.0  # No real API call made!
```

---

## Integration Testing

### What to Test

**Test component interactions and data flow**:

```python
# Integration test: API → Service → Database
@pytest.mark.integration
def test_user_registration_flow():
    """Test complete user registration flow."""
    # Setup
    test_db = create_test_database()
    email_service = MockEmailService()  # Mock external email
    api = UserAPI(database=test_db, email=email_service)

    # Execute
    response = api.register_user(
        email="test@example.com",
        password="secure_password_123"
    )

    # Assert
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

    # Verify database
    user = test_db.get_user("test@example.com")
    assert user is not None
    assert user.email_verified == False

    # Verify email sent
    assert len(email_service.sent_emails) == 1
    assert "verify your email" in email_service.sent_emails[0].body

    # Cleanup
    cleanup_test_database(test_db)
```

### Integration Test Patterns

**Pattern 1: Partial Mocking**

Mock external dependencies, use real internal components:

```python
def test_payment_processing():
    """Test payment flow with mocked payment gateway."""
    # Real components
    db = create_test_database()
    order_service = OrderService(db)

    # Mock external
    payment_gateway = MockPaymentGateway()

    # Test flow
    order = order_service.create_order(items=[...])
    result = order_service.process_payment(order, payment_gateway)

    assert result.success
    assert order.status == "paid"
```

**Pattern 2: In-Memory Alternatives**

Use fast in-memory versions for integration tests:

```python
@pytest.fixture
def test_database():
    """In-memory SQLite database for fast tests."""
    db = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(db)
    yield db
    db.dispose()

def test_user_crud_operations(test_database):
    """Test user CRUD with in-memory DB."""
    # Fast! No disk I/O
    user = create_user(test_database, "test@example.com")
    assert get_user(test_database, user.id) == user
    update_user(test_database, user.id, name="Updated")
    delete_user(test_database, user.id)
    assert get_user(test_database, user.id) is None
```

---

## Simulation Testing

### Digital Twin / Simulated Environment

**When external systems don't exist yet, simulate them**:

```python
class SimulatedEnvironment:
    """
    Simulates the complete system environment.

    Perfect for "shift-left" testing - test integration logic
    before external systems are ready!
    """

    def __init__(self, fidelity: str = "realistic"):
        """
        Initialize simulated environment.

        Args:
            fidelity: "perfect" (no noise), "realistic" (with noise),
                     "adversarial" (failures and edge cases)
        """
        self.fidelity = fidelity
        self.time = 0.0
        self.entities = {}

    def add_entity(self, entity_id: str, initial_state: dict):
        """Add entity to simulation."""
        self.entities[entity_id] = initial_state

    def step(self, dt: float):
        """Advance simulation by dt seconds."""
        self.time += dt

        # Update entity states
        for entity_id, state in self.entities.items():
            self._update_entity(entity_id, state, dt)

        # Inject failures in adversarial mode
        if self.fidelity == "adversarial":
            self._inject_failures()

    def read_sensor(self, sensor_id: str) -> dict:
        """Read sensor value with fidelity-appropriate noise."""
        true_value = self._get_true_value(sensor_id)

        if self.fidelity == "perfect":
            return true_value
        elif self.fidelity == "realistic":
            return self._add_noise(true_value)
        else:  # adversarial
            if random.random() < 0.05:  # 5% failure rate
                return None  # Sensor dropout
            return self._add_noise(true_value)

# Usage in tests
@pytest.mark.simulation
def test_tracking_with_simulation():
    """Test tracking logic with simulated target."""
    env = SimulatedEnvironment(fidelity="realistic")
    env.add_entity("target_001", {"x": 0.0, "y": 5.0, "velocity": 1.0})

    tracker = TargetTracker()

    # Simulate 10 seconds
    for _ in range(100):
        env.step(dt=0.1)  # 100ms steps
        sensor_data = env.read_sensor("radar")
        tracker.update(sensor_data)

    # Verify tracking accuracy
    estimated_pos = tracker.get_position("target_001")
    true_pos = env.entities["target_001"]
    assert abs(estimated_pos.x - true_pos["x"]) < 0.5  # Within 0.5m
```

### Benefits of Simulation Testing

**Why simulate?**

1. **Test before dependencies exist** - Don't wait for APIs, hardware, or external systems
2. **Test edge cases safely** - Simulate failures, extreme conditions, rare scenarios
3. **Test at scale** - Simulate thousands of users, millions of requests
4. **Test deterministically** - Control time, randomness, network conditions
5. **Test continuously** - Fast enough for CI/CD pipelines

---

## Test Fixtures

### Shared Fixtures

**File**: `tests/conftest.py`

```python
"""
Root test configuration and shared fixtures.

Fixtures defined here are available to all tests.
"""

import pytest
from datetime import datetime
import tempfile
import shutil

@pytest.fixture
def temp_directory():
    """Create temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)  # Cleanup after test

@pytest.fixture
def current_timestamp():
    """Provide consistent timestamp for tests."""
    return datetime(2025, 1, 1, 12, 0, 0)

@pytest.fixture
def mock_config():
    """Test configuration."""
    return {
        "debug": True,
        "database": {"url": "sqlite:///:memory:"},
        "api": {"timeout": 5, "retries": 1}
    }

@pytest.fixture
def test_database():
    """In-memory test database."""
    from myapp.database import create_engine, Base

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    yield engine

    engine.dispose()

@pytest.fixture
def sample_user_data():
    """Sample user data for tests."""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "age": 30,
        "role": "user"
    }

@pytest.fixture
def mock_external_api():
    """Mock external API client."""
    from tests.fixtures.mock_api import MockAPIClient

    return MockAPIClient(responses={
        "/users/1": {"id": 1, "name": "John Doe"},
        "/users/2": {"id": 2, "name": "Jane Smith"}
    })
```

### Component-Specific Fixtures

**File**: `tests/integration/conftest.py`

```python
"""Integration test fixtures."""

import pytest

@pytest.fixture
def integration_environment():
    """Setup complete integration environment."""
    db = setup_test_database()
    cache = setup_test_cache()
    queue = setup_test_queue()

    yield {
        "database": db,
        "cache": cache,
        "queue": queue
    }

    # Cleanup
    teardown_test_database(db)
    teardown_test_cache(cache)
    teardown_test_queue(queue)
```

---

## Mock Implementation Patterns

### Pattern 1: Simple Mock

**For simple external services**:

```python
class MockEmailService:
    """Mock email service for testing."""

    def __init__(self):
        self.sent_emails = []

    def send_email(self, to: str, subject: str, body: str):
        """Record email instead of sending."""
        self.sent_emails.append({
            "to": to,
            "subject": subject,
            "body": body,
            "sent_at": datetime.now()
        })

# Usage
def test_password_reset():
    email_service = MockEmailService()
    auth_service = AuthService(email=email_service)

    auth_service.request_password_reset("user@example.com")

    assert len(email_service.sent_emails) == 1
    assert "reset your password" in email_service.sent_emails[0]["body"]
```

### Pattern 2: Configurable Mock

**For APIs with multiple endpoints**:

```python
class MockAPIClient:
    """Configurable mock for API testing."""

    def __init__(self, responses: dict = None):
        """
        Initialize mock with predefined responses.

        Args:
            responses: Dict mapping endpoints to response data
        """
        self.responses = responses or {}
        self.call_history = []

    def get(self, endpoint: str) -> dict:
        """Mock GET request."""
        self.call_history.append(("GET", endpoint))

        if endpoint in self.responses:
            return self.responses[endpoint]

        raise ValueError(f"No mock response configured for GET {endpoint}")

    def post(self, endpoint: str, data: dict) -> dict:
        """Mock POST request."""
        self.call_history.append(("POST", endpoint, data))

        response_key = f"POST:{endpoint}"
        if response_key in self.responses:
            return self.responses[response_key]

        return {"success": True}  # Default success

# Usage
def test_api_integration():
    mock_api = MockAPIClient(responses={
        "/users/123": {"id": 123, "name": "Test User"},
        "POST:/users": {"id": 456, "name": "New User"}
    })

    service = UserService(api=mock_api)

    user = service.get_user(123)
    assert user["name"] == "Test User"

    new_user = service.create_user({"name": "New User"})
    assert new_user["id"] == 456

    # Verify calls made
    assert len(mock_api.call_history) == 2
    assert mock_api.call_history[0] == ("GET", "/users/123")
```

### Pattern 3: Realistic Mock with Behavior

**For complex simulations**:

```python
class MockSensorWithNoise:
    """
    Realistic sensor mock with configurable noise and failures.

    Perfect for testing robustness to real-world sensor behavior!
    """

    def __init__(self, noise_std: float = 0.1, failure_rate: float = 0.01):
        """
        Initialize mock sensor.

        Args:
            noise_std: Standard deviation of measurement noise
            failure_rate: Probability of sensor dropout (0.0 to 1.0)
        """
        self.noise_std = noise_std
        self.failure_rate = failure_rate
        self.true_value = 0.0

    def set_true_value(self, value: float):
        """Set true sensor value (for test control)."""
        self.true_value = value

    def read(self) -> Optional[float]:
        """Read sensor with realistic noise and failures."""
        # Simulate sensor dropout
        if random.random() < self.failure_rate:
            return None

        # Add Gaussian noise
        noise = random.gauss(0, self.noise_std)
        return self.true_value + noise

# Usage
def test_sensor_filtering():
    """Test sensor filter handles noise and dropouts."""
    sensor = MockSensorWithNoise(noise_std=0.5, failure_rate=0.1)
    filter = KalmanFilter()

    sensor.set_true_value(10.0)

    # Take 100 readings
    estimates = []
    for _ in range(100):
        reading = sensor.read()
        if reading is not None:
            filter.update(reading)
            estimates.append(filter.get_estimate())

    # Filter should converge to true value despite noise
    final_estimate = estimates[-1]
    assert abs(final_estimate - 10.0) < 0.2  # Within 0.2 of true value
```

---

## Test Data Management

### Test Data Fixtures

**File**: `tests/fixtures/test_data.yaml`

```yaml
# Sample test data
users:
  - id: 1
    email: "alice@example.com"
    name: "Alice Anderson"
    role: "admin"
    created_at: "2025-01-01T00:00:00Z"

  - id: 2
    email: "bob@example.com"
    name: "Bob Brown"
    role: "user"
    created_at: "2025-01-02T00:00:00Z"

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

**Loading in tests**:

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
    """Test using fixture data."""
    users = test_data["users"]
    assert len(users) == 2
    assert users[0]["email"] == "alice@example.com"
```

### Generated Test Data

**For large-scale testing**:

```python
from faker import Faker

@pytest.fixture
def fake():
    """Faker instance for generating test data."""
    return Faker()

def test_with_generated_data(fake):
    """Test with realistic generated data."""
    # Generate 100 fake users
    users = [
        {
            "email": fake.email(),
            "name": fake.name(),
            "age": fake.random_int(18, 80)
        }
        for _ in range(100)
    ]

    # Test batch operations
    result = batch_create_users(users)
    assert result.success_count == 100
```

---

## Test Organization Best Practices

### Naming Conventions

**Test files**: `test_*.py` or `*_test.py`
```
test_user_service.py    ✅
test_api.py             ✅
user_service_test.py    ✅
tests.py                ❌ (too generic)
```

**Test functions**: `test_*`
```python
def test_user_creation():                       ✅
def test_user_creation_with_invalid_email():    ✅
def test_edge_case_empty_name():                ✅
def check_user_creation():                      ❌ (won't be discovered)
```

**Test classes**: `Test*`
```python
class TestUserService:                          ✅
class TestAuthenticationFlow:                   ✅
class UserTests:                                ❌ (won't be discovered)
```

### Test Markers

**Use pytest markers to categorize tests**:

```python
import pytest

@pytest.mark.unit
def test_calculation():
    """Fast unit test."""
    assert calculate(2, 3) == 5

@pytest.mark.integration
def test_database_query():
    """Integration test with database."""
    result = db.query("SELECT * FROM users")
    assert len(result) > 0

@pytest.mark.slow
def test_long_running_process():
    """Slow test (>10s)."""
    result = process_large_dataset()
    assert result.success

@pytest.mark.external
@pytest.mark.skipif(not os.getenv("RUN_EXTERNAL_TESTS"), reason="External tests disabled")
def test_live_api():
    """Test with real external API."""
    response = api.call_real_endpoint()
    assert response.status_code == 200
```

**Running specific test categories**:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run all except slow tests
pytest -m "not slow"

# Run unit and integration (not external)
pytest -m "unit or integration"
```

---

## Continuous Integration (CI/CD)

### GitHub Actions Example

**File**: `.github/workflows/tests.yml`

```yaml
name: Tests

on:
  push:
    branches: [ main, dev-* ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=src --cov-report=xml

    - name: Run integration tests
      run: |
        pytest tests/integration/ -v

    - name: Run simulation tests
      run: |
        pytest tests/simulation/ -v

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
```

### Test Coverage Requirements

**Set coverage thresholds**:

```ini
# .coveragerc or pyproject.toml
[coverage:run]
source = src/
omit =
    */tests/*
    */test_*.py
    */__pycache__/*

[coverage:report]
fail_under = 80  # Require 80% coverage
show_missing = true
```

---

## Testing Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Tests Depend on Execution Order

```python
# BAD: Tests must run in specific order
def test_01_create_user():
    global USER_ID
    USER_ID = create_user("test@example.com")

def test_02_update_user():
    update_user(USER_ID, name="Updated")  # Depends on test_01
```

**Fix**: Make each test independent.

### ❌ Anti-Pattern 2: Testing Implementation, Not Behavior

```python
# BAD: Testing internal implementation
def test_user_password_hashing():
    user = User("test@example.com", "password")
    assert user._hashed_password.startswith("$2b$")  # Tests bcrypt internal
```

**Fix**: Test behavior (can user login?), not implementation (hash format).

### ❌ Anti-Pattern 3: Slow Tests in CI

```python
# BAD: Slow test that hits real API in CI
def test_api_integration():
    time.sleep(30)  # Wait for eventual consistency
    response = real_api.call()  # Real API call
    assert response.success
```

**Fix**: Use mocks in CI, save external tests for manual runs.

### ❌ Anti-Pattern 4: Brittle Tests

```python
# BAD: Test breaks on any text change
def test_error_message():
    with pytest.raises(ValueError, match="Invalid email address: test@"):
        validate_email("test@")
```

**Fix**: Test message contains key info, not exact text.

---

## Testing Checklist

### Before Committing Code

- [ ] All new code has corresponding tests
- [ ] Tests pass locally (`pytest`)
- [ ] Tests are independent (can run in any order)
- [ ] External dependencies are mocked
- [ ] Test coverage meets threshold (e.g., 80%)
- [ ] Tests are fast (<1s for unit tests)
- [ ] Tests have clear, descriptive names
- [ ] Edge cases and error cases are tested

### Before Merging Pull Request

- [ ] All CI tests pass
- [ ] Integration tests pass
- [ ] No test skips without explanation
- [ ] Coverage report reviewed
- [ ] New fixtures documented
- [ ] Test data committed (if applicable)

### Periodic Review

- [ ] Remove obsolete tests
- [ ] Update test data
- [ ] Refactor duplicated test code
- [ ] Review slow tests (optimize or mark)
- [ ] Update mocks to match real system changes

---

## Examples by Domain

### Web API Testing

```python
@pytest.mark.integration
def test_user_registration_api():
    """Test user registration endpoint."""
    client = TestClient(app)

    response = client.post("/api/users/register", json={
        "email": "test@example.com",
        "password": "SecurePassword123"
    })

    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
    assert "id" in response.json()
```

### Data Pipeline Testing

```python
def test_data_transformation():
    """Test data transformation step."""
    input_data = pd.DataFrame({
        "name": ["Alice", "Bob"],
        "age": [25, 30]
    })

    result = transform_data(input_data)

    assert len(result) == 2
    assert "age_group" in result.columns
    assert result["age_group"].tolist() == ["20-30", "30-40"]
```

### ML Model Testing

```python
def test_model_prediction():
    """Test model prediction with test data."""
    model = load_test_model()
    test_input = np.array([[1.0, 2.0, 3.0]])

    prediction = model.predict(test_input)

    assert prediction.shape == (1,)
    assert 0 <= prediction[0] <= 1  # Probability output
```

---

## References

### Testing Frameworks
- [pytest](https://docs.pytest.org/) - Python testing framework
- [unittest](https://docs.python.org/3/library/unittest.html) - Python standard library
- [Jest](https://jestjs.io/) - JavaScript testing
- [JUnit](https://junit.org/) - Java testing

### Test Doubles (Mocks, Stubs, Fakes)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html) - Python mocking
- [pytest-mock](https://github.com/pytest-dev/pytest-mock/) - pytest plugin
- [Faker](https://faker.readthedocs.io/) - Generate test data

### Coverage Tools
- [coverage.py](https://coverage.readthedocs.io/) - Python coverage
- [pytest-cov](https://pytest-cov.readthedocs.io/) - pytest plugin
- [Codecov](https://about.codecov.io/) - Coverage reporting

### Best Practices
- [Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html) - Martin Fowler
- [Testing Best Practices](https://testdriven.io/blog/testing-best-practices/) - TestDriven.io

---

**Maintained by**: Shift-Left Testing Skill
**Version**: 1.0.0
**Last Updated**: 2025-11-14
