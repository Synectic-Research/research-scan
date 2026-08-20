"""Verification against the live record (spec §10.5)."""

from __future__ import annotations

from datetime import date

import httpx
import pytest
import respx

from conftest import make_candidate, ranked_entry
from research_scan import verify as verify_module
from research_scan.dedup import with_cid
from research_scan.http import HttpClient
from research_scan.schema import Mismatch, VerifiedBy
from research_scan.sources import crossref as crossref_module
from research_scan.sources.crossref import CrossrefRecord, CrossrefSource, CrossrefUnavailable
from research_scan.sources.openalex import OpenAlexSource

TODAY = date(2026, 8, 19)


def crossref_record(**overrides) -> CrossrefRecord:
    payload = {
        "doi": "10.1000/a",
        "title": "Default options and retirement saving dynamics",
        "year": 2024,
        "first_author_surname": "Researcher",
        "retracted": False,
    }
    payload.update(overrides)
    return CrossrefRecord(**payload)


def verify_one(candidate, *, crossref=None, openalex=None, attempted=True, ratio=90):
    return verify_module.verify_entry(
        candidate,
        crossref=crossref,
        crossref_attempted=attempted,
        openalex=openalex,
        ratio=ratio,
        today=TODAY,
    )


# --- the happy path ---------------------------------------------------------


def test_a_matching_record_verifies():
    candidate = with_cid(make_candidate(doi="10.1000/a", year=2024))
    result = verify_one(
        candidate,
        crossref=crossref_record(),
        openalex={"title": candidate.title, "publication_year": 2024, "is_retracted": False},
    )

    assert result.verified is True
    assert result.mismatches == []
    assert VerifiedBy.crossref in result.verified_by
    assert VerifiedBy.openalex in result.verified_by
    assert result.verified_on == "2026-08-19"
    assert result.title_match_ratio == 100.0


def test_a_year_one_off_is_tolerated():
    """Print-vs-online dates disagree constantly; ±1 is the spec's tolerance."""
    candidate = with_cid(make_candidate(doi="10.1000/a", year=2024))
    assert verify_one(candidate, crossref=crossref_record(year=2025)).verified is True


def test_a_missing_year_on_either_side_is_not_a_mismatch():
    candidate = with_cid(make_candidate(doi="10.1000/a", year=None))
    assert verify_one(candidate, crossref=crossref_record(year=2019)).verified is True


# --- mismatches -------------------------------------------------------------


def test_a_different_title_is_a_mismatch_not_a_deletion():
    candidate = with_cid(make_candidate(doi="10.1000/a", title="Something else entirely"))
    result = verify_one(candidate, crossref=crossref_record())

    assert result.verified is False
    assert Mismatch.title in result.mismatches
    assert VerifiedBy.crossref in result.verified_by  # the record resolved; it just disagreed


def test_a_wrong_year_is_a_mismatch():
    candidate = with_cid(make_candidate(doi="10.1000/a", year=2019))
    assert Mismatch.year in verify_one(candidate, crossref=crossref_record(year=2024)).mismatches


def test_a_different_first_author_is_a_mismatch():
    candidate = with_cid(make_candidate(doi="10.1000/a", authors=("Bo Beta",)))
    assert Mismatch.author in verify_one(candidate, crossref=crossref_record()).mismatches


def test_an_unresolvable_doi_is_flagged():
    candidate = with_cid(make_candidate(doi="10.1000/nope"))
    result = verify_one(candidate, crossref=None, openalex=None)

    assert result.verified is False
    assert Mismatch.doi_unresolved in result.mismatches


def test_no_record_anywhere_for_a_doiless_paper():
    candidate = with_cid(make_candidate(title="Untraceable", doi=None))
    result = verify_one(candidate, crossref=None, openalex=None, attempted=False)
    assert result.mismatches == [Mismatch.no_record]


