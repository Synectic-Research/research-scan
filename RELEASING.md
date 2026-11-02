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

**4. Smoke-test the tunnel.** A bad path must come back **401** — the server's token gate
answering before any route runs (it was a router 404 before 0.6.2). A **502** or **530** is
Cloudflare failing to reach the origin, which means the tunnel is down even though the local port
is fine. An unauthenticated `initialize` must be refused the same way, with no session opened:

```bash
curl -s -o /dev/null -w '%{http_code}\n' "https://<tunnel-host>/definitely-not-the-secret/mcp"
curl -s -o /dev/null -w '%{http_code}\n' -X POST "https://<tunnel-host>/mcp" \
  -H 'content-type: application/json' -H 'accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"smoke","version":"0"}}}'
```

Both print `401`. `GET /health` without a token prints `200`.

### Hardening the resident server

The path-secret form puts the token in every request line. From 0.6.2 the server redacts it from
its own logs, but the process's files and the token's history still need an operator:

- **Log permissions.** `chmod 600 ~/Library/Logs/research-scan/mcp*.log` — an existing file keeps
  its mode when it is reopened for append, so this holds across restarts. Also add
  `<key>Umask</key><integer>63</integer>` (octal 077) to the LaunchAgent plist so anything the
  process creates is private; re-check the log modes after the first restart rather than assume
  launchd applies it to the files it opens for you. A `0644` log is readable by every process on
  the machine, including a VM that shares the host filesystem.
- **Rotate after any exposure.** A token that ever reached a log, a shell history or a URL bar is
  spent. Rotate in one sitting, in one shell, with the connector idle: it is down from step 1
  (the message gate re-reads `.env` on every call) until its URL is updated in step 3, and the new
  token works only after the restart in step 2, so keep the order. Nothing below puts a token in
  your shell history or on screen. The token is read and written through the package's own
  `config.load()` and `write_env`, so quoted values, `export` lines and comments in a hand-edited
  `.env` behave exactly as the server sees them.

  ```bash
  rsc() {
    env -u RESEARCH_SCAN_MCP_TOKEN -u UV_ENV_FILE \
      uv run -q --project "$HOME/Projects/research-scan" python -c "$1"
  }
  OLD="$(rsc 'from research_scan.config import load; print(load().mcp_token or "")')"
  [ -n "$OLD" ] && echo "old token captured" || echo "no token found: stop here"

  # 1. Write a new URL-safe token: atomic, every other line kept, file left 0600.
  rsc 'import secrets
  from research_scan.config import write_env
  write_env({"RESEARCH_SCAN_MCP_TOKEN": secrets.token_urlsafe(32)})'

  # 2. Restart onto it.
  launchctl kickstart -k gui/$(id -u)/org.synectic.research-scan-mcp

  # 3. Copy the new token, paste it into the connector URL in claude.ai, then clear the clipboard.
  rsc 'from research_scan.config import load; print(load().mcp_token, end="")' | pbcopy
  pbcopy < /dev/null   # after pasting
  ```

  A clipboard manager or Universal Clipboard may already have copied the token before it is
  cleared; turn those off for the paste if you use them.

  **Scrub last, in place, in the same shell.** Apart from the logs themselves and the connector
  URL until step 3, `$OLD` is the only copy of the old value. The server redacts only the token it
  booted with, so between steps 2 and 3 every connector call to the *old* URL writes the old token
  into a 401 line again — and so does any client still configured with it afterwards. Scrub once
  nothing uses the old URL. Rewrite the files through `cat >`, never `sed -i`: BSD `sed -i` swaps
  in a new file, and launchd keeps the server writing to the old, unlinked one until the next
  restart. `cat >` is safe under the live writer because launchd opens both logs append-only, so
  the server's next line lands at the new end.

  ```bash
  LOGS=(~/Library/Logs/research-scan/mcp.log ~/Library/Logs/research-scan/mcp.err.log)
  [ -n "$OLD" ] || echo "OLD is empty: stop, the scrub would match every line"
  ( umask 077   # the .scrub copies hold the rest of the request log
    for f in "${LOGS[@]}"; do
      sed "s|$OLD|***REDACTED***|g" "$f" > "$f.scrub" && cat "$f.scrub" > "$f" && rm "$f.scrub"
    done )
  grep -qF -- "$OLD" "${LOGS[@]}"
  case $? in
    0) echo "OLD TOKEN STILL PRESENT: OLD kept, fix and re-run the scrub" ;;
    1) echo "scrubbed"; unset OLD ;;
    *) echo "CHECK FAILED: a log is missing or unreadable, nothing verified; OLD kept" ;;
  esac
  ```

  `|` never occurs in a URL-safe token, so it is a safe `sed` delimiter. `OLD` is unset only when
  the check proves the scrub, so a failed run can be repeated. The old token is briefly in `sed`'s
  and `grep`'s arguments, visible to processes of the same user, who can read `.env` anyway. A line
  the server appends between the `sed` read and the `cat` write is lost, which is why the
  connector should be idle.
- **Keep the token URL-safe.** The recipe above uses `secrets.token_urlsafe`. The redaction also
  covers percent-encoded forms, but a token that never needs encoding is one less thing to trust,
  and a non-ASCII token will not authenticate as a bearer header.

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
