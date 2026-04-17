#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="${DIST_DIR:-$ROOT_DIR/dist/curated}"
OCI_PREFIX="${OCI_PREFIX:-}"
PUSH="${PUSH:-0}"

mkdir -p "$DIST_DIR"

python3 "$ROOT_DIR/scripts/ensure_helm_repos.py"

for chart_dir in "$ROOT_DIR"/charts/*; do
  [[ -d "$chart_dir" ]] || continue
  helm dependency build "$chart_dir"
  helm package "$chart_dir" --destination "$DIST_DIR"
done

if [[ "$PUSH" == "1" ]]; then
  if [[ -z "$OCI_PREFIX" ]]; then
    echo "OCI_PREFIX must be set when PUSH=1" >&2
    exit 1
  fi
  for archive in "$DIST_DIR"/*.tgz; do
    helm push "$archive" "$OCI_PREFIX"
  done
fi

echo "$DIST_DIR"
