"""Tests for src/machine.py."""

import pytest

from src import machine

# --- fixtures ---

ROSTER = """\
project:
  name: "paperboy"

machines:
  titanx:
    role: workstation
    scope: [work, personal]
    references:
      lakehouse: ~/projects/gitlab/dis-data/dis-lakehouse
  unknown:
    role: unspecified
    scope: [personal]
    references: {}
"""


@pytest.fixture
def roster(tmp_path, monkeypatch):
    """Point the module at a fake config/project.yaml."""
    config = tmp_path / "project.yaml"
    config.write_text(ROSTER)
    monkeypatch.setattr(machine, "CONFIG_FILE", config)
    return config


def _at_host(monkeypatch, hostname):
    monkeypatch.setattr(machine.socket, "gethostname", lambda: hostname)


# --- resolve_machine ---


class TestResolveMachine:
    def test_known_hostname_resolves_to_its_roster_entry(self, roster, monkeypatch):
        _at_host(monkeypatch, "titanx")

        result = machine.resolve_machine()

        assert result.name == "titanx"
        assert result.role == "workstation"
        assert result.scope == ("work", "personal")
        assert result.known is True

    def test_unlisted_hostname_degrades_to_unknown(self, roster, monkeypatch):
        _at_host(monkeypatch, "some-new-laptop")

        result = machine.resolve_machine()

        # The name stays truthful even off-roster; `known` carries membership.
        assert result.name == "some-new-laptop"
        assert result.known is False
        assert result.scope == ("personal",)

    def test_reference_paths_expand_to_absolute(self, roster, monkeypatch, tmp_path):
        _at_host(monkeypatch, "titanx")
        # expanduser reads HOME on POSIX and USERPROFILE on Windows; set both
        # so the test controls expansion on either platform.
        fake_home = tmp_path / "home" / "someone"
        monkeypatch.setenv("HOME", str(fake_home))
        monkeypatch.setenv("USERPROFILE", str(fake_home))

        result = machine.resolve_machine()

        lakehouse = result.references["lakehouse"]
        assert lakehouse.is_absolute()
        assert "~" not in str(lakehouse)
        assert lakehouse == fake_home / "projects/gitlab/dis-data/dis-lakehouse"

    def test_machine_without_references_gets_empty_mapping(self, roster, monkeypatch):
        _at_host(monkeypatch, "some-new-laptop")

        assert machine.resolve_machine().references == {}


# --- describe ---


class TestDescribe:
    def test_known_machine_reads_as_one_line(self, roster, monkeypatch):
        _at_host(monkeypatch, "titanx")

        line = machine.describe(machine.resolve_machine())

        assert line == "titanx (workstation, work+personal)"

    def test_unknown_machine_says_so_rather_than_guessing(self, roster, monkeypatch):
        _at_host(monkeypatch, "some-new-laptop")

        line = machine.describe(machine.resolve_machine())

        assert "not in the roster" in line
        assert "some-new-laptop" in line
