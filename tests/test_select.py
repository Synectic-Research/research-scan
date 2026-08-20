"""Selection rules and rendering (spec §10.4, §9.8)."""

from __future__ import annotations

import pytest

from conftest import make_candidate, ranked_entry, verification_payload
from research_scan import render, select
from research_scan.dedup import with_cid
from research_scan.schema import (
    BriefRelation,
    CoverageFile,
    Evidence,
    RunInfo,
    SelectionReason,
)


def pair(
    title: str,
    *,
    overall: int = 2,
    doi: str | None = None,
    authors=("Ada Researcher",),
    outside_window: bool = False,
    verified: bool = True,
    mismatches: list[str] | None = None,
    year: int = 2024,
    publication_date: str = "2024-01-01",
    **flags,
):
    candidate = with_cid(
        make_candidate(
            title=title,
            doi=doi or f"10.1000/{title.lower().replace(' ', '-')}",
            authors=authors,
            year=year,
            publication_date=publication_date,
        )
    )
    if outside_window:
        candidate = candidate.model_copy(update={"outside_window": True})
    entry = ranked_entry(
        candidate.cid,
        overall=overall,
        verification=verification_payload(verified, mismatches),
        **flags,
    )
    return candidate, entry


def run_info() -> RunInfo:
    return RunInfo.model_validate(
        {
            "run_dir": "research/scans/2026-08-19-t",
            "slug": "t",
            "date": "2026-08-19",
            "brief_path": "research/scans/2026-08-19-t/brief.md",
            "defaults": {"domain": "behavioral"},
        }
    )


def titles(packets) -> list[str]:
    return [packet.title for packet in packets]


# --- the verification gate --------------------------------------------------


def test_emit_refuses_ranked_entries_without_verification():
    candidate = with_cid(make_candidate(doi="10.1000/a"))
    with pytest.raises(select.NotVerified) as raised:
        select.select([(candidate, ranked_entry(candidate.cid))])

    assert raised.value.cids == [candidate.cid]
    assert "research-scan verify" in " ".join(raised.value.lines())


# --- retraction -------------------------------------------------------------


def test_a_paper_retracted_at_verify_never_ships():
    """§14.4: injected only at verify, dropped by emit, counted."""
    keep = pair("A live paper", overall=3)
    dead = pair("A retracted paper", overall=3, verified=False, mismatches=["retracted"])

    result = select.select([dead, keep], top=10, foundational=0)

    assert titles(result.packets) == ["A live paper"]
    assert result.dropped_retracted == 1


# --- unverified path --------------------------------------------------------


def test_an_unverified_paper_is_still_eligible_and_is_marked():
    unverified = pair("Unverified but relevant", overall=3, verified=False, mismatches=["title"])
    result = select.select([unverified], top=10, foundational=0)

    assert len(result.packets) == 1
    assert result.packets[0].verification.verified is False

    evidence = Evidence(run=run_info(), packets=result.packets)
    markdown = render.render_markdown(evidence)
    assert render.UNVERIFIED_MARKER in markdown
    assert markdown.count(render.UNVERIFIED_MARKER) >= 2  # table row and block heading
    assert "could not be verified" in markdown


# --- ordering ---------------------------------------------------------------


def test_ordering_is_overall_then_criteria_then_origins_then_recency():
    low = pair("Low", overall=1, authors=("Cy Gamma",))
    high = pair("High", overall=3, authors=("Ada Alpha",))
    middle = pair("Middle", overall=2, authors=("Bo Beta",))

    result = select.select([low, high, middle], top=10, foundational=0)

    assert titles(result.packets) == ["High", "Middle", "Low"]
    assert [packet.rank for packet in result.packets] == [1, 2, 3]


def test_top_and_foundational_bound_the_output():
    pairs = [pair(f"Paper {n}", overall=3, authors=(f"P{n} S{n}",)) for n in range(20)]
    result = select.select(pairs, top=6, foundational=2)
    assert len(result.packets) == 6


def test_diversity_can_legitimately_leave_the_output_short_of_top():
    """A full list from one lab is worse than a short list of distinct voices (§10.4)."""
    one_lab = [pair(f"Paper {n}", overall=3, authors=("Ada Prolific",)) for n in range(20)]

    result = select.select(one_lab, top=6, foundational=2)

    assert len(result.packets) == select.MAX_PER_FIRST_AUTHOR


