#!/usr/bin/env bash
set -euo pipefail

# Resolve project root (script lives in scripts/)
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# Ensure virtualenv is active if you use one before running this script

mkdir -p reports

echo "[1/3] Running consolidated test_all_scanners..."
pytest -q tests/test_all_scanners.py --junitxml=reports/test_all_scanners.xml || true

echo "[2/3] Running individual scanner tests..."
shopt -s nullglob
for f in tests/test_*_scanner.py; do
  base="$(basename "$f" .py)"
  echo "  - $base"
  pytest -q "$f" --junitxml="reports/${base}.xml" || true
done
shopt -u nullglob

echo "[3/3] Running full test suite..."
pytest -q tests --junitxml=reports/combined.xml || true

echo
echo "Reports generated in: $(realpath reports)"
ls -1 reports | sed 's/^/ - /'
