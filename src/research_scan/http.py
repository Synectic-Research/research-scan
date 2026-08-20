# SPDX-License-Identifier: Apache-2.0
"""HTTP layer: one httpx client, per-host rate limiting, bounded retries, sqlite response cache.

Three properties the rest of the package depends on:

* **Politeness is structural.** Rate limits live in a per-host table (spec §6), not in call sites.
* **Re-running a stage costs nothing.** Successful GETs are cached in
  ``~/.cache/research-scan/http.sqlite`` for 7 days; ``--no-cache`` bypasses it and `doctor`
  passes ``cache=False`` per call.
* **A bad status is data, not a crash.** After retries are exhausted the last response is
  returned so callers (notably `doctor`) can report "429" rather than blow up. Only a transport
  failure — nothing came back at all — raises :class:`HttpError`.
"""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from dataclasses import field as dc_field
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import httpx

from research_scan import __version__
from research_scan.config import Settings

log = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 7 * 24 * 60 * 60

#: Minimum seconds between requests to a host (spec §6 "Rate limits & retries").
HOST_MIN_INTERVAL: dict[str, float] = {
    "api.openalex.org": 0.2,  # 5 req/s with key + mailto
    "api.semanticscholar.org": 1.0,  # 1 req/s with key
    "api.crossref.org": 0.2,  # polite pool
    "export.arxiv.org": 3.0,  # 1 req / 3 s
    "eutils.ncbi.nlm.nih.gov": 0.34,  # 3 req/s
}
DEFAULT_MIN_INTERVAL = 1.0
S2_ANONYMOUS_MIN_INTERVAL = 3.34  # 0.3 req/s without a key
NCBI_KEYED_MIN_INTERVAL = 0.1  # 10 req/s with a key

_MAX_RETRY_AFTER = 60.0
_SECRET_PARAM_NAMES = frozenset({"api_key", "apikey", "key", "token"})

_CACHE_SCHEMA = """
CREATE TABLE IF NOT EXISTS responses (
    key         TEXT PRIMARY KEY,
    url         TEXT NOT NULL,
    status      INTEGER NOT NULL,
    headers     TEXT NOT NULL,
    body        BLOB NOT NULL,
    fetched_at  REAL NOT NULL
)
"""


def min_intervals(settings: Settings) -> dict[str, float]:
    """Per-host intervals adjusted for which keys are actually present."""
    intervals = dict(HOST_MIN_INTERVAL)
    if not settings.s2_api_key:
        intervals["api.semanticscholar.org"] = S2_ANONYMOUS_MIN_INTERVAL
    if settings.ncbi_api_key:
        intervals["eutils.ncbi.nlm.nih.gov"] = NCBI_KEYED_MIN_INTERVAL
    return intervals


#: The host each source authenticates against, for :func:`auth_mode`.
SOURCE_HOSTS: dict[str, str] = {
    "openalex": "api.openalex.org",
    "s2": "api.semanticscholar.org",
    "arxiv": "export.arxiv.org",
    "pubmed": "eutils.ncbi.nlm.nih.gov",
}


def auth_mode(settings: Settings, source: str) -> str:
    """``key`` when this run sends a credential to the source's host, ``anon`` otherwise.

    Recorded per source in the stage log and the manifest because a 429 under ``anon`` and a 429
    under ``key`` are different bugs, and the run dir is the only place that question can be
    answered after the fact. arXiv takes no credential, so it is always ``anon``.
    """
    host = SOURCE_HOSTS.get(source)
    if host == "api.openalex.org":
        return "key" if settings.openalex_api_key else "anon"
    if host == "api.semanticscholar.org":
        return "key" if settings.s2_api_key else "anon"
    if host == "eutils.ncbi.nlm.nih.gov":
        return "key" if settings.ncbi_api_key else "anon"
    return "anon"


def user_agent(settings: Settings) -> str:
    """Crossref's polite pool and OpenAlex both key off a contactable User-Agent."""
    base = f"research-scan/{__version__} (+https://github.com/research-scan)"
    mailto = settings.openalex_mailto
    return f"{base} mailto:{mailto}" if mailto else base


@dataclass
class ClientStats:
    """What the client did during one run, for the stage log (canon §8)."""

    requests: int = 0
    cache_hits: int = 0
    transport_errors: int = 0
    status: dict[str, int] = dc_field(default_factory=dict)

    def record_status(self, status_code: int) -> None:
        self.requests += 1
        key = str(status_code)
        self.status[key] = self.status.get(key, 0) + 1

    def record_cache_hit(self) -> None:
        self.cache_hits += 1

    def record_transport_error(self) -> None:
        self.requests += 1
        self.transport_errors += 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "requests": self.requests,
            "cache_hits": self.cache_hits,
            "transport_errors": self.transport_errors,
            "status": dict(sorted(self.status.items())),
        }


