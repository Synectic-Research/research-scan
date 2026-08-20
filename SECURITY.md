# Security Policy

## Reporting a vulnerability

Report security issues through **GitHub private vulnerability reporting** on this repository:
open the [Security tab](https://github.com/Synectic-Research/research-scan/security) and choose
**Report a vulnerability**. That channel is private until a fix is published.

Please do not open a public issue for a suspected vulnerability, and please do not include real
credentials in a report — a redacted log excerpt is enough.

## Supported versions

Only the latest release line is supported. Fixes land on `main` and go out in the next release;
older tags are not patched.

## What this tool touches

`research-scan` is a local-first CLI. Its whole network surface is **outbound HTTPS to scholarly
APIs** — OpenAlex, Semantic Scholar, Crossref, arXiv and PubMed/NCBI. It opens no inbound port and
listens for nothing during a scan.

- **No LLM SDK, no model calls.** The package contains no `anthropic` or other model client, and
  sends nothing to a model provider. Every judgement belongs to whatever agent drives the CLI.
- **Credentials** are read only from the process environment, `~/.config/research-scan/.env`, or a
  repo-local `./.env`, in that order of precedence. They go out only as API authentication to the
  services above. Every secret is registered for redaction before anything is logged or cached, so
  keys do not reach stage logs, run artifacts, or the HTTP cache.
- **On-disk state** is the run directory, the stage logs, and an HTTP response cache at
  `~/.cache/research-scan/http.sqlite`.

The optional MCP server can be served over HTTP (`research-scan mcp --http`, or the
`research-scan-mcp` console script), which binds a local port. It defaults to `127.0.0.1`, and
without a shared token it starts but rejects every request with `401` — health-checkable, never
silently open. Exposing it beyond loopback is the operator's decision and is outside what this
project supports; the token is a bearer secret, so anything that puts it in a URL puts it in browser
history and proxy logs. The default `research-scan mcp` transport is stdio, which binds no port and
reads no token.