# --- diversity --------------------------------------------------------------


def test_at_most_two_papers_share_a_first_author():
    prolific = [pair(f"Prolific {n}", overall=3, authors=("Ada Prolific",)) for n in range(5)]
    others = [pair(f"Other {n}", overall=2, authors=(f"Person{n} Surname{n}",)) for n in range(3)]

    result = select.select(prolific + others, top=5, foundational=0)

    first_authors = [packet.authors[0].name for packet in result.packets]
    assert first_authors.count("Ada Prolific") == select.MAX_PER_FIRST_AUTHOR
    assert len(result.packets) == 5


def test_a_pick_that_got_in_because_of_the_diversity_rule_says_so():
    prolific = [pair(f"Prolific {n}", overall=3, authors=("Ada Prolific",)) for n in range(3)]
    outsider = pair("Outsider", overall=2, authors=("Bo Beta",))

    result = select.select([*prolific, outsider], top=3, foundational=0)

    outsider_packet = next(p for p in result.packets if p.title == "Outsider")
    assert outsider_packet.selection_reason is SelectionReason.diversity


# --- guarantees -------------------------------------------------------------


def test_a_central_review_is_guaranteed_a_slot():
    fillers = [pair(f"Filler {n}", overall=3, authors=(f"P{n} S{n}",)) for n in range(3)]
    review = pair("The meta-analysis", overall=3, authors=("Rev Iewer",), review=True)

    result = select.select([*fillers, review], top=3, foundational=0)

    assert "The meta-analysis" in titles(result.packets)
    packet = next(p for p in result.packets if p.title == "The meta-analysis")
    assert packet.selection_reason is SelectionReason.review


def test_a_closely_related_review_earns_the_slot_without_scoring_three():
    fillers = [pair(f"Filler {n}", overall=3, authors=(f"P{n} S{n}",)) for n in range(3)]
    review = pair(
        "Same question, near setting",
        overall=2,
        authors=("Rev Iewer",),
        review=True,
        relation="closely-related",
    )

    result = select.select([*fillers, review], top=3, foundational=0)

    packet = next(p for p in result.packets if p.title == "Same question, near setting")
    assert packet.selection_reason is SelectionReason.review


def test_a_merely_relevant_review_no_longer_takes_a_slot_from_a_better_paper():
    """The V1.1 floor. "Best available review" is not "good enough to emit"."""
    fillers = [pair(f"Filler {n}", overall=3, authors=(f"P{n} S{n}",)) for n in range(3)]
    review = pair("An off-topic review", overall=2, authors=("Rev Iewer",), review=True)

    result = select.select([*fillers, review], top=3, foundational=0)

    assert "An off-topic review" not in titles(result.packets)
    assert sorted(titles(result.packets)) == ["Filler 0", "Filler 1", "Filler 2"]


def test_a_contradicting_paper_is_guaranteed_a_slot():
    fillers = [pair(f"Filler {n}", overall=3, authors=(f"P{n} S{n}",)) for n in range(3)]
    against = pair("Nudges did nothing", overall=2, authors=("Con Trarian",), contradicts=True)

    result = select.select([*fillers, against], top=3, foundational=0)

    packet = next(p for p in result.packets if p.title == "Nudges did nothing")
    assert packet.selection_reason is SelectionReason.contradicting


def test_the_guarantee_displaces_the_lowest_scoring_pick():
    best = pair("Best", overall=3, authors=("A A",))
    middle = pair("Middle", overall=3, authors=("B B",))
    worst = pair("Worst", overall=2, authors=("C C",))
    review = pair("Review", overall=3, authors=("D D",), review=True)

    result = select.select([best, middle, worst, review], top=3, foundational=0)

    assert "Worst" not in titles(result.packets)
    assert "Best" in titles(result.packets)


def test_a_review_scoring_below_two_earns_no_guarantee():
    fillers = [pair(f"Filler {n}", overall=3, authors=(f"P{n} S{n}",)) for n in range(3)]
    weak_review = pair("A weak review", overall=1, authors=("Rev Iewer",), review=True)

    result = select.select([*fillers, weak_review], top=3, foundational=0)

    assert "A weak review" not in titles(result.packets)


