# SPDX-License-Identifier: Apache-2.0
"""Check a published release's assets against the manifest the builder emitted.

The manifest is the contract, not a hint: it names the exact publishable set. That is what
makes this check answer both questions a release needs answered, and it is why the previous
shape — a glob over the build directory — answered neither reliably.

* A file the manifest does not name is never consulted, wherever it sits. The repository's
  own `assets/research-scan-logo.jpg` is the case that broke v0.6.0: the builder wrote its
  archives into the tracked `assets/` directory, the verifier globbed that directory, and a
  file that was never a release asset failed the release after a wholly successful publish.
* A file the manifest names and the release does not carry is a failure, by name. A glob
  cannot see this at all: iterate an empty directory and the loop passes vacuously.

Both directions are checked, because "extra" and "missing" are different faults and a release
that quietly grew an asset is as wrong as one that quietly lost one.

    python scripts/verify_release_assets.py \
        --manifest dist/release-assets-manifest.json \
        --built dist-assets --downloaded roundtrip
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

#: A manifest name is a bare filename. Anything that could escape the directory it is joined
#: to — a separator, a parent reference, an absolute path — is rejected before it is used to
#: build a path, not after.
_UNSAFE = ("/", "\\", "..")


def load_manifest(path: Path) -> tuple[dict, list[str]]:
    """Return (manifest, problems). A manifest that cannot be trusted yields no assets."""
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}, [f"manifest {path} does not exist"]
    except json.JSONDecodeError as exc:
        return {}, [f"manifest {path} is not valid JSON: {exc}"]

    if not isinstance(manifest, dict):
        return {}, [f"manifest {path} is not an object"]
    assets = manifest.get("assets")
    if not isinstance(assets, list):
        return {}, [f"manifest {path} has no `assets` array"]
    if not assets:
        return {}, [f"manifest {path} lists no assets — nothing was built"]

    problems: list[str] = []
    seen: set[str] = set()
    for index, entry in enumerate(assets):
        if not isinstance(entry, dict):
            problems.append(f"manifest asset {index} is not an object")
            continue
        name, digest = entry.get("name"), entry.get("sha256")
        if not isinstance(name, str) or not name:
            problems.append(f"manifest asset {index} has no name")
            continue
        if any(token in name for token in _UNSAFE) or Path(name).is_absolute():
            problems.append(f"manifest asset {name!r} is not a bare filename")
            continue
        if not isinstance(digest, str) or len(digest) != 64:
            problems.append(f"{name}: manifest carries no usable sha256")
            continue
        if name in seen:
            problems.append(f"{name}: named more than once in the manifest")
            continue
        seen.add(name)
    return manifest, problems


def digest_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(manifest: dict, built: Path | None, downloaded: Path) -> list[str]:
    """Compare the published set, and the built set when given, against the manifest."""
    problems: list[str] = []
    expected = {entry["name"]: entry["sha256"] for entry in manifest["assets"]}

    for name, want in sorted(expected.items()):
        target = downloaded / name
        if not target.is_file():
            problems.append(f"{name}: named in the manifest but missing from the release")
            continue
        got = digest_of(target)
        print(f"{name}\n  built:     {want}\n  published: {got}")
        if got != want:
            problems.append(f"{name}: built {want}, published {got}")

    surplus = sorted(p.name for p in downloaded.iterdir() if p.is_file() and p.name not in expected)
    for name in surplus:
        problems.append(f"{name}: on the release but not named in the manifest")

    if built is not None:
        extra = sorted(p.name for p in built.iterdir() if p.is_file() and p.name not in expected)
        for name in extra:
            problems.append(f"{name}: in the build directory but not named in the manifest")

    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--downloaded", required=True, type=Path, help="assets fetched back")
    parser.add_argument("--built", type=Path, help="the build output directory, checked for extras")
    args = parser.parse_args(argv)

    manifest, problems = load_manifest(args.manifest)
    if not problems:
        problems = verify(manifest, args.built, args.downloaded)

    if problems:
        for problem in problems:
            print(f"::error title=Release asset mismatch::{problem}")
        return 1
    print(f"{len(manifest['assets'])} asset(s) match the manifest.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
