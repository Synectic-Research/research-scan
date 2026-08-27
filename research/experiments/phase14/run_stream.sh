#!/bin/zsh
# Phase-1.4 — one topic's replicates, strictly sequential.
#
# Two of these run in parallel (one per topic); the ledger is flock'd so the shared $33 cap is
# enforced across both. Idempotent and resumable: a replicate whose summary.json already exists is
# skipped, so the script can be re-run after an interruption or to add replicates on top.
#
#   run_stream.sh <topic> <first_rep> <last_rep> <cell> [cell …]
#
# Requires ANTHROPIC_API_KEY in the environment and `research-scan` on PATH.
set -u
PY=/Users/nabergoj/Projects/research-scan/research/experiments/phase14/.venv/bin/python
HERE=${0:A:h}

topic=$1; shift
first=$1; shift
last=$1; shift

if [[ $topic == defaults-savings ]]; then slug=p11-t1; else slug=p11-t2; fi
mkdir -p "$HERE/logs"

for cell in "$@"; do
  for r in $(seq $first $last); do
    d="$HERE/runs/$slug/$cell/rep$r"
    if [[ -f "$d/summary.json" ]]; then echo "skip $topic $cell rep$r (done)"; continue; fi
    echo "=== $topic $cell rep$r  $(date +%H:%M:%S) ==="
    $PY "$HERE/run14.py" run "$topic" "$cell" "$r" 2>&1 \
      | tee -a "$HERE/logs/$slug-$cell-rep$r.log" \
      || echo "FAILED $topic $cell rep$r"
  done
done
echo "STREAM DONE $topic $(date +%H:%M:%S)"
