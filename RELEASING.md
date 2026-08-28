# Releasing research-scan

A release moves four surfaces: PyPI, the GitHub Release, the Claude Code plugin marketplace, and
the MCP registry. Three of them are automated from a tag push. The fourth — the registry — is
deliberately manual, because automating it would mean putting the Ed25519 domain key into GitHub
secrets, and that key is what proves control of `synectic.org`. It stays off CI.

## The happy path

**1. One atomic version commit.** Five things move together, and CI fails the build if any of them
disagrees:

| File | Field |
| --- | --- |
| `pyproject.toml` | `[project] version` |
| `.claude-plugin/plugin.json` | `version` |
| `CITATION.cff` | `version`, and `date-released` |
| `server.json` | `version` **and** `packages[0].version` |
| `CHANGELOG.md` | a `## [X.Y.Z]` section |

The changelog section is not optional: the GitHub Release body is generated from it, and the
release job fails when the section is missing.

The five-way check is `scripts/check_versions.py`, run by both `ci.yml` and `release.yml`. On a
tag, `release.yml` passes `--tag` so the tag becomes a sixth claim. Run it locally before pushing:

```bash
python3 scripts/check_versions.py       # or --tag vX.Y.Z to include the tag
```

Then `uv sync` so the lockfile and the installed distribution follow, and check the gate locally:

```bash
uv sync
uv run ruff check && uv run pytest -q
uv run research-scan --version          # must print the new version
```

**2. Push the tag as a single ref.**

```bash
git push origin main
git tag -a vX.Y.Z -m "vX.Y.Z — <short reason>"
git push origin refs/tags/vX.Y.Z
```

Never `git push --tags`. This repository carries local tags from its private era that must not
reach `origin`; `--tags` would push all of them at once.

**3. Approve the `pypi` environment.** The workflow stops before publishing and waits for a
review from the repository owner in the GitHub UI — Actions → the running workflow → **Review
deployments** → approve. Nothing reaches PyPI until that click. This is the last point at which a
release can be stopped for free.

**4. The workflow does the rest.** After approval it publishes to PyPI via Trusted Publishing (no
API token exists anywhere), generates provenance attestations for both archives, creates the
GitHub Release with notes from `CHANGELOG.md`, attaches `research-scan-skill-X.Y.Z.skill` and
`research-scan-plugin-X.Y.Z.zip`, and downloads both back from the public release to confirm the
served bytes match what it built. The wheel and sdist are **not** attached: PyPI is canonical for
those.

**5. Publish to the MCP registry by hand.** From a checkout of the released tag:

```bash
mcp-publisher login dns -domain synectic.org -private-key <ed25519-key-hex>
mcp-publisher publish
```

The key lives at `~/.config/mcp-publisher/synectic.org-ed25519.pem` and is PKCS#8; the CLI wants
the raw 32-byte seed as hex. It never goes into the repository, CI, or a secret store.

`publish` sends the whole of `server.json`, `websiteUrl` included — so the documentation site's
address reaches the registry only through this step. Changing that URL without a republish leaves
the registry pointing at the old one, and no drift check catches it: `registry-check.yml` compares
versions, not URLs. `mcp-publisher validate` checks the file against the live registry before you
publish, and is worth running first; note that the registry caps `description` at 100 characters.

**6. The drift check has your back.** `registry-check.yml` runs weekly and fails if PyPI and the
registry hold different versions — which is exactly what a forgotten step 5 looks like. You can
also run it on demand from the Actions tab.

## Verify after every release

A green workflow proves the artifacts were built and uploaded. It does not prove anyone can
install them. Run these from a machine that is not this repository:

```bash
# PyPI, resolved fresh. Add --refresh, or use an isolated UV_TOOL_DIR, if a
# previously installed `research-scan` uv tool shadows the resolve.
uvx research-scan --version

# The plugin, from the public marketplace
claude plugin marketplace update synectic
claude plugin install research-scan@synectic     # or `claude plugin update` if installed
claude plugin details research-scan@synectic     # skill present, MCP server listed
```

Then, in a session, `/mcp` should show `research-scan` connected with `scan_start`,
`scan_continue`, `scan_verify` and `scan_result`.

## Refresh the private server, then verify the fingerprint

**Required. A release is not complete until the resident process is refreshed and
fingerprint-verified.** Publishing moves PyPI, the registry and the tag; it does not touch a
server that is already running. A source install serves the modules it imported at boot, so the
checkout can advance to the new release while the process keeps answering with the old one — that
is not hypothetical, it ran for six days undetected before the fingerprint existed.

**1. Restart**, per `ops.md` in the private stack-context staging tree:

```bash
launchctl kickstart -k gui/$(id -u)/org.synectic.research-scan-mcp
```

Note the wall-clock time of the restart; `started_at` is checked against it below.

**2. Read the fingerprint back.** Liveness is public, but the tuple needs the token — so the
health call is authenticated. The token goes into a variable and is never echoed:

```bash
TOKEN="$(grep '^RESEARCH_SCAN_MCP_TOKEN=' ~/.config/research-scan/.env | cut -d= -f2-)"
curl -sS -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8765/health
```

**3. Check it against the release, by deployment mode.** The mode is not a judgement call:
`dirty: null` means the package resolved from an installed copy, anything else means a checkout.

