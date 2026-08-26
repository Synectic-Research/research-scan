#!/bin/zsh
# One topic's replicates, strictly sequential. Two of these run in parallel (one per topic);
# the ledger is flock'd so the shared $18 cap is enforced across both.
set -u
PY=/Users/nabergoj/Projects/research-scan/research/experiments/phase11-golden/.venv/bin/python
HERE=${0:A:h}
topic=$1; shift
reps=$1; shift
for arm in "$@"; do
  for r in $(seq 1 $reps); do
    d="$HERE/runs/$([[ $topic == defaults-savings ]] && echo p11-t1 || echo p11-t2)/$arm/O1/rep$r"
    if [[ -f "$d/summary.json" ]]; then echo "skip $topic $arm rep$r (done)"; continue; fi
    echo "=== $topic $arm rep$r  $(date +%H:%M:%S) ==="
    $PY "$HERE/stability.py" run "$topic" "$arm" O1 "$r" 2>&1 || echo "FAILED $topic $arm rep$r"
  done
done
echo "STREAM DONE $topic $(date +%H:%M:%S)"
