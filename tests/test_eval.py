"""Golden-set recall, judge merging, and the two S4 fixes (spec §13, §9.11)."""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from conftest import make_candidate, ranked_entry, verification_payload
from research_scan import evalrun, run
from research_scan import schema as s
from research_scan.dedup import arxiv_id_from_doi, is_arxiv_doi, with_cid
from research_scan.run import StageInputError
from research_scan.schema import (
    CandidatesFile,
    Defaults,
    Evidence,
    EvidencePacket,
    GoldenTopic,
    JudgeFile,
    Ranked,
    RunInfo,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
GOLDEN_DIR = REPO_ROOT / "eval" / "golden"


# --- the golden files that ship in this repo --------------------------------


def test_every_golden_file_matches_the_contract():
    """A typo in a curated file must fail here, not silently score zero in a run."""
    files = sorted(GOLDEN_DIR.glob("*.yaml"))
    assert files, "no golden topics found"
    for path in files:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not payload.get("expected"):
            continue  # the placeholder is deliberately unscoreable until the maintainer fills it in
        GoldenTopic.model_validate(payload)


def test_every_ratified_topic_carries_its_evidence():
    """Only the maintainer promotes a topic; a promoted one must justify every entry it holds."""
    for path in sorted(GOLDEN_DIR.glob("*.yaml")):
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        status = payload.get("status")
        assert status in {"draft", "ratified-with-caveat", "ratified"}, path.name
        if status == "draft":
            continue
        topic = GoldenTopic.model_validate(payload)
        assert topic.expected, f"{path.name} is ratified with no expected papers"
        for paper in topic.expected:
            assert paper.why.strip(), f"{path.name}: {paper.doi} has no why"


def test_the_placeholder_is_still_a_draft():
    payload = yaml.safe_load((GOLDEN_DIR / "TOPIC3-PLACEHOLDER.yaml").read_text(encoding="utf-8"))
    assert payload["status"] == "draft"


def test_the_placeholder_cannot_be_scored_by_accident():
    payload = yaml.safe_load((GOLDEN_DIR / "TOPIC3-PLACEHOLDER.yaml").read_text(encoding="utf-8"))
    assert payload["expected"] == []
    with pytest.raises(ValidationError):
        GoldenTopic.model_validate(payload)  # min_length=1 on `expected`


# --- fixtures ---------------------------------------------------------------


def topic_payload(**overrides) -> dict:
    payload = {
        "topic": "t",
        "status": "draft",
        "brief": "A brief.",
        "domain": "behavioral",
        "expected": [
            {"doi": "10.1000/a", "why": "the central result"},
            {"doi": "10.1000/b", "why": "the contradicting one"},
        ],
    }
    payload.update(overrides)
    return payload


def build_run(
    tmp_path: Path,
    emitted: list[str],
    ranked_only: list[str] = (),
    foundational: list[str] = (),
) -> evalrun.RunFiles:
    """A run where `emitted` reached the top 10 and `ranked_only` stayed in the ranked pool.

    `foundational` appends packets in the reserved out-of-window slots, as `emit` writes them.
    """
    info = RunInfo.model_validate(
        {
            "run_dir": str(tmp_path),
            "slug": "t",
            "date": "2026-08-19",
            "brief_path": str(tmp_path / "brief.md"),
            "defaults": {"domain": "behavioral"},
        }
    )
    candidates, packets, entries = {}, [], []
    slots = [(doi, "score") for doi in emitted] + [(doi, "foundational") for doi in foundational]
    for rank, (doi, reason) in enumerate(slots, start=1):
        candidate = with_cid(make_candidate(title=f"Paper {doi}", doi=doi))
        candidates[candidate.cid] = candidate
        entry = ranked_entry(candidate.cid, overall=3, verification=verification_payload())
        entries.append(entry)
        packets.append(
            EvidencePacket(
                **(candidate.model_dump() | entry.model_dump()),
                rank=rank,
                selection_reason=reason,
            )
        )
    for doi in ranked_only:
        candidate = with_cid(make_candidate(title=f"Paper {doi}", doi=doi))
        candidates[candidate.cid] = candidate
        entries.append(ranked_entry(candidate.cid, overall=1, verification=verification_payload()))

    return evalrun.RunFiles(
        evidence=Evidence(run=info, packets=packets),
        ranked=Ranked(entries),
        candidates=candidates,
    )


# --- recall -----------------------------------------------------------------


def test_recall_counts_hits_at_ten_and_twenty_five(tmp_path):
    topic = GoldenTopic.model_validate(topic_payload())
    files = build_run(tmp_path, emitted=["10.1000/a"], ranked_only=["10.1000/b"])

    result = evalrun.score(topic, tmp_path, files)

    assert result.expected == 2
    assert result.found_at_10 == 1
    assert result.found_at_25 == 2
    assert result.recall_10 == 0.5
    assert result.recall_25 == 1.0
    assert result.misses == []


def test_a_paper_absent_from_the_pool_is_a_miss_carrying_its_why(tmp_path):
    topic = GoldenTopic.model_validate(topic_payload())
    files = build_run(tmp_path, emitted=["10.1000/a"])

    result = evalrun.score(topic, tmp_path, files)

    assert result.found_at_25 == 1
    assert [miss.doi for miss in result.misses] == ["10.1000/b"]
    assert result.misses[0].why == "the contradicting one"


def test_matching_survives_doi_formatting(tmp_path):
    topic = GoldenTopic.model_validate(
        topic_payload(expected=[{"doi": "https://doi.org/10.1000/A", "why": "cased and prefixed"}])
    )
    files = build_run(tmp_path, emitted=["10.1000/a"])
    assert evalrun.score(topic, tmp_path, files).recall_10 == 1.0


def test_an_arxiv_paper_matches_under_either_identifier(tmp_path):
    """The golden file carries the 10.48550 DOI; the run may only have the bare arXiv id."""
    topic = GoldenTopic.model_validate(
        topic_payload(
            expected=[
                {"doi": "10.48550/arXiv.2501.10120", "arxiv": "2501.10120", "why": "PaSa"},
            ]
        )
    )
    info = build_run(tmp_path, emitted=[]).evidence.run
    candidate = with_cid(make_candidate(title="PaSa", doi=None, arxiv="2501.10120v2"))
    entry = ranked_entry(candidate.cid, overall=3, verification=verification_payload())
    files = evalrun.RunFiles(
        evidence=Evidence(
            run=info,
            packets=[
                EvidencePacket(
                    **(candidate.model_dump() | entry.model_dump()),
                    rank=1,
                    selection_reason="score",
                )
            ],
        ),
        ranked=Ranked([entry]),
        candidates={candidate.cid: candidate},
    )

    assert evalrun.score(topic, tmp_path, files).recall_10 == 1.0


def test_an_alias_matches_a_paper_found_under_another_identifier(tmp_path):
    """The real case: the run carried the meta-analysis under an SSRN DOI for a different work."""
    topic = GoldenTopic.model_validate(
        topic_payload(
            expected=[
                {
                    "doi": "10.1017/bpp.2018.43",
                    "aliases": ["10.2139/ssrn.2727301"],
                    "why": "the run carried the SSRN variant",
                }
            ]
        )
    )
    files = build_run(tmp_path, emitted=["10.2139/ssrn.2727301"])
    assert evalrun.score(topic, tmp_path, files).recall_10 == 1.0


def test_an_unrelated_doi_is_not_rescued_by_the_alias_list(tmp_path):
    topic = GoldenTopic.model_validate(
        topic_payload(
            expected=[
                {"doi": "10.1017/bpp.2018.43", "aliases": ["10.2139/ssrn.2727301"], "why": "x"}
            ]
        )
    )
    files = build_run(tmp_path, emitted=["10.9999/unrelated"])
    assert evalrun.score(topic, tmp_path, files).recall_10 == 0.0


DEFAULTS_META_TITLE = (
    "When and why defaults influence decisions: a meta-analysis of default effects"
)


def test_a_near_identical_title_matches_when_no_identifier_is_shared(tmp_path):
    """Upstream can attach the wrong DOI; scoring that a miss would measure the registrar."""
    topic = GoldenTopic.model_validate(
        topic_payload(
            expected=[
                {
                    "doi": "10.1017/bpp.2018.43",
                    "title": DEFAULTS_META_TITLE,
                    "why": "found under a wrong DOI, right title",
                }
            ]
        )
    )
    candidate = with_cid(
        make_candidate(
            title=DEFAULTS_META_TITLE + ".",
            doi="10.9999/some-mislinked-record",
        )
    )
    entry = ranked_entry(candidate.cid, overall=3, verification=verification_payload())
    files = evalrun.RunFiles(
        evidence=Evidence(
            run=build_run(tmp_path, emitted=[]).evidence.run,
            packets=[
                EvidencePacket(
                    **(candidate.model_dump() | entry.model_dump()),
                    rank=1,
                    selection_reason="score",
                )
            ],
        ),
        ranked=Ranked([entry]),
        candidates={candidate.cid: candidate},
    )

    assert evalrun.score(topic, tmp_path, files).recall_10 == 1.0


def test_a_merely_similar_title_does_not_match(tmp_path):
    """95 is deliberately strict: a false positive here inflates the one number eval reports."""
    topic = GoldenTopic.model_validate(
        topic_payload(
            expected=[
                {
                    "doi": "10.1000/x",
                    "title": "Defaults and retirement saving in Denmark",
                    "why": "x",
                }
            ]
        )
    )
    files = build_run(tmp_path, emitted=["10.9999/other"])
    files.evidence.packets[0].title = "Defaults and retirement saving in Sweden and Norway"
    assert evalrun.score(topic, tmp_path, files).recall_10 == 0.0


def test_recall_at_25_uses_the_selection_ordering(tmp_path):
    """The 26th paper by §10.4 order is out of scope even if it sits first in the file."""
    info = build_run(tmp_path, emitted=[]).evidence.run
    candidates, entries = {}, []
    wanted = with_cid(make_candidate(title="Wanted", doi="10.1000/wanted"))
    candidates[wanted.cid] = wanted
    entries.append(ranked_entry(wanted.cid, overall=0, verification=verification_payload()))
    for n in range(30):
        other = with_cid(make_candidate(title=f"Other {n}", doi=f"10.1000/o{n}"))
        candidates[other.cid] = other
        entries.append(ranked_entry(other.cid, overall=3, verification=verification_payload()))

    files = evalrun.RunFiles(
        evidence=Evidence(run=info, packets=[]), ranked=Ranked(entries), candidates=candidates
    )
    topic = GoldenTopic.model_validate(
        topic_payload(expected=[{"doi": "10.1000/wanted", "why": "ranked last by merit"}])
    )

    assert evalrun.score(topic, tmp_path, files).found_at_25 == 0


# --- judge merging ----------------------------------------------------------


def test_judge_precision_is_the_share_scoring_two_or_more(tmp_path):
    topic = GoldenTopic.model_validate(topic_payload())
    result = evalrun.score(topic, tmp_path, build_run(tmp_path, emitted=["10.1000/a"]))
    judge = JudgeFile.model_validate(
        {
            "judge_model": "claude-fable-5",
            "scores": [
                {"rank": 1, "score": 3, "reason": "central"},
                {"rank": 2, "score": 2, "reason": "relevant"},
                {"rank": 3, "score": 1, "reason": "tangential"},
                {"rank": 4, "score": 0, "reason": "off-topic"},
            ],
        }
    )

    merged = evalrun.merge_judge(result, judge)

    assert merged.judged.precision_ge2 == 0.5
    assert [item.rank for item in merged.judged.per_rank] == [1, 2, 3, 4]
    assert merged.judged.per_rank[0].reason == "central"


def test_a_partly_scored_top_ten_uses_the_judged_count_as_the_denominator(tmp_path):
    """Inventing zeroes for unscored packets would read as quality rather than missing judgment."""
    topic = GoldenTopic.model_validate(topic_payload())
    result = evalrun.score(topic, tmp_path, build_run(tmp_path, emitted=["10.1000/a"]))
    judge = JudgeFile.model_validate({"scores": [{"rank": 1, "score": 3}, {"rank": 2, "score": 3}]})

    assert evalrun.merge_judge(result, judge).judged.precision_ge2 == 1.0


def test_an_empty_judge_file_yields_no_precision(tmp_path):
    topic = GoldenTopic.model_validate(topic_payload())
    result = evalrun.score(topic, tmp_path, build_run(tmp_path, emitted=["10.1000/a"]))
    merged = evalrun.merge_judge(result, JudgeFile(scores=[]))
    assert merged.judged.precision_ge2 is None


def test_foundational_packets_are_held_out_of_the_in_window_precision(tmp_path):
    """The acceptance number must not be dragged down by slots emit reserved for classics."""
    topic = GoldenTopic.model_validate(topic_payload())
    files = build_run(tmp_path, emitted=["10.1000/a", "10.1000/b"], foundational=["10.1000/old"])
    result = evalrun.score(topic, tmp_path, files)
    judge = JudgeFile.model_validate(
        {
            "scores": [
                {"rank": 1, "score": 3, "reason": "central"},
                {"rank": 2, "score": 2, "reason": "relevant"},
                {"rank": 3, "score": 0, "reason": "a classic, judged on the wrong scale"},
            ]
        }
    )

    merged = evalrun.merge_judge(result, judge, files.evidence)

    assert merged.judged.precision_ge2 == round(2 / 3, 3)  # raw share still ships
    assert merged.judged.precision_ge2_in_window == 1.0
    assert [item.rank for item in merged.judged.foundational] == [3]
    assert [item.rank for item in merged.judged.per_rank] == [1, 2, 3]


def test_the_split_matches_on_cid_not_on_rank_order(tmp_path):
    """A judge may emit its entries in any order; one acceptance run does exactly that."""
    topic = GoldenTopic.model_validate(topic_payload())
    files = build_run(tmp_path, emitted=["10.1000/a"], foundational=["10.1000/old"])
    result = evalrun.score(topic, tmp_path, files)
    by_reason = {packet.selection_reason.value: packet for packet in files.evidence.packets}
    classic, current = by_reason["foundational"], by_reason["score"]

    # Entries out of rank order, and each rank paired with the *other* packet's cid would be a
    # different answer — so this only passes if the cid decides.
    judge = JudgeFile.model_validate(
        {
            "scores": [
                {"rank": 2, "cid": classic.cid, "score": 3, "reason": "canonical background"},
                {"rank": 1, "cid": current.cid, "score": 1, "reason": "tangential"},
            ]
        }
    )

    merged = evalrun.merge_judge(result, judge, files.evidence)

    assert [item.cid for item in merged.judged.foundational] == [classic.cid]
    assert merged.judged.precision_ge2_in_window == 0.0
    assert merged.judged.precision_ge2 == 0.5


def test_without_evidence_the_in_window_share_is_null_rather_than_guessed(tmp_path):
    """Same refusal as the partial-judge denominator: do not invent a number you cannot compute."""
    topic = GoldenTopic.model_validate(topic_payload())
    result = evalrun.score(topic, tmp_path, build_run(tmp_path, emitted=["10.1000/a"]))
    judge = JudgeFile.model_validate({"scores": [{"rank": 1, "score": 3}]})

    merged = evalrun.merge_judge(result, judge)

    assert merged.judged.precision_ge2 == 1.0
    assert merged.judged.precision_ge2_in_window is None
    assert merged.judged.foundational == []


# --- loading ----------------------------------------------------------------


def test_a_malformed_golden_file_exits_two_with_the_error_list(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.safe_dump({"topic": "bad", "brief": "b", "expected": []}))
    with pytest.raises(StageInputError) as raised:
        evalrun.load_topic(path)
    assert "GoldenTopic" in raised.value.message
    assert raised.value.lines


def test_invalid_yaml_is_reported_as_such(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("topic: [unclosed\n")
    with pytest.raises(StageInputError, match="not valid YAML"):
        evalrun.load_topic(path)


def test_an_unknown_topic_lists_what_is_available(tmp_path):
    (tmp_path / "known.yaml").write_text("topic: known\n")
    with pytest.raises(StageInputError) as raised:
        evalrun.find_topic("missing", tmp_path)
    assert "known" in " ".join(raised.value.lines)


def test_the_shipped_topics_load(tmp_path):
    topic = evalrun.load_topic(evalrun.find_topic("defaults-savings", GOLDEN_DIR))
    assert topic.status == "ratified-with-caveat"
    assert all(paper.why.strip() for paper in topic.expected)
    # The maintainer added two entries chosen without reference to any run; the split must
    # stay visible.
    independent = [paper for paper in topic.expected if paper.found_in_s3e2e is False]
    assert len(independent) >= 4


# --- fix (b): arXiv DOIs ----------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("10.48550/arXiv.2310.00340", "2310.00340"),
        ("10.48550/arxiv.2310.00340", "2310.00340"),
        ("https://doi.org/10.48550/arXiv.2501.10120v2", "2501.10120"),
        ("10.1257/aer.20210881", None),
        (None, None),
    ],
)
def test_arxiv_id_from_doi(raw, expected):
    assert arxiv_id_from_doi(raw) == expected
    assert is_arxiv_doi(raw) is (expected is not None)


