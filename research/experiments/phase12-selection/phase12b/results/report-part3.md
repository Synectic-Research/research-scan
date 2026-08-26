## 6. Branch ruling

**The predefined branch triggers: G4 fails, on both G1-passing cells.** Per the slice, the
recommendation is therefore *not* further k tuning. But the probe changes what the branch should
be built as, and that qualification is the most important thing this slice learned.

**Why not more k tuning.** k is not a free parameter here — it is trapped. Below 40 the reranker
cannot see OpenScholar, LitSearch or Madrian & Shea at all (G1 fails by construction). At 40 it
sees all of them and the output becomes least stable of any arm measured (J = 0.502). There is no
k that is both sufficient and stable, because sufficiency and stability move in opposite
directions across the whole measured range.

**Why pointwise assessment does not, on this evidence, follow automatically.** The branch's premise
is that listwise reranking is *intrinsically frontier/order-sensitive* — that cross-candidate
context is contaminating the judgement. The probe tested that premise directly and it did not hold:

* between-ordering mean Jaccard **0.445** vs within-ordering **0.476** — order-induced dispersion is
  *no larger* than resampling dispersion, and slightly smaller;
* O2 and O3 move 38 of 40 rows and change which papers share a 13-row chunk, and neither shifts
  recall (means 2.0, 2.0, 2.5) nor per-golden inclusion beyond the replicate band.

Removing cross-candidate context is therefore removing something the measurement says is not the
cause. A pointwise architecture would still be exposed to the mechanism that *is*:

**The measured mechanism is score saturation at the cut.** In `t2 R40` the reranker assigns
`overall` = 3 to **19–27 of the 40 rows** it is given, against a 10-slot output, and that count
itself moves replicate to replicate (23/15/2 → 25/15/0 → 27/13/0 → 24/13/3 → 23/16/1 → 21/18/1 →
19/20/1). In **every one of the seven** runs of that cell, 2–5 rows are tied on the exact
`select.order_key` value that decides tenth place. The top-10 boundary falls inside a tie band
every time, so a one-step perturbation in any of those rows' `overall` reshuffles the output.

This is precisely the failure the slice's architect note anticipated *for the pointwise branch* —
"pointwise scoring loses comparative calibration and risks score saturation (many indistinguishable
3s)". The measurement says the **listwise reranker already has that failure**, with comparative
calibration available to it. Going pointwise removes the calibration and keeps the saturation.

**Ruling.** k tuning is ruled out. A Phase-1.4 pointwise-rerank candidate is worth carrying, but
**its discriminativeness is the gating design problem, not a flagged side risk** — and it should be
specified against the measurement in this slice: any replacement assessment must place fewer
candidates in the top band than there are output slots, or the deterministic slot-rule assembly
inherits exactly the tie-band instability measured here. Two cheaper interventions are also now on
the table and were not before, because nothing had measured the variance:

1. **A more discriminative scale at the existing listwise call** — the binding defect is a 4-point
   `overall` over a pool where more than half the rows earn the top value. This is a schema change,
   not an architecture change.
2. **Aggregation over repeated rerank samples** — the variance is per-call and, on this evidence,
   not positional, which is the condition under which resample-and-pool actually reduces it.

Neither is built here, and neither is recommended over the other without a measurement. What the
evidence does support is that the Phase-1.4 question should be framed as *"how is relevance scored
and cut"*, not *"listwise or pointwise"*.
