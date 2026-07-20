# PROPERTY-BASED — Invariant Testing with Hypothesis

Sidecar to `SKILL.md`. Example-based tests check one input against one expected output. Property-based tests state an invariant that must hold for all valid inputs; the framework generates hundreds of inputs, hunts for a counterexample, and shrinks any failure to the smallest input that still breaks. Read this when the code under test has algebraic structure: scorers, normalizers, parsers, serializers, graph transforms.

The tool is [Hypothesis](https://hypothesis.readthedocs.io/). Install with the dev extras: `hypothesis>=6.0`.

## When Properties Beat Examples

Use property-based tests when you can finish one of these sentences:

- "For any valid input, the output is always..." (range invariant)
- "Doing it twice is the same as doing it once..." (idempotence)
- "The order of inputs does not matter..." (permutation invariance)
- "Encoding then decoding returns the original..." (round trip)
- "Improving an input never worsens the output..." (monotonicity)
- "The fast version agrees with the obvious slow version..." (oracle)

Decision-science code is dense with these. A MAUT scorer has a range invariant, a monotonicity claim, and a permutation claim before you have written a single example.

## Core Pattern

```python
from hypothesis import given, strategies as st

@given(st.lists(st.floats(min_value=0.0, max_value=1.0, allow_nan=False), min_size=1))
def test_normalized_weights_sum_to_one(raw_weights):
    weights = normalize_weights(raw_weights)
    assert abs(sum(weights) - 1.0) < 1e-9
```

Hypothesis calls the test with generated lists: empty-adjacent sizes, repeated values, extreme floats. When a case fails, it shrinks toward the minimal failing input and prints it. Add that input as a permanent regression pin:

```python
from hypothesis import example

@given(st.lists(st.floats(0.0, 1.0, allow_nan=False), min_size=1))
@example([0.0])  # Regression: division by zero when all weights are 0
def test_normalized_weights_sum_to_one(raw_weights):
    ...
```

## Worked Example: A Weighted Scorer

The unit under test:

```python
def weighted_score(utilities: list[float], weights: list[float]) -> float:
    """Weighted sum of utilities. Both lists the same length; weights sum to 1."""
```

A composite strategy builds valid paired inputs:

```python
@st.composite
def utilities_and_weights(draw):
    n = draw(st.integers(min_value=1, max_value=8))
    utils = draw(st.lists(st.floats(0.0, 1.0, allow_nan=False), min_size=n, max_size=n))
    raw = draw(st.lists(st.floats(0.01, 1.0, allow_nan=False), min_size=n, max_size=n))
    total = sum(raw)
    return utils, [w / total for w in raw]
```

The invariant suite:

```python
@given(utilities_and_weights())
def test_score_is_bounded(pair):
    utils, weights = pair
    assert 0.0 <= weighted_score(utils, weights) <= 1.0 + 1e-9


@given(utilities_and_weights(), st.data())
def test_score_is_monotone_in_each_utility(pair, data):
    """Raising any single utility never lowers the score."""
    utils, weights = pair
    i = data.draw(st.integers(min_value=0, max_value=len(utils) - 1))
    bumped = list(utils)
    bumped[i] = min(1.0, bumped[i] + 0.1)

    assert weighted_score(bumped, weights) >= weighted_score(utils, weights) - 1e-9


@given(utilities_and_weights())
def test_score_is_permutation_consistent(pair):
    """Reordering (utility, weight) pairs together does not change the score."""
    utils, weights = pair
    paired = sorted(zip(utils, weights))
    u2, w2 = [p[0] for p in paired], [p[1] for p in paired]

    assert weighted_score(u2, w2) == pytest.approx(weighted_score(utils, weights))
```

Three tests, no hand-picked examples, and they encode the scorer's contract more completely than twenty examples would. The monotonicity test is the flagship for decision models: it catches inverted-sign bugs that example tests miss because the examples were written by the same mind that inverted the sign.

## Oracle Testing

When optimizing an implementation, keep the naive version as the referee:

```python
@given(st.lists(st.floats(0.0, 1.0, allow_nan=False), min_size=1, max_size=50))
def test_fast_topk_matches_sorted(values):
    assert fast_top_k(values, k=5) == sorted(values, reverse=True)[:5]
```

The naive version is allowed to be slow and obvious; that is its job.

## Settings and CI Behavior

```python
from hypothesis import settings, HealthCheck

# pyproject.toml or conftest.py: register profiles once
settings.register_profile("dev", max_examples=50)
settings.register_profile("ci", max_examples=300, deadline=None)
settings.load_profile("ci" if os.getenv("CI") else "dev")
```

- `max_examples` trades thoroughness for speed. 50 in the inner loop, more in CI.
- `deadline=None` in CI avoids false failures on slow shared runners.
- Hypothesis stores failing examples in `.hypothesis/`; add it to `.gitignore`. The `@example` decorator, not the database, is the durable regression record.
- Property tests carry `@pytest.mark.unit` unless they are genuinely slow; then mark and shard per `TIERS.md`.

## Anti-Patterns

- **Tautology**: re-implementing the function inside the test and asserting the two agree. An oracle must be a *different*, simpler computation, not a copy.
- **Over-constrained strategies**: generating only friendly inputs (no zeros, no duplicates, no size-1 lists) hides exactly the bugs Hypothesis exists to find. Constrain to the documented contract, nothing tighter.
- **Float equality inside properties**: generated inputs explore the ugly corners of float arithmetic, so bare `==` on computed floats flakes. Use `pytest.approx`; see `NUMERIC.md` for tolerance selection.
- **Properties as a substitute for examples**: keep a few concrete examples for readability. A newcomer learns the function from `test_score_of_all_ones_is_one`, then trusts it from the properties.

## See Also

- `NUMERIC.md`: tolerances for the approx comparisons every numeric property needs.
- `REGRESSION.md`: pinning shrunk counterexamples as permanent regression tests.
- `PATTERNS.md`: the example-based shapes these properties complement.
- `VERTICAL-SLICING.md`: properties join the rhythm like any other test; one property per slice.
