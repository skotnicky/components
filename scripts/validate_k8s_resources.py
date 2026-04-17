#!/usr/bin/env python3
"""Run kubeconfig-backed smoke checks and cleanup for CCF validation."""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import time

READY_RESOURCE_KINDS = {
    "deployments": ("availableReplicas", "replicas"),
    "statefulsets": ("readyReplicas", "replicas"),
    "daemonsets": ("numberReady", "desiredNumberScheduled"),
    "jobs": ("succeeded", "completions"),
}
OBSERVED_KINDS = [
    "deployments",
    "statefulsets",
    "daemonsets",
    "jobs",
    "pods",
    "services",
    "endpoints",
    "ingresses",
    "persistentvolumeclaims",
]
CLEANUP_KINDS = [
    "pods",
    "services",
    "endpoints",
    "ingresses",
    "persistentvolumeclaims",
    "configmaps",
    "secrets",
]


def run_kubectl(kubeconfig: str, args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["kubectl", "--kubeconfig", kubeconfig, *args],
        text=True,
        capture_output=True,
        check=check,
    )


def kubectl_json(kubeconfig: str, args: list[str], default: dict | None = None) -> dict:
    result = run_kubectl(kubeconfig, args, check=False)
    if result.returncode != 0:
        if default is not None:
            return default
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "kubectl command failed")
    return json.loads(result.stdout or "{}")


def namespace_exists(kubeconfig: str, namespace: str) -> bool:
    result = run_kubectl(kubeconfig, ["get", "namespace", namespace, "-o", "json"], check=False)
    return result.returncode == 0


def current_context(kubeconfig: str) -> str:
    result = run_kubectl(kubeconfig, ["config", "current-context"])
    return result.stdout.strip()


def can_i(kubeconfig: str, verb: str, resource: str, all_namespaces: bool = False) -> bool:
    args = ["auth", "can-i", verb, resource]
    if all_namespaces:
        args.append("--all-namespaces")
    result = run_kubectl(kubeconfig, args, check=False)
    output = result.stdout.strip().lower()
    if output == "yes":
        return True
    if output == "no":
        return False
    raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "kubectl auth can-i failed")


def load_targets(manifest_path: str | None, components: list[str], namespace: str | None, name: str) -> list[dict]:
    if namespace:
        return [
            {
                "id": name,
                "displayName": name,
                "namespace": namespace,
                "smokeProfile": "default",
                "kubernetesValidation": {
                    "namespace": namespace,
                    "smokeProfile": "default",
                    "skipSmokeChecks": False,
                },
            }
        ]

    if not manifest_path:
        raise ValueError("Either --manifest or --namespace must be provided.")

    payload = json.loads(pathlib.Path(manifest_path).read_text(encoding="utf-8"))
    curated = payload.get("curated", [])
    if components:
        wanted = set(components)
        curated = [item for item in curated if item["id"] in wanted]
    if not curated:
        raise ValueError("No manifest targets matched the requested components.")
    return curated


def summarize_workloads(items: list[dict], ready_field: str, desired_field: str) -> tuple[list[dict], list[dict]]:
    ready = []
    unready = []
    for item in items:
        desired = item.get("spec", {}).get(desired_field)
        if desired is None:
            desired = item.get("status", {}).get(desired_field, 1)
        observed = item.get("status", {}).get(ready_field, 0)
        row = {
            "name": item["metadata"]["name"],
            "ready": observed,
            "desired": desired,
        }
        if observed >= desired:
            ready.append(row)
        else:
            unready.append(row)
    return ready, unready


def summarize_jobs(items: list[dict]) -> tuple[list[dict], list[dict]]:
    ready = []
    unready = []
    for item in items:
        desired = item.get("spec", {}).get("completions", 1)
        observed = item.get("status", {}).get("succeeded", 0)
        conditions = item.get("status", {}).get("conditions", [])
        complete = any(condition.get("type") == "Complete" and condition.get("status") == "True" for condition in conditions)
        row = {
            "name": item["metadata"]["name"],
            "ready": observed,
            "desired": desired,
        }
        if complete or observed >= desired:
            ready.append(row)
        else:
            unready.append(row)
    return ready, unready