def test_an_already_selected_review_triggers_no_displacement():
    review = pair("Review", overall=3, authors=("A A",), review=True)
    other = pair("Other", overall=2, authors=("B B",))

    result = select.select([review, other], top=2, foundational=0)

    assert titles(result.packets) == ["Review", "Other"]
    assert result.packets[0].selection_reason is SelectionReason.score


def test_the_contradicting_reserve_takes_more_than_one_counter_result():
    """v0.2.5: a premise is argued with from several directions; one slot ships only the loudest."""
    fillers = [pair(f"Filler {n}", overall=3, authors=(f"P{n} S{n}",)) for n in range(6)]
    against = [
        pair(
            f"Nudges did nothing {n}", overall=3, authors=(f"Con{n} Trarian{n}",), contradicts=True
        )
        for n in range(3)
    ]

    result = select.select([*fillers, *against], top=6, foundational=0, contradicting=3)

    reserved = [p for p in result.packets if p.selection_reason is SelectionReason.contradicting]
    assert len(reserved) == 3
    assert sorted(p.title for p in reserved) == [
        "Nudges did nothing 0",
        "Nudges did nothing 1",
        "Nudges did nothing 2",
    ]


def test_the_reserve_counts_counter_results_the_ordering_already_picked():
    """Two slots and one counter-result already in on merit means one displacement, not two."""
    fillers = [pair(f"Filler {n}", overall=2, authors=(f"P{n} S{n}",)) for n in range(3)]
    strong = pair("Strong and against", overall=3, authors=("Con Trarian",), contradicts=True)
    weak = pair("Weak and against", overall=2, authors=("Ann Other",), contradicts=True)

    result = select.select([*fillers, strong, weak], top=4, foundational=0, contradicting=2)

    assert "Strong and against" in titles(result.packets)
    assert "Weak and against" in titles(result.packets)
    # Only the lowest filler lost its slot; the other two survive.
    assert len([t for t in titles(result.packets) if t.startswith("Filler")]) == 2


def test_the_reserve_never_displaces_its_own_earlier_pick():
    """The bug the single-slot loop hid: pick two, and the second evicts the first."""
    fillers = [pair(f"Filler {n}", overall=3, authors=(f"P{n} S{n}",)) for n in range(4)]
    first = pair("Against, stronger", overall=3, authors=("Con Trarian",), contradicts=True)
    second = pair("Against, weaker", overall=2, authors=("Ann Other",), contradicts=True)

    result = select.select([*fillers, first, second], top=4, foundational=0, contradicting=2)

    assert "Against, stronger" in titles(result.packets)
    assert "Against, weaker" in titles(result.packets)


def test_the_flag_alone_does_not_satisfy_the_counter_evidence_reserve():
    """v0.2.5: `flags.contradicts` is additive; `relation` is the reranker's single answer.

    Measured across the 21 committed runs the flag is set 3-9x more often than the relation — 5 of
    10 emitted against 0 on golden topic 1 — so counting satisfaction on the flag meant the
    guarantee had effectively never fired.
    """
    incidental = [
        pair(
            f"Answers the brief {n}",
            overall=3,
            authors=(f"P{n} S{n}",),
            contradicts=True,
            relation="design-changing",
        )
        for n in range(3)
    ]
    real = pair(
        "Argues with the premise",
        overall=2,
        authors=("Con Trarian",),
        contradicts=True,
        relation="contradicting",
    )

    result = select.select([*incidental, real], top=3, foundational=0)

    packet = next(p for p in result.packets if p.title == "Argues with the premise")
    assert packet.selection_reason is SelectionReason.contradicting


def test_a_flagged_paper_that_is_not_counter_evidence_cannot_fill_the_slot():
    """A slot you can fill with a paper that does not satisfy it is not a reserve."""
    fillers = [pair(f"Filler {n}", overall=3, authors=(f"P{n} S{n}",)) for n in range(3)]
    incidental = pair(
        "Answers the brief",
        overall=3,
        authors=("Con Trarian",),
        contradicts=True,
        relation="plan-influencing",
    )

    result = select.select([*fillers, incidental], top=3, foundational=0)

    assert not [p for p in result.packets if p.selection_reason is SelectionReason.contradicting]


