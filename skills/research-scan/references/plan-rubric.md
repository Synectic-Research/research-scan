# Plan rubric — writing `queries.json`

You have read the brief. Your job now is to turn it into 6–8 queries that reach papers a strong
human searcher would find, including the ones written in a vocabulary the brief never uses.

Everything you write here is judgment. The CLI will not second-guess a bad query — it will
faithfully run it and return nothing.

---

## The single rule that matters most: 2–4 core terms naming one concept

**A semantic query is 2–4 core terms, in the target community's own vocabulary, naming exactly one
concept. Never a sentence, and never a concept plus a stack of qualifiers. When a concept has
several names, each name is its own query — that is what the 6–8 slots are for.**

This is not a style preference, it is how the two APIs behave. Verified live (probes recorded
2026-08-19):

- OpenAlex's `search` combines bare terms with **AND** (stemmed, stop words removed) over title,
  abstract **and fulltext** — so every extra term is another chance to exclude the paper you want,
  while the fulltext index floods the ranking with incidental matches. Its `relevance_score` also
  mixes in a **citation boost**, which sinks recent low-citation work; a short precise query is the
  only lever against both.
- Semantic Scholar's `/paper/search` answers a natural-language sentence with `{"total": 0}` — no
  error, no hits, nothing. It matches keywords, not meaning.

Measured on the llm-lit-search golden set: five-term queries found **1 of 6** expected papers at
the candidates stage; the same intents as 2–4-term queries found **5 of 6**, with no loss on the
defaults-savings set. The killed queries were not sentences — they were concepts with qualifiers
stacked on (`agentic LLM literature search system`), and each qualifier AND-ed away a target.

| Don't | Do |
|---|---|
| `default enrollment effect on consumer savings participation and contribution rates` | `default enrollment savings` |
| `agentic LLM literature search system` | `agentic academic paper search` |
| `deep research agent iterative search` | `deep research agent` (put *iterative search* in its own query if it is a real second vocabulary) |

`mode: keyword` means Boolean syntax, and OpenAlex **fully supports it** (verified live: uppercase
`AND` / `OR` / `NOT`, double-quoted phrases, parentheses — not just tolerated, honored); Semantic
Scholar, PubMed and arXiv accept it too:

```
("meta-analysis" OR "systematic review") AND (default OR "choice architecture") AND savings
```

If a source answers every query with zero hits, `retrieve` warns you. That warning almost always
means the queries were written for a reader, not for an index.

---

## What to write

### `brief_summary`

One paragraph restating the project **in your own words** — the problem, the decision that hangs on
it, and the setting. This is how a later reader checks whether you understood the brief before you
searched. Do not paste the brief back.

### `sub_criteria` — 3 to 6

Decompose the brief into the dimensions a paper could satisfy. Screening and reranking both score
against these, so they have to be answerable from a title and abstract. **Which dimensions to draw
from depends on the purpose** — the brief's `Purpose:` line, or the one you inferred and wrote into
`brief_summary`.

**`build`** — the answer moves a design or plan decision:

| Dimension | Asks |
|---|---|
| problem match | Does it study the thing the project is deciding about? |
| population / setting | Same kind of people, same kind of environment? |
| mechanism / method | Does it explain *why*, or contribute a way of measuring? |
| outcome / measure | Does it measure the outcome the project cares about? |
| constraints | Does it speak to the project's stated limits — regulatory, ethical, distributional? |

**`research`** — the answer changes what we believe, what we would test, or how we would measure it:

| Dimension | Asks |
|---|---|
| population / sample | Whom or what was studied, at what scale? |
| exposure / intervention / method | What was varied, or what technique was applied? |
| outcome / measure | What was measured, and how — the operationalisation, not just the topic? |
| the claim under test | Does it bear on the specific relation the brief is asking about, in either direction? |
| comparison / baseline | Against what was the effect measured — is there a real counterfactual? |

**`orient`** — what a newcomer to the topic must know, recent first:

| Dimension | Asks |
|---|---|
| topic scope | Is it inside the field as the brief draws it, or a neighbour? |
| sub-areas | Which branch of the field does it cover — and is that branch otherwise uncovered? |
| method families | Does it represent a distinct way of doing the work, not a variation on one already held? |
| time band | Does it belong to the current state, the turn the field just took, or the settled background? |

Give each an `id` (`C1`…), a two-or-three-word `name`, and a `text` saying what would make a paper
satisfy it. Vague criteria produce vague screening. Three to six either way — an `orient` scan with
four criteria is not underspecified, it is scoped.

### `queries` — 6 to 8

