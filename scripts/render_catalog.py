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

from catalog_data import (
    component_access_url,
    CURATED_COMPONENTS,
    DEFAULT_CHART_VERSION,
    EXCLUDED_COMPONENTS,
    component_app_version,
    component_matrix,
    component_release_notes_url,
    component_source_repository,
    parse_path,
)


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
    chart_kind = "wrapper chart" if dependency_items else "standalone chart"

    chart = {
        "apiVersion": "v2",
        "name": component["package_name"],
        "description": (
            f"Curated {component['display_name']} {chart_kind} for the Cloudera Cloud Factory "
            "components catalog."
        ),
        "type": "application",
        "version": component.get("chart_version", DEFAULT_CHART_VERSION),
        "appVersion": component_app_version(component),
        "annotations": {
            "ccf.catalog/source-classification": component["source_classification"],
            "ccf.catalog/source-repository": component_source_repository(component),
            "ccf.catalog/default-namespace": component["namespace"],
            "ccf.catalog/smoke-profile": component["smoke_profile"],
            "ccf.catalog/image-source-choice": component["image_source_choice"],
        },
    }
    if component.get("home"):
        chart["annotations"]["ccf.catalog/home-url"] = component["home"]
    release_notes_url = component_release_notes_url(component)
    if release_notes_url:
        chart["annotations"]["ccf.catalog/release-notes-url"] = release_notes_url
    if dependency_items:
        chart["dependencies"] = dependency_items
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
        "# This file follows the common Rancher-style questions.yaml shape so catalog UIs can\n"
        "# present CCF-friendly prompts.\n"
        + dump_yaml(payload)
    )


def render_chart_readme(component: dict) -> str:
    dependencies = component["dependencies"]
    dependency_lines = "\n".join(
        f"- `{dep['name']}` from `{dep['repository']}` at `{dep['version']}`" for dep in dependencies
    )
    notes = component.get("notes", "").strip()
    home = component.get("home", "").strip()
    release_notes_url = component_release_notes_url(component).strip()
    icon = component.get("icon", "").strip()
    has_dependencies = bool(dependencies)
    purpose = (
        "This chart packages upstream Helm dependencies with curated default values and a "
        "Rancher-style `questions.yaml` so it can be imported and installed more easily in CCF."
        if has_dependencies
        else component.get(
            "standalone_purpose",
            "This chart is maintained directly in this repository so the application can be "
            "installed without depending on upstream Bitnami-backed subcharts.",
        )
    )
    lines = [
        f"# {component['package_name']}",
        "",
        (
            f"Curated `{component['display_name']}` {'wrapper' if has_dependencies else 'standalone'} "
            "chart for the Cloudera Cloud Factory components catalog."
        ),
        "",
        "## Purpose",
        "",
        purpose,
        "",
        "## Upstream Dependencies",
        "",
        dependency_lines if dependency_lines else "This chart has no external Helm dependencies.",
        "",
        "## Defaults",
        "",
        f"- Namespace: `{component['namespace']}`",
        f"- Smoke profile: `{component['smoke_profile']}`",
        f"- Image source choice: `{component['image_source_choice']}`",
        f"- Chart version: `{component.get('chart_version', DEFAULT_CHART_VERSION)}`",
        f"- App version: `{component_app_version(component)}`",
        "",
        "## Notes",
        "",
        notes if notes else "No additional notes.",
        "",
        "## Files",
        "",
        "- `Chart.yaml`: chart metadata and any pinned upstream dependencies",
        "- `values.yaml`: curated default values for CCF environments",
        "- `questions.yaml`: catalog prompts exposed to operators",
        "- `templates/NOTES.txt`: post-install guidance shown by Helm after install or upgrade",
        "",
        "## References",
        "",
        f"- Source repository: `{component_source_repository(component)}`",
    ]
    if home:
        lines.append(f"- Project home: {home}")
    if release_notes_url:
        lines.append(f"- Release notes: {release_notes_url}")
    if icon:
        lines.append(f"- Icon: {icon}")
    return "\n".join(lines) + "\n"


def helm_index_expression(path: str) -> str:
    parts = []
    for part in parse_path(path):
        if part.isdigit():
            parts.append(part)
        else:
            parts.append(f'"{part}"')
    return "(index .Values " + " ".join(parts) + ")"


def helm_and_expression(parts: list[str]) -> str:
    if not parts:
        return "true"
    if len(parts) == 1:
        return parts[0]
    return f'(and {" ".join(parts)})'


