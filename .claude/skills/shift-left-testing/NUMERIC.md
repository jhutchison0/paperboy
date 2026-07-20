# NUMERIC — Floats, Arrays, DataFrames, and Determinism

Sidecar to `SKILL.md`. How to assert on computed numbers without lying to yourself in either direction: exact equality flakes on rounding, and lazy tolerances pass broken code. Read this when tests touch floats, numpy, pandas, or anything random.

## Float Comparison

Never use bare `==` on a computed float. It works until an intermediate rounding changes the last bit, and then the failure message is useless.

```python
# BAD: passes today, breaks when the summation order changes
assert calculate_score(inputs) == 0.7342105263157895

# GOOD: states the claim at the precision you actually mean
assert calculate_score(inputs) == pytest.approx(0.73421, rel=1e-5)
```

`pytest.approx` defaults to `rel=1e-6`, which suits most single computations. For values near zero, relative tolerance collapses; add an absolute floor:

```python
assert residual == pytest.approx(0.0, abs=1e-9)
```

Exact `==` remains correct for floats that are exact by construction: integers stored as floats, `0.0`, values copied without arithmetic. The worked examples in `PATTERNS.md` use bare equality on tax math; they pass because the chosen decimals happen to be representable. Treat that as a property of the example, not a license. Default to `approx`.

### Choosing a Tolerance

Derive the tolerance from the algorithm, then write the derivation down:

```python
def test_kalman_converges():
    # Tolerance: 3 sigma of steady-state variance for noise_std=0.5, n=100 (see docs/design/filter.md)
    assert estimate == pytest.approx(true_value, abs=0.2)
```

The anti-pattern is tolerance creep: a failing test gets its tolerance loosened until green, one decimal at a time, until the test would pass a broken implementation. A tolerance without a written rationale is a future creep site.

## Arrays

Use `numpy.testing`; its failure messages show mismatch counts and locations.

```python
import numpy.testing as npt

npt.assert_allclose(result, expected, rtol=1e-6)   # Computed floats
npt.assert_array_equal(mask, expected_mask)         # Ints, bools, indices: exact
```

Assert structure before values; a wrong shape produces a clearer failure than a thousand elementwise mismatches:

```python
assert result.shape == (n_nodes, 3)
assert result.dtype == np.float64
npt.assert_allclose(result, expected, rtol=1e-6)
```

## DataFrames

```python
import pandas.testing as pdt

pdt.assert_frame_equal(result, expected, check_dtype=False, check_like=True)
```

- `check_like=True` ignores column and index order when the contract does not promise order.
- If the contract does not promise row order, sort both frames on a key column before comparing; do not let incidental ordering become a hidden assertion.
- Compare small frames inline; move anything bigger to golden files (see `REGRESSION.md`).

## Determinism

Nondeterministic tests are unpayable debt: the failure cannot be reproduced, so it cannot be fixed. The usual leaks, and the fix for each:

| Leak | Fix |
|---|---|
| `random` / `np.random` global state | Inject a seeded generator (below) |
| Wall-clock time | Inject a clock, or use the `current_timestamp` fixture in `FIXTURES.md` |
| Set and dict iteration in assertions | `sorted()` before comparing |
| Filesystem listing order | `sorted(path.iterdir())` |
| Parallel test interference | True test independence; see `ANTIPATTERNS.md` 1 |

### Injectable Randomness

Pass the generator in, exactly like the constructor injection in `PATTERNS.md`:

```python
def simulate(n: int, rng: np.random.Generator) -> np.ndarray:
    return rng.normal(size=n)

def test_simulate_is_reproducible():
    a = simulate(100, np.random.default_rng(42))
    b = simulate(100, np.random.default_rng(42))
    npt.assert_array_equal(a, b)
```

Production passes `np.random.default_rng()`; tests pass a seeded one. `random.seed(42)` at module scope is the fallback for legacy code, not the pattern for new code.

## Stochastic Code

Two honest ways to test code that is random on purpose:

1. **Fixed seed, exact assertion.** Seed the generator, assert the exact output. Fast and precise, but re-blessed whenever the sampling implementation changes.
2. **Statistical assertion.** Large n, assert on the statistic with a tolerance derived from its standard error, and mark it `@pytest.mark.slow` if n makes it slow:

```python
def test_estimator_is_unbiased():
    rng = np.random.default_rng(7)
    estimates = [estimate(sample(rng)) for _ in range(2000)]
    # SE of the mean at n=2000 is ~0.011; 4 SE bound keeps false-failure odds < 1e-4
    assert np.mean(estimates) == pytest.approx(TRUE_VALUE, abs=0.045)
```

Never assert on a single unseeded draw. That test is a coin flip wearing a test name.

## Ground Truth for Graph and Metric Code

For graph algorithms and scoring metrics, hand-compute tiny cases and assert exactly:

```python
def test_clustering_coefficient_triangle():
    g = graph_from_edges([(0, 1), (1, 2), (2, 0)])
    assert clustering_coefficient(g, node=0) == pytest.approx(1.0)
```

A triangle, a path, a star: three tiny graphs with pencil-and-paper answers catch more metric bugs than any large random graph, and they double as documentation. Use large random graphs for property tests (bounds, symmetry; see `PROPERTY-BASED.md`), not for exact values.

## See Also

- `PROPERTY-BASED.md`: invariants over generated numeric inputs.
- `REGRESSION.md`: golden files for outputs too large to assert inline.
- `FIXTURES.md`: the seeded Faker and timestamp fixtures.
- `ANTIPATTERNS.md`: brittleness; exact-value ML tests.
