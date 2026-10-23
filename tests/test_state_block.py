"""Slice 2 of the common operating picture: no maintained surface states the repo's state.

config/project.yaml holds identity. The campaign focus is intent and lives at the head
of docs/tasks.md; known unknowns live in docs/gaps.md; the last session is the newest
file in docs/sessions/ by name. A fact that drifts is measured by command when it is
needed, never kept in an orientation surface, because a kept fact reads as current
after it stops being true. Paperboy's own cases: CONTEXT.md said "Tests: 156 passing"
while the suite ran 180 at commit 3ddde2d, and said auto mode tries the backends "in
that order" after the 2026-09-10 machine-roster preference changed the order. The
config carried last_updated and updated_by, a prose session summary, which is the same
defect as a state block.
"""

import re
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]

# The surfaces that wrote, read, or pointed readers at the state block.
SURFACES = [
    "config/project.yaml",
    ".claude/commands/session-end.md",
    ".claude/commands/session-start.md",
    ".claude/commands/sitrep.md",
    ".claude/README.md",
    "CONTEXT.md",
    ".claude/skills/maintaining-project-context/SKILL.md",
]

# The files an agent reads first (the /pcc check 5 set, less the task list).
ORIENTATION = ["CLAUDE.md", "CONTEXT.md", "README.md", "LANGUAGE.md", ".claude/README.md"]

# A count of something that drifts, or a percentage. "Level 0 agents" names a tier.
DRIFTING_COUNT = re.compile(
    r"(?<![Ll]evel )(?<![Ll]evel-)\b\d[\d,]*(?:\.\d+)?"
    r"(?:%|\s+(?:\w+\s+)?(?:tests?|repos?|repositories|consumers?|agents?|passed|passing)\b)"
)

# A "most recent" or "latest" pinned to a date: true on that date, stale after.
STALE_LATEST = re.compile(r"(?:most recent|latest)[^.\n]*20\d{2}-\d{2}-\d{2}", re.I)

TAG = re.compile(r"\[(measured|identity|record|intent|register|unchecked): [^\]]+\]")


def _read(path: str) -> str:
    return (REPO / path).read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    return re.search(rf"^## {re.escape(heading)}.*?(?=^## |^---)", text, re.S | re.M).group(0)


@pytest.mark.parametrize(
    "text",
    ["189 tests", "53% coverage", "reached 16 downstream repos", "4 agents", "508 passed",
     "Propagated to 15 downstream repos", "20 repositories"],
)
def test_the_drifting_count_pattern_sees_the_shapes_that_went_stale(text):
    assert DRIFTING_COUNT.findall(text)


@pytest.mark.parametrize("text", ["Level 0 agents", "Level-1 agents", "Python 3.12"])
def test_the_drifting_count_pattern_passes_names_that_are_not_counts(text):
    assert DRIFTING_COUNT.findall(text) == []


def test_the_config_has_no_state_block():
    config = yaml.safe_load(_read("config/project.yaml"))
    assert {"state", "last_updated", "updated_by"} & set(config) == set()


@pytest.mark.parametrize("surface", SURFACES)
def test_no_surface_names_a_state_block_key(surface):
    text = _read(surface)
    assert [key for key in ("active_work", "last_session") if key in text] == []


def test_the_focus_lives_at_the_head_of_the_task_list():
    focus = re.search(r"^## Focus\n(.*?)^## Active", _read("docs/tasks.md"), re.S | re.M)
    assert focus, "docs/tasks.md has no ## Focus section before ## Active"
    assert re.findall(r"^\d+\. ", focus.group(1), re.M), "the Focus has no numbered step"
    assert [m.group(0) for m in DRIFTING_COUNT.finditer(focus.group(1))] == []
    assert "## Focus" in _read(".claude/commands/session-end.md")


def test_session_start_reads_the_focus_and_the_gap_register():
    text = _read(".claude/commands/session-start.md")
    assert "## Focus" in _section(text, "Step 3.5")
    assert "docs/gaps.md" in _section(text, "Step 3.7")
    assert "Never restate a count or a status" in _section(text, "Step 5")


def test_every_session_start_summary_line_says_where_it_came_from():
    step5 = _section(_read(".claude/commands/session-start.md"), "Step 5")
    items = re.findall(r"^\d+\. \*\*.*$", step5, re.M)
    assert items
    assert [item for item in items if not TAG.search(item)] == []
    assert "`[unchecked: <reason>]`" in step5


@pytest.mark.parametrize("surface", ORIENTATION)
def test_no_orientation_surface_keeps_a_drifting_count(surface):
    text = _read(surface)
    kept = [m.group(0) for m in DRIFTING_COUNT.finditer(text)]
    kept += [m.group(0) for m in STALE_LATEST.finditer(text)]
    assert kept == []


@pytest.mark.parametrize(
    "surface",
    ORIENTATION + [f".claude/commands/{c}.md" for c in ("session-start", "session-end", "sitrep")],
)
def test_no_surface_picks_the_session_doc_by_modification_time(surface):
    # A fresh clone gives every session doc the same modification time; names
    # are date-first. Slice 2 fixed two surfaces and a traversal found a third.
    assert not re.search(r"most recently modified|ls -t docs/sessions", _read(surface), re.I)
