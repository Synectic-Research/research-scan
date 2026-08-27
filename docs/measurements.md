# Measurements

What was measured, on what, and what shipped because of it.

## How to read this file

This is the measured-or-reverted record behind the defaults. A change that did not move a number
was reverted, and the measurement that killed it is kept here rather than deleted, so the same idea
is not retried blind. If you are deciding whether to trust `research-scan`'s defaults, this is the
file that argues for them.

It was written as work happened, and it reads that way. A few conventions, so it is legible without
having been there:

- **Three numbering schemes, not one sequence.** `V1` and `V1.1` are spec milestones. `v0.2.x` are
  releases. `S0`–`S10g` are build slices — the units of work the project was cut into. A heading
  named for a slice describes what that slice measured, not a release.
- **Run slugs name an experiment, not a version.** `exp-r2-t1-capdiag` reads as: experiment, round 2,
  topic 1, cap diagnostic.
- **`§N` points at `research-scan-v1-spec.md`** in the repo root — the spec of record, kept unedited
  so these citations stay stable. `canon §N` refers to a portfolio-level convention document that is
  not part of this repo.
- **Ratification** is the golden-set's own status vocabulary. `ratified` means the maintainer has
  accepted the topic's expected-paper list as correct; `ratified-with-caveat` means accepted with a
  recorded reservation. An unratified topic's numbers are provisional.
- **Field names** (`cid`, `order_key`, `ge2`, the `xr` batch family) are defined in
  [`skills/research-scan/references/schemas.md`](../skills/research-scan/references/schemas.md).

**What the numbers do not claim.** They come from two curated golden topics. They say the defaults
beat the alternatives that were tried on those two topics; they are not a benchmark against other
tools, and no comparison against one was run.

**Where the evidence lives.** Most runs are local artefacts under `research/scans/` and are
gitignored — the numbers quoted from them are not independently checkable from this repo. Two
exceptions are committed in full: the `*-mcp-transport` runs used for the transport evidence below.
Acceptance results are committed under `eval/results/`.

**On the redactions.** Some passages describing a private project brief and a private deployment
were removed before publication and are marked inline where they were cut. Every measured number is
unchanged; nothing was re-derived, re-run or restated to fill a gap.

---

## V1 acceptance run (2026-08-19)

Two ratified-enough golden topics, each scanned end to end and then scored by an independent judge
(`claude-fable-5`, per canon §3 — a different and stronger model than the one that wrote
`ranked.json`).

| Topic | Run | recall@10 | recall@25 | `precision_ge2` (raw) | `precision_ge2_in_window` |
|---|---|---|---|---|---|
| `defaults-savings` (`ratified-with-caveat`) | `2026-08-19-s3-e2e` | 0.50 (5/10) | 0.80 (8/10) | 0.80 (8/10) | **0.875 (7/8)** |
| `llm-lit-search` (`ratified`) | `2026-08-19-topic2b` | 0.50 (3/6) | 0.67 (4/6) | 0.70 (7/10) | **0.875 (7/8)** |

Committed: `eval/results/2026-08-19-defaults-savings.json`,
`eval/results/2026-08-19-llm-lit-search.json`. Both carry the full per-rank judge scores and reasons.

**Why two precision numbers.** `emit` reserves the last two slots of the top 10 for out-of-window
classics (`selection_reason: foundational`), placed after the current work so they read as context
rather than as the answer. The judge scored them on the same "does this inform a decision the brief
names" scale as everything else — a scale a classic cannot win by construction. `llm-lit-search`
reads 0.70 raw and fails the §14.6 ≥ 0.80 target on that basis; its seven in-window packets score
7/8 and pass. `precision_ge2_in_window` is the acceptance number; `precision_ge2` still ships so the
cost of the foundational reservation stays visible rather than being quietly discounted.

**Caveat on the foundational scores.** The `judged.foundational` entries above were produced under
the pre-S5 judge prompt, which scored every packet on decision-relevance. [`eval/judge-prompt.md`](../eval/judge-prompt.md) now
scores a `foundational` packet on "canonical background a newcomer to this topic must know", and
`eval/judge.sh` passes `selection_reason` through so the judge can tell them apart. Those scores
apply from the next judge run onward; the committed ones were not re-rolled.

**What the judge found that the reranker did not** — both tracked as V1.1 items in [`AGENTS.md`](../AGENTS.md):

- `2026-08-19-topic2b` rank 7 (`e41a22d0ceac`) scored 1. Off-domain: requirements-traceability QA,
  not literature search. It reached rank 7 on a `why_it_matters` analogy the rerank rubric did not
  challenge.
- `2026-08-19-s3-e2e` rank 8 (`5ec73694904d`) scored 1. Pulled in by the `review` selection
  guarantee, which has no relevance floor — it promotes the best available review even when the best
  available is off-topic.

---

## S10f + S10g — query shape, per_query, expansion sort, arXiv (2026-08-19, overnight)

*Two build slices, measured together overnight.*

**Outcome: topic-2 candidates recall went 1/6 → 6/6 (retrieval) and 1/6 → 2/6 (expansion A/B,
LitSearch recovered), with zero loss on topic 1 at every step; both commits shipped, all gates
green.**

The changes: query rubric rewritten to 2–4 core terms (measured, biggest single win: 1/6 → 5/6),
`per_query` 20 → 40 (recovers LitLLM), pool cap scaled by built-source count (450 × n/2 — found
the hard way, see below), S2 reference ranking switched to citations-per-year with a
newest-in-window reservation (recovers LitSearch), and a real arXiv source (spec §7) wired into
cs routing and doctor.

### OpenAlex semantics (≤ 5 lines)

Docs + 6 live probes through HttpClient agree: `search=` AND-joins bare terms (stemmed, stop words
dropped) over title + abstract + **fulltext**; uppercase `AND`/`OR`/`NOT`, quoted phrases and
parentheses are fully honored (471 hits for `perovskite crispr` vs 713,299 with `OR`);
`title_and_abstract.search` is ~540× **tighter** than `search=` (154 vs 83,202 for the same
5-term query + window) — the looseness lives in the fulltext index; and `relevance_score` mixes a
citation boost into text match, structurally sinking recent zero-citation preprints.

Consequence chosen (option **a**, rubric-only — the conservative fork): semantic queries are 2–4
core terms naming one concept in the target community's vocabulary; synonym families get their own
query; keyword mode uses real Boolean. No CLI query mapping. arXiv, probed while building the
source, needed one: bare multi-word queries are effectively OR there — the source AND-joins terms
under `all:` prefixes and maps `NOT` → `ANDNOT`.

### Candidates-recall table

All `eval --stage candidates`, retrieval stage unless noted.

