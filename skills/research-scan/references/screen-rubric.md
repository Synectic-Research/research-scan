# Screen rubric — writing `screen.json`

Retrieval hands you 150–250 candidates. Most are noise: short queries buy recall and pay for it in
precision. Your job is to sort them cheaply and honestly, so that expansion grows from the right
seeds and the reranker spends its attention where it counts.

Read one batch file at a time. Score **every** item — `shortlist` refuses to run unless each cid in
`candidates.json` has exactly one score.

Score against the sub-criteria the plan derived **for the declared purpose**, not against a general
sense of the topic; and on an `orient` scan, breadth counts as relevance — the first solid paper on
a sub-area nothing else covers is a 2 even when a dozen better papers on an already-covered
sub-area are also in the batch.

---

## The scale

| Score | Meaning | Test |
|---|---|---|
| **3** | central | Squarely about the brief's decision. You would be surprised if the final list omitted it. |
| **2** | relevant | Satisfies at least one sub-criterion properly. Worth the reranker's time. |
| **1** | tangential | Right vocabulary, wrong question — a nudge study in an unrelated domain, a mechanism paper with no bearing on the decision. |
| **0** | off-topic | Matched a keyword in another sense. Object detection, oncology trials, a paper about *loan* default. |

The 2 boundary is the one that matters. Everything scoring ≥ 2 becomes an expansion seed and reaches
the shortlist; everything below is invisible from here on. When genuinely torn, ask: *does this
paper give evidence on a sub-criterion, or does it merely share vocabulary with one?* Evidence → 2.

## What counts, and what does not

- **Do not reward citation counts or venue prestige.** You are not shown them, deliberately. A 2026
  preprint answering the brief's exact question beats a famous paper that does not.
- **Do reward contradiction.** A paper showing the brief's premise is wrong is *relevant*, often the
  most relevant thing in the batch. Score it on evidential value, not on whether it is welcome.
- **Judge on the abstract you were given.** `abstract_600` is truncated at 600 characters and
  sometimes falls back to a one-line summary. Score what is there; do not fill gaps from memory.
- **`origin_count` is weak evidence of centrality** — several queries converging on one paper is a
  signal, but not a substitute for reading the abstract.
- **`outside_window: true`** marks a paper the citation graph pulled in from before the window.
  Score it on relevance exactly as you would anything else. Its age is handled by code, not by you.
- **Watch for the false friend.** `default` means loan default, `inertia` means grid inertia,
  `anchoring` means seabed anchors. Check the abstract before scoring on a title.

## Reasons

One line, **at most 20 words**, saying what made the score. Write the reason that would let someone
re-derive your judgment without re-reading the abstract:

- good: `auto-enrolment effects attenuate over the medium run; contradicts the premise`
- good: `grid frequency inertia, an unrelated sense of inertia`
- useless: `relevant`, `not relevant`, `interesting paper`

## Which batches, and when

Up to four families of batch reach you, in this order. **Every one of them ends with the whole of
`screen.json` rewritten**, carrying every score from every pass so far — write the file, never
append to it. A cid that scored 1 in an earlier pass keeps that score; you are adding, not
re-deciding.

| Family | Written by | Score them after |
|---|---|---|
| `01`, `02`, … | `retrieve` | retrieval |
| `x01`, `x02`, … | `expand` | citation-graph expansion |
| `r01`, `r02`, … | `retrieve --round 2` | the gap round's queries |
| `xr01`, `xr02`, … | `expand --round 2` | the gap round's expansion |

Work sequentially, one batch at a time. Do not delegate batches to subagents in V1.

## `criteria_hit` — which criteria a paper satisfies

A score says *how* relevant; `criteria_hit` says *to what*. Without it, a criterion nobody wrote a
working query for is indistinguishable from a criterion the literature is thin on, and `coverage`
cannot aim the gap round at either.

**Required on every score of 2 or 3**: list the ids (`C1`, `C3`, …) from the batch's own
`sub_criteria` block that the paper actually satisfies — not the ones it is adjacent to. One id is
a normal answer; a paper that plausibly hits every criterion usually hits none of them precisely.
Leave it empty on a 0 or 1. An id the plan does not define is exit 2, not a silent miss.

---

## The file you must produce

`<run_dir>/screen.json` — a `ScreenFile`:

| Field | Type | Required | Notes |
|---|---|---|---|
| `scores` | array of ScreenScore | yes | one entry per cid in `candidates.json`, exactly once |

Each `ScreenScore`:

| Field | Type | Required | Notes |
|---|---|---|---|
| `cid` | string | yes | pattern `^[0-9a-f]{12}$` — copy it from the batch, never invent one |
| `score` | integer | yes | ≥ 0, ≤ 3 |
| `reason` | string | yes | at most 20 words |
| `criteria_hit` | array of string | on 2 and 3 | sub-criterion ids from the batch, e.g. `["C1","C3"]` |

```json
{
  "scores": [
    { "cid": "32831b736c11", "score": 3, "reason": "auto-enrolment effects attenuate over the medium run; contradicts the premise", "criteria_hit": ["C1", "C3"] },
    { "cid": "c2d27c54ca20", "score": 2, "reason": "status quo bias mechanism review; explains why defaults hold", "criteria_hit": ["C2"] },
    { "cid": "88831f8bbfe5", "score": 1, "reason": "nudging review but environmental domain, no enrolment or savings outcome", "criteria_hit": [] },
    { "cid": "c3f670731ab6", "score": 0, "reason": "aerial object detection", "criteria_hit": [] }
  ]
}
```

Unknown keys are rejected. If `shortlist` exits 2, it prints exactly which cids are missing,
duplicated, or not in `candidates.json` — fix those and rerun.
