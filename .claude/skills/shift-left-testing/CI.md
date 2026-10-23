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

      - name: Set up uv with Python ${{ matrix.python-version }}
        uses: astral-sh/setup-uv@v5
        with:
          python-version: ${{ matrix.python-version }}
          enable-cache: true

      - name: Install dependencies
        # --clear: setup-uv@v5 has already run `uv venv` for python-version, and
        # uv refuses to overwrite an existing .venv without it (exit 2).
        run: |
          uv venv --clear
          uv pip install -e ".[dev]"

      - name: Run unit tests
        run: .venv/bin/pytest tests/unit/ -v --cov=src --cov-report=xml

      - name: Run integration tests
        run: .venv/bin/pytest tests/integration/ -v

      - name: Run simulation tests
        run: .venv/bin/pytest tests/simulation/ -v

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

**Notes**:
- External tests (`tests/external/`) are NOT in CI by default. They run manually or on a nightly schedule.
- Matrix the Python versions you support, not "all of them." Three versions covers most cases.
- `uv pip install -e ".[dev]"` requires a `pyproject.toml` with a `[project.optional-dependencies] dev = [...]` section.
- `setup-uv@v5` with a `python-version` input installs a uv-managed interpreter, sets `UV_PYTHON`, and runs `uv venv` itself, so `.venv` already exists when your install step starts and the job never touches the runner's system Python. Current uv refuses to overwrite an existing environment: a bare `uv venv` exits 2 with "A virtual environment already exists". Write `uv venv --clear`. The flag holds whether or not the action created the environment first (`setup-uv` v6 makes that opt-in), so it is the form to copy. Found 2026-09-18 in `fist`, where the job died in "Install dependencies" 8 ms in; a hosted runner and a self-hosted one fail the same way.
- A dry run of the workflow's `run:` lines on your own box does not cover what a `uses:` step did to the workspace first. Read the action, or say the dry run covers the shell lines only.

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
- **<60%** suggests systematic under-testing; investigate before lowering further.
- **>90%** can drive over-testing: tests written for coverage metrics, not for risk.
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

`setup-uv` handles caching itself — `enable-cache: true` in the example above persists uv's wheel cache between runs. Key it on your dependency spec if you want tighter invalidation:

```yaml
- uses: astral-sh/setup-uv@v5
  with:
    enable-cache: true
    cache-dependency-glob: "**/pyproject.toml"
```

uv's installs are fast enough that cold-cache runs are rarely the bottleneck; the cache mostly saves PyPI bandwidth.

On a self-hosted runner, set two inputs differently. `setup-uv@v5` puts uv's cache under `RUNNER_TEMP` by default, and a self-hosted runner wipes `RUNNER_TEMP` after every job, so every run starts cold. `enable-cache: true` also round-trips the cache through GitHub's cache service, which a box with its own disk does not need:

```yaml
- uses: astral-sh/setup-uv@v5
  with:
    enable-cache: auto             # GitHub's cache service on hosted runners only
    cache-local-path: ~/.cache/uv  # survives the job on a self-hosted runner
```

Both values are safe on a hosted runner too, so one workflow serves both (read from `setup-uv` v5's `src/utils/inputs.ts`, 2026-09-18).

## Parallel Execution

For large test suites, run tests in parallel with `pytest-xdist`:

```bash
uv pip install pytest-xdist
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

Don't put integration or external tests in the pre-commit hook; they're too slow for the inner loop.

## See Also

- `TIERS.md` — marker definitions used by `pytest -m`.
- `ANTIPATTERNS.md` — "slow tests in CI" anti-pattern.
- The project's CI workflow (`.github/workflows/tests.yml`) once it exists.