def test_a_null_relation_falls_back_to_the_flag():
    """Pre-S4.5 ranked.json carries no `relation`; those runs keep the behaviour they measured."""
    fillers = [pair(f"Filler {n}", overall=3, authors=(f"P{n} S{n}",)) for n in range(3)]
    against = pair("Nudges did nothing", overall=2, authors=("Con Trarian",), contradicts=True)
    assert against[1].relation is None

    result = select.select([*fillers, against], top=3, foundational=0)

    packet = next(p for p in result.packets if p.title == "Nudges did nothing")
    assert packet.selection_reason is SelectionReason.contradicting


def test_one_main_slot_still_goes_to_the_counter_result_over_the_review():
    """Emit's standing precedence: guarantees run in order and the last one wins a scarce slot.

    `--top 3 --foundational 2` leaves one main slot. Protecting the review pick from the
    contradicting guarantee would reverse a rule that predates the reserve.
    """
    filler = pair("Filler", overall=3, authors=("P S",))
    review = pair("A central review", overall=3, authors=("Rev Iewer",), review=True)
    against = pair("Nudges did nothing", overall=3, authors=("Con Trarian",), contradicts=True)

    result = select.select([filler, review, against], top=1, foundational=0)

    assert titles(result.packets) == ["Nudges did nothing"]
    assert result.packets[0].selection_reason is SelectionReason.contradicting


def test_the_reserve_stops_at_half_the_main_slots():
    """Counter-evidence earns slots; it does not get to become the page."""
    fillers = [pair(f"Filler {n}", overall=3, authors=(f"P{n} S{n}",)) for n in range(4)]
    against = [
        pair(f"Against {n}", overall=3, authors=(f"Con{n} Trarian{n}",), contradicts=True)
        for n in range(4)
    ]

    result = select.select([*fillers, *against], top=4, foundational=0, contradicting=4)

    reserved = [p for p in result.packets if p.selection_reason is SelectionReason.contradicting]
    assert len(reserved) == 2
    assert len(result.packets) == 4


def test_the_reserve_holds_the_diversity_cap():
    """Three papers from one contrarian lab is the failure the cap exists to prevent."""
    fillers = [pair(f"Filler {n}", overall=3, authors=(f"P{n} S{n}",)) for n in range(6)]
    against = [
        pair(f"Against {n}", overall=3, authors=("Con Trarian",), contradicts=True)
        for n in range(3)
    ]

    result = select.select([*fillers, *against], top=6, foundational=0, contradicting=3)

    reserved = [p for p in result.packets if p.selection_reason is SelectionReason.contradicting]
    assert len(reserved) == 2


def test_zero_contradicting_slots_disables_the_guarantee():
    fillers = [pair(f"Filler {n}", overall=3, authors=(f"P{n} S{n}",)) for n in range(3)]
    against = pair("Nudges did nothing", overall=2, authors=("Con Trarian",), contradicts=True)

    result = select.select([*fillers, against], top=3, foundational=0, contradicting=0)

    assert "Nudges did nothing" not in titles(result.packets)


def test_the_default_reserve_is_one_slot():
    """The frozen default: raising it is a selection change with its own gate."""
    fillers = [pair(f"Filler {n}", overall=3, authors=(f"P{n} S{n}",)) for n in range(6)]
    against = [
        pair(f"Against {n}", overall=3, authors=(f"Con{n} Trarian{n}",), contradicts=True)
        for n in range(3)
    ]

    result = select.select([*fillers, *against], top=6, foundational=0)

    reserved = [p for p in result.packets if p.selection_reason is SelectionReason.contradicting]
    assert len(reserved) == 1


# --- foundational and backfill ---------------------------------------------


def test_foundational_slots_come_from_outside_the_window():
    current = [pair(f"Current {n}", overall=3, authors=(f"P{n} S{n}",)) for n in range(5)]
    classic = pair(
        "A 2003 classic", overall=3, outside_window=True, authors=("Old Timer",), year=2003
    )

    result = select.select([*current, classic], top=4, foundational=1)

    packet = next(p for p in result.packets if p.title == "A 2003 classic")
    assert packet.selection_reason is SelectionReason.foundational
    assert len(result.packets) == 4


