"""Shared builders for the S1 tests: candidates, plans, and the recorded API fixtures."""

from __future__ import annotations

import json
import logging
from collections.abc import Iterable
from pathlib import Path

import pytest

from research_scan import config, log
from research_scan.schema import (
    Author,
    Candidate,
    Ids,
    Origin,
    QueryPlan,
    RankedEntry,
    Relation,
    SourceName,
    WorkType,
)

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    """A response recorded from the real API with the same params production sends."""
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def make_candidate(
    title: str = "Default options and retirement saving dynamics",
    *,
    cid: str = "0" * 12,
    doi: str | None = None,
    arxiv: str | None = None,
    pmid: str | None = None,
    s2: str | None = None,
    openalex: str | None = None,
    year: int | None = 2024,
    publication_date: str | None = None,
    abstract: str | None = None,
    tldr: str | None = None,
    venue: str | None = None,
    authors: Iterable[str] = ("Ada Researcher",),
    citation_count: int = 0,
    influential_citation_count: int | None = None,
    is_retracted: bool = False,
    work_type: WorkType = WorkType.article,
    raw_type: str | None = "article",
    origins: list[Origin] | None = None,
    source: SourceName = SourceName.openalex,
    query_id: str | None = "Q1",
    rank: int = 0,
) -> Candidate:
    return Candidate(
        cid=cid,
        title=title,
        abstract=abstract,
        tldr=tldr,
        authors=[Author(name=name) for name in authors],
        year=year,
        publication_date=publication_date,
        venue=venue,
        type=work_type,
        raw_type=raw_type,
        ids=Ids(doi=doi, arxiv=arxiv, pmid=pmid, s2=s2, openalex=openalex),
        citation_count=citation_count,
        influential_citation_count=influential_citation_count,
        is_retracted=is_retracted,
        origins=origins
        if origins is not None
        else [Origin(source=source, relation=Relation.query, query_id=query_id, rank=rank)],
    )


def ranked_entry(
    cid: str,
    *,
    overall: int = 2,
    criteria: dict[str, int] | None = None,
    evidence_level: str = "experimental",
    review: bool = False,
    contradicts: bool = False,
    methods_paper: bool = False,
    relation: str | None = None,
    verification: dict | None = None,
) -> RankedEntry:
    payload = {
        "cid": cid,
        "criteria": criteria or {"C1": overall, "C2": overall, "C3": overall},
        "overall": overall,
        "evidence_level": evidence_level,
        "relation": relation,
        "flags": {"review": review, "contradicts": contradicts, "methods_paper": methods_paper},
        "key_finding": "Defaults raised enrolment from 49% to 86%.",
        "methodology": "Field experiment, abstract-only.",
        "why_it_matters": "Sets the ceiling for our enrolment decision.",
        "limitations": ["single-country sample"],
        "relevance_reason": "Measures the outcome the brief targets.",
    }
    if verification is not None:
        payload["verification"] = verification
    return RankedEntry.model_validate(payload)


def verification_payload(verified: bool = True, mismatches: list[str] | None = None) -> dict:
    return {
        "verified": verified,
        "verified_by": ["crossref", "openalex"] if verified else [],
        "verified_on": "2026-08-19",
        "title_match_ratio": 99.0 if verified else 40.0,
        "mismatches": mismatches or [],
    }


def plan_payload(**overrides) -> dict:
    payload = {
        "brief_summary": "How default choice architecture shapes savings-product enrolment.",
        "domain": "behavioral",
        "window": {"from": "2023-08", "to": None},
        "sub_criteria": [
            {"id": "C1", "name": "problem match", "text": "defaults and enrolment decisions"},
            {"id": "C2", "name": "population", "text": "consumers choosing a savings product"},
            {"id": "C3", "name": "outcome", "text": "enrolment or contribution rate"},
        ],
        "must_not": [],
        "queries": [
            {
                "id": "Q1",
                "type": "direct",
                "text": "default enrollment savings",
                "mode": "semantic",
            },
            {
                "id": "Q2",
                "type": "terminology",
                "text": "automatic enrolment nudge",
                "mode": "semantic",
            },
            {
                "id": "Q3",
                "type": "mechanism",
                "text": "status quo bias inertia",
                "mode": "semantic",
            },
            {
                "id": "Q4",
                "type": "contradictory",
                "text": "null effects of nudges",
                "mode": "semantic",
            },
            {
                "id": "Q5",
                "type": "review",
                "text": "meta-analysis default effects",
                "mode": "keyword",
            },
            {"id": "Q6", "type": "adjacent", "text": "organ donation opt-out", "mode": "semantic"},
        ],
    }
    payload.update(overrides)
    return payload


def make_plan(**overrides) -> QueryPlan:
    return QueryPlan.model_validate(plan_payload(**overrides))


@pytest.fixture(autouse=True)
def isolate_logging():
    """`log.configure` mutates a module-level logger; restore it so tests cannot leak."""
    logger = logging.getLogger(log.ROOT_LOGGER)
    handlers, level, propagate = list(logger.handlers), logger.level, logger.propagate
    yield
    logger.handlers = handlers
    logger.setLevel(level)
    logger.propagate = propagate


def settings_for(**values: str) -> config.Settings:
    """A Settings carrying exactly these credentials, for stage code that records auth mode.

    Not a fixture: stage helpers build one inline, and the paths are deliberately unreachable so a
    test that accidentally reads the filesystem fails loudly instead of picking up the real HOME.
    """
    return config.Settings(
        values=dict(values),
        origins=dict.fromkeys(values, "env"),
        config_env=Path("/nonexistent/.config/research-scan/.env"),
        local_env=Path("/nonexistent/.env"),
        cache_db=Path("/nonexistent/http.sqlite"),
    )


@pytest.fixture
def fake_settings(tmp_path, monkeypatch) -> config.Settings:
    """Credentials that look real enough to exercise auth, in an isolated HOME and cwd."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.chdir(tmp_path)
    for var in config.KNOWN_VARS:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("OPENALEX_API_KEY", "fake-openalex-key-abcd")
    monkeypatch.setenv("OPENALEX_MAILTO", "me@example.com")
    monkeypatch.setenv("S2_API_KEY", "fake-s2-key-wxyz")
    return config.load()
