#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HELMFORGE_REPO_URL="${HELMFORGE_REPO_URL:-https://repo.helmforge.dev}"
OCI_PREFIX="${OCI_PREFIX:-}"
WORK_DIR="${WORK_DIR:-$ROOT_DIR/mirror-cache/helmforge}"
REPORT_PATH="${REPORT_PATH:-$ROOT_DIR/reports/helmforge-mirror-manifest.json}"
HELMFORGE_FILTER_REGEX="${HELMFORGE_FILTER_REGEX:-}"
HELMFORGE_LIMIT="${HELMFORGE_LIMIT:-0}"
DRY_RUN="${DRY_RUN:-0}"

case "${DRY_RUN,,}" in
  1|true|yes)
    DRY_RUN="1"
    ;;
  0|false|no|"")
    DRY_RUN="0"
    ;;
  *)
    echo "Unsupported DRY_RUN value: ${DRY_RUN}" >&2
    exit 1
    ;;
esac

if [[ -z "$OCI_PREFIX" && "$DRY_RUN" != "1" ]]; then
  echo "OCI_PREFIX must be set unless DRY_RUN=1" >&2
  exit 1
fi

mkdir -p "$WORK_DIR" "$(dirname "$REPORT_PATH")"

inventory_json="$(python3 "$ROOT_DIR/scripts/helmforge_inventory.py" --repo-url "$HELMFORGE_REPO_URL" --format json)"
export INVENTORY_JSON="$inventory_json"
export HELMFORGE_FILTER_REGEX
export HELMFORGE_LIMIT

mapfile -t selected < <(
  python3 - <<'PY'
import json
import os
import re

records = json.loads(os.environ["INVENTORY_JSON"])
pattern = os.environ.get("HELMFORGE_FILTER_REGEX", "")
limit = int(os.environ.get("HELMFORGE_LIMIT", "0") or "0")
regex = re.compile(pattern) if pattern else None

count = 0
for item in records:
    if regex and not regex.search(item["name"]):
        continue
    print(f"{item['name']}\t{item['version']}\t{item.get('appVersion', '')}\t{item.get('digest', '')}")
    count += 1
    if limit and count >= limit:
        break
PY
)

if [[ "${#selected[@]}" -eq 0 ]]; then
  echo "No HelmForge charts matched the current filters."
  exit 0
fi

manifest_tmp="$(mktemp)"
printf '[\n' > "$manifest_tmp"
count=0

for item in "${selected[@]}"; do
  IFS=$'\t' read -r name version app_version source_digest <<< "$item"
  archive_path="$WORK_DIR/${name}-${version}.tgz"

  echo "Mirroring ${name}:${version}"
  helm pull "$name" --repo "$HELMFORGE_REPO_URL" --version "$version" --destination "$WORK_DIR"

  target_ref=""
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "DRY_RUN=1 skipping helm push for ${archive_path}"
  else
    target_ref="${OCI_PREFIX%/}/${name}"
    helm push "$archive_path" "$OCI_PREFIX"
  fi

  archive_sha="$(sha256sum "$archive_path" | awk '{print $1}')"
  count=$((count + 1))
  export SYNC_NAME="$name"
  export SYNC_VERSION="$version"
  export SYNC_APP_VERSION="$app_version"
  export SYNC_SOURCE_REPOSITORY="$HELMFORGE_REPO_URL"
  export SYNC_SOURCE_DIGEST="$source_digest"
  export SYNC_ARCHIVE_SHA="$archive_sha"
  export SYNC_DESTINATION_REF="$target_ref"
  export SYNC_DRY_RUN="$DRY_RUN"
  export SYNC_FIRST="$([[ "$count" -eq 1 ]] && echo 1 || echo 0)"

  python3 - <<'PY' >> "$manifest_tmp"
import json
import os

record = {
    "name": os.environ["SYNC_NAME"],
    "version": os.environ["SYNC_VERSION"],
    "appVersion": os.environ["SYNC_APP_VERSION"],
    "sourceRepository": os.environ["SYNC_SOURCE_REPOSITORY"],
    "sourceDigest": os.environ["SYNC_SOURCE_DIGEST"],
    "archiveSha256": os.environ["SYNC_ARCHIVE_SHA"],
    "destinationRef": os.environ["SYNC_DESTINATION_REF"],
    "dryRun": os.environ["SYNC_DRY_RUN"] == "1",
}
prefix = "" if os.environ["SYNC_FIRST"] == "1" else ","
print(prefix + json.dumps(record, indent=2))
PY
done

printf '\n]\n' >> "$manifest_tmp"
mv "$manifest_tmp" "$REPORT_PATH"

echo "Mirrored ${count} HelmForge chart(s)."
echo "Manifest written to ${REPORT_PATH}."
