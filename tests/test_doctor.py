"""Doctor readiness gate (spec §8.6): statuses, exit codes, and 'never report an unrun check'."""

from __future__ import annotations

import json

import pytest

from research_scan import config, doctor, http

OK_PAYLOADS = {
    "api.openalex.org/works?search": {
        "meta": {"count": 1, "cost_usd": 0.001},
        "results": [
            {
                "id": "https://openalex.org/W1",
                "doi": "https://doi.org/10.1000/x",
                "title": "A work",
                "publication_date": "2025-01-01",
                "is_retracted": False,
            }
        ],
    },
    "api.openalex.org/works?filter": {
        "meta": {"count": 1, "cost_usd": 0.0001},
        "results": [
            {
                "id": "https://openalex.org/W2",
                "doi": f"https://doi.org/{doctor.PSYARXIV_PROBE_DOI}",
                "title": "Redefine statistical significance",
                "type": "preprint",
            }
        ],
    },
    "paper/search": {"total": 1, "data": [{"title": "A paper", "year": 2024}]},
    "references": {"data": [{"citedPaper": {"title": "A reference", "year": 2019}}]},
    "api.crossref.org": {"status": "ok", "message": {"DOI": doctor.CROSSREF_PROBE_DOI}},
    "esearch.fcgi": {"esearchresult": {"count": "7", "idlist": ["42610908"]}},
}

ARXIV_FEED = b"<?xml version='1.0'?><feed><entry><title>An electron</title></entry></feed>"


class FakeClient:
    """Dispatches on URL fragments; `overrides` replaces a fragment's outcome."""

    def __init__(self, overrides: dict[str, object] | None = None) -> None:
        self.overrides = overrides or {}
        self.calls: list[tuple[str, dict]] = []

    def get(self, url, *, params=None, headers=None, cache=None):
        assert cache is False, "doctor must bypass the cache"
        self.calls.append((url, dict(params or {})))
        key = self._match(url, params or {})
        outcome = self.overrides.get(key)
        if isinstance(outcome, Exception):
            raise outcome
        if isinstance(outcome, int):
            return http.Response(url=url, status_code=outcome, headers={}, content=b"{}")
        if "export.arxiv.org" in url:
            return http.Response(url=url, status_code=200, headers={}, content=ARXIV_FEED)
        body = json.dumps(OK_PAYLOADS[key]).encode()
        return http.Response(url=url, status_code=200, headers={}, content=body)

    @staticmethod
    def _match(url: str, params: dict) -> str:
        if "api.openalex.org" in url:
            return (
                "api.openalex.org/works?filter"
                if "filter" in params
                else "api.openalex.org/works?search"
            )
        for fragment in (
            "paper/search",
            "references",
            "api.crossref.org",
            "esearch.fcgi",
            "export.arxiv.org",
        ):
            if fragment in url:
                return fragment
        raise AssertionError(f"unexpected doctor call: {url}")


@pytest.fixture
def settings(tmp_path, monkeypatch) -> config.Settings:
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


def statuses(report: doctor.Report) -> dict[str, str]:
    return {check.name: check.status for check in report.checks}


def test_everything_healthy_exits_zero(settings):
    report = doctor.run_checks(settings, FakeClient())

    assert report.exit_code == 0
    assert report.ok is True
    assert all(check.status in {"OK", "WARN"} for check in report.checks)
    assert statuses(report)["openalex search"] == "OK"
    assert statuses(report)["openalex psyarxiv-doi"] == "OK"


def test_missing_openalex_key_fails_with_exit_three(settings, monkeypatch):
    monkeypatch.delenv("OPENALEX_API_KEY", raising=False)
    bare = config.load()

    report = doctor.run_checks(bare, FakeClient())

    assert report.exit_code == 3
    assert statuses(report)["OPENALEX_API_KEY"] == "FAIL"
    # the live search is not attempted, and is not reported as OK either
    assert statuses(report)["openalex search"] == "SKIP"


