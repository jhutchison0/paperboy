"""deploy/update-server.sh proves the server's clone from a non-login shell.

`ssh <alias> 'command'` runs without .profile, so ~/.local/bin is off PATH and
`claude` is not found; `main.py health` then reports claude_cli FAILED and exits
1, and the deploy dies (measured on the server 2026-10-25). The prove string
must put ~/.local/bin on PATH itself, before anything under main.py runs.
"""

import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "deploy" / "update-server.sh"


def _prove_line() -> str:
    for line in SCRIPT.read_text().splitlines():
        if line.startswith("prove="):
            return line
    raise AssertionError("no prove= line in deploy/update-server.sh")


def test_prove_string_puts_local_bin_on_path_before_main():
    line = _prove_line()
    path_at = line.find(".local/bin")
    main_at = line.find("main.py")
    assert path_at != -1, "the prove string never adds ~/.local/bin to PATH"
    assert path_at < main_at, "PATH must be set before main.py runs"


def test_script_parses_as_bash():
    result = subprocess.run(["bash", "-n", str(SCRIPT)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
