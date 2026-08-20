# SPDX-License-Identifier: Apache-2.0
"""Remote MCP adapter — the same pipeline, driven over the wire instead of over the filesystem.

`SKILL.md` already holds every judgement this tool makes: the queries, the screening scores, the
gap queries, the rerank. Locally those arrive as files in a run directory; here they arrive as MCP
tool arguments and are written to exactly the same files. Nothing in this module decides anything
about papers.

What lives here, and nothing else: tool definitions, authentication, input validation, the
`scan_id` → run-directory mapping, invocation of the existing CLI, deterministic bridging between
its stages, compact serialization, structured errors, one log line per call.

The stage order is the repository's, unchanged:

    retrieve → screen → expand → screen → conditional gap round → screen → shortlist
    → rank → verify → emit

Stages run as subprocesses of the installed `research-scan` CLI, so the engine is untouched by
this file and its measured behaviour is the behaviour a remote scan gets. Exit codes are the
CLI's documented contract (0 ok · 1 runtime · 2 input/schema · 3 doctor), and every non-zero exit
is read from the structured JSON the CLI writes to stderr, never from the bare code.
"""

from __future__ import annotations

import asyncio
import contextlib
import hmac
import json
import logging
import os
import shutil
import subprocess
import sys
import threading
import time
import uuid
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Any

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_http_request
from fastmcp.server.middleware import Middleware, MiddlewareContext
from pydantic import Field
from starlette.applications import Starlette
from starlette.routing import Mount

from research_scan import __version__, config
from research_scan import coverage as coverage_module
from research_scan import run as run_module
from research_scan import shortlist as shortlist_module
from research_scan.schema import (
    CandidatesFile,
    CoverageFile,
    Evidence,
    Manifest,
    Profile,
    Query,
    QueryPlan,
    Ranked,
    RankedEntry,
    ScreenFile,
    ScreenScore,
    Shortlist,
)

logger = logging.getLogger(__name__)

#: One existing screen batch per response; the batch itself is already capped at 25 by `retrieve`.
#: Rank pages are smaller because `shortlist.json` carries full records with full abstracts.
RANK_PAGE = 10

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765

#: Every scan's subprocess work is serialized: the HTTP cache is one sqlite file without WAL and
#: the rate limiter is per-process, so two concurrent scans would multiply the request rate at the
#: sources. V1 is single-process by design; a second scan waits rather than racing.
_LOCK = threading.Lock()
_HELD_BY: str | None = None


# --- structured failure ------------------------------------------------------


