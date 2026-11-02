## What and why

<!-- One concern per PR. Say what changes for a user, and why. -->

## Verification

- [ ] `uv run ruff check && uv run pytest -q` passes
- [ ] `schemas.md` regenerated in this PR if `schema.py` changed
- [ ] A change to a frozen default, a rubric or selection carries its before/after measurement
      (see AGENTS.md, "Defaults are frozen")
- [ ] CHANGELOG `## [Unreleased]` updated if users will notice
