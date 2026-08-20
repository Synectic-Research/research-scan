# SPDX-License-Identifier: Apache-2.0
"""Emit selection rules (spec §10.4) — code selects, the rubric scored.

The chat proposal's weighted formula was dropped on purpose (§3, "no invented weights"). What is
left is a deterministic ordering plus four rules that a scoring function cannot express:

* **Retracted is fatal.** Everything else can ship flagged; a retraction cannot.
* **Diversity.** At most two papers by the same first author, so one prolific lab cannot become
  the answer.
* **Guarantees.** If a review or a contradicting paper scored well enough, it ships even if the
  ordering would have cut it — a scan that only confirms the brief's premise is not evidence. The
  review slot has the higher floor: `overall` 3 or `closely-related`, because an off-topic review
  in a guaranteed slot is worse than no review at all. One review; `--contradicting` counter-
  results, because a premise is usually argued with from more than one direction and the ordering
  cuts the narrow papers that do it (v0.2.5).
* **Foundational slots, then backfill.** Out-of-window classics fill their reserved slots; any
  they cannot fill go back to in-window papers rather than shrinking the output.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field

from research_scan.dedup import first_author_surname
from research_scan.schema import (
    BriefRelation,
    Candidate,
    EvidencePacket,
    Mismatch,
    RankedEntry,
    SelectionReason,
)

log = logging.getLogger(__name__)

DEFAULT_TOP = 10
DEFAULT_FOUNDATIONAL = 2
ALTERNATES = 5

#: At most this many papers may share a first author (§10.4).
MAX_PER_FIRST_AUTHOR = 2

#: A flagged paper only earns its guaranteed slot if the reranker thought it was relevant.
GUARANTEE_THRESHOLD = 2

#: Counter-evidence slots the guarantee reserves. Default 1 keeps every measured run byte-identical
#: (§10.4 says "at least one"); raising it is a selection change and needs the AGENTS.md gate.
CONTRADICTING_SLOTS = 1

#: Counter-evidence earns slots; it does not get to become the page. The guarantee may take at most
#: half the main slots, so the papers that answered the brief keep the majority.
GUARANTEE_SHARE = 2

#: Reasons a pick is a guaranteed one, and so cannot be displaced to make room for another.
GUARANTEED_REASONS = frozenset({SelectionReason.review, SelectionReason.contradicting})

#: The review slot has a floor the contradicting slot does not (V1.1).
#:
#: "Best available review" is not "good enough to emit". The S5 acceptance judge scored
#: `2026-08-19-s3-e2e` rank 8 a 1: an administrative-burden meta-analysis in a slot the guarantee
#: handed it because it was the only review in reach. A review earns the slot by being *central* —
#: `overall` 3, or `relation: closely-related`, which is the reranker saying the same question in a
#: near setting. Otherwise the slot stays with the paper that won it on score.
REVIEW_RELATIONS = frozenset({BriefRelation.closely_related})


class NotVerified(Exception):
    """`ranked.json` reached `emit` without verification. Exit 2 — run `verify` (§10.4)."""

    def __init__(self, cids: list[str]) -> None:
        super().__init__("ranked entries are missing `verification`")
        self.cids = cids

    def lines(self) -> list[str]:
        shown = ", ".join(self.cids[:10])
        more = f", … (+{len(self.cids) - 10} more)" if len(self.cids) > 10 else ""
        return [
            f"{len(self.cids)} entr(ies) lack verification: {shown}{more}",
            "run `research-scan verify` first",
        ]


@dataclass
class Pick:
    candidate: Candidate
    entry: RankedEntry
    reason: SelectionReason = SelectionReason.score


@dataclass
class SelectionResult:
    packets: list[EvidencePacket] = field(default_factory=list)
    alternates: list[EvidencePacket] = field(default_factory=list)
    dropped_retracted: int = 0


def order_key(pair: tuple[Candidate, RankedEntry]) -> tuple:
    """Overall, then the criteria sum, then origin count, then recency (§10.4)."""
    candidate, entry = pair
    return (
        entry.overall,
        sum(entry.criteria.values()),
        len(candidate.origins),
        candidate.publication_date or "0000-00-00",
    )


def select(
    pairs: list[tuple[Candidate, RankedEntry]],
    *,
    top: int = DEFAULT_TOP,
    foundational: int = DEFAULT_FOUNDATIONAL,
    contradicting: int = CONTRADICTING_SLOTS,
) -> SelectionResult:
    """Apply §10.4 to verified, ranked pairs of (candidate, rerank)."""
    missing = [entry.cid for _, entry in pairs if entry.verification is None]
    if missing:
        raise NotVerified(missing)

    live = [pair for pair in pairs if Mismatch.retracted not in pair[1].verification.mismatches]
    dropped_retracted = len(pairs) - len(live)
    if dropped_retracted:
        log.warning("dropping %d retracted paper(s) at emit", dropped_retracted)

    ordered = sorted(live, key=order_key, reverse=True)
    in_window = [pair for pair in ordered if not pair[0].outside_window]
    outside_window = [pair for pair in ordered if pair[0].outside_window]

    main_slots = max(0, top - foundational)
    picks, used = _fill_main(in_window, main_slots)
    picks = _apply_guarantees(
        picks, in_window, used, contradicting=_contradicting_budget(contradicting, main_slots)
    )

    foundational_picks, used = _fill_foundational(outside_window, foundational, used)
    picks.extend(foundational_picks)

    shortfall = foundational - len(foundational_picks)
    if shortfall > 0:
        # Diversity is a property of the emitted set, so backfill inherits the counts so far.
        backfill, used = _fill_backfill(in_window, shortfall, used, _author_counts(picks))
        picks.extend(backfill)

    packets = [_packet(pick, rank) for rank, pick in enumerate(presentation_order(picks), start=1)]

    spare = [pair for pair in ordered if pair[1].cid not in used][:ALTERNATES]
    alternates = [
        _packet(Pick(candidate, entry, SelectionReason.score), rank)
        for rank, (candidate, entry) in enumerate(spare, start=len(packets) + 1)
    ]

    return SelectionResult(
        packets=packets, alternates=alternates, dropped_retracted=dropped_retracted
    )


def presentation_order(picks: list[Pick]) -> list[Pick]:
    """Current work first, foundational classics after it, each group by merit.

    Rank is a reading order, not only a score. A 2000 paper can out-score everything on the page
    and still be the wrong thing to open first — the brief asked what to know *before building
    this*, and the classics are context for the recent work, not the headline. Ranks run straight
    through both groups so the numbering stays a single sequence.
    """
    by_merit = sorted(picks, key=lambda pick: order_key((pick.candidate, pick.entry)), reverse=True)
    current = [pick for pick in by_merit if pick.reason is not SelectionReason.foundational]
    classics = [pick for pick in by_merit if pick.reason is SelectionReason.foundational]
    return current + classics


def _fill_main(
    in_window: list[tuple[Candidate, RankedEntry]], slots: int
) -> tuple[list[Pick], set[str]]:
    """Take the best in-window papers, holding the diversity cap (§10.4)."""
    picks: list[Pick] = []
    used: set[str] = set()
    authors: dict[str, int] = {}
    displaced = False

    for candidate, entry in in_window:
        if len(picks) >= slots:
            break
        author = first_author_surname(candidate)
        if author and authors.get(author, 0) >= MAX_PER_FIRST_AUTHOR:
            # This pick is skipped; whoever takes the slot got it because of the diversity rule.
            displaced = True
            continue
        reason = SelectionReason.diversity if displaced else SelectionReason.score
        displaced = False
        picks.append(Pick(candidate, entry, reason))
        used.add(entry.cid)
        if author:
            authors[author] = authors.get(author, 0) + 1

    return picks, used


def _contradicting_budget(requested: int, main_slots: int) -> int:
    """Cap the counter-evidence reserve at half the main slots, and say so when it binds.

    A guarantee that can take every slot is not a guarantee, it is a different scan. The cap is a
    share rather than a constant so it scales with `--top`: `--top 4` reserves at most 2 however
    many counter-results scored well.
    """
    ceiling = max(1, main_slots // GUARANTEE_SHARE)
    if requested > ceiling:
        log.info(
            "trimming the contradicting reserve %d -> %d (half of %d main slots)",
            requested,
            ceiling,
            main_slots,
        )
    return max(0, min(requested, ceiling))


def _apply_guarantees(
    picks: list[Pick],
    in_window: list[tuple[Candidate, RankedEntry]],
    used: set[str],
    *,
    contradicting: int = CONTRADICTING_SLOTS,
) -> list[Pick]:
    """Ensure a review and `contradicting` counter-results are present when they exist (§10.4)."""
    for attribute, reason, slots, counts in (
        ("review", SelectionReason.review, 1, _is_review),
        ("contradicts", SelectionReason.contradicting, contradicting, _is_counter_evidence),
    ):
        _guarantee(
            picks, in_window, used, attribute=attribute, reason=reason, slots=slots, counts=counts
        )
    return picks


def _is_review(entry: RankedEntry) -> bool:
    return entry.flags.review


def _is_counter_evidence(entry: RankedEntry) -> bool:
    """Does this paper fill a counter-evidence slot — as opposed to merely carrying the flag?

    `flags.contradicts` is additive: a paper that answers the brief and also pushes back on one
    premise carries it, and measured across the 21 committed runs it is set 3-9x more often than
    `relation: contradicting` (5 of 10 emitted against 0 on golden topic 1). Counting satisfaction
    on the flag therefore let a page of papers that answer the brief fill a reserve meant for the
    papers that argue with it, and the guarantee had effectively never fired on any run.

    `relation` is the reranker's single answer to how a paper stands to the brief, so it is the
    honest signal. It is optional in the schema for pre-S4.5 files, which is what the fallback is
    for — never a shortcut for a run that simply left it null.
    """
    if entry.relation is None:
        return entry.flags.contradicts
    return entry.relation is BriefRelation.contradicting


def _guarantee(
    picks: list[Pick],
    in_window: list[tuple[Candidate, RankedEntry]],
    used: set[str],
    *,
    attribute: str,
    reason: SelectionReason,
    slots: int,
    counts: Callable[[RankedEntry], bool],
) -> None:
    """Bring the papers that `counts` recognises up to `slots`, each displacing the lowest pick that
    is not itself guaranteed — otherwise the second counter-result evicts the first and the reserve
    never grows.

    `attribute` is the §10.4 eligibility gate and `counts` is the question "is the reserve already
    full?". They differ only for counter-evidence, and a candidate must pass both: a slot you can
    fill with a paper that does not satisfy it is not a reserve.

    The diversity cap binds here too. Three papers from one contrarian lab is the same failure the
    cap exists to prevent, wearing the other flag.
    """
    wanted = slots - sum(1 for pick in picks if counts(pick.entry))
    if wanted <= 0 or not picks:
        return

    for candidate, entry in in_window:
        if wanted <= 0:
            return
        if entry.cid in used or not getattr(entry.flags, attribute):
            continue
        if not counts(entry) or not _earns_the_slot(attribute, entry):
            continue
        author = first_author_surname(candidate)
        if author and _author_counts(picks).get(author, 0) >= MAX_PER_FIRST_AUTHOR:
            continue
        lowest = _lowest_displaceable(picks, reason)
        if lowest is None:
            log.info("no displaceable pick left; the %s reserve stops short", reason.value)
            return

        used.discard(picks[lowest].entry.cid)
        log.info(
            "guaranteeing a %s paper, displacing %r", reason.value, picks[lowest].candidate.title
        )
        picks[lowest] = Pick(candidate, entry, reason)
        used.add(entry.cid)
        wanted -= 1


def _lowest_displaceable(picks: list[Pick], reason: SelectionReason) -> int | None:
    """The weakest pick this guarantee may take: one the ordering made, else another guarantee's,
    never its own.

    The fallback tier is not decoration. With `--top 3 --foundational 2` there is a single main
    slot, and emit has always let the counter-result take it from the review — the guarantees run
    in order and the last one wins a slot that scarce. Protecting every guaranteed pick would
    quietly reverse that precedence on a run that has both flags and one slot.
    """
    tiers = (
        [i for i, pick in enumerate(picks) if pick.reason not in GUARANTEED_REASONS],
        [i for i, pick in enumerate(picks) if pick.reason in GUARANTEED_REASONS - {reason}],
    )
    for tier in tiers:
        if tier:
            return min(tier, key=lambda i: order_key((picks[i].candidate, picks[i].entry)))
    return None


def _earns_the_slot(attribute: str, entry: RankedEntry) -> bool:
    """The contradicting slot takes any relevant paper; the review slot wants a central one."""
    if entry.overall < GUARANTEE_THRESHOLD:
        return False
    if attribute == "review":
        return entry.overall == 3 or entry.relation in REVIEW_RELATIONS
    return True


def _fill_foundational(
    outside_window: list[tuple[Candidate, RankedEntry]], slots: int, used: set[str]
) -> tuple[list[Pick], set[str]]:
    picks: list[Pick] = []
    for candidate, entry in outside_window:
        if len(picks) >= slots:
            break
        if entry.overall < GUARANTEE_THRESHOLD or entry.cid in used:
            continue
        picks.append(Pick(candidate, entry, SelectionReason.foundational))
        used.add(entry.cid)
    return picks, used


def _author_counts(picks: list[Pick]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for pick in picks:
        author = first_author_surname(pick.candidate)
        if author:
            counts[author] = counts.get(author, 0) + 1
    return counts


def _fill_backfill(
    in_window: list[tuple[Candidate, RankedEntry]],
    slots: int,
    used: set[str],
    authors: dict[str, int],
) -> tuple[list[Pick], set[str]]:
    """An empty foundational slot goes back to an in-window paper rather than shrinking `top`.

    The diversity cap still binds here. If it cannot be satisfied, the scan emits fewer than `top`
    papers — a short list of distinct voices beats a full one from a single lab.
    """
    picks: list[Pick] = []
    for candidate, entry in in_window:
        if len(picks) >= slots:
            break
        if entry.cid in used:
            continue
        author = first_author_surname(candidate)
        if author and authors.get(author, 0) >= MAX_PER_FIRST_AUTHOR:
            continue
        picks.append(Pick(candidate, entry, SelectionReason.backfill))
        used.add(entry.cid)
        if author:
            authors[author] = authors.get(author, 0) + 1
    return picks, used


def _packet(pick: Pick, rank: int) -> EvidencePacket:
    payload = pick.candidate.model_dump()
    payload.update(pick.entry.model_dump())
    payload["cid"] = pick.candidate.cid
    return EvidencePacket(
        **payload,
        rank=rank,
        selection_reason=pick.reason,
        url=canonical_url(pick.candidate),
    )


def canonical_url(candidate: Candidate) -> str | None:
    if candidate.ids.doi:
        return f"https://doi.org/{candidate.ids.doi}"
    if candidate.ids.arxiv:
        return f"https://arxiv.org/abs/{candidate.ids.arxiv}"
    if candidate.oa_url:
        return candidate.oa_url
    if candidate.ids.pmid:
        return f"https://pubmed.ncbi.nlm.nih.gov/{candidate.ids.pmid}"
    return None
