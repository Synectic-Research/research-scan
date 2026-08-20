# SPDX-License-Identifier: Apache-2.0
"""Golden-set recall and judged precision (spec §13, §9.11).

Two numbers, measured against two different things:

* **recall** — did the scan find the papers a curated set says it should have? Scored at 10 (the
  emitted list) and at 25 (the reranked pool in §10.4 order), so a paper the scan found but ranked
  11th reads as a ranking problem rather than a retrieval one.
* **judged precision** — of what it did emit, how much a *different, stronger* model calls relevant
  (canon §3). That comes from `eval/judge.sh` and is merged in here.

The golden set is a floor, not ground truth: RollingEval found an LLM judge rated only 51 % of real
human citation lists moderately relevant. A missed "expected" paper is a signal to investigate, not
proof of failure — which is why `misses` carries each paper's `why` rather than just its DOI.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

import yaml
from pydantic import ValidationError

from research_scan import run as run_module
from research_scan import schema
from research_scan.dedup import (
    arxiv_id_from_doi,
    normalise_arxiv,
    normalise_doi,
    title_similarity,
)
from research_scan.run import StageInputError
from research_scan.schema import (
    Candidate,
    CandidateHit,
    CandidatesRecall,
    EvalMiss,
    EvalResult,
    Evidence,
    GoldenPaper,
    GoldenTopic,
    JudgeFile,
    JudgeScore,
    JudgeSummary,
    Profile,
    Ranked,
    ScreenFile,
    SelectionReason,
)
from research_scan.select import order_key

log = logging.getLogger(__name__)

GOLDEN_ROOT = Path("eval") / "golden"
RESULTS_ROOT = Path("eval") / "results"

RECALL_AT_10 = 10
RECALL_AT_25 = 25

#: A judged packet counts as a hit at this score or above (§14 acceptance 6).
JUDGED_RELEVANT = 2

#: Fuzzy-title fallback for golden matching. Stricter than dedup's 92, because a false positive
#: here inflates recall — the one number the eval exists to report honestly.
GOLDEN_TITLE_RATIO = 95


@dataclass
class RunFiles:
    """The three files eval reads out of a run directory."""

    evidence: Evidence
    ranked: Ranked
    candidates: dict[str, Candidate]


def load_topic(path: Path) -> GoldenTopic:
    """Read and validate one `eval/golden/<topic>.yaml`.

    Validated rather than duck-typed because a typo in a curated file would otherwise show up as a
    quiet zero on the scoreboard, which is the one failure an eval harness must never have.
    """
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise StageInputError(f"cannot read {path}: {exc.strerror or exc}") from exc
    try:
        payload = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise StageInputError(f"{path} is not valid YAML", lines=[str(exc)]) from exc
    if not isinstance(payload, dict):
        raise StageInputError(f"{path} must contain a mapping, not {type(payload).__name__}")
    try:
        return GoldenTopic.model_validate(payload)
    except ValidationError as exc:
        raise StageInputError(
            f"{path} does not match the GoldenTopic contract", lines=schema.format_errors(exc)
        ) from exc


def find_topic(name: str, root: Path | None = None) -> Path:
    root = root or GOLDEN_ROOT
    path = root / f"{name}.yaml"
    if path.is_file():
        return path
    available = sorted(item.stem for item in root.glob("*.yaml")) if root.is_dir() else []
    raise StageInputError(
        f"no golden topic {name!r} under {root}/",
        lines=[f"available: {', '.join(available)}" if available else "no topic files found"],
    )


def load_run(run_dir: Path) -> RunFiles:
    from research_scan.run import read_model  # local import keeps the module import graph acyclic

    evidence = read_model(run_dir / "evidence.json", Evidence)
    ranked = read_model(run_dir / "ranked.json", Ranked)
    candidates = read_model(run_dir / "candidates.json", schema.CandidatesFile)
    return RunFiles(
        evidence=evidence,
        ranked=ranked,
        candidates={candidate.cid: candidate for candidate in candidates.candidates},
    )


def identifiers_of(candidate: Candidate) -> set[str]:
    """Every identifier under which this candidate could match a golden entry."""
    found: set[str] = set()
    doi = normalise_doi(candidate.ids.doi)
    if doi:
        found.add(doi)
        embedded = arxiv_id_from_doi(doi)
        if embedded:
            found.add(embedded)
    arxiv = normalise_arxiv(candidate.ids.arxiv)
    if arxiv:
        found.add(arxiv)
    return found


def _expected_identifiers(paper: GoldenPaper) -> set[str]:
    """Normalise the golden side the same way, so `10.48550/arXiv.X` matches a bare `X`."""
    found: set[str] = set()
    for raw in paper.identifiers():
        doi = normalise_doi(raw)
        if doi:
            found.add(doi)
            embedded = arxiv_id_from_doi(doi)
            if embedded:
                found.add(embedded)
        arxiv = normalise_arxiv(raw)
        if arxiv:
            found.add(arxiv)
    return found


def ranked_in_selection_order(files: RunFiles) -> list[Candidate]:
    """`ranked.json` in §10.4 order.

    Reuses `select.order_key` rather than restating the ordering, so recall@25 can never drift from
    what `emit` would actually have chosen.
    """
    pairs = [
        (files.candidates[entry.cid], entry)
        for entry in files.ranked.root
        if entry.cid in files.candidates
    ]
    return [candidate for candidate, _ in sorted(pairs, key=order_key, reverse=True)]


def matches(paper: GoldenPaper, candidate: Candidate) -> bool:
    """A golden paper is found if any identifier lines up, or the titles are near-identical.

    The title fallback exists because upstream metadata is not always trustworthy: a run can carry
    the right paper under a DOI that resolves to a different work. Scoring that a miss would measure
    the registrar, not the retrieval.
    """
    if _expected_identifiers(paper) & identifiers_of(candidate):
        return True
    return title_similarity(paper.title, candidate.title) >= GOLDEN_TITLE_RATIO


def score(topic: GoldenTopic, run_dir: Path, files: RunFiles) -> EvalResult:
    """recall@10 over what was emitted, recall@25 over the reranked pool (§13)."""
    emitted = list(files.evidence.packets[:RECALL_AT_10])
    pool = ranked_in_selection_order(files)[:RECALL_AT_25]

    found_at_10 = 0
    found_at_25 = 0
    misses: list[EvalMiss] = []

    for paper in topic.expected:
        if any(matches(paper, packet) for packet in emitted):
            found_at_10 += 1
        if any(matches(paper, candidate) for candidate in pool):
            found_at_25 += 1
        else:
            misses.append(EvalMiss(doi=paper.doi, why=paper.why))

    expected = len(topic.expected)
    return EvalResult(
        topic=topic.topic,
        run_dir=str(run_dir),
        expected=expected,
        found_at_10=found_at_10,
        found_at_25=found_at_25,
        recall_10=round(found_at_10 / expected, 3) if expected else 0.0,
        recall_25=round(found_at_25 / expected, 3) if expected else 0.0,
        misses=misses,
    )


# --- recall at the candidate pool (S10e) -------------------------------------


def load_candidate_pool(run_dir: Path) -> tuple[dict[str, Candidate], dict[str, int] | None]:
    """`candidates.json`, plus `screen.json` scores when the run has got that far.

    Deliberately narrower than :func:`load_run`: this stage exists to measure retrieval *without*
    re-running the agent stages, so requiring `evidence.json` and `ranked.json` would defeat it. A
    run that has only retrieved and expanded scores fine; `screened` reports whether scores were
    available rather than silently reporting `null` for every paper.
    """
    from research_scan.run import read_model

    candidates = read_model(run_dir / "candidates.json", schema.CandidatesFile)
    pool = {candidate.cid: candidate for candidate in candidates.candidates}

    screen_path = run_dir / "screen.json"
    if not screen_path.is_file():
        return pool, None
    screen = read_model(screen_path, ScreenFile)
    return pool, {entry.cid: entry.score for entry in screen.scores}


def match_kind(paper: GoldenPaper, candidate: Candidate) -> str | None:
    """Which identifier connected these two, or None. Same rules as :func:`matches`.

    Reported rather than collapsed to a boolean because the distinction is the finding: `alias`
    means the run surfaced the published version and only the alias saved it from reading as a
    miss, which is a different story from `doi`.
    """
    found = identifiers_of(candidate)
    primary = normalise_doi(paper.doi)
    if primary and primary in found:
        return "doi"
    for raw in paper.aliases:
        alias = normalise_doi(raw.strip())
        if alias and alias in found:
            return "alias"
    if paper.arxiv and normalise_arxiv(paper.arxiv) in found:
        return "arxiv"
    if _expected_identifiers(paper) & found:
        # An identifier lined up that none of the branches above owns — an alias written as a bare
        # arXiv id, say. Report it as an alias rather than inventing a fifth kind.
        return "alias"
    if paper.title and title_similarity(paper.title, candidate.title) >= GOLDEN_TITLE_RATIO:
        return "title"
    return None


def describe_origins(candidate: Candidate) -> list[str]:
    """`source:relation:query-or-seed:rank`, so a hit says which stage and query produced it."""
    described = []
    for origin in candidate.origins:
        via = origin.query_id or origin.seed_id or "-"
        described.append(f"{origin.source.value}:{origin.relation.value}:{via}:{origin.rank}")
    return described


def score_candidates(
    topic: GoldenTopic,
    pool: dict[str, Candidate],
    scores: dict[str, int] | None,
) -> CandidatesRecall:
    """Recall at the candidate pool: was the paper ever retrieved, and what happened to it."""
    papers: list[CandidateHit] = []
    for paper in topic.expected:
        hit = CandidateHit(doi=paper.doi, title=paper.title, present=False)
        for candidate in pool.values():
            kind = match_kind(paper, candidate)
            if kind is None:
                continue
            hit = CandidateHit(
                doi=paper.doi,
                title=paper.title,
                present=True,
                cid=candidate.cid,
                matched_by=kind,
                origins=describe_origins(candidate),
                screen_score=None if scores is None else scores.get(candidate.cid),
            )
            break
        papers.append(hit)

    expected = len(topic.expected)
    found = sum(1 for hit in papers if hit.present)
    return CandidatesRecall(
        expected=expected,
        found=found,
        recall=round(found / expected, 3) if expected else 0.0,
        screened=scores is not None,
        papers=papers,
    )


def load_judge(path: Path) -> JudgeFile:
    from research_scan.run import read_model

    return read_model(path, JudgeFile)


def foundational_keys(evidence: Evidence) -> tuple[set[str], set[int]]:
    """The cids and ranks of the packets `emit` put in the reserved out-of-window slots."""
    packets = [
        packet
        for packet in evidence.packets
        if packet.selection_reason is SelectionReason.foundational
    ]
    return {packet.cid for packet in packets}, {packet.rank for packet in packets}


def _is_foundational(item: JudgeScore, cids: set[str], ranks: set[int]) -> bool:
    """Cid first, rank only as a fallback.

    A judge is free to emit its entries in any order, and one of the acceptance runs does exactly
    that — so matching on list position or on rank alone would be right by luck. The cid is the
    join key everywhere else in this package; it is the join key here too.
    """
    if item.cid is not None:
        return item.cid in cids
    return item.rank in ranks


def _precision(scores: list[JudgeScore]) -> float | None:
    if not scores:
        return None
    return round(sum(1 for item in scores if item.score >= JUDGED_RELEVANT) / len(scores), 3)


def merge_judge(
    result: EvalResult, judge: JudgeFile, evidence: Evidence | None = None
) -> EvalResult:
    """Fold the independent judge's scores into the result (§13).

    `precision_ge2` is the share of *judged* packets scoring ≥ 2. If the judge scored fewer packets
    than were emitted, that is the denominator — inventing zeroes for the unscored ones would read
    as a quality signal when it is really a missing judgment.

    `precision_ge2_in_window` drops the foundational slots from that share. A classic is emitted to
    be canonical background, not to inform a decision the brief names, so scoring it on the latter
    measures the emit policy rather than the reranker. Without `evidence` the split cannot be made
    and the field stays null — the same refusal to invent a number as the denominator rule above.
    """
    scored = sorted(judge.scores, key=lambda item: item.rank)
    if not scored:
        return result.model_copy(update={"judged": JudgeSummary()})

    per_rank = [
        JudgeScore(rank=item.rank, cid=item.cid, score=item.score, reason=item.reason)
        for item in scored
    ]

    in_window, foundational = per_rank, []
    if evidence is not None:
        cids, ranks = foundational_keys(evidence)
        in_window, foundational = [], []
        for item in per_rank:
            (foundational if _is_foundational(item, cids, ranks) else in_window).append(item)

    summary = JudgeSummary(
        precision_ge2=_precision(per_rank),
        precision_ge2_in_window=_precision(in_window) if evidence is not None else None,
        per_rank=per_rank,
        foundational=foundational,
    )
    return result.model_copy(update={"judged": summary})


def result_path(result: EvalResult, date_stamp: str, root: Path | None = None) -> Path:
    """Keyed by profile from v0.2.1: the same topic scores differently at each cost setting."""
    suffix = f"-{result.profile.value}" if result.profile else ""
    return (root or RESULTS_ROOT) / f"{date_stamp}-{result.topic}{suffix}.json"


def run_cost(run_dir: Path) -> tuple[Profile | None, float | None]:
    """Profile and wall clock from the run's own manifest — absent is not fatal."""
    try:
        manifest = run_module.read_manifest(Path(run_dir))
    except (run_module.StageInputError, OSError):
        return None, None
    return manifest.defaults.profile, manifest.counts.wall_clock_s


def with_cost(
    result: EvalResult, run_dir: Path, *, pool_size: int, found: int, expected: int
) -> EvalResult:
    """Attach what the recall cost. `recall_per_100_screened` is the row a gate table needs.

    `pool_size` is the pool as scored, not `counts.deduped`: expansion adds to the pool after
    retrieval writes that count, and what the agent screened is the number the cost is paid in.
    """
    profile, wall = run_cost(run_dir)
    recall = (found / expected) if expected else 0.0
    per_100 = round(recall * 100 / pool_size, 4) if pool_size else None
    return result.model_copy(
        update={
            "profile": profile,
            "pool_size": pool_size,
            "wall_clock_s": wall,
            "recall_per_100_screened": per_100,
        }
    )


def write_result(result: EvalResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.model_dump(mode="json"), indent=2) + "\n", encoding="utf-8")
