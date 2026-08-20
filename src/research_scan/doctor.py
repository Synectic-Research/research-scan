# SPDX-License-Identifier: Apache-2.0
"""Readiness gate (spec §8.6): invoke every source, don't list them.

Two rules shape this module:

* **Never report a check you did not execute.** A source excluded by `--sources` produces no
  row at all; a live call skipped because its key is missing is reported as `SKIP`, not `OK`.
* **The cache is bypassed.** A green doctor has to mean the network is green right now.

`FAIL` means exit 3. `WARN` means the scan will still run, degraded — no key for Semantic
Scholar, Crossref unreachable (verification falls back to OpenAlex), a routed source down.
"""

from __future__ import annotations

import platform
import sys
import time
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Literal, Protocol

from research_scan import __version__
from research_scan.config import Settings
from research_scan.http import HttpError, Response, is_retryable

Status = Literal["OK", "WARN", "FAIL", "SKIP"]

ALL_SOURCES: tuple[str, ...] = ("openalex", "s2", "crossref", "arxiv", "pubmed")
MIN_PYTHON = (3, 11)

#: Which live checks roll up into one line per provider. Presentation only — the checks
#: themselves, their statuses and the exit code are untouched by anything in this map.
PROVIDER_CHECKS: dict[str, tuple[str, ...]] = {
    "openalex": ("openalex search", "openalex psyarxiv-doi"),
    "s2": ("s2 search", "s2 references"),
    "crossref": ("crossref lookup",),
    "arxiv": ("arxiv query",),
    "pubmed": ("pubmed esearch",),
}
PROVIDER_LABELS: dict[str, str] = {
    "openalex": "OpenAlex",
    "s2": "Semantic Scholar",
    "crossref": "Crossref",
    "arxiv": "arXiv",
    "pubmed": "PubMed",
}

#: Local checks, rolled up the same way.
CONFIG_CHECKS: tuple[str, ...] = ("python", "config path")
RUN_STORE_CHECKS: tuple[str, ...] = ("cache path",)

#: Worst-first, so a rollup can take the max. `SKIP` outranks `OK`: a check that never ran
#: must never read as a passing one (module rule 1).
_SEVERITY: dict[Status, int] = {"OK": 0, "SKIP": 1, "WARN": 2, "FAIL": 3}
_SERIALISED: dict[Status, str] = {"OK": "ok", "SKIP": "skip", "WARN": "warn", "FAIL": "fail"}

# Fixed probes. Stable, famous, and — for the PsyArXiv one — the coverage question that decides
# whether OpenAlex's Crossref ingestion is enough for preprint-heavy behavioural topics (§16).
OPENALEX_WORKS_URL = "https://api.openalex.org/works"
OPENALEX_PROBE_QUERY = "large language models"
PSYARXIV_PROBE_DOI = "10.31234/osf.io/mky9j"  # Benjamin et al., "Redefine statistical significance"
S2_SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
S2_REFERENCES_URL = "https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}/references"
S2_PROBE_QUERY = "large language models"
CROSSREF_PROBE_DOI = "10.1038/s41586-021-03819-2"  # AlphaFold
CROSSREF_WORKS_URL = "https://api.crossref.org/works/{doi}"
ARXIV_QUERY_URL = "https://export.arxiv.org/api/query"
ARXIV_PROBE_QUERY = "electron"
PUBMED_ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_PROBE_TERM = "crispr"


class Client(Protocol):
    """The slice of :class:`research_scan.http.HttpClient` doctor needs."""

    def get(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = ...,
        headers: dict[str, str] | None = ...,
        cache: bool | None = ...,
    ) -> Response: ...


@dataclass
class Check:
    name: str
    status: Status
    detail: str
    mandatory: bool = False
    duration_ms: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "detail": self.detail,
            "mandatory": self.mandatory,
            "duration_ms": round(self.duration_ms, 1) if self.duration_ms is not None else None,
        }