class ScanFailure(Exception):
    """A refusal the model can act on: bad artifact, wrong phase, or a stage that failed.

    Carries the engine's own words. This module never rewrites an engine message, and never
    invents a recovery the engine did not offer.
    """

    def __init__(
        self,
        status: str,
        message: str,
        *,
        lines: list[str] | None = None,
        code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.message = message
        self.lines = lines or []
        #: Set where the model needs to branch on the refusal rather than read it.
        self.code = code


# --- the CLI, as a subprocess ------------------------------------------------


def cli_binary() -> str:
    """The `research-scan` executable: explicit override, our own venv, then PATH."""
    override = os.environ.get("RESEARCH_SCAN_BIN")
    if override:
        return override
    beside = Path(sys.executable).with_name("research-scan")
    if beside.exists():
        return str(beside)
    found = shutil.which("research-scan")
    if not found:
        raise ScanFailure("failed", "the research-scan CLI is not installed on this server")
    return found


@dataclass(frozen=True)
class StageOutcome:
    """One CLI invocation. `payload` is stdout's JSON on success, stderr's on a structured exit."""

    stage: str
    code: int
    payload: dict[str, Any]
    stderr: str

    @property
    def ok(self) -> bool:
        return self.code == 0


def run_stage(cwd: Path, stage: str, *args: str) -> StageOutcome:
    """Invoke one CLI stage in the scan's own directory. Never raises on a non-zero exit."""
    argv = [cli_binary(), stage, *args, "--json"]
    started = time.monotonic()
    completed = subprocess.run(  # noqa: S603 - argv is built here, never from model input
        argv, cwd=cwd, capture_output=True, text=True, check=False
    )
    logger.debug(
        "stage %s exit=%d in %.1fs", stage, completed.returncode, time.monotonic() - started
    )
    stream = completed.stdout if completed.returncode == 0 else completed.stderr
    payload: dict[str, Any] = {}
    try:
        parsed = json.loads(stream)
        if isinstance(parsed, dict):
            payload = parsed
    except (json.JSONDecodeError, TypeError):
        payload = {}
    return StageOutcome(
        stage=stage, code=completed.returncode, payload=payload, stderr=completed.stderr
    )


def check(outcome: StageOutcome, *, tolerate_structured: bool = False) -> StageOutcome:
    """Turn a non-zero exit into a `ScanFailure`, reading the CLI's stderr JSON, never the code.

    `retrieve`'s `AllSourcesFailed`, `expand`'s `NoSeeds` and an uncaught traceback all exit 1 and
    none of them names a type, so the caller says which invocation may legitimately come back
    empty — only `expand --round 2`, which SKILL.md §4.5 documents as a normal outcome.
    """
    if outcome.ok:
        return outcome

    structured = bool(outcome.payload) and outcome.payload.get("ok") is False
    if not structured:
        tail = outcome.stderr.strip().splitlines()[-5:]
        raise ScanFailure(
            "failed",
            f"`research-scan {outcome.stage}` exited {outcome.code} without a structured error",
            lines=tail,
        )

    message = str(outcome.payload.get("error", "")) or f"{outcome.stage} failed"
    # `errors` is optional: only `_fail_stage` (exit 2) writes the repair list.
    lines = [str(line) for line in outcome.payload.get("errors", [])]

    if outcome.code == 1 and tolerate_structured:
        logger.info("stage %s came back empty: %s", outcome.stage, message)
        return outcome
    status = "invalid_artifact" if outcome.code == 2 else "failed"
    raise ScanFailure(status, message, lines=lines)


# --- scan directories --------------------------------------------------------


def scan_root(settings: config.Settings, scan_id: str) -> Path:
    """`$RESEARCH_SCAN_MCP_DATA/<scan_id>/`. The CLI's own relative `research/scans/` lands here."""
    return settings.mcp_data_dir / scan_id


def valid_scan_id(scan_id: str) -> str:
    """A canonical lowercase UUIDv4 and nothing else.

    The id is the client's retry handle and a directory name, so it has to round-trip exactly:
    `uuid.UUID(value, version=4)` rewrites the version and variant bits, which means a v1 id, a
    braced or `urn:` form, an undashed hex string and an uppercase id all fail the round-trip and
    are refused here rather than opening a second directory for the same scan.
    """
    value = scan_id if isinstance(scan_id, str) else ""
    try:
        parsed: uuid.UUID | None = uuid.UUID(value, version=4)
    except (ValueError, AttributeError, TypeError):
        parsed = None
    if parsed is None or str(parsed) != value or value.lower() != value:
        raise ScanFailure(
            "invalid_artifact",
            f"scan_id must be a canonical lowercase UUIDv4: {scan_id!r}",
            code="invalid_scan_id",
        )
    return value


def options_path(root: Path) -> Path:
    """Server-owned, outside the run directory: the start inputs, and the retry fingerprint.

    Written before `init` runs, so a `scan_start` that dies mid-retrieve still leaves the record a
    retry is compared against.
    """
    return root / "mcp-options.json"


def canonical(options: Mapping[str, Any]) -> str:
    """One byte sequence per set of inputs, so a retry is a string comparison."""
    return json.dumps(options, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def start_inputs(
    *,
    brief: str,
    queries: QueryPlan,
    profile: Profile,
    top: int,
    foundational: int,
    since: str | None,
    until: str | None,
    slug: str | None,
    max_candidates: int | None,
    per_query: int | None,
    force_gap_round: bool,
) -> dict[str, Any]:
    """Every `scan_start` argument except the id itself — what a retry has to match."""
    return {
        "brief": brief,
        "queries": queries.model_dump(mode="json", by_alias=True),
        "profile": profile.value,
        "top": top,
        "foundational": foundational,
        "since": since,
        "until": until,
        "slug": slug,
        "max_candidates": max_candidates,
        "per_query": per_query,
        "force_gap_round": bool(force_gap_round),
    }


def differing_keys(incoming: Mapping[str, Any], persisted: Mapping[str, Any]) -> list[str]:
    """Names only. The brief runs to paragraphs and the query plan to kilobytes."""
    names = sorted(set(incoming) | set(persisted))
    return [
        name
        for name in names
        if canonical({name: incoming.get(name)}) != canonical({name: persisted.get(name)})
    ]


def read_options(root: Path) -> dict[str, Any]:
    try:
        return json.loads(options_path(root).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def write_options(root: Path, options: Mapping[str, Any]) -> None:
    options_path(root).write_text(canonical(options), encoding="utf-8")


def runs_root(root: Path) -> Path:
    """`research/scans/` under this scan's directory: the CLI's relative root, made absolute."""
    return root / run_module.RUNS_ROOT


def find_run_dir(root: Path) -> Path | None:
    """One scan holds one run, so `newest_run` is also the only run. The engine owns the lookup."""
    return run_module.newest_run(runs_root(root))


# --- the state on disk -------------------------------------------------------

#: Screening batches, in the order the pipeline writes them: retrieval, expansion, then the gap
#: round's own two families. `retrieve`/`expand` own these names; this only reads them.
BATCH_FAMILIES = ("", "x", "r", "xr")


def batch_family(name: str) -> str:
    return "".join(character for character in name if character.isalpha())


@dataclass
class ScanState:
    """Everything the phase machine needs, read from the run directory. No state of its own."""

    root: Path
    run_dir: Path | None = None
    manifest: Manifest | None = None
    plan: QueryPlan | None = None
    candidates: CandidatesFile | None = None
    screen: ScreenFile | None = None
    coverage: CoverageFile | None = None
    shortlist: Shortlist | None = None
    ranked: Ranked | None = None
    evidence_exists: bool = False
    expanded_exists: bool = False
    batches: list[Path] = field(default_factory=list)

    @property
    def scored(self) -> dict[str, ScreenScore]:
        return {entry.cid: entry for entry in (self.screen.scores if self.screen else [])}

    @property
    def ranked_cids(self) -> set[str]:
        return {entry.cid for entry in (self.ranked.root if self.ranked else [])}

    @property
    def in_gap_round(self) -> bool:
        """`coverage` decides which round a plan is in; the adapter only asks it."""
        return self.plan is not None and coverage_module.current_round(self.plan) == 2

    @property
    def shortlist_records(self) -> list[Any]:
        if not self.shortlist:
            return []
        return [*self.shortlist.in_window, *self.shortlist.outside_window]

    def next_batch(self) -> Path | None:
        """The first batch with an unscored item, in pipeline order."""
        scored = set(self.scored)
        for path in self.batches:
            cids = {item["cid"] for item in json.loads(path.read_text(encoding="utf-8"))["items"]}
            if cids - scored:
                return path
        return None

    def batch_progress(self) -> tuple[int, int]:
        scored = set(self.scored)
        done = 0
        for path in self.batches:
            cids = {item["cid"] for item in json.loads(path.read_text(encoding="utf-8"))["items"]}
            if not (cids - scored):
                done += 1
        return done, len(self.batches)


def _maybe(path: Path, model):
    if not path.exists():
        return None
    try:
        return run_module.read_model(path, model)
    except run_module.StageInputError:
        return None


def read_state(root: Path) -> ScanState:
    state = ScanState(root=root, run_dir=find_run_dir(root))
    directory = state.run_dir
    if directory is None:
        return state

    state.manifest = _maybe(directory / "manifest.json", Manifest)
    state.plan = _maybe(directory / "queries.json", QueryPlan)
    state.candidates = _maybe(directory / "candidates.json", CandidatesFile)
    state.screen = _maybe(directory / "screen.json", ScreenFile)
    state.coverage = _maybe(directory / "coverage.json", CoverageFile)
    state.shortlist = _maybe(directory / "shortlist.json", Shortlist)
    state.ranked = _maybe(directory / "ranked.json", Ranked)
    state.evidence_exists = (directory / "evidence.json").exists()
    state.expanded_exists = (directory / "expanded.json").exists()

    batches = (directory / "screen-batches").glob("*.json")
    state.batches = sorted(
        batches, key=lambda path: (BATCH_FAMILIES.index(batch_family(path.stem)), path.stem)
    )
    return state


# --- the bridge between stages ----------------------------------------------


def expand_round2_attempted(state: ScanState) -> bool:
    if state.manifest is not None and state.manifest.expansion_round2 is not None:
        return True
    return any(batch_family(path.stem) == "xr" for path in state.batches)


def coverage_round2_recorded(state: ScanState) -> bool:
    return bool(state.coverage) and any(entry.round == 2 for entry in state.coverage.rounds)


def next_stage(state: ScanState, skip: set[str]) -> tuple[str, list[str]] | None:
    """The next deterministic stage, or None when the pipeline needs a model decision.

    This is the repository's frozen order and nothing else. `None` means exactly one thing: the
    conditional gap round asked for gap queries, which only the model can write.
    """
    if not state.expanded_exists:
        return "expand", []
    if state.coverage is None:
        return "coverage", []

    advice = state.coverage.gap_round
    if advice and advice.should_run and not state.in_gap_round and "gap" not in skip:
        return None

    if state.in_gap_round:
        if state.manifest is None or state.manifest.retrieval_round2 is None:
            return "retrieve", ["--round", "2"]
        if not expand_round2_attempted(state) and "expand-r2" not in skip:
            return "expand", ["--round", "2"]
        if not coverage_round2_recorded(state):
            return "coverage", []
    return "shortlist", []


def stage_args(stage: str, args: list[str], options: dict[str, Any]) -> list[str]:
    """Deferred `scan_start` flags, routed to the stage that owns them (SKILL.md:15)."""
    extra: list[str] = []
    if stage == "coverage" and options.get("force_gap_round"):
        extra.append("--gap-round")
    if stage == "retrieve":
        if options.get("max_candidates"):
            extra += ["--max-candidates", str(options["max_candidates"])]
        if options.get("per_query"):
            extra += ["--per-query", str(options["per_query"])]
    return [*args, *extra]


def advance(root: Path, skip: set[str] | None = None) -> ScanState:
    """Run deterministic stages until the pipeline needs the model again."""
    skipped = set(skip or ())
    options = read_options(root)
    state = read_state(root)
    while True:
        if state.evidence_exists or state.shortlist is not None:
            return state
        if state.next_batch() is not None:
            return state

        stage = next_stage(state, skipped)
        if stage is None:
            return state

        name, args = stage
        gap_expand = name == "expand" and "2" in args
        argv = stage_args(name, args, options)
        check(
            run_stage(root, name, "--run", str(state.run_dir), *argv),
            tolerate_structured=gap_expand,
        )
        if gap_expand:
            # `NoSeeds` here is a documented outcome (SKILL.md §4.5); do not ask for it twice.
            skipped.add("expand-r2")
        state = read_state(root)


# --- envelope ----------------------------------------------------------------


def rank_page_index(state: ScanState) -> int:
    """The first page holding an unranked record; 1-based, so a retry of page N repeats page N."""
    ranked = state.ranked_cids
    records = state.shortlist_records
    for index, record in enumerate(records):
        if record.cid not in ranked:
            return index // RANK_PAGE + 1
    return 0


def progress_of(state: ScanState) -> dict[str, Any]:
    scored, total = state.batch_progress()
    progress: dict[str, Any] = {"batches_scored": scored, "batches_total": total}
    if state.manifest is not None:
        progress["counts"] = state.manifest.counts.model_dump(mode="json", exclude_none=True)
    if state.shortlist is not None:
        records = len(state.shortlist_records)
        pages = max(1, -(-records // RANK_PAGE))
        page = rank_page_index(state)
        progress["ranked"] = len(state.ranked_cids)
        progress["shortlisted"] = records
        progress["page"] = page or pages
        progress["of"] = pages
    return progress


def decision(state: ScanState) -> tuple[str, str | None, dict[str, Any]]:
    """Phase, next_action, and the payload that decision needs. Checked latest stage first."""
    if state.evidence_exists:
        return "complete", "complete", {}

    if state.shortlist is not None:
        page = rank_page_index(state)
        if page == 0:
            return "rank", "verify_ranked", {}
        raw = json.loads((state.run_dir / "shortlist.json").read_text(encoding="utf-8"))
        records = [*raw["in_window"], *raw["outside_window"]]
        window = records[(page - 1) * RANK_PAGE : page * RANK_PAGE]
        return "rank", "rank_shortlist", {"shortlist_records": window}

    batch = state.next_batch()
    if batch is not None:
        return "screen", "screen_candidates", {
            "screen_batch": json.loads(batch.read_text(encoding="utf-8"))
        }

    advice = state.coverage.gap_round if state.coverage else None
    if advice and advice.should_run and not state.in_gap_round:
        latest = state.coverage.rounds[-1] if state.coverage.rounds else None
        return "gap", "write_gap_queries", {
            "gap_round": advice.model_dump(mode="json"),
            "coverage": latest.model_dump(mode="json") if latest else {},
            "thin": coverage_module.thin_criteria(latest) if latest else [],
        }

    return "unknown", None, {}


def envelope(scan_id: str, state: ScanState, **payload: Any) -> dict[str, Any]:
    phase, next_action, decided = decision(state)
    return {
        "scan_id": scan_id,
        "phase": phase,
        "status": "ok",
        "next_action": next_action,
        "progress": progress_of(state),
        "payload": {**decided, **payload},
    }


def busy_envelope(scan_id: str, status: str) -> dict[str, Any]:
    message = (
        "an earlier call for this scan is still running — do not resubmit; poll scan_result"
        if status == "in_progress"
        else "another scan holds the pipeline; retry shortly"
    )
    return {
        "scan_id": scan_id,
        "phase": "unknown",
        "status": status,
        "next_action": None,
        "progress": {},
        "payload": {"error": message},
    }


def failure_envelope(scan_id: str, failure: ScanFailure, state: ScanState | None) -> dict[str, Any]:
    phase = decision(state)[0] if state is not None else "unknown"
    payload: dict[str, Any] = {"error": failure.message, "errors": failure.lines}
    if failure.code:
        payload["code"] = failure.code
    return {
        "scan_id": scan_id,
        "phase": phase,
        "status": failure.status,
        "next_action": None,
        "progress": progress_of(state) if state is not None else {},
        "payload": payload,
    }


# --- model artifacts: validate whole, then write ------------------------------


def _plain(item: Any) -> Any:
    return item.model_dump(mode="json", by_alias=True) if hasattr(item, "model_dump") else item


def _validate(model, payload: Any, what: str):
    from pydantic import ValidationError

    from research_scan import schema as schema_module

    try:
        return model.model_validate(payload)
    except ValidationError as exc:
        raise ScanFailure(
            "invalid_artifact",
            f"{what} does not match the {model.__name__} contract",
            lines=schema_module.format_errors(exc),
        ) from None


def require(state: ScanState, condition: bool, message: str) -> None:
    if not condition:
        raise ScanFailure("wrong_phase", message)


def write_screen(state: ScanState, incoming: list[Any]) -> None:
    """Validate the whole submission against the run, then rewrite `screen.json`. All or nothing."""
    require(state, state.candidates is not None, "this scan has no candidate pool yet")
    batch = state.next_batch()
    require(state, batch is not None, "no screening batch is outstanding on this scan")

    scores = _validate(ScreenFile, {"scores": [_plain(item) for item in incoming]}, "screen_scores")
    merged: dict[str, ScreenScore] = {**state.scored}
    for entry in scores.scores:
        merged[entry.cid] = entry
    screen = ScreenFile(scores=list(merged.values()))

    # A cid this run never retrieved is named first: it is the more specific fault, and reading
    # it as "you left an item unscored" would send the model looking in the wrong place.
    # `missing` is whole-pool and belongs to `shortlist`, which enforces it for us at exit 2.
    report = shortlist_module.validate_coverage(state.candidates.candidates, screen)
    if report.duplicate or report.unknown:
        raise ScanFailure(
            "invalid_artifact",
            "screen scores do not line up with candidates.json",
            lines=report.lines(),
        )

    batch_cids = {item["cid"] for item in json.loads(batch.read_text(encoding="utf-8"))["items"]}
    unscored = sorted(batch_cids - set(merged))
    if unscored:
        raise ScanFailure(
            "invalid_artifact",
            f"batch {batch.stem} still has {len(unscored)} unscored item(s) — score every item",
            lines=[f"unscored cid: {cid}" for cid in unscored[:10]],
        )

    # The engine's own attribution check, on the merged file, before anything is written.
    attribution = coverage_module.validate_criteria_hit(state.plan, screen)
    if not attribution.ok:
        raise ScanFailure(
            "invalid_artifact",
            "screen scores name sub-criteria that queries.json does not define",
            lines=attribution.lines(),
        )

    run_module.write_model(state.run_dir / "screen.json", screen)


def write_gap_round(state: ScanState, incoming: list[Any]) -> None:
    """Append the model's gap queries to `queries.json.round2`; `queries` is left untouched."""
    advice = state.coverage.gap_round if state.coverage else None
    require(
        state,
        bool(advice and advice.should_run and not state.in_gap_round),
        "this scan is not waiting for gap queries",
    )
    merged = state.plan.model_dump(mode="json", by_alias=True)
    merged["round2"] = [_plain(item) for item in incoming]
    plan = _validate(QueryPlan, merged, "gap_queries")
    run_module.write_model(state.run_dir / "queries.json", plan)


def write_ranked(state: ScanState, incoming: list[Any]) -> None:
    """Merge reranked entries into `ranked.json`, in shortlist order. `verify` fills the rest."""
    require(state, state.shortlist is not None, "this scan has no shortlist to rank yet")
    entries = _validate(Ranked, [_plain(item) for item in incoming], "ranked_entries")

    known = {record.cid for record in state.shortlist_records}
    unknown = sorted({entry.cid for entry in entries.root} - known)
    if unknown:
        raise ScanFailure(
            "invalid_artifact",
            "ranked entries name cids that are not in shortlist.json",
            lines=[f"unknown cid: {cid}" for cid in unknown[:10]],
        )

    existing = state.ranked.root if state.ranked else []
    merged: dict[str, RankedEntry] = {entry.cid: entry for entry in existing}
    for entry in entries.root:
        merged[entry.cid] = entry
    ordered = [merged[record.cid] for record in state.shortlist_records if record.cid in merged]
    run_module.write_model(state.run_dir / "ranked.json", Ranked(ordered))


# --- the lock ----------------------------------------------------------------


def acquire(scan_id: str) -> str | None:
    """None when the pipeline is ours. Otherwise the status that says who is holding it."""
    global _HELD_BY
    if _LOCK.acquire(blocking=False):
        _HELD_BY = scan_id
        return None
    return "in_progress" if scan_id == _HELD_BY else "queued_behind_other_scan"


def release() -> None:
    global _HELD_BY
    _HELD_BY = None
    _LOCK.release()


async def guarded(scan_id: str, tool: str, work) -> dict[str, Any]:
    """One tool call: take the pipeline, do the blocking work off the loop, log one line."""
    status = acquire(scan_id)
    if status is not None:
        logger.info("scan=%s tool=%s status=%s", scan_id, tool, status)
        return busy_envelope(scan_id, status)

    started = time.monotonic()
    try:
        result = await asyncio.to_thread(work)
        logger.info(
            "scan=%s tool=%s phase=%s status=%s %.1fs",
            scan_id, tool, result.get("phase"), result.get("status"), time.monotonic() - started,
        )
        return result
    except ScanFailure as failure:
        state = None
        with contextlib.suppress(Exception):
            state = read_state(scan_root(config.load(), valid_scan_id(scan_id)))
        logger.info(
            "scan=%s tool=%s status=%s error=%s %.1fs",
            scan_id, tool, failure.status, failure.message, time.monotonic() - started,
        )
        return failure_envelope(scan_id, failure, state)
    finally:
        release()


# --- tools -------------------------------------------------------------------

mcp: FastMCP = FastMCP(
    name="research-scan",
    # Without this FastMCP falls back to its own version (`version=... or fastmcp.__version__`),
    # so the handshake told every client the library's version instead of ours. serverInfo has
    # to state what this server is, and the number comes from the one place it is written.
    version=__version__,
    instructions=(
        "Runs the research-scan evidence pipeline. You supply every judgement — the query plan,"
        " the screening scores, any gap queries, the rerank — using the research-scan skill's"
        " rubrics and schemas. This server only retrieves, expands, counts coverage, shortlists,"
        " verifies and emits. Follow `next_action` on every response, and never issue two mutating"
        " calls for the same scan_id at once."
    ),
)


@mcp.tool
async def scan_start(
    scan_id: Annotated[
        str,
        Field(
            description=(
                "A fresh canonical lowercase UUIDv4 you generate, one per brief. Retry a failed or"
                " timed-out scan_start with this same id and the same arguments to resume it."
            )
        ),
    ],
    brief: str,
    queries: QueryPlan,
    profile: Profile = Profile.standard,
    top: int = 10,
    foundational: int = 2,
    since: str | None = None,
    until: str | None = None,
    slug: str | None = None,
    max_candidates: int | None = None,
    per_query: int | None = None,
    force_gap_round: bool = False,
) -> dict[str, Any]:
    """Open a scan and run retrieval. Returns the first screening batch.

    `scan_id` is yours to generate: a fresh canonical lowercase UUIDv4, one per brief. Retrieval is
    the longest call in a scan, so if this one fails or times out, **call it again with the same
    `scan_id` and the same arguments** — the server resumes the run it already has instead of
    starting a second one. The same arguments means the same: a changed brief or plan under an
    id that is already in use is refused (`scan_id_conflict`) rather than silently applied.

    `brief` is the project brief in Markdown (or the question). `queries` is the full query plan
    you wrote with the skill's plan rubric — this server never writes queries for you.
    `since`/`until` are `YYYY-MM` window bounds. `force_gap_round` makes the gap round run whatever
    the profile says, and is applied when coverage is computed later in the scan.
    """
    try:
        # Before the lock and before any directory: a malformed id must leave no trace at all.
        scan_id = valid_scan_id(scan_id)
    except ScanFailure as failure:
        return failure_envelope(scan_id, failure, None)

    settings = config.load()
    root = scan_root(settings, scan_id)
    inputs = start_inputs(
        brief=brief,
        queries=queries,
        profile=profile,
        top=top,
        foundational=foundational,
        since=since,
        until=until,
        slug=slug,
        max_candidates=max_candidates,
        per_query=per_query,
        force_gap_round=force_gap_round,
    )

    def work() -> dict[str, Any]:
        # A call that reaches here holds the lock, so an in-flight retry never gets this far:
        # `guarded` has already answered it `in_progress`.
        if options_path(root).exists():
            if options_path(root).read_text(encoding="utf-8") != canonical(inputs):
                differing = differing_keys(inputs, read_options(root))
                raise ScanFailure(
                    "invalid_artifact",
                    f"scan_id {scan_id} was started with different inputs; retry with the same"
                    " arguments, or use a fresh scan_id for a different brief",
                    lines=[f"differs: {name}" for name in differing],
                    code="scan_id_conflict",
                )
            if runs_root(root).exists():
                # The run exists: report where it stands rather than retrieving a second time.
                return envelope(scan_id, read_state(root))
            # Inputs landed but `init` never produced a run directory. That is an unfinished
            # first call, not a completed one — resume it below rather than leave it stranded.
        else:
            root.mkdir(parents=True, exist_ok=True)
            write_options(root, inputs)

        (root / "brief.md").write_text(brief, encoding="utf-8")
        args = ["brief.md", "--slug", slug or run_module.derive_slug(brief, None)]
        args += ["--profile", profile.value, "--top", str(top), "--foundational", str(foundational)]
        args += ["--domain", queries.domain.value]
        if since:
            args += ["--from", since]
        if until:
            args += ["--to", until]
        check(run_stage(root, "init", *args))

        state = read_state(root)
        if state.run_dir is None:
            raise ScanFailure("failed", "`research-scan init` did not create a run directory")
        run_module.write_model(state.run_dir / "queries.json", queries)

        retrieve = ["--run", str(state.run_dir)]
        if max_candidates:
            retrieve += ["--max-candidates", str(max_candidates)]
        if per_query:
            retrieve += ["--per-query", str(per_query)]
        check(run_stage(root, "retrieve", *retrieve))
        return envelope(scan_id, advance(root))

    return await guarded(scan_id, "scan_start", work)


@mcp.tool
async def scan_continue(
    scan_id: str,
    screen_scores: list[ScreenScore] | None = None,
    gap_queries: list[Query] | None = None,
    ranked_entries: list[RankedEntry] | None = None,
) -> dict[str, Any]:
    """Submit the artifact the current phase asked for, and get the next decision.

    Send exactly one of: `screen_scores` for the batch you were handed (score every item),
    `gap_queries` for `queries.json.round2` when `write_gap_queries` was requested (an empty list
    means you found nothing worth reformulating, and the gap round is skipped), or `ranked_entries`
    for the shortlist page you were handed. Send none of them to poll the current phase.
    """
    def work() -> dict[str, Any]:
        root = scan_root(config.load(), valid_scan_id(scan_id))
        state = read_state(root)
        if state.run_dir is None:
            raise ScanFailure("wrong_phase", f"no scan with id {scan_id}")

        supplied = [
            name
            for name, value in (
                ("screen_scores", screen_scores),
                ("gap_queries", gap_queries),
                ("ranked_entries", ranked_entries),
            )
            if value is not None
        ]
        if len(supplied) > 1:
            raise ScanFailure(
                "invalid_artifact", f"send one artifact per call, not {', '.join(supplied)}"
            )

        expected = decision(state)[1]
        skip: set[str] = set()
        if screen_scores is not None:
            require(state, expected == "screen_candidates", f"this scan is waiting for {expected}")
            write_screen(state, screen_scores)
        elif gap_queries is not None:
            require(state, expected == "write_gap_queries", f"this scan is waiting for {expected}")
            if gap_queries:
                write_gap_round(state, gap_queries)
            else:
                skip.add("gap")
        elif ranked_entries is not None:
            require(state, expected == "rank_shortlist", f"this scan is waiting for {expected}")
            write_ranked(state, ranked_entries)
        else:
            return envelope(scan_id, state)
        return envelope(scan_id, advance(root, skip))

    return await guarded(scan_id, "scan_continue", work)


@mcp.tool
async def scan_verify(
    scan_id: str, ranked_entries: list[RankedEntry] | None = None
) -> dict[str, Any]:
    """Verify every ranked paper against the live record, then emit the evidence packet.

    Call this once `next_action` is `verify_ranked`. Any final `ranked_entries` you still hold are
    merged first. Verification is the engine's: DOIs and titles are checked, never repaired.
    """
    def work() -> dict[str, Any]:
        root = scan_root(config.load(), valid_scan_id(scan_id))
        state = read_state(root)
        if state.run_dir is None:
            raise ScanFailure("wrong_phase", f"no scan with id {scan_id}")
        if ranked_entries:
            write_ranked(state, ranked_entries)
            state = read_state(root)
        if state.evidence_exists:
            return envelope(scan_id, state)
        require(state, bool(state.ranked_cids), "nothing has been ranked on this scan yet")

        check(run_stage(root, "verify", "--run", str(state.run_dir)))
        check(run_stage(root, "emit", "--run", str(state.run_dir)))
        return envelope(scan_id, read_state(root))

    return await guarded(scan_id, "scan_verify", work)


@mcp.tool
async def scan_result(scan_id: str) -> dict[str, Any]:
    """Read a scan's result. Read-only, never blocked, safe to poll while a call is running.

    On a finished scan the payload carries the evidence packets' summary rows, the unverified
    list, the counts, `coverage.json` and the rendered `evidence.md`. `why` and `coverage_risks`
    are yours to write, per §6 of the skill — this server does not compose prose.
    """
    try:
        root = scan_root(config.load(), valid_scan_id(scan_id))
        state = read_state(root)
    except ScanFailure as failure:
        return failure_envelope(scan_id, failure, None)
    if state.run_dir is None:
        missing = ScanFailure("wrong_phase", f"no scan with id {scan_id}")
        return failure_envelope(scan_id, missing, None)

    phase, next_action, _ = decision(state)
    payload: dict[str, Any] = {"run_dir": str(state.run_dir)}

    if state.coverage is not None:
        payload["coverage"] = state.coverage.model_dump(mode="json")

    pool = state.candidates.candidates if state.candidates else []
    titles = {item.cid: item.title for item in pool}
    payload["unverified"] = [
        {
            "title": titles.get(entry.cid, entry.cid),
            "mismatches": [mismatch.value for mismatch in entry.verification.mismatches],
        }
        for entry in (state.ranked.root if state.ranked else [])
        if entry.verification is not None and not entry.verification.verified
    ]

    if state.evidence_exists:
        try:
            evidence = run_module.read_model(state.run_dir / "evidence.json", Evidence)
        except run_module.StageInputError as exc:
            unreadable = ScanFailure("failed", exc.message, lines=exc.lines)
            return failure_envelope(scan_id, unreadable, state)
        payload["evidence_json"] = str(state.run_dir / "evidence.json")
        payload["top"] = [
            {
                "rank": packet.rank,
                "title": packet.title,
                "year": packet.year,
                "doi": packet.ids.doi,
                "url": packet.url,
                "evidence_level": packet.evidence_level.value,
                "verified": packet.verification.verified,
                "selection_reason": packet.selection_reason.value,
                "relation": packet.relation.value if packet.relation else None,
                "relevance_reason": packet.relevance_reason,
            }
            for packet in evidence.packets
        ]
        markdown = state.run_dir / "evidence.md"
        if markdown.exists():
            payload["evidence_md"] = markdown.read_text(encoding="utf-8")

    logger.info("scan=%s tool=scan_result phase=%s", scan_id, phase)
    return {
        "scan_id": scan_id,
        "phase": phase,
        "status": "ok",
        "next_action": next_action,
        "progress": progress_of(state),
        "payload": payload,
    }


# --- authentication ----------------------------------------------------------


def authorize(path: str, authorization: str | None, token: str | None) -> bool:
    """Either mechanism admits: a bearer header, or the token as the first path segment.

    Bearer is preferred and is what a client that can set headers should send. The path-segment
    form exists only for clients that cannot set them, and it is strictly worse — a secret in a
    URL reaches browser history and proxy logs — so it is for a short-lived local session and
    nothing more. Both compare in constant time.
    """
    if not token:
        return False
    if authorization and authorization.lower().startswith("bearer "):
        supplied = authorization.split(" ", 1)[1].strip()
        if hmac.compare_digest(supplied, token):
            return True
    segments = [segment for segment in path.split("/") if segment]
    return bool(segments) and hmac.compare_digest(segments[0], token)


class TokenAuth(Middleware):
    """One gate in front of every MCP message. The token is read through `config.load()`."""

    async def on_message(self, context: MiddlewareContext, call_next):
        try:
            request = get_http_request()
        except RuntimeError:
            # No HTTP layer at all (in-process transport). Nothing to authenticate against.
            return await call_next(context)

        scope = request.scope
        path = f"{scope.get('root_path') or ''}{scope.get('path') or ''}"
        if not authorize(path, request.headers.get("authorization"), config.load().mcp_token):
            raise ToolError("unauthorized")
        return await call_next(context)


mcp.add_middleware(TokenAuth())


# --- serving -----------------------------------------------------------------


class RejectEverything:
    """An ASGI app that answers 401 and nothing else.

    Mounted only when no token is configured. Refusing to *start* in that case made the server
    un-probeable: an operator whose credential file failed to load got a dead port and had to
    read the logs to learn why. Starting and rejecting is the same security posture — no request
    is ever served — but a health check gets an answer, and the answer names the problem.
    """

    def __init__(self, detail: str) -> None:
        self.detail = detail

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] == "lifespan":  # let the parent's lifespan protocol complete
            message = await receive()
            while True:
                if message["type"] == "lifespan.startup":
                    await send({"type": "lifespan.startup.complete"})
                elif message["type"] == "lifespan.shutdown":
                    await send({"type": "lifespan.shutdown.complete"})
                    return
                message = await receive()
        body = json.dumps({"error": "unauthorized", "detail": self.detail}).encode()
        await send(
            {
                "type": "http.response.start",
                "status": 401,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode()),
                ],
            }
        )
        await send({"type": "http.response.body", "body": body})


NO_TOKEN_DETAIL = "no RESEARCH_SCAN_MCP_TOKEN configured — every request will be rejected"


def build_app(token: str | None = None) -> Starlette:
    """One MCP app, mounted twice: `/mcp` for a bearer client, `/<token>/mcp` for a client that
    cannot set headers.

    `http_app()` is called once, so there is one session manager and one lifespan — which the
    parent router must run, or streamable HTTP never initializes.

    With no token configured there is no secret to put in a path, so the path-segment mount is
    not created and every route answers 401. Never silently open.
    """
    token = token or config.load().mcp_token
    if not token:
        return Starlette(routes=[Mount("/", app=RejectEverything(NO_TOKEN_DETAIL))])
    inner = mcp.http_app(path="/mcp")
    return Starlette(
        routes=[Mount(f"/{token}", app=inner), Mount("/", app=inner)],
        lifespan=inner.lifespan,
    )


def main(host: str | None = None, port: int | None = None) -> None:
    """The `research-scan-mcp` console script, and what `research-scan mcp --http` calls.

    Arguments override the environment; with neither, behaviour is exactly what the console
    script has always done.
    """
    logging.basicConfig(
        level=os.environ.get("RESEARCH_SCAN_MCP_LOG", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    settings = config.load()
    if not settings.mcp_token:
        logger.warning("%s — put it in %s or the environment", NO_TOKEN_DETAIL, settings.config_env)

    host = host or os.environ.get("RESEARCH_SCAN_MCP_HOST", DEFAULT_HOST)
    port = (
        port
        if port is not None
        else int(os.environ.get("RESEARCH_SCAN_MCP_PORT", str(DEFAULT_PORT)))
    )
    settings.mcp_data_dir.mkdir(parents=True, exist_ok=True)

    # The token is never printed: the operator has it, and a log line is not the place for it.
    if settings.mcp_token:
        sys.stderr.write(
            f"research-scan MCP on http://{host}:{port}\n"
            f"  bearer      /mcp   token {settings.masked('RESEARCH_SCAN_MCP_TOKEN')}\n"
            "  path secret /$RESEARCH_SCAN_MCP_TOKEN/mcp\n"
            f"  runs        {settings.mcp_data_dir}\n"
        )
    else:
        sys.stderr.write(
            f"research-scan MCP on http://{host}:{port} — REJECTING EVERY REQUEST (401)\n"
            f"  configure a token in {settings.config_env}, then restart\n"
        )

    import uvicorn

    uvicorn.run(build_app(settings.mcp_token), host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
