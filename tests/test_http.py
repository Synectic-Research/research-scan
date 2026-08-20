"""HTTP client: sqlite cache + 7-day TTL, retries/backoff, per-host rate limiting (spec §6)."""

from __future__ import annotations

import sqlite3

import httpx
import pytest
import respx

from research_scan import config, http

WORKS = "https://api.openalex.org/works"


class FakeClock:
    """Injectable wall clock + monotonic clock; sleeping advances both."""

    def __init__(self, start: float = 1_000_000.0) -> None:
        self.t = start
        self.slept: list[float] = []

    def time(self) -> float:
        return self.t

    def monotonic(self) -> float:
        return self.t

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self.t += seconds

    def advance(self, seconds: float) -> None:
        self.t += seconds


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


def make_client(settings: config.Settings, clock: FakeClock, **kwargs) -> http.HttpClient:
    kwargs.setdefault("max_retries", 3)
    return http.HttpClient(
        settings,
        sleep=clock.sleep,
        monotonic=clock.monotonic,
        now=clock.time,
        **kwargs,
    )


# --- cache ------------------------------------------------------------------


@respx.mock
def test_second_call_within_ttl_is_served_from_cache(settings, tmp_path):
    clock = FakeClock()
    route = respx.get(WORKS).mock(return_value=httpx.Response(200, json={"results": [1]}))

    with make_client(settings, clock, cache_path=tmp_path / "http.sqlite") as client:
        first = client.get(WORKS, params={"search": "x"})
        clock.advance(6 * 24 * 3600)
        second = client.get(WORKS, params={"search": "x"})

    assert route.call_count == 1
    assert first.from_cache is False
    assert second.from_cache is True
    assert second.json() == {"results": [1]}


@respx.mock
def test_cache_entry_expires_after_seven_days(settings, tmp_path):
    clock = FakeClock()
    route = respx.get(WORKS).mock(return_value=httpx.Response(200, json={"results": [1]}))

    with make_client(settings, clock, cache_path=tmp_path / "http.sqlite") as client:
        client.get(WORKS, params={"search": "x"})
        clock.advance(http.CACHE_TTL_SECONDS + 1)
        again = client.get(WORKS, params={"search": "x"})

    assert route.call_count == 2
    assert again.from_cache is False


@respx.mock
def test_different_params_are_different_cache_entries(settings, tmp_path):
    clock = FakeClock()
    route = respx.get(WORKS).mock(return_value=httpx.Response(200, json={"results": []}))

    with make_client(settings, clock, cache_path=tmp_path / "http.sqlite") as client:
        client.get(WORKS, params={"search": "a"})
        client.get(WORKS, params={"search": "b"})

    assert route.call_count == 2


@respx.mock
def test_param_order_does_not_change_the_cache_key(settings, tmp_path):
    clock = FakeClock()
    route = respx.get(WORKS).mock(return_value=httpx.Response(200, json={"results": []}))

    with make_client(settings, clock, cache_path=tmp_path / "http.sqlite") as client:
        client.get(WORKS, params={"search": "a", "per_page": 1})
        client.get(WORKS, params={"per_page": 1, "search": "a"})

    assert route.call_count == 1


@respx.mock
def test_no_cache_bypasses_reads_and_writes(settings, tmp_path):
    clock = FakeClock()
    route = respx.get(WORKS).mock(return_value=httpx.Response(200, json={"results": []}))

    with make_client(settings, clock, cache=False, cache_path=tmp_path / "http.sqlite") as client:
        client.get(WORKS, params={"search": "x"})
        client.get(WORKS, params={"search": "x"})

    assert route.call_count == 2
    assert not (tmp_path / "http.sqlite").exists()


@respx.mock
def test_per_call_cache_false_bypasses_a_caching_client(settings, tmp_path):
    """`doctor` needs live answers from a client that otherwise caches."""
    clock = FakeClock()
    route = respx.get(WORKS).mock(return_value=httpx.Response(200, json={"results": []}))

    with make_client(settings, clock, cache_path=tmp_path / "http.sqlite") as client:
        client.get(WORKS, params={"search": "x"}, cache=False)
        client.get(WORKS, params={"search": "x"}, cache=False)

    assert route.call_count == 2


@respx.mock
def test_error_responses_are_not_cached(settings, tmp_path):
    clock = FakeClock()
    route = respx.get(WORKS).mock(return_value=httpx.Response(404, json={"error": "no"}))

    with make_client(settings, clock, cache_path=tmp_path / "http.sqlite") as client:
        client.get(WORKS, params={"search": "x"})
        client.get(WORKS, params={"search": "x"})

    assert route.call_count == 2


@respx.mock
def test_cached_url_column_never_stores_a_key(settings, tmp_path):
    clock = FakeClock()
    respx.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi").mock(
        return_value=httpx.Response(200, json={"esearchresult": {"idlist": ["1"]}})
    )
    db = tmp_path / "http.sqlite"

    with make_client(settings, clock, cache_path=db) as client:
        client.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
            params={"db": "pubmed", "term": "crispr", "api_key": "fake-ncbi-key-1234"},
        )

    rows = sqlite3.connect(db).execute("select url from responses").fetchall()
    assert rows
    assert "fake-ncbi-key-1234" not in rows[0][0]