@dataclass
class Report:
    checks: list[Check] = field(default_factory=list)
    paths: dict[str, str] = field(default_factory=dict)
    keys: dict[str, dict[str, Any]] = field(default_factory=dict)
    sources: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.exit_code == 0

    @property
    def exit_code(self) -> int:
        return 3 if any(check.status == "FAIL" for check in self.checks) else 0

    def by_name(self) -> dict[str, Check]:
        return {check.name: check for check in self.checks}

    def rollup(self, names: Sequence[str]) -> Status | None:
        """The worst status among the named checks, or None if none of them ran.

        None rather than "OK" is the point: `--sources openalex` runs no arXiv probe, and a
        source that was not checked gets no row at all.
        """
        found = [check.status for check in self.checks if check.name in names]
        return max(found, key=lambda status: _SEVERITY[status]) if found else None

    def providers(self) -> dict[str, Status]:
        """One status per source that was actually selected and checked."""
        rolled = {name: self.rollup(PROVIDER_CHECKS[name]) for name in self.sources}
        return {name: status for name, status in rolled.items() if status is not None}

    @property
    def config_status(self) -> Status | None:
        """Python, the config path, and any credential whose absence is disqualifying.

        Optional keys are deliberately excluded. A missing `NCBI_API_KEY` means PubMed runs at
        3 req/s instead of 10 — it does not mean the configuration is broken, and a headline
        that says otherwise trains people to ignore it. Those still land in the warning tally
        and in `--verbose`.
        """
        blocking = tuple(
            check.name for check in self.checks if check.name in self.keys and check.mandatory
        )
        return self.rollup(tuple(CONFIG_CHECKS) + blocking)

    @property
    def run_store_status(self) -> Status | None:
        return self.rollup(RUN_STORE_CHECKS)

    def to_dict(self) -> dict[str, Any]:
        """The machine interface. Keys here are stable — add, never remove or repurpose.

        The five summary keys are what CI and an agent should read. Everything below them is
        the original detailed shape, kept because the research-scan skill's preflight parses
        `checks` and reports failing ones verbatim.
        """
        return {
            "version": __version__,
            "ready": self.ok,
            "providers": {name: _SERIALISED[status] for name, status in self.providers().items()},
            "config": _SERIALISED[status] if (status := self.config_status) else None,
            "run_store": _SERIALISED[status] if (status := self.run_store_status) else None,
            "ok": self.ok,
            "exit_code": self.exit_code,
            "tool_version": __version__,
            "python": platform.python_version(),
            "sources": self.sources,
            "paths": self.paths,
            "keys": self.keys,
            "checks": [check.to_dict() for check in self.checks],
        }


def normalise_sources(sources: Iterable[str] | str | None) -> list[str]:
    if sources is None:
        return list(ALL_SOURCES)
    if isinstance(sources, str):
        sources = sources.split(",")
    selected = [item.strip().lower() for item in sources if item.strip()]
    unknown = [item for item in selected if item not in ALL_SOURCES]
    if unknown:
        raise ValueError(
            f"unknown source(s): {', '.join(unknown)}; known: {', '.join(ALL_SOURCES)}"
        )
    return [source for source in ALL_SOURCES if source in selected]


def run_checks(
    settings: Settings,
    client: Client,
    sources: Sequence[str] | str | None = None,
) -> Report:
    selected = normalise_sources(sources)
    report = Report(sources=selected)
    report.paths = {
        "config_env": str(settings.config_env),
        "local_env": str(settings.local_env),
        "cache_db": str(settings.cache_db),
    }

    report.checks.append(_check_python())
    report.checks.append(_check_path("config path", settings.config_dir))
    report.checks.append(_check_path("cache path", settings.cache_dir))
    report.checks.extend(_check_keys(settings, selected, report))

    if "openalex" in selected:
        report.checks.append(
            _timed("openalex search", True, _probe_openalex_search, client, settings)
        )
        report.checks.append(
            _timed("openalex psyarxiv-doi", False, _probe_openalex_psyarxiv, client, settings)
        )
    if "s2" in selected:
        report.checks.append(_timed("s2 search", True, _probe_s2_search, client, settings))
        report.checks.append(_timed("s2 references", True, _probe_s2_references, client, settings))
    if "crossref" in selected:
        report.checks.append(_timed("crossref lookup", False, _probe_crossref, client, settings))
    if "arxiv" in selected:
        report.checks.append(_timed("arxiv query", False, _probe_arxiv, client, settings))
    if "pubmed" in selected:
        report.checks.append(_timed("pubmed esearch", False, _probe_pubmed, client, settings))

    return report


# --- local checks -----------------------------------------------------------


