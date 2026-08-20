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
cannot publish even if you point it at a tag. Dispatch **is** the dry run; there is no flag to
flip.

Real publishing requires a tag push. To rebuild the archives locally and compare against what a
release published:

```bash
python scripts/build_plugin_assets.py --ref vX.Y.Z --out /tmp/assets
```

Same builder as CI, same bytes: it exports the tree with `git archive` and writes zip entries in
sorted order with fixed timestamps, so the hashes are reproducible from any machine.