# --- fix (a): timestamps ----------------------------------------------------


def test_stamp_records_one_stage_without_touching_others():
    started = datetime(2026, 8, 19, 10, 0, tzinfo=UTC)
    finished = datetime(2026, 8, 19, 10, 5, tzinfo=UTC)
    existing = {"init.started_at": "2026-08-19T09:00:00+00:00"}

    stamped = run.stamp(existing, "retrieve", started, finished)

    assert stamped["init.started_at"] == "2026-08-19T09:00:00+00:00"
    assert stamped["retrieve.started_at"] == "2026-08-19T10:00:00+00:00"
    assert stamped["retrieve.finished_at"] == "2026-08-19T10:05:00+00:00"


def test_re_running_a_stage_overwrites_only_its_own_pair():
    first = run.stamp(
        None, "verify", datetime(2026, 8, 19, 1, tzinfo=UTC), datetime(2026, 8, 19, 2, tzinfo=UTC)
    )
    first["emit.finished_at"] = "2026-08-19T03:00:00+00:00"

    second = run.stamp(
        first, "verify", datetime(2026, 8, 19, 5, tzinfo=UTC), datetime(2026, 8, 19, 6, tzinfo=UTC)
    )

    assert second["verify.started_at"] == "2026-08-19T05:00:00+00:00"
    assert second["emit.finished_at"] == "2026-08-19T03:00:00+00:00"