def test_a_classic_never_outranks_the_current_work():
    """Rank is reading order: the 2000 paper is context for the recent work, not the headline."""
    current = [pair(f"Current {n}", overall=2, authors=(f"P{n} S{n}",)) for n in range(3)]
    classic = pair(
        "A 2000 classic", overall=3, outside_window=True, authors=("Old Timer",), year=2000
    )

    result = select.select([*current, classic], top=4, foundational=1)

    assert result.packets[-1].title == "A 2000 classic"
    assert result.packets[-1].rank == len(result.packets)
    assert result.packets[0].selection_reason is not SelectionReason.foundational
    # ranks stay one unbroken sequence across both groups
    assert [packet.rank for packet in result.packets] == list(range(1, len(result.packets) + 1))


def test_a_weak_classic_does_not_take_a_foundational_slot():
    current = [pair(f"Current {n}", overall=3, authors=(f"P{n} S{n}",)) for n in range(5)]
    weak_classic = pair("A weak classic", overall=1, outside_window=True, authors=("Old Timer",))

    result = select.select([*current, weak_classic], top=4, foundational=1)

    assert "A weak classic" not in titles(result.packets)


def test_empty_foundational_slots_are_backfilled_from_in_window_papers():
    """The output is `top` papers even when the graph found no classics worth shipping."""
    current = [pair(f"Current {n}", overall=3, authors=(f"P{n} S{n}",)) for n in range(6)]

    result = select.select(current, top=5, foundational=2)

    assert len(result.packets) == 5
    reasons = {packet.selection_reason for packet in result.packets}
    assert SelectionReason.backfill in reasons
    assert sum(1 for p in result.packets if p.selection_reason is SelectionReason.backfill) == 2


def test_backfill_only_fills_the_slots_the_classics_left_empty():
    current = [pair(f"Current {n}", overall=3, authors=(f"P{n} S{n}",)) for n in range(6)]
    classic = pair("Classic", overall=3, outside_window=True, authors=("Old Timer",))

    result = select.select([*current, classic], top=5, foundational=2)

    reasons = [p.selection_reason for p in result.packets]
    assert reasons.count(SelectionReason.foundational) == 1
    assert reasons.count(SelectionReason.backfill) == 1
    assert len(result.packets) == 5


def test_no_paper_is_selected_twice():
    current = [pair(f"Current {n}", overall=3, authors=(f"P{n} S{n}",)) for n in range(3)]
    result = select.select(current, top=10, foundational=5)
    cids = [packet.cid for packet in result.packets]
    assert len(cids) == len(set(cids))


# --- alternates -------------------------------------------------------------


def test_alternates_are_the_next_five_and_never_overlap_the_selection():
    pairs = [pair(f"Paper {n:02d}", overall=3, authors=(f"P{n} S{n}",)) for n in range(20)]
    result = select.select(pairs, top=4, foundational=0)

    assert len(result.alternates) == select.ALTERNATES
    assert not {p.cid for p in result.packets} & {a.cid for a in result.alternates}


# --- packet shape and rendering --------------------------------------------


def test_a_packet_carries_the_candidate_the_rerank_and_the_verification():
    candidate, entry = pair("A paper", overall=3)
    packet = select.select([(candidate, entry)], top=1, foundational=0).packets[0]

    assert packet.cid == candidate.cid
    assert packet.title == candidate.title
    assert packet.key_finding == entry.key_finding
    assert packet.verification.verified is True
    assert packet.url == f"https://doi.org/{candidate.ids.doi}"
    assert packet.rank == 1


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        ({"doi": "10.1000/x"}, "https://doi.org/10.1000/x"),
        ({"arxiv": "2501.10120"}, "https://arxiv.org/abs/2501.10120"),
        ({"pmid": "37993839"}, "https://pubmed.ncbi.nlm.nih.gov/37993839"),
        ({}, None),
    ],
)
def test_the_url_falls_back_through_the_identifiers(kwargs, expected):
    assert select.canonical_url(make_candidate(**kwargs)) == expected


