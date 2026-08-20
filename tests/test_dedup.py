"""Identifier normalisation, cid stability, and merge semantics (spec §8.2)."""

from __future__ import annotations

import pytest

from conftest import make_candidate
from research_scan import dedup
from research_scan.schema import Origin, Relation, SourceName, WorkType

# --- normalisation ----------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("https://doi.org/10.1257/AER.20210881", "10.1257/aer.20210881"),
        ("http://dx.doi.org/10.1000/X", "10.1000/x"),
        ("doi:10.1000/Example", "10.1000/example"),
        ("10.1000/Example", "10.1000/example"),
        ("  10.1000/example  ", "10.1000/example"),
        (None, None),
        ("", None),
    ],
)
def test_normalise_doi(raw, expected):
    assert dedup.normalise_doi(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("2501.10120v2", "2501.10120"),
        ("arXiv:2501.10120", "2501.10120"),
        ("https://arxiv.org/abs/2501.10120v11", "2501.10120"),
        ("cs/0701001", "cs/0701001"),
        (None, None),
    ],
)
def test_normalise_arxiv(raw, expected):
    assert dedup.normalise_arxiv(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("https://pubmed.ncbi.nlm.nih.gov/37993839", "37993839"),
        ("37993839", "37993839"),
        (None, None),
    ],
)
def test_normalise_pmid(raw, expected):
    assert dedup.normalise_pmid(raw) == expected


def test_normalise_title_strips_case_accents_and_punctuation():
    assert dedup.normalise_title("Défaults, Nudges & Savings!") == "defaults nudges savings"
    assert dedup.normalise_title("  Spaced   out  ") == "spaced out"
    assert dedup.normalise_title(None) == ""


# --- cid --------------------------------------------------------------------


def test_cid_prefers_doi_over_every_other_identifier():
    candidate = make_candidate(doi="10.1000/x", arxiv="2501.10120", pmid="123456")
    assert dedup.primary_id(candidate) == ("doi", "10.1000/x")


def test_cid_priority_falls_through_doi_arxiv_pmid_title():
    assert dedup.primary_id(make_candidate(arxiv="2501.10120", pmid="1"))[0] == "arxiv"
    assert dedup.primary_id(make_candidate(pmid="1"))[0] == "pmid"
    assert dedup.primary_id(make_candidate())[0] == "title"


def test_cid_is_stable_across_runs_and_identifier_formatting():
    first = dedup.with_cid(make_candidate(doi="https://doi.org/10.1257/AER.20210881"))
    second = dedup.with_cid(make_candidate(doi="10.1257/aer.20210881", title="A different title"))

    assert first.cid == second.cid
    assert len(first.cid) == 12
    assert first.cid == dedup.with_cid(first).cid  # idempotent


def test_cid_differs_for_different_papers():
    left = dedup.with_cid(make_candidate(doi="10.1000/a"))
    right = dedup.with_cid(make_candidate(doi="10.1000/b"))
    assert left.cid != right.cid


def test_title_derived_cid_includes_the_year():
    same_title_2023 = dedup.with_cid(make_candidate(year=2023))
    same_title_2024 = dedup.with_cid(make_candidate(year=2024))
    assert same_title_2023.cid != same_title_2024.cid


# --- merging ----------------------------------------------------------------


def test_merge_keeps_the_union_of_what_both_records_knew():
    openalex = make_candidate(
        doi="10.1000/x",
        openalex="W1",
        abstract="A short abstract.",
        citation_count=10,
        venue="Journal of Defaults",
        authors=("Ada Researcher", "Bob Coauthor"),
    )
    s2 = make_candidate(
        doi="10.1000/x",
        s2="paper-1",
        arxiv="2501.10120",
        abstract="A considerably longer abstract with more detail in it.",
        tldr="Defaults matter.",
        citation_count=14,
        influential_citation_count=3,
        authors=("Ada Researcher",),
        source=SourceName.s2,
        query_id="Q2",
        rank=4,
    )

    merged = dedup.merge(dedup.with_cid(openalex), dedup.with_cid(s2))

    assert merged.ids.doi == "10.1000/x"
    assert merged.ids.openalex == "W1"
    assert merged.ids.s2 == "paper-1"
    assert merged.ids.arxiv == "2501.10120"
    assert merged.abstract.startswith("A considerably longer")
    assert merged.tldr == "Defaults matter."
    assert merged.citation_count == 14
    assert merged.influential_citation_count == 3
    assert len(merged.authors) == 2
    assert len(merged.origins) == 2
    assert {origin.query_id for origin in merged.origins} == {"Q1", "Q2"}


