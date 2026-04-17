#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_PATH="${REPORT_PATH:-$ROOT_DIR/reports/upstream-updates.json}"

mkdir -p "$(dirname "$REPORT_PATH")"

python3 - <<'PY' > "$REPORT_PATH"
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path.cwd()
sys.path.insert(0, str(ROOT / "scripts"))

from catalog_data import CURATED_COMPONENTS  # noqa: E402


def helm_show_chart(dep):
    if dep["repository"].startswith("oci://"):
        ref = f"{dep['repository'].rstrip('/')}/{dep['name']}"
        cmd = ["helm", "show", "chart", ref]
    else:
        cmd = ["helm", "show", "chart", dep["name"], "--repo", dep["repository"]]
    out = subprocess.check_output(cmd, text=True)
    version = ""
    app_version = ""
    for line in out.splitlines():
        if line.startswith("version:"):
            version = line.split(":", 1)[1].strip()
        elif line.startswith("appVersion:"):
            app_version = line.split(":", 1)[1].strip().strip('"')
    return version, app_version


report = []
for component in CURATED_COMPONENTS:
    dep = component["dependencies"][0]
    latest_version, latest_app_version = helm_show_chart(dep)
    report.append(
        {
            "component": component["id"],
            "currentVersion": dep["version"],
            "latestVersion": latest_version,
            "currentAppVersion": dep["app_version"],
            "latestAppVersion": latest_app_version,
            "needsUpdate": dep["version"] != latest_version or (dep["app_version"] or "") != (latest_app_version or ""),
        }
    )

print(json.dumps(report, indent=2))
PY

echo "$REPORT_PATH"
