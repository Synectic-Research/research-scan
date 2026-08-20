"""Data contracts: round-trips, the constraints from spec §9.1, and generated docs."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from research_scan import schema as s

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_MD = REPO_ROOT / "skills" / "research-scan" / "references" / "schemas.md"

# Every model spec §5 names for schema.py.
SPEC_MODELS = [
    "QueryPlan",
    "Candidate",
    "ScreenFile",
    "Expanded",
    "Shortlist",
    "Ranked",
    "Verification",
    "EvidencePacket",
    "Evidence",
    "Manifest",
    "RunInfo",
    "ScanSummary",
    "EvalResult",
]


def query_plan_payload(**overrides) -> dict:
    payload = {
        "brief_summary": "A study of how default choice architecture affects retirement saving.",
        "domain": "behavioral",
        "window": {"from": "2023-08", "to": None},
        "sub_criteria": [
            {"id": "C1", "name": "problem match", "text": "defaults and enrolment decisions"},
            {"id": "C2", "name": "population", "text": "working adults in employer plans"},
            {"id": "C3", "name": "outcome", "text": "contribution rate or participation"},
        ],
        "must_not": ["cryptocurrency"],
        "queries": [
            {
                "id": "Q1",
                "type": "direct",
                "text": "default enrolment retirement saving",
                "mode": "semantic",
            },
            {
                "id": "Q2",
                "type": "terminology",
                "text": "automatic enrollment nudge pension",
                "mode": "semantic",
            },
            {
                "id": "Q3",
                "type": "mechanism",
                "text": "status quo bias choice architecture",
                "mode": "semantic",
            },
            {
                "id": "Q4",
                "type": "contradictory",
                "text": "null effects of nudges on saving",
                "mode": "semantic",
            },
            {
                "id": "Q5",
                "type": "review",
                "text": "review OR meta-analysis default effects",
                "mode": "keyword",
            },
            {
                "id": "Q6",
                "type": "adjacent",
                "text": "organ donation default opt-out",
                "mode": "semantic",
            },
        ],
    }
    payload.update(overrides)
    return payload


def candidate_payload(cid: str = "0123456789ab", **overrides) -> dict:
    payload = {
        "cid": cid,
        "title": "Defaults and the speed of retirement plan enrolment",
        "abstract": "We field an experiment across 40 employers.",
        "authors": [{"name": "A. Researcher", "s2_id": "1234"}],
        "year": 2024,
        "publication_date": "2024-04-01",
        "venue": "Journal of Public Economics",
        "type": "article",
        "ids": {"doi": "10.1000/example", "openalex": "W123"},
        "citation_count": 12,
        "is_retracted": False,
        "origins": [{"source": "openalex", "relation": "query", "query_id": "Q1", "rank": 3}],
        "outside_window": False,
    }
    payload.update(overrides)
    return payload


def run_info_payload() -> dict:
    return {
        "run_dir": "research/scans/2026-08-18-defaults",
        "slug": "defaults",
        "date": "2026-08-18",
        "brief_path": "research/scans/2026-08-18-defaults/brief.md",
        "defaults": {
            "window": {"from": "2023-08", "to": None},
            "top": 10,
            "foundational": 2,
            "domain": "behavioral",
            "sources": ["openalex", "s2"],
        },
    }


def ranked_entry_payload(cid: str = "0123456789ab", **overrides) -> dict:
    payload = {
        "cid": cid,
        "criteria": {"C1": 3, "C2": 2, "C3": 3},
        "overall": 3,
        "evidence_level": "rct",
        "flags": {"review": False, "contradicts": False, "methods_paper": False},
        "key_finding": "Automatic enrolment raised participation from 49% to 86%.",
        "methodology": "Field experiment, abstract-only.",
        "why_it_matters": "Sets the ceiling our default-design decision is measured against.",
        "limitations": ["single-country sample"],
        "relevance_reason": "Directly measures the outcome the brief targets.",
    }
    payload.update(overrides)
    return payload


def verification_payload(**overrides) -> dict:
    payload = {
        "verified": True,
        "verified_by": ["crossref", "openalex"],
        "verified_on": "2026-08-18",
        "title_match_ratio": 98.5,
        "mismatches": [],
    }
    payload.update(overrides)
    return payload


# --- registry ---------------------------------------------------------------


@pytest.mark.parametrize("name", SPEC_MODELS)
def test_every_spec_model_is_registered(name):
    assert name in s.MODELS


@pytest.mark.parametrize("name", sorted(s.MODELS))
def test_every_model_emits_a_json_schema(name):
    document = s.json_schema(name)
    assert document["title"] or document.get("$ref") or document.get("type")
    json.dumps(document)  # must be serialisable


def test_json_schema_rejects_an_unknown_name():
    with pytest.raises(KeyError):
        s.json_schema("NotAModel")


def test_scan_summary_schema_is_closed_for_structured_output():
    """`claude -p --json-schema` needs a closed object schema."""
    document = s.json_schema("ScanSummary")
    assert document["type"] == "object"
    assert document["additionalProperties"] is False


# --- round-trips ------------------------------------------------------------


def test_query_plan_round_trip_preserves_the_from_alias():
    plan = s.QueryPlan.model_validate(query_plan_payload())
    dumped = json.loads(plan.model_dump_json(by_alias=True))

    assert dumped["window"]["from"] == "2023-08"
    assert dumped["window"]["to"] is None
    assert s.QueryPlan.model_validate(dumped) == plan


def test_candidate_round_trip():
    candidate = s.Candidate.model_validate(candidate_payload())
    dumped = json.loads(candidate.model_dump_json(by_alias=True))
    assert s.Candidate.model_validate(dumped) == candidate


def test_screen_file_round_trip():
    payload = {
        "scores": [
            {
                "cid": "0123456789ab",
                "score": 2,
                "reason": "matches C1 and C3",
                "criteria_hit": ["C1", "C3"],
            }
        ]
    }
    screen = s.ScreenFile.model_validate(payload)
    assert json.loads(screen.model_dump_json()) == payload


def test_a_screen_file_without_criteria_hit_still_validates():
    """Pre-v0.2 `screen.json` files stay readable; coverage calls them unattributed."""
    payload = {"scores": [{"cid": "0123456789ab", "score": 2, "reason": "relevant"}]}
    screen = s.ScreenFile.model_validate(payload)
    assert screen.scores[0].criteria_hit == []


def test_gap_queries_belong_to_round2_not_to_the_plan():
    with pytest.raises(ValidationError, match="belong in `round2`"):
        s.QueryPlan.model_validate(
            query_plan_payload(
                queries=[
                    *query_plan_payload()["queries"][:5],
                    {"id": "Q6", "type": "gap", "text": "x", "target_criterion": "C1"},
                ]
            )
        )


def test_a_gap_query_must_name_a_target_criterion():
    with pytest.raises(ValidationError, match="must name a target_criterion"):
        s.QueryPlan.model_validate(
            query_plan_payload(round2=[{"id": "G1", "type": "gap", "text": "thin area"}])
        )


def test_a_target_criterion_must_exist():
    with pytest.raises(ValidationError, match="unknown criterion"):
        s.QueryPlan.model_validate(
            query_plan_payload(
                round2=[{"id": "G1", "type": "gap", "text": "x", "target_criterion": "C9"}]
            )
        )


def test_round2_ids_must_not_collide_with_round_one():
    with pytest.raises(ValidationError, match="unique across"):
        s.QueryPlan.model_validate(
            query_plan_payload(
                round2=[{"id": "Q1", "type": "gap", "text": "x", "target_criterion": "C1"}]
            )
        )


def test_round2_is_empty_until_the_gap_round():
    assert s.QueryPlan.model_validate(query_plan_payload()).round2 == []


def test_ranked_round_trip_as_a_bare_array():
    ranked = s.Ranked.model_validate([ranked_entry_payload()])
    dumped = json.loads(ranked.model_dump_json(by_alias=True))
    assert isinstance(dumped, list)
    assert s.Ranked.model_validate(dumped) == ranked


def test_evidence_round_trip_with_verification():
    packet = (
        candidate_payload()
        | ranked_entry_payload()
        | {
            "verification": verification_payload(),
            "rank": 1,
            "selection_reason": "score",
            "url": "https://doi.org/10.1000/example",
        }
    )
    evidence = s.Evidence.model_validate(
        {"run": run_info_payload(), "packets": [packet], "alternates": []}
    )
    dumped = json.loads(evidence.model_dump_json(by_alias=True))
    assert s.Evidence.model_validate(dumped) == evidence
    assert evidence.packets[0].verification.verified is True


def test_shortlist_round_trip():
    scored = candidate_payload() | {"score": 3}
    shortlist = s.Shortlist.model_validate({"in_window": [scored], "outside_window": []})
    assert shortlist.in_window[0].score == 3


def test_manifest_sections_are_independently_upsertable():
    manifest = s.Manifest.model_validate(
        {
            "run": run_info_payload(),
            "defaults": run_info_payload()["defaults"],
            "tool_version": "0.1.0",
        }
    )
    assert manifest.retrieval is None
    assert manifest.counts.retrieved == 0


def test_scan_summary_and_eval_result_round_trip():
    summary = s.ScanSummary.model_validate(
        {
            "run_dir": "research/scans/2026-08-18-defaults",
            "evidence_json": "research/scans/2026-08-18-defaults/evidence.json",
            "top": [
                {
                    "rank": 1,
                    "title": "Defaults and the speed of retirement plan enrolment",
                    "year": 2024,
                    "doi": "10.1000/example",
                    "evidence_level": "rct",
                    "verified": True,
                    "why": "design-changing; the field experiment our enrolment decision rests on",
                }
            ],
            "counts": {},
            "unverified": [{"title": "A preprint", "mismatches": ["doi_unresolved"]}],
            "coverage_risks": "Q6 returned 3 hits.",
        }
    )
    assert s.ScanSummary.model_validate(json.loads(summary.model_dump_json())) == summary

    result = s.EvalResult.model_validate(
        {
            "topic": "defaults",
            "run_dir": "research/scans/2026-08-18-defaults",
            "expected": 6,
            "found_at_10": 4,
            "found_at_25": 5,
            "recall_10": 0.667,
            "recall_25": 0.833,
            "misses": [{"doi": "10.1000/missed", "why": "terminology gap"}],
        }
    )
    assert result.judged is None


# --- constraints (these are what make `exit 2` actionable) ------------------


def test_fewer_than_six_queries_is_rejected():
    payload = query_plan_payload()
    payload["queries"] = payload["queries"][:5]
    with pytest.raises(ValidationError):
        s.QueryPlan.model_validate(payload)


def test_more_than_eight_queries_is_rejected():
    payload = query_plan_payload()
    extra = [
        {"id": f"Q{i}", "type": "emerging", "text": "another query", "mode": "semantic"}
        for i in range(7, 11)
    ]
    payload["queries"] = payload["queries"] + extra
    with pytest.raises(ValidationError):
        s.QueryPlan.model_validate(payload)


def test_missing_mandatory_query_type_is_rejected():
    payload = query_plan_payload()
    payload["queries"][4]["type"] = "emerging"  # drops the mandatory `review`
    with pytest.raises(ValidationError, match="review"):
        s.QueryPlan.model_validate(payload)


def test_duplicate_query_ids_are_rejected():
    payload = query_plan_payload()
    payload["queries"][1]["id"] = "Q1"
    with pytest.raises(ValidationError, match="unique"):
        s.QueryPlan.model_validate(payload)


def test_query_text_longer_than_thirty_words_is_rejected():
    payload = query_plan_payload()
    payload["queries"][0]["text"] = " ".join(["word"] * 31)
    with pytest.raises(ValidationError, match="30 words"):
        s.QueryPlan.model_validate(payload)


def test_domain_auto_is_rejected_the_agent_must_resolve_it():
    with pytest.raises(ValidationError):
        s.QueryPlan.model_validate(query_plan_payload(domain="auto"))


@pytest.mark.parametrize("count", [2, 7])
def test_sub_criteria_must_number_three_to_six(count):
    payload = query_plan_payload()
    payload["sub_criteria"] = [
        {"id": f"C{i}", "name": f"c{i}", "text": "..."} for i in range(1, count + 1)
    ]
    with pytest.raises(ValidationError):
        s.QueryPlan.model_validate(payload)


def test_unknown_keys_are_rejected_so_typos_surface_as_exit_2():
    with pytest.raises(ValidationError):
        s.QueryPlan.model_validate(query_plan_payload(subcriteria=[]))


@pytest.mark.parametrize("score", [-1, 4])
def test_screen_scores_outside_zero_to_three_are_rejected(score):
    with pytest.raises(ValidationError):
        s.ScreenFile.model_validate(
            {"scores": [{"cid": "0123456789ab", "score": score, "reason": "x"}]}
        )


def test_malformed_cid_is_rejected():
    with pytest.raises(ValidationError):
        s.Candidate.model_validate(candidate_payload(cid="not-a-cid"))


def test_malformed_window_month_is_rejected():
    with pytest.raises(ValidationError):
        s.QueryPlan.model_validate(query_plan_payload(window={"from": "2023-13", "to": None}))


def test_summary_why_is_bounded_at_thirty_words():
    payload = {
        "rank": 1,
        "title": "T",
        "evidence_level": "rct",
        "verified": True,
        "why": " ".join(["word"] * 31),
    }
    with pytest.raises(ValidationError, match="30 words"):
        s.SummaryPaper.model_validate(payload)


def test_ranked_relation_round_trips_and_is_optional():
    entry = s.RankedEntry.model_validate(ranked_entry_payload(relation="foundational"))
    assert entry.relation is s.BriefRelation.foundational
    assert json.loads(entry.model_dump_json())["relation"] == "foundational"
    # pre-S4.5 files omit it entirely
    assert s.RankedEntry.model_validate(ranked_entry_payload()).relation is None


def test_anchor_requires_a_title_or_doi():
    with pytest.raises(ValidationError, match="title or a doi"):
        s.Anchor.model_validate({})
    assert s.Anchor.model_validate({"doi": "10.1000/x"}).doi == "10.1000/x"
    assert s.Anchor.model_validate({"title": "A paper"}).title == "A paper"


def test_query_plan_accepts_anchors():
    plan = s.QueryPlan.model_validate(
        query_plan_payload(anchors=[{"doi": "10.1086/380085"}, {"title": "Save More Tomorrow"}])
    )
    assert len(plan.anchors) == 2


def test_ranked_entry_requires_at_least_one_limitation():
    with pytest.raises(ValidationError):
        s.Ranked.model_validate([ranked_entry_payload(limitations=[])])


def test_evidence_packet_requires_verification():
    packet = candidate_payload() | ranked_entry_payload() | {"rank": 1, "selection_reason": "score"}
    with pytest.raises(ValidationError):
        s.EvidencePacket.model_validate(packet)


# --- generated documentation ------------------------------------------------


def test_markdown_is_deterministic_and_covers_every_model():
    first = s.markdown()
    assert first == s.markdown()
    for name in s.MODELS:
        assert f"### {name}" in first


def test_schemas_md_is_current():
    """Acceptance §14.9: references/schemas.md equals `research-scan schema --md`."""
    assert SCHEMAS_MD.exists(), (
        "run: research-scan schema --md > skills/research-scan/references/schemas.md"
    )
    assert SCHEMAS_MD.read_text(encoding="utf-8") == s.markdown()
