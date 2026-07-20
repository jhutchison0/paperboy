# PATTERNS — Unit, Integration, and Simulation Patterns

Sidecar to `SKILL.md`. Worked examples for each tier. Read when writing a new test and you're not sure what shape it should take.

## Unit Testing

### What to Test

Test at the smallest possible unit: a function, a method, a small class. Mock everything it depends on.

```python
class OrderCalculator:
    def __init__(self, tax_rate: float = 0.08):
        self.tax_rate = tax_rate

    def calculate_total(self, subtotal: float, discount: float = 0.0) -> float:
        if discount < 0:
            raise ValueError("Discount cannot be negative")
        discounted = subtotal - discount
        tax = discounted * self.tax_rate
        return discounted + tax

# Unit tests
def test_calculate_total_no_discount():
    calc = OrderCalculator(tax_rate=0.10)
    assert calc.calculate_total(subtotal=100.0) == 110.0

def test_calculate_total_with_discount():
    calc = OrderCalculator(tax_rate=0.10)
    assert calc.calculate_total(subtotal=100.0, discount=20.0) == 88.0

def test_calculate_total_zero_subtotal():
    calc = OrderCalculator()
    assert calc.calculate_total(subtotal=0.0) == 0.0

def test_calculate_total_negative_discount_raises():
    calc = OrderCalculator()
    with pytest.raises(ValueError, match="Discount cannot be negative"):
        calc.calculate_total(subtotal=100.0, discount=-10.0)
```

Bare `==` passes in these examples only because the chosen decimals happen to come out exact in binary floating point; default to `pytest.approx` for computed floats (see `NUMERIC.md`).

### Coverage Strategy

For each behavior under test, cover these scenarios:

1. **Happy path** — normal, expected usage.
2. **Edge cases** — boundaries (0, empty, null, max).
3. **Error cases** — invalid input, exceptions.
4. **State transitions** — object state changes (if stateful).
5. **Side effects** — database writes, API calls (mocked).

Don't test more than these unless the code has a specific reason. Over-testing is its own anti-pattern.

### Mocking External Dependencies in Unit Tests

The whole point of unit tests is *not* hitting external systems. See `MOCKS.md` for the mock patterns; here's the shape:

```python
class WeatherService:
    def __init__(self, api_client):
        self.api = api_client

    def get_temperature(self, city: str) -> float:
        response = self.api.get(f"/weather/{city}")
        return response["temperature"]

class MockAPIClient:
    def __init__(self, responses: dict):
        self.responses = responses

    def get(self, endpoint: str) -> dict:
        if endpoint in self.responses:
            return self.responses[endpoint]
        raise ValueError(f"No mock response for {endpoint}")

def test_get_temperature():
    mock_api = MockAPIClient(responses={
        "/weather/Seattle": {"temperature": 65.0, "conditions": "cloudy"}
    })
    service = WeatherService(api_client=mock_api)
    assert service.get_temperature("Seattle") == 65.0
```

The dependency (`api_client`) is injected at construction. Real code passes the real client; tests pass a mock. This is *constructor injection*: the simplest dependency injection pattern Python supports.

## Integration Testing

### What to Test

Component interactions and data flow. You're verifying that pieces compose correctly, not that any one piece is correct in isolation.

```python
@pytest.mark.integration
def test_user_registration_flow():
    """Test complete user registration flow."""
    test_db = create_test_database()
    email_service = MockEmailService()
    api = UserAPI(database=test_db, email=email_service)

    response = api.register_user(
        email="test@example.com",
        password="secure_password_123"
    )

    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

    # Verify database side effect
    user = test_db.get_user("test@example.com")
    assert user is not None
    assert user.email_verified is False

    # Verify email side effect
    assert len(email_service.sent_emails) == 1
    assert "verify your email" in email_service.sent_emails[0].body

    cleanup_test_database(test_db)
```

### Pattern 1: Partial Mocking

Real internal components, mocked external systems. The most common integration pattern.

```python
def test_payment_processing():
    db = create_test_database()                # Real (in-memory)
    order_service = OrderService(db)           # Real
    payment_gateway = MockPaymentGateway()     # Mock (external)

    order = order_service.create_order(items=[...])
    result = order_service.process_payment(order, payment_gateway)

    assert result.success
    assert order.status == "paid"
```

### Pattern 2: In-Memory Alternatives

Use fast in-memory versions of stateful dependencies for integration tests.

```python
@pytest.fixture
def test_database():
    """In-memory SQLite database for fast tests."""
    db = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(db)
    yield db
    db.dispose()

def test_user_crud_operations(test_database):
    user = create_user(test_database, "test@example.com")
    assert get_user(test_database, user.id) == user
    update_user(test_database, user.id, name="Updated")
    delete_user(test_database, user.id)
    assert get_user(test_database, user.id) is None
```

SQLite-in-memory is the workhorse: drop-in for most SQL workloads in tests. For Redis, use `fakeredis`. For S3, use `moto`.

## Simulation Testing

### Digital Twin / Simulated Environment

When the external system doesn't exist yet (or is too expensive to use in tests), simulate it.

```python
class SimulatedEnvironment:
    """Simulate the complete external environment for shift-left testing."""

    def __init__(self, fidelity: str = "realistic"):
        """
        Args:
            fidelity: "perfect" (no noise), "realistic" (with noise),
                      "adversarial" (failures + edge cases)
        """
        self.fidelity = fidelity
        self.time = 0.0
        self.entities = {}

    def add_entity(self, entity_id: str, initial_state: dict):
        self.entities[entity_id] = initial_state

    def step(self, dt: float):
        self.time += dt
        for entity_id, state in self.entities.items():
            self._update_entity(entity_id, state, dt)
        if self.fidelity == "adversarial":
            self._inject_failures()

    def read_sensor(self, sensor_id: str) -> Optional[dict]:
        true_value = self._get_true_value(sensor_id)
        if self.fidelity == "perfect":
            return true_value
        elif self.fidelity == "realistic":
            return self._add_noise(true_value)
        else:  # adversarial
            if random.random() < 0.05:
                return None  # Sensor dropout
            return self._add_noise(true_value)

@pytest.mark.simulation
def test_tracking_with_simulation():
    env = SimulatedEnvironment(fidelity="realistic")
    env.add_entity("target_001", {"x": 0.0, "y": 5.0, "velocity": 1.0})

    tracker = TargetTracker()
    for _ in range(100):
        env.step(dt=0.1)
        sensor_data = env.read_sensor("radar")
        tracker.update(sensor_data)

    estimated_pos = tracker.get_position("target_001")
    true_pos = env.entities["target_001"]
    assert abs(estimated_pos.x - true_pos["x"]) < 0.5
```

### Why Simulate?

- **Test before dependencies exist.** Don't wait for the real API, hardware, or service.
- **Test edge cases safely.** Simulate failures, extreme conditions, rare scenarios.
- **Test at scale.** Simulate thousands of users, millions of requests.
- **Test deterministically.** Control time, randomness, network conditions.
- **Test continuously.** Fast enough for CI/CD.

The cost is the simulator itself. Keep it small, prove it matches real behavior, and revisit it when the real system arrives.

## See Also

- `MOCKS.md` — the three mock patterns referenced by unit and integration patterns.
- `FIXTURES.md` — how `conftest.py` and `tests/fixtures/` set up the dependencies used here.
- `VERTICAL-SLICING.md` — the *rhythm* of writing these tests one at a time.
