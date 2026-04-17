#!/usr/bin/env python3
"""Build a validation manifest for curated charts and the HelmForge mirror."""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from catalog_data import CURATED_COMPONENTS, HELMFORGE_MIRROR


def helmforge_inventory(repo_url: str) -> list[dict]:
    cmd = ["python3", str(ROOT / "scripts/helmforge_inventory.py"), "--repo-url", repo_url, "--format", "json"]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def curated_manifest() -> list[dict]:
    items = []
    for component in CURATED_COMPONENTS:
        items.append(
            {
                "kind": "curated",
                "id": component["id"],
                "displayName": component["display_name"],
                "packageName": component["package_name"],
                "namespace": component["namespace"],
                "smokeProfile": component["smoke_profile"],
                "questionsYaml": f"charts/{component['id']}/questions.yaml",
                "valuesPath": f"charts/{component['id']}/values.yaml",
                "chartPath": f"charts/{component['id']}",
                "notes": component["notes"],
            }
        )
    return items


def mirror_manifest(repo_url: str, limit: int) -> list[dict]:
    records = helmforge_inventory(repo_url)
    if limit:
        records = records[:limit]
    return [
        {
            "kind": "helmforge-mirror",
            "name": item["name"],
            "version": item["version"],
            "appVersion": item.get("appVersion", ""),
            "digest": item.get("digest", ""),
            "sourceRepository": repo_url,
            "smokeProfile": HELMFORGE_MIRROR["smoke_profile"],
        }
        for item in records
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-url", default=HELMFORGE_MIRROR["repository_url"])
    parser.add_argument("--mirror-limit", type=int, default=0)
    parser.add_argument(
        "--output",
        default=str(ROOT / "reports" / "ccf-validation-manifest.json"),
        help="Path to write the generated manifest",
    )
    args = parser.parse_args()

    payload = {
        "curated": curated_manifest(),
        "helmforgeMirror": mirror_manifest(args.repo_url, args.mirror_limit),
    }

    output = pathlib.Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
