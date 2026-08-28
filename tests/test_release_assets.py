# SPDX-License-Identifier: Apache-2.0
"""The release-asset contract: the manifest names the publishable set, exactly.

These tests are the rehearsal for a step that cannot otherwise be rehearsed. `release.yml`
accepts `workflow_dispatch`, but that runs the build job only — the release job, and this
verifier inside it, are gated on a tag push. Before v0.6.1 the first time the check ran on a
release was the release, which is how v0.6.0 published cleanly and then went red.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_release_assets as verifier  # noqa: E402

SKILL = "research-scan-skill-9.9.9.skill"
PLUGIN = "research-scan-plugin-9.9.9.zip"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@pytest.fixture
def release(tmp_path):
    """A built directory, a matching download, and the manifest that ties them together."""
    built, downloaded = tmp_path / "dist-assets", tmp_path / "roundtrip"
    built.mkdir()
    downloaded.mkdir()
    payloads = {SKILL: b"skill-bytes", PLUGIN: b"plugin-bytes"}
    for name, data in payloads.items():
        (built / name).write_bytes(data)
        (downloaded / name).write_bytes(data)
    manifest = tmp_path / "release-assets-manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "version": "9.9.9",
                "assets": [
                    {"name": name, "sha256": digest(data), "bytes": len(data)}
                    for name, data in payloads.items()
                ],
            }
        ),
        encoding="utf-8",
    )
    return manifest, built, downloaded


def run(manifest: Path, built: Path, downloaded: Path) -> int:
    return verifier.main(
        ["--manifest", str(manifest), "--built", str(built), "--downloaded", str(downloaded)]
    )


def test_an_exact_match_passes(release):
    assert run(*release) == 0


def test_a_stray_file_in_the_repositorys_assets_directory_is_irrelevant(release, tmp_path):
    """The v0.6.0 regression, locked.

    The builder used to write into the repository's tracked `assets/`, so the old glob picked
    up `assets/research-scan-logo.jpg` — a file that is not, and never was, a release asset —
    and failed the release for it. Nothing outside the manifest is consulted now.
    """
    stray = tmp_path / "assets"
    stray.mkdir()
    (stray / "research-scan-logo.jpg").write_bytes(b"not a release asset")
    (stray / "README.md").write_bytes(b"nor is this")

    assert run(*release) == 0


def test_an_extra_file_inside_the_build_directory_fails(release, capsys):
    manifest, built, downloaded = release
    (built / "unexpected.zip").write_bytes(b"where did this come from")

    assert run(manifest, built, downloaded) == 1
    assert "unexpected.zip" in capsys.readouterr().out


def test_an_unexpected_downloaded_release_asset_fails(release, capsys):
    manifest, built, downloaded = release
    (downloaded / "surprise.tar.gz").write_bytes(b"published but never built")

    assert run(manifest, built, downloaded) == 1
    out = capsys.readouterr().out
    assert "surprise.tar.gz" in out and "not named in the manifest" in out


def test_a_missing_asset_fails_and_names_it(release, capsys):
    manifest, built, downloaded = release
    (downloaded / PLUGIN).unlink()

    assert run(manifest, built, downloaded) == 1
    out = capsys.readouterr().out
    assert PLUGIN in out and "missing from the release" in out


def test_a_one_byte_difference_fails_and_prints_both_digests(release, capsys):
    manifest, built, downloaded = release
    original = (downloaded / SKILL).read_bytes()
    (downloaded / SKILL).write_bytes(original[:-1] + bytes([original[-1] ^ 0x01]))

    assert run(manifest, built, downloaded) == 1
    out = capsys.readouterr().out
    assert digest(original) in out, "the built digest is printed"
    assert digest((downloaded / SKILL).read_bytes()) in out, "the published digest is printed"


def test_an_empty_manifest_fails(release, capsys):
    """A glob over an empty directory iterates zero times and passes. This must not."""
    manifest, built, downloaded = release
    manifest.write_text(json.dumps({"version": "9.9.9", "assets": []}), encoding="utf-8")

    assert run(manifest, built, downloaded) == 1
    assert "lists no assets" in capsys.readouterr().out


@pytest.mark.parametrize(
    "body",
    ["{not json", json.dumps(["not", "an", "object"]), json.dumps({"version": "9.9.9"})],
    ids=["unparseable", "not-an-object", "no-assets-key"],
)
def test_a_malformed_manifest_fails(release, body, capsys):
    manifest, built, downloaded = release
    manifest.write_text(body, encoding="utf-8")

    assert run(manifest, built, downloaded) == 1
    assert "manifest" in capsys.readouterr().out


def test_a_missing_manifest_file_fails(release, tmp_path, capsys):
    _, built, downloaded = release

    assert run(tmp_path / "absent.json", built, downloaded) == 1
    assert "does not exist" in capsys.readouterr().out


def test_duplicate_manifest_names_fail(release, capsys):
    manifest, built, downloaded = release
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["assets"].append(dict(payload["assets"][0]))
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    assert run(manifest, built, downloaded) == 1
    assert "more than once" in capsys.readouterr().out


@pytest.mark.parametrize(
    "name",
    ["../escape.zip", "nested/asset.zip", "/absolute.zip", "back\\slash.zip"],
    ids=["parent", "separator", "absolute", "backslash"],
)
def test_unsafe_manifest_names_fail(release, name, capsys):
    """A name is joined to a directory, so it must be a bare filename — checked before use."""
    manifest, built, downloaded = release
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["assets"][0]["name"] = name
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    assert run(manifest, built, downloaded) == 1
    assert "bare filename" in capsys.readouterr().out


def test_the_builder_and_the_verifier_agree_on_the_real_tree(tmp_path):
    """Round-trip over this repository: what the builder writes is what the verifier expects."""
    built, manifest = tmp_path / "dist-assets", tmp_path / "manifest.json"
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_plugin_assets.py"),
         "--ref", "HEAD", "--out", str(built), "--manifest", str(manifest)],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert payload["assets"], "the builder must name what it built"
    for entry in payload["assets"]:
        target = built / entry["name"]
        assert target.is_file()
        assert digest(target.read_bytes()) == entry["sha256"]
        assert target.stat().st_size == entry["bytes"]

    # The published set is the built set: verifying the build directory against itself passes.
    assert run(manifest, built, built) == 0
