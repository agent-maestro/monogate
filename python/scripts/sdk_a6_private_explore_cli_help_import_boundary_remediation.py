#!/usr/bin/env python3
"""SDK-A6 private explore CLI help import-boundary remediation implementation."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import sdk_a5_private_explore_cli_help_import_boundary_contract as sdk_a5  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_explore_cli_help_import_boundary_remediation.v0"
STATUS = "SDK_A6_PRIVATE_EXPLORE_CLI_HELP_IMPORT_BOUNDARY_REMEDIATION_PASS"

TRUE_CLAIM_FLAGS = {
    "sdk_a5_consumed",
    "sdk_implementation_changed",
    "explore_cli_import_boundary_remediated",
    "help_boundary_obligations_executed",
    "dependency_gate_obligations_checked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "sdk_a5_consumed": True,
    "sdk_implementation_changed": True,
    "explore_cli_import_boundary_remediated": True,
    "help_boundary_obligations_executed": True,
    "dependency_gate_obligations_checked": True,
    "d109_hold_respected": True,
    "optional_dependency_installed": False,
    "public_package_install_executed": False,
    "sdk_stability_claim": False,
    "sdk_public_ready": False,
    "public_readiness_claim": False,
    "public_copy_approved": False,
    "public_package_release_claim": False,
    "api_compatibility_claim": False,
    "semantic_versioning_commitment": False,
    "compiler_correctness_claim": False,
    "semantic_preservation_claim": False,
    "runtime_performance_claim": False,
    "training_savings_claim": False,
    "estimator_accuracy_claim": False,
    "hardware_readiness_claim": False,
    "silicon_readiness_claim": False,
    "electronics_repo_touched": False,
    "laptop_owned_repo_touched": False,
    "d110_started": False,
    "reviewer_response_consumed": False,
    "reviewer_approval_recorded": False,
    "broad_eml_advantage_claim": False,
    "benchmark_executed": False,
    "forge_emit_check_executed": False,
}

NON_CLAIMS = [
    "SDK-A6 implements only the private explore CLI import-boundary remediation described by SDK-A5.",
    "SDK-A6 does not install optional dependencies, build native extensions, install public packages, or claim installed-extra behavior.",
    "SDK-A6 does not claim SDK stability, public readiness, public package release readiness, API compatibility, or semantic-versioning commitments.",
    "SDK-A6 does not claim compiler correctness, semantic preservation, runtime performance, training savings, estimator accuracy, hardware readiness, silicon readiness, or broad EML advantage.",
    "SDK-A6 respects the D109 hold and does not start D110, consume reviewer response, or touch laptop-owned electronics repositories.",
]


def load_sdk_a5_result() -> dict[str, Any]:
    path = (
        ROOT
        / "python/results/sdk_a5_private_explore_cli_help_import_boundary_contract"
        / f"sdk_a5_private_explore_cli_help_import_boundary_contract_{STAMP}.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    sdk_a5.validate_payload(payload)
    return payload


def _env() -> dict[str, str]:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = f"{PYTHON_ROOT}{os.pathsep}{existing}" if existing else str(PYTHON_ROOT)
    return env


def _run(command_id: str, argv: list[str], expected: str) -> dict[str, Any]:
    proc = subprocess.run(
        argv,
        cwd=ROOT,
        env=_env(),
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    combined = f"{proc.stdout}\n{proc.stderr}"
    if expected == "help_pass":
        result = proc.returncode == 0 and "usage:" in proc.stdout and "Traceback" not in combined
    elif expected == "version_pass":
        result = proc.returncode == 0 and "monogate-explore" in proc.stdout and "Traceback" not in combined
    elif expected == "pass_or_dependency_gate":
        result = (
            (proc.returncode == 0)
            or (
                proc.returncode == 2
                and "optional dependency" in combined
                and "install monogate[cli]" in combined
            )
        ) and "Traceback" not in combined
    else:
        raise ValueError(f"unknown expected mode: {expected}")
    return {
        "commandId": command_id,
        "argv": argv,
        "expectedMode": expected,
        "returnCode": proc.returncode,
        "resultStatus": "pass" if result else "fail",
        "stdoutPreview": proc.stdout[:500],
        "stderrPreview": proc.stderr[:500],
    }


def command_results() -> list[dict[str, Any]]:
    py = sys.executable
    return [
        _run("top_level_help_no_optional_substrate_import", [py, "-m", "monogate.cli.explore", "--help"], "help_pass"),
        _run("top_level_version_no_optional_substrate_import", [py, "-m", "monogate.cli.explore", "--version"], "version_pass"),
        _run("subcommand_help_no_optional_substrate_import", [py, "-m", "monogate.cli.explore", "witness", "--help"], "help_pass"),
        _run("witness_command_dependency_gate", [py, "-m", "monogate.cli.explore", "witness", "exp(x)"], "pass_or_dependency_gate"),
        _run("analyze_command_dependency_gate", [py, "-m", "monogate.cli.explore", "analyze", "exp(x)"], "pass_or_dependency_gate"),
        _run("identify_command_dependency_gate", [py, "-m", "monogate.cli.explore", "identify", "exp(x)"], "pass_or_dependency_gate"),
    ]


def build_payload() -> dict[str, Any]:
    source = load_sdk_a5_result()
    results = command_results()
    help_results = results[:3]
    gate_results = results[3:]
    summary = {
        "sourceArtifact": source["artifactId"],
        "implementationChangedFiles": ["python/monogate/cli/explore.py"],
        "testFilesAdded": ["python/tests/test_cli_explore_import_boundary.py"],
        "helpBoundaryCommandCount": len(help_results),
        "dependencyGateCommandCount": len(gate_results),
        "helpBoundaryPassCount": sum(1 for item in help_results if item["resultStatus"] == "pass"),
        "dependencyGatePassCount": sum(1 for item in gate_results if item["resultStatus"] == "pass"),
        "optionalDependencyInstalled": False,
        "publicReadinessClaim": False,
        "sdkStabilityClaim": False,
        "nextRecommendedArtifact": "SDK-A7 private SDK smoke chain refresh after explore CLI remediation",
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="sdk-a6-private-explore-cli-help-import-boundary-remediation",
        artifact_type="private_explore_cli_help_import_boundary_remediation",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "commandResults": results,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifact"] != "sdk-a5-private-explore-cli-help-import-boundary-contract":
        raise ValueError("SDK-A6 must consume SDK-A5")
    summary = payload["summary"]
    if summary["implementationChangedFiles"] != ["python/monogate/cli/explore.py"]:
        raise ValueError("unexpected implementation file set")
    if summary["helpBoundaryCommandCount"] != 3 or summary["dependencyGateCommandCount"] != 3:
        raise ValueError("command count drift")
    if summary["helpBoundaryPassCount"] != 3 or summary["dependencyGatePassCount"] != 3:
        raise ValueError("all SDK-A6 commands must pass")
    for key in ["optionalDependencyInstalled", "publicReadinessClaim", "sdkStabilityClaim"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    for result in payload["commandResults"]:
        if result["resultStatus"] != "pass":
            raise ValueError(f"{result['commandId']} failed")
        if "Traceback" in f"{result['stdoutPreview']}\n{result['stderrPreview']}":
            raise ValueError(f"{result['commandId']} leaked a traceback")
    for key in TRUE_CLAIM_FLAGS:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return build_evidence_packet(
        artifact_id=payload["artifactId"],
        artifact_type=payload["artifactType"],
        semantic_strength="private_import_boundary_remediation_command_evidence",
        source=f"python/results/sdk_a6_private_explore_cli_help_import_boundary_remediation/sdk_a6_private_explore_cli_help_import_boundary_remediation_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="sdk_a6_private_explore_cli_help_import_boundary_remediation_feed",
        date=DATE,
        status=payload["status"],
        next_action="Refresh the private SDK smoke chain after the explore CLI import-boundary remediation.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "implementationChangedFiles": payload["summary"]["implementationChangedFiles"],
            "helpBoundaryPassCount": payload["summary"]["helpBoundaryPassCount"],
            "dependencyGatePassCount": payload["summary"]["dependencyGatePassCount"],
            "sdkStabilityClaim": payload["summary"]["sdkStabilityClaim"],
            "publicReadinessClaim": payload["summary"]["publicReadinessClaim"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="SDK-A6 Private Explore CLI Help Import-Boundary Remediation",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("implementation changed files", ", ".join(payload["summary"]["implementationChangedFiles"])),
            ("help boundary pass count", payload["summary"]["helpBoundaryPassCount"]),
            ("dependency gate pass count", payload["summary"]["dependencyGatePassCount"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Command Results",
                [
                    f"- `{item['commandId']}`: `{item['resultStatus']}` (return code `{item['returnCode']}`)"
                    for item in payload["commandResults"]
                ],
            ),
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"sdk_a6_private_explore_cli_help_import_boundary_remediation_{STAMP}.json"
    report_path = report_dir / f"sdk_a6_private_explore_cli_help_import_boundary_remediation_{STAMP}.md"
    evidence_path = evidence_dir / "sdk_a6_private_explore_cli_help_import_boundary_remediation.json"
    feed_path = command_feed_dir / f"sdk_a6_private_explore_cli_help_import_boundary_remediation_feed_{STAMP}.json"
    write_json(result_path, payload)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(payload), encoding="utf-8")
    write_json(evidence_path, evidence)
    write_json(feed_path, feed)
    return {
        "payload": payload,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/sdk_a6_private_explore_cli_help_import_boundary_remediation")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    validate_payload(payload)
    if args.build:
        build_outputs(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    print("SDK_A6_PRIVATE_EXPLORE_CLI_HELP_IMPORT_BOUNDARY_REMEDIATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
