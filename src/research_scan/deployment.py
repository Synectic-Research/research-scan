# SPDX-License-Identifier: Apache-2.0
"""Which code is actually running in this process.

A source install is a mutable checkout: `.venv/bin/research-scan-mcp` resolves the package to
the working tree, so the tree can move to a new release while a long-lived server keeps serving
the modules it imported at start. That happened — a private server served pre-0.5.0 code for six
days while the tree said 0.5.2 — and nothing on the wire could have revealed it.

This module answers "what started?" rather than "what is checked out now". The tuple is resolved
once and frozen, so every surface that reports it reports the same process, however long it runs
and whatever the checkout does afterwards.

The git half is *operational observability, never proof*. A SHA read from a mutable checkout says
what HEAD pointed at when the process booted; it cannot attest that the bytes in memory are that
commit's. See RELEASING.md — immutable artifact deployment is the stronger end state.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path

from research_scan import __version__

#: Import time, which for a server process is startup: `main()` imports this module before it
#: binds a port. Captured as a constant rather than inside the cached resolver so that a late
#: first call still reports when the process began, not when someone first asked.
_STARTED_AT = datetime.now(UTC)

#: `git status --porcelain` walks the work tree, so it gets the longer budget. Neither is allowed
#: to hold up a boot: a slow or wedged git is reported as unknown, never waited on.
_REV_PARSE_TIMEOUT = 2.0
_STATUS_TIMEOUT = 5.0

#: An installed copy lives under one of these. The check matters because a venv commonly sits
#: *inside* the checkout (`.venv/lib/.../site-packages/research_scan/`), so walking up for `.git`
#: would find the repo and report a wheel install as a source deployment.
_INSTALLED_MARKERS = ("site-packages", "dist-packages")


def _iso(moment: datetime) -> str:
    """ISO 8601 UTC, second resolution, `Z` rather than `+00:00`."""
    return moment.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class Deployment:
    """One process's identity. Frozen: it describes a moment that has already passed."""

    version: str
    git_sha: str
    dirty: bool | None
    started_at: datetime
    #: `source` when the package resolves to a checkout, `wheel` when it is an installed copy.
    #: Recorded rather than inferred from `dirty`: git can fail *inside* a checkout, and that is
    #: a source deployment whose tree state is unknown — not a wheel. The release gate reads this
    #: to decide which verification applies, so the two must not be conflated.
    mode: str = "wheel"

    @property
    def tree_state(self) -> str:
        """The banner's third field: `dirty`, `clean`, or `n/a` off a checkout."""
        if self.dirty is None:
            return "n/a"
        return "dirty" if self.dirty else "clean"

    def banner(self) -> str:
        """The single startup line, identical on both transports."""
        return (
            f"research-scan {self.version} git={self.git_sha} "
            f"{self.tree_state} started={_iso(self.started_at)}"
        )

    def as_dict(self) -> dict[str, object]:
        """The health surface's payload. Carries no credential and no hostname."""
        return {
            "version": self.version,
            "git_sha": self.git_sha,
            "dirty": self.dirty,
            "started_at": _iso(self.started_at),
        }


def _git(args: list[str], cwd: Path, timeout: float) -> str | None:
    """Run one git command. Every failure mode is the same answer: we do not know."""
    try:
        completed = subprocess.run(  # noqa: S603 - fixed argv, no shell, no user input
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        # No git binary, no permission, wedged past the timeout — all "unknown", never a raise.
        # A server must boot and report honestly; it must not fail because git is unavailable.
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()


def _checkout_root(package: Path) -> Path | None:
    """The repository root above the package, or None if this is an installed copy.

    `.git` is a directory in a normal clone and a file in a worktree or submodule, so presence
    is what is tested, not type.
    """
    if any(part in _INSTALLED_MARKERS for part in package.parts):
        return None
    for candidate in [package, *package.parents]:
        if (candidate / ".git").exists():
            return candidate
    return None


@lru_cache(maxsize=1)
def current() -> Deployment:
    """The process's deployment fingerprint, resolved once and cached for the process lifetime.

    Cached deliberately: this must describe the code that started, so re-running git on a later
    request would be a bug, not a refresh. Tests reset it with `current.cache_clear()`.
    """
    root = _checkout_root(Path(__file__).resolve().parent)
    if root is None:
        return Deployment(__version__, "unknown", None, _STARTED_AT, mode="wheel")

    head = _git(["rev-parse", "HEAD"], root, _REV_PARSE_TIMEOUT)
    if head is None:
        # Inside a checkout but git would not answer. The tree state is unknowable too: claiming
        # "clean" here would be a guess, and this tuple is read by a release gate.
        return Deployment(__version__, "unknown", None, _STARTED_AT, mode="source")

    porcelain = _git(["status", "--porcelain"], root, _STATUS_TIMEOUT)
    dirty = None if porcelain is None else bool(porcelain)
    sha = head[:12] if len(head) >= 12 else "unknown"
    return Deployment(__version__, sha, dirty, _STARTED_AT, mode="source")


def banner() -> str:
    """Convenience for the two call sites that log the line at startup."""
    return current().banner()
