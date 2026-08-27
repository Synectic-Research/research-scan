#!/bin/zsh
# Phase-1.4 — launch both topic streams in parallel and wait.
#
#   ANTHROPIC_API_KEY=... ./phase14.sh 1 3 C0 S C SC      # stage 1: 3 replicates of every cell
#   ANTHROPIC_API_KEY=... ./phase14.sh 4 5 C0             # stage 2: extend a contender to 5
#
# Both streams share one flock'd ledger and one $33 cap. Every replicate is skipped if it already
# has a summary.json, so re-running is safe and resumes rather than repeats.
#
# ~10 minutes per replicate (Phase-1.2B measured 506-732 s at R40), so stage 1 is about two hours
# with the two streams running side by side.
set -u
HERE=${0:A:h}

if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
  echo "ANTHROPIC_API_KEY is not set" >&2
  exit 1
fi

first=$1; shift
last=$1; shift

echo "=== phase 1.4  reps $first..$last  cells: $*  started $(date +%H:%M:%S) ==="
$HERE/.venv/bin/python "$HERE/run14.py" plan

"$HERE/run_stream.sh" defaults-savings "$first" "$last" "$@" &
t1=$!
"$HERE/run_stream.sh" llm-lit-search  "$first" "$last" "$@" &
t2=$!
wait $t1 $t2

echo "=== phase 1.4 both streams done $(date +%H:%M:%S) ==="
$HERE/.venv/bin/python -c "
import json, pathlib
led = pathlib.Path('$HERE/results/spend.json')
d = json.loads(led.read_text()) if led.exists() else {'total_usd': 0.0, 'calls': []}
print(f\"ledger: \${d['total_usd']:.4f} over {len(d['calls'])} calls\")
"
