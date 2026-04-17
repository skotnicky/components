#!/usr/bin/env python3
"""Detect upstream chart updates and optionally persist new curated wrapper versions."""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from catalog_data import CURATED_COMPONENTS, DEFAULT_CHART_VERSION, STATE_PATH


def helm_show_chart(dep: dict) -> tuple[str, str]:
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


def bump_patch(version: str) -> str:
    parts = version.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise ValueError(f"Unsupported chart version format: {version}")
    major, minor, patch = (int(part) for part in parts)
    return f"{major}.{minor}.{patch + 1}"


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def build_report() -> tuple[list[dict], dict]:
    state = load_state()
    report = []
    next_state = json.loads(json.dumps(state))

    for component in CURATED_COMPONENTS:
        current_chart_version = component.get("chart_version", DEFAULT_CHART_VERSION)
        dependency_rows = []
        needs_update = False

        for dependency in component["dependencies"]:
            latest_version, latest_app_version = helm_show_chart(dependency)
            dependency_changed = dependency["version"] != latest_version or (
                dependency.get("app_version", "") or ""
            ) != (latest_app_version or "")
            needs_update = needs_update or dependency_changed
            dependency_rows.append(
                {
                    "name": dependency["name"],
                    "repository": dependency["repository"],
                    "currentVersion": dependency["version"],
                    "latestVersion": latest_version,
                    "currentAppVersion": dependency.get("app_version", ""),
                    "latestAppVersion": latest_app_version,
                    "needsUpdate": dependency_changed,
                }
            )

        next_chart_version = bump_patch(current_chart_version) if needs_update else current_chart_version
        report.append(
            {
                "component": component["id"],
                "chartVersion": current_chart_version,
                "nextChartVersion": next_chart_version,
                "needsUpdate": needs_update,
                "dependencies": dependency_rows,
            }
        )

        if not needs_update:
            continue

        next_state[component["id"]] = {
            "chart_version": next_chart_version,
            "dependencies": {
                dependency["name"]: {
                    "repository": dependency["repository"],
                    "version": row["latestVersion"],
                    "app_version": row["latestAppVersion"],
                }
                for dependency, row in zip(component["dependencies"], dependency_rows, strict=True)
            },
        }

    return report, next_state


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report",
        default=str(ROOT / "reports" / "upstream-updates.json"),
        help="Path to write the update report",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Persist changed dependency pins and chart versions to scripts/catalog_state.json",
    )
    args = parser.parse_args()

    report, next_state = build_report()

    report_path = pathlib.Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.write:
        STATE_PATH.write_text(json.dumps(next_state, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    changed = [item for item in report if item["needsUpdate"]]
    print(f"Detected {len(changed)} curated chart(s) with upstream changes.")
    for item in changed:
        print(f"- {item['component']}: {item['chartVersion']} -> {item['nextChartVersion']}")
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
