# Skill trigger check

Does a fresh Claude Code session reach for `research-scan` on the questions it should, and leave it
alone on the ones it should not? The skill's `description` is the only thing deciding that, so this
file is the check on the string in `skills/research-scan/SKILL.md`.

It is documentation, not a pytest file — pytest collects `test_*.py` only, so nothing here runs in
the ordinary gate. Re-run it by hand when the description changes.

## Method

Twelve prompts, each in its own fresh session, from a **scratch working directory** — never the
repo, because a session that does trigger the skill will start a real scan and write
`research/scans/` wherever it happens to be:

```bash
cd <scratch dir>
claude -p "<prompt>" --max-turns 2 --output-format json --session-id "$uuid"
```

- `--session-id` pins the transcript to a known path, so detection is exact rather than inferred
  from the answer text.

**A probe that hits costs a real scan, and there is no way around it.** Three attempts to record
the invocation without letting the fork run:

| Attempt | Result |
|---|---|
| `--max-turns 2` | the fork reported `num_turns: 4` and ran `doctor`, `init` and a full retrieval |
| `--disallowed-tools Bash` | the fork still ran the CLI — it honours the skill's own `allowed-tools: Bash(research-scan *)` |
| `PATH` shimmed to a directory without `research-scan` | the fork's Bash re-initialises from the user profile, restoring `~/.local/bin` |

A forked skill's `allowed-tools` beats the parent session's restrictions. So the scratch working
directory is not a nicety, it is the only mitigation that held: two probes wrote populated run
directories of 450 candidates each, harmlessly, outside the repo.

**Budget by outcome, not per probe.** A probe that does not trigger costs cents. A probe that
triggers and is left to run costs whatever the scan costs: the twelve-probe sweep averaged $0.46
because most sessions stopped early, while the two-probe re-check that ran to completion cost
$6.19 and $10.88. Expect one real scan per hit and price the sweep on the number of hits.

**Detection** (`detect.py`, kept beside the probes in the scratch dir): read the session's own
`.jsonl` transcript and look for a `tool_use` block with `name: "Skill"` and
`input.skill == "research-scan"`.

| Result | Means |
|---|---|
| `invoked` | the Skill tool was called — a hit |
| `named` | research-scan appears in the answer text but was never invoked — a near miss |
| `no` | neither |

A should-trigger prompt passes on `invoked`. A should-not-trigger prompt passes on anything except
`invoked`.

## What this does and does not show

Invocation is model-sampled, not deterministic. This is **one run of each prompt**, so the table is
evidence about the description, not a gate: a cell could flip on a re-run. It also says nothing
about whether the scan that follows is any good, or whether the planner infers the right purpose —
neither is measured here.

## Results

Run 2026-08-19, against the reframed description.

The `<question>` / `<topic> since <year>` placeholders were later replaced with "this question" and
"this topic since a given year" — claude.ai's skill uploader rejects angle brackets as XML tags.
`r1` and `r2` were re-run against the reworded description and both still invoked; the other ten
rows are from the original sweep.

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