def test_strict_mode_raises_the_title_bar():
    candidate = with_cid(
        make_candidate(doi="10.1000/a", title="Default options and retirement savings")
    )
    lenient = verify_one(candidate, crossref=crossref_record(), ratio=90)
    strict = verify_one(candidate, crossref=crossref_record(), ratio=95)

    assert lenient.verified is True
    assert strict.verified is False
    assert Mismatch.title in strict.mismatches


def test_verify_options_carry_the_two_thresholds():
    assert verify_module.VerifyOptions().title_ratio == 90
    assert verify_module.VerifyOptions(strict=True).title_ratio == 95


# --- retraction -------------------------------------------------------------


def test_openalex_retraction_is_caught_even_when_crossref_is_silent():
    """The Wakefield case: Crossref resolves it happily, OpenAlex knows it was retracted."""
    candidate = with_cid(make_candidate(doi="10.1000/a", year=2024))
    result = verify_one(
        candidate,
        crossref=crossref_record(),
        openalex={"title": candidate.title, "publication_year": 2024, "is_retracted": True},
    )

    assert result.verified is False
    assert Mismatch.retracted in result.mismatches


def test_a_crossref_retraction_notice_is_caught():
    candidate = with_cid(make_candidate(doi="10.1000/a", year=2024))
    result = verify_one(candidate, crossref=crossref_record(retracted=True))
    assert Mismatch.retracted in result.mismatches


def test_the_retracted_title_prefix_is_not_mistaken_for_a_title_mismatch():
    candidate = with_cid(
        make_candidate(doi="10.1000/a", title="Ileal-lymphoid-nodular hyperplasia")
    )
    record = crossref_record(title="Ileal-lymphoid-nodular hyperplasia", retracted=True)
    result = verify_one(candidate, crossref=record)

    assert Mismatch.retracted in result.mismatches
    assert Mismatch.title not in result.mismatches


# --- arXiv-only path --------------------------------------------------------


def test_an_arxiv_only_paper_verifies_by_its_arxiv_and_s2_identity():
    candidate = with_cid(make_candidate(doi=None, arxiv="2501.10120", s2="paper-1"))
    result = verify_one(candidate, crossref=None, openalex=None, attempted=False)

    assert result.verified is True
    assert result.verified_by == [VerifiedBy.arxiv, VerifiedBy.s2]


# --- the whole stage --------------------------------------------------------


class FakeCrossref:
    def __init__(self, records=None, unavailable_after=None):
        self._records = records or {}
        self._unavailable_after = unavailable_after
        self.calls = 0

    def lookup(self, doi, *, cache=None):
        self.calls += 1
        if self._unavailable_after is not None and self.calls > self._unavailable_after:
            raise CrossrefUnavailable("crossref HTTP 429")
        return self._records.get(doi)


class FakeOpenAlex:
    def __init__(self, records=None):
        self._records = records or {}

    def lookup(self, *, doi=None, openalex_id=None, cache=None):
        return self._records.get(doi)


def test_run_verify_stamps_every_entry_and_counts():
    good = with_cid(make_candidate(doi="10.1000/a", year=2024))
    bad = with_cid(make_candidate(title="Mystery", doi="10.1000/b", year=2024))
    entries = [ranked_entry(good.cid), ranked_entry(bad.cid)]

    result = verify_module.run_verify(
        entries,
        {good.cid: good, bad.cid: bad},
        FakeCrossref(
            {"10.1000/a": crossref_record(), "10.1000/b": crossref_record(doi="10.1000/b")}
        ),
        FakeOpenAlex(),
        options=verify_module.VerifyOptions(),
        today=TODAY,
    )

    assert all(entry.verification is not None for entry in result.entries)
    assert result.stats.verified == 1
    assert result.stats.unverified == 1
    assert result.unverified[0][0] == "Mystery"


