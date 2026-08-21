#!/usr/bin/env python3
"""The 5-way version guard: every file that carries the version must carry the same one.

Four files claim a version, and server.json claims it twice. A release that moves only
some of them ships a package whose plugin manifest, citation record or registry entry
disagrees with the wheel. On a tag, the tag is a sixth claim and has to agree too.

    python3 scripts/check_versions.py                # the five file claims
    python3 scripts/check_versions.py --tag v0.5.1   # ...and the tag

Exit 0 iff every claim agrees; exit 1 naming each source that disagrees with
pyproject.toml, which is the reference. Stdlib only, so CI can run it on a bare
interpreter without installing the project first.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import tomllib

ROOT = pathlib.Path(__file__).resolve().parent.parent


def cff_version(path: pathlib.Path) -> str:
    """Read CITATION.cff's top-level `version:` without a YAML parser.

    Anchoring at column 0 is what makes this safe: in CFF the key is top-level, and a
    nested `version:` under `references:` is indented and cannot match.
    """
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^version:[ \t]*(.+?)[ \t]*$", text, re.MULTILINE)
    if not match:
        sys.exit(f"{path.name} has no top-level `version:` — the guard cannot check it.")
    value = match.group(1)
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value


def claims_for(root: pathlib.Path, tag: str | None) -> dict[str, str]:
    claims: dict[str, str] = {}

    claims["pyproject.toml"] = tomllib.loads(
        (root / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]["version"]

    claims[".claude-plugin/plugin.json"] = json.loads(
        (root / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
    )["version"]

    claims["CITATION.cff"] = cff_version(root / "CITATION.cff")

    server = json.loads((root / "server.json").read_text(encoding="utf-8"))
    claims["server.json (version)"] = server["version"]
    claims["server.json (packages[0].version)"] = server["packages"][0]["version"]

    if tag:
        claims[f"git tag {tag}"] = tag.removeprefix("v")

    return claims


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tag", help="a tag ref name, e.g. v0.5.1; adds it as a sixth claim")
    parser.add_argument(
        "--root", type=pathlib.Path, default=ROOT, help="repo root (default: this repo)"
    )
    args = parser.parse_args()

    claims = claims_for(args.root, args.tag)
    for source, version in claims.items():
        print(f"  {source}: {version}")

    distinct = set(claims.values())
    if len(distinct) != 1:
        expected = claims["pyproject.toml"]
        for source, version in claims.items():
            if version != expected:
                print(
                    f"::error title=Version mismatch::{source} says {version}, "
                    f"pyproject.toml says {expected}. Move every version together; "
                    f"do not publish this build."
                )
        return 1

    print(f"\nall sources agree: {distinct.pop()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
