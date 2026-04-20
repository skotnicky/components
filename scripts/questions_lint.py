#!/usr/bin/env python3
"""Validate that curated questions.yaml variables map to chart values."""

from __future__ import annotations

import pathlib
import sys

import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]
CHARTS_DIR = ROOT / "charts"


def parse_path(path: str) -> list[str]:
    parts = []
    for chunk in path.split("."):
        while "[" in chunk:
            prefix, rest = chunk.split("[", 1)
            if prefix:
                parts.append(prefix)
            index, chunk = rest.split("]", 1)
            parts.append(index)
        if chunk:
            parts.append(chunk)
    return parts


def has_path(data, path: str) -> bool:
    cur = data
    for part in parse_path(path):
        if isinstance(cur, list):
            if not part.isdigit():
                return False
            idx = int(part)
            if idx >= len(cur):
                return False
            cur = cur[idx]
            continue
        if not isinstance(cur, dict) or part not in cur:
            return False
        cur = cur[part]
    return True


def has_indexed_parent_path(data, path: str) -> bool:
    cur = data
    for part in parse_path(path):
        if part.isdigit():
            return isinstance(cur, list)
        if not isinstance(cur, dict) or part not in cur:
            return False
        cur = cur[part]
    return False


def main() -> int:
    failed = False
    for chart_dir in sorted(p for p in CHARTS_DIR.iterdir() if p.is_dir()):
        values_path = chart_dir / "values.yaml"
        questions_path = chart_dir / "questions.yaml"
        if not values_path.exists() or not questions_path.exists():
            continue
        values = yaml.safe_load(values_path.read_text(encoding="utf-8")) or {}
        questions = yaml.safe_load(questions_path.read_text(encoding="utf-8")) or {}
        for item in questions.get("questions", []):
            variable = item["variable"]
            if not has_path(values, variable) and not has_indexed_parent_path(values, variable):
                failed = True
                print(f"{chart_dir.name}: missing values path for question variable '{variable}'", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
