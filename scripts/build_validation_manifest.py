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

from catalog_data import CURATED_COMPONENTS, component_app_version


VALIDATION_HINTS = {
    "cert-manager": {"waitTimeout": 900},
    "cloudnative-pg": {"waitTimeout": 900},
    "eck-operator": {"waitTimeout": 900},
    "eck-stack": {"prerequisites": ["eck-operator"], "waitTimeout": 900},
    "harbor": {"waitTimeout": 1200},
    "istio": {"waitTimeout": 900},
    "jupyterhub": {"waitTimeout": 1200},
    "openmetadata": {"waitTimeout": 1200},
}
SUPPORTED_CCF_PARAMETER_TYPES = {"string", "enum"}
KUBERNETES_READY_KINDS = ["deployments", "statefulsets", "daemonsets", "jobs"]
KUBERNETES_OBSERVED_KINDS = ["pods", "services", "endpoints", "ingresses", "persistentvolumeclaims"]
KUBERNETES_CLEANUP_KINDS = [
    "pods",
    "services",
    "endpoints",
    "ingresses",
    "persistentvolumeclaims",
    "configmaps",
    "secrets",
]
OBSERVABILITY_LOG_LIMIT = 100


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


def normalize_question_value(item: dict) -> str:
    value = item["default"]
    if item["type"] == "boolean":
        return "true" if value else "false"
    if item["type"] == "int":
        return str(int(value))
    if item["type"] == "listofstrings":
        return json.dumps(value) if value else "[]"
    return str(value)


def question_parameters(component: dict) -> tuple[list[dict], list[str]]:
    supported = []
    unsupported = []
    for item in component["questions"]:
        has_indexed_path = any(part.isdigit() for part in parse_path(item["variable"]))
        if item["type"] in SUPPORTED_CCF_PARAMETER_TYPES and not has_indexed_path:
            supported.append(
                {
                    "key": item["variable"],
                    "value": normalize_question_value(item),
                    "type": item["type"],
                    "required": item["required"],
                }
            )
        else:
            unsupported.append(item["variable"])
    return supported, unsupported


def kubernetes_validation(component: dict) -> dict:
    smoke_profile = component["smoke_profile"]
    return {
        "mode": "kubeconfig",
        "helperScript": "scripts/validate_k8s_resources.py",
        "namespace": component["namespace"],
        "smokeProfile": smoke_profile,
        "skipSmokeChecks": smoke_profile == "manual-only",
        "requiresOperatorOverrides": smoke_profile == "needs-overrides",
        "requiredReadyKinds": KUBERNETES_READY_KINDS,
        "observedKinds": KUBERNETES_OBSERVED_KINDS,
        "cleanup": {
            "preferNamespaceDelete": True,
            "verifyNamespaceDeletion": True,
            "verifyKinds": KUBERNETES_CLEANUP_KINDS,
        },
    }


def observability_validation(component: dict) -> dict:
    namespace = component["namespace"]
    return {
        "mode": "mcp",
        "requiresMonitoring": True,
        "tools": {
            "metricAutocomplete": "autocomplete-project-metrics",
            "metricQuery": "query-project-prometheus-metrics",
            "logQuery": "query-project-loki-logs",
            "logExport": "export-project-loki-logs",
        },
        "logs": {
            "query": f'{{namespace="{namespace}"}}',
            "limit": OBSERVABILITY_LOG_LIMIT,
            "direction": "backward",
        },
        "metrics": [
            {
                "name": "namespaceActive",
                "query": f'kube_namespace_status_phase{{namespace="{namespace}",phase="Active"}}',
            },
            {
                "name": "readyPods",
                "query": f'sum(kube_pod_status_ready{{namespace="{namespace}",condition="true"}})',
            },
            {
                "name": "serviceCount",
                "query": f'count(kube_service_info{{namespace="{namespace}"}})',
            },
            {
                "name": "containerRestarts",
                "query": f'sum(kube_pod_container_status_restarts_total{{namespace="{namespace}"}})',
            },
        ],
        "captureOnFailure": True,
    }


def curated_manifest(repository_name: str, component_filter: set[str] | None = None) -> list[dict]:
    items = []
    for install_order, component in enumerate(CURATED_COMPONENTS, start=1):
        if component_filter and component["id"] not in component_filter:
            continue
        hints = VALIDATION_HINTS.get(component["id"], {})
        safe_question_params, unsupported_question_params = question_parameters(component)
        items.append(
            {
                "kind": "curated",
                "id": component["id"],
                "displayName": component["display_name"],
                "repositoryName": repository_name,
                "packageName": component["package_name"],
                "chartVersion": component.get("chart_version", ""),
                "appVersion": component_app_version(component),
                "namespace": component["namespace"],
                "smokeProfile": component["smoke_profile"],
                "installOrder": install_order,
                "prerequisites": hints.get("prerequisites", []),
                "waitTimeout": hints.get("waitTimeout", 600),
                "questionParameters": safe_question_params,
                "unsupportedQuestionParameters": unsupported_question_params,
                "kubernetesValidation": kubernetes_validation(component),
                "observabilityValidation": observability_validation(component),
                "questionsYaml": f"charts/{component['id']}/questions.yaml",
                "valuesPath": f"charts/{component['id']}/values.yaml",
                "chartPath": f"charts/{component['id']}",
                "readmePath": f"charts/{component['id']}/README.md",
                "notes": component["notes"],
            }
        )
    return items


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository-name",
        default="ccf",
        help="CCF repository name to use for curated chart package resolution",
    )
    parser.add_argument(
        "--component",
        action="append",
        dest="components",
        help="Optional curated component ID to include; can be passed multiple times",
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "reports" / "ccf-validation-manifest.json"),
        help="Path to write the generated manifest",
    )
    args = parser.parse_args()

    component_filter = set(args.components or [])
    payload = {
        "curated": curated_manifest(
            repository_name=args.repository_name,
            component_filter=component_filter or None,
        )
    }

    output = pathlib.Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
