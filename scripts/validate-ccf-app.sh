#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <app-json-file|component-id>" >&2
  exit 1
fi

INPUT="$1"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_DIR="${REPORT_DIR:-$ROOT_DIR/reports}"
MCP_RUNNER_CMD="${MCP_RUNNER_CMD:-}"
REQUIRE_MCP_RUNNER="${REQUIRE_MCP_RUNNER:-0}"
VALIDATION_USE_KUBECTL="${VALIDATION_USE_KUBECTL:-0}"
VALIDATION_KUBECONFIG_PATH="${VALIDATION_KUBECONFIG_PATH:-}"
KUBECTL_VALIDATION_SCRIPT="${KUBECTL_VALIDATION_SCRIPT:-$ROOT_DIR/scripts/validate_k8s_resources.py}"

mkdir -p "$REPORT_DIR"

if [[ -f "$INPUT" ]]; then
  APP_FILE="$INPUT"
else
  APP_FILE="$REPORT_DIR/ccf-validation-app-${INPUT}.json"
  python3 "$ROOT_DIR/scripts/build_validation_manifest.py" --component "$INPUT" --output "$APP_FILE" >/dev/null
fi

echo "Prepared CCF app validation manifest: $APP_FILE"

if [[ "$VALIDATION_USE_KUBECTL" == "1" ]]; then
  if [[ -z "$VALIDATION_KUBECONFIG_PATH" ]]; then
    echo "VALIDATION_KUBECONFIG_PATH must be set when VALIDATION_USE_KUBECTL=1." >&2
    exit 1
  fi
  python3 "$KUBECTL_VALIDATION_SCRIPT" \
    --manifest "$APP_FILE" \
    --kubeconfig "$VALIDATION_KUBECONFIG_PATH" \
    --phase preflight \
    --report "$REPORT_DIR/ccf-k8s-preflight-app.json"
fi

export VALIDATION_USE_KUBECTL VALIDATION_KUBECONFIG_PATH KUBECTL_VALIDATION_SCRIPT

if [[ -n "$MCP_RUNNER_CMD" ]]; then
  echo "Invoking MCP runner command for app manifest."
  eval "$MCP_RUNNER_CMD" "\"$APP_FILE\""
else
  if [[ "$REQUIRE_MCP_RUNNER" == "1" ]]; then
    echo "MCP_RUNNER_CMD must be configured for enforced CCF validation." >&2
    exit 1
  fi
  echo "No MCP_RUNNER_CMD configured; manifest preparation only."
fi