Each query aims at **a different research community's vocabulary**. That is the whole point of
having several: economists, HCI researchers, and consumer-psychology researchers name the same
phenomenon differently, and a single query only reaches one of them.

| `type` | Reaches | Mandatory |
|---|---|---|
| `direct` | the brief's own terms | **yes** |
| `terminology` | the same idea under another field's name | **yes** |
| `contradictory` | evidence against the brief's premise | **yes** |
| `review` | syntheses and meta-analyses, for effect sizes | **yes** |
| `mechanism` | why the effect happens | no |
| `method` | how it is measured or identified | no |
| `adjacent` | a neighbouring decision structure | no |
| `emerging` | what is new since the older literature settled | no |

Constraints the CLI enforces: 6–8 queries, unique ids, each `text` ≤ 30 words (you should be far
under), and all four mandatory types present. Failing any of these is `exit 2` with the list.

The eight intents and the four mandatory ones are the same at every purpose. Two of them aim
differently:

- **`research`: the `contradictory` query targets the claim**, not the topic. The brief states a
  relation it believes — X affects Y, method A beats method B — and this query goes after the
  people who dispute *that relation*, in their words: `reproducibility`, `null result`,
  `does not replicate`, `overestimated`. A contradictory query aimed at the topic in general comes
  back with the same literature the `direct` query already found.
- **`orient`: the `review` query is mandatory in two variants** — one reaching for the synthesis of
  the field as a whole, one for the sub-area the brief says is least familiar. A single review query
  on a mapping scan returns one community's idea of the field, and the second variant is what makes
  the map wider than that. They count as two of your 6–8.

### `round2` — the gap round, written later

Leave `round2` out of the file you write now. It is filled once, after `coverage` reports which
sub-criteria came back thin, and `retrieve --round 2` runs those queries and only those.

When you get there:

- **1–2 queries per thin criterion** — or, when `coverage` marks nothing thin, for the criterion
  with the fewest hits; a pool of 300 kept papers can leave one criterion at a twelfth of another's
  coverage without any of them falling under the flat threshold — each `{"id": "G1…", "type": "gap", "target_criterion":
  "<criterion id>", "text": "…", "mode": "semantic"}`. Same shape rule as above — 2–4 core terms,
  one concept. A thin criterion is usually thin because round 1 asked in the wrong community's
  words, so reach for the vocabulary that criterion's own literature uses, not a rewording of the
  query that already failed.
- **At most 2 reformulations** of the lowest-yield query in `coverage.json.queries`, ids `R1…`,
  keeping the original's `type` and dropping `target_criterion` unless one criterion is the point.
- Ids must not collide with `queries`. `type: "gap"` is rejected inside `queries`, and a `gap`
  query without a real `target_criterion` is `exit 2`.

Budget: eight `round2` queries maximum, and the round runs once. A criterion still thin after it is
a coverage risk to report, not a reason to write a third round.

### `anchors` — the papers the brief already names

Copy every paper or author the brief names into `anchors`, one entry per paper:

```json
"anchors": [
  { "doi": "10.1086/380085" },
  { "title": "The Power of Suggestion: Inertia in 401(k) Participation and Savings Behavior" }
]
```

A DOI resolves unambiguously and is always preferred; a title must match a live record at ratio
≥ 95, so give the real title, not a paraphrase. Anchored papers are pinned into the candidate pool
(they bypass the filters and the cap; an out-of-window anchor is tagged, not dropped), and
expansion **always** seeds from them — references, citations and recommendations all grow from
what the brief already trusts. When the brief names an author rather than a paper, anchor that
author's most on-point paper if you know it with confidence; do not guess DOIs.

An anchor that cannot be resolved is warned about and recorded in the stage log — check the
retrieve output rather than assuming it landed.

### `must_not`

Every exclusion goes here, as plain phrases. **Never write exclusions into query text.** Agents
reliably mishandle negation and search engines treat `NOT crypto` as a vote *for* crypto
(ScholarQuest 2026, the finding this rule exists for). The CLI matches these case-insensitively at
word boundaries against title and abstract, so `AI` will not fire on `AIDS`.

### `domain`

Resolve it yourself; `auto` is rejected. It selects sources: `behavioral` and `general` →
OpenAlex + Semantic Scholar; `cs` adds arXiv; `biomed` adds PubMed. Pick the field the *evidence*
lives in, not the field the product is in.

### `window`

Keep the run's default (36 months back) unless the brief argues otherwise. Widen to ~60 months for
slow-moving literatures. You do not need to reach back for the classics — citation-graph expansion
finds those and tags them `outside_window` for the foundational slots.