def test_openalex_http_failure_is_mandatory_fail(settings):
    report = doctor.run_checks(settings, FakeClient({"api.openalex.org/works?search": 500}))

    assert report.exit_code == 3
    assert statuses(report)["openalex search"] == "FAIL"


def test_missing_s2_key_only_warns(settings, monkeypatch):
    monkeypatch.delenv("S2_API_KEY", raising=False)
    report = doctor.run_checks(config.load(), FakeClient())

    assert report.exit_code == 0
    assert statuses(report)["S2_API_KEY"] == "WARN"


def test_s2_rate_limited_warns_but_exits_zero(settings):
    report = doctor.run_checks(settings, FakeClient({"paper/search": 429, "references": 429}))

    assert report.exit_code == 0
    assert statuses(report)["s2 search"] == "WARN"
    assert "429" in dict((c.name, c.detail) for c in report.checks)["s2 search"]


def test_s2_unreachable_with_a_key_fails(settings):
    unreachable = http.HttpError("connect error", url="https://api.semanticscholar.org", attempts=3)
    report = doctor.run_checks(
        settings, FakeClient({"paper/search": unreachable, "references": unreachable})
    )

    assert report.exit_code == 3
    assert statuses(report)["s2 search"] == "FAIL"


def test_s2_unreachable_without_a_key_only_warns(settings, monkeypatch):
    monkeypatch.delenv("S2_API_KEY", raising=False)
    unreachable = http.HttpError("connect error", url="https://api.semanticscholar.org", attempts=3)
    report = doctor.run_checks(
        config.load(), FakeClient({"paper/search": unreachable, "references": unreachable})
    )

    assert report.exit_code == 0
    assert statuses(report)["s2 search"] == "WARN"


@pytest.mark.parametrize(
    ("fragment", "check"),
    [
        ("api.crossref.org", "crossref lookup"),
        ("export.arxiv.org", "arxiv query"),
        ("esearch.fcgi", "pubmed esearch"),
    ],
)
def test_degradable_sources_only_warn(settings, fragment, check):
    report = doctor.run_checks(settings, FakeClient({fragment: 503}))

    assert report.exit_code == 0
    assert statuses(report)[check] == "WARN"


def test_psyarxiv_coverage_probe_warns_when_the_doi_is_absent(settings):
    client = FakeClient({"api.openalex.org/works?filter": 404})
    report = doctor.run_checks(settings, client)

    assert report.exit_code == 0
    assert statuses(report)["openalex psyarxiv-doi"] == "WARN"


def test_sources_flag_narrows_and_omits_unrun_checks(settings):
    client = FakeClient()
    report = doctor.run_checks(settings, client, sources=["openalex"])

    names = statuses(report)
    assert "openalex search" in names
    assert "s2 search" not in names
    assert "crossref lookup" not in names
    assert all("semanticscholar" not in url for url, _ in client.calls)


def test_unwritable_cache_path_fails(settings, monkeypatch, tmp_path):
    blocked = tmp_path / "blocked"
    blocked.write_text("not a directory", encoding="utf-8")
    monkeypatch.setattr(doctor, "_writable", lambda path: (False, "Not a directory"))

    report = doctor.run_checks(settings, FakeClient())

    assert report.exit_code == 3
    assert statuses(report)["cache path"] == "FAIL"


def test_report_json_masks_every_key(settings):
    report = doctor.run_checks(settings, FakeClient())
    blob = json.dumps(report.to_dict())

    assert "fake-openalex-key-abcd" not in blob
    assert "fake-s2-key-wxyz" not in blob
    assert "****abcd" in blob


def test_report_table_renders_every_check(settings):
    report = doctor.run_checks(settings, FakeClient())
    table = doctor.render_table(report)

    for check in report.checks:
        assert check.name in table
    assert "research-scan doctor" in table


# --- presentation: compact, verbose and --json all describe the same report ----


