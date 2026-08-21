"""The 5-way version guard: agreement passes, any single disagreement fails and is named."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check_versions.py"

# Each version-bearing file, with a callable that rewrites its version in a repo copy.
VERSION_FILES = ["pyproject.toml", ".claude-plugin/plugin.json", "CITATION.cff", "server.json"]


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=False
    )


def repo_copy(tmp_path: Path) -> Path:
    """A minimal copy of the repo: only the files the guard reads, plus the script."""
    root = tmp_path / "repo"
    (root / ".claude-plugin").mkdir(parents=True)
    (root / "scripts").mkdir()
    for name in VERSION_FILES:
        shutil.copy(REPO_ROOT / name, root / name)
    shutil.copy(SCRIPT, root / "scripts" / SCRIPT.name)
    return root


def perturb(root: Path, name: str, version: str) -> None:
    path = root / name
    if name == "pyproject.toml":
        text = path.read_text(encoding="utf-8")
        path.write_text(re.sub(r'^version = "[^"]+"', f'version = "{version}"', text, count=1,
                               flags=re.MULTILINE), encoding="utf-8")
    elif name == "CITATION.cff":
        text = path.read_text(encoding="utf-8")
        path.write_text(re.sub(r"^version:.*$", f"version: {version}", text, count=1,
                               flags=re.MULTILINE), encoding="utf-8")
    else:
        data = json.loads(path.read_text(encoding="utf-8"))
        data["version"] = version
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def test_repo_versions_agree() -> None:
    result = run()
    assert result.returncode == 0, result.stdout + result.stderr
    assert "all sources agree:" in result.stdout
    for name in ["pyproject.toml", ".claude-plugin/plugin.json", "CITATION.cff",
                 "server.json (version)", "server.json (packages[0].version)"]:
        assert name in result.stdout


def test_matching_tag_agrees() -> None:
    version = run().stdout.rsplit("all sources agree: ", 1)[1].strip()
    result = run("--tag", f"v{version}")
    assert result.returncode == 0, result.stdout + result.stderr
    assert f"git tag v{version}" in result.stdout


def test_mismatched_tag_fails() -> None:
    result = run("--tag", "v9.9.9")
    assert result.returncode == 1
    assert "git tag v9.9.9 says 9.9.9" in result.stdout


@pytest.mark.parametrize("name", VERSION_FILES)
def test_one_perturbed_field_fails_and_is_named(tmp_path: Path, name: str) -> None:
    root = repo_copy(tmp_path)
    perturb(root, name, "9.9.9")
    result = run("--root", str(root))
    assert result.returncode == 1, result.stdout + result.stderr
    assert "::error title=Version mismatch::" in result.stdout
    if name == "pyproject.toml":
        # pyproject is the reference, so every other source is named as disagreeing with it.
        assert "pyproject.toml says 9.9.9" in result.stdout
        assert ".claude-plugin/plugin.json says" in result.stdout
    else:
        expected = "server.json (version)" if name == "server.json" else name
        assert f"{expected} says 9.9.9" in result.stdout


def test_perturbing_only_server_packages_version_fails(tmp_path: Path) -> None:
    root = repo_copy(tmp_path)
    path = root / "server.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["packages"][0]["version"] = "9.9.9"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    result = run("--root", str(root))
    assert result.returncode == 1
    assert "server.json (packages[0].version) says 9.9.9" in result.stdout


def test_unperturbed_copy_passes(tmp_path: Path) -> None:
    result = run("--root", str(repo_copy(tmp_path)))
    assert result.returncode == 0, result.stdout + result.stderr
