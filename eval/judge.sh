#!/usr/bin/env bash
# Independent judge for one scan's top 10 (spec §13, canon §3).
#
#   ./eval/judge.sh <judge-model> <run-dir> [out-file]
#
# Writes a JudgeFile JSON, which `research-scan eval --judge <file>` merges into the EvalResult.
#
# The judge MUST be a stronger model than the one that produced ranked.json, and MUST NOT be the
# same model — a judge sharing the reranker's priors scores its own work. Per fable-dispatch,
# Fable 5 is the first-choice judge slot.
#
# This script CANNOT check that for you: nothing in the run records which model ran the skill, so
# the constraint is yours to honour. It prints what it knows and leaves the choice where it belongs.

set -euo pipefail

JUDGE_MODEL="${1:-}"
RUN_DIR="${2:-}"
OUT_FILE="${3:-}"

if [[ -z "$JUDGE_MODEL" || -z "$RUN_DIR" ]]; then
  echo "usage: $0 <judge-model> <run-dir> [out-file]" >&2
  echo "  e.g. $0 claude-fable-5 research/scans/2026-08-19-s3-e2e" >&2
  exit 2
fi

if [[ ! -f "$RUN_DIR/evidence.json" ]]; then
  echo "error: no evidence.json in $RUN_DIR — run \`research-scan emit\` first" >&2
  exit 2
fi

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPT_FILE="$HERE/judge-prompt.md"
OUT_FILE="${OUT_FILE:-$RUN_DIR/judge.json}"

TOOL_VERSION="$(jq -r '.tool_version // "unknown"' "$RUN_DIR/manifest.json")"
echo "run          $RUN_DIR (research-scan $TOOL_VERSION)" >&2
echo "judge model  $JUDGE_MODEL" >&2
echo "reminder     canon §3 — the judge must differ from, and be stronger than, the reranker." >&2
echo "             Nothing records the reranker's model; this script cannot verify it." >&2

# The judge sees the brief and the packets, never the reranker's scores — see judge-prompt.md.
BRIEF="$(cat "$RUN_DIR/brief.md")"
# selection_reason is included on purpose: judge-prompt.md scores `foundational` packets on
# canonicity rather than on the brief's decisions, and cannot tell them apart without it.
PACKETS="$(jq '{run_dir: .run.run_dir,
                packets: [.packets[] | {rank, cid, selection_reason, title, year, venue, abstract,
                                        key_finding, why_it_matters}]}' \
             "$RUN_DIR/evidence.json")"
SUB_CRITERIA="$(jq -c '.sub_criteria' "$RUN_DIR/queries.json")"

PROMPT="$(cat "$PROMPT_FILE")

## The brief

$BRIEF

## Sub-criteria

$SUB_CRITERIA

## The packets to score

$PACKETS"

claude -p "$PROMPT" \
  --model "$JUDGE_MODEL" \
  --output-format json \
  --json-schema "$(research-scan schema --name JudgeFile)" \
  | jq '.structured_output' > "$OUT_FILE"

echo "wrote        $OUT_FILE" >&2
echo "next         research-scan eval --topic <topic> --run $RUN_DIR --judge $OUT_FILE" >&2