def test_a_retraction_found_at_verify_is_counted():
    candidate = with_cid(make_candidate(doi="10.1000/a", year=2024))
    result = verify_module.run_verify(
        [ranked_entry(candidate.cid)],
        {candidate.cid: candidate},
        FakeCrossref({"10.1000/a": crossref_record(retracted=True)}),
        FakeOpenAlex(),
        options=verify_module.VerifyOptions(),
        today=TODAY,
    )
    assert result.stats.dropped_retracted == 1


def test_crossref_refusing_once_skips_it_for_the_rest_of_the_run():
    """§10.5: one 429 ends Crossref; OpenAlex carries the rest and the manifest says so."""
    first = with_cid(make_candidate(doi="10.1000/a", year=2024))
    second = with_cid(make_candidate(title="Second paper", doi="10.1000/b", year=2024))
    crossref = FakeCrossref({"10.1000/a": crossref_record()}, unavailable_after=1)
    openalex = FakeOpenAlex(
        {
            "10.1000/a": {"title": first.title, "publication_year": 2024},
            "10.1000/b": {"title": second.title, "publication_year": 2024},
        }
    )

    result = verify_module.run_verify(
        [ranked_entry(first.cid), ranked_entry(second.cid)],
        {first.cid: first, second.cid: second},
        crossref,
        openalex,
        options=verify_module.VerifyOptions(),
        today=TODAY,
    )

    assert result.stats.crossref_skipped is True
    assert crossref.calls == 2  # tried once more, then gave up for good
    assert result.entries[1].verification.verified is True
    assert result.entries[1].verification.verified_by == [VerifiedBy.openalex]
    assert result.stats.verified == 2


# --- the Crossref adapter over recorded shapes ------------------------------


@pytest.fixture
def client(fake_settings):
    with HttpClient(fake_settings, cache=False, sleep=lambda _: None, max_retries=1) as http_client:
        yield http_client


@respx.mock
def test_crossref_parses_a_real_response(client):
    respx.get(url__regex=r"https://api\.crossref\.org/works/.*").mock(
        return_value=httpx.Response(
            200,
            json={
                "message": {
                    "DOI": "10.1257/aer.20210881",
                    "title": ["Default Options and Retirement Saving Dynamics"],
                    "issued": {"date-parts": [[2025, 11, 1]]},
                    "author": [{"given": "Taha", "family": "Choukhmane", "sequence": "first"}],
                    "update-to": None,
                }
            },
        )
    )
    record = CrossrefSource(client).lookup("10.1257/aer.20210881")

    assert record.title == "Default Options and Retirement Saving Dynamics"
    assert record.year == 2025
    assert record.first_author_surname == "Choukhmane"
    assert record.retracted is False


@respx.mock
def test_crossref_strips_a_retracted_prefix_and_flags_it(client):
    respx.get(url__regex=r"https://api\.crossref\.org/works/.*").mock(
        return_value=httpx.Response(
            200,
            json={
                "message": {
                    "DOI": "10.1016/x",
                    "title": ["RETRACTED: Ileal-lymphoid-nodular hyperplasia"],
                    "issued": {"date-parts": [[1998, 2]]},
                    "author": [{"given": "AJ", "family": "Wakefield", "sequence": "first"}],
                }
            },
        )
    )
    record = CrossrefSource(client).lookup("10.1016/x")

    assert record.title == "Ileal-lymphoid-nodular hyperplasia"
    assert record.retracted is True


@respx.mock
def test_crossref_reads_an_update_to_retraction_notice(client):
    respx.get(url__regex=r"https://api\.crossref\.org/works/.*").mock(
        return_value=httpx.Response(
            200,
            json={
                "message": {
                    "DOI": "10.1000/x",
                    "title": ["A withdrawn study"],
                    "update-to": [{"type": "retraction", "DOI": "10.1000/notice"}],
                }
            },
        )
    )
    assert CrossrefSource(client).lookup("10.1000/x").retracted is True


