"""The gap register: what this repo cannot see yet.

Rule 5 of the maintaining-the-common-operating-picture skill: gaps are listed,
each naming the collector that would close it and the decision it blocks, and
the list is never empty. The register is the markdown table in docs/gaps.md,
pinned by tests/test_gaps.py.
"""

import re
from collections import Counter
from pathlib import Path

REGISTER = Path(__file__).resolve().parents[1] / "docs" / "gaps.md"

EMPTY = "no open gap: the list is never empty (rule 5)"

SEPARATOR = re.compile(r"^\|[\s:|-]+\|$")

# A cell that fills a field without naming anything, once punctuation and markup
# are stripped. A cell of punctuation alone strips to nothing.
FILLERS = {"tbd", "none", "none exists", "n/a", "unknown", "nothing", "nothing exists"}

# The fields every open gap must fill, by header key: the gap itself, and the
# two rule 5 requires (an empty Gap cell survived the hub's pins; agent-eval
# gate, 2026-10-06, mutation M16).
REQUIRED = {
    "gap": "describes nothing",
    "collector": "names no collector that would close it",
    "decision": "names no decision it blocks",
}

# Rule 4: a gap is never deleted. It closes or is superseded in place, with the
# date and a pointer to what closed or replaced it, and only `open` rows count.
STATUS = re.compile(r"^(open|(closed|superseded) \d{4}-\d{2}-\d{2} by \S.*)$")
BAD_STATUS = (
    "status must be open, closed YYYY-MM-DD by <pointer>, "
    "or superseded YYYY-MM-DD by <pointer>"
)


def problems(text: str) -> list[str]:
    """Every way the register breaks rule 5. An empty list means it holds."""
    keys, data = _table(text)
    found = [
        f"{cells[0]}: has {len(cells)} cells where the header has {len(keys)} (a | inside a cell?)"
        for cells in data
        if len(cells) != len(keys)
    ]
    rows = [dict(zip(keys, cells)) for cells in data if len(cells) == len(keys)]
    # A pointer names an id; two rows under one id make every pointer at it ambiguous.
    found += [
        f"{id_}: appears {n} times; a pointer at it is ambiguous"
        for id_, n in Counter(row["id"] for row in rows).items()
        if n > 1
    ]
    found += [f"{row['id']}: {BAD_STATUS}" for row in rows if not STATUS.match(row["status"])]
    live = [row for row in rows if row["status"] == "open"]
    if not live:
        return found + [EMPTY]
    return found + [
        f"{row['id']}: {message}"
        for row in live
        for key, message in REQUIRED.items()
        if _says_nothing(row[key])
    ]


def _says_nothing(cell: str) -> bool:
    """True when a cell, stripped of punctuation and markup, names nothing."""
    words = re.sub(r"[^a-z0-9/]+", " ", cell.lower()).split()
    return not words or " ".join(words) in FILLERS


def _table(text: str) -> tuple[list[str], list[list[str]]]:
    """The header's keys (each heading's first word, lowercased) and each data row's cells."""
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip().startswith("|") and not SEPARATOR.match(line.strip())
    ]
    if not lines:
        return [], []
    header, *data = ([cell.strip() for cell in line.strip("|").split("|")] for line in lines)
    return [cell.split()[0].lower() if cell else "" for cell in header], data
