#!/usr/bin/env python3
"""Prepare and optionally run question-type probes through the CCF MCP runner."""

from __future__ import annotations

import argparse
import copy
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from build_validation_manifest import curated_manifest


CHART_COMPONENT_ID = "question-types-smoke"
QUESTIONS_PATH = ROOT / "charts" / CHART_COMPONENT_ID / "questions.yaml"
DEFAULT_REPORT = ROOT / "reports" / "question-types-mcp-probe.json"
DEFAULT_CASE_DIR = ROOT / "reports" / "question-types-mcp-cases"


def sanitize_slug(value: str) -> str:
    chars = []
    for char in value.lower():
        if char.isalnum():
            chars.append(char)
        elif chars and chars[-1] != "-":
            chars.append("-")
    return "".join(chars).strip("-")


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


def has_indexed_path(path: str) -> bool:
    return any(part.isdigit() for part in parse_path(path))


def load_questions() -> list[dict[str, Any]]:
    payload = yaml.safe_load(QUESTIONS_PATH.read_text(encoding="utf-8")) or {}
    questions = payload.get("questions", [])
    if not questions:
        raise ValueError(f"No questions found in {QUESTIONS_PATH}.")
    return questions


def probe_value(question: dict[str, Any]) -> tuple[Any, str]:
    qtype = question["type"]
    default = question.get("default")
    if qtype == "string":
        candidate = "bravo" if default != "bravo" else "charlie"
        return candidate, candidate
    if qtype == "enum":
        for option in question.get("options", []):
            if option != default:
                return option, option
        raise ValueError(f"Enum question {question['variable']} has no alternate option.")
    if qtype == "boolean":
        candidate = not bool(default)
        return candidate, "true" if candidate else "false"
    if qtype == "int":
        candidate = int(default if default is not None else 0) + 4
        return candidate, str(candidate)
    if qtype == "listofstrings":
        candidate = ["alpha", "beta", "gamma"]
        if candidate == default:
            candidate = ["delta", "epsilon"]
        return candidate, json.dumps(candidate)
    raise ValueError(f"Unsupported question type: {qtype}")


def build_cases(questions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cases = [
        {
            "caseId": "baseline",
            "label": "Baseline defaults",
            "questionType": None,
            "variable": None,
            "expectedNativeValue": None,
            "serializedValue": None,
            "notes": "No app parameters. Confirms the chart installs through the MCP runner before per-type probes.",
        }
    ]
    for question in questions:
        if has_indexed_path(question["variable"]):
            continue
        native_value, serialized_value = probe_value(question)
        cases.append(
            {
                "caseId": sanitize_slug(question["variable"]),
                "label": question["label"],
                "questionType": question["type"],
                "variable": question["variable"],
                "expectedNativeValue": native_value,
                "serializedValue": serialized_value,
                "notes": f"Override only `{question['variable']}` through the safe non-indexed question-parameter path.",
            }
        )
    return cases


def build_base_target(repository_name: str) -> dict[str, Any]:
    targets = curated_manifest(repository_name=repository_name, component_filter={CHART_COMPONENT_ID})
    if len(targets) != 1:
        raise RuntimeError(f"Expected exactly one manifest target for `{CHART_COMPONENT_ID}`, got {len(targets)}.")
    return targets[0]


def case_manifest(target: dict[str, Any], case: dict[str, Any], namespace_prefix: str) -> dict[str, Any]:
    case_target = copy.deepcopy(target)
    case_slug = sanitize_slug(case["caseId"])
    namespace = f"{namespace_prefix}-{case_slug}"

    case_target["namespace"] = namespace
    case_target["notes"] = f"{target['notes']} Probe case: {case['caseId']}."
    case_target["questionParameters"] = (
        []
        if not case["variable"]
        else [
            {
                "key": case["variable"],
                "value": case["serializedValue"],
                "type": case["questionType"],
                "required": True,
            }
        ]
    )
    unsupported = []
    for variable in case_target.get("unsupportedQuestionParameters", []):
        if variable != case["variable"]:
            unsupported.append(variable)
    case_target["unsupportedQuestionParameters"] = unsupported
    case_target["kubernetesValidation"]["namespace"] = namespace
    case_target["observabilityValidation"]["logs"]["query"] = f'{{namespace="{namespace}"}}'
    for metric in case_target["observabilityValidation"]["metrics"]:
        metric["query"] = metric["query"].replace(target["namespace"], namespace)
    case_target["probeCase"] = {
        "caseId": case["caseId"],
        "label": case["label"],
        "questionType": case["questionType"],
        "variable": case["variable"],
        "expectedNativeValue": case["expectedNativeValue"],
        "serializedValue": case["serializedValue"],
        "notes": case["notes"],
    }
    return {"curated": [case_target]}


def write_case_manifests(
    target: dict[str, Any],
    cases: list[dict[str, Any]],
    case_dir: Path,
    namespace_prefix: str,
) -> list[dict[str, Any]]:
    case_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for case in cases:
        manifest = case_manifest(target, case, namespace_prefix)
        path = case_dir / f"{case['caseId']}.json"
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        written.append({"case": case, "path": path, "manifest": manifest})
    return written


def run_case(case_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(SCRIPT_DIR / "validate-ccf-app.sh"), str(case_path)],
        text=True,
        capture_output=True,
        check=False,
        cwd=str(ROOT),
        env=os.environ.copy(),
    )


