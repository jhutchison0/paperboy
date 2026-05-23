# ANTIPATTERNS — What to Avoid + Pre-Commit Checklist

Sidecar to `SKILL.md`. The mistakes that look productive but corrode the test suite. Includes the pre-commit and pre-merge checklists.

## Anti-Pattern 1: Tests Depend on Execution Order

```python
# BAD — tests must run in specific order
USER_ID = None

def test_01_create_user():
    global USER_ID
    USER_ID = create_user("test@example.com").id

def test_02_update_user():
    update_user(USER_ID, name="Updated")  # Depends on test_01
```

**Why it's bad**: a single-test re-run fails. Reordering tests fails. Parallel execution fails. The test suite has implicit state that isn't part of any test.

**Fix**: each test creates the state it needs:

```python
def test_create_user():
    user = create_user("test@example.com")
    assert user.email == "test@example.com"

def test_update_user():
    user = create_user("test@example.com")  # Fresh state
    updated = update_user(user.id, name="Updated")
    assert updated.name == "Updated"
```

If creation is expensive enough that you want to share it, use a fixture — but the fixture must teardown cleanly so each test sees fresh state.

## Anti-Pattern 2: Testing Implementation, Not Behavior

```python
# BAD — coupled to bcrypt implementation
def test_user_password_hashing():
    user = User("test@example.com", "password")
    assert user._hashed_password.startswith("$2b$")
```

**Why it's bad**: the test breaks the day someone switches from bcrypt to argon2, even though the user-facing behavior didn't change. The test asserts on *how* the password is stored, not *that* the user can authenticate.

**Fix**: test behavior through the public interface:

```python
def test_user_can_authenticate_after_setting_password():
    user = User("test@example.com")
    user.set_password("correct_password")

    assert user.authenticate("correct_password") is True
    assert user.authenticate("wrong_password") is False
```

See `VERTICAL-SLICING.md` for the core principle this anti-pattern violates.

## Anti-Pattern 3: Slow Tests in CI

```python
# BAD — sleeps in CI
def test_api_integration():
    time.sleep(30)  # Wait for eventual consistency
    response = real_api.call()
    assert response.success
```

**Why it's bad**: every CI run pays the 30-second cost. Multiplied across a suite, CI becomes the bottleneck for development velocity. Also, real API calls in CI introduce flakiness (network blips, rate limits, third-party downtime).

**Fix**: mock the API in CI; run real-API tests separately.

```python
@pytest.mark.unit
def test_api_integration():
    mock_api = MockAPIClient(responses={"/data": {"success": True}})
    response = service.call_with_client(mock_api)
    assert response.success

@pytest.mark.external
@pytest.mark.skipif(not os.getenv("RUN_EXTERNAL_TESTS"), reason="opt-in")
def test_api_integration_live():
    response = real_api.call()
    assert response.success
```

See `CI.md` for the matching CI configuration.

## Anti-Pattern 4: Brittle Tests

```python
# BAD — breaks on any text change
def test_error_message():
    with pytest.raises(ValueError, match="Invalid email address: test@"):
        validate_email("test@")
```

**Why it's bad**: a copy-edit to the error message ("Invalid email address: 'test@'") breaks the test, even though the error behavior is unchanged.

**Fix**: assert on the structural aspects, not the exact prose:

```python
def test_error_message():
    with pytest.raises(ValueError, match="Invalid email"):
        validate_email("test@")
```

Or assert on a stable error code if your domain has one:

```python
def test_error_code():
    with pytest.raises(InvalidEmailError) as exc_info:
        validate_email("test@")
    assert exc_info.value.code == "EMAIL_MISSING_DOMAIN"
```

## Anti-Pattern 5 (Implicit): Mock-the-Thing-You're-Testing

```python
# BAD — mocking the class under test
def test_user_service_create():
    mock_service = Mock(spec=UserService)
    mock_service.create_user.return_value = {"id": 123}
    result = mock_service.create_user("test@example.com")
    assert result["id"] == 123
```

**Why it's bad**: this test verifies nothing. It verifies that a mock returns what you told it to return.

**Fix**: instantiate the real `UserService` with mocked *dependencies*, then test it:

```python
def test_user_service_create():
    mock_db = MockDatabase()
    service = UserService(database=mock_db)
    result = service.create_user("test@example.com")
    assert result.id is not None
    assert mock_db.get_user("test@example.com") is not None
```

See `MOCKS.md` for the line between "mock dependencies" and "mock the thing under test."

## Examples by Domain

### Web API Testing

```python
@pytest.mark.integration
def test_user_registration_api():
    """Test user registration endpoint."""
    client = TestClient(app)

    response = client.post("/api/users/register", json={
        "email": "test@example.com",
        "password": "SecurePassword123",
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
        "age": [25, 30],
    })

    result = transform_data(input_data)

    assert len(result) == 2
    assert "age_group" in result.columns
    assert result["age_group"].tolist() == ["20-30", "30-40"]
```

### ML Model Testing

```python
def test_model_prediction_shape_and_range():
    """Test model prediction shape and that output is a valid probability."""
    model = load_test_model()
    test_input = np.array([[1.0, 2.0, 3.0]])

    prediction = model.predict(test_input)

    assert prediction.shape == (1,)
    assert 0 <= prediction[0] <= 1
```

ML tests should focus on **invariants** (shapes, ranges, monotonicity) rather than exact values — model retraining changes exact values without changing correctness.

## Pre-Commit Checklist

Before every commit:

- [ ] All new code has corresponding tests
- [ ] Tests pass locally (`pytest`)
- [ ] Tests are independent (can run in any order, `pytest --random-order` if installed)
- [ ] External dependencies are mocked
- [ ] Tests are fast (<1s for unit tests)
- [ ] Tests have clear, descriptive names
- [ ] Edge cases and error cases are tested

## Pre-Merge Checklist

Before merging a PR:

- [ ] All CI tests pass
- [ ] Integration tests pass
- [ ] Coverage threshold met (see `CI.md`)
- [ ] No `pytest.skip` or `xfail` added without explanation
- [ ] New test fixtures documented
- [ ] No test data committed to the wrong location (`tests/fixtures/`, not `tests/`)

## Periodic Review Checklist

Quarterly or per phase:

- [ ] Remove obsolete tests (deleted features should have deleted tests)
- [ ] Update test data (it ages)
- [ ] Refactor duplicated test code into fixtures
- [ ] Review slow tests — optimize or mark them
- [ ] Update mocks to match real system changes
- [ ] Confirm marker definitions in `pyproject.toml` still match how tests are categorized

## See Also

- `VERTICAL-SLICING.md` — the rhythm that prevents anti-patterns 2 and 5 from creeping in.
- `ENFORCEMENT.md` — the deterministic mechanisms (PostToolUse audit hook) that catch new code without a test partner.
- `CI.md` — the CI configuration that surfaces anti-pattern 3 if it appears.
- `MOCKS.md` — the line between healthy mocking and mock-the-thing-you're-testing.
