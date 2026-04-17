#!/usr/bin/env python3
"""Fetch and normalize the published HelmForge chart inventory."""

from __future__ import annotations

import argparse
import json
import time
import sys
import urllib.request

import yaml


def latest_entries(index_data: dict) -> list[dict]:
    records = []
    for chart_name, entries in sorted(index_data.get("entries", {}).items()):
        if not entries:
            continue
        latest = entries[0]
        records.append(
            {
                "name": chart_name,
                "version": latest.get("version", ""),
                "appVersion": latest.get("appVersion", ""),
                "description": latest.get("description", ""),
                "digest": latest.get("digest", ""),
                "urls": latest.get("urls", []),
            }
        )
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-url",
        default="https://repo.helmforge.dev",
        help="Base HelmForge repository URL",
    )
    parser.add_argument(
        "--format",
        choices=["json", "tsv"],
        default="json",
        help="Output format",
    )
    parser.add_argument(
        "--index-file",
        default="",
        help="Optional local index.yaml path to read instead of downloading",
    )
    args = parser.parse_args()

    if args.index_file:
        payload = yaml.safe_load(open(args.index_file, "r", encoding="utf-8").read())
    else:
        index_url = args.repo_url.rstrip("/") + "/index.yaml"
        last_error = None
        payload = None
        for attempt in range(1, 6):
            try:
                with urllib.request.urlopen(index_url, timeout=60) as response:
                    payload = yaml.safe_load(response.read().decode("utf-8"))
                break
            except Exception as exc:  # pragma: no cover - transient network behavior
                last_error = exc
                if attempt == 5:
                    raise
                time.sleep(attempt)
        if payload is None and last_error is not None:
            raise last_error

    records = latest_entries(payload or {})
    if args.format == "json":
        json.dump(records, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    for item in records:
        sys.stdout.write(
            "\t".join(
                [
                    item["name"],
                    item["version"],
                    item["appVersion"],
                    item["digest"],
                ]
            )
            + "\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
