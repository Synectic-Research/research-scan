# drivers/

Cognition engines: code that produces the judgements a scan needs, for people who want a scan
driven by something other than a hosting agent.

Nothing here is part of the `research-scan` package. These trees are not installed by it, not
imported by it, not shipped in its sdist or wheel, and not covered by its dependency list — each
driver carries its own `pyproject.toml` and `uv.lock`. The package's core stays model-independent:
a scan with no engine at all, screened by a person or an agent against the same rubrics, is the
first-class path and remains so.

| driver | what it is |
|---|---|
| [`stateless/`](stateless/) | experimental reference engine for the screening stage: stateless parallel calls, reconciled CID contract, recorded provenance |

The provider-neutral engine protocol these are informing has not shipped. Until it does, a driver
is a reference implementation you run yourself, against a run directory, on purpose.
