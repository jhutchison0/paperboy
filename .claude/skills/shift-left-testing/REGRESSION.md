# REGRESSION — Characterization Tests and Golden Files

Sidecar to `SKILL.md`. What to do when the audit hook fires on legacy code, and how to test outputs too large or too structured to assert inline. `ENFORCEMENT.md` lists "edits to legacy untested code" as something the hook surfaces; this file is the next step it points to.

## Characterization Tests: Pinning Legacy Behavior

A characterization test asserts what the code *does*, not what it should do. It exists to make change safe, not to certify correctness. The sequence, adapted from Feathers' legacy-code discipline:

1. **Pin.** Before touching the legacy function, write tests that capture its current observable behavior, including behavior that looks wrong. If the output for an empty list is `-1` and that seems odd, the pin asserts `-1` anyway, with a comment:

   ```python
   def test_score_empty_input_returns_negative_one():
       # Characterization: pins current behavior, correctness not verified.
       # Revisit when score() gets a real contract.
       assert score([]) == -1
   ```

2. **Refactor under the pin.** With current behavior pinned, restructure freely: extract functions, inject dependencies, break up the module. The pins prove the refactor changed nothing observable.

3. **Evolve.** Once the structure supports real tests, replace pins one at a time with tests of *intended* behavior. Changing the empty-list result from `-1` to `raise ValueError` is now a deliberate, reviewed change with a failing pin to delete, not a silent side effect of a refactor.

The discipline mirrors `VERTICAL-SLICING.md` in reverse: slicing grows new code one test at a time; characterization wraps old code one pin at a time. Both refuse to change implementation and expectation in the same motion.

### Finding the Seam

Legacy code resists testing because its dependencies are welded in. Look for the cheapest seam first:

- A function that takes its data as parameters: test it directly.
- A hard-coded dependency (`datetime.now()`, module-level client): add a parameter with the old behavior as default. The signature grows; no caller changes; the seam exists.
- A tangle with no seam: pin at the outermost observable boundary (CLI output, file written, rows inserted) and refactor inward.

## Golden Files

A golden file (snapshot) is a committed artifact holding expected output: a rendered document, an exported CSV, a generated config. The test regenerates the output and compares against the golden copy.

**Use goldens when** the output is large, structured, and reviewed by eye more naturally than expressed as assertions. **Do not use them when** the expectation is computable; a golden file for `2 + 2` is an assertion with extra steps and a worse diff.

### Layout and Comparison

```
tests/
├── golden/
│   ├── report_basic.json
│   └── export_two_nodes.csv
```

```python
GOLDEN_DIR = Path(__file__).parent / "golden"

def normalize(text: str) -> str:
    """Strip run-varying content before comparison."""
    return re.sub(r"generated_at: .*", "generated_at: <TIMESTAMP>", text)

def test_report_matches_golden(tmp_path):
    output = render_report(load_fixture("basic"))
    golden = GOLDEN_DIR / "report_basic.json"

    if os.getenv("UPDATE_GOLDEN"):
        golden.write_text(output)
        pytest.skip("Golden updated; rerun without UPDATE_GOLDEN to verify")

    assert normalize(output) == normalize(golden.read_text())
```

Normalization is what separates a durable golden from a flaky one. Timestamps, hostnames, absolute paths, and float formatting all vary by run or machine; canonicalize them out. Sort JSON keys, format floats with fixed precision, and keep the file human-readable, because humans review its diffs.

### The Bless Workflow

Updating a golden is a code change and gets a code change's scrutiny:

1. `UPDATE_GOLDEN=1 pytest tests/unit/test_report.py` regenerates locally.
2. `git diff tests/golden/` gets read line by line. The diff *is* the review; an unread golden update is an unreviewed behavior change.
3. The commit message states why the output changed.
4. CI never blesses. `UPDATE_GOLDEN` has no effect in CI configuration, so a golden can only change through a reviewed commit.

### Snapshot Churn

The failure mode of golden testing is the golden that updates on every PR. When a diff appears so often that reviewers rubber-stamp it, the test teaches nothing and gates nothing. Fixes, in order of preference: shrink the golden to the stable core of the output; split one large golden into several small ones so diffs localize; or replace the volatile region with invariant assertions (row counts, schema, bounds; see `PROPERTY-BASED.md`).

## Regression Pins for Fixed Bugs

Every fixed bug leaves a test behind, named for its origin so future readers know it is a pin, not a spec:

```python
def test_regression_empty_yaml_config_returns_defaults():
    # Bug: loader crashed on zero-byte YAML (fixed 2026-06-02).
    assert load_config(io.StringIO("")) == DEFAULT_CONFIG
```

Property-test counterexamples get the same treatment via `@example`; see `PROPERTY-BASED.md`.

## See Also

- `ENFORCEMENT.md`: the hook that surfaces the legacy gaps this file closes.
- `VERTICAL-SLICING.md`: the forward discipline this one mirrors.
- `NUMERIC.md`: normalizing float formatting inside goldens.
- `SCRIPTS.md`: golden-style tree comparisons for scripts that write files.