def summarize(report: dict[str, Any]) -> dict[str, Any]:
    executed = [case for case in report["cases"] if case.get("runnerInvoked")]
    return {
        "generatedCaseCount": len(report["cases"]),
        "executedCaseCount": len(executed),
        "successfulCases": [case["caseId"] for case in executed if case.get("runnerExitCode") == 0],
        "failedCases": [case["caseId"] for case in executed if case.get("runnerExitCode") != 0],
        "manifestOnlyCases": [case["caseId"] for case in report["cases"] if not case.get("runnerInvoked")],
    }


def render_stdout(report: dict[str, Any]) -> str:
    lines = [
        f"Repository: {report['repositoryName']}",
        f"Component: {report['componentId']}",
        f"Case directory: {report['caseDirectory']}",
        "",
    ]
    for case in report["cases"]:
        if case.get("runnerInvoked"):
            lines.append(f"- {case['caseId']}: exit={case['runnerExitCode']} manifest={case['manifestPath']}")
        else:
            lines.append(f"- {case['caseId']}: manifest-only {case['manifestPath']}")
    summary = report["summary"]
    lines.extend(
        [
            "",
            f"Successful cases: {', '.join(summary['successfulCases']) or 'none'}",
            f"Failed cases: {', '.join(summary['failedCases']) or 'none'}",
            f"Report: {report['outputPath']}",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-name", default=os.environ.get("CCF_REPOSITORY_NAME", "ccf"))
    parser.add_argument("--output", default=str(DEFAULT_REPORT))
    parser.add_argument("--case-dir", default=str(DEFAULT_CASE_DIR))
    parser.add_argument("--namespace-prefix", default="question-types-smoke")
    parser.add_argument("--case", action="append", default=[], help="Limit to specific case IDs, can be passed multiple times.")
    parser.add_argument("--run", action="store_true", help="Invoke validate-ccf-app.sh for each generated case manifest.")
    args = parser.parse_args()

    questions = load_questions()
    cases = build_cases(questions)
    if args.case:
        wanted = set(args.case)
        cases = [case for case in cases if case["caseId"] in wanted]
        if not cases:
            raise ValueError("No probe cases matched --case filters.")

    if args.run and not os.environ.get("MCP_RUNNER_CMD"):
        raise RuntimeError("--run requires MCP_RUNNER_CMD so validate-ccf-app.sh can reach the MCP server.")

    target = build_base_target(args.repository_name)
    case_dir = Path(args.case_dir)
    written_cases = write_case_manifests(target, cases, case_dir, args.namespace_prefix)

    report = {
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repositoryName": args.repository_name,
        "componentId": CHART_COMPONENT_ID,
        "caseDirectory": str(case_dir.resolve()),
        "outputPath": str(Path(args.output).resolve()),
        "cases": [],
    }

    for entry in written_cases:
        case = entry["case"]
        case_report = {
            "caseId": case["caseId"],
            "label": case["label"],
            "questionType": case["questionType"],
            "variable": case["variable"],
            "serializedValue": case["serializedValue"],
            "expectedNativeValue": case["expectedNativeValue"],
            "manifestPath": str(entry["path"].resolve()),
            "runnerInvoked": args.run,
        }
        if args.run:
            result = run_case(entry["path"])
            case_report.update(
                {
                    "runnerExitCode": result.returncode,
                    "runnerStdout": result.stdout,
                    "runnerStderr": result.stderr,
                }
            )
        report["cases"].append(case_report)

    report["summary"] = summarize(report)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(render_stdout(report))
    return 1 if any(case.get("runnerExitCode", 0) != 0 for case in report["cases"] if case.get("runnerInvoked")) else 0


if __name__ == "__main__":
    raise SystemExit(main())
