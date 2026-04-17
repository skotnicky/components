#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_PATH="${REPORT_PATH:-$ROOT_DIR/reports/upstream-updates.json}"

mkdir -p "$(dirname "$REPORT_PATH")"

python3 "$ROOT_DIR/scripts/apply_upstream_updates.py" --report "$REPORT_PATH"
