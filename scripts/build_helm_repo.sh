#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_DIR="${REPO_DIR:-$ROOT_DIR/dist/helm-repo}"
HELM_REPO_URL="${HELM_REPO_URL:-}"

if [[ -z "$HELM_REPO_URL" ]]; then
  echo "HELM_REPO_URL must be set to build a classic Helm repository index." >&2
  exit 1
fi

rm -rf "$REPO_DIR"
mkdir -p "$REPO_DIR"

DIST_DIR="$REPO_DIR" PUSH=0 bash "$ROOT_DIR/scripts/package_curated.sh" >/dev/null
helm repo index "$REPO_DIR" --url "$HELM_REPO_URL"

echo "$REPO_DIR"
