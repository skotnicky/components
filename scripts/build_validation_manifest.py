#!/usr/bin/env python3
"""Build a validation manifest for curated charts."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from catalog_data import CURATED_COMPONENTS


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=str(ROOT / "reports" / "ccf-validation-manifest.json"),
        help="Path to write the generated manifest",
    )
    args = parser.parse_args()

    payload = {"curated": curated_manifest()}

    output = pathlib.Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
