#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_DIR="${REPORT_DIR:-$ROOT_DIR/reports}"
MANIFEST_PATH="${MANIFEST_PATH:-$REPORT_DIR/ccf-validation-manifest.json}"
SHARD_INDEX="${SHARD_INDEX:-0}"
SHARD_TOTAL="${SHARD_TOTAL:-1}"
REPOSITORY_NAME="${REPOSITORY_NAME:-ccf}"
MCP_RUNNER_CMD="${MCP_RUNNER_CMD:-}"
REQUIRE_MCP_RUNNER="${REQUIRE_MCP_RUNNER:-0}"
VALIDATION_USE_KUBECTL="${VALIDATION_USE_KUBECTL:-0}"
VALIDATION_KUBECONFIG_PATH="${VALIDATION_KUBECONFIG_PATH:-}"
KUBECTL_VALIDATION_SCRIPT="${KUBECTL_VALIDATION_SCRIPT:-$ROOT_DIR/scripts/validate_k8s_resources.py}"

mkdir -p "$REPORT_DIR"

python3 "$ROOT_DIR/scripts/build_validation_manifest.py" --repository-name "$REPOSITORY_NAME" --output "$MANIFEST_PATH"

SHARD_MANIFEST="$REPORT_DIR/ccf-validation-shard-${SHARD_INDEX}.json"
export MANIFEST_PATH SHARD_MANIFEST SHARD_INDEX SHARD_TOTAL
python3 - <<'PY'
import json
import os
from pathlib import Path

manifest_path = Path(os.environ["MANIFEST_PATH"])
shard_manifest = Path(os.environ["SHARD_MANIFEST"])
shard_index = int(os.environ["SHARD_INDEX"])
shard_total = int(os.environ["SHARD_TOTAL"])

data = json.loads(manifest_path.read_text(encoding="utf-8"))
curated = data.get("curated", [])

selected = [item for idx, item in enumerate(curated) if idx % shard_total == shard_index]
payload = {
    "curated": selected,
    "shard": {"index": shard_index, "total": shard_total},
}
shard_manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(shard_manifest)
PY

echo "Prepared CCF shard manifest: $SHARD_MANIFEST"

if [[ "$VALIDATION_USE_KUBECTL" == "1" ]]; then
  if [[ -z "$VALIDATION_KUBECONFIG_PATH" ]]; then
    echo "VALIDATION_KUBECONFIG_PATH must be set when VALIDATION_USE_KUBECTL=1." >&2
    exit 1
  fi
  python3 "$KUBECTL_VALIDATION_SCRIPT" \
    --manifest "$SHARD_MANIFEST" \
    --kubeconfig "$VALIDATION_KUBECONFIG_PATH" \
    --phase preflight \
    --report "$REPORT_DIR/ccf-k8s-preflight-shard-${SHARD_INDEX}.json"
fi

export VALIDATION_USE_KUBECTL VALIDATION_KUBECONFIG_PATH KUBECTL_VALIDATION_SCRIPT

if [[ -n "$MCP_RUNNER_CMD" ]]; then
  echo "Invoking MCP runner command for shard manifest."
  eval "$MCP_RUNNER_CMD" "\"$SHARD_MANIFEST\""
else
  if [[ "$REQUIRE_MCP_RUNNER" == "1" ]]; then
    echo "MCP_RUNNER_CMD must be configured for enforced CCF validation." >&2
    exit 1
  fi
  echo "No MCP_RUNNER_CMD configured; manifest preparation only."
fi