@respx.mock
def test_an_unresolvable_doi_returns_none(client):
    respx.get(url__regex=r"https://api\.crossref\.org/works/.*").mock(
        return_value=httpx.Response(404)
    )
    assert CrossrefSource(client).lookup("10.1000/nope") is None


@pytest.mark.parametrize("status", [403, 429])
@respx.mock
def test_crossref_shutting_us_out_raises_the_skip_signal(client, status):
    respx.get(url__regex=r"https://api\.crossref\.org/works/.*").mock(
        return_value=httpx.Response(status)
    )
    with pytest.raises(CrossrefUnavailable):
        CrossrefSource(client).lookup("10.1000/x")


@respx.mock
def test_openalex_lookup_reads_the_retraction_flag(client):
    respx.get(url__regex=r"https://api\.openalex\.org/works.*").mock(
        return_value=httpx.Response(
            200,
            json={
                "results": [
                    {"id": "https://openalex.org/W1", "title": "A work", "is_retracted": True}
                ]
            },
        )
    )
    record = OpenAlexSource(client).lookup(doi="10.1000/x")
    assert record["is_retracted"] is True


@respx.mock
def test_openalex_lookup_returns_none_when_nothing_matches(client):
    respx.get(url__regex=r"https://api\.openalex\.org/works.*").mock(
        return_value=httpx.Response(200, json={"results": []})
    )
    assert OpenAlexSource(client).lookup(doi="10.1000/x") is None


def test_crossref_module_exposes_its_url_template():
    assert "{doi}" in crossref_module.WORKS_URL


# --- S4.5 hardening: bibliographic identification of DOI-less records --------


class BibliographicCrossref:
    """A Crossref stub whose bibliographic search returns a fixed record list."""

    def __init__(self, records=None):
        self._records = records or []
        self.bibliographic_calls: list[tuple] = []

    def lookup(self, doi, *, cache=None):
        return None

    def search_bibliographic(self, title, first_author_surname, year, *, cache=None):
        from research_scan.dedup import title_similarity
        from research_scan.sources.crossref import (
            BIBLIOGRAPHIC_TITLE_RATIO,
            BIBLIOGRAPHIC_YEAR_TOLERANCE,
        )

        self.bibliographic_calls.append((title, first_author_surname, year))
        for record in self._records:
            if title_similarity(title, record.title) < BIBLIOGRAPHIC_TITLE_RATIO:
                continue
            if (
                year is not None
                and record.year is not None
                and abs(year - record.year) > BIBLIOGRAPHIC_YEAR_TOLERANCE
            ):
                continue
            return record
        return None


def no_doi_candidate():
    return with_cid(
        make_candidate(
            title="How Do Consumers Finance Increased Retirement Savings? ∗",
            doi=None,
            s2="d704ca9b2a66",
            year=2023,
            authors=("Taha Choukhmane",),
        )
    )


def test_a_doiless_record_is_identified_by_bibliographic_search():
    candidate = no_doi_candidate()
    match = crossref_record(
        doi="10.3386/w99999",
        title="How Do Consumers Finance Increased Retirement Savings?",
        year=2023,
        first_author_surname="Choukhmane",
    )
    crossref = BibliographicCrossref([match])

    result = verify_module.run_verify(
        [ranked_entry(candidate.cid)],
        {candidate.cid: candidate},
        crossref,
        FakeOpenAlex(),
        options=verify_module.VerifyOptions(),
        today=TODAY,
    )

    verification = result.entries[0].verification
    assert crossref.bibliographic_calls  # it was attempted
    assert verification.verified is True
    assert VerifiedBy.crossref in verification.verified_by
    assert Mismatch.no_record not in verification.mismatches