def summarize_pods(items: list[dict]) -> list[dict]:
    unhealthy = []
    for item in items:
        phase = item.get("status", {}).get("phase", "")
        if phase not in {"Running", "Succeeded"}:
            unhealthy.append({"name": item["metadata"]["name"], "phase": phase})
            continue
        for status in item.get("status", {}).get("containerStatuses", []):
            waiting = status.get("state", {}).get("waiting", {})
            if waiting.get("reason") in {"CrashLoopBackOff", "ImagePullBackOff", "ErrImagePull"}:
                unhealthy.append({"name": item["metadata"]["name"], "phase": waiting["reason"]})
                break
    return unhealthy


def collect_namespace_resources(kubeconfig: str, namespace: str) -> dict:
    resources: dict[str, dict] = {}
    for kind in OBSERVED_KINDS:
        resources[kind] = kubectl_json(
            kubeconfig,
            ["-n", namespace, "get", kind, "-o", "json", "--ignore-not-found"],
            default={"items": []},
        )
    return resources


def smoke_check_target(kubeconfig: str, target: dict, allow_manual_only: bool) -> dict:
    component_id = target["id"]
    validation = target.get("kubernetesValidation", {})
    namespace = validation.get("namespace") or target["namespace"]
    smoke_profile = validation.get("smokeProfile") or target.get("smokeProfile", "default")

    if smoke_profile == "manual-only" and not allow_manual_only:
        return {
            "component": component_id,
            "namespace": namespace,
            "status": "skipped",
            "reason": "manual-only smoke profile",
        }

    if not namespace_exists(kubeconfig, namespace):
        return {
            "component": component_id,
            "namespace": namespace,
            "status": "failed",
            "reason": "namespace missing",
        }

    resources = collect_namespace_resources(kubeconfig, namespace)
    ready_workloads = []
    unready_workloads = []
    workload_count = 0
    for kind, (ready_field, desired_field) in READY_RESOURCE_KINDS.items():
        items = resources[kind].get("items", [])
        workload_count += len(items)
        if kind == "jobs":
            ready, unready = summarize_jobs(items)
        else:
            ready, unready = summarize_workloads(items, ready_field, desired_field)
        ready_workloads.extend({"kind": kind, **row} for row in ready)
        unready_workloads.extend({"kind": kind, **row} for row in unready)

    unhealthy_pods = summarize_pods(resources["pods"].get("items", []))
    services = len(resources["services"].get("items", []))
    endpoints = len(resources["endpoints"].get("items", []))
    ingresses = len(resources["ingresses"].get("items", []))
    pvcs = len(resources["persistentvolumeclaims"].get("items", []))

    failures = []
    warnings = []
    if workload_count == 0:
        failures.append("no workloads found in namespace")
    if unready_workloads:
        failures.append("unready workloads present")
    if unhealthy_pods:
        failures.append("unhealthy pods present")
    if services == 0:
        warnings.append("no services found")
    if endpoints == 0:
        warnings.append("no endpoints found")

    return {
        "component": component_id,
        "namespace": namespace,
        "status": "passed" if not failures else "failed",
        "smokeProfile": smoke_profile,
        "failures": failures,
        "warnings": warnings,
        "summary": {
            "workloads": workload_count,
            "readyWorkloads": ready_workloads,
            "unreadyWorkloads": unready_workloads,
            "unhealthyPods": unhealthy_pods,
            "services": services,
            "endpoints": endpoints,
            "ingresses": ingresses,
            "persistentVolumeClaims": pvcs,
        },
    }


def cleanup_summary(kubeconfig: str, namespace: str) -> dict:
    summary: dict[str, int] = {}
    for kind in CLEANUP_KINDS:
        payload = kubectl_json(
            kubeconfig,
            ["-n", namespace, "get", kind, "-o", "json", "--ignore-not-found"],
            default={"items": []},
        )
        summary[kind] = len(payload.get("items", []))
    return summary


def wait_for_namespace_deletion(kubeconfig: str, namespace: str, timeout_seconds: int) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if not namespace_exists(kubeconfig, namespace):
            return True
        time.sleep(2)
    return False