class HttpError(RuntimeError):
    """No response at all after retries — DNS, TLS, connect or read failure."""

    def __init__(self, message: str, *, url: str, attempts: int) -> None:
        super().__init__(message)
        self.url = url
        self.attempts = attempts


@dataclass(frozen=True)
class Response:
    url: str  # canonical and redacted; safe to log
    status_code: int
    headers: dict[str, str]
    content: bytes
    from_cache: bool = False

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 300

    @property
    def text(self) -> str:
        return self.content.decode("utf-8", errors="replace")

    def json(self) -> Any:
        return json.loads(self.content)


def is_retryable(status_code: int) -> bool:
    return status_code == 429 or 500 <= status_code < 600


def canonical_url(url: str, params: Mapping[str, Any] | None = None) -> str:
    """URL with query parameters merged and sorted, so cache keys are order-independent."""
    merged = httpx.URL(url)
    if params:
        merged = merged.copy_merge_params({k: str(v) for k, v in params.items()})
    query = urlencode(sorted(merged.params.multi_items()))
    return str(merged.copy_with(query=query.encode() if query else None))


def redact_url(url: str, settings: Settings) -> str:
    """Strip credential-shaped query parameters, then scrub any known secret value."""
    parsed = httpx.URL(url)
    items = [
        (name, "REDACTED" if name.lower() in _SECRET_PARAM_NAMES else value)
        for name, value in parsed.params.multi_items()
    ]
    query = urlencode(items)
    return settings.redact(str(parsed.copy_with(query=query.encode() if query else None)))


def cache_key(
    method: str,
    url: str,
    params: Mapping[str, Any] | None = None,
    json_body: Any = None,
) -> str:
    """Hash of the *caller's* request, computed before auth is applied.

    Keeping credentials out of the key means rotating a key does not invalidate the cache. The
    body is part of the key because S2's recommendations endpoint is a POST whose seed list is
    the whole query.
    """
    body = json.dumps(json_body, sort_keys=True) if json_body is not None else ""
    material = f"{method.upper()}\n{canonical_url(url, params)}\n{body}"
    return hashlib.sha256(material.encode()).hexdigest()


class RateLimiter:
    """Minimum-interval limiter, one slot per host."""

    def __init__(
        self,
        intervals: Mapping[str, float],
        *,
        default: float = DEFAULT_MIN_INTERVAL,
        monotonic: Callable[[], float] | None = None,
        sleep: Callable[[float], None] | None = None,
    ) -> None:
        self._intervals = dict(intervals)
        self._default = default
        # Resolved at call time, not bound at import, so tests can substitute a fake clock.
        self._monotonic = monotonic or time.monotonic
        self._sleep = sleep or time.sleep
        self._last: dict[str, float] = {}

    def acquire(self, host: str) -> float:
        """Block until the host's next slot. Returns the seconds waited."""
        interval = self._intervals.get(host, self._default)
        now = self._monotonic()
        waited = 0.0
        last = self._last.get(host)
        if last is not None:
            remaining = interval - (now - last)
            if remaining > 0:
                self._sleep(remaining)
                waited = remaining
                now = self._monotonic()
        self._last[host] = now
        return waited


class HttpCache:
    """sqlite-backed response cache with a fixed TTL."""

    def __init__(
        self,
        path: Path,
        *,
        ttl_seconds: int = CACHE_TTL_SECONDS,
        now: Callable[[], float] | None = None,
    ) -> None:
        self.path = Path(path)
        self.ttl_seconds = ttl_seconds
        self._now = now or time.time
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.path))
        self._conn.execute(_CACHE_SCHEMA)
        self._conn.commit()

    def get(self, key: str) -> Response | None:
        row = self._conn.execute(
            "SELECT url, status, headers, body, fetched_at FROM responses WHERE key = ?", (key,)
        ).fetchone()
        if row is None:
            return None
        url, status, headers, body, fetched_at = row
        if self._now() - fetched_at > self.ttl_seconds:
            self._conn.execute("DELETE FROM responses WHERE key = ?", (key,))
            self._conn.commit()
            return None
        return Response(
            url=url,
            status_code=status,
            headers=json.loads(headers),
            content=body,
            from_cache=True,
        )

    def set(self, key: str, response: Response) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO responses (key, url, status, headers, body, fetched_at)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (
                key,
                response.url,
                response.status_code,
                json.dumps(response.headers),
                response.content,
                self._now(),
            ),
        )
        self._conn.commit()

    def purge_expired(self) -> int:
        cursor = self._conn.execute(
            "DELETE FROM responses WHERE ? - fetched_at > ?", (self._now(), self.ttl_seconds)
        )
        self._conn.commit()
        return cursor.rowcount

    def close(self) -> None:
        self._conn.close()


