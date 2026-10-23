"""Tests pinning the verifying-claims skill to its markable requirements.

The skill is prose, so these tests check shape, not judgment: the size caps,
the kernel's rule count, what each probe row must name, one example per
failure shape, and that the surfaces carrying the kernel and its terms agree.
Whether a rule is well worded is a reviewer's call and stays out of this file.

Two requirements have no test here. "Probes are read-only" needs a reader:
no string separates a read from a write. "No work-system names" cannot be
pinned without committing the names.
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / ".claude" / "skills" / "verifying-claims"
SKILL = SKILL_DIR / "SKILL.md"
EXAMPLES = SKILL_DIR / "EXAMPLES.md"
CLAUDE_MD = ROOT / "CLAUDE.md"
FRAMEWORK = ROOT / ".claude" / "skills" / "SKILLS_FRAMEWORK.md"
REVIEWER = ROOT / ".claude" / "agents" / "code-reviewer.md"
SESSION_END = ROOT / ".claude" / "commands" / "session-end.md"
SESSION_FORMAT = ROOT / "docs" / "session-doc-format.md"

STATES = ("written", "tested", "deployed", "observed")
BOUND = "claim a reader will act on"
LEDGER_LINES = (
    "Overclaims the user caught this session: N",
    "Overclaims a reviewer caught this session: M",
)


def _frontmatter(text: str) -> dict[str, str]:
    block = re.match(r"^---\n(.*?)\n---\n", text, re.S).group(1)
    return dict(line.split(": ", 1) for line in block.splitlines())


def _section(text: str, heading: str) -> str:
    """The body under a `## heading`, up to the next `## ` or the end."""
    match = re.search(rf"^## {re.escape(heading)}[^\n]*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    assert match, f"no '## {heading}' section"
    return match.group(1)


def _numbered_rules(section: str) -> list[str]:
    return re.findall(r"^\d+\. (.+)$", section, re.M)


def _table_rows(section: str) -> list[list[str]]:
    """Body rows of the first markdown table in a section, as stripped cells."""
    lines = [line for line in section.splitlines() if line.startswith("|")]
    return [[cell.strip() for cell in line.strip("|").split("|")] for line in lines[2:]]


def _kernel() -> str:
    return _section(SKILL.read_text(), "The Kernel")


# --- SKILL.md ---------------------------------------------------------------


def test_skill_is_directory_form_with_frontmatter():
    meta = _frontmatter(SKILL.read_text())
    assert meta["name"] == SKILL_DIR.name
    assert meta["description"]
    assert meta["version"]


def test_skill_md_is_under_110_lines():
    assert len(SKILL.read_text().splitlines()) < 110


def test_kernel_has_at_most_six_rules():
    assert 1 <= len(_numbered_rules(_kernel())) <= 6
    assert not re.search(r"^\s*[-*] ", _kernel(), re.M), "a rule written as a bullet escapes the count"


def test_kernel_carries_the_decided_terms():
    """Four states, freshness, the Evidence line, UNVERIFIED, the clean tree, read-only probes."""
    kernel = "\n".join(_numbered_rules(_kernel()))
    for term in (
        "written, tested, deployed, or observed",
        "An absence is a claim",
        "this turn",
        "after the last change",
        f"each {BOUND}",
        "`Evidence:`",
        "`UNVERIFIED: <blocker>`",
        "a timer or service runs from",
        "`git status --porcelain`",
        "never write",
    ):
        assert term in kernel, f"kernel lost {term!r}"


def test_state_table_defines_the_four_states():
    rows = _table_rows(_section(SKILL.read_text(), "The Four States"))
    assert [row[0] for row in rows] == list(STATES)


# What each probe row must name, by claim type.
PROBE_ELEMENTS = {
    "run landed": ("exit status", "`tail <log>`", "newer than the launch"),
    "pushed": ("`git rev-parse HEAD`", "`git ls-remote origin refs/heads/<branch>`", "`git status --porcelain`"),
    "mirror synced": ("`git ls-remote <mirror> refs/heads/<branch>`",),
    "tests pass": ("summary line", "python -V", "CI"),
    "venv exists": ("`find . -maxdepth 3 -name pyvenv.cfg`", "python -V"),
    "merged": ("`git merge-base --is-ancestor <sha> main", "`git ls-remote origin refs/heads/main`"),
    "deployed": ("`git status --porcelain`", "`git ls-remote origin refs/heads/<branch>`"),
}


def test_probe_table_has_one_probe_per_claim_type():
    rows = _table_rows(_section(SKILL.read_text(), "Probes"))
    assert len(rows) == len(PROBE_ELEMENTS)
    for claim_type, elements in PROBE_ELEMENTS.items():
        matching = [row for row in rows if claim_type in row[0].lower()]
        assert len(matching) == 1, f"want one row for {claim_type!r}"
        row = " | ".join(matching[0])
        assert matching[0][1] in STATES
        for element in elements:
            assert element in row, f"the {claim_type!r} row lost {element!r}"


def test_tests_are_not_called_read_only():
    """The test tripwire stops deletes, not overwrites; the skill must not promise more."""
    assert "rule 6 does not hold for them" in _section(SKILL.read_text(), "Probes")


# --- EXAMPLES.md ------------------------------------------------------------


def _pairs() -> list[str]:
    """The bodies of the numbered `## N. title` sections of EXAMPLES.md."""
    return re.findall(r"^## \d+\. [^\n]*\n(.*?)(?=^## |\Z)", EXAMPLES.read_text(), re.S | re.M)


def test_examples_hold_seven_pairs():
    """Six failure shapes plus the line-count slip: 11 claimed, 12 measured."""
    pairs = _pairs()
    assert len(pairs) == 7
    before, _, after = pairs[6].partition("**After**")
    assert "11 lines" in before
    assert "12 lines" in after


def test_each_example_shows_a_before_and_an_evidenced_after():
    for number, pair in enumerate(_pairs(), start=1):
        before, _, after = pair.partition("**After**")
        assert "**Before**" in before, f"pair {number} has no Before"
        assert after, f"pair {number} has no After"
        assert "Evidence:" in after or "UNVERIFIED:" in after, f"pair {number}'s After shows no evidence"
        assert "Evidence:" not in before and "UNVERIFIED:" not in before


def test_examples_show_a_clean_report():
    """The counterweight: a report that needs no added line, so the pairs do not teach over-flagging."""
    clean = _section(EXAMPLES.read_text(), "A clean report")
    assert "**Before**" not in clean
    assert "Evidence:" not in clean.split("\n\n")[0] and "UNVERIFIED:" not in clean.split("\n\n")[0]


# --- The surfaces that carry the kernel and its terms -----------------------


def test_claude_md_carries_the_kernel_verbatim():
    """The ambient copy and the skill's kernel are one text in two places."""
    ambient = _numbered_rules(_section(CLAUDE_MD.read_text(), "Claim Style"))
    assert ambient == _numbered_rules(_kernel())


