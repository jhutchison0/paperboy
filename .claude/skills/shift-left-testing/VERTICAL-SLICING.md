# VERTICAL-SLICING — Tracer-Bullet TDD Discipline

Sidecar to `SKILL.md`. The discipline of writing tests **one at a time**, in lockstep with the implementation each one drives. Adapted from Matt Pocock's `tdd` skill (`mattpocock/skills/skills/engineering/tdd/SKILL.md`); the rules are verbatim where attributed.

The patterns in `PATTERNS.md` and `MOCKS.md` describe *what* tests look like. This file describes *when* to write each one — and it is the hardest part to maintain.

## The Failure Mode

Without explicit discipline, both agents and humans tend to write **horizontal slices**: all tests first, then all implementation. The structure looks productive but produces brittle code — the implementation gets shaped by what the author *thought* the tests would need, not by what each test actually requires.

```
WRONG (horizontal):
  RED:   test1, test2, test3, test4, test5
  GREEN: impl1, impl2, impl3, impl4, impl5

RIGHT (vertical):
  RED → GREEN: test1 → impl1
  RED → GREEN: test2 → impl2
  RED → GREEN: test3 → impl3
```

The vertical slice is sometimes called a "tracer bullet" — each test pierces the entire stack from input to output, and the implementation grows just enough to pass it before the next bullet is fired.

## Rules (verbatim from Pocock)

- **One test at a time.** Only enough code to pass the current test.
- **Don't anticipate future tests.** If a test you'll write later needs different structure, that pressure should surface when you write *that* test, not now.
- **Never refactor while RED.** Get to GREEN first. Refactor only when all tests pass.

The third rule is the one most often broken. The temptation to "just clean this up while I'm here" while a test is failing is strong. Resist it. RED + refactoring concurrently means you can't tell whether the failure is from the rule or the refactor.

## Pre-Code Planning Checklist (verbatim from Pocock)

Before writing the first test or the first line of implementation, confirm with the user:

> - Confirm with user what interface changes are needed
> - Confirm with user which behaviors to test (prioritize)
> - Identify opportunities for deep modules (small interface, deep implementation)
> - Design interfaces for testability
> - List the behaviors to test (not implementation steps)
> - Get user approval on the plan

The driving question: *"What should the public interface look like? Which behaviors are most important to test?"*

This checklist exists because TDD without a plan degenerates into chasing whatever test happens to be top-of-mind. The plan provides the *order* of the vertical slices.

## Core Principle (verbatim from Pocock)

> Tests should verify behavior through public interfaces, not implementation details. Code can change entirely; tests shouldn't.

This is the discriminator between brittle tests and durable tests. A test that breaks when you refactor the implementation (without changing the public behavior) is the wrong kind of test — it is coupled to internals.

The practical heuristic: when a test asserts on a private attribute (`obj._internal_state`), a private method (`obj._helper()`), or a specific implementation choice (`assert isinstance(result.cache, RedisCache)`), it has fallen into this trap.

## How This Interacts with the Rest of This Skill

The mock, fixture, and tier patterns describe the **mechanical** structure of tests. Vertical slicing describes the **temporal** structure of how you write them. They are complementary:

- The test pyramid (unit/integration/system) sets the strategy.
- Vertical slicing sets the rhythm.
- Mocks set the boundary between the unit under test and its dependencies.

A test that does not verify behavior through a public interface fails the core principle, regardless of how well it follows the other patterns.

## Worked Example

Feature: a function that calculates the total price of a shopping cart including tax.

### Plan

Behaviors to test, in priority order:
1. Empty cart → total is 0
2. Single item → total includes tax
3. Multiple items → total is sum + tax
4. Negative quantity → raises ValueError

### Vertical Slice 1 (test1 → impl1)

```python
# RED
def test_empty_cart_total_is_zero():
    assert calculate_cart_total([]) == 0.0
```

```python
# GREEN — minimum code to pass test 1, nothing more
def calculate_cart_total(items):
    return 0.0
```

Resist the urge to "do the real thing now." The discipline is what generates the design pressure.

### Vertical Slice 2 (test2 → impl2)

```python
# RED
def test_single_item_total_includes_tax():
    items = [{"price": 100.0, "quantity": 1}]
    assert calculate_cart_total(items, tax_rate=0.10) == 110.0
```

```python
# GREEN — minimum code to pass tests 1 AND 2
def calculate_cart_total(items, tax_rate=0.0):
    subtotal = sum(item["price"] * item["quantity"] for item in items)
    return subtotal * (1 + tax_rate)
```

Notice: a `tax_rate` parameter appeared. It wasn't in the original plan, but the test required it. The plan informs the order; the test reveals the interface.

### Vertical Slice 3 (test3 → impl3)

```python
# RED
def test_multiple_items_total():
    items = [
        {"price": 100.0, "quantity": 2},
        {"price": 50.0, "quantity": 1},
    ]
    assert calculate_cart_total(items, tax_rate=0.10) == 275.0
```

```python
# GREEN — already passes! No code change needed.
```

When a new test passes without code change, that's a sign the implementation is over-fitted from the previous slice. Some teams write the test anyway for documentation; others skip and rely on the earlier slice. Either is defensible.

### Vertical Slice 4 (test4 → impl4)

```python
# RED
def test_negative_quantity_raises():
    items = [{"price": 100.0, "quantity": -1}]
    with pytest.raises(ValueError, match="quantity must be non-negative"):
        calculate_cart_total(items)
```

```python
# GREEN
def calculate_cart_total(items, tax_rate=0.0):
    for item in items:
        if item["quantity"] < 0:
            raise ValueError("quantity must be non-negative")
    subtotal = sum(item["price"] * item["quantity"] for item in items)
    return subtotal * (1 + tax_rate)
```

Now all 4 tests pass. **This is the point at which refactoring is allowed.** Not before.

## Anti-Pattern: Writing All Tests First

```python
def test_empty_cart_total_is_zero(): ...
def test_single_item_total_includes_tax(): ...
def test_multiple_items_total(): ...
def test_negative_quantity_raises(): ...
def test_zero_tax_rate(): ...
def test_high_tax_rate(): ...
# ... then implementation
```

This *looks* disciplined but it isn't. The implementation will be shaped to pass all six tests at once, which means each test is no longer driving design — it's checking that an already-decided implementation satisfies some shape. You've moved from TDD to test-after-design.

## Source

- Matt Pocock, `mattpocock/skills/skills/engineering/tdd/SKILL.md` — verbatim quotes attributed inline.
- Kent Beck, *Test-Driven Development by Example* (2002) — the original red-green-refactor cycle.

## See Also

- `PATTERNS.md` — the test shapes you'll be writing one at a time.
- `MOCKS.md` — how to set up the dependencies each test needs.
- `ANTIPATTERNS.md` — the broader set of testing anti-patterns this discipline avoids.