class HttpClient:
    """The only thing in the package that talks to the network."""

    def __init__(
        self,
        settings: Settings,
        *,
        cache: bool = True,
        cache_path: Path | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        backoff_base: float = 1.0,
        sleep: Callable[[float], None] | None = None,
        monotonic: Callable[[], float] | None = None,
        now: Callable[[], float] | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.settings = settings
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self._sleep = sleep or time.sleep
        self._cache_enabled = cache
        self._cache = HttpCache(cache_path or settings.cache_db, now=now) if cache else None
        self._limiter = RateLimiter(min_intervals(settings), monotonic=monotonic, sleep=sleep)
        self._owns_client = client is None
        self._client = client or httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": user_agent(settings)},
        )
        #: Per-run tallies for the stage log (canon §8): status histogram, cache hits, failures.
        self.stats = ClientStats()

    # -- public API ----------------------------------------------------------

    def get(
        self,
        url: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        cache: bool | None = None,
    ) -> Response:
        return self.request("GET", url, params=params, headers=headers, cache=cache)

    def post(
        self,
        url: str,
        *,
        json_body: Any = None,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        cache: bool | None = None,
    ) -> Response:
        return self.request(
            "POST", url, params=params, headers=headers, json_body=json_body, cache=cache
        )

    def request(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        json_body: Any = None,
        cache: bool | None = None,
    ) -> Response:
        use_cache = self._cache_enabled if cache is None else (cache and self._cache is not None)
        key = cache_key(method, url, params, json_body)

        if use_cache and self._cache is not None:
            hit = self._cache.get(key)
            if hit is not None:
                log.debug("cache hit %s", hit.url)
                self.stats.record_cache_hit()
                return hit

        request_params, request_headers = self._authorize(url, params, headers)
        response = self._request(method, url, request_params, request_headers, json_body)

        if use_cache and self._cache is not None and response.ok:
            self._cache.set(key, response)
        return response

    def close(self) -> None:
        if self._owns_client:
            self._client.close()
        if self._cache is not None:
            self._cache.close()

    def __enter__(self) -> HttpClient:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    # -- internals -----------------------------------------------------------

    def _authorize(
        self,
        url: str,
        params: Mapping[str, Any] | None,
        headers: Mapping[str, str] | None,
    ) -> tuple[dict[str, Any], dict[str, str]]:
        request_params = dict(params or {})
        request_headers = dict(headers or {})
        host = httpx.URL(url).host
        settings = self.settings

        if host == "api.openalex.org":
            if settings.openalex_api_key:
                request_headers.setdefault("Authorization", f"Bearer {settings.openalex_api_key}")
            if settings.openalex_mailto:
                request_params.setdefault("mailto", settings.openalex_mailto)
        elif host == "api.semanticscholar.org":
            if settings.s2_api_key:
                request_headers.setdefault("x-api-key", settings.s2_api_key)
        elif host == "eutils.ncbi.nlm.nih.gov":
            if settings.ncbi_api_key:
                request_params.setdefault("api_key", settings.ncbi_api_key)

        return request_params, request_headers

    def _request(
        self,
        method: str,
        url: str,
        params: Mapping[str, Any],
        headers: Mapping[str, str],
        json_body: Any = None,
    ) -> Response:
        host = httpx.URL(url).host or ""
        safe_url = redact_url(canonical_url(url, params), self.settings)
        delay = self.backoff_base
        last: Response | None = None
        last_error: Exception | None = None

        for attempt in range(self.max_retries + 1):
            self._limiter.acquire(host)
            started = time.monotonic()
            try:
                raw = self._client.request(
                    method, url, params=dict(params), headers=dict(headers), json=json_body
                )
            except httpx.HTTPError as exc:
                last_error = exc
                self.stats.record_transport_error()
                log.info("%s %s -> transport error (%s)", method, safe_url, type(exc).__name__)
            else:
                last = Response(
                    url=safe_url,
                    status_code=raw.status_code,
                    headers=dict(raw.headers),
                    content=raw.content,
                )
                self.stats.record_status(raw.status_code)
                log.info(
                    "%s %s -> %s in %.0f ms",
                    method,
                    safe_url,
                    raw.status_code,
                    (time.monotonic() - started) * 1000,
                )
                if not is_retryable(raw.status_code):
                    return last

            if attempt == self.max_retries:
                break
            wait = _retry_after(last) if last is not None else None
            self._sleep(wait if wait is not None else delay)
            delay *= 2

        if last is not None:
            return last
        raise HttpError(
            f"{method} {safe_url} failed after {self.max_retries + 1} attempts: {last_error}",
            url=safe_url,
            attempts=self.max_retries + 1,
        )


def _retry_after(response: Response) -> float | None:
    raw = response.headers.get("retry-after") or response.headers.get("Retry-After")
    if not raw:
        return None
    try:
        return min(float(raw), _MAX_RETRY_AFTER)
    except ValueError:
        return None