def test_claude_md_block_bounds_a_claim():
    """The lead sentence says what a claim is; the closing lines say what is not, and keep plans honest."""
    lead, _, closing = _section(CLAUDE_MD.read_text(), "Claim Style").partition("\n1. ")
    assert BOUND in lead
    closing = closing.split("\n\n", 1)[1]
    assert "is not a claim" in closing
    assert "check it before you act" in closing


def _reviewer_line() -> str:
    return next(line for line in REVIEWER.read_text().splitlines() if line.startswith("**Success claims**"))


@pytest.mark.parametrize(
    "surface",
    ["SKILL.md intro", "kernel", "CLAUDE.md", "session-end", "format doc", "reviewer"],
)
def test_every_surface_uses_one_bound(surface):
    text = {
        "SKILL.md intro": SKILL.read_text().split("## When to Use")[0],
        "kernel": _kernel(),
        "CLAUDE.md": _section(CLAUDE_MD.read_text(), "Claim Style"),
        "session-end": _section(SESSION_END.read_text(), "Step 5: Session Documentation"),
        "format doc": SESSION_FORMAT.read_text(),
        "reviewer": _reviewer_line(),
    }[surface]
    assert BOUND in text


def test_skill_is_registered():
    sidecars = len(list(SKILL_DIR.glob("*.md"))) - 1
    plural = "sidecar" if sidecars == 1 else "sidecars"
    framework = FRAMEWORK.read_text()
    assert "### verifying-claims (directory form)" in framework
    assert f"`.claude/skills/verifying-claims/SKILL.md` + {sidecars} {plural}" in framework
    for name in sorted(path.name for path in SKILL_DIR.glob("*.md")):
        assert name in framework.split("├── verifying-claims/")[1].split("│\n")[0]
    assert "verifying-claims/" in (ROOT / ".claude" / "README.md").read_text()


def test_reviewer_checks_claims_for_evidence():
    line = _reviewer_line()
    assert "`.claude/skills/verifying-claims/SKILL.md`" in line
    assert "`Evidence:`" in line
    assert "`UNVERIFIED: <blocker>`" in line
    assert "refutes" in line


# --- The Claims table at session end ----------------------------------------


def test_session_end_requires_the_claims_table():
    step5 = _section(SESSION_END.read_text(), "Step 5: Session Documentation")
    assert "Summary, Claims, and Next Steps" in step5
    assert "`## Claims`" in step5
    assert "`Evidence:`" in step5
    assert "`UNVERIFIED: <blocker>`" in step5


def test_session_end_defines_what_each_count_holds():
    """The user's ruling on the two counts: reliance puts a claim in N; a self-retracted claim is in neither."""
    step5 = _section(SESSION_END.read_text(), "Step 5: Session Documentation")
    assert "that the user corrected, asked about, or had already relied on" in step5
    assert "every other claim a reviewer's re-run refuted" in step5
    assert "is in neither count" in step5


def test_session_doc_format_defines_the_claims_table():
    fmt = SESSION_FORMAT.read_text()
    assert "\n## Claims\n" in fmt
    assert "| Claim | State | Evidence |" in fmt
    assert "Summary, Claims, and Next Steps" in fmt


@pytest.mark.parametrize("path", [SKILL, SESSION_END, SESSION_FORMAT], ids=lambda path: path.name)
def test_ledger_lines_are_the_same_strings_everywhere(path):
    """N is the count a repo's overclaim rate is read from; reworded in one file, it stops being one instrument."""
    for line in LEDGER_LINES:
        assert line in path.read_text()
