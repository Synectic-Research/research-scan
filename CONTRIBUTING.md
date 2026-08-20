# Contributing

Thanks for looking. This project has one unusual rule — the eval gate, below — and it is the one
worth reading before you write code.

## Development setup

```bash
git clone https://github.com/Synectic-Research/research-scan
cd research-scan
uv sync                                   # environment, including the dev group
uv run pytest -q                          # the suite; nothing here touches the network
uv tool install --editable .              # optional: research-scan on PATH, tracking the tree
```

Running an actual scan needs credentials — see `.env.example` and the README. Contributing to the
code does not: the test suite mocks every source with `respx`, and no test outside `-m live` opens
a socket.

## The quality gate

Both must be clean before you open a PR, and both run in seconds:

```bash
uv run ruff check
uv run pytest -q
```

`uv run ruff format` is the canonical formatter (line length 100). If you change `schema.py`,
regenerate the contract docs in the same commit — a test compares them:

```bash
uv run research-scan schema --md > skills/research-scan/references/schemas.md
```

## Measured or reverted

**Any change to retrieval, expansion, screening caps, or selection behavior must arrive with
golden-set eval results showing no recall regression.** A green test suite is not evidence for
these changes: the tests prove the code does what it says, not that the scan finds better papers.

```bash
research-scan eval --topic <topic> --run <run-dir> --json
```

Run it on both golden topics in `eval/golden/`, at the cheapest stage that can see your change —
`--stage candidates` is enough for anything in retrieval or expansion; a selection change needs an
emit diff against a committed run. Put the before/after numbers in the PR description.

A change that does not move a number, and does not buy something else you can name, gets reverted.
That is not a judgement about the idea — `docs/measurements.md` records several good ideas that
measured flat, and they are kept there precisely so nobody spends the afternoon again. If your
change measures flat and you still think it is right, say so in the PR and argue it; the record of
what was tried is more valuable than a tidy diff.

Two things that make this cheap rather than painful:

- Scoring at the `candidates` stage costs no agent tokens. Use it first.
- If a golden topic moves, diagnose the miss before changing anything — `docs/measurements.md`
  classifies misses as terminology gaps, query-plan variance, or cap effects, and the three want
  different fixes.

## Pull requests

- Branch from `main`, then open a PR. **`main` is never force-pushed**, and neither is any branch
  someone else may have fetched.
- One concern per commit; imperative mood; keep the subject under 72 characters.
- If your change is architectural, say what you considered and rejected. The repo documents
  reverted experiments on purpose.

## Where things live

`AGENTS.md` is the operating doctrine — boundaries the code must hold, and the open questions.
`research-scan-v1-spec.md` is the specification of record; section references like §10.4 point
there. `docs/measurements.md` is every measurement behind the current defaults, including the ones
that failed.
