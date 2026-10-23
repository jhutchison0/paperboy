"""The shift-left audit hook fires only if it is executable.

settings.json runs .claude/hooks/post-tool-shift-left-audit.sh by path, not
through bash, so a hook at mode 644 is never invoked and the audit log falls
silent with no error. Found 2026-10-22 on Nidhogg: an Edit to src/gaps.py
logged nothing, while a pipe test through bash logged OK_TEST_EXISTS.
"""

import os
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HOOK = Path(".claude") / "hooks" / "post-tool-shift-left-audit.sh"


def test_the_audit_hook_is_executable_on_disk():
    assert os.access(REPO / HOOK, os.X_OK), f"{HOOK} is not executable; chmod +x it"


def test_the_audit_hook_is_executable_in_the_index():
    # The index mode is what every clone receives; a chmod on one box is not enough.
    out = subprocess.run(
        ["git", "ls-files", "-s", str(HOOK)], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout
    assert out.startswith("100755"), f"{HOOK} index mode: {out.strip() or 'untracked'} (git update-index --chmod=+x)"