def test_the_url_precedence_prefers_the_stablest_identifier_it_has():
    """The one owner of link resolution, on the cases the table above cannot express.

    `oa_url` is the only branch with no id of its own; a preprint that also carries a DOI is the
    case where two branches apply, and the DOI wins because it survives a version bump. Note the
    order deliberately puts a publisher's open-access landing page *above* a PubMed record.
    """
    both = make_candidate(doi="10.1000/x", arxiv="2501.10120")
    assert select.canonical_url(both) == "https://doi.org/10.1000/x"

    open_access = make_candidate().model_copy(update={"oa_url": "https://example.org/paper.pdf"})
    assert select.canonical_url(open_access) == "https://example.org/paper.pdf"

    # `oa_url` outranks a PMID: the reader wants the paper, not the index entry.
    with_pmid = make_candidate(pmid="37993839").model_copy(
        update={"oa_url": "https://example.org/paper.pdf"}
    )
    assert select.canonical_url(with_pmid) == "https://example.org/paper.pdf"

    # But an arXiv id outranks it, because the abs page is the paper's own home.
    preprint = make_candidate(arxiv="2501.10120").model_copy(
        update={"oa_url": "https://example.org/paper.pdf"}
    )
    assert select.canonical_url(preprint) == "https://arxiv.org/abs/2501.10120"


def test_the_top_table_links_the_title_when_the_packet_has_a_url():
    candidate, entry = pair("A linked paper", overall=3)
    packet = select.select([(candidate, entry)], top=1, foundational=0).packets[0]
    evidence = Evidence(run=run_info(), packets=[packet], alternates=[])

    row = next(
        line for line in render.render_markdown(evidence).splitlines() if line.startswith("| 1 |")
    )
    assert f"[A linked paper]({packet.url})" in row
    assert packet.ids.doi in row, "the DOI rides alongside, in a form you can copy"


def test_a_preprint_without_a_doi_links_its_arxiv_page_and_names_no_doi():
    candidate = with_cid(make_candidate(title="A preprint", doi="10.1000/tmp", arxiv="2501.10120"))
    entry = ranked_entry(candidate.cid, overall=3, verification=verification_payload(True))
    candidate = candidate.model_copy(update={"ids": candidate.ids.model_copy(update={"doi": None})})
    packet = select.select([(candidate, entry)], top=1, foundational=0).packets[0]
    evidence = Evidence(run=run_info(), packets=[packet], alternates=[])

    row = next(
        line for line in render.render_markdown(evidence).splitlines() if line.startswith("| 1 |")
    )
    assert "[A preprint](https://arxiv.org/abs/2501.10120)" in row
    assert "10.1000" not in row


def test_a_packet_without_a_url_renders_its_title_plainly():
    candidate = with_cid(make_candidate(title="An unlinkable paper", doi="10.1000/tmp"))
    entry = ranked_entry(candidate.cid, overall=3, verification=verification_payload(True))
    candidate = candidate.model_copy(update={"ids": candidate.ids.model_copy(update={"doi": None})})
    packet = select.select([(candidate, entry)], top=1, foundational=0).packets[0]
    assert packet.url is None
    evidence = Evidence(run=run_info(), packets=[packet], alternates=[])

    row = next(
        line for line in render.render_markdown(evidence).splitlines() if line.startswith("| 1 |")
    )
    assert "| An unlinkable paper |" in row
    assert "[" not in row


def test_markdown_has_a_table_then_a_block_per_paper():
    pairs = [pair("First paper", overall=3), pair("Second paper", overall=2, authors=("Bo Beta",))]
    result = select.select(pairs, top=2, foundational=0)
    evidence = Evidence(run=run_info(), packets=result.packets, alternates=result.alternates)

    markdown = render.render_markdown(evidence)

    assert "| # | Paper | Year | Venue | Evidence | Verified |" in markdown
    assert "## 1. First paper" in markdown
    assert "## 2. Second paper" in markdown
    assert "**Key finding.**" in markdown
    assert "**Why it matters here.**" in markdown
    assert "selected: score" in markdown


def test_markdown_escapes_a_pipe_in_a_title():
    candidate, entry = pair("Defaults | nudges")
    evidence = Evidence(run=run_info(), packets=select.select([(candidate, entry)]).packets)
    table_row = [
        line for line in render.render_markdown(evidence).splitlines() if line.startswith("| 1 |")
    ][0]
    assert r"Defaults \| nudges" in table_row


def test_bib_entries_carry_the_verification_trail():
    verified = pair("A verified paper", overall=3)
    unverified = pair("A doubtful paper", overall=3, verified=False, mismatches=["title", "year"])
    result = select.select([verified, unverified], top=2, foundational=0)
    bib = render.render_bib(Evidence(run=run_info(), packets=result.packets))

    assert "@article{" in bib
    assert "verified = {true}" in bib
    assert "verified = {false}" in bib
    assert "verified_on = {2026-08-19}" in bib
    assert "verification_note = {title, year}" in bib
    assert "doi = {10.1000/a-verified-paper}" in bib


