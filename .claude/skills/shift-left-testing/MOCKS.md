# MOCKS — Mock Implementation Patterns

Sidecar to `SKILL.md`. Three mock patterns ordered by complexity. Use the simplest one that captures the behavior your test needs to verify.

## Pattern 1: Simple Mock

For external services with one or two methods where you only need to verify *that* they were called.

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
            "sent_at": datetime.now(),
        })

# Usage
def test_password_reset():
    email_service = MockEmailService()
    auth_service = AuthService(email=email_service)

    auth_service.request_password_reset("user@example.com")

    assert len(email_service.sent_emails) == 1
    assert "reset your password" in email_service.sent_emails[0]["body"]
```

**When this is enough**: the mock only needs to capture inputs. The test verifies the inputs match expectations.

## Pattern 2: Configurable Mock

For APIs with multiple endpoints or methods where the response shape matters to the test.

```python
class MockAPIClient:
    """Configurable mock for API testing."""

    def __init__(self, responses: dict = None):
        """
        Args:
            responses: Dict mapping endpoints to response data.
                       Keys for POST use "POST:{endpoint}" form.
        """
        self.responses = responses or {}
        self.call_history = []

    def get(self, endpoint: str) -> dict:
        self.call_history.append(("GET", endpoint))
        if endpoint in self.responses:
            return self.responses[endpoint]
        raise ValueError(f"No mock response configured for GET {endpoint}")

    def post(self, endpoint: str, data: dict) -> dict:
        self.call_history.append(("POST", endpoint, data))
        response_key = f"POST:{endpoint}"
        if response_key in self.responses:
            return self.responses[response_key]
        return {"success": True}  # Default success

# Usage
def test_api_integration():
    mock_api = MockAPIClient(responses={
        "/users/123": {"id": 123, "name": "Test User"},
        "POST:/users": {"id": 456, "name": "New User"},
    })

    service = UserService(api=mock_api)

    user = service.get_user(123)
    assert user["name"] == "Test User"

    new_user = service.create_user({"name": "New User"})
    assert new_user["id"] == 456

    # Verify call sequence
    assert len(mock_api.call_history) == 2
    assert mock_api.call_history[0] == ("GET", "/users/123")
```

**When this is right**: you need to control responses by endpoint, you want to verify call history, and the real API has more than one or two operations.

**`call_history` tip**: log the calls verbatim. Tests that depend on call order are brittle; tests that just check "did this specific call happen at all" are durable.

## Pattern 3: Realistic Mock with Behavior

For tests that need to exercise behavior under realistic conditions (noise, latency, intermittent failures).

```python
class MockSensorWithNoise:
    """
    Realistic sensor mock with configurable noise and failures.
    Use for testing robustness to real-world sensor behavior.
    """

    def __init__(self, noise_std: float = 0.1, failure_rate: float = 0.01):
        """
        Args:
            noise_std: Standard deviation of measurement noise.
            failure_rate: Probability of sensor dropout (0.0 to 1.0).
        """
        self.noise_std = noise_std
        self.failure_rate = failure_rate
        self.true_value = 0.0

    def set_true_value(self, value: float):
        """Set the underlying true value the sensor measures."""
        self.true_value = value

    def read(self) -> Optional[float]:
        """Read with realistic noise + dropout."""
        if random.random() < self.failure_rate:
            return None  # Sensor dropout
        noise = random.gauss(0, self.noise_std)
        return self.true_value + noise

# Usage
def test_sensor_filtering():
    """Filter should converge to true value despite noise and dropouts."""
    sensor = MockSensorWithNoise(noise_std=0.5, failure_rate=0.1)
    kalman = KalmanFilter()

    sensor.set_true_value(10.0)

    estimates = []
    for _ in range(100):
        reading = sensor.read()
        if reading is not None:
            kalman.update(reading)
            estimates.append(kalman.get_estimate())

    final_estimate = estimates[-1]
    assert abs(final_estimate - 10.0) < 0.2  # Within 0.2 of true value
```

**When this is right**: you're testing robustness, error recovery, or statistical behavior. The simpler patterns can't generate the conditions you need to verify.

**Determinism warning**: seed the random number generator in test setup, or your test will flake. `random.seed(42)` at the top of the test method (or in a fixture) is the easy fix.

## Choosing Between Patterns

| You need to... | Pattern |
|---|---|
| Verify a call happened with specific arguments | Pattern 1 |
| Stub a multi-endpoint API with controlled responses | Pattern 2 |
| Test behavior under noise, failure, or realistic conditions | Pattern 3 |
| Verify the exact sequence of calls | Pattern 2 (with `call_history`) |
| Test the same component against multiple response shapes | Pattern 2 with parameterized tests |

When in doubt, start with Pattern 1. Move up only when the test you're writing genuinely needs more.

## Anti-Patterns

- **Using `unittest.mock.Mock()` for everything.** It works, but it makes tests cryptic: any attribute access returns another Mock, so typos pass silently. Prefer explicit mock classes.
- **Mocking the thing under test.** If you find yourself mocking the very class your test is supposed to verify, the test isn't testing anything. Step back.
- **Asserting on the mock's internal state instead of the system's behavior.** "The mock's `_called` attribute is True" is a weaker test than "the user was created in the database."
- **Letting the mock drift from the real interface.** Mocks should match the real type signature. If the real API adds a parameter, the mock should too; otherwise tests pass with code that's broken in production. (Tools like `unittest.mock.create_autospec` enforce this.)

## See Also

- `PATTERNS.md` — how mocks fit into unit and integration test patterns.
- `FIXTURES.md` — how to provide mock instances via `conftest.py` fixtures.
- `ANTIPATTERNS.md` — broader testing anti-patterns including mock-related ones.
