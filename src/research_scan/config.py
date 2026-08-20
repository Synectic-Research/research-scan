# SPDX-License-Identifier: Apache-2.0
"""Credential discovery, resolved paths, and key redaction.

Precedence, highest first:

    process environment  >  ~/.config/research-scan/.env  >  ./.env

The user-level file outranks the repo-local one because the CLI is normally installed with
`uv tool install` and run from arbitrary directories; `./.env` exists for repo-local dev.

Nothing else in the package may read `os.environ` for a credential — everything goes through
:func:`load`, so :meth:`Settings.redact` sees every secret string before anything is logged.
"""

from __future__ import annotations

import contextlib
import os
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

APP_NAME = "research-scan"
REDACTED = "***REDACTED***"

#: Values shorter than this are not worth redacting — scrubbing them would mangle log lines.
MIN_REDACTABLE_LENGTH = 6

SECRET_VARS: tuple[str, ...] = (
    "OPENALEX_API_KEY",
    "S2_API_KEY",
    "NCBI_API_KEY",
    # The MCP adapter's shared bearer/path secret. Here rather than read straight from the
    # environment so `Settings.redact()` sees it before any adapter log line is written.
    "RESEARCH_SCAN_MCP_TOKEN",
)
PUBLIC_VARS: tuple[str, ...] = (
    "OPENALEX_MAILTO",
    "RESEARCH_SCAN_RUN",
    "RESEARCH_SCAN_MCP_DATA",
)
KNOWN_VARS: tuple[str, ...] = SECRET_VARS + PUBLIC_VARS

Layer = Literal["env", "user-config", "local-env", "unset"]


def config_dir() -> Path:
    return Path.home() / ".config" / APP_NAME


def config_env_path() -> Path:
    return config_dir() / ".env"


def cache_dir() -> Path:
    return Path.home() / ".cache" / APP_NAME


def cache_db_path() -> Path:
    return cache_dir() / "http.sqlite"


def local_env_path() -> Path:
    return Path.cwd() / ".env"


def parse_env_file(path: Path) -> dict[str, str]:
    """Parse a dotenv file. Tolerant by design: this is a hand-edited file."""
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {}

    parsed: dict[str, str] = {}
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("export "):
            stripped = stripped[len("export ") :].lstrip()
        name, sep, value = stripped.partition("=")
        name = name.strip()
        if not sep or not name:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        else:
            value = value.split(" #", 1)[0].strip()
        parsed[name] = value
    return parsed


def write_env(values: Mapping[str, str], *, path: Path | None = None) -> Path:
    """Merge `values` into the user `.env`, preserving every line this call does not own.

    Line-based on purpose, rather than reading through :func:`parse_env_file` and rewriting
    the result. The file is hand-edited and it is not only ours: the MCP server's
    ``RESEARCH_SCAN_MCP_TOKEN`` lives here too, and a running server reads it from this exact
    path. Rewriting the file from a parsed dict would drop every comment and every variable
    the caller did not happen to pass. So: replace the assignment lines we were given, append
    the ones that are new, and leave all other bytes alone.

    `.env` is the v0.5 credential store. Moving to a `credentials.toml` with a richer shape
    is a v0.6 decision — deliberately not taken here, because a second format would mean a
    second reader, and :func:`load` is meant to be the only one.

    Permissions are tightened on every call: 0700 on the directory, 0600 on the file.
    """
    target = path or config_env_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    with contextlib.suppress(OSError):  # a mode we cannot set is not a reason to lose the write
        target.parent.chmod(0o700)

    try:
        lines = target.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        lines = []

    remaining = dict(values)
    for index, line in enumerate(lines):
        name = _assigned_name(line)
        if name in remaining:
            # `export ` is kept if the hand-edited file used it: the line is the user's shape,
            # only the value is ours.
            prefix = "export " if line.strip().startswith("export ") else ""
            lines[index] = f"{prefix}{name}={remaining.pop(name)}"
    for name, value in remaining.items():
        lines.append(f"{name}={value}")

    body = "\n".join(lines) + ("\n" if lines else "")
    # Written beside the target and moved into place: an interrupted write must never leave
    # a truncated file where a running service expects to find its token.
    handle, temporary = tempfile.mkstemp(dir=target.parent, prefix=".env.", suffix=".tmp")
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            stream.write(body)
        os.chmod(temporary, 0o600)
        os.replace(temporary, target)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(temporary)
        raise
    return target


