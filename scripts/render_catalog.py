#!/usr/bin/env python3
"""Generate curated wrapper charts and catalog matrix docs from shared metadata."""

from __future__ import annotations

import pathlib
import sys
from textwrap import dedent

import yaml

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from catalog_data import CURATED_COMPONENTS, DEFAULT_CHART_VERSION, EXCLUDED_COMPONENTS, component_matrix


CHARTS_DIR = ROOT / "charts"
DOCS_DIR = ROOT / "docs"


def dump_yaml(data: object) -> str:
    return yaml.safe_dump(data, sort_keys=False, default_flow_style=False)


def render_chart_yaml(component: dict) -> str:
    dependency_items = []
    for dep in component["dependencies"]:
        item = {
            "name": dep["name"],
            "repository": dep["repository"],
            "version": dep["version"],
        }
        dependency_items.append(item)

    chart = {
        "apiVersion": "v2",
        "name": component["package_name"],
        "description": (
            f"Curated {component['display_name']} wrapper chart for the Cloudera Cloud Factory "
            "components catalog."
        ),
        "type": "application",
        "version": component.get("chart_version", DEFAULT_CHART_VERSION),
        "appVersion": component["dependencies"][0]["app_version"] or component["dependencies"][0]["version"],
        "annotations": {
            "ccf.catalog/source-classification": component["source_classification"],
            "ccf.catalog/source-repository": component["dependencies"][0]["repository"],
            "ccf.catalog/default-namespace": component["namespace"],
            "ccf.catalog/smoke-profile": component["smoke_profile"],
            "ccf.catalog/image-source-choice": component["image_source_choice"],
        },
        "dependencies": dependency_items,
    }
    if component.get("home"):
        chart["home"] = component["home"]
    if component.get("icon"):
        chart["icon"] = component["icon"]
    return (
        "# Generated from scripts/catalog_data.py. Edit metadata there and re-run "
        "scripts/render_catalog.py.\n"
        + dump_yaml(chart)
    )


def render_values_yaml(component: dict) -> str:
    return (
        "# Generated from scripts/catalog_data.py. Adjust the shared metadata instead of "
        "editing this file by hand.\n"
        + dump_yaml(component["values"])
    )


def render_questions_yaml(component: dict) -> str:
    questions = []
    for item in component["questions"]:
        record = {
            "variable": item["variable"],
            "label": item["label"],
            "type": item["type"],
            "default": item["default"],
            "description": item["description"],
            "group": item["group"],
            "required": item["required"],
        }
        if "options" in item:
            record["options"] = item["options"]
        questions.append(record)
    payload = {"questions": questions}
    return (
        "# Generated from scripts/catalog_data.py.\n"
        "# This file follows the common Rancher-style questions.yaml shape so catalog "
        "UIs can present CCF-friendly prompts.\n"
        + dump_yaml(payload)
    )


def render_chart_readme(component: dict) -> str:
    dependency_lines = "\n".join(
        f"- `{dep['name']}` from `{dep['repository']}` at `{dep['version']}`"
        for dep in component["dependencies"]
    )
    notes = component.get("notes", "").strip()
    home = component.get("home", "").strip()
    icon = component.get("icon", "").strip()
    lines = [
        f"# {component['package_name']}",
        "",
        f"Curated `{component['display_name']}` wrapper chart for the Cloudera Cloud Factory components catalog.",
        "",
        "## Purpose",
        "",
        "This chart packages upstream Helm dependencies with curated default values and a Rancher-style",
        "`questions.yaml` so it can be imported and installed more easily in CCF.",
        "",
        "## Upstream Dependencies",
        "",
        dependency_lines,
        "",
        "## Defaults",
        "",
        f"- Namespace: `{component['namespace']}`",
        f"- Smoke profile: `{component['smoke_profile']}`",
        f"- Image source choice: `{component['image_source_choice']}`",
        f"- Chart version: `{component.get('chart_version', DEFAULT_CHART_VERSION)}`",
        f"- Upstream app version: `{component['dependencies'][0]['app_version'] or component['dependencies'][0]['version']}`",
        "",
        "## Notes",
        "",
        notes if notes else "No additional notes.",
        "",
        "## Files",
        "",
        "- `Chart.yaml`: wrapper metadata and pinned upstream dependencies",
        "- `values.yaml`: curated default values for CCF environments",
        "- `questions.yaml`: catalog prompts exposed to operators",
        "",
        "## References",
        "",
        f"- Upstream repository: `{component['dependencies'][0]['repository']}`",
    ]
    if home:
        lines.append(f"- Project home: {home}")
    if icon:
        lines.append(f"- Icon: {icon}")
    return "\n".join(lines) + "\n"


def render_catalog_matrix() -> str:
    rows = component_matrix()
    header = [
        "# Catalog Matrix",
        "",
        "Generated from `scripts/catalog_data.py` to keep the curated catalog, validation, and "
        "automation flows aligned.",
        "",
        "## Curated Wrappers And Exclusions",
        "",
        "| Component | Packaged Chart | Upstream Source | Version | Namespace | Classification | Packaging | Questions | Smoke Profile | Images | Notes |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        header.append(
            "| {requested_component} | {packaged_chart_name} | `{upstream_chart_source}` | "
            "{pinned_version} | `{default_namespace}` | {source_classification} | "
            "{packaging_mode} | {questions_yaml_support} | {ccf_smoke_test_profile} | "
            "{image_source_choice} | {notes} |".format(**row)
        )
    header.extend(["", "## Explicit Exclusions", "",])
    for item in EXCLUDED_COMPONENTS:
        header.append(f"- `{item['id']}`: {item['reason']}")
    header.append("")
    return "\n".join(header)


def ensure_dirs() -> None:
    CHARTS_DIR.mkdir(exist_ok=True)
    DOCS_DIR.mkdir(exist_ok=True)


def write_text(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    for component in CURATED_COMPONENTS:
        chart_dir = CHARTS_DIR / component["id"]
        chart_dir.mkdir(parents=True, exist_ok=True)
        write_text(chart_dir / "Chart.yaml", render_chart_yaml(component))
        write_text(chart_dir / "values.yaml", render_values_yaml(component))
        write_text(chart_dir / "questions.yaml", render_questions_yaml(component))
        write_text(chart_dir / "README.md", render_chart_readme(component))
    write_text(DOCS_DIR / "catalog-matrix.md", render_catalog_matrix())
    print(
        dedent(
            f"""
            Rendered {len(CURATED_COMPONENTS)} curated wrapper charts.
            Updated {DOCS_DIR / 'catalog-matrix.md'}.
            """
        ).strip()
    )


if __name__ == "__main__":
    main()
