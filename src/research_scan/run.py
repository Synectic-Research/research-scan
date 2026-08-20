# SPDX-License-Identifier: Apache-2.0
"""The run directory: create it, find it, read and write the files inside it.

Every stage after `init` needs the same four things — locate the run, load a JSON file as a
validated model, resolve a parameter across the three precedence layers, and upsert its own
manifest section without trampling anyone else's. They live here so `cli.py` stays a thin
argument-parsing layer and later slices do not each reinvent them.

Not in spec §5's module list; added deliberately (see AGENTS.md).
"""

from __future__ import annotations

import calendar
import json
import re
from collections.abc import Mapping
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from research_scan import __version__, schema
from research_scan.config import Settings
from research_scan.schema import Defaults, Manifest, RunInfo, Window

ModelT = TypeVar("ModelT", bound=BaseModel)

RUNS_ROOT = Path("research") / "scans"
DEFAULT_WINDOW_MONTHS = 36
MAX_SLUG_LENGTH = 40

_SLUG_STRIP = re.compile(r"[^a-z0-9]+")


class StageInputError(Exception):
    """A stage's input file is missing or invalid. The CLI turns this into exit 2 (§6)."""

    def __init__(self, message: str, *, lines: list[str] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.lines = lines or []

    def payload(self) -> dict[str, Any]:
        return {"ok": False, "error": self.message, "errors": self.lines}


def today() -> date:
    """Seam: tests freeze this so a run's outputs are byte-identical across invocations."""
    return date.today()


def now() -> datetime:
    """Seam for stage timestamps. Timezone-aware so runs stay comparable across machines."""
    return datetime.now(UTC)


# --- stage timestamps -------------------------------------------------------


def stamp(
    existing: Mapping[str, str] | None, stage: str, started: datetime, finished: datetime
) -> dict[str, str]:
    """Record one stage's start and finish, leaving every other stage's pair untouched.

    Flat dotted keys (`retrieve.started_at`) rather than nesting, so re-running a stage overwrites
    exactly its own two entries — the same ownership rule the manifest sections follow (§9.9).
    """
    stamped = dict(existing or {})
    stamped[f"{stage}.started_at"] = started.isoformat(timespec="seconds")
    stamped[f"{stage}.finished_at"] = finished.isoformat(timespec="seconds")
    return stamped


def wall_clock_seconds(timestamps: Mapping[str, str] | None) -> float | None:
    """`init.started_at` → the latest `*.finished_at`, which is what a human means by "how long".

    Returns None when `init` never stamped — an older run, or one assembled by hand.
    """
    timestamps = timestamps or {}
    start = timestamps.get("init.started_at")
    if not start:
        return None
    finishes = [value for key, value in timestamps.items() if key.endswith(".finished_at")]
    if not finishes:
        return None
    try:
        began = datetime.fromisoformat(start)
        ended = max(datetime.fromisoformat(value) for value in finishes)
    except ValueError:
        return None
    return round(max(0.0, (ended - began).total_seconds()), 1)


# --- window -----------------------------------------------------------------


def months_ago(anchor: date, months: int) -> date:
    total = anchor.year * 12 + (anchor.month - 1) - months
    year, month = divmod(total, 12)
    return date(year, month + 1, 1)


def default_window(anchor: date | None = None) -> Window:
    """36 months back → today (spec §6 defaults table)."""
    start = months_ago(anchor or today(), DEFAULT_WINDOW_MONTHS)
    return Window(from_=f"{start.year:04d}-{start.month:02d}", to=None)


def window_bounds(window: Window | None, anchor: date | None = None) -> tuple[date, date]:
    """`YYYY-MM` months → inclusive day bounds. `to: null` means today."""
    anchor = anchor or today()
    window = window or default_window(anchor)

    if window.from_:
        year, month = (int(part) for part in window.from_.split("-"))
        start = date(year, month, 1)
    else:
        start = months_ago(anchor, DEFAULT_WINDOW_MONTHS)

    if window.to:
        year, month = (int(part) for part in window.to.split("-"))
        end = date(year, month, calendar.monthrange(year, month)[1])
    else:
        end = anchor

    return start, end


# --- run directories --------------------------------------------------------


def slugify(text: str) -> str:
    slug = _SLUG_STRIP.sub("-", text.casefold()).strip("-")
    return slug[:MAX_SLUG_LENGTH].strip("-") or "scan"


def derive_slug(brief_arg: str, brief_path: Path | None) -> str:
    """A file's stem, or the first words of a bare question."""
    if brief_path is not None:
        return slugify(brief_path.stem)
    return slugify(" ".join(brief_arg.split()[:6]))


def create_run(
    brief_arg: str,
    *,
    slug: str | None = None,
    defaults: Defaults | None = None,
    root: Path | None = None,
    anchor: date | None = None,
) -> RunInfo:
    """Create `research/scans/<date>-<slug>/` with `brief.md` and `manifest.json`.

    `brief_arg` is either a path to a brief or the question itself (spec §6).
    """
    started = now()
    anchor = anchor or today()
    root = root or RUNS_ROOT

    source_path = Path(brief_arg)
    brief_path = source_path if source_path.is_file() else None
    resolved_slug = slugify(slug) if slug else derive_slug(brief_arg, brief_path)

    run_dir = root / f"{anchor.isoformat()}-{resolved_slug}"
    run_dir.mkdir(parents=True, exist_ok=True)

    brief_target = run_dir / "brief.md"
    if brief_path is not None:
        brief_target.write_text(brief_path.read_text(encoding="utf-8"), encoding="utf-8")
    else:
        brief_target.write_text(f"# {resolved_slug}\n\n{brief_arg.strip()}\n", encoding="utf-8")

    info = RunInfo(
        run_dir=str(run_dir),
        slug=resolved_slug,
        date=anchor.isoformat(),
        brief_path=str(brief_target),
        defaults=defaults or Defaults(window=default_window(anchor)),
    )
    write_manifest(
        run_dir,
        Manifest(
            run=info,
            defaults=info.defaults,
            tool_version=__version__,
            timestamps=stamp(None, "init", started, now()),
        ),
    )
    return info


def resolve_run_dir(explicit: str | None, settings: Settings, root: Path | None = None) -> Path:
    """`--run` > `$RESEARCH_SCAN_RUN` > newest directory under `research/scans/` (§6)."""
    if explicit:
        path = Path(explicit)
    elif settings.run_dir:
        path = Path(settings.run_dir)
    else:
        path = newest_run(root)
        if path is None:
            raise StageInputError(
                f"no run directory found under {(root or RUNS_ROOT)}/ —"
                " run `research-scan init <brief.md>` first"
            )
    if not path.is_dir():
        raise StageInputError(f"run directory does not exist: {path}")
    return path


def newest_run(root: Path | None = None) -> Path | None:
    root = root or RUNS_ROOT
    if not root.is_dir():
        return None
    runs = sorted((path for path in root.iterdir() if path.is_dir()), key=lambda p: p.name)
    return runs[-1] if runs else None


# --- files ------------------------------------------------------------------


def read_model(path: Path, model: type[ModelT]) -> ModelT:
    """Load and validate a stage file, or raise the error list the agent has to fix (§6)."""
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise StageInputError(f"cannot read {path}: {exc.strerror or exc}") from exc

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise StageInputError(
            f"{path} is not valid JSON", lines=[f"line {exc.lineno}: {exc.msg}"]
        ) from exc

    try:
        return model.model_validate(payload)
    except ValidationError as exc:
        raise StageInputError(
            f"{path} does not match the {model.__name__} contract",
            lines=schema.format_errors(exc),
        ) from exc


def write_model(path: Path, instance: BaseModel) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(instance.model_dump(mode="json", by_alias=True), indent=2) + "\n",
        encoding="utf-8",
    )


def manifest_path(run_dir: Path) -> Path:
    return run_dir / "manifest.json"


def read_manifest(run_dir: Path) -> Manifest:
    return read_model(manifest_path(run_dir), Manifest)


def write_manifest(run_dir: Path, manifest: Manifest) -> None:
    write_model(manifest_path(run_dir), manifest)


def upsert_manifest(run_dir: Path, **sections: Any) -> Manifest:
    """Update only the named sections. Each command owns one; none may clobber another's (§9.9)."""
    manifest = read_manifest(run_dir)
    updated = manifest.model_copy(update=sections)
    write_manifest(run_dir, updated)
    return updated


# --- parameter precedence ---------------------------------------------------


def resolve(*layers: Any) -> Any:
    """Precedence: flag > `queries.json` > `manifest.defaults` (§6). First non-None wins."""
    for candidate in layers:
        if candidate is not None:
            return candidate
    return None
