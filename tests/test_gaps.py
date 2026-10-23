"""Tests for src/gaps.py, and the pin on docs/gaps.md."""

import re

import pytest
import yaml

from src import gaps

REPO = gaps.REGISTER.parents[1]


def _keys(node) -> set[str]:
    """Every mapping key at any depth of a parsed YAML document."""
    if isinstance(node, dict):
        return set(node) | {k for v in node.values() for k in _keys(v)}
    if isinstance(node, list):
        return {k for v in node for k in _keys(v)}
    return set()

# --- fixtures ---

HEADER = """\
# Gap Register

| ID | Gap | Collector that would close it | Decision it blocks | Opened | Status |
|---|---|---|---|---|---|
"""

OPEN = "| G1 | Fleet membership | a fleet ledger | the roster | 2026-10-02 | open |\n"


def register(*rows: str) -> str:
    return HEADER + "".join(rows)


def test_the_repo_register_holds_rule_5():
    assert gaps.problems(gaps.REGISTER.read_text()) == []


@pytest.mark.parametrize("command", ["session-end.md", "sitrep.md"])
def test_known_unknowns_live_only_in_the_register(command):
    # The config's known_issues list was the register's predecessor; two homes
    # for one list let them drift. The commands that wrote and read it now point
    # here, so the next session cannot put the key back.
    # The key, not the word, because a comment or a record may name the key's removal.
    config = yaml.safe_load((REPO / "config" / "project.yaml").read_text(encoding="utf-8"))
    assert "known_issues" not in _keys(config)
    text = (REPO / ".claude" / "commands" / command).read_text()
    assert "known_issues" not in text
    # On a list item: an instruction to write it, or a source to read. A heading
    # that merely mentions the file does not count.
    assert re.search(r"^\s*(?:[-*]|\d+\.)\s.*docs/gaps\.md", text, re.MULTILINE)


def test_a_well_formed_register_has_no_problems():
    assert gaps.problems(register(OPEN)) == []


def test_an_empty_register_is_a_problem():
    assert gaps.problems("") == ["no open gap: the list is never empty (rule 5)"]


def test_a_register_of_closed_and_superseded_rows_counts_as_empty():
    closed = OPEN.replace("| open |", "| closed 2026-10-04 by tests/unit/test_x.py |")
    superseded = OPEN.replace("G1", "G2").replace("| open |", "| superseded 2026-10-04 by G3 |")
    assert gaps.problems(register(closed, superseded)) == [
        "no open gap: the list is never empty (rule 5)"
    ]


@pytest.mark.parametrize(
    "filler",
    ["", "-", "TBD", "none", "N/A", "?", "None exists.", "TBD.", "—", "`none`", "*unknown*"],
)
def test_an_open_gap_must_name_its_collector(filler):
    # Punctuation and markup do not make a filler name something. "None exists."
    # alone is a filler; "None exists. A Stop hook ..." names the instrument.
    row = OPEN.replace("| a fleet ledger |", f"| {filler} |")
    assert gaps.problems(register(row)) == ["G1: names no collector that would close it"]


@pytest.mark.parametrize("filler", ["", "TBD", "TBD."])
def test_an_open_gap_must_name_the_decision_it_blocks(filler):
    row = OPEN.replace("| the roster |", f"| {filler} |")
    assert gaps.problems(register(row)) == ["G1: names no decision it blocks"]


@pytest.mark.parametrize(
    "status",
    [
        "Open",
        "opened",
        "done",
        "closed 2026-10-04",
        "superseded by G3",
        "closed by G3",
        "closed today by G3",
    ],
)
def test_a_status_outside_the_three_marks_is_a_problem(status):
    # A typo would hide the row from the field checks; a mark without a date or
    # a pointer would break rule 4's "points at what replaced it".
    odd = OPEN.replace("| open |", f"| {status} |")
    other = OPEN.replace("G1", "G2")
    assert gaps.problems(register(odd, other)) == [
        "G1: status must be open, closed YYYY-MM-DD by <pointer>, "
        "or superseded YYYY-MM-DD by <pointer>"
    ]


@pytest.mark.parametrize(
    ("row", "cells"),
    [
        (OPEN.replace("a fleet ledger", "a `Write|Edit` hook"), 7),
        (OPEN.replace("| 2026-10-02 ", ""), 5),
    ],
)
def test_a_row_whose_cells_do_not_match_the_header_is_a_problem(row, cells):
    # A `|` inside a cell shifts every cell after it; a dropped cell does the same.
    other = OPEN.replace("G1", "G2")
    assert gaps.problems(register(row, other)) == [
        f"G1: has {cells} cells where the header has 6 (a | inside a cell?)"
    ]


def test_a_two_word_filler_still_names_nothing():
    # assay's reviewer defeated the check with "Nothing exists." on the first try
    # (2026-10-05): one word off the documented filler.
    row = OPEN.replace("| a fleet ledger |", "| Nothing exists. |")
    assert gaps.problems(register(row)) == ["G1: names no collector that would close it"]


def test_two_rows_sharing_an_id_is_a_problem():
    # A supersession pointer names an id; two rows under one id make every
    # pointer at it ambiguous (assay, 2026-10-05).
    other = OPEN.replace("Fleet membership", "Fleet membership, restated")
    assert gaps.problems(register(OPEN, other)) == [
        "G1: appears 2 times; a pointer at it is ambiguous"
    ]


def test_an_open_gap_must_describe_itself():
    # An empty Gap cell survived the hub's pins (agent-eval mutation M16, 2026-10-06).
    row = OPEN.replace("Fleet membership", "")
    assert gaps.problems(register(row)) == ["G1: describes nothing"]
