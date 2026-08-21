# SPDX-License-Identifier: Apache-2.0
"""Build the two release archives — the skill bundle and the Claude Code plugin.

One builder, used by CI and by hand, so a locally built asset and a CI-built asset are
byte-identical. Determinism comes from three choices: the tree is exported with
`git archive <ref>` rather than read from the working directory, so uncommitted files
cannot leak in; entries are written in sorted arcname order; and every entry carries a
fixed timestamp and mode, because a zip otherwise records the mtime of whatever machine
happened to build it. Rebuilding the same ref anywhere reproduces the same sha256.

The plugin archive is the plugin only. `marketplace.json` lives in the repository, not in
the artifact: the repo is its own marketplace, and shipping the catalog inside the entry
it lists is a loop with no purpose.

    python scripts/build_plugin_assets.py --ref vX.Y.Z --out dist/assets
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import zipfile
from pathlib import Path, PurePosixPath

# A zip entry records an mtime. Pinning it to the DOS epoch, the earliest a zip can
# express, is what makes two builds of one ref compare equal byte for byte.
FIXED_DATE_TIME = (1980, 1, 1, 0, 0, 0)
FIXED_MODE = 0o644
COMPRESS_LEVEL = 9

# The plugin's own files, in the layout Claude Code scans: the manifest under
# .claude-plugin/, the MCP definition at the plugin root, and skills/ beside them.
PLUGIN_MANIFEST = ".claude-plugin/plugin.json"
PLUGIN_MCP_CONFIG = ".mcp.json"
SKILLS_DIR = "skills"
SKILL_NAME = "research-scan"


def export_ref(ref: str, dest: Path) -> None:
    """Extract `ref`'s tree into `dest` via git archive."""
    archive = subprocess.run(
        ["git", "archive", "--format=tar", ref],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout
    with tempfile.NamedTemporaryFile(suffix=".tar") as handle:
        handle.write(archive)
        handle.flush()
        with tarfile.open(handle.name) as tar:
            tar.extractall(dest, filter="data")


def read_version(tree: Path) -> str:
    """The version the exported ref declares, which names both archives."""
    pyproject = tomllib.loads((tree / "pyproject.toml").read_text(encoding="utf-8"))
    version: str = pyproject["project"]["version"]
    return version


def files_under(root: Path) -> list[Path]:
    return [path for path in sorted(root.rglob("*")) if path.is_file()]


def write_zip(target: Path, members: list[tuple[str, Path]]) -> str:
    """Write `members` deterministically and return the archive's sha256."""
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=COMPRESS_LEVEL) as bundle:
        for arcname, source in sorted(members, key=lambda member: member[0]):
            info = zipfile.ZipInfo(arcname, date_time=FIXED_DATE_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = FIXED_MODE << 16
            bundle.writestr(info, source.read_bytes())
    return hashlib.sha256(target.read_bytes()).hexdigest()


def skill_members(tree: Path) -> list[tuple[str, Path]]:
    """The skill directory under a `research-scan/` prefix — the claude.ai upload shape."""
    root = tree / SKILLS_DIR / SKILL_NAME
    if not root.is_dir():
        raise SystemExit(f"error: {SKILLS_DIR}/{SKILL_NAME}/ is missing from the exported ref")
    return [
        (str(PurePosixPath(SKILL_NAME) / path.relative_to(root)), path)
        for path in files_under(root)
    ]


def plugin_members(tree: Path) -> list[tuple[str, Path]]:
    """The plugin, and nothing else — no marketplace.json, no src/, tests/, docs/ or runs."""
    members: list[tuple[str, Path]] = []
    for relative in (PLUGIN_MANIFEST, PLUGIN_MCP_CONFIG):
        path = tree / relative
        if not path.is_file():
            raise SystemExit(f"error: {relative} is missing from the exported ref")
        members.append((relative, path))
    members += [(str(path.relative_to(tree)), path) for path in files_under(tree / SKILLS_DIR)]
    return members


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ref", required=True, help="git ref to build from (tag, branch or SHA)")
    parser.add_argument("--out", required=True, type=Path, help="directory to write archives into")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as staging:
        tree = Path(staging)
        export_ref(args.ref, tree)
        version = read_version(tree)

        built = [
            (args.out / f"research-scan-skill-{version}.skill", skill_members(tree)),
            (args.out / f"research-scan-plugin-{version}.zip", plugin_members(tree)),
        ]
        for target, members in built:
            digest = write_zip(target, members)
            print(f"{digest}  {target.name}")
            for arcname, _ in sorted(members, key=lambda member: member[0]):
                print(f"    {arcname}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
