"""`configure` end to end: what it writes, what it refuses to touch, and what it never hangs on.

The load-bearing test here is `test_an_unrelated_variable_survives_a_reconfigure`. The user
`.env` is not only ours — the MCP adapter's `RESEARCH_SCAN_MCP_TOKEN` lives in it, and a
deployment reads it from that exact path. A writer that rebuilt the file from the four
variables it prompts for would take that deployment down at the next restart.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from research_scan import cli, config, doctor
from research_scan.cli import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def offline_doctor(monkeypatch):
    """`configure` ends by running doctor. No test outside `-m live` opens a socket."""
    report = doctor.Report(sources=list(doctor.ALL_SOURCES))
    report.checks.append(doctor.Check("python", "OK", "3.13.0"))
    report.checks.append(doctor.Check("config path", "OK", "ok", mandatory=True))
    report.checks.append(doctor.Check("cache path", "OK", "ok", mandatory=True))
    monkeypatch.setattr(doctor, "run_checks", lambda *args, **kwargs: report)
    monkeypatch.setattr(cli, "HttpClient", _NoClient)
    return report


class _NoClient:
    """Stands in for HttpClient so the command's `with` block works without a network."""

    def __init__(self, *args, **kwargs) -> None: ...

    def __enter__(self):
        return self

    def __exit__(self, *exc) -> bool:
        return False


@pytest.fixture
def home(tmp_path, monkeypatch) -> Path:
    """A scratch HOME with no credentials anywhere, and a terminal on stdin."""
    scratch = tmp_path / "home"
    scratch.mkdir()
    monkeypatch.setenv("HOME", str(scratch))
    monkeypatch.chdir(tmp_path)
    for var in config.KNOWN_VARS:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr(cli, "_interactive", lambda: True)
    return scratch


def answer(monkeypatch, *values: str) -> None:
    """Feed the getpass prompts in order; the mailto prompt reads from CliRunner's stdin."""
    remaining = list(values)
    monkeypatch.setattr("getpass.getpass", lambda *a, **k: remaining.pop(0) if remaining else "")


# --- writing ------------------------------------------------------------------


def test_a_first_run_writes_the_env_file_with_private_permissions(home, monkeypatch):
    answer(monkeypatch, "openalex-key-1234", "s2-key-5678", "")

    result = runner.invoke(app, ["configure", "--quiet"], input="me@example.com\n")

    assert result.exit_code == 0, result.output
    target = home / ".config" / "research-scan" / ".env"
    values = config.parse_env_file(target)
    assert values["OPENALEX_API_KEY"] == "openalex-key-1234"
    assert values["OPENALEX_MAILTO"] == "me@example.com"
    assert values["S2_API_KEY"] == "s2-key-5678"
    assert "NCBI_API_KEY" not in values, "an empty answer writes nothing"
    assert target.stat().st_mode & 0o777 == 0o600
    assert target.parent.stat().st_mode & 0o777 == 0o700


def test_the_alias_is_the_same_command(home, monkeypatch):
    answer(monkeypatch, "openalex-key-1234", "", "")

    result = runner.invoke(app, ["setup", "--quiet"], input="\n")

    assert result.exit_code == 0, result.output
    assert (
        config.parse_env_file(home / ".config" / "research-scan" / ".env")["OPENALEX_API_KEY"]
        == "openalex-key-1234"
    )


def test_the_key_never_reaches_the_terminal(home, monkeypatch):
    """getpass, not prompt: a key must not land in the scrollback."""
    answer(monkeypatch, "super-secret-key-9999", "", "")

    result = runner.invoke(app, ["configure", "--quiet"], input="me@example.com\n")

    assert "super-secret-key-9999" not in result.output


# --- re-running ---------------------------------------------------------------


