"""The runtime deployment fingerprint: what code is in *this* process.

The bug this exists for: a source install serves the modules it imported at boot, so a checkout
can move to a new release while the running server keeps answering with the old one. Nothing on
the wire revealed that for six days. These tests pin the three properties that make it visible —
the banner reads the same on both transports, the health surface carries the tuple only for a
caller holding the token, and the answer is computed once and frozen for the process lifetime.
"""

from __future__ import annotations

import asyncio
import re
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest

from research_scan import __version__, deployment, mcp_server

TOKEN = "test-token-abcdef123456"

#: `research-scan <version> git=<sha12|unknown> <dirty|clean|n/a> started=<ISO8601>`
BANNER = re.compile(
    r"^research-scan (?P<version>\S+) git=(?P<sha>[0-9a-f]{12}|unknown) "
    r"(?P<state>dirty|clean|n/a) started=(?P<started>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)$"
)


@pytest.fixture(autouse=True)
def fresh_cache():
    """`current()` is cached for the process lifetime, which every test here has to defeat."""
    deployment.current.cache_clear()
    yield
    deployment.current.cache_clear()


def fake_git(mapping: dict[str, str | None], calls: list[str] | None = None):
    def _git(args, cwd, timeout):
        if calls is not None:
            calls.append(args[0])
        return mapping.get(args[0])

    return _git


# --- banner ------------------------------------------------------------------


def test_banner_on_a_checkout_names_the_commit_and_the_tree_state(monkeypatch):
    monkeypatch.setattr(deployment, "_checkout_root", lambda _package: Path("/repo"))
    monkeypatch.setattr(
        deployment,
        "_git",
        fake_git({"rev-parse": "d701ee016b3b1d67efd68bc3906805c13099157d", "status": ""}),
    )

    line = deployment.banner()

    assert BANNER.match(line), line
    assert line.startswith(f"research-scan {__version__} git=d701ee016b3b clean started=")
    # Twelve hex, not forty: enough to identify a commit, short enough to read in a log.
    assert BANNER.match(line).group("sha") == "d701ee016b3b"


def test_banner_reports_a_dirty_checkout_as_dirty(monkeypatch):
    monkeypatch.setattr(deployment, "_checkout_root", lambda _package: Path("/repo"))
    monkeypatch.setattr(
        deployment,
        "_git",
        fake_git({"rev-parse": "a" * 40, "status": " M src/research_scan/cli.py"}),
    )

    assert " dirty started=" in deployment.banner()


def test_banner_on_a_wheel_install_says_unknown_and_na_rather_than_erroring(monkeypatch):
    """A wheel has no git. That is the ordinary state of an installed package, not a defect."""
    monkeypatch.setattr(deployment, "_checkout_root", lambda _package: None)

    def explode(*_args, **_kwargs):
        raise AssertionError("git must not run when the package is not in a checkout")

    monkeypatch.setattr(deployment, "_git", explode)

    line = deployment.banner()

    assert BANNER.match(line), line
    assert line.startswith(f"research-scan {__version__} git=unknown n/a started=")
    assert deployment.current().mode == "wheel"


def test_a_checkout_whose_git_will_not_answer_stays_source_mode_with_an_unknown_sha(monkeypatch):
    """Failing git is not a wheel. The release gate picks its rules off `mode`, so conflating
    the two would apply the wrong verification."""
    monkeypatch.setattr(deployment, "_checkout_root", lambda _package: Path("/repo"))
    monkeypatch.setattr(deployment, "_git", fake_git({"rev-parse": None}))

    current = deployment.current()

    assert (current.git_sha, current.dirty, current.mode) == ("unknown", None, "source")
    assert " n/a started=" in current.banner()


def test_git_failure_never_propagates(monkeypatch):
    """No git binary, no permission, wedged past the timeout — a server still has to boot."""
    monkeypatch.setattr(deployment, "_checkout_root", lambda _package: Path("/repo"))

    def raise_oserror(*_args, **_kwargs):
        raise FileNotFoundError("git")

    monkeypatch.setattr(deployment.subprocess, "run", raise_oserror)

    assert deployment.current().git_sha == "unknown"


# --- checkout detection ------------------------------------------------------


def test_a_venv_inside_the_checkout_is_read_as_an_installed_copy(tmp_path):
    """The trap: `.venv/` commonly sits *inside* the repo, so walking up for `.git` from
    site-packages finds the repo and would report a wheel install as a source deployment."""
    (tmp_path / ".git").mkdir()
    installed = tmp_path / ".venv" / "lib" / "python3.13" / "site-packages" / "research_scan"
    installed.mkdir(parents=True)

    assert deployment._checkout_root(installed) is None


def test_a_package_in_a_checkout_finds_the_repository_root(tmp_path):
    (tmp_path / ".git").mkdir()
    package = tmp_path / "src" / "research_scan"
    package.mkdir(parents=True)

    assert deployment._checkout_root(package) == tmp_path


def test_a_worktree_git_file_counts_as_a_checkout(tmp_path):
    """`.git` is a file in a worktree or submodule, so presence is tested, not type."""
    (tmp_path / ".git").write_text("gitdir: /elsewhere/.git/worktrees/x\n")
    package = tmp_path / "src" / "research_scan"
    package.mkdir(parents=True)

    assert deployment._checkout_root(package) == tmp_path