def test_the_real_near_miss_is_rejected_not_misidentified():
    """Live finding: the search returns a same-author-DIFFERENT-paper item. It must not match."""
    candidate = no_doi_candidate()
    near_miss = crossref_record(
        doi="10.3386/w31195",
        title=(
            "Efficiency in Household Decision Making:"
            " Evidence from the Retirement Savings of U.S. Couples"
        ),
        year=2023,
        first_author_surname="Choukhmane",
    )
    crossref = BibliographicCrossref([near_miss])

    result = verify_module.run_verify(
        [ranked_entry(candidate.cid)],
        {candidate.cid: candidate},
        crossref,
        FakeOpenAlex(),
        options=verify_module.VerifyOptions(),
        today=TODAY,
    )

    verification = result.entries[0].verification
    assert crossref.bibliographic_calls  # attempted, then honestly rejected
    assert verification.verified is False
    assert Mismatch.no_record in verification.mismatches


def test_bibliographic_search_is_not_attempted_when_a_doi_exists():
    candidate = with_cid(make_candidate(doi="10.1000/a", year=2024))
    crossref = BibliographicCrossref([])

    verify_module.run_verify(
        [ranked_entry(candidate.cid)],
        {candidate.cid: candidate},
        crossref,
        FakeOpenAlex(),
        options=verify_module.VerifyOptions(),
        today=TODAY,
    )

    assert crossref.bibliographic_calls == []


@respx.mock
def test_search_bibliographic_parses_and_gates_a_real_response(client):
    respx.get(url__regex=r"https://api\.crossref\.org/works\?.*").mock(
        return_value=httpx.Response(
            200,
            json={
                "message": {
                    "items": [
                        {
                            "DOI": "10.3386/w31195",
                            "title": ["Efficiency in Household Decision Making"],
                            "issued": {"date-parts": [[2023]]},
                            "author": [{"family": "Choukhmane", "sequence": "first"}],
                        },
                        {
                            "DOI": "10.3386/w99999",
                            "title": ["How Do Consumers Finance Increased Retirement Savings?"],
                            "issued": {"date-parts": [[2023]]},
                            "author": [{"family": "Choukhmane", "sequence": "first"}],
                        },
                    ]
                }
            },
        )
    )
    record = CrossrefSource(client).search_bibliographic(
        "How Do Consumers Finance Increased Retirement Savings? ∗", "Choukhmane", 2023
    )
    assert record is not None
    assert record.doi == "10.3386/w99999"  # the near-miss was passed over, the exact hit taken


# --- S4.5 hardening: S2 retraction signal ------------------------------------


class FakeS2Types:
    def __init__(self, types):
        self._types = types
        self.calls: list[str] = []

    def lookup_publication_types(self, paper_id, *, cache=None):
        self.calls.append(paper_id)
        return self._types


def test_s2_retracted_publication_type_is_a_retraction_mismatch():
    candidate = with_cid(make_candidate(doi="10.1000/a", s2="p1", year=2024))
    result = verify_module.run_verify(
        [ranked_entry(candidate.cid)],
        {candidate.cid: candidate},
        FakeCrossref({"10.1000/a": crossref_record()}),
        FakeOpenAlex(),
        FakeS2Types(["JournalArticle", "Retracted"]),
        options=verify_module.VerifyOptions(),
        today=TODAY,
    )

    verification = result.entries[0].verification
    assert Mismatch.retracted in verification.mismatches
    assert VerifiedBy.s2 not in verification.verified_by  # a status signal, not an identity check
    assert result.stats.dropped_retracted == 1


def test_a_clean_s2_record_adds_no_mismatch():
    candidate = with_cid(make_candidate(doi="10.1000/a", s2="p1", year=2024))
    s2 = FakeS2Types(["JournalArticle"])
    result = verify_module.run_verify(
        [ranked_entry(candidate.cid)],
        {candidate.cid: candidate},
        FakeCrossref({"10.1000/a": crossref_record()}),
        FakeOpenAlex(),
        s2,
        options=verify_module.VerifyOptions(),
        today=TODAY,
    )

    assert s2.calls == ["p1"]
    assert result.entries[0].verification.verified is True