def _check_python() -> Check:
    version = platform.python_version()
    if sys.version_info >= MIN_PYTHON:
        return Check("python", "OK", version)
    return Check("python", "FAIL", f"{version} < {'.'.join(map(str, MIN_PYTHON))}", mandatory=True)


def _writable(path: Path) -> tuple[bool, str]:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".research-scan-write-probe"
        probe.write_text("", encoding="utf-8")
        probe.unlink()
    except OSError as exc:
        return False, exc.strerror or str(exc)
    return True, str(path)


def _check_path(name: str, path: Path) -> Check:
    ok, detail = _writable(path)
    if ok:
        return Check(name, "OK", detail, mandatory=True)
    return Check(name, "FAIL", f"{path}: {detail}", mandatory=True)


def _check_keys(settings: Settings, selected: Sequence[str], report: Report) -> list[Check]:
    """One row per credential that matters for the selected sources. Values are masked."""
    wanted: list[tuple[str, bool, str]] = [
        # (variable, mandatory, why it matters)
        ("OPENALEX_API_KEY", True, "required since Feb 2026"),
    ]
    if "openalex" in selected or "crossref" in selected:
        wanted.append(
            ("OPENALEX_MAILTO", False, "raises OpenAlex to 5 req/s, Crossref polite pool")
        )
    if "s2" in selected:
        wanted.append(("S2_API_KEY", False, "1 req/s instead of ~0.3 req/s"))
    if "pubmed" in selected:
        wanted.append(("NCBI_API_KEY", False, "10 req/s instead of 3 req/s"))

    checks: list[Check] = []
    for name, mandatory, why in wanted:
        present = bool(settings.values.get(name))
        report.keys[name] = {
            "present": present,
            "masked": settings.masked(name),
            "origin": settings.origin_of(name),
        }
        if present:
            checks.append(
                Check(name, "OK", f"{settings.masked(name)} from {settings.origin_of(name)}")
            )
        else:
            status: Status = "FAIL" if mandatory else "WARN"
            checks.append(Check(name, status, f"not set ({why})", mandatory=mandatory))
    return checks


# --- live probes ------------------------------------------------------------


def _timed(name: str, mandatory: bool, probe: Any, client: Client, settings: Settings) -> Check:
    started = time.monotonic()
    status, detail = probe(client, settings)
    return Check(
        name, status, detail, mandatory=mandatory, duration_ms=(time.monotonic() - started) * 1000
    )


def _probe_openalex_search(client: Client, settings: Settings) -> tuple[Status, str]:
    if not settings.openalex_api_key:
        return "SKIP", "no OPENALEX_API_KEY — not attempted"
    try:
        response = client.get(
            OPENALEX_WORKS_URL,
            params={
                "search": OPENALEX_PROBE_QUERY,
                "per_page": 1,
                "select": "id,doi,title,publication_date,is_retracted",
            },
            cache=False,
        )
    except HttpError as exc:
        return "FAIL", f"unreachable: {exc}"
    if not response.ok:
        return "FAIL", f"HTTP {response.status_code}"

    payload = response.json()
    results = payload.get("results") or []
    if not results:
        return "FAIL", f"0 hits for {OPENALEX_PROBE_QUERY!r}"
    if "is_retracted" not in results[0]:
        return (
            "FAIL",
            "is_retracted missing from the response — the retraction filter would be blind",
        )
    cost = (payload.get("meta") or {}).get("cost_usd")
    suffix = f", cost ${cost}" if cost is not None else ""
    return "OK", f"{payload.get('meta', {}).get('count', '?')} hits, is_retracted readable{suffix}"


def _probe_openalex_psyarxiv(client: Client, settings: Settings) -> tuple[Status, str]:
    """PsyArXiv/SocArXiv coverage reaches us through OpenAlex's Crossref DOI ingestion."""
    if not settings.openalex_api_key:
        return "SKIP", "no OPENALEX_API_KEY — not attempted"
    try:
        response = client.get(
            OPENALEX_WORKS_URL,
            params={
                "filter": f"doi:https://doi.org/{PSYARXIV_PROBE_DOI}",
                "select": "id,doi,title,type",
            },
            cache=False,
        )
    except HttpError as exc:
        return "WARN", f"unreachable: {exc}"
    if not response.ok:
        return "WARN", f"HTTP {response.status_code} for {PSYARXIV_PROBE_DOI}"
    results = response.json().get("results") or []
    if not results:
        return "WARN", f"{PSYARXIV_PROBE_DOI} not indexed — preprint coverage may be thin"
    return "OK", f"{PSYARXIV_PROBE_DOI} indexed as {results[0].get('type', 'unknown')}"