| | source deployment | wheel deployment |
|---|---|---|
| `version` | equals the released version | equals the released version |
| `git_sha` | equals the released commit (12 hex) | `"unknown"` — **expected, not a defect** |
| `dirty` | `false` — a dirty tree invalidates the release claim | `null` |
| identity | — | artifact hash matches the published wheel |
| `started_at` | at or after the restart in step 1 | at or after the restart in step 1 |

A `started_at` earlier than the restart means the kickstart did not take and the old process is
still bound to the port. Re-read `ops.md`; do not re-run the release.

**4. Smoke-test the tunnel.** A bad path must come back **404** — the server answering that the
route does not exist. A **502** or **530** is Cloudflare failing to reach the origin, which means
the tunnel is down even though the local port is fine:

```bash
curl -s -o /dev/null -w '%{http_code}\n' "https://<tunnel-host>/definitely-not-the-secret/mcp"
```

### The release receipt

One JSON object per release, recording what was published and what the process actually reports.
It is written to the **private** stack-context tree, never to this repository — the procedure is
public, the receipts are not.

```bash
cd ~/Projects/research-scan
VERSION="$(uv run research-scan --version)"
TOKEN="$(grep '^RESEARCH_SCAN_MCP_TOKEN=' ~/.config/research-scan/.env | cut -d= -f2-)"
RECEIPTS=~/Projects/stack-context/staging/research-scan/receipts
mkdir -p "$RECEIPTS"

curl -sS -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8765/health \
  | VERSION="$VERSION" python3 -c '
import json, os, subprocess, sys, urllib.request
from datetime import UTC, datetime

health = json.load(sys.stdin)
git = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True).stdout.strip()
with urllib.request.urlopen("https://pypi.org/pypi/research-scan/json", timeout=30) as fh:
    pypi = json.load(fh)["info"]["version"]

json.dump({
    "version": os.environ["VERSION"],
    "git_sha": git("rev-parse", "HEAD")[:12],
    "dirty": bool(git("status", "--porcelain")),
    # `dirty: null` is the installed-copy signal. A checkout whose git will not answer also lands
    # here, but it fails the source criteria anyway on `git_sha == "unknown"`, so the label
    # cannot mask a bad release.
    "deployment_mode": "wheel" if health.get("dirty") is None else "source",
    "pypi_version": pypi,
    "server_sha": health.get("git_sha"),
    "server_started_at": health.get("started_at"),
    "verified_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
}, sys.stdout, indent=2)
print()
' > "$RECEIPTS/v$VERSION.json"

cat "$RECEIPTS/v$VERSION.json"
```

`pypi.org` HTML is Fastly-challenged; the JSON API above is the reliable read. The receipt carries
no token and no hostname. An commits stack-context.

### What the SHA does and does not prove

> SHA+clean is operational observability, not cryptographic proof of executed code from a mutable
> checkout; immutable wheel/artifact deployment is the stronger end state (backlog decision at
> next release).

Concretely: the fingerprint reports what `HEAD` pointed at and what the tree looked like *when the
process booted*. It cannot attest that the bytes running in memory are that commit's — a checkout
can be edited between boot and inspection, and a `.pyc` can outlive its source. It closes the gap
that actually bit us, which was a stale process nobody could see, and it is worth exactly that.

## Rollback

Releases are append-only. Nothing here deletes.

- **PyPI**: yank the release if it is actively harmful (`pypi.org` → the project → Manage → the
  version → Yank). Yanking hides it from resolvers without breaking pins that already reference
  it. **The version number stays burned** — PyPI never allows reuse, and neither should you.
- **GitHub Release**: edit the notes to say the release is broken and what to use instead. Leave
  the assets in place; something may already reference their hashes.
- **Tags are permanent.** Never delete or move a tag that has been pushed. Someone may have built
  from it.
- **Fix forward** with a patch release. That is the only repair path.
- **The registry** needs a manual `mcp-publisher publish` from the fixed tag, the same as any
  other release.

## Single source of truth for release notes

GitHub Release bodies are generated from `CHANGELOG.md` by the release job. Never hand-edit a
release body: the next person to read the changelog would see something different from what the
release says. Edit `CHANGELOG.md` instead, and if a published release needs new text, correct the
changelog and update the release body from it.

## Testing workflow changes

`release.yml` accepts `workflow_dispatch`, which runs the **build job only** — lint, tests, the
five-way version guard, the wheel identity check, and the deterministic asset build with its
hashes in the job summary. `publish-pypi` and `release` are gated on
`github.event_name == 'push'` in addition to the `v*` tag prefix, so dispatching the workflow
cannot publish even if you point it at a tag.

Read that limit precisely: dispatch is the dry run **for the build job**, and it never reaches
the release job or the round-trip verifier inside it. Before v0.6.1 that meant the first time
the verifier ran on a release was the release — which is how v0.6.0 published cleanly and then
went red on a check of its own. The verifier is now a script with its own tests
(`scripts/verify_release_assets.py`, `tests/test_release_assets.py`), so its rehearsal is the
ordinary pytest suite on every push and PR, before any tag exists.

Real publishing requires a tag push. To rebuild the archives locally and compare against what a
release published:

```bash
python scripts/build_plugin_assets.py --ref vX.Y.Z --out /tmp/assets
```

Same builder as CI, same bytes: it exports the tree with `git archive` and writes zip entries in
sorted order with fixed timestamps, so the hashes are reproducible from any machine.
