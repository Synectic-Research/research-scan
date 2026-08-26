"""`research-scan init` for one golden topic, relocated under the experiment tree.

`init` always writes to `research/scans/<date>-<slug>/` (RUNS_ROOT is relative to the repo
root and not configurable), so the run is created there and then moved under
research/experiments/phase11-golden/runs/ with `manifest.run.run_dir` and `brief_path`
repointed at the copy — the same relocation Phase 1 used for its rerank arms. Nothing is left
behind under research/scans/.

Usage:  python setup_run.py <topic>
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import common as C  # noqa: E402


def main() -> None:
    topic = sys.argv[1]
    cfg = C.TOPICS[topic]
    dest = C.run_dir(topic)
    if dest.exists():
        sys.exit(f"{dest} already exists — remove it to re-init")

    code, out = C.run_cli([
        "research-scan", "init", str(cfg["brief"]),
        "--slug", cfg["slug"],
        "--domain", cfg["domain"],
        "--from", cfg["window_from"],
        "--profile", C.PROFILE,
        "--top", str(C.TOP),
        "--foundational", str(C.FOUNDATIONAL),
        "--json", "--quiet",
    ])
    if code != 0:
        sys.exit(f"init failed ({code}): {out}")
    info = json.loads(out)
    created = C.REPO / info["run_dir"]

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(created), str(dest))
    manifest = json.loads((dest / "manifest.json").read_text())
    manifest["run"]["run_dir"] = str(dest)
    manifest["run"]["brief_path"] = str(dest / "brief.md")
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=1))

    print(json.dumps({"topic": topic, "run_dir": str(dest),
                      "defaults": manifest["run"]["defaults"]}, indent=1))


if __name__ == "__main__":
    main()