def _s2_failure(response: Response) -> tuple[Status, str]:
    """Reachable but unhappy. Per §8.6 always a WARN: the scan degrades, it does not stop."""
    if is_retryable(response.status_code):
        return "WARN", f"HTTP {response.status_code} (rate limited or upstream error)"
    return "WARN", f"HTTP {response.status_code}"


def _probe_s2_search(client: Client, settings: Settings) -> tuple[Status, str]:
    try:
        response = client.get(
            S2_SEARCH_URL,
            params={"query": S2_PROBE_QUERY, "limit": 1, "fields": "title,year,externalIds"},
            cache=False,
        )
    except HttpError as exc:
        return _s2_unreachable(settings, exc)
    if response.ok:
        hits = len(response.json().get("data") or [])
        return "OK", f"{hits} hit(s)"
    return _s2_failure(response)


def _probe_s2_references(client: Client, settings: Settings) -> tuple[Status, str]:
    try:
        response = client.get(
            S2_REFERENCES_URL.format(doi=CROSSREF_PROBE_DOI),
            params={"limit": 1, "fields": "title,year"},
            cache=False,
        )
    except HttpError as exc:
        return _s2_unreachable(settings, exc)
    if response.ok:
        found = len(response.json().get("data") or [])
        return "OK", f"{found} reference(s) — graph expansion available"
    return _s2_failure(response)


def _s2_unreachable(settings: Settings, exc: HttpError) -> tuple[Status, str]:
    if settings.s2_api_key:
        return "FAIL", f"unreachable with a key: {exc}"
    return "WARN", f"unreachable and no S2_API_KEY: {exc}"


def _probe_crossref(client: Client, settings: Settings) -> tuple[Status, str]:
    try:
        response = client.get(CROSSREF_WORKS_URL.format(doi=CROSSREF_PROBE_DOI), cache=False)
    except HttpError as exc:
        return "WARN", f"unreachable, verification degrades to OpenAlex: {exc}"
    if not response.ok:
        return "WARN", f"HTTP {response.status_code}, verification degrades to OpenAlex"
    doi = (response.json().get("message") or {}).get("DOI", "")
    if doi.lower() != CROSSREF_PROBE_DOI.lower():
        return "WARN", f"resolved to {doi!r}, expected {CROSSREF_PROBE_DOI!r}"
    return "OK", f"{CROSSREF_PROBE_DOI} resolves"


def _probe_arxiv(client: Client, settings: Settings) -> tuple[Status, str]:
    """Goes through :class:`ArxivSource` so query mapping and Atom parsing are exercised (S10g)."""
    from research_scan.sources.arxiv import ArxivSource
    from research_scan.sources.base import SourceQueryError

    window = (date(1990, 1, 1), date(2100, 1, 1))
    try:
        hits = ArxivSource(client).search(ARXIV_PROBE_QUERY, window, limit=1, cache=False)
    except HttpError as exc:
        return "WARN", f"unreachable, cs/physics routing skipped: {exc}"
    except SourceQueryError as exc:
        return "WARN", f"{exc}, cs/physics routing skipped"
    if not hits:
        return "WARN", "no entries in the Atom feed"
    return "OK", f"parsed a candidate for {ARXIV_PROBE_QUERY!r} (arXiv:{hits[0].ids.arxiv})"


def _probe_pubmed(client: Client, settings: Settings) -> tuple[Status, str]:
    try:
        response = client.get(
            PUBMED_ESEARCH_URL,
            params={"db": "pubmed", "term": PUBMED_PROBE_TERM, "retmax": 1, "retmode": "json"},
            cache=False,
        )
    except HttpError as exc:
        return "WARN", f"unreachable, biomed routing skipped: {exc}"
    if not response.ok:
        return "WARN", f"HTTP {response.status_code}, biomed routing skipped"
    ids = (response.json().get("esearchresult") or {}).get("idlist") or []
    if not ids:
        return "WARN", f"0 hits for {PUBMED_PROBE_TERM!r}"
    return "OK", f"esearch returned pmid {ids[0]}"