def test_an_unrelated_variable_survives_a_reconfigure(home, monkeypatch):
    """The regression that guards a running deployment. Nothing we did not ask about moves."""
    target = home / ".config" / "research-scan" / ".env"
    target.parent.mkdir(parents=True)
    original = (
        "# research-scan credentials.\n"
        "\n"
        "# Mandatory.\n"
        "OPENALEX_API_KEY=old-openalex\n"
        "\n"
        "# The MCP adapter's shared secret. A service reads this file for it.\n"
        "RESEARCH_SCAN_MCP_TOKEN=deployment-secret-do-not-lose\n"
        "RESEARCH_SCAN_MCP_DATA=/srv/research-scan/runs\n"
    )
    target.write_text(original, encoding="utf-8")
    answer(monkeypatch, "new-openalex", "", "")

    result = runner.invoke(app, ["configure", "--quiet"], input="\n")

    assert result.exit_code == 0, result.output
    after = target.read_text(encoding="utf-8")
    assert "RESEARCH_SCAN_MCP_TOKEN=deployment-secret-do-not-lose" in after
    assert "RESEARCH_SCAN_MCP_DATA=/srv/research-scan/runs" in after
    assert "# research-scan credentials." in after
    assert "# The MCP adapter's shared secret. A service reads this file for it." in after
    assert "OPENALEX_API_KEY=new-openalex" in after
    assert "old-openalex" not in after
    # Every line except the one we were asked to change is byte-identical, in place.
    assert [line for line in after.splitlines() if not line.startswith("OPENALEX_API_KEY=")] == [
        line for line in original.splitlines() if not line.startswith("OPENALEX_API_KEY=")
    ]


def test_enter_keeps_the_current_value(home, monkeypatch):
    target = home / ".config" / "research-scan" / ".env"
    target.parent.mkdir(parents=True)
    target.write_text("OPENALEX_API_KEY=keep-me\nS2_API_KEY=keep-me-too\n", encoding="utf-8")
    answer(monkeypatch, "", "", "")

    result = runner.invoke(app, ["configure", "--quiet"], input="\n")

    assert result.exit_code == 0, result.output
    values = config.parse_env_file(target)
    assert values["OPENALEX_API_KEY"] == "keep-me"
    assert values["S2_API_KEY"] == "keep-me-too"
    assert "nothing changed" in result.output


def test_a_set_value_is_shown_masked_and_never_in_full(home, monkeypatch):
    target = home / ".config" / "research-scan" / ".env"
    target.parent.mkdir(parents=True)
    target.write_text("OPENALEX_API_KEY=abcdefghijkl-tail\n", encoding="utf-8")
    answer(monkeypatch, "", "", "")

    result = runner.invoke(app, ["configure", "--quiet"], input="\n")

    assert "abcdefghijkl-tail" not in result.output
    assert "****tail" in result.output
    assert "from user-config" in result.output, "where a value came from is worth knowing"


# --- refusals -----------------------------------------------------------------


def test_a_non_tty_prints_instructions_and_exits_two_rather_than_hanging(tmp_path, monkeypatch):
    scratch = tmp_path / "home"
    scratch.mkdir()
    monkeypatch.setenv("HOME", str(scratch))
    monkeypatch.chdir(tmp_path)
    for var in config.KNOWN_VARS:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr(cli, "_interactive", lambda: False)

    result = runner.invoke(app, ["configure", "--quiet"])

    assert result.exit_code == 2
    assert "OPENALEX_API_KEY=" in result.output
    assert "research-scan doctor" in result.output
    assert not (scratch / ".config" / "research-scan" / ".env").exists(), "wrote nothing"


def test_a_first_run_with_no_openalex_key_refuses_rather_than_writing_half_a_config(
    home, monkeypatch
):
    answer(monkeypatch, "", "", "")

    result = runner.invoke(app, ["configure", "--quiet"], input="\n")

    assert result.exit_code == 2
    assert "OPENALEX_API_KEY is required" in result.output
    assert not (home / ".config" / "research-scan" / ".env").exists()


def test_the_exit_code_is_doctors(home, monkeypatch, offline_doctor):
    """A configure that leaves the install unusable must not exit 0."""
    offline_doctor.checks.append(
        doctor.Check("OPENALEX_API_KEY", "FAIL", "not set", mandatory=True)
    )
    answer(monkeypatch, "openalex-key-1234", "", "")

    result = runner.invoke(app, ["configure", "--quiet"], input="\n")

    assert result.exit_code == 3