def test_merge_recomputes_the_cid_from_the_merged_identifiers():
    """An arXiv-only record that gains a DOI must move to the DOI's cid, not keep the arXiv one."""
    arxiv_only = dedup.with_cid(make_candidate(arxiv="2501.10120"))
    with_doi = dedup.with_cid(make_candidate(arxiv="2501.10120", doi="10.1000/x"))

    merged = dedup.merge(arxiv_only, with_doi)

    assert merged.cid == dedup.with_cid(make_candidate(doi="10.1000/x")).cid
    assert merged.cid != arxiv_only.cid


def test_merge_never_loses_a_retraction_flag():
    clean = dedup.with_cid(make_candidate(doi="10.1000/x"))
    retracted = dedup.with_cid(make_candidate(doi="10.1000/x", is_retracted=True))
    assert dedup.merge(clean, retracted).is_retracted is True


def test_merge_upgrades_an_unknown_type():
    unknown = dedup.with_cid(make_candidate(doi="10.1000/x", work_type=WorkType.other))
    known = dedup.with_cid(make_candidate(doi="10.1000/x", work_type=WorkType.review))
    assert dedup.merge(unknown, known).type is WorkType.review


def test_merge_deduplicates_identical_origins():
    origin = Origin(source=SourceName.openalex, relation=Relation.query, query_id="Q1", rank=0)
    left = dedup.with_cid(make_candidate(doi="10.1000/x", origins=[origin]))
    right = dedup.with_cid(make_candidate(doi="10.1000/x", origins=[origin]))
    assert len(dedup.merge(left, right).origins) == 1


# --- deduplicate ------------------------------------------------------------


def test_deduplicate_merges_on_doi_across_sources():
    candidates = [
        make_candidate(doi="https://doi.org/10.1257/AER.20210881", openalex="W1"),
        make_candidate(doi="10.1257/aer.20210881", s2="p1", source=SourceName.s2, query_id="Q2"),
    ]

    kept, report = dedup.deduplicate(candidates)

    assert len(kept) == 1
    assert report.merged_by == {"doi": 1}
    assert len(kept[0].origins) == 2


def test_deduplicate_merges_on_arxiv_and_pmid():
    kept, report = dedup.deduplicate(
        [
            make_candidate(title="A", arxiv="2501.10120v1"),
            make_candidate(title="A", arxiv="2501.10120"),
            make_candidate(title="B", pmid="https://pubmed.ncbi.nlm.nih.gov/999"),
            make_candidate(title="B", pmid="999"),
        ]
    )

    assert len(kept) == 2
    assert report.merged_by == {"arxiv": 1, "pmid": 1}


def test_fuzzy_title_match_needs_a_corroborating_signal():
    """Same title, different first author, five years apart — two different papers."""
    kept, _ = dedup.deduplicate(
        [
            make_candidate(
                title="Choice architecture and defaults", year=2018, authors=("Ann Alpha",)
            ),
            make_candidate(
                title="Choice architecture and defaults", year=2024, authors=("Bo Beta",)
            ),
        ]
    )
    assert len(kept) == 2


def test_fuzzy_title_match_accepts_reformatting_with_the_same_first_author():
    kept, report = dedup.deduplicate(
        [
            make_candidate(
                title="Choice Architecture and Defaults", year=2018, authors=("Ann Alpha",)
            ),
            make_candidate(
                title="Choice architecture, and defaults!", year=2024, authors=("Ann Alpha",)
            ),
        ]
    )
    assert len(kept) == 1
    assert report.merged_by == {"title": 1}


def test_fuzzy_title_match_accepts_a_neighbouring_year():
    kept, _ = dedup.deduplicate(
        [
            make_candidate(
                title="Choice architecture and defaults", year=2023, authors=("Ann Alpha",)
            ),
            make_candidate(
                title="Choice architecture and defaults", year=2024, authors=("Bo Beta",)
            ),
        ]
    )
    assert len(kept) == 1


def test_deduplicate_preserves_first_seen_order():
    kept, _ = dedup.deduplicate(
        [
            make_candidate(title="First", doi="10.1000/a"),
            make_candidate(title="Second", doi="10.1000/b"),
            make_candidate(title="First again", doi="10.1000/a"),
        ]
    )
    assert [candidate.title for candidate in kept] == ["First", "Second"]


def test_deduplicate_is_deterministic():
    candidates = [
        make_candidate(title="A", doi="10.1000/a"),
        make_candidate(title="B", arxiv="2501.1"),
        make_candidate(title="A", doi="10.1000/a", source=SourceName.s2),
    ]
    first = [candidate.cid for candidate in dedup.deduplicate(candidates)[0]]
    second = [candidate.cid for candidate in dedup.deduplicate(candidates)[0]]
    assert first == second
