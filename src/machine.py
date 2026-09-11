"""Which machine is this?

The fleet spans several boxes and no repo has ever known which one it sits on.
Every machine distinction in this corpus is prose written by whoever was at the
keyboard. This module makes the machine a name that code can read.

The roster lives in `config/project.yaml` under `machines:`, keyed by hostname.
"""

import socket
from dataclasses import dataclass
from pathlib import Path

import yaml

CONFIG_FILE = Path(__file__).resolve().parents[1] / "config" / "project.yaml"

UNKNOWN = "unknown"


@dataclass(frozen=True)
class Machine:
    """One box, as the roster describes it."""

    name: str
    role: str
    scope: tuple[str, ...]
    references: dict[str, Path]
    known: bool


def resolve_machine() -> Machine:
    """Identify this machine from the roster in config/project.yaml.

    An unlisted hostname resolves to the `unknown` entry with `known=False`.
    A repo on a new box still works; it just knows less about where it is.
    """
    hostname = socket.gethostname()
    roster = yaml.safe_load(CONFIG_FILE.read_text()).get("machines", {})

    known = hostname in roster
    entry = roster.get(hostname) or roster.get(UNKNOWN) or {}

    return Machine(
        name=hostname,
        role=entry.get("role", "unspecified"),
        scope=tuple(entry.get("scope") or ()),
        references={
            name: Path(raw).expanduser()
            for name, raw in (entry.get("references") or {}).items()
        },
        known=known,
    )


def describe(machine: Machine) -> str:
    """One line naming this box, for /session-start to print."""
    if not machine.known:
        return f"{machine.name} (not in the roster; add it to config/project.yaml)"
    return f"{machine.name} ({machine.role}, {'+'.join(machine.scope)})"


if __name__ == "__main__":
    print(describe(resolve_machine()))
