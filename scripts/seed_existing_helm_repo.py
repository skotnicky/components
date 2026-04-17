#!/usr/bin/env python3
"""Download the currently published Helm repo contents to preserve historical versions."""

from __future__ import annotations

import argparse
import pathlib
import urllib.error
import urllib.parse
import urllib.request

import yaml


def fetch(url: str) -> bytes | None:
    try:
        with urllib.request.urlopen(url) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise
    except urllib.error.URLError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-url", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--index-output", required=True)
    args = parser.parse_args()

    repo_url = args.repo_url.rstrip("/")
    output_dir = pathlib.Path(args.output_dir)
    index_output = pathlib.Path(args.index_output)
    output_dir.mkdir(parents=True, exist_ok=True)
    index_output.parent.mkdir(parents=True, exist_ok=True)

    index_url = f"{repo_url}/index.yaml"
    raw_index = fetch(index_url)
    if raw_index is None:
        return 0

    index_output.write_bytes(raw_index)
    payload = yaml.safe_load(raw_index) or {}
    entries = payload.get("entries", {})

    seen = set()
    for versions in entries.values():
        for version in versions or []:
            for chart_url in version.get("urls", []):
                download_url = urllib.parse.urljoin(f"{repo_url}/", chart_url)
                parsed = urllib.parse.urlparse(download_url)
                basename = pathlib.Path(parsed.path).name
                if not basename.endswith(".tgz") or basename in seen:
                    continue
                seen.add(basename)
                data = fetch(download_url)
                if data is None:
                    continue
                (output_dir / basename).write_bytes(data)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
