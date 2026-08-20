# Third-party licenses

`research-scan` is licensed under Apache-2.0. See [`LICENSE`](LICENSE).

Its dependencies are separate works, distributed under their own licenses. This file is an
acknowledgment of what those are; it is not a redistribution notice, and no dependency's terms are
altered by anything here.

## What the dependency set is

The resolved set is defined by `pyproject.toml` (direct dependencies, exact pins for the MCP server)
and `uv.lock` (the full transitive closure with hashes). Those two files are authoritative — this
document describes them but is not a substitute for reading them.

At the time of writing the set is predominantly MIT, BSD (2- and 3-clause), Apache-2.0, ISC and
PSF-2.0, with one Unlicense entry.

## The one exception worth naming

**`certifi` is MPL-2.0** — file-level weak copyleft, rather than the permissive licenses the rest of
the set carries. It reaches this project as a transitive dependency of `httpx` and `httpcore`, and
is consumed unmodified: `research-scan` neither vendors it, patches it, nor derives from its source.
MPL-2.0's reciprocity attaches to modified versions of the covered files, so consuming the package
as published carries no obligation onto this project's own code.

This is recorded rather than remediated. Replacing or pinning around `certifi` would churn the
dependency graph of the standard Python HTTP stack for no license benefit.

## Regenerating the full table

Install the package into a clean environment and enumerate what actually resolved:

```bash
uv venv --python 3.13 /tmp/rs-licenses
VIRTUAL_ENV=/tmp/rs-licenses uv pip install research-scan pip-licenses
/tmp/rs-licenses/bin/pip-licenses --format=markdown --order=license
```

Run it against an installed environment rather than against `pyproject.toml`: extras, platform
markers and transitive pulls all move the real set, and only an install resolves them.
