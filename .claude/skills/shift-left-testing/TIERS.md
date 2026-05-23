# TIERS — Test Pyramid, Tier Strategy, Directory Layout

Sidecar to `SKILL.md`. Read when designing the test strategy for a project or component.

## Test Pyramid

```
         /\
        /  \   E2E / External
       /____\
      /      \
     / System  \
    /__________\
   /            \
  /  Integration  \
 /__________________\
/                    \
/   Unit Tests         \
/______________________\
```

More tests at the base (unit), fewer at the top (E2E). The cost of each test (in runtime, in flakiness, in maintenance) grows as you go up.

## Test Tiers

| Tier | Speed | Scope | Dependencies | Share |
|---|---|---|---|---|
| **Unit** | <1s | Single component (function, class, small module) | All external mocked | 60–70% |
| **Integration** | 1–10s | Multiple components interacting | Some real (in-memory DB), some mocked (network) | 20–30% |
| **System** | 10–60s | End-to-end, full app stack | Real or simulated | 5–10% |
| **External** | >60s | Against real external systems (live API, real DB) | Real | Optional (manual or nightly) |

The shares are guidelines, not rules. A high-integration codebase (many service interactions) might run 40% integration; a pure-function library might run 95% unit.

## Test Directory Layout

### Root-Level Tests (default)

Use this layout unless a component clearly justifies its own test tree.

```
project/
├── src/
│   └── myapp/
│       ├── core/
│       ├── component_a/
│       └── component_b/
│
└── tests/                  # Root-level tests
    ├── __init__.py
    ├── conftest.py         # Shared pytest fixtures (see FIXTURES.md)
    │
    ├── fixtures/           # Test data and mocks
    │   ├── __init__.py
    │   ├── mock_external_apis.py
    │   ├── mock_database.py
    │   ├── test_data.yaml
    │   └── sample_users.json
    │
    ├── unit/               # Component unit tests
    │   ├── __init__.py
    │   ├── test_component_a.py
    │   ├── test_component_b.py
    │   └── test_core_utils.py
    │
    ├── integration/        # Multi-component tests
    │   ├── __init__.py
    │   ├── test_api_integration.py
    │   ├── test_database_operations.py
    │   └── test_end_to_end.py
    │
    ├── simulation/         # Simulated environment tests
    │   ├── __init__.py
    │   ├── test_simulated_workflow.py
    │   └── test_failure_scenarios.py
    │
    └── external/           # Real external system tests (optional)
        ├── __init__.py
        ├── test_live_api.py
        └── test_production_db.py
```

**When root-level is right**:
- Default for most projects
- Always for unit tests
- Always for integration tests
- Anywhere a single test exercises multiple components

### Component-Level Tests

Use when a component is large, complex, or maintained separately.

```
src/myapp/component_a/
├── __init__.py
├── module1.py
├── module2.py
├── submodule/
│   ├── __init__.py
│   └── feature.py
│
└── tests/                  # Component-specific tests
    ├── __init__.py
    ├── test_module1.py
    ├── test_module2.py
    └── test_submodule_feature.py
```

**When component-level is right**:
- Component >1000 lines AND has its own internal structure
- Component developed by a separate team
- Component has component-specific test fixtures that don't belong in root `tests/`
- Component may be extracted into its own package

### Decision Rule

```
if component_size > 1000 lines
   AND (component_complexity = high
        OR component_team = separate
        OR component_likely_to_split_out = true):
    use component-level tests
else:
    use root-level tests
```

When in doubt, root-level. Splitting test trees is a real maintenance cost; do it only when the component genuinely justifies the isolation.

## Test Markers (pytest)

Mark tests by tier so you can run subsets:

```python
import pytest

@pytest.mark.unit
def test_calculation():
    """Fast unit test."""
    assert calculate(2, 3) == 5

@pytest.mark.integration
def test_database_query(test_db):
    """Integration test with in-memory DB."""
    result = test_db.query("SELECT 1")
    assert result

@pytest.mark.slow
def test_long_running_process():
    """Slow test (>10s)."""
    result = process_large_dataset()
    assert result.success

@pytest.mark.external
@pytest.mark.skipif(
    not os.getenv("RUN_EXTERNAL_TESTS"),
    reason="External tests disabled by default"
)
def test_live_api():
    """Test against real external API."""
    response = api.call_real_endpoint()
    assert response.status_code == 200
```

Run subsets:

```bash
pytest -m unit                   # Only unit
pytest -m integration            # Only integration
pytest -m "not slow"             # Everything except slow
pytest -m "unit or integration"  # Unit + integration (not external)
```

Register markers in `pyproject.toml` to silence "unknown marker" warnings:

```toml
[tool.pytest.ini_options]
markers = [
    "unit: Fast, isolated unit tests",
    "integration: Multi-component integration tests",
    "simulation: Tests using simulated environments",
    "external: Tests against real external systems (opt-in)",
    "slow: Tests that take >10s",
]
```

## See Also

- `PATTERNS.md` — what each tier looks like in practice (unit, integration, simulation).
- `FIXTURES.md` — how `conftest.py` and `tests/fixtures/` support all tiers.
- `CI.md` — running tiers in CI (skipping external, parallelizing unit).
