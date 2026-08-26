#!/bin/zsh
# Phase-1.2C — the whole offline replay, in order. $0 API. Deterministic: re-running from an
# empty results/ reproduces every file byte-for-byte.
set -eu
PY=/Users/nabergoj/Projects/research-scan/.venv/bin/python
HERE=${0:A:h}
for stage in inventory replay measure stability_of_features decide tables12c; do
  echo "=== $stage ==="
  $PY "$HERE/$stage.py"
done
$PY -m pytest "$HERE" -q