# --- retries ----------------------------------------------------------------


@respx.mock
def test_retries_429_then_succeeds(settings, tmp_path):
    clock = FakeClock()
    route = respx.get(WORKS).mock(
        side_effect=[
            httpx.Response(429),
            httpx.Response(503),
            httpx.Response(200, json={"results": [1]}),
        ]
    )

    with make_client(settings, clock, cache_path=tmp_path / "http.sqlite") as client:
        response = client.get(WORKS, params={"search": "x"})

    assert route.call_count == 3
    assert response.status_code == 200
    assert clock.slept[:2] == [1.0, 2.0]  # exponential backoff


@respx.mock
def test_last_response_is_returned_after_retries_are_exhausted(settings, tmp_path):
    """doctor must be able to *report* a 429 rather than crash on it."""
    clock = FakeClock()
    route = respx.get(WORKS).mock(return_value=httpx.Response(429))

    with make_client(settings, clock, max_retries=2, cache_path=tmp_path / "http.sqlite") as client:
        response = client.get(WORKS, params={"search": "x"})

    assert route.call_count == 3  # 1 attempt + 2 retries
    assert response.status_code == 429


@respx.mock
def test_transport_errors_raise_http_error(settings, tmp_path):
    clock = FakeClock()
    respx.get(WORKS).mock(side_effect=httpx.ConnectError("unreachable"))

    with (
        make_client(settings, clock, max_retries=1, cache_path=tmp_path / "http.sqlite") as client,
        pytest.raises(http.HttpError),
    ):
        client.get(WORKS, params={"search": "x"})


@respx.mock
def test_non_retryable_status_is_returned_immediately(settings, tmp_path):
    clock = FakeClock()
    route = respx.get(WORKS).mock(return_value=httpx.Response(403))

    with make_client(settings, clock, cache_path=tmp_path / "http.sqlite") as client:
        response = client.get(WORKS, params={"search": "x"})

    assert route.call_count == 1
    assert response.status_code == 403
    assert clock.slept == []


@respx.mock
def test_retry_after_header_is_honoured(settings, tmp_path):
    clock = FakeClock()
    respx.get(WORKS).mock(
        side_effect=[
            httpx.Response(429, headers={"Retry-After": "7"}),
            httpx.Response(200, json={}),
        ]
    )

    with make_client(settings, clock, cache_path=tmp_path / "http.sqlite") as client:
        client.get(WORKS, params={"search": "x"})

    assert clock.slept == [7.0]


# --- auth + rate limiting ---------------------------------------------------


@respx.mock
def test_openalex_gets_bearer_auth_and_mailto(settings, tmp_path):
    clock = FakeClock()
    route = respx.get(WORKS).mock(return_value=httpx.Response(200, json={}))

    with make_client(settings, clock, cache_path=tmp_path / "http.sqlite") as client:
        client.get(WORKS, params={"search": "x"})

    request = route.calls[0].request
    assert request.headers["authorization"] == "Bearer fake-openalex-key-abcd"
    assert request.url.params["mailto"] == "me@example.com"
    assert "research-scan/" in request.headers["user-agent"]


@respx.mock
def test_semantic_scholar_gets_its_api_key_header(settings, tmp_path):
    clock = FakeClock()
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    route = respx.get(url).mock(return_value=httpx.Response(200, json={}))

    with make_client(settings, clock, cache_path=tmp_path / "http.sqlite") as client:
        client.get(url, params={"query": "x"})

    assert route.calls[0].request.headers["x-api-key"] == "fake-s2-key-wxyz"


def test_rate_limiter_waits_out_the_per_host_interval():
    clock = FakeClock()
    limiter = http.RateLimiter(
        {"api.semanticscholar.org": 1.0}, sleep=clock.sleep, monotonic=clock.monotonic
    )

    assert limiter.acquire("api.semanticscholar.org") == 0.0
    assert limiter.acquire("api.semanticscholar.org") == 1.0
    clock.advance(5.0)
    assert limiter.acquire("api.semanticscholar.org") == 0.0


def test_rate_limiter_tracks_hosts_independently():
    clock = FakeClock()
    limiter = http.RateLimiter(
        {"a.example": 1.0, "b.example": 3.0}, sleep=clock.sleep, monotonic=clock.monotonic
    )

    limiter.acquire("a.example")
    assert limiter.acquire("b.example") == 0.0


def test_semantic_scholar_is_throttled_harder_without_a_key(settings, monkeypatch):
    keyed = http.min_intervals(settings)
    monkeypatch.delenv("S2_API_KEY", raising=False)
    anonymous = http.min_intervals(config.load())

    assert keyed["api.semanticscholar.org"] == 1.0
    assert anonymous["api.semanticscholar.org"] > keyed["api.semanticscholar.org"]