def test_bib_keys_are_distinct_per_paper():
    pairs = [pair("First study of defaults"), pair("Second study of nudges", authors=("Bo Beta",))]
    bib = render.render_bib(Evidence(run=run_info(), packets=select.select(pairs).packets))
    keys = [line.split("{")[1].rstrip(",") for line in bib.splitlines() if line.startswith("@")]
    assert len(keys) == len(set(keys))


def test_the_why_it_made_the_cut_line_fuses_the_meta_justification():
    candidate, entry = pair("A paper", overall=3, contradicts=True)
    entry = entry.model_copy(update={"relation": BriefRelation.contradicting})
    packet = select.select([(candidate, entry)], top=1, foundational=0).packets[0]
    evidence = Evidence(run=run_info(), packets=[packet])

    markdown = render.render_markdown(evidence, criterion_names={"C1": "default effect size"})

    assert "**Why it made the cut.**" in markdown
    line = next(line for line in markdown.splitlines() if "Why it made the cut" in line)
    assert "contradicting" in line
    assert "selected by score" in line
    assert "C1 default effect size" in line  # strongest criterion, named
    assert entry.relevance_reason in line


def test_the_why_line_degrades_gracefully_without_relation_or_names():
    """Pre-S4.5 entries have no relation, and a run dir may lack queries.json."""
    candidate, entry = pair("A paper", overall=2)
    packet = select.select([(candidate, entry)], top=1, foundational=0).packets[0]
    evidence = Evidence(run=run_info(), packets=[packet])

    markdown = render.render_markdown(evidence)

    line = next(line for line in markdown.splitlines() if "Why it made the cut" in line)
    assert "selected by score" in line
    assert "strongest on C1 (2/3)" in line  # bare id, no invented name


# --- the coverage section (V1.1) --------------------------------------------


def coverage_file(round_two: bool = False, thin: bool = True):
    def snapshot(number: int, hits: int):
        return {
            "round": number,
            "screened": 40,
            "ge2": hits,
            "criteria": [
                {"id": "C1", "name": "problem match", "hits": hits, "thin": thin},
                {"id": "C2", "name": "population", "hits": 7, "thin": False},
            ],
        }

    rounds = [snapshot(1, 2)] + ([snapshot(2, 6)] if round_two else [])
    return CoverageFile.model_validate(
        {"run": run_info().model_dump(mode="json"), "rounds": rounds}
    )


def one_paper_evidence():
    result = select.select([pair("Only paper", overall=3)], top=1, foundational=0)
    return Evidence(run=run_info(), packets=result.packets, alternates=result.alternates)


def test_a_run_without_coverage_renders_exactly_as_it_did_in_v1():
    evidence = one_paper_evidence()
    assert render.render_markdown(evidence) == render.render_markdown(evidence, coverage=None)
    assert "## Coverage" not in render.render_markdown(evidence)


def test_the_coverage_section_names_what_is_still_thin():
    markdown = render.render_markdown(one_paper_evidence(), coverage=coverage_file())

    assert "## Coverage" in markdown
    assert "| C1 problem match | 2 |" in markdown
    assert "Still thin after round 1: C1 problem match" in markdown
    assert "Gap round added" not in markdown  # there was no gap round


def test_the_coverage_section_reports_what_the_gap_round_recovered():
    markdown = render.render_markdown(one_paper_evidence(), coverage=coverage_file(round_two=True))

    assert "Gap round added" in markdown
    assert "| C1 problem match | 6 | +4 |" in markdown
    assert "Still thin after the gap round" in markdown


def test_a_closely_related_review_still_has_to_clear_the_old_floor():
    """The V1.1 floor is added to the ≥ 2 rule, not swapped for it."""
    fillers = [pair(f"Filler {n}", overall=3, authors=(f"P{n} S{n}",)) for n in range(3)]
    weak = pair(
        "A weak but closely-related review",
        overall=1,
        authors=("Rev Iewer",),
        review=True,
        relation="closely-related",
    )

    result = select.select([*fillers, weak], top=3, foundational=0)

    assert "A weak but closely-related review" not in titles(result.packets)
