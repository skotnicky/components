#!/usr/bin/env python3
"""Run local validation for curated wrapper charts."""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
CHARTS_DIR = ROOT / "charts"


def run(cmd: list[str], cwd: pathlib.Path | None = None) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=cwd or ROOT)


def chart_dirs() -> list[pathlib.Path]:
    return sorted(path for path in CHARTS_DIR.iterdir() if path.is_dir())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-template",
        action="store_true",
        help="Skip helm template smoke rendering",
    )
    args = parser.parse_args()

    run(["python3", str(ROOT / "scripts/ensure_helm_repos.py")])

    for chart_dir in chart_dirs():
        run(["helm", "dependency", "build", str(chart_dir)])
        run(["helm", "lint", str(chart_dir)])
        if not args.skip_template:
            run(
                [
                    "helm",
                    "template",
                    chart_dir.name,
                    str(chart_dir),
                    "--namespace",
                    chart_dir.name,
                ]
            )

    run(["python3", str(ROOT / "scripts/questions_lint.py")])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