def _assigned_name(line: str) -> str | None:
    """The variable a line assigns, or None for a comment, a blank, or anything else."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    if stripped.startswith("export "):
        stripped = stripped[len("export ") :].lstrip()
    name, sep, _ = stripped.partition("=")
    return name.strip() if sep and name.strip() else None


def mask(value: str | None) -> str:
    """Render a credential for display: presence and tail only."""
    if not value:
        return "(unset)"
    if len(value) <= 8:
        return "*" * len(value)
    return f"****{value[-4:]}"


def redact_text(text: str, secrets: tuple[str, ...]) -> str:
    for secret in sorted(secrets, key=len, reverse=True):
        text = text.replace(secret, REDACTED)
    return text


@dataclass(frozen=True)
class Settings:
    """Resolved configuration for one CLI invocation."""

    values: Mapping[str, str]
    origins: Mapping[str, Layer]
    config_env: Path
    local_env: Path
    cache_db: Path

    @property
    def openalex_api_key(self) -> str | None:
        return self.values.get("OPENALEX_API_KEY")

    @property
    def openalex_mailto(self) -> str | None:
        return self.values.get("OPENALEX_MAILTO")

    @property
    def s2_api_key(self) -> str | None:
        return self.values.get("S2_API_KEY")

    @property
    def ncbi_api_key(self) -> str | None:
        return self.values.get("NCBI_API_KEY")

    @property
    def run_dir(self) -> str | None:
        return self.values.get("RESEARCH_SCAN_RUN")

    @property
    def mcp_token(self) -> str | None:
        return self.values.get("RESEARCH_SCAN_MCP_TOKEN")

    @property
    def mcp_data_dir(self) -> Path:
        """Where the MCP adapter isolates one run directory per scan."""
        configured = self.values.get("RESEARCH_SCAN_MCP_DATA")
        if configured:
            return Path(configured).expanduser()
        return Path.home() / ".local" / "share" / "research-scan-mcp" / "runs"

    @property
    def config_dir(self) -> Path:
        return self.config_env.parent

    @property
    def cache_dir(self) -> Path:
        return self.cache_db.parent

    def origin_of(self, name: str) -> Layer:
        return self.origins.get(name, "unset")

    def secrets(self) -> tuple[str, ...]:
        """Every secret string that must never reach a log, a run dir, or the cache."""
        return tuple(
            value
            for name in SECRET_VARS
            if (value := self.values.get(name)) and len(value) >= MIN_REDACTABLE_LENGTH
        )

    def redact(self, text: str) -> str:
        return redact_text(text, self.secrets())

    def masked(self, name: str) -> str:
        return mask(self.values.get(name))


def load(environ: Mapping[str, str] | None = None) -> Settings:
    """Resolve credentials across the three layers, recording where each one came from."""
    env = os.environ if environ is None else environ
    config_env = config_env_path()
    local_env = local_env_path()

    # Lowest precedence first; later layers overwrite earlier ones.
    layers: list[tuple[Layer, Mapping[str, str]]] = [
        ("local-env", parse_env_file(local_env)),
        ("user-config", parse_env_file(config_env)),
        ("env", env),
    ]

    values: dict[str, str] = {}
    origins: dict[str, Layer] = {}
    for layer, source in layers:
        for name in KNOWN_VARS:
            value = (source.get(name) or "").strip()
            if value:
                values[name] = value
                origins[name] = layer

    return Settings(
        values=values,
        origins=origins,
        config_env=config_env,
        local_env=local_env,
        cache_db=cache_db_path(),
    )
