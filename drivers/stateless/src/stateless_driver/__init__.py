"""An experimental reference cognition engine for the Research Scan screening stage.

Repo-only: nothing here is installed by the `research-scan` package, imported by it, or shipped
in its sdist or wheel. See `drivers/stateless/README.md` for what that means and what promotion
would require.
"""

__version__ = "0.1.0"

#: The version of the record shape in `provenance.py`. No provider-neutral engine protocol has
#: shipped yet; this driver is the reference the protocol is being drawn from, so the number
#: names a draft and says so (`PLUGGABLE_COGNITION_ENGINE`).
ENGINE_PROTOCOL_VERSION = "0.1.0-draft"

#: Stable identity of this engine. A provenance record naming it says which code ran, not which
#: provider is preferred: any engine may implement the same contract under its own id.
ENGINE_ID = "anthropic-stateless-reference"