| Variant | Topic 2 (llm-lit-search) | Topic 1 (defaults-savings) |
|---|---|---|
| Reference runs, full pool (retrieval+expansion) | 1/6 | 8/10 |
| Baseline, retrieval-only re-run (old queries, 20/250) | 1/6 | 4/10 |
| New query shape, 20/250 | **5/6** | 4/10 (same four) |
| New shape, 30/350 | 5/6 | 4/10 |
| New shape, 40/450 | **6/6** (LitLLM at s2:Q5:36) | 4/10 |
| New shape + arXiv routed, 40/**450** | **5/6 — REGRESSION** (cap displaced LitLLM) | n/a (behavioral) |
| New shape + arXiv routed, 40/**675** (scaled cap, shipped) | **6/6** | n/a |
| Shipped defaults re-run (derived cap: t1 → 450) | — | 4/10, identical |
| Expansion A/B, old sort (reference pools + screens) | 1/6 (LitSearch cut at 40–69 of 3 seeds' refs) | 8/10 |
| Expansion A/B, **new sort** (shipped) | **2/6** — LitSearch in via s2:references ranks 27 & 22 | 8/10, same misses |
| Instructed variant: expand new-shape pool w/ reference screen | 5/6 in → 5/6 out (nothing lost or gained) | — |

Topic 1's other six goldens: four are expansion-stage finds (all preserved in the A/B), two are
pre-window classics no retrieval configuration can reach (`found_in_s3e2e: false` entries).
Pool sizes on the new shape: t2 236 → 450 → 675 (with arXiv), t1 250 → 450; abstracts 92–96%
throughout; OpenAlex cost $0.008/run at every setting (per_page is free depth).

### Shipped defaults

- **Rubric** (`plan-rubric.md` + `queries.example.json`): semantic queries 2–4 core terms, one
  concept, community vocabulary; Boolean allowed and honored in keyword mode. Example file is the
  measured topic-1 set.
- **`DEFAULT_PER_QUERY` 20 → 40**; **default cap derived**: `scaled_max_candidates(built) =
  450 × built // 2` → 450 for two sources (sweep-validated), 675 for cs's three.
  `--max-candidates` overrides. Cost: cs pools now screen at ~27 batches (was 10) — agent-side
  screening cost rises; trim with the flag if that bites.
- **S2 references ranking** (`rank_references`): two-thirds of each seed's slots by
  citations-per-year (age vs window end, min 1), one-third reserved for the newest in-window
  references, topped back up when a seed cites too few recent works. Citations stay newest-first.
  OpenAlex references fallback untouched (bare-id list; ordering it would cost a metadata fetch
  per reference).
- **arXiv source** (`sources/arxiv.py`): `search_query` with `all:`-prefixed AND-joined terms,
  `sortBy=submittedDate` desc (the deliberate recency voice — same-day listings), window applied
  client-side, arXiv-id normalisation (`…v2` stripped), synthesised DataCite DOI
  `10.48550/arXiv.<id>` so dedup merges with OpenAlex/S2 copies, category-neutral, no graph.
  Wired into `IMPLEMENTED_SOURCES` (cs → openalex, s2, arxiv now real) and doctor (probe goes
  through the source: query mapping + Atom parsing exercised). Recorded fixture + 7 tests.
  In the 675 run: 203 arxiv-only candidates, 32 merged with OpenAlex/S2 records; PaSa,
  RollingEval and ScholarQuest each gained an independent arxiv origin (an origin-count reranker
  signal), though none *depended* on it tonight. Rate limit 1 req/3 s enforced by HttpClient;
  `auth: anon` correctly recorded (arXiv takes no credential).

### Tried, not shipped

- **arXiv at the unscaled 450 cap** — routing the third source with the cap fixed displaced
  LitLLM (5/6): 869 raw hits → 281 cap-dropped. Reverted in favour of the scaled default above;
  measured back to 6/6.
- Nothing else was reverted; every other measured change met its gate.

### Forks recorded (conservative option taken)

1. **Expansion A/B setup.** Instructed: re-run expand on exp-queryshape with the reference run's
   screen.json. The new-shape pool keeps only 20/151 of the reference's screened-≥2 cids and
   2/15 of its seed list, so that setup cannot isolate the sort change. A/B ran instead on clones
   of the reference runs (retrieval-stage pool + full screen.json — literally "the same seeds
   from the reference run's screen.json", all 15). The instructed variant was also run and is in
   the table (15 seeds after re-intersection; no golden movement).
2. **exp-arxiv cap regression** — treated as in-scope for step 5 (the change would otherwise fail
   the night's no-loss gate); fixed by deriving the default cap rather than by touching per_query
   or the queries.

Experiments live under `research/scans/exp-*` (gitignored, so the runs behind this section are
not in the repo). Commits:
`10f: query shape + per_query (measured)`, `10g: expansion sort + arXiv source (measured)`.

---

## V1.1 — the coverage-driven gap round (2026-08-19)

**Outcome: topic 1 candidates recall 8/10 → 9/10 (Carroll 2009 recovered through a gap-round
paper's bibliography), topic 2 unchanged at 5/6 — gate met, shipped. Two things had to be fixed
along the way that the design did not anticipate, and both are recorded below.**

The change: `screen.json` entries gain `criteria_hit`; a new `coverage` command counts, per
sub-criterion, the papers screening kept, split by query type and source, plus per-query yield and
per-seed expansion precision; `retrieve --round 2` and `expand --round 2` run one extra
coverage-driven round against the criteria that came back thinnest.

### Candidates recall, before and after

All `eval --stage candidates`. Baseline is the reference run's own pool (retrieval + expansion);
"after" adds the gap round on an `exp-` clone of it. The clones carry a `criteria_hit` backfill
written for this measurement: every round-1 paper scored ≥ 2 attributed to sub-criteria from its
batch title and `abstract_600` — 104 papers on topic 1, 301 on topic 2.

| Variant | Topic 1 (defaults-savings) | Topic 2 (llm-lit-search) |
|---|---|---|
| Reference run, no gap round | 8/10 | 5/6 |
| Gap round, `max_outside_window` at round 1's 20 | 8/10 — **reached Carroll 2009 but capped it out** | 5/6 |
| Gap round, own out-of-window budget of 100 (**shipped**) | **9/10** — Carroll 2009 at `openalex:references:4ac4cad676f4:3` | 5/6 |

Pool growth: topic 1 359 → 503 after gap retrieval → 631 after gap expansion; topic 2 713 → 1,092
→ 1,260. Gap-round screening cost is the price: 144 new items to score on topic 1, 379 on topic 2.

**What recovered Carroll 2009.** Topic 1's gap round reformulated `Q8` (`anchoring preselected
contribution amount slider`, 20 pooled and **0** kept — its yield was the thinnest signal in
`coverage.json`) into `default contribution rate pension` and `suggested donation amounts`. The
second found *Optimal Design of Default Donations*, which scored 3, seeded the gap round's
expansion, and cites Carroll 2009 in its bibliography. No query could have retrieved Carroll
directly: it is a 2009 paper and `retrieve` **drops** out-of-window hits — only expansion tags
them. The path from "a criterion is thin" to "a pre-window classic returns" runs through
gap query → new paper → its references, and it worked.

**Topic 2 gained nothing on recall, and LitLLM stayed missing.** Its gap round targeted `C1`
(12 hits against `C4`'s 160) with `relative recall search strategy` and `search string
sensitivity`, and reformulated the lowest-yield query `Q6` into `automated related work
generation` and `literature review automation survey`. LitLLM (`2402.01788`) was not retrieved by
any of the four, and did not appear in the bibliographies of the five papers they seeded.

### Per-criterion coverage, round 1 → round 2

Counted per paper, not per origin. The round-2 column omits the gap round's *expansion* batches,
which were left unscreened in this measurement, so it is a lower bound.

| Topic 1 criterion | round 1 | round 2 | Topic 2 criterion | round 1 | round 2 |
|---|---|---|---|---|---|
| C1 enrolment effect | 66 | 70 | C1 baseline recall ceiling | 12 | **22** |
| C2 persistence and amount | 33 | 34 | C2 agentic design | 98 | 104 |
| C3 preset level anchoring | 12 | **17** | C3 benchmark construction | 63 | 66 |
| C4 consumer self-directed setting | 23 | 27 | C4 retrieval and reranking | 160 | 163 |
| C5 heterogeneity and legitimacy | 47 | 50 | C5 gains that do not hold | 53 | 54 |

Topic 2's targeted criterion nearly doubled (12 → 22) while the others moved by 1–6. That is the
mechanism doing what it is for, on the topic where the recall number did not move.

### Two findings the design did not anticipate

1. **A flat "fewer than 5 hits" threshold never fires on a real pool.** Topic 1 keeps 104 papers
   and topic 2 keeps 301; the thinnest criterion on either is 12. The absolute threshold ships
   unchanged (it is the right alarm for a small pool), but the agent-side rule now reads: target
   every criterion marked `thin` **and, when none is, the criterion with the fewest hits**. Without
   that line the gap round degenerates into "reformulate the weakest query" on every real topic.
   What `coverage.json` makes visible is the *ratio* — topic 2's C1 at a twelfth of its C4 — and
   that is the signal an agent can act on.
2. **Round 1's out-of-window budget cannot be shared with the gap round.** `rank_additions` orders
   out-of-window additions by citations per year, and a newly-reached community's bibliographies
   are led by its methodology classics: G*Power (58,916 citations), Hayes' PROCESS (48,628),
   *Judgment Under Uncertainty* (33,416). Those took all twenty slots on topic 1 and left Carroll
   2009 (685 citations, out-of-window rank 4 once the cap lifts) outside the pool. The gap round
   now gets `GAP_MAX_OUTSIDE_WINDOW = 100` of its own. Ranking out-of-window additions by
   something other than raw citation velocity is the real fix and is **not** attempted here.

### Tried, not shipped

- **Bare two-term reformulations.** Topic 1's first gap round used `default contribution rate` and
  `suggested amount anchoring`. Both are polysemous outside the brief's field: `anchoring`
  retrieved covalent-organic-framework photocatalysis and single-atom catalysts, `default`
  retrieved loan-default prediction and default-mode-network neuroimaging. Scanned from the batch
  titles, not screened — the queries were rewritten to `default contribution rate pension` and
  `suggested donation amounts` before scoring, and the measurement above uses the rewritten pair.
  The same effect hit topic 2's `search string sensitivity`, which pulled gravitational-wave and
  axion searches. **The plan rubric's "2–4 core terms" rule needs a domain-bound term when the
  concept words are IR-generic.**
- **Seeding the gap round from any paper its queries touched.** A gap query re-finds plenty of
  round-1 papers, and those carry the higher origin counts, so they won all five seed slots on
  topic 2 and the round walked bibliographies the pool already reflected. Restricted to the round's
  own *additions*, which is what the brief said and what the batch files make deterministic.
- **Choi 2001 (`10.3386/w8651`) is not reachable this way.** Removing every expansion cap
  (`--max-new 300 --max-outside-window 200`, `cap: 0` dropped) still does not surface it: the
  seeds' reference lists do not carry that NBER working-paper record. Note for the maintainer, not acted on:
  the pool *does* contain *Perspectives on the Economics of Aging* (`27753f3a0af1`), the volume
  the Choi et al. chapter appears in, under a different DOI — the golden entry carries no alias
  for it, and adding one is the maintainer's call.

---

## V1.1 — full-bibliography expansion for anchors: TRIED, NOT SHIPPED (2026-08-19)

**Outcome: the change works and buys nothing. An anchor's whole reference list does reach the
pool — LitSearch went from 30 to 41 references and 30 to 61 in-window citations, a defaults
meta-analysis from 30 to 88 references — and candidates recall moves on neither topic, because the
expansion caps cut the extra records again and the golden papers that would benefit turn out to be
blocked by something else entirely. Reverted.**

The change (reverted): in `expand.collect`, a seed carrying an `anchor` origin takes its full
reference list and full in-window citation list, capped at 100 each, bypassing
`REFERENCES_PER_SEED` / `CITATIONS_PER_SEED` (30/30) and the `rank_references` slice.

### A/B, both arms on one shared retrieval pool

Anchors were injected into `exp-` clones for the measurement only; the golden briefs stay
anchor-free, and the injected anchors are excluded from the recall numerator (they are trivially
present in both arms).

| Arm | Topic 1 (defaults-savings) | Topic 2 (llm-lit-search) |
|---|---|---|
| Per-seed slice (30/30), shipped code | 6/8 non-anchor goldens | 3/4 non-anchor goldens |
| Anchor full bibliography (100/100) | 6/8 — no change | 3/4 — no change |
| Full bibliography, expansion caps lifted | **10/10 (all goldens)** | 5/6 — no change |
| **Per-seed slice, expansion caps lifted** | **10/10, identical origins** | 5/6 |

The last row is the one that decided it. Choi 2001 arrives at
`openalex:references:f0395b76e878:19` and Carroll 2009 at `openalex:references:f9d28a450ab0:6`
in *both* lifted-cap arms, byte-identical. **Every bit of the gain is the cap, and none of it is
the anchor branch.**

### Why each topic could not move

- **Topic 1, first attempt.** Anchors `10.1257/aer.20210881` and `10.3386/w31601` have 26 and 22
  references and 15 and 5 in-window citations — *smaller than the 30-slice they were meant to
  bypass*. The arm was uninformative by construction, which is a lesson about picking anchors for
  an A/B, not a result.
- **Topic 1, second attempt.** Re-run with the defaults meta-analysis `10.1017/bpp.2018.43` as an
  anchor: references 30 → 88, exactly the intended effect. Recall still 6/8, because the 68 extra
  records are then cut by `max_new`/`max_outside_window`, which the row above shows were the real
  constraint all along.
- **Topic 2.** LitSearch's fuller graph (+42 records) does not contain LitLLM, and neither does
  anything else within reach: with `--max-new 2000 --max-outside-window 500` and `cap: 0` dropped,
  LitLLM is still absent. It is not in the S2/OpenAlex citation neighbourhood of this pool's
  seventeen seeds at all.

### What this measurement actually found

**`DEFAULT_MAX_OUTSIDE_WINDOW = 20` costs topic 1 two golden papers.** Lifting it takes the pool
from 8/10 to **10/10** — both pre-window classics the golden file marks `found_in_s3e2e: false`.
The cost is screening load: out-of-window additions go from 20 to 210 on topic 1, so a run would
screen roughly eight more batches. That is a default change with a real trade-off and it is **not**
in the three items this release scopes, so it is recorded here and in [`AGENTS.md`](../AGENTS.md) as the leading
V1.2 candidate rather than slipped in. The gap round's own `GAP_MAX_OUTSIDE_WINDOW = 100`
(shipped above) is the same finding met at a narrower scope, where its cost was one round's worth
of batches rather than every run's.

---

## V1.1 — the two rerank guards (2026-08-19)

**Outcome: both papers the S5 acceptance judge scored 1 leave the top 10, each replaced by a
golden-set paper, and every paper the judge scored 3 stays. Gate met, shipped — but only the two
guards *together* do it, and the code half alone changes nothing on either reference run.**

The changes: `rerank-rubric.md` gains an off-domain cap — a paper whose *setting* is not the
brief's setting caps at `overall` 2 unless `relevance_reason` names an explicit method transfer;
`select.py` gives the `review` guarantee a floor of `overall` 3 or `relation: closely-related`, on
top of the existing ≥ 2, and otherwise leaves the slot with the paper that won it on score.

### Three arms, top-10 diff against the committed `evidence.json`

| Arm | Topic 1 (`2026-08-19-s3-e2e`) | Topic 2 (`2026-08-19-topic2b`) |
|---|---|---|
| Before (shipped V1) | rank 8 `5ec73694904d`, judge **1** | rank 7 `e41a22d0ceac`, judge **1** |
| Code only — new `select.py`, `ranked.json` untouched | **identical, zero lines** | **identical, zero lines** |
| Code + uniform off-domain audit | rank 8 → `32831b736c11` *(golden)* | rank 7 → `fad2d47d6aa0` PaSa *(golden)* |

Nothing else moved on either run: ranks 1–7 and 9–10 are unchanged, and every judge-3 packet is
still in the top 10.

**Why the code arm is a null result, and why that is worth publishing.** Both reference runs'
guaranteed reviews already clear the new floor — topic 1's `5ec73694904d` holds `overall: 3` and
topic 2's `aac7d9e865ef` is `closely-related` — so the rule does not bind on either. The
`select.py` change is a guard against a case these two runs do not contain, and the flagged papers
were reachable only through the rubric. Publishing the zero-line diff is the honest form of that:
the code rule ships as a guard, not as a fix, and the fix is the rubric.

### The audit, and what it capped

The rubric guard cannot be applied retroactively by code, so it was applied by hand — **uniformly
over all 52 ranked entries in each run**, from the `criteria`, `relevance_reason` and `limitations`
already in `ranked.json`, with no new API calls and no re-scoring of anything else. The test, kept
deliberately narrow: cap when the entry's *own* `limitations` state the setting is not the brief's
setting **and** its `relevance_reason` argues by analogy rather than naming what carries across.
Four of 52 capped on each topic. Every one, with its reason:

| Run | cid | Why capped to 2 |
|---|---|---|
| t1 | `5ec73694904d` | social benefit take-up, not consumer product adoption; the reason asserts the headline result *is* the brief's gap — the analogy the cap exists for |
| t1 | `3b4211254cf6` | public pension scheme, not a consumer app; the reason claims its terms "map onto our constraints" without naming what maps |
| t1 | `00fa4cf93040` | health-insurance selection market with different economics; the reason offers a "mirror image", not a transfer |
| t1 | `e94addc54543` | students and exams, not consumers and money; its own limitations say the effort construct has no analogue in this product |
| t2 | `e41a22d0ceac` | requirements-traceability and Wikipedia corpora; its own limitations call GraphRAG "a proxy for citation-graph traversal, not the same thing" |
| t2 | `5e840924901f` | a single BEIR subset "far from scholarly search"; no technique named that carries |
| t2 | `37b82519b62a` | evaluated on BrowseComp-Plus rather than scholarly search; "a working fix" names no transferring mechanism |
| t2 | `562d076772cb` | heterogeneous open sources rather than scholarly corpora; points at where evaluation "should look", naming nothing that carries |

Papers that stayed at 3 despite an off-domain setting did so by naming the transfer: the 12%-default
study ("a high pre-set contribution level" — the brief's second decision), the taxi-tipping paper
("why consumers accept preset amounts"), BrowseComp-Plus ("isolates the retriever's contribution").
That asymmetry is the guard working as intended — it is not a domain filter, it is a demand that
the analogy be spelled out.

### Two things the guards exposed

1. **The review slot can legitimately end up empty.** Once topic 1's only qualifying in-window
   review was capped, the two remaining eligible reviews were both `outside_window`, and
   `_apply_guarantees` only ever considered in-window entries. So topic 1's top 10 now carries no
   `selection_reason: review` at all, and rank 8 went to the next in-window paper — which is what
   the brief asked for, and which produced a golden-set paper instead of an off-topic one.
2. **The rubric guard assumes a population/setting sub-criterion exists, and topic 2 has none.**
   Its five criteria are all about method and evidence (`baseline recall ceiling`, `agentic
   design`, `benchmark construction`, `retrieval and reranking method`, `gains that do not hold`);
   nothing names who or what is studied. The audit fell back to `brief_summary` for that topic. The
   plan rubric only *suggests* population/setting as one of five dimensions — it does not require
   it, and the off-domain cap silently depends on it. Recorded for V1.2, not fixed here.

---

## v0.2.1 — profiles, a bounded out-of-window total, a conditional gap round (2026-08-19)

**Outcome: three profiles now price the cost/recall trade-off explicitly, and measuring them found
that the V1 acceptance table was never one setting — topic 1's acceptance run was `quick`-depth and
topic 2's was `deep`. The gap-round trigger fires on both reference runs, on the relative rule and
never on the absolute one. The proposed out-of-window ranking key measured as an exact no-op and
was reverted.**

### The profile table, measured

`retrieve` then `expand` on each profile, both topics, from the reference runs' own `queries.json`
and round-1 `screen.json` (so the seed set is the intersection with each profile's pool). Pool is
the count the agent would have to screen; `per 100` is `recall_per_100_screened`, the new cost
column on `EvalResult`.

| Profile | knobs | Topic 1 pool | Topic 1 recall | per 100 | Topic 2 pool | Topic 2 recall | per 100 |
|---|---|---|---|---|---|---|---|
| `quick` | 20 / 250 / 12 · no gap round | 351 | 7/10 | **0.199** | 362 | ~~6/6~~ **4/6** | ~~0.276~~ 0.184 |
| `standard` | 40 / 450 / 20 · conditional | 565 | 8/10 | 0.142 | 570 | 5/6 | 0.146 |
| `deep` | 40 / scaled / 30 · always | 575 | **9/10** | 0.157 | 805 | 5/6 | 0.104 |

Retrieval-stage pools before expansion: topic 1 239 / 445 / 445, topic 2 250 / 450 / 675. Only
topic 2 is a three-source (`cs`) topic, so only there does `deep`'s scaled cap separate from
`standard`'s flat 450.

**`deep` buys topic 1 two papers for 224 extra screened candidates.** Choi 2001 arrives at
`openalex:references:f0395b76e878:19`, out-of-window rank 26 — inside `deep`'s 30 and outside
`standard`'s 20. That is the profile doing exactly what it is for.

**CORRECTED at v0.2.2 — `quick` does not beat `deep` on topic 2.** The 6/6 published here came
from a run in which **arXiv failed all eight queries** (`per_source.arxiv = 0 hits, 8 failed`;
29 × HTTP 429 against 6 cache hits), so it was a two-source run that happened to keep a different
mix. Re-run twice with a warm cache and arXiv clean (131 hits, 0 failed), the same profile gives
**4/6 at the same pool of 362**, reproducibly. The explanation offered above — that a narrower pool
is not a subset of a wider one — was drawn from a degraded run and is withdrawn; the corrected
table is monotone in recall, `quick` ≤ `standard` ≤ `deep` on both topics. See the v0.2.2 section.

### Which reference runs would fire the gap round

Computed from each run's round-1 coverage, at `standard`:

| Run | min hits | median | absolute rule (< 8) | relative rule (< 0.5 × median) | query rule (< 20) | fires |
|---|---|---|---|---|---|---|
| `2026-08-19-s3-e2e` | 12 (C3) | 33 | no | **yes** — 12 < 16.5 | no (thinnest query 20) | **yes** |
| `2026-08-19-topic2b` | 12 (C1) | 63 | no | **yes** — 12 < 31.5 | no (thinnest query 36) | **yes** |

Both fire, and both only on the relative rule. The absolute floor never trips on a real pool — the
same finding as V1.1's flat threshold, which is why the relative test is in the trigger at all. The
query rule did not trip either, but topic 1 came within one paper of it.

### Tried, not shipped: the out-of-window ranking key

Proposed: distinct **in-window** seeds (desc), then **log** citations-per-year. Implemented, A/B'd
against the shipped key on one fixed pool (219 out-of-window candidates from the `standard` topic-1
run, cap lifted so nothing was hidden), and **the two orderings are identical, position for
position**. Choi 2001 sits at rank 26 under both.

Neither half can move anything, for reasons visible before the run and confirmed by it:

- **`log1p` is monotone**, so as a sort key it is the same key. It could only matter if the terms
  were summed, and summing them is the hand-tuned weight vector [`AGENTS.md`](../AGENTS.md) rules out.
- **Every seed is in-window already.** `select_seeds` only ever returns in-window papers plus
  anchors, so the restriction is inert unless a user anchors an out-of-window classic — and in
  exactly that case it would demote the references of the paper the user pinned, which is the
  opposite of what anchoring is for.

Reverted. What the data does say: the top 30 out-of-window slots hold 3 papers with 4 seed links,
7 with 3 and 19 with 2. Choi 2001 has 2, so it is not buried by citation velocity — it is mid-pack
in a crowded band, and the cap, not the key, decides it. A per-seed round-robin over out-of-window
admissions (the shape `cap_round_robin` already uses for queries) is the untried idea with a reason
behind it: in the V1.1 gap round Carroll 2009 was rank **3** within its own seed's reference list
and rank 24 overall.

### The Choi 2001 alias

Added, resolved live at Crossref: `10.7208/chicago/9780226903286.003.0003`, the Choi, Laibson,
Madrian & Metrick chapter "For Better or for Worse" in *Perspectives on the Economics of Aging*
(Wise, ed., 2004) — the published version of NBER w8651, four authors matching.

The *volume* DOI `10.7208/chicago/9780226903286.001.0001` was deliberately **not** added: it is the
edited monograph, a different work, and matching a paper by its container would let any chapter of
it count as this one.

**It changes no number measured here.** In every pool where the chapter record appears, the NBER
DOI is present too, so the primary identifier already matched. The alias removes a failure mode —
a run that surfaces only the published chapter reading as a miss — rather than fixing a live miss.

### Acceptance-number bookkeeping

The V1 acceptance table at the top of this file was measured before profiles existed, and its two
runs were **not** at the same setting. From their own `retrieval.log.jsonl` `plan` events:

| Acceptance run | per_query | max_candidates | Profile it corresponds to |
|---|---|---|---|
| `2026-08-19-s3-e2e` | 20 | 250 | **`quick`** depth and cap (out-of-window cap was 20, i.e. `standard`'s) |
| `2026-08-19-topic2b` | 40 | 675 | **`deep`** (three sources scaled) |

So `llm-lit-search`'s 0.50 / 0.67 / 0.875 are `deep` numbers, and `defaults-savings`'s
0.50 / 0.80 / 0.875 are `quick`-depth numbers that happened to hold a `standard` out-of-window cap.
Eval results are keyed by profile from v0.2.1 (`<date>-candidates-<topic>-<profile>.json`) so this
cannot silently recur, and `EvalResult` now carries `profile`, `pool_size`, `wall_clock_s` and
`recall_per_100_screened` alongside recall.

---

## v0.2.2 — the two-profile collapse, measured and rejected (2026-08-19)

**Outcome: the candidate `standard` (20 / 250 / 12 + the gap trigger) misses the decision rule on
both topics and on both terms — recall 7/10 and 4/6 against a bar of 8/10 and 5/6, at pools of 521
and 619 against a bar of 420. Three profiles stay. The same measurement caught a wrong number in
the v0.2.1 table and corrected it.**

### The decision

Rule: candidate-`standard` recall ≥ current `standard` on both topics (T1 ≥ 8/10, T2 ≥ 5/6) with
pool ≤ 420.

| Stage | T1 pool | T1 recall | T2 pool | T2 recall |
|---|---|---|---|---|
| Candidate knobs, before the gap round | 351 | 7/10 | 362 | 4/6 |
| Gap trigger | fires — C3 at 11 vs median 32 | | fires — C1 at 8 vs median 34 | |
| Gap round, after retrieval | 459 | — | 524 | — |
| **Candidate `standard`, final** | **521** | **7/10** | **619** | **4/6** |
| Bar | ≤ 420 | ≥ 8/10 | ≤ 420 | ≥ 5/6 |
| Verdict | **fail** | **fail** | **fail** | **fail** |

**Why recall cannot move, structurally.** The out-of-window cap is a total for the run (v0.2.1), so
round 1's expansion spends all 12 slots and `expand --round 2` reports `out: 0` on both topics —
measured, not inferred. Every paper topic 1 is still missing is pre-window (Thaler & Benartzi 2004,
Choi 2001, Carroll 2009) and `retrieve` drops out-of-window hits, so with no out-of-window budget
left there is no path by which the gap round could return one. The gap round can only add in-window
papers to a topic whose remaining misses are all classics.

**Why the pool cannot stay under 420.** The gap round is three extra queries at `per_query` 20
across two or three sources, then an expansion pass: +108 then +62 on topic 1, +162 then +95 on
topic 2. A cheap round is still 170–257 candidates of screening, which is most of a `quick` pool
again. The bar was 420; the cheapest thing the gap round can cost put both topics past it.

**What this says about the design.** `standard`'s value is not its query depth — the candidate
matched `quick` on depth and still failed. It is the **out-of-window budget of 20**, which is what
separates 7/10 from 8/10 on topic 1. Collapsing the profiles to two would have had to keep that
number, and then it would not have been the quick knobs. The three profiles are three points on
one curve — 12, 20 and 30 out-of-window slots — and the middle one is load-bearing.

### Corrected profile table (all runs verified source-clean)

Every run below reports `failed: 0` for every routed source. The topic-2 `quick` row replaces the
v0.2.1 number, which came from a run with arXiv dead.

| Profile | knobs | T1 pool | T1 recall | T1 per 100 | T2 pool | T2 recall | T2 per 100 |
|---|---|---|---|---|---|---|---|
| `quick` | 20 / 250 / 12 · no gap round | 351 | 7/10 | **0.199** | 362 | 4/6 | **0.184** |
| `standard` | 40 / 450 / 20 · conditional | 565 | 8/10 | 0.142 | 570 | 5/6 | 0.146 |
| `deep` | 40 / scaled / 30 · always | 575 | **9/10** | 0.157 | 805 | **5/6** | 0.104 |
| *candidate `standard`* | *20 / 250 / 12 · conditional* | *521* | *7/10* | *0.134* | *619* | *4/6* | *0.108* |

Recall is monotone in the profile on both topics, and `recall_per_100_screened` falls as the pool
grows — which is what a cost dial should look like. The candidate profile is the worst row in the
table on efficiency for topic 1 and topic 2 alike: it pays the gap round's screening bill and buys
nothing with it.

### A measurement-hygiene finding, and a correction

The v0.2.1 topic-2 `quick` number (6/6, and the "quick beats deep" claim built on it) came from a
degraded run. `manifest.retrieval.per_source` recorded it plainly — `arxiv: 0 hits, 8 failed`
against 29 × HTTP 429 — and it was not read before publishing. Two clean re-runs agree at **4/6**.

The tooling was already telling the truth; the process was not reading it. From here, a measured
run is not quotable until `per_source[*].failed == 0` for every routed source. The manifest has
carried `failed` since S1 and `auth` since the topic-2 diagnostic, so this costs one line of
checking, not a feature.

Nothing else in the v0.2.1 table changed: topic 1 routes no arXiv and every other run was clean.

### Wall clock

CLI time is not the cost. With a warm cache the whole chain is seconds — retrieval 0.3–2.2 s and
expansion 7–16 s at every profile, and OpenAlex bills $0.008 a run at all three. What a run costs
is the agent reading the pool: the one end-to-end run with a recorded `wall_clock_s` is
`2026-08-19-topic2b` at **2,230 s (37 min) for a 593-paper pool**, or roughly 3.8 s per candidate
screened. That ratio is the honest basis for the README's bands, and it makes the profile table a
time table: ~350 candidates ≈ 22 min, ~570 ≈ 36 min, 805 ≈ 51 min.

---

## v0.2.3 — per-seed round-robin for out-of-window admissions: MEASURED AND REVERTED (2026-08-19)

**Outcome: the pool held identical at all six cells, topic 2 did not move at any profile, and
topic 1 lost three golden papers at every profile — 7/10 → 4/10, 8/10 → 5/10, 9/10 → 6/10.
Condition (2) fails; reverted. The candidate was V1.2 #1 and the measurement refutes it in exactly
the case that motivated it.**

The change (reverted): out-of-window admissions filled one seed at a time, best rank within that
seed first — §8.4's `cap_round_robin` shape, keyed on `seed_id` instead of `query_id`. In-window
expansion ordering was untouched.

### Source health, every run quoted below

`manifest.retrieval.per_source[*].failed`, printed per run before the numbers were read:

| Run | openalex | s2 | arxiv |
|---|---|---|---|
| t1 quick / standard / deep | 0 / 0 / 0 | 0 / 0 / 0 | not routed (behavioral) |
| t2 quick / standard / deep | 0 / 0 / 0 | 0 / 0 / 0 | **0 / 0 / 0** |

### The profile table, before and after

Both arms on the *same* retrieval pool: `retrieve` re-run to reset, then `expand` under each
version of the code. The before column reproduces the v0.2.2 table exactly, which is the harness
checking itself.

| Profile | T1 pool | T1 recall | T1 per 100 | T2 pool | T2 recall | T2 per 100 |
|---|---|---|---|---|---|---|
| `quick` before | 351 | 7/10 | 0.199 | 362 | 4/6 | 0.184 |
| `quick` **after** | **351** | **4/10** ❌ | 0.114 | **362** | 4/6 | 0.184 |
| `standard` before | 565 | 8/10 | 0.142 | 570 | 5/6 | 0.146 |
| `standard` **after** | **565** | **5/10** ❌ | 0.089 | **570** | 5/6 | 0.146 |
| `deep` before | 575 | 9/10 | 0.157 | 805 | 5/6 | 0.104 |
| `deep` **after** | **575** | **6/10** ❌ | 0.104 | **805** | 5/6 | 0.104 |

**Condition (1) holds exactly.** Pool is identical in all six cells, by construction: the policy
decides *which* papers fill the budget, never how many, and a unit test pins
`len(admitted) == min(len(candidates), limit)` across five limits. **Condition (3) holds** — every
routed source reported `failed: 0`. **Condition (2) fails on topic 1 at all three profiles.**

Topic 2 is flat because its remaining misses (PaSa, LitLLM) are in-window arXiv preprints, and this
policy only governs out-of-window admissions. It neither confirms nor refutes anything.

### Which papers moved, and why

Three golden papers left the pool at every topic-1 profile: **Madrian & Shea 2001** (`10.3386/w7682`),
the **defaults meta-analysis** (`10.1017/bpp.2018.43`) and **Chetty 2014** (`10.1093/qje/qju013`)
at `quick`. The single decisive case, from the 219-paper out-of-window set of the `standard` run:

| Paper | seed links | best rank in a seed | global position | admitted before | admitted after |
|---|---|---|---|---|---|
| Madrian & Shea 2001 | **4** | 3 | **1** | yes | **no** |
| Chetty 2014 | 2 | 1 | 14 | yes | yes |
| Choi 2001 | 2 | 17 | 26 | no | no |

Madrian & Shea is the most-cited-by-seeds paper in the entire out-of-window set and round-robin
drops it, because every seed's rank-0 paper is admitted before any seed's rank-3 paper and the
budget of 20 runs out first. The admitted sets tell the same story in one line:

- **before** — seed links `[4,4,4,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2,2,2]`: every admission is cited by
  at least two seeds.
- **after** — `[3,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]`: sixteen of twenty are cited by exactly
  one seed.

And the diversity it was supposed to buy barely materialised: distinct seeds represented went from
**10 to 11**, out of 15. The policy traded the entire centrality signal for one extra seed.

### Why the V1.2 candidate was wrong

The hypothesis came from the V1.1 gap round, where **every** out-of-window candidate had exactly
one seed link. With the seed-count term inert, the global sort degenerates to pure citation
velocity, which is what buried Carroll 2009 at rank 24 while it sat at rank 3 of its own seed's
list. That observation was correct and it does not generalise: the gap round expands from 5 fresh
seeds, round 1 expands from 15, and in the round-1 pool the seed-count term is the load-bearing
part of the key. A classic that four of your fifteen seeds all cite is precisely the classic the
brief wants, and "cited by four seeds" is a better relevance signal than "rank 3 in one seed's
bibliography".

Stated generally, and this is the part worth keeping: **fair-share admission helps when the
producers are interchangeable and hurts when agreement between producers is itself the signal.**
Queries are interchangeable — §8.4's round-robin over them is right, and stays. Seeds are not:
they are all drawn from the same screened-relevant set, so overlap between their bibliographies
means consensus, not redundancy.

### What is still open

Only the narrow case: out-of-window admission **in the gap round**, where the seed set is small and
fresh and every candidate carries one link. Splitting the policy by round would mean two admission
rules for one budget, which is more mechanism than the evidence justifies — the gap round can
already reach its classics when the budget has slots left (`deep`), and v0.2.2 showed the budget,
not the ordering, is what binds. Left alone.

---

## Reframe — skill trigger check (2026-08-19)

**Outcome: 12/12. Every should-trigger prompt invoked the skill and every should-not-trigger prompt
left it alone, against the reframed description.** Documentation and rubrics only — no default, cap,
selection rule or eval metric changed, and no number above was touched.

The skill's contract is now "the 5–10 recent papers with the highest impact on a research question,
topic, or project", judged through a purpose (`build` / `research` / `orient`) the brief declares or
the planner infers. The `description` is the trigger surface, so the reframe is only worth anything
if it actually routes the questions it now claims. Method and caveats in [`tests/skill_triggers.md`](../tests/skill_triggers.md).

| # | Purpose | Prompt | Expected | Result |
|---|---|---|---|---|
| `b1` | build | We're about to build a round-up savings feature in a banking app. What should we know before we design the opt-in flow? | trigger | **invoked** ✅ |
| `b2` | build | Kicking off a project on agentic code review — has this been done, and what would change how we build it? | trigger | **invoked** ✅ |
| `r1` | research | What's the strongest recent evidence that default enrolment affects how much people actually save? | trigger | **invoked** ✅ |
| `r2` | research | What has been published on LLM agents for literature search since 2024? | trigger | **invoked** ✅ |
| `r3` | research | Is the evidence contested on whether GraphRAG beats vector RAG for multi-hop questions? | trigger | **invoked** ✅ |
| `r4` | research | What's the closest prior work to using citation-graph traversal to expand a literature search? | trigger | **invoked** ✅ |
| `o1` | orient | I'm new to mechanistic interpretability. What are the papers I need to know, recent first? | trigger | **invoked** ✅ |
| `o2` | orient | Map the field of automated systematic review for me — the main sub-areas and the key papers. | trigger | **invoked** ✅ |
| `n1` | — | Format these three references in APA for my manuscript. | no trigger | **no** ✅ |
| `n2` | — | Find the DOI for 'Attention Is All You Need'. | no trigger | **no** ✅ |
| `n3` | — | What's the current pricing for the Anthropic API? | no trigger | **no** ✅ |
| `n4` | — | Why is my pytest fixture not being found from a subdirectory? | no trigger | **no** ✅ |

**8/8 should-trigger prompts invoked the skill; 4/4 should-not-trigger prompts
left it alone.** No prompt landed in the `named` state: every session either called the skill or never
mentioned it. The sweep cost $5.57 across 12 sessions.

The four research phrasings are the interesting column: "strongest recent evidence", "published
since 2024", "is the evidence contested", "closest prior work" are the questions the old
design-centric description did not name, and all four invoked. The `orient` pair invoked with
sensible arguments too — `o1` passed "highest-impact recent papers a newcomer needs to know".

**This is one run of each prompt, not a gate.** Invocation is model-sampled; a cell could flip on a
re-run. It measures the description's reach, nothing about scan quality and nothing about whether
the planner infers purpose correctly.

### A harness finding worth keeping

**A forked skill's own `allowed-tools` beats the parent session's restrictions.** The probes were
meant to record the invocation without letting a scan run. Neither mitigation worked:

| Attempt | Result |
|---|---|
| `--max-turns 2` | fork reported `num_turns: 4`; ran `doctor`, `init` and a full retrieval |
| `--disallowed-tools Bash` | fork still ran the CLI — it honours the skill's `allowed-tools: Bash(research-scan *)` |
| `PATH` shimmed to exclude `research-scan` | fork's Bash re-initialises from the user profile, restoring `~/.local/bin` |

So a trigger probe against a forking skill costs a real scan per hit. Two probes wrote populated run
directories (450 candidates each) before this was understood. The only mitigation that held was the
one chosen up front: **run every probe from a scratch working directory**, so the artefacts landed
outside the repo and no measurement was contaminated.

---

## v0.2.5 — the contradicting reserve: N slots, keyed on `relation` (2026-08-20)

Two changes, shipped as two commits because only the second changes what the guarantee means.
Commit 1 makes the reserve hold N slots instead of one; commit 2 moves the question "is the reserve
already full?" from `flags.contradicts` to `relation: contradicting`.

### The signal-rate table — why the guarantee had effectively never fired

`flags.contradicts` ("contradicts a premise of the brief") and `relation: contradicting` ("pushes
against a premise the brief states") are near-identical in the rerank rubric, and the reranker sets
them at very different rates. Counted over the committed runs:

| Run | emitted `flags.contradicts` | emitted `relation` | pool flag | pool relation |
|---|---|---|---|---|
| `2026-08-19-s3-e2e` (golden 1) | 5 | **0** | 18 | 2 |
| `2026-08-19-topic2b` (golden 2) | 6 | 2 | 19 | 8 |
| `2026-08-19-topic2` | 7 | 2 | 19 | 11 |
| `2026-08-19-headless-proof` | 2 | 1 | 21 | 7 |
| `2026-08-18-s1-smoke` | 3 | 0 | 5 | 0 |
| an internal project brief (external) | 4 | **0** | 13 | 5 |

[internal topic details removed for publication — measurements unchanged]

The flag runs 3–9× the relation. Since satisfaction was counted on the flag, almost every run
arrived at `_apply_guarantees` already "satisfied" by papers that answer the brief and incidentally
push back on one premise — so the slot meant for papers that argue with the brief was never
actually reserved. That is the defect; N slots keyed on the flag would have inherited it.

### A/B, commit 1 (N slots, default 1): zero-diff

`select()` re-run in-process over every committed run that still has its pool, compared on
`(rank, cid, selection_reason)` plus the alternates list. **21 runs identical**, both golden topics
included. 11 `exp-anchor*` runs skipped — their `ranked.json` references cids no longer in
`candidates.json`. Three runs (`exp-r2-t1`, `exp-r2-t1-capdiag`, `exp-trigger-t1`) differ, and
differ **identically at HEAD**: they predate the V1.1 review floor.

One regression this A/B caught that the suite did not: protecting *every* guaranteed pick from
displacement reversed emit's standing precedence on `2026-08-19-headless-proof2`, where `--top 3
--foundational 2` leaves one main slot and the counter-result has always taken it from the review.
553 tests passed with that bug in place. Displacement is two-tier now — a pick the ordering made,
else another guarantee's, never its own.

### A/B, commit 2 (relation keying): zero packets change, for two different reasons

Same 21 runs, same comparison. **No packet, rank or `selection_reason` changes on any run.** The
only differences are the alternates *ordering* on the same three pre-existing runs above — same
cids, different order.

The prediction going in was that golden topic 1 would move (2 relation-contradicting in pool, 0
emitted). It does not, and the reason is worth recording:

| Run | relation-contradicting in pool | why the reserve stays put |
|---|---|---|
| `s3-e2e` | 2 | **both are `outside_window`.** The guarantee draws from in-window only; those two are pre-window classics the foundational slots serve. No in-window counter-evidence exists to promote. |
| `topic2b` | 8 | **2 are already emitted**, so a reserve of 1 is satisfied — on the honest signal this time, not on incidental flags. |
| `topic2` | 11 | same: 2 already emitted. |

So the keying is semantically real and empirically inert on this corpus **at a reserve of 1**. Its
effect appears when the reserve is raised, or on a run whose counter-evidence is in-window and
outranked. Per the ship conditions, the judge gate covers "runs whose top-10 changed" — none did,
so no re-judge was rolled and no `precision_ge2_in_window` number moves. Nothing here is comparable
against the committed judge scores anyway; the judge prompt has changed twice since they were
rolled.

### The external case the change was built for

An internal project brief (a kickoff scan, outside this repo) names a counter-result to one of its
premises as an open question, and four papers scored `overall` 3 with `relation: contradicting`.
[internal topic details removed for publication — measurements unchanged]
All four lost `order_key`, sitting at positions 30, 31, 32 and 34 of 44 in-window, because
arguing against one premise scores on one sub-criterion while answering the brief scores on four.
Before the keying, `--contradicting 4` on that run was inert: four emitted papers carried the flag,
so the reserve read as full. After it, the same run promotes counter-evidence on the honest signal.

**`order_key` is not wrong and the reranker is not wrong.** A narrow paper that refutes a premise
*should* score below a broad paper that answers the brief; the guarantee is the right place to
correct for it, which is why nothing about the ordering moved.

Caveat on that row: this run's pool was widened by hand before the measurement (`shortlist` re-run
at `--max-in-window 130`, `ranked.json` 46 → 50) to get the four counter-results reranked at all,
so four of its five relation-contradicting entries were added by the same person reading the
result. The fifth was not, and it is the interesting one — see below.

### Post-ship verification on that run

| `emit` invocation | counter-results emitted | what it costs |
|---|---|---|
| defaults (`--top 10 --contradicting 1`) | **1** | nothing; the guarantee fires where before it did not |
| `--top 10 --contradicting 4` | 4 | displaces 4 of the page's best answers, incl. rank 5 |
| `--top 14 --contradicting 5` | 5 | pays in slots rather than in answers; the run's final state |

At the shipped default the guarantee promotes exactly one paper — and it is **not** one of the four
that motivated the change. It is a fifth, which the original scan had itself reranked
`relation: contradicting` and which the ordering had cut.
[internal topic details removed for publication — measurements unchanged]
The keying surfaced a counter-result that was in the pool all along, which is the
cleanest evidence that the old satisfaction test was measuring the wrong thing.

### A wrinkle worth knowing before raising the default

At `--contradicting 5` the reserve displaced a review the brief names.
[internal topic details removed for publication — measurements unchanged]
It had arrived on **merit**, so the review guarantee saw
`flags.review` among the picks, counted itself satisfied and claimed no protected slot — and the
two-tier rule only protects picks a guarantee *made*. A review that earns its place is therefore
displaceable by counter-evidence, while a weaker one promoted by the guarantee is not.

Not fixed here: it is the cross-guarantee twin of the self-eviction bug, it is unmeasured, and the
obvious fix collides with the precedence deliberately preserved in commit 1 (with one main slot the
counter-result takes it from the review). Logged for V1.2 alongside the rubric-signal defect.

---

## MCP transport evidence — claude.ai over Streamable HTTP (2026-08-20)

**These are transport / integration runs. They are never quotable as golden-set retrieval
measurements** — no `failed: 0` source check was made, `eval` was not run against a golden topic,
and the harness is a different one (a claude.ai client over Streamable HTTP, not the local skill).
Nothing in this section is a statement about the engine's recall or precision.

Both runs drove the frozen pipeline from a plain claude.ai conversation through the MCP adapter
over Streamable HTTP at `e6730602e326a86cf8e25713168404367513859f` (tagged `v0.4.0` — the tag ran
ahead of the package version, which the changelog records). That commit and that tag belong to the
pre-publication private history and are not reachable in this repository; the CHANGELOG's v0.5.0
note records why. The skill's own rubrics drove every judgement rather than the model improvising
them. Server started 2026-08-20 12:10:13, twelve seconds after that commit; the working tree was
clean and both scans opened later. Artifacts under `research/scans/*-mcp-transport/`.
[deployment details removed for publication — measurements unchanged]

| | scan 1 | scan 2 |
|---|---|---|
| `scan_id` | `a2b2044a-4f4c-4744-ba1a-2b525b68f18b` | `7e03448b-2a2e-4a8e-991b-0138847a476b` |
| profile | `quick` | `quick`, gap round forced |
| tool calls | 23 | 36 |
| timeouts | 0 | 0 |
| retries | 0 | 0 |
| `in_progress` / `queued` | 0 | 0 |
| retrieved → deduped | 428 → 250 | 623 → 542 |
| screened ≥ 2 | 148 | 252 |
| shortlisted / ranked | 47 / 47 | 49 / 49 |
| verified | **47 / 47** | **49 / 49** |
| emitted | 10 | 10 |
| wall clock | 1210 s | 1479 s |

Call sequence, from the server's own log — one line per tool call, no interleaving, no repeats:

```
scan 1  scan_start → scan_continue ×14 (screen) → scan_continue ×6 (rank) → scan_verify → scan_result
scan 2  scan_start → scan_continue ×14 (screen) → scan_continue ×1 (gap)
                   → scan_continue ×12 (screen) → scan_continue ×6 (rank) → scan_verify → scan_result
```

### Acceptance criteria

| Criterion | Result |
|---|---|
| Skill package loads in claude.ai and its rubrics drive the scan | pass |
| MCP tools selected over native web search | pass |
| Loop continuity — every `next_action` followed to `complete` | pass (23 and 36 calls, no gaps) |
| Model artifacts accepted without a schema fight | pass (no `invalid_artifact` in either run) |
| No unrecoverable timeout | pass (0 timeouts, 0 retries, 0 busy envelopes) |
| Verified top 10 delivered | pass (47/47 and 49/49 verified, 10 emitted each) |

### The gap round, scan 2

`force_gap_round` was passed to `scan_start`, persisted in `mcp-options.json` and applied when
`coverage` ran — `coverage.json` records `forced: true`, reason `--gap-round was passed`. The
`write_gap_queries` boundary was reached, the model wrote four round-2 queries, and the pipeline
carried them through `retrieve --round 2` and `expand --round 2`.

| id | type | target | text |
|---|---|---|---|
| G1 | `gap` | C2 baseline search recall | `database coverage overlap` |
| G2 | `gap` | C2 baseline search recall | `supplementary citation searching` |
| R1 | `review` | — | `literature review automation survey` |
| R2 | `review` | — | `survey deep research agents` |

The gap round put **77 additional papers over the screening threshold** — `coverage.json` records
`ge2` 175 after round 1 and 252 after round 2, scored by the existing screening rubric. That is a
count of what the model scored ≥ 2, **not** a claim that 77 papers are relevant: no ground truth was
consulted, and screening precision is exactly what this run does not measure.

Of the papers the gap round **added to the pool** (the `r` and `xr` batch families — 280 candidates),
**9 reached the ranked set and 1 reached the top 10** (rank 8, *Deep Research: A Systematic Survey*).
Counting instead every ranked paper carrying a round-2 *query origin* — which includes papers round 1
had already found — also gives 9; the union of the two definitions is 11 ranked and 2 in the top 10
(adding rank 7, *Lacuna: A Research Map for Machine Learning*). The scan's own closing self-report
said 4 ranked and 2 in the top 10; the "2 in the top 10" reproduces under the union definition, the
"4" reproduces under none of the three and is recorded here as unexplained. Derive these counts from
the artifacts, not from the report.

---

## Phase 1.x — stateless screening, the shortlist order, and the rerank contract (2026-08-26 → 2026-08-27)

A four-arc measurement programme asking whether the judgement stages could be driven by stateless
API calls instead of a conversation, and — once that turned out to be the wrong question — where a
scan actually loses good papers. It closed at **Outcome C**: the reranker is frozen, no rubric or
reranker change ships, and the one selection defect it found is fixed in v0.6.0.

Everything below cites an immutable `SHA:path` under `research/experiments/`, which is committed
and append-only. **MEASURED and PROJECTED are separated on purpose, and the separation is the
point**: the wall-clock and cost figures are real measurements of *one stage*; the full-scan
figures are arithmetic over those parts and have never been run end to end as a default path.

### MEASURED — screening, on the recorded baseline run

Replay of `research/scans/2026-08-26-claim-grounding-sonnet` (a $6.45, 28-minute, 60-turn Sonnet-5
run) through stateless calls. Same model, same effort, same batches, same rubric; the saved run
directory was read and never written
(`552f09c462dce07a7c20fa3f30e85c3264f42346:research/experiments/phase1-stateless/report.md`,
`552f09c462dce07a7c20fa3f30e85c3264f42346:research/experiments/phase1-stateless/measurements.json`).

| | baseline (conversational) | arm B — stateless, sequential, thinking on | arm C — stateless, parallel, thinking off |
|---|---|---|---|
| screening wall clock | 979 s | 960.9 s | **72.6 s** (13.5×) |
| screening cost | $3.003 | $1.300 | **$0.757** |
| candidates scored | 572 | 572 | 572 |
| schema-valid `screen.json` | — | yes | yes |
| binary ≥ 2 agreement with the baseline | — | 89.5% | 83.0% |
| exact score agreement | — | 73.1% | 60.3% |
| papers kept at ≥ 2 | 187 | 135 | 90 |

**The same arc failed its own pre-registered gate, and that is not a footnote.** Arm C's cost was
25.2% of the baseline screening share against a ≤ 20% target, binary agreement 83.0% against
≥ 95%, exact agreement 60.3% against ≥ 80% — three FAILs
(`552f09c462dce07a7c20fa3f30e85c3264f42346:research/experiments/phase1-stateless/report.md` §4).
Concurrency, not statelessness, is
the speed lever: arm B is stateless too and takes essentially the baseline's wall time. Thinking is
the entire cost difference and buys about seven points of binary agreement.

The rerank arms are the one place a pre-registered fallback passed: top-10 DOI overlap was 5/10 for
every cut depth (FAIL), while an independent Fable-5 judge scored **1.00 in-window precision on all
four lists**, with the two cheapest cuts scoring a higher mean relevance than the baseline. Two good
lists drawn from a pool of near-equivalent 3s, not one good and one bad.

**That fallback cannot stand alone, and is not treated as if it could.** The judge rates the papers
a list actually contains, so it measures precision and is blind to the paper that was never
selected — a list of ten strong papers and a list of ten strong papers missing the one that mattered
score the same. Recall is what the golden set is for, and no judge score substitutes for it: a
judge pass beside a recall FAIL is a reason to keep measuring, never a reason to ship.

### MEASURED — where the golden topics actually lose papers

Two live end-to-end golden scans through the stateless driver, nothing changed to fix anything
(`552f09c462dce07a7c20fa3f30e85c3264f42346:research/experiments/phase11-golden/report.md`,
`552f09c462dce07a7c20fa3f30e85c3264f42346:research/experiments/phase11-golden/measurements.json`).
Of the 13 golden papers the two
runs failed to emit: **1 was lost at screening, 4 were never retrieved, and 8 were lost downstream**
— at the shortlist cap, the rerank cut, or the reranker's own ordering. Put the other way round:
of the **12 golden papers the two runs retrieved, 11 were retained** by screening at ≥ 2. Screening
is not the loss stage. That is the finding that redirected the rest of the programme.

### MEASURED — the shortlist ordering defect (shipped in v0.6.0)

An offline sweep of three orderings × five caps over six frozen inputs — both golden topics, both
eras, and the two V1-acceptance control runs swept twice (as recorded, and with the `p-standard`
attribution overlay), 90 recomputations, zero model calls
(`552f09c462dce07a7c20fa3f30e85c3264f42346:research/experiments/phase12-selection/results/report_head.md`,
`…/results/report_tail.md`, `…/results/sweep.json`). The sweep's control arm reproduces each run's
recorded `shortlist.json` cid-for-cid, so it recomputes the shipped code rather than resembling it.

The shipped key was `score DESC, origin_count DESC, date DESC`. In a real pool the first two tiers
tie in large bands, so date was the only discriminator left and **the cap ran as a recency filter**:
on `p11-t2` the 54 score-3 candidates split 7/16/31 by origin count, and the 31 single-origin 3s
were ordered by age alone — OpenScholar (2024-11-21) at rank 52 and LitSearch (2024-07-10) at rank
54, the two oldest, both cut at 40. On the pre-v0.4-era control run `2026-08-19-topic2b`,
OpenScholar sat at rank 90 of a 289-strong population and was cut at 40, 60 and 80. It is a latent
defect, not something the stateless screen created.

Golden survival into the rerank frontier, pooled over both stateless topics (11 goldens scored ≥ 2):

| ordering | @40 | @60 | @80 | @120 |
|---|---|---|---|---|
| shipped (T0) | **8/11** | 10/11 | 10/11 | 10/11 |
| T1 | **10/11** | 10/11 | 10/11 | 10/11 |

10/11 is the finite maximum; the shipped order at the shipped cap is the unique loser. T1 —
`score DESC, criteria_supported DESC, origin_count DESC, best_retrieval_rank ASC, date DESC` —
recovers both papers **at cap 40**, with no cap change, no weights, and no extra rerank tokens. A
stratified per-criterion reserve (T2) was swept alongside it and is a pure no-op on all six inputs
at every cap, so the simpler policy shipped. v0.6.0 adds `cid ASC` as a terminal tier to make the
order total; on the same six inputs that moves 4 rows, every one inside a fully tied band, with
shortlist membership at the shipped caps unchanged
(`1fd1465f413c21104d7af3710ed219ce595ca49a:research/experiments/phase12-selection/results/src-t1-replay.json`).

**This measurement makes no recall claim.** Every paper beyond the original cap of 40 was never
reranked, so no simulated recall@10 was computed for any configuration, and none is reported.

### MEASURED — the reranker, and why it is frozen

Phase-1.2C replayed the 28 recorded rerank runs under every deterministic tie-break ladder over the
recorded features. Some ladders rescue individual papers inside a tie band, but none meets both the
recall and the stability bar on both topics — `winner_restores_stability_and_worst_run_recall:
false` — and on the frontier the architecture actually runs, `defaults-savings/R40`, **all 18 misses
are SCORE-LOSS**: the golden's `overall` is strictly below the boundary row's, so no ladder
beginning with `overall DESC` can reach it, by construction. Deterministic selection was exhausted
there (`23d7c360590e4d44db986812c390d9026ede9a13:research/experiments/phase12-selection/phase12c/results/tables.md` §5,
`…/results/ruling.json`).

Phase-1.4 then ran the judgement itself: a 2×2 factorial (rubric discrimination × content
correction) against a **fresh** five-replicate control, both topics, 39 live runs
(`232effc2bb540526d046449e0700e039e0d2c12a:research/experiments/phase14/results/tables.md`,
`232effc2bb540526d046449e0700e039e0d2c12a:research/experiments/phase14/results/ruling.json`).
No cell cleared the pre-registered
bar on both topics — the strongest cell gained +2.2 mean recall@10 on `defaults-savings` and lost
0.4 on `llm-lit-search`. `adopted_factors: []`. **Outcome C — freeze the current reranker.** Its
own README states the consequence: failure does not authorise another tuning slice. The one
experiment that may reopen it, and the hard kill rule that would end it, are recorded in
[#3](https://github.com/Synectic-Research/research-scan/issues/3); the screening-strictness
finding is parked in [#2](https://github.com/Synectic-Research/research-scan/issues/2).

So the position after Phase-1.4 is this, and it is deliberately a negative one. The reranker is
frozen. Deterministic selection over the recorded features is exhausted on the frontier the
architecture runs. Generic rubric changes did not generalise across both topics, and the ones that
helped one hurt the other. The LLM judge is precision-oriented and cannot gate recall on its own.
And end-to-end non-inferiority for the stateless path is undemonstrated — not refuted, undemonstrated
— which is why the driver ships repo-only and the promotion bar below is written down.

### PROJECTED — not measured, not demonstrated

| | measured baseline | projected, arm C + the R15 rerank cut |
|---|---|---|
| full-scan cost | $6.45 | **~$1.31** |
| full-scan wall clock | 1689 s | ~537 s |

These are arithmetic: the measured screening and rerank arms plus the baseline's own cost and wall
time for every stage neither arm touched
(`552f09c462dce07a7c20fa3f30e85c3264f42346:research/experiments/phase1-stateless/measurements.json`,
`extrapolation`). **No scan has
been run end to end this way as a default path**, no golden non-inferiority has been demonstrated
for it, and nothing in the shipped pipeline calls a model. Quote the screening numbers; do not
quote the full-scan numbers as a result.

### What shipped in v0.6.0, and what did not

**Shipped:** the T1 shortlist ordering, above. The reference driver in `drivers/stateless/`, as a
repo-only experimental engine, outside the package and outside the sdist.

**Not shipped:** any reranker or rubric change (Outcome C); the stateless driver as a default or
documented path; any engine interface in the package. `research-scan` still makes no model calls
of its own, and `engine = none` — a person or an agent screening against the rubrics — remains the
first-class way to run a scan; the ratified invariant and the conditions any future engine
protocol is bound by are in
[#4](https://github.com/Synectic-Research/research-scan/issues/4).

**The promotion bar, recorded so it is not renegotiated later.** A cognition engine may become a
documented path only on **end-to-end golden non-inferiority against a fresh multi-replicate
conversational control**, on both topics. Cost is not a promotion criterion: the arc above is
exactly the shape of evidence — 979 s to 72.6 s (13.5×), a quarter of the cost, and quality that
the same evidence cannot yet call equal — that a cost bar would have waved through.
