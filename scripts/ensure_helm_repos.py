#!/usr/bin/env python3
"""Register Helm repositories referenced by curated wrapper charts."""

from __future__ import annotations

import hashlib
import pathlib
import subprocess
import time

import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]
CHARTS_DIR = ROOT / "charts"


def repo_alias(url: str) -> str:
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]
    return f"repo-{digest}"


def iter_repo_urls() -> set[str]:
    repos = set()
    for chart_dir in sorted(path for path in CHARTS_DIR.iterdir() if path.is_dir()):
        chart = yaml.safe_load((chart_dir / "Chart.yaml").read_text(encoding="utf-8")) or {}
        for dep in chart.get("dependencies", []):
            repo = dep.get("repository", "")
            if repo and not repo.startswith("oci://"):
                repos.add(repo)
    return repos


def main() -> int:
    for url in sorted(iter_repo_urls()):
        alias = repo_alias(url)
        last_error = None
        for attempt in range(1, 4):
            try:
                subprocess.run(["helm", "repo", "add", alias, url, "--force-update"], check=True)
                last_error = None
                break
            except subprocess.CalledProcessError as exc:
                last_error = exc
                if attempt == 3:
                    raise
                time.sleep(attempt)
    if iter_repo_urls():
        subprocess.run(["helm", "repo", "update"], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
