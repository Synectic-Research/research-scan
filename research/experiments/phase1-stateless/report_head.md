# Phase-1 stateless-screening replay — report

Replay of `research/scans/2026-08-26-claim-grounding-sonnet` (the $6.45 / 28-min / 60-turn
Sonnet-5 forked-skill run) through stateless API calls. No pipeline change: nothing under
`src/`, `skills/` or `pyproject.toml` was touched, and the saved run directory was read and
never written. `git status` is clean; everything new lives under the gitignored
`research/experiments/phase1-stateless/`.

Model for every screening and rerank call: `claude-sonnet-5` at `effort: high` — the model the
session json records (`modelUsage`) and the effort every one of the baseline's 59 assistant
turns ran at (`effort` field in the transcript). No substitution was needed.

## 1. Files created

```
research/experiments/phase1-stateless/
├── lib/common.py            pricing, spend ledger + $12 cap, prompt assembly, ScreenScore
│                            validation, `research-scan schema` shape checks
├── arm_a.py                 ARM A — baseline bookkeeping and stage cost attribution
├── screen_arms.py           ARMS B / C / D — stateless screening replay
├── rerank_arms.py           RERANK-CUT R52 / R25 / R15
├── judge.py                 independent judge (Fable 5) over the top-10 lists
├── analyze.py               measurements, recovery curves, gate verdict
├── measurements.json        every number in this report, machine-readable
├── tables.md                rendered tables (sections 2-4 below)
├── spend.json               per-call ledger, $5.09 total
├── .venv/                   anthropic 1.0.0 + jsonschema (pyproject.toml untouched)
└── arms/
    ├── A/baseline.json          scores, ≥2 set, shortlist ids, top-10 DOIs, stage attribution
    ├── {B,C,D}/                 batches/*.json, screen.json, calls.json, summary.json, run/
    ├── D/priority-order.json    the deterministic screening order
    ├── rerank/{R52,R25,R15}/    run/ (full pipeline copy), calls.json, summary.json
    └── judge/                   baseline.json, R52.json, R25.json, R15.json, summary.json
```

### How the baseline's screening+rerank share was estimated

The whole-scan $6.45 / 28 min covers plan, retrieval, expansion, verification and reporting too,
so the gate needs like-for-like. Two independent decompositions, both reported:

- **Stage clock** — `manifest.json` timestamps bracket every CLI stage exactly. The gaps between
  one CLI stage finishing and the next starting *are* the agent's screening and rerank work.
- **Turn cost** — each assistant turn in the session transcript is billed at the verified Sonnet-5
  rates and attributed to the stage window its timestamp falls in. One API request appears as up
  to three transcript rows carrying the same usage block, so rows are deduped by `requestId`;
  doing so reproduces the session json's totals exactly (output 146,359 · cache-read 13,340,895 ·
  thinking 77,635), which is what makes the split trustworthy. Attributed turns sum to $6.371 of
  the billed $6.448 (98.8%); the 1.2% residual is turns outside every stage window.

The four Sonnet-5 rates used throughout ($2.00 / $10.00 / $2.50 / $0.20 per MTok for
input / output / cache-write / cache-read) reproduce the session's `total_cost_usd` of
$6.4480633 to the cent from its own token counts, so pricing is not an assumption here.

| baseline stage | wall | cost | turns |
|---|---|---|---|
| plan | 62 s | $0.179 | 5 |
| retrieve (CLI) | 39 s | $0 | 0 |
| **screen round 1** | **767 s** | **$2.063** | 23 |
| expand (CLI) | 76 s | $0 | 0 |
| **screen expansion** | **212 s** | **$0.940** | 9 |
| coverage + shortlist (CLI) | 10 s | $0.077 | 1 |
| **rerank** | **449 s** | **$2.417** | 8 |
| verify (CLI) | 63 s | $0 | 0 |
| emit + report | 11 s | $0.112 | 1 |

**Screening share: $3.003 / 979 s. Rerank share: $2.417 / 449 s. Together $5.420 — 84% of the
whole-scan cost.** The ≤20% gate target is therefore **$0.601** for screening.

