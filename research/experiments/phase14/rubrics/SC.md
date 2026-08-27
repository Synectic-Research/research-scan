# Rerank rubric — writing `ranked.json`

`shortlist.json` gives you up to 40 in-window records and up to 12 out-of-window ones, with full
metadata this time. Score every record in **both** lists.

Screening asked "is this worth reading?". Reranking asks a harder question: **would this paper
change what the project builds?** A well-executed study of a question the project has already
settled is a 1 here even if it was a 3 there.

This decomposition — score sub-criteria separately, then judge holistically — is the step the
literature identifies as the reranking win (Paper Finder's "mini breakthrough"). Do not skip
straight to `overall`.

---

## Scoring

### `criteria` — each sub-criterion, 0–3

Score each `C*` from `queries.json` independently, from the abstract in front of you. A paper can be
3 on outcome and 0 on population; that pattern is information, and code uses the sum as a tie-break.

### `overall` — 0–3 against absolute anchors

Judge every record against these four anchors. They are **absolute**: there is no cap on how many
records may reach any level and no quota requiring that any of them be used.

| Score | Means |
|---|---|
| **0** | No material bearing on the research question. |
| **1** | Related or background; unlikely to change what should be believed, tested, measured, compared or selected. |
| **2** | Directly useful evidence materially informing at least one criterion, but replaceable by stronger evidence in the current candidate set. |
| **3** | Decision-changing: omitting this paper would materially weaken or alter the evidence portfolio — closest prior work, strongest evidence, serious contradiction, uniquely relevant method or benchmark precedent, or a necessary foundational result. |

`overall` is your own judgment, **not an average** of `criteria`. A paper that is 3 on the one
criterion the decision turns on may deserve a 3 overall while scoring 0 elsewhere. Say what you
actually think.

### `priority_rank` — a strict order over the records you scored 3

Every record you score `overall: 3` also carries a `priority_rank`: a strict ranking of those
records against each other, best first. The ranks are **1, 2, 3, … with no gaps and no ties** — if
four records in front of you score 3, exactly one carries `1`, one `2`, one `3` and one `4`. Every
record you score 0, 1 or 2 carries `priority_rank: 0`.

Rank on the same question the top anchor asks: how much would the evidence portfolio lose if this
paper were left out. This is where you say which of your 3s matters most; the four-level scale
deliberately cannot.

### What counts as decision-changing value

The purpose taxonomy defines a `research` answer as one that **changes what we believe, what we
would test, or how we would measure it**, and asks of the claim under test whether a paper bears on
the relation the brief is asking about **in either direction**. Read that widely, and at every
purpose. All of the following are legitimate decision-changing value in their own right, not weaker
substitutes for it:

- **closest prior work** — the published work nearest to what the brief is deciding or claiming;
- **strongest evidence** — the most rigorous, or largest-sample, estimate available on the question;
- **contested or contradicting evidence** — work bearing on the brief's relation in the other
  direction;
- **method or benchmark precedent** — the technique, design, measurement or evaluation set that the
  later work is reported against;
- **necessary foundational results** — the result without which the current literature's argument,
  baseline or comparison cannot be read.

A paper whose value to the brief is one of these is not scored down for it being one of these.

### `relation` — required from S4.5 on

How the paper stands to the brief, one of:

| Value | Means |
|---|---|
| `design-changing` | Acting on it would change what gets built. |
| `plan-influencing` | Changes sequencing, measurement, or what to watch for — not the design itself. |
| `closely-related` | High-quality work on the same question in a near setting. |
| `contradicting` | Pushes against a premise the brief states. |
| `foundational` | The older work the current literature argues with. |

**`relation` records how the paper stands to the brief; it does not set `overall`.** Score `overall`
against the anchors above, at every purpose, not only at `build`. Closely-related high-quality work
is NOT scored down for being non-actionable: a rigorous study of the same question in a
neighbouring setting is exactly what a reader wants next to the directly actionable papers, and on
a `research` or `orient` scan it may be the whole answer. "Informs no named decision" is not a
defect when the brief never named one. `foundational` papers are scored on merit like everything
else; code handles where they render.

### The off-domain cap — `overall` 2 maximum

Ask one more question of every paper before you write `overall`: **is this paper's setting the
brief's setting?** Compare it against the population/setting sub-criterion — the one naming who or
what is being studied and where. If the answer is no, `overall` caps at **2**, whatever the other
criteria scored and whatever `relation` you chose.

**When no sub-criterion names a population or setting, compare against `brief_summary` instead.**
The plan rubric offers population/setting as one of five dimensions and does not require it, so a
methods-heavy plan can legitimately have none — `llm-lit-search`'s five criteria are all about
evidence and technique, and nothing in them says "scientific literature search" is the setting. The
brief always says it. Do not skip the question because the criterion is missing; that is the case
the cap was written for.

The single exception: `relevance_reason` names an **explicit method transfer** — the specific
technique, design or measurement that carries across, and why it survives the change of setting.
"Analogous", "similar dynamics", "the same underlying mechanism" are not method transfers; they are
the analogy the cap exists to stop. If you cannot name what transfers, it does not transfer.

The same exception is available when the paper's value to the brief is one of the decision-changing
roles named above, and `relevance_reason` says which role and what specifically carries across —
the closest-prior-work claim, the estimate, the contradicted relation, the method or benchmark, or
the foundational result the brief's decision rests on. The bar is identical to the method-transfer
bar: a role asserted without naming what carries across is the analogy the cap exists to stop.

This is a real defect, not a hypothetical. The S5 acceptance judge scored `2026-08-19-topic2b`
rank 7 a 1: a requirements-traceability QA paper, in a scan about scientific literature search,
holding `overall: 3` on a `why_it_matters` analogy nothing in this rubric had asked it to defend.
An off-domain paper can still be worth emitting — at 2, ranked under the work that is actually
about the brief's setting, which is where a reader can weigh the analogy themselves.

### `evidence_level`

What kind of evidence this is, exactly one of: `systematic-review`, `meta-analysis`, `rct`,
`prospective`, `observational`, `experimental`, `computational`, `qualitative`, `other`. Choose from
what the abstract states. A narrative overview is `other` with `flags.review` set, not
`systematic-review` — that label means the paper says it followed a systematic protocol.

### `flags`

- `review` — a review or meta-analysis. Code guarantees at least one flagged paper reaches the
  output if any scored ≥ 2, so this flag decides whether the scan ships a synthesis.
- `contradicts` — contradicts a premise of the brief. Same guarantee. A scan that only confirms what
  the team already believed is not evidence, so set this honestly.
- `methods_paper` — contributes a method or measure rather than a finding.

## Writing

- **`key_finding`** — one sentence, the result itself. **Use the abstract's numbers when it gives
  them**; never supply numbers it does not. If you know the famous figure from that paper but the
  abstract in front of you does not state it, you do not have it.
- **`methodology`** — design, data, scale. When the abstract is all you have, say `abstract-only`
  in this field. That is not an admission of failure, it is the provenance a reader needs.
- **`why_it_matters`** — the field that earns the scan, and the one field whose test depends on the
  brief's purpose. Whichever purpose, the failure mode is the same: a sentence that would be true of
  any paper in the field. "Important for behavioural science" is worthless.

  | Purpose | What this field has to say |
  |---|---|
  | `build` | **Which decision it moves, and how.** "Sets the ceiling our default-design decision should be measured against." |
  | `research` | **How it changes what we believe, what we would test, or how we would measure it.** "Puts the baseline recall at 20%, so our claimed improvement is measured against the wrong number." |
  | `orient` | **Why a newcomer must know it.** "The result the whole sub-field argues with; nothing after 2023 makes sense without it." |
- **`limitations`** — at least one, and it must be real. Distance from the project's setting counts:
  an employer-plan study is limited *for us* even if flawless in its own terms.
- **`relevance_reason`** — one line on why this record is in the list at all.

## Boundaries

- **Never introduce a cid that is not in `shortlist.json`.** `verify` and `emit` both exit 2 on an
  unknown cid, naming it.
- **Never edit metadata.** Title, year, venue and identifiers are the CLI's, checked against the
  live record at `verify`. If a title looks wrong, that is a finding for the report, not a fix.
- **Do not write `verification`.** `verify` fills it. `emit` exits 2 if it is missing, which means
  you forgot to run `verify`.
- Out-of-window records are candidates for the foundational slots. Score them on merit; code decides
  where they land and renders them after the current work.

---

## The file you must produce

`<run_dir>/ranked.json` — a **bare JSON array** of `RankedEntry` (no wrapper object):

| Field | Type | Required | Notes |
|---|---|---|---|
| `cid` | string | yes | must already exist in `shortlist.json`; pattern `^[0-9a-f]{12}$` |
| `criteria` | object (string → integer 0–3) | yes | sub-criterion id → score |
| `overall` | integer | yes | ≥ 0, ≤ 3 — holistic, not an average |
| `evidence_level` | enum | yes | one of the nine values above |
| `relation` | enum or null | no | `design-changing` · `plan-influencing` · `closely-related` · `contradicting` · `foundational` — set it; only pre-S4.5 files omit it |
| `flags` | RankedFlags | no | `review`, `contradicts`, `methods_paper`, all default false |
| `key_finding` | string | yes | one sentence, with the abstract's numbers when it gives them |
| `methodology` | string | yes | say `abstract-only` when the abstract is all there is |
| `why_it_matters` | string | yes | specific to this project's design decisions |
| `limitations` | array of string | yes | at least one |
| `relevance_reason` | string | yes | — |
| `verification` | Verification or null | no | leave it out; `verify` writes it |

```json
[
  {
    "cid": "32831b736c11",
    "criteria": { "C1": 3, "C2": 3, "C3": 2, "C4": 1, "C5": 1 },
    "overall": 3,
    "evidence_level": "observational",
    "relation": "contradicting",
    "flags": { "review": false, "contradicts": true, "methods_paper": false },
    "key_finding": "Medium- and long-run dynamics undermine the measured effect of automatic enrolment and of default contribution auto-escalation.",
    "methodology": "Longitudinal analysis of automatic savings policies. Abstract-only.",
    "why_it_matters": "The clearest statement of our support team's objection: the enrolment lift is real at signup and much smaller later.",
    "limitations": [
      "retirement plans rather than liquid consumer savings",
      "abstract gives no effect sizes"
    ],
    "relevance_reason": "Contradicts the premise that defaults reliably raise saving, which the brief asked us to look for."
  }
]
```

Then: `research-scan verify --run <run_dir> --json`, and `research-scan emit --run <run_dir> --json`.
