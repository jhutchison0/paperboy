# CI — Continuous Integration and Coverage

Sidecar to `SKILL.md`. Wiring tests into CI/CD and enforcing coverage thresholds. Examples use GitHub Actions; the principles apply to any CI provider.

## GitHub Actions Example

`.github/workflows/tests.yml`:

```yaml
name: Tests

on:
  push:
    branches: [main, dev-*]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Run unit tests
        run: pytest tests/unit/ -v --cov=src --cov-report=xml

      - name: Run integration tests
        run: pytest tests/integration/ -v

      - name: Run simulation tests
        run: pytest tests/simulation/ -v

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

**Notes**:
- External tests (`tests/external/`) are NOT in CI by default. They run manually or on a nightly schedule.
- Matrix the Python versions you support, not "all of them." Three versions covers most cases.
- `pip install -e ".[dev]"` requires a `pyproject.toml` with a `[project.optional-dependencies] dev = [...]` section.

## Coverage Configuration

`pyproject.toml`:

```toml
[tool.coverage.run]
source = ["src/"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__pycache__/*",
]

[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

### Setting the Threshold

- **80%** is the conventional default and reasonable for most projects.
- **<60%** suggests systematic under-testing — investigate before lowering further.
- **>90%** can drive over-testing — tests written for coverage metrics, not for risk.
- The right threshold is what gives you confidence to deploy. There's no universal answer.

Don't chase 100%. Some lines (defensive guards, branch-unreachable paths) are not worth testing. Use `# pragma: no cover` to mark intentional omissions.

## Test Selection in CI

Use markers (see `TIERS.md`) to control what runs where:

```yaml
- name: Fast feedback (unit + integration only)
  run: pytest -m "unit or integration" --tb=short

- name: Slow tests (separate job, possibly nightly)
  run: pytest -m "slow"

- name: External tests (manual trigger only)
  if: github.event_name == 'workflow_dispatch'
  run: pytest -m "external"
```

The pattern: fast tests on every push, slow tests on a schedule, external tests on demand.

## Failure Annotations

GitHub Actions can surface pytest failures inline in PRs:

```yaml
- name: Run tests
  run: pytest -v --tb=short
```

For better PR annotations, use `pytest-github-actions-annotate-failures`:

```toml
[project.optional-dependencies]
ci = ["pytest-github-actions-annotate-failures>=0.2"]
```

Then test failures appear as inline review comments on the changed lines.

## Caching Dependencies

Speed up CI by caching `~/.cache/pip`:

```yaml
- name: Cache pip
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

This typically cuts install time from 60s to 5s on subsequent runs.

## Parallel Execution

For large test suites, run tests in parallel with `pytest-xdist`:

```bash
pip install pytest-xdist
pytest -n auto  # Use all available cores
```

Caveats:
- Tests must be truly independent (no shared mutable state, no execution order assumptions).
- Some fixtures don't parallelize cleanly (notably anything using a shared file path).
- Worth doing when test suite runtime exceeds ~30 seconds; below that the overhead doesn't pay off.

## Local Pre-Commit Hook (Optional)

Run the fast tier locally before commit:

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: pytest-unit
        name: pytest unit tests
        entry: pytest tests/unit/ --tb=short
        language: system
        pass_filenames: false
        always_run: true
```

Install once: `pre-commit install`. Now `git commit` runs unit tests automatically.

Don't put integration or external tests in the pre-commit hook — they're too slow for the inner loop.

## See Also

- `TIERS.md` — marker definitions used by `pytest -m`.
- `ANTIPATTERNS.md` — "slow tests in CI" anti-pattern.
- The project's CI workflow (`.github/workflows/tests.yml`) once it exists.