def render_access_url_snippet(component: dict) -> str:
    config = component_access_url(component)
    if not config:
        return ""

    enabled_expr = helm_index_expression(config["enable_path"]) if config.get("enable_path") else ""
    explicit_expr = helm_index_expression(config["explicit_url_path"]) if config.get("explicit_url_path") else ""
    host_expr = helm_index_expression(config["host_path"]) if config.get("host_path") else ""
    path_expr = helm_index_expression(config["path_path"]) if config.get("path_path") else ""
    path_default = config.get("path_default", "/")
    tls_expr = helm_index_expression(config["tls_path"]) if config.get("tls_path") else ""

    if explicit_expr:
        guard_parts = [f"(not (empty ({explicit_expr})))"]
        if enabled_expr:
            guard_parts.insert(0, enabled_expr)
        guard = helm_and_expression(guard_parts)
        return dedent(
            f"""\
            {{{{- $accessUrl := "" -}}}}
            {{{{- if {guard} -}}}}
            {{{{- $accessUrl = {explicit_expr} -}}}}
            {{{{- end -}}}}
            {{{{- if $accessUrl }}}}
            Access URL:
              {{{{ $accessUrl }}}}
            {{{{- end }}}}
            """
        )

    if not host_expr:
        return ""

    if config.get("tls_mode") == "bool":
        scheme_expr = f'(ternary "https" "http" {tls_expr})' if tls_expr else '"http"'
    elif config.get("tls_mode") == "list":
        scheme_expr = f'(ternary "https" "http" (gt (len (default (list) {tls_expr})) 0))' if tls_expr else '"http"'
    else:
        scheme_expr = '"http"'

    path_value_expr = f'(default "{path_default}" {path_expr})' if path_expr else f'"{path_default}"'
    guard_parts = [f"(not (empty ({host_expr})))"]
    if enabled_expr:
        guard_parts.insert(0, enabled_expr)
    guard = helm_and_expression(guard_parts)
    return dedent(
        f"""\
        {{{{- $accessUrl := "" -}}}}
        {{{{- if {guard} -}}}}
        {{{{- $accessUrl = printf "%s://%s%s" {scheme_expr} {host_expr} {path_value_expr} -}}}}
        {{{{- end -}}}}
        {{{{- if $accessUrl }}}}
        Access URL:
          {{{{ $accessUrl }}}}
        {{{{- end }}}}
        """
    )


def render_notes_txt(component: dict) -> str:
    packaging_hint = (
        "This curated wrapper chart pins upstream Helm dependencies for easier import into CCF."
        if component["dependencies"]
        else "This standalone chart is maintained directly in this repository to avoid upstream Bitnami-backed subcharts."
    )
    component_note = component.get("notes", "").strip()
    access_url_snippet = render_access_url_snippet(component).strip()
    lines = [
        "{{- $annotations := .Chart.Annotations | default dict -}}",
        "Thank you for installing {{ .Chart.Name }}.",
        "",
        "Release name: {{ .Release.Name }}",
        "Namespace: {{ .Release.Namespace }}",
        "Chart version: {{ .Chart.Version }}",
        "App version: {{ .Chart.AppVersion }}",
        "",
        packaging_hint,
        component_note,
        "",
        "Useful commands:",
        "  helm status {{ .Release.Name }} --namespace {{ .Release.Namespace }}",
        "  helm get all {{ .Release.Name }} --namespace {{ .Release.Namespace }}",
        "  kubectl get pods,svc,ingress -n {{ .Release.Namespace }}",
        "  kubectl get events -n {{ .Release.Namespace }} --sort-by=.lastTimestamp",
    ]
    if access_url_snippet:
        lines.extend(["", access_url_snippet])
    lines.extend(
        [
            "",
            '{{- with (index $annotations "ccf.catalog/source-repository") }}',
            "Source repository:",
            "  {{ . }}",
            "{{- end }}",
            '{{- with (index $annotations "ccf.catalog/home-url") }}',
            "Project home:",
            "  {{ . }}",
            "{{- end }}",
            '{{- with (index $annotations "ccf.catalog/release-notes-url") }}',
            "Release notes:",
            "  {{ . }}",
            "{{- end }}",
        ]
    )
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
        write_text(chart_dir / "templates" / "NOTES.txt", render_notes_txt(component))
    write_text(DOCS_DIR / "catalog-matrix.md", render_catalog_matrix())
    print(
        dedent(
            f"""
            Rendered {len(CURATED_COMPONENTS)} curated charts.
            Updated {DOCS_DIR / 'catalog-matrix.md'}.
            """
        ).strip()
    )


if __name__ == "__main__":
    main()
