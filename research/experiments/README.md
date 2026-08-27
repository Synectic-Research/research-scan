# research/experiments — measured evidence

Frozen artefacts from the measurement arcs that decide this repo's rubric, selection and
rerank behaviour. Committed on purpose, against `.gitignore`'s default for `research/`, for
one reason: **these runs cannot be re-measured.** The stages under study are non-deterministic
by nature — the arc exists precisely because the reranker returns different top-10s from
identical calls — so a lost run is not regenerable, only re-samplable, and every gate verdict
in the reports is scored against these exact files.

## The arcs

| Directory | Arc | Narrative report |
|---|---|---|
| `phase1-stateless/` | Stateless replay — can the [A] stages be driven headlessly and reproducibly | `report.md` here; `stack-context/staging/research-scan/phase1-stateless-replay-report.md` |
| `phase11-golden/` | Golden-set validation under the current prompt | `report.md` here; `…/phase11-golden-validation-report.md` |
| `phase12-selection/` | 1.2A shortlist sweep + `phase12b/` rerank stability probe | `results/report_head.md`, `phase12b/results/report-part*.md`; `…/phase12a-shortlist-sweep-report.md`, `…/phase12b-rerank-stability-report.md` |
| `phase14/` | 1.4 rerank judgment contract — 2×2 factorial (rubric discrimination × content correction) with a fresh control | `results/tables.md`; `…/phase14-rerank-contract-report.md` |

Each arc carries its own `spend.json` (per-call cost and usage) and `measurements.json`
(the numbers the report quotes). `phase12-selection/phase12b/runs/` holds the 28 recorded
rerank runs whose `ranked.json` outputs are the input to any offline replay.

## Rules

- **Append-only.** A recorded run is never edited, re-scored in place, or tidied. A new
  analysis writes a new file; the old numbers stay quotable.
- **The report cites the file.** Any claim in a phase report must resolve to a path under its
  arc directory. A number with no artefact behind it is a self-report, not evidence.
- **Not part of the package.** Nothing here is imported by `src/`, shipped in the wheel, or
  read by the CLI. Excluding it from the sdist/wheel is `pyproject.toml`'s job, not
  `.gitignore`'s.
- **Not part of the repo gate.** This tree is excluded from repo lint (`[tool.ruff]
  extend-exclude`) and outside repo test collection (`testpaths = ["tests"]`), because it is
  append-only and never imported by `src/` — a lint or test gate here could only be satisfied
  by editing frozen artefacts. Each arc's own suite is run from its own directory by its slice.
- **`.venv/` and `__pycache__/` stay out** — the repo-level rules bind inside these trees, which
  is what keeps them to artefacts rather than environments.