def cleanup_target(kubeconfig: str, target: dict, delete_namespace: bool, timeout_seconds: int) -> dict:
    component_id = target["id"]
    validation = target.get("kubernetesValidation", {})
    namespace = validation.get("namespace") or target["namespace"]

    if not namespace_exists(kubeconfig, namespace):
        return {
            "component": component_id,
            "namespace": namespace,
            "status": "passed",
            "summary": {"namespacePresent": False, "residuals": {}},
        }

    before = cleanup_summary(kubeconfig, namespace)
    deleted = False
    if delete_namespace:
        run_kubectl(kubeconfig, ["delete", "namespace", namespace, "--wait=false"])
        deleted = wait_for_namespace_deletion(kubeconfig, namespace, timeout_seconds)

    if not namespace_exists(kubeconfig, namespace):
        return {
            "component": component_id,
            "namespace": namespace,
            "status": "passed",
            "summary": {"namespacePresent": False, "deletedNamespace": deleted, "residuals": {}},
        }

    after = cleanup_summary(kubeconfig, namespace)
    residuals = {kind: count for kind, count in after.items() if count}
    return {
        "component": component_id,
        "namespace": namespace,
        "status": "failed" if residuals else "passed",
        "summary": {
            "namespacePresent": True,
            "deletedNamespace": deleted,
            "before": before,
            "residuals": residuals,
        },
    }


def print_result(phase: str, result: dict) -> None:
    component = result.get("component", "cluster")
    status = result["status"]
    namespace = result.get("namespace")
    prefix = f"[{phase}] {component}"
    if namespace:
        prefix = f"{prefix} ({namespace})"
    print(f"{prefix}: {status}")
    if result.get("reason"):
        print(f"  reason: {result['reason']}")
    for item in result.get("failures", []):
        print(f"  failure: {item}")
    for item in result.get("warnings", []):
        print(f"  warning: {item}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", help="Validation manifest or shard manifest path")
    parser.add_argument("--component", action="append", default=[], help="Component ID to select from the manifest")
    parser.add_argument("--namespace", help="Direct namespace target for ad-hoc checks")
    parser.add_argument("--name", default="adhoc", help="Synthetic target name used with --namespace")
    parser.add_argument("--kubeconfig", required=True, help="Path to kubeconfig file")
    parser.add_argument(
        "--phase",
        required=True,
        choices=["preflight", "smoke", "cleanup"],
        help="Validation phase to execute",
    )
    parser.add_argument("--delete-namespace", action="store_true", help="Delete the namespace during cleanup")
    parser.add_argument(
        "--namespace-timeout",
        type=int,
        default=180,
        help="Seconds to wait for namespace deletion during cleanup",
    )
    parser.add_argument(
        "--allow-manual-only",
        action="store_true",
        help="Run smoke checks for manual-only targets instead of skipping them",
    )
    parser.add_argument("--report", help="Optional JSON report output path")
    args = parser.parse_args()

    kubeconfig = str(pathlib.Path(args.kubeconfig).resolve())
    results: list[dict]

    if args.phase == "preflight":
        targets = load_targets(args.manifest, args.component, args.namespace, args.name)
        context = current_context(kubeconfig)
        results = [
            {
                "component": "cluster",
                "status": "passed",
                "context": context,
                "targets": [target["id"] for target in targets],
                "permissions": {
                    "getNamespaces": can_i(kubeconfig, "get", "namespaces"),
                    "getPodsAllNamespaces": can_i(kubeconfig, "get", "pods", all_namespaces=True),
                    "deleteNamespaces": can_i(kubeconfig, "delete", "namespaces"),
                },
            }
        ]
    else:
        targets = load_targets(args.manifest, args.component, args.namespace, args.name)
        if args.phase == "smoke":
            results = [smoke_check_target(kubeconfig, target, args.allow_manual_only) for target in targets]
        else:
            results = [
                cleanup_target(kubeconfig, target, args.delete_namespace, args.namespace_timeout)
                for target in targets
            ]

    for result in results:
        print_result(args.phase, result)

    if args.report:
        report_path = pathlib.Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps({"phase": args.phase, "results": results}, indent=2) + "\n", encoding="utf-8")

    failed = [item for item in results if item["status"] == "failed"]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
