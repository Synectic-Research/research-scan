"""`completion` prints a script the shell can actually use, for the three shells it claims."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from research_scan.cli import app

runner = CliRunner()


@pytest.mark.parametrize("shell", ["bash", "zsh", "fish"])
def test_each_shell_gets_a_script_naming_this_binary(shell):
    result = runner.invoke(app, ["completion", shell])

    assert result.exit_code == 0
    assert "_RESEARCH_SCAN_COMPLETE" in result.stdout
    assert "research-scan" in result.stdout


def test_an_unknown_shell_names_the_ones_that_work(monkeypatch):
    result = runner.invoke(app, ["completion", "tcsh"])

    assert result.exit_code == 2
    assert "bash, zsh, fish" in result.output


def test_the_root_never_grows_typers_own_completion_flags():
    """`add_completion=False` is a deliberate choice; registering the shell classes must not
    quietly reverse it by adding a second completion surface to every invocation."""
    help_text = runner.invoke(app, ["--help"]).output

    assert "--install-completion" not in help_text
    assert "--show-completion" not in help_text


def test_the_generated_script_resolves_real_commands():
    """The script is only useful if the callback it installs answers.

    `add_completion=False` also skips registering the per-shell completion classes, so this
    returned "Shell zsh not supported" until they were registered at import. Click intercepts
    the callback before any command runs, which is why a call inside `completion` was too late.
    """
    binary = Path(sys.executable).parent / "research-scan"
    if not binary.exists():  # pragma: no cover - only when the package is not installed
        pytest.skip("the console script is not installed in this environment")

    completed = subprocess.run(
        [str(binary)],
        env={
            "_RESEARCH_SCAN_COMPLETE": "complete_bash",
            "COMP_WORDS": "research-scan doc",
            "COMP_CWORD": "1",
            "PATH": "/usr/bin:/bin",
        },
        capture_output=True,
        text=True,
        check=False,
    )

    assert "not supported" not in completed.stdout
    assert "doctor" in completed.stdout