def test_the_json_superset_keeps_every_key_the_skill_already_parses(settings):
    """The skill's preflight reads `checks` and reports failures verbatim. Add, never remove."""
    payload = doctor.run_checks(settings, FakeClient()).to_dict()

    for key in ("exit_code", "python", "sources", "paths", "keys", "checks"):
        assert key in payload, f"{key} is a published key and may not be dropped"
    for key in ("version", "ready", "providers", "config", "run_store"):
        assert key in payload
    assert payload["config"] == "ok"
    assert payload["run_store"] == "ok"
    assert set(payload["providers"]) == set(doctor.ALL_SOURCES)
    assert payload["providers"]["openalex"] == "ok"


def test_the_legacy_duplicate_keys_are_gone(settings):
    """`ok` and `tool_version` duplicated `ready` and `version` and were removed at 0.5.2.

    Removing a published key is the one thing to_dict's contract forbids, so it happens once,
    at a named version, and this test is what stops it happening again by accident.
    """
    payload = doctor.run_checks(settings, FakeClient()).to_dict()

    assert "ok" not in payload
    assert "tool_version" not in payload
    assert payload["ready"] is True
    assert payload["version"] == doctor.__version__


def test_a_provider_rollup_takes_the_worst_of_its_checks(settings):
    """`s2 references` failing must not be hidden by `s2 search` passing."""
    unreachable = http.HttpError("connect error", url="https://api.semanticscholar.org", attempts=3)
    client = FakeClient({"references": unreachable})

    report = doctor.run_checks(settings, client)

    assert statuses(report)["s2 search"] == "OK"
    assert report.providers()["s2"] == "FAIL"
    assert report.to_dict()["providers"]["s2"] == "fail"


def test_a_provider_that_was_never_checked_is_reported_as_skip_not_ok(settings, monkeypatch):
    """Module rule 1: never report a check you did not execute — not even as a rollup."""
    monkeypatch.delenv("OPENALEX_API_KEY")
    report = doctor.run_checks(config.load(), FakeClient())

    assert statuses(report)["openalex search"] == "SKIP"
    assert report.to_dict()["providers"]["openalex"] == "skip"


def test_an_unselected_source_gets_no_row_at_all(settings):
    report = doctor.run_checks(settings, FakeClient(), ["openalex"])

    assert set(report.to_dict()["providers"]) == {"openalex"}


def test_the_compact_summary_says_ready_and_names_every_selected_provider(settings):
    summary = doctor.render_compact(doctor.run_checks(settings, FakeClient()))

    for label in doctor.PROVIDER_LABELS.values():
        assert label in summary
    assert summary.startswith("Research Scan ")
    assert "writable run store" in summary
    # A missing optional key must not demote the headline — it is a warning, not a fault.
    assert "✓ configuration" in summary
    assert summary.splitlines()[-1].startswith("Ready")


def test_a_failing_compact_summary_carries_one_actionable_sentence(settings, monkeypatch):
    monkeypatch.delenv("OPENALEX_API_KEY")
    report = doctor.run_checks(config.load(), FakeClient())

    summary = doctor.render_compact(report)

    assert "✗ configuration" in summary
    assert "research-scan configure" in summary, "a failure must say what to do about it"
    assert "Not ready" in summary
    assert "--verbose" in summary


def test_presentation_never_moves_the_exit_code(settings, monkeypatch):
    """The whole contract of this change: three renderings, one set of checks, one exit code."""
    monkeypatch.delenv("OPENALEX_API_KEY")
    report = doctor.run_checks(config.load(), FakeClient())

    assert report.exit_code == 3
    assert report.to_dict()["exit_code"] == 3
    assert report.to_dict()["ready"] is False
    # Rendering is pure: it reads the report and returns a string, and cannot change either.
    doctor.render_compact(report)
    doctor.render_table(report)
    assert report.exit_code == 3


@pytest.mark.live
def test_doctor_against_the_real_apis():
    """`pytest -m live` — the fresh-machine gate, needs real keys."""
    settings = config.load()
    with http.HttpClient(settings, cache=False, max_retries=1) as client:
        report = doctor.run_checks(settings, client)
    assert report.exit_code == 0, doctor.render_table(report)


