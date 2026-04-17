#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <app-json-file>" >&2
  exit 1
fi

APP_FILE="$1"
MCP_RUNNER_CMD="${MCP_RUNNER_CMD:-}"
REQUIRE_MCP_RUNNER="${REQUIRE_MCP_RUNNER:-0}"

if [[ ! -f "$APP_FILE" ]]; then
  echo "App manifest not found: $APP_FILE" >&2
  exit 1
fi

echo "Prepared CCF app validation manifest: $APP_FILE"

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