def test_wall_clock_runs_from_init_to_the_last_finish():
    timestamps = {
        "init.started_at": "2026-08-19T10:00:00+00:00",
        "init.finished_at": "2026-08-19T10:00:01+00:00",
        "retrieve.finished_at": "2026-08-19T10:00:30+00:00",
        "emit.finished_at": "2026-08-19T10:02:00+00:00",
    }
    assert run.wall_clock_seconds(timestamps) == 120.0


@pytest.mark.parametrize(
    "timestamps",
    [
        None,
        {},
        {"retrieve.finished_at": "2026-08-19T10:00:00+00:00"},
        {"init.started_at": "nonsense"},
    ],
)
def test_wall_clock_is_none_when_it_cannot_be_known(timestamps):
    assert run.wall_clock_seconds(timestamps) is None


def test_init_stamps_the_manifest(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(run, "today", lambda: date(2026, 8, 19))
    info = run.create_run("A question about defaults", slug="t")

    manifest = run.read_manifest(Path(info.run_dir))

    assert "init.started_at" in manifest.timestamps
    assert "init.finished_at" in manifest.timestamps
    assert manifest.counts.wall_clock_s is None  # only `emit` can know the total


# --- recall at the candidate pool (S10e) ------------------------------------


def _topic_with(**paper: object) -> GoldenTopic:
    return GoldenTopic.model_validate(
        {
            "topic": "t",
            "status": "ratified",
            "brief": "b",
            "expected": [{"why": "because", **paper}],
        }
    )


def test_recall_at_candidates_matches_on_the_published_alias():
    """The topic-2 failure exactly: the run holds the Nature version, the golden pins the preprint.

    Without the alias this reads as a miss even though the paper was emitted at rank 1, which
    measures the DOI registrar rather than the retrieval.
    """
    topic = _topic_with(
        doi="10.48550/arXiv.2411.14199",
        arxiv="2411.14199",
        aliases=["10.1038/s41586-025-10072-4"],
    )
    candidate = with_cid(make_candidate(doi="10.1038/s41586-025-10072-4"))
    pool = {candidate.cid: candidate}

    recall = evalrun.score_candidates(topic, pool, {candidate.cid: 3})

    assert recall.found == 1
    assert recall.recall == 1.0
    hit = recall.papers[0]
    assert hit.present and hit.matched_by == "alias"
    assert hit.cid == candidate.cid
    assert hit.screen_score == 3
    assert hit.origins  # the origin string is the point: it names the stage and query


def test_recall_at_candidates_reports_the_matching_identifier():
    """`doi`, `arxiv`, `alias` and `title` are different findings, so they are not collapsed."""
    by_doi = with_cid(make_candidate(doi="10.48550/arXiv.2407.18940", title="LitSearch"))
    topic = _topic_with(doi="10.48550/arXiv.2407.18940", arxiv="2407.18940")
    assert evalrun.score_candidates(topic, {by_doi.cid: by_doi}, None).papers[0].matched_by == "doi"

    by_title = with_cid(make_candidate(doi="10.9999/unrelated", title="LitSearch"))
    titled = _topic_with(doi="10.48550/arXiv.2407.18940", title="LitSearch")
    hit = evalrun.score_candidates(titled, {by_title.cid: by_title}, None).papers[0]
    assert hit.matched_by == "title"


def test_recall_at_candidates_marks_an_absent_paper_without_inventing_a_score():
    topic = _topic_with(doi="10.48550/arXiv.2501.10120", arxiv="2501.10120")
    other = with_cid(make_candidate(doi="10.1234/other"))

    recall = evalrun.score_candidates(topic, {other.cid: other}, {other.cid: 3})

    assert recall.found == 0
    miss = recall.papers[0]
    assert not miss.present
    assert miss.cid is None and miss.matched_by is None and miss.screen_score is None


def test_recall_at_candidates_says_when_screening_has_not_happened(tmp_path):
    """The stage must work on a run that has only retrieved — that is its whole purpose."""
    candidate = with_cid(make_candidate(doi="10.48550/arXiv.2411.14199"))
    info = RunInfo(
        run_dir=str(tmp_path),
        slug="s",
        date="2026-08-19",
        brief_path="b.md",
        defaults=Defaults(),
    )
    run.write_model(
        tmp_path / "candidates.json",
        CandidatesFile(run=info, candidates=[candidate]),
    )

    pool, scores = evalrun.load_candidate_pool(tmp_path)
    recall = evalrun.score_candidates(
        _topic_with(doi="10.48550/arXiv.2411.14199", arxiv="2411.14199"), pool, scores
    )

    assert scores is None
    assert recall.screened is False
    assert recall.found == 1
    assert recall.papers[0].screen_score is None


# --- profile-keyed bookkeeping (v0.2.1) -------------------------------------


def test_results_are_keyed_by_profile():
    """The same topic scores differently at each cost setting, so the files cannot collide."""
    base = s.EvalResult(
        topic="defaults-savings",
        run_dir="research/scans/x",
        expected=10,
        found_at_10=5,
        found_at_25=8,
        recall_10=0.5,
        recall_25=0.8,
    )
    plain = evalrun.result_path(base, "2026-08-19-candidates", root=Path("eval/results"))
    deep = evalrun.result_path(
        base.model_copy(update={"profile": s.Profile.deep}),
        "2026-08-19-candidates",
        root=Path("eval/results"),
    )
    assert plain.name == "2026-08-19-candidates-defaults-savings.json"
    assert deep.name == "2026-08-19-candidates-defaults-savings-deep.json"


def test_recall_per_100_screened_prices_the_recall(tmp_path):
    """8/10 out of a 400-paper pool is a different buy from 8/10 out of 1,200."""
    base = s.EvalResult(
        topic="t",
        run_dir=str(tmp_path),
        expected=10,
        found_at_10=0,
        found_at_25=8,
        recall_10=0.0,
        recall_25=0.8,
    )
    priced = evalrun.with_cost(base, tmp_path, pool_size=400, found=8, expected=10)
    assert priced.pool_size == 400
    assert priced.recall_per_100_screened == 0.2  # 0.8 recall / 4 hundreds screened
    assert priced.profile is None  # no manifest in tmp_path, and that is not fatal