# --- routed but not built ----------------------------------------------------
#
# `_probe_pubmed` asks whether NCBI's E-utilities endpoint answers. Whether this package can
# retrieve from PubMed is a different question, and `retrieve.IMPLEMENTED_SOURCES` has always
# been the one that answers it. Until 0.6.1 doctor kept its own source list and could only say
# "ok", so a reachable endpoint read as a working source. The fix is strictly additive: every
# key, value and type below the new one is what 0.6.0 emitted.


def test_pubmed_is_reported_not_built_even_when_its_endpoint_answers(settings):
    report = doctor.run_checks(settings, FakeClient())

    assert statuses(report)["pubmed esearch"] == "OK", "the endpoint really does answer"
    assert report.sources_not_built() == ["pubmed"], "and the source really is not built"


def test_the_not_built_list_does_not_depend_on_reachability(settings):
    """Two different questions. An unreachable PubMed is still a PubMed that is not built."""
    reachable = doctor.run_checks(settings, FakeClient())
    unreachable = doctor.run_checks(settings, FakeClient({"esearch.fcgi": 503}))

    assert unreachable.sources_not_built() == reachable.sources_not_built() == ["pubmed"]
    assert statuses(unreachable)["pubmed esearch"] == "WARN", "the probe result still moves"


def test_crossref_never_appears_as_not_built(settings):
    """Crossref verifies DOIs and is never a retrieval source, so the question does not apply."""
    report = doctor.run_checks(settings, FakeClient())

    assert "crossref" not in report.sources_not_built()
    assert report.to_dict()["providers"]["crossref"] == "ok"


def test_the_not_built_list_is_sorted_deduplicated_and_scoped_to_the_selection(settings):
    full = doctor.run_checks(settings, FakeClient()).sources_not_built()
    assert full == sorted(set(full))

    without = doctor.run_checks(settings, FakeClient(), sources=["openalex"]).sources_not_built()
    assert without == [], "a source that was not selected is not reported on"


@pytest.mark.parametrize("overrides", [None, {"esearch.fcgi": 503}], ids=["reachable", "down"])
def test_the_legacy_json_contract_is_untouched_by_the_new_field(settings, overrides):
    """0.6.0's keys, values and types, whatever the PubMed probe did."""
    report = doctor.run_checks(settings, FakeClient(overrides))
    payload = report.to_dict()

    assert set(payload["providers"]) == set(doctor.ALL_SOURCES)
    assert all(isinstance(value, str) for value in payload["providers"].values())
    assert payload["providers"]["pubmed"] in {"ok", "warn"}, "the legacy value still moves"
    assert payload["ready"] is True
    assert payload["exit_code"] == 0
    assert report.ok is True
    assert payload["sources_not_built"] == ["pubmed"]


def test_the_new_field_is_json_serialisable_and_a_list_of_strings(settings):
    payload = json.loads(json.dumps(doctor.run_checks(settings, FakeClient()).to_dict()))

    assert isinstance(payload["sources_not_built"], list)
    assert all(isinstance(name, str) for name in payload["sources_not_built"])


def test_the_compact_summary_marks_pubmed_rather_than_ticking_it(settings):
    rendered = doctor.render_compact(doctor.run_checks(settings, FakeClient()))

    assert "○ PubMed" in rendered
    assert "✓ PubMed" not in rendered
    assert "PubMed: endpoint reachable; source routed for biomed but not built" in rendered
    assert "✓ OpenAlex" in rendered, "a built source still ticks"


def test_the_compact_note_stays_truthful_when_the_endpoint_is_down(settings):
    rendered = doctor.render_compact(doctor.run_checks(settings, FakeClient({"esearch.fcgi": 503})))

    assert "PubMed: endpoint check did not pass; source routed for biomed but not built" in rendered


def test_the_verbose_table_says_it_too(settings):
    rendered = doctor.render_table(doctor.run_checks(settings, FakeClient()))

    assert "pubmed esearch" in rendered, "the probe row is unchanged"
    assert "source routed for biomed but not built" in rendered
