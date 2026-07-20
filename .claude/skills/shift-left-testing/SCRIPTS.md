# SCRIPTS — Testing CLIs, Scripts, and the Enforcement Perimeter

Sidecar to `SKILL.md`. The audit hook watches `src/*.py` (paperboy's flat layout). Nothing watches `scripts/`. Paperboy has no `scripts/` directory today; this file is the standard to apply the day one appears (e.g., cron wrappers or backfill tools in Phase 3 automation). It covers how to test script code, and how to bring `scripts/` inside the perimeter.

## Structure Scripts for Testability

The testability of a script is decided by its `main`. Keep the entry point thin and every behavior importable:

```python
# BAD: everything under __main__, testable only by subprocess
if __name__ == "__main__":
    args = parse()
    for repo in find_repos(Path.home() / "projects"):
        write_notification(repo, build_entry())

# GOOD: functions take their inputs; main only wires argv to functions
def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repos = find_downstream_repos(args.projects_dir)
    ...
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Two details do most of the work. `parse_args(argv)` takes an explicit argv parameter, so tests call it with a list instead of patching `sys.argv`. Paths arrive as parameters with defaults, so tests pass `tmp_path` instead of touching `Path.home()`. This is the constructor injection of `PATTERNS.md` applied to procedures.

## Filesystem Behavior: Build the World in tmp_path

Scripts that walk and modify directory trees get tested against constructed trees, never against the developer's real `~/projects`:

```python
@pytest.fixture
def repo_factory(tmp_path):
    """Create fake repos under a fake projects dir."""
    projects = tmp_path / "projects"

    def make(name: str, *, has_commands: bool = True, parent: Path = projects) -> Path:
        repo = parent / name
        (repo / ".claude" / "commands").mkdir(parents=True) if has_commands \
            else repo.mkdir(parents=True)
        return repo

    return projects, make


def test_discovery_finds_repos_with_commands_dir(repo_factory):
    projects, make = repo_factory
    a = make("alpha")
    make("plain", has_commands=False)

    assert find_downstream_repos(projects) == [a]


def test_discovery_filters_nested_repos(repo_factory):
    """A repo inside another repo's subtree is excluded; only the outer repo remains."""
    projects, make = repo_factory
    outer = make("outer")
    make("vendored", parent=outer / "lib")

    assert find_downstream_repos(projects) == [outer]


def test_notification_append_preserves_unread_content(repo_factory):
    projects, make = repo_factory
    repo = make("alpha")
    target = repo / ".claude" / "upstream-update.md"
    target.write_text("UNREAD ENTRY\n")

    write_notification(repo, "NEW ENTRY")

    content = target.read_text()
    assert "UNREAD ENTRY" in content and "NEW ENTRY" in content
    assert content.index("UNREAD ENTRY") < content.index("NEW ENTRY")
```

These three tests are not hypothetical: discovery, nested-repo filtering, and append-mode preservation are the exact behaviors `propagate_doctrine.py` promises in its docstring. Each promise gets a pin. A propagation bug discovered in production means eleven repos need cleanup; a propagation bug discovered here costs one red test.

## Dry-Run Is a Contract

`--dry-run` promises zero writes. Test the promise, not the log output:

```python
def snapshot(root: Path) -> dict[str, bytes]:
    return {str(p): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


def test_dry_run_writes_nothing(repo_factory):
    projects, make = repo_factory
    make("alpha")
    before = snapshot(projects)

    main(["--dry-run", "--projects-dir", str(projects)])

    assert snapshot(projects) == before
```

The snapshot comparison catches any write anywhere in the tree, including ones added to the script after this test was written. That future-proofing is the point.

## Environment, Output, and Exit Codes

- **Home and env**: `monkeypatch.setenv("HOME", str(tmp_path))` or patch the default at its seam. Better: thread the path through parameters so no patching is needed.
- **stdout and stderr**: `capsys.readouterr()` for scripts whose output is the product. Assert on structure ("3 repos updated"), not full prose; see `ANTIPATTERNS.md` 4.
- **Exit codes**: argparse errors raise `SystemExit`; assert them explicitly:

```python
def test_unknown_flag_exits_nonzero():
    with pytest.raises(SystemExit) as exc_info:
        parse_args(["--no-such-flag"])
    assert exc_info.value.code != 0
```

## The Subprocess Tier

One or two end-to-end runs verify the wiring that direct calls bypass (shebang, `__main__` guard, argv plumbing):

```python
@pytest.mark.integration
def test_cli_dry_run_end_to_end(tmp_path):
    result = subprocess.run(
        [sys.executable, "scripts/propagate_doctrine.py", "--dry-run"],
        capture_output=True, text=True, env={**os.environ, "HOME": str(tmp_path)},
    )
    assert result.returncode == 0
```

Keep this tier thin per the pyramid in `TIERS.md`: subprocess tests are slow, and every behavior they check is checked faster by the direct-call tests above. They exist to prove the entry point, nothing more.

## Closing the Perimeter

Two changes bring `scripts/` inside the enforcement gradient of `ENFORCEMENT.md`:

1. **Test layout**: script tests live at `tests/scripts/test_<script_name>.py`, mirroring the `tests/**/test_<basename>.py` inference the hook already performs.
2. **Hook scope**: extend the path filter in `post-tool-shift-left-audit.sh` from `*/src/*.py` to also match `*/scripts/*.py`. The hook stays non-blocking; the MAUT rationale in `ENFORCEMENT.md` (false positives, bypass cost, educational over punitive) is unchanged by widening what gets observed.

## See Also

- `ENFORCEMENT.md`: the hook whose perimeter this file widens.
- `PATTERNS.md`: constructor injection, applied here to paths and argv.
- `REGRESSION.md`: snapshot-style tree comparison, generalized to golden files.
- `FIXTURES.md`: `tmp_path` and factory-fixture conventions.