def test_a_package_outside_any_checkout_has_no_root(tmp_path):
    package = tmp_path / "nowhere" / "research_scan"
    package.mkdir(parents=True)

    assert deployment._checkout_root(package) is None


# --- computed once -----------------------------------------------------------


def test_the_fingerprint_is_computed_once_and_never_re_runs_git(monkeypatch):
    """Every surface must report the process that started, not the current checkout. Re-running
    git on a request would silently start reporting a tree the process never loaded."""
    calls: list[str] = []
    monkeypatch.setattr(deployment, "_checkout_root", lambda _package: Path("/repo"))
    monkeypatch.setattr(
        deployment, "_git", fake_git({"rev-parse": "b" * 40, "status": ""}, calls=calls)
    )

    first = deployment.current()
    for _ in range(10):
        deployment.current()

    assert calls == ["rev-parse", "status"], calls
    assert deployment.current() is first


def test_started_at_is_process_start_not_call_time(monkeypatch):
    """Captured at import, so a late first call still reports when the process began."""
    monkeypatch.setattr(deployment, "_checkout_root", lambda _package: None)

    assert deployment.current().started_at is deployment._STARTED_AT
    assert deployment.current().started_at.tzinfo is UTC


def test_the_tuple_is_frozen():
    with pytest.raises(Exception):  # noqa: B017 - dataclasses raise FrozenInstanceError
        deployment.current().version = "9.9.9"  # type: ignore[misc]


# --- the reported tuple ------------------------------------------------------


def test_as_dict_is_exactly_the_four_fields_and_carries_no_secret(monkeypatch):
    monkeypatch.setattr(deployment, "_checkout_root", lambda _package: Path("/repo"))
    monkeypatch.setattr(deployment, "_git", fake_git({"rev-parse": "c" * 40, "status": ""}))

    payload = deployment.current().as_dict()

    assert set(payload) == {"version", "git_sha", "dirty", "started_at"}
    assert payload == {
        "version": __version__,
        "git_sha": "c" * 12,
        "dirty": False,
        "started_at": deployment._iso(deployment._STARTED_AT),
    }


def test_started_at_serializes_as_utc_iso8601_with_a_z():
    moment = datetime(2026, 8, 27, 12, 31, 17, 123456, tzinfo=UTC)

    assert deployment._iso(moment) == "2026-08-27T12:31:17Z"


# --- the health surface ------------------------------------------------------


@pytest.fixture
def mcp_home(fake_settings, tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCH_SCAN_MCP_TOKEN", TOKEN)
    monkeypatch.setenv("RESEARCH_SCAN_MCP_DATA", str(tmp_path / "mcp-runs"))
    return tmp_path


def get(app, url: str, auth: str | None = None) -> httpx.Response:
    async def go() -> httpx.Response:
        headers = {"Authorization": f"Bearer {auth}"} if auth else {}
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            return await client.get(url, headers=headers)

    return asyncio.run(go())


def test_health_without_a_token_is_liveness_only(mcp_home, monkeypatch):
    """The server sits behind a public tunnel. An unauthenticated body must not publish the
    exact commit it is running — that is free reconnaissance for anyone who finds the host."""
    monkeypatch.setattr(deployment, "_checkout_root", lambda _package: Path("/repo"))
    monkeypatch.setattr(deployment, "_git", fake_git({"rev-parse": "d" * 40, "status": ""}))

    response = get(mcp_server.build_app(TOKEN), "/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize("kind", ["bearer", "path"])
def test_health_with_the_token_carries_the_deployment_tuple(mcp_home, monkeypatch, kind):
    monkeypatch.setattr(deployment, "_checkout_root", lambda _package: Path("/repo"))
    monkeypatch.setattr(deployment, "_git", fake_git({"rev-parse": "e" * 40, "status": ""}))
    app = mcp_server.build_app(TOKEN)

    response = get(app, "/health", auth=TOKEN) if kind == "bearer" else get(app, f"/{TOKEN}/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "version": __version__,
        "git_sha": "e" * 12,
        "dirty": False,
        "started_at": deployment._iso(deployment._STARTED_AT),
    }


def test_health_with_a_wrong_bearer_falls_back_to_liveness(mcp_home):
    """A bad credential is not an error here — it is simply not authenticated, so it gets the
    same public answer an anonymous monitor gets. Nothing leaks by guessing wrong."""
    response = get(mcp_server.build_app(TOKEN), "/health", auth="wrong-token")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_a_wrong_path_secret_is_not_a_route_at_all(mcp_home):
    """Only `/{token}` is mounted, so a guessed prefix 404s before any handler runs — it never
    reaches the liveness answer."""
    assert get(mcp_server.build_app(TOKEN), "/not-the-token/health").status_code == 404


def test_health_never_names_the_token(mcp_home, monkeypatch):
    monkeypatch.setattr(deployment, "_checkout_root", lambda _package: Path("/repo"))
    monkeypatch.setattr(deployment, "_git", fake_git({"rev-parse": "f" * 40, "status": ""}))

    body = get(mcp_server.build_app(TOKEN), "/health", auth=TOKEN).text

    assert TOKEN not in body
