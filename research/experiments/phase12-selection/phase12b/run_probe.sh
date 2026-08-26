#!/bin/zsh
# Order-sensitivity probe: the winning cell's exact candidate set under three deterministic
# orderings. O1 replicates already exist from the primary run; this adds O2 and O3.
set -u
PY=/Users/nabergoj/Projects/research-scan/research/experiments/phase11-golden/.venv/bin/python
HERE=${0:A:h}
topic=$1; arm=$2; reps=${3:-2}; shift 3 2>/dev/null || shift $#
slug=$([[ $topic == defaults-savings ]] && echo p11-t1 || echo p11-t2)
for o in O2 O3; do
  for r in $(seq 1 $reps); do
    d="$HERE/runs/$slug/$arm/$o/rep$r"
    if [[ -f "$d/summary.json" ]]; then echo "skip $topic $arm $o rep$r (done)"; continue; fi
    echo "=== PROBE $topic $arm $o rep$r  $(date +%H:%M:%S) ==="
    $PY "$HERE/stability.py" run "$topic" "$arm" "$o" "$r" 2>&1 || echo "FAILED $topic $arm $o rep$r"
  done
done
echo "PROBE DONE $topic $arm $(date +%H:%M:%S)"
