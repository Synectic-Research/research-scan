# SPDX-License-Identifier: Apache-2.0
"""research-scan — verified evidence scans for a project brief.

The package is deterministic plumbing: HTTP, dedup, graph expansion, shortlisting,
verification, rendering. Every judgment (queries, relevance, "why it matters") belongs
to the agent hosting the skill. There is no LLM SDK here, on purpose.
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _distribution_version

try:
    #: `pyproject.toml` is the only place the version is written. Resolving it from the
    #: installed distribution keeps `__version__`, `--version`, `manifest.json`, the
    #: User-Agent and the MCP handshake from ever disagreeing with it.
    __version__ = _distribution_version("research-scan")
except PackageNotFoundError:  # pragma: no cover - a source tree that was never installed
    # A PEP 440 local segment, deliberately not a version claim: it is a second *sentinel*,
    # never a second source of truth. Reinstall (`uv sync`) to get a real number.
    __version__ = "0+unknown"