---

## How the brief template maps onto this file

Briefs written from `examples/brief.example.md` carry a `Purpose:` line and five sections, each of
which lands in a specific place — do not let content from one leak into another's mechanism:

| Brief section | Goes to | Why |
|---|---|---|
| Purpose | the first sentence of `brief_summary`; which `sub_criteria` set you draw from | it decides what counts as impact, so it decides what a paper is scored against |
| What this is about | `brief_summary`, `sub_criteria`, `domain` | the setting fixes the criteria |
| What we need to decide or answer | `sub_criteria`, the `direct` and `method` queries | what a paper must inform |
| What we already believe (the premise) | the `contradictory` query | search for evidence *against* it, in its own words |
| Exclusions | `must_not` — never query text | negation in queries is treated as a positive keyword |
| Known papers or authors | `anchors` | pin them; expansion grows from them |

---

## Worked example

This is `examples/queries.example.json`, measured against the defaults-savings golden set: it
finds the same golden papers at the candidates stage as the longer forms it replaced, with a
tighter, more on-topic pool. Note the query lengths: every semantic query is 2–4 core terms.

```json
{
  "brief_summary": "A consumer banking app is choosing how users enter a round-up savings feature (opt-in, opt-out, or forced active choice) and whether to pre-set the round-up multiplier. The team needs evidence on how large default effects are on enrolment, whether they persist and change amounts actually saved rather than just nominal sign-ups, whether pre-set levels anchor people downward, whether active choice recovers most of the benefit without the disengagement cost, and who is helped versus harmed. Consumer product with liquid savings, not an employer pension plan.",
  "domain": "behavioral",
  "window": { "from": "2023-08", "to": null },
  "sub_criteria": [
    { "id": "C1", "name": "default effect size",
      "text": "Measures how much a default, opt-out or active-choice enrolment design changes participation or contribution, ideally with an effect size." },
    { "id": "C2", "name": "persistence and depth",
      "text": "Follows outcomes beyond initial sign-up: retention, withdrawal, engagement, or amount actually saved at 6 months or more." },
    { "id": "C3", "name": "anchoring on preset levels",
      "text": "Says something about pre-set contribution amounts or slider defaults anchoring the level people choose." },
    { "id": "C4", "name": "consumer, self-directed setting",
      "text": "Adults choosing for themselves in a consumer financial or digital product, rather than an employer-mediated plan." },
    { "id": "C5", "name": "distributional or ethical cost",
      "text": "Reports heterogeneity across users, welfare consequences, or when a default is perceived as manipulative." }
  ],
  "must_not": ["cryptocurrency", "organ donation", "clinical trial"],
  "queries": [
    { "id": "Q1", "type": "direct",        "text": "default enrollment savings",           "mode": "semantic" },
    { "id": "Q2", "type": "terminology",   "text": "choice architecture fintech",          "mode": "semantic" },
    { "id": "Q3", "type": "mechanism",     "text": "status quo bias defaults",             "mode": "semantic" },
    { "id": "Q4", "type": "contradictory", "text": "nudge publication bias",               "mode": "semantic" },
    { "id": "Q5", "type": "review",        "text": "(\"meta-analysis\" OR \"systematic review\") AND (default OR \"choice architecture\") AND savings", "mode": "keyword" },
    { "id": "Q6", "type": "adjacent",      "text": "active choice automatic enrollment",   "mode": "semantic" },
    { "id": "Q7", "type": "emerging",      "text": "dark patterns defaults",               "mode": "semantic" },
    { "id": "Q8", "type": "mechanism",     "text": "anchoring default contribution",       "mode": "semantic" }
  ]
}
```

A note on precision, honestly: short queries buy recall and cost you precision — an earlier
variant of Q8 pulled in grid-frequency *inertia* and carbon *anchoring*. Screening is where you
pay that back. Prefer terms that are ambiguous only inside your own field, and never fix an
ambiguous query by stacking qualifiers onto it — swap the ambiguous term for the community's more
specific one instead.

---

## Before you run `retrieve`

- [ ] 6–8 queries, all four mandatory types present, unique ids
- [ ] every semantic query is 2–4 core terms naming one concept, no sentences, no stacked qualifiers
- [ ] queries reach at least three different vocabularies, not three rewordings of one
- [ ] 3–6 sub-criteria, each answerable from an abstract
- [ ] every exclusion is in `must_not`, none in query text
- [ ] `domain` resolved, not `auto`
- [ ] `round2` absent or empty — it is written after `coverage`, not now

Then: `research-scan retrieve --run <run_dir> --json`.
