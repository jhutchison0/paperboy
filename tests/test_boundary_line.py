"""The boundary line: no tracked file may name a host, share or address.

Tracked docs write examples as placeholders (`\\\\<host>\\<share>`); the
literals that prove the patterns live only in this file's assertions.
"""

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()

# Two backslashes, a host with a letter, a backslash, a share. `<host>` never matches.
UNC = re.compile(r"(?<![\w:\\])\\\\(?=[A-Za-z0-9.-]*[A-Za-z])[A-Za-z0-9.-]+\\[A-Za-z0-9$_.-]+")
SMB = re.compile(r"smb://(?!<)[\w.-]+", re.I)  # a bare `smb://` or `smb://<host>` is a name or placeholder
IPV4 = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])")
IP_ALLOWED = {"0.0.0.0", "127.0.0.1"}


def scan(files: list[tuple[str, str]]) -> list[str]:
    """Return ``path:line: kind`` for each boundary crossing in (path, text) pairs."""
    hits = []
    for path, text in files:
        for n, line in enumerate(text.splitlines(), 1):
            if UNC.search(line):
                hits.append(f"{path}:{n}: unc path")
            if SMB.search(line):
                hits.append(f"{path}:{n}: smb url")
            if any(m.group() not in IP_ALLOWED for m in IPV4.finditer(line)):
                hits.append(f"{path}:{n}: ipv4 literal")
    return hits


def _tracked_texts() -> list[tuple[str, str]]:
    out = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True
    ).stdout.decode()
    files = []
    for name in filter(None, out.split("\0")):
        path = ROOT / name
        if not path.is_file() or path.resolve() == SELF:
            continue
        try:
            files.append((name, path.read_text(encoding="utf-8")))
        except UnicodeDecodeError:
            continue
    return files


def test_calibration_plants_are_caught():
    planted = [("a.md", "mount \\\\nas01\\media\nping 10.0.0.5\nopen smb://nas01/x")]
    kinds = [h.split(": ")[1] for h in scan(planted)]
    assert kinds == ["unc path", "ipv4 literal", "smb url"]


def test_placeholders_and_allowlist_are_not_caught():
    text = "mount \\\\<host>\\<share>\nbind 0.0.0.0 and 127.0.0.1\nversion 1.2.3"
    assert scan([("a.md", text)]) == []


def test_tracked_tree_crosses_no_boundary_line():
    assert scan(_tracked_texts()) == []