# --- rendering --------------------------------------------------------------

_MARK: dict[Status, str] = {"OK": "✓", "WARN": "!", "FAIL": "✗", "SKIP": "-"}

#: What to do about it, per check, when it is not OK. One sentence, imperative, no diagnosis
#: theatre — `--verbose` is there for the detail.
_REMEDY: dict[str, str] = {
    "OPENALEX_API_KEY": "get a free key at openalex.org, then run: research-scan configure",
    "OPENALEX_MAILTO": "add your email with `research-scan configure` for 5 req/s",
    "S2_API_KEY": "request a key at semanticscholar.org/product/api, then re-run configure",
    "NCBI_API_KEY": "only matters for biomedical topics; add it with `research-scan configure`",
    "python": f"install Python {'.'.join(map(str, MIN_PYTHON))} or newer",
    "config path": "make the config directory writable",
    "cache path": "make the cache directory writable",
}


def _remedy(report: Report, names: Sequence[str]) -> str:
    """The first actionable sentence among the named checks that are not OK."""
    lookup = report.by_name()
    for name in names:
        check = lookup.get(name)
        if check is None or check.status == "OK":
            continue
        return _REMEDY.get(name) or check.detail
    return ""


def render_compact(report: Report) -> str:
    """Four lines and a verdict. `--verbose` renders the full table this summarises."""
    lines = [f"Research Scan {__version__}"]

    config_status = report.config_status
    if config_status is not None:
        blocking = tuple(
            check.name for check in report.checks if check.name in report.keys and check.mandatory
        )
        line = f"{_MARK[config_status]} configuration"
        if config_status != "OK":
            hint = _remedy(report, tuple(CONFIG_CHECKS) + blocking)
            line += f" — {hint}" if hint else ""
        lines.append(line)

    providers = report.providers()
    if providers:
        lines.append(
            "   ".join(
                f"{_MARK[status]} {PROVIDER_LABELS[name]}" for name, status in providers.items()
            )
        )
        for name, status in providers.items():
            if status != "OK":
                hint = _remedy(report, PROVIDER_CHECKS[name])
                if hint:
                    lines.append(f"  {PROVIDER_LABELS[name]}: {hint}")

    run_store = report.run_store_status
    if run_store is not None:
        line = f"{_MARK[run_store]} writable run store"
        if run_store != "OK":
            hint = _remedy(report, RUN_STORE_CHECKS)
            line += f" — {hint}" if hint else ""
        lines.append(line)

    warnings = sum(1 for check in report.checks if check.status in {"WARN", "SKIP"})
    if not report.ok:
        lines.append("Not ready — exit 3. Run `research-scan doctor --verbose` for the detail.")
    elif warnings:
        lines.append(f"Ready, {warnings} warning(s). `--verbose` for the detail.")
    else:
        lines.append("Ready.")
    return "\n".join(lines)


_SYMBOL = {"OK": "ok  ", "WARN": "warn", "FAIL": "FAIL", "SKIP": "skip"}


def render_table(report: Report) -> str:
    width = max((len(check.name) for check in report.checks), default=10)
    lines = [f"research-scan doctor — v{__version__}, python {platform.python_version()}", ""]
    for check in report.checks:
        marker = "!" if check.mandatory else " "
        timing = f"  [{check.duration_ms:.0f} ms]" if check.duration_ms is not None else ""
        lines.append(
            f"{_SYMBOL[check.status]} {marker} {check.name.ljust(width)}  {check.detail}{timing}"
        )

    lines += ["", "paths:"]
    for name, value in report.paths.items():
        lines.append(f"  {name}: {value}")

    failures = [check.name for check in report.checks if check.status == "FAIL"]
    warnings = [check.name for check in report.checks if check.status == "WARN"]
    lines.append("")
    if failures:
        lines.append(f"FAIL ({len(failures)}): {', '.join(failures)} — exit 3")
    else:
        lines.append(
            "ready" + (f" — {len(warnings)} warning(s): {', '.join(warnings)}" if warnings else "")
        )
    lines.append("(! marks a check that can exit 3)")
    return "\n".join(lines)
