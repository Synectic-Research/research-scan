"""Config precedence, path resolution, and key redaction (spec §5, §6 logging)."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from research_scan import config
from research_scan.log import RedactingFilter


def write_env(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def sandbox(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    """An isolated HOME and cwd with every known var cleared from the process env."""
    home = tmp_path / "home"
    cwd = tmp_path / "cwd"
    home.mkdir()
    cwd.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.chdir(cwd)
    for var in config.KNOWN_VARS:
        monkeypatch.delenv(var, raising=False)
    return home, cwd


# --- precedence -------------------------------------------------------------


def test_process_env_beats_both_files(sandbox, monkeypatch):
    home, cwd = sandbox
    write_env(home / ".config/research-scan/.env", "OPENALEX_API_KEY=from-user-config\n")
    write_env(cwd / ".env", "OPENALEX_API_KEY=from-local-env\n")
    monkeypatch.setenv("OPENALEX_API_KEY", "from-process-env")

    settings = config.load()

    assert settings.openalex_api_key == "from-process-env"
    assert settings.origin_of("OPENALEX_API_KEY") == "env"


def test_user_config_beats_local_env(sandbox):
    home, cwd = sandbox
    write_env(home / ".config/research-scan/.env", "S2_API_KEY=from-user-config\n")
    write_env(cwd / ".env", "S2_API_KEY=from-local-env\n")

    settings = config.load()

    assert settings.s2_api_key == "from-user-config"
    assert settings.origin_of("S2_API_KEY") == "user-config"


def test_local_env_is_the_last_resort(sandbox):
    _, cwd = sandbox
    write_env(cwd / ".env", "NCBI_API_KEY=from-local-env\n")

    settings = config.load()

    assert settings.ncbi_api_key == "from-local-env"
    assert settings.origin_of("NCBI_API_KEY") == "local-env"


def test_layers_merge_per_variable(sandbox, monkeypatch):
    """Each variable resolves independently — a high layer does not shadow a whole file."""
    home, cwd = sandbox
    write_env(home / ".config/research-scan/.env", "OPENALEX_MAILTO=user@example.com\n")
    write_env(cwd / ".env", "S2_API_KEY=local-s2\n")
    monkeypatch.setenv("OPENALEX_API_KEY", "env-openalex")

    settings = config.load()

    assert settings.openalex_api_key == "env-openalex"
    assert settings.openalex_mailto == "user@example.com"
    assert settings.s2_api_key == "local-s2"
    assert settings.ncbi_api_key is None
    assert settings.origin_of("NCBI_API_KEY") == "unset"


def test_missing_files_are_not_an_error(sandbox):
    settings = config.load()
    assert settings.openalex_api_key is None
    assert settings.secrets() == ()


def test_empty_value_counts_as_unset(sandbox):
    home, _ = sandbox
    write_env(home / ".config/research-scan/.env", "OPENALEX_API_KEY=\nS2_API_KEY=   \n")

    settings = config.load()

    assert settings.openalex_api_key is None
    assert settings.s2_api_key is None


def test_unknown_variables_are_ignored(sandbox):
    home, _ = sandbox
    write_env(
        home / ".config/research-scan/.env",
        "ANTHROPIC_API_KEY=not-ours-and-long\nOPENALEX_API_KEY=ours-and-long\n",
    )

    settings = config.load()

    assert settings.values.get("ANTHROPIC_API_KEY") is None
    assert settings.secrets() == ("ours-and-long",)


# --- .env parsing -----------------------------------------------------------


def test_parse_env_file_quirks(tmp_path: Path):
    path = tmp_path / ".env"
    path.write_text(
        "\n".join(
            [
                "# a comment",
                "",
                "export OPENALEX_API_KEY=exported-value",
                'S2_API_KEY="double quoted"',
                "NCBI_API_KEY='single quoted'",
                "OPENALEX_MAILTO=me@example.com  # trailing comment",
                "MALFORMED_LINE_WITHOUT_EQUALS",
            ]
        ),
        encoding="utf-8",
    )

    parsed = config.parse_env_file(path)

    assert parsed == {
        "OPENALEX_API_KEY": "exported-value",
        "S2_API_KEY": "double quoted",
        "NCBI_API_KEY": "single quoted",
        "OPENALEX_MAILTO": "me@example.com",
    }


def test_parse_env_file_missing_returns_empty(tmp_path: Path):
    assert config.parse_env_file(tmp_path / "nope.env") == {}


# --- paths ------------------------------------------------------------------


def test_paths_are_the_documented_fixed_locations(sandbox):
    home, cwd = sandbox
    settings = config.load()

    assert settings.config_env == home / ".config/research-scan/.env"
    assert settings.cache_db == home / ".cache/research-scan/http.sqlite"
    assert settings.local_env == cwd / ".env"


# --- redaction --------------------------------------------------------------


def test_redact_replaces_every_secret(sandbox, monkeypatch):
    monkeypatch.setenv("OPENALEX_API_KEY", "oa-secret-value")
    monkeypatch.setenv("S2_API_KEY", "s2-secret-value")
    monkeypatch.setenv("OPENALEX_MAILTO", "me@example.com")
    settings = config.load()

    text = (
        "GET https://api.openalex.org/works?api_key=oa-secret-value"
        " (s2=s2-secret-value) mailto=me@example.com"
    )
    redacted = settings.redact(text)

    assert "oa-secret-value" not in redacted
    assert "s2-secret-value" not in redacted
    assert redacted.count(config.REDACTED) == 2
    # mailto is not a secret and stays legible in logs
    assert "me@example.com" in redacted


def test_redact_handles_overlapping_secrets(sandbox, monkeypatch):
    """The shorter secret is a prefix of the longer one, so replacement order decides the result.

    Redacting the short one first would leave `***REDACTED***-000000` — the tail of the real key
    surviving in a log line. Both values are ≥ `MIN_REDACTABLE_LENGTH`, so both are live secrets.
    """
    monkeypatch.setenv("OPENALEX_API_KEY", "not-a-real-key-000000")
    monkeypatch.setenv("S2_API_KEY", "not-a-real-key")
    settings = config.load()

    redacted = settings.redact("key=not-a-real-key-000000")

    assert "not-a-real-key-000000" not in redacted
    assert redacted == f"key={config.REDACTED}"


def test_redact_ignores_trivially_short_values(sandbox, monkeypatch):
    """A 2-char 'secret' would otherwise scrub half of every log line."""
    monkeypatch.setenv("OPENALEX_API_KEY", "ab")
    settings = config.load()

    assert settings.redact("a table of abstracts") == "a table of abstracts"


def test_mask_shows_only_the_tail():
    assert config.mask("supersecretkey1234") == "****1234"
    assert config.mask("short") == "*****"
    assert config.mask(None) == "(unset)"


def test_redacting_log_filter_scrubs_message_and_args(sandbox, monkeypatch, caplog):
    monkeypatch.setenv("OPENALEX_API_KEY", "oa-secret-value")
    settings = config.load()

    logger = logging.getLogger("research_scan.test_redaction")
    logger.addFilter(RedactingFilter(settings.secrets()))
    try:
        with caplog.at_level(logging.INFO):
            logger.info("bearer %s for %s", "oa-secret-value", "https://api.openalex.org")
    finally:
        logger.filters.clear()

    rendered = caplog.records[-1].getMessage()
    assert "oa-secret-value" not in rendered
    assert config.REDACTED in rendered
