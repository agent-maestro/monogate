#!/usr/bin/env python3
"""SDK-A5 private explore CLI help import-boundary remediation contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import sdk_a4_private_sdk_smoke_result_review_selector as sdk_a4  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_explore_cli_help_import_boundary_contract.v0"
STATUS = "SDK_A5_PRIVATE_EXPLORE_CLI_HELP_IMPORT_BOUNDARY_CONTRACT_PASS"

TRUE_CLAIM_FLAGS = {
    "sdk_a4_consumed",
    "remediation_contract_created",
    "help_boundary_obligations_recorded",
    "dependency_gate_obligations_recorded",
    "next_action_selected",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "sdk_a4_consumed": True,
    "remediation_contract_created": True,
    "help_boundary_obligations_recorded": True,
    "dependency_gate_obligations_recorded": True,
    "next_action_selected": True,
    "d109_hold_respected": True,
    "sdk_implementation_changed": False,
    "explore_cli_remediated": False,
    "remediation_test_executed": False,
    "smoke_probe_rerun": False,
    "optional_dependency_installed": False,
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
    "public_package_install_executed": False,
    "benchmark_executed": False,
    "forge_emit_check_executed": False,
}

NON_CLAIMS = [
    "SDK-A5 is a private remediation contract; it does not change SDK implementation or remediate the explore CLI.",
    "SDK-A5 does not execute remediation tests, rerun smoke probes, install optional dependencies, build native extensions, or install public packages.",
    "SDK-A5 does not claim SDK stability, public readiness, public package release readiness, API compatibility, or semantic-versioning commitments.",
    "SDK-A5 does not claim compiler correctness, semantic preservation, runtime performance, training savings, estimator accuracy, hardware readiness, silicon readiness, or broad EML advantage.",
    "SDK-A5 respects the D109 hold and does not start D110, consume reviewer response, or touch laptop-owned electronics repositories.",
]


def load_sdk_a4_result() -> dict[str, Any]:
    path = (
        ROOT
        / "python/results/sdk_a4_private_sdk_smoke_result_review_selector"
        / f"sdk_a4_private_sdk_smoke_result_review_selector_{STAMP}.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    sdk_a4.validate_payload(payload)
    return payload


def help_boundary_obligations() -> list[dict[str, Any]]:
    return [
        {
            "obligationId": "top_level_help_no_optional_substrate_import",
            "targetCommandShape": "PYTHONPATH=python python -m monogate.cli.explore --help",
            "intendedSignal": "exits 0 and prints top-level usage without optional substrate imports at module import time",
            "requiredForRemediation": True,
        },
        {
            "obligationId": "top_level_version_no_optional_substrate_import",
            "targetCommandShape": "PYTHONPATH=python python -m monogate.cli.explore --version",
            "intendedSignal": "exits 0 and prints version text without optional substrate imports",
            "requiredForRemediation": True,
        },
        {
            "obligationId": "subcommand_help_no_optional_substrate_import",
            "targetCommandShape": "PYTHONPATH=python python -m monogate.cli.explore witness --help",
            "intendedSignal": "exits 0 and prints subcommand help without optional substrate imports",
            "requiredForRemediation": True,
        },
    ]


def dependency_gate_obligations() -> list[dict[str, Any]]:
    return [
        {
            "obligationId": "witness_command_dependency_gate",
            "targetCommandShape": "PYTHONPATH=python python -m monogate.cli.explore witness 'exp(x)'",
            "intendedSignal": "if optional substrate packages are absent, returns a clear dependency-gate error rather than a raw import traceback",
            "blockedInterpretation": "This does not claim witness correctness or compiler correctness.",
        },
        {
            "obligationId": "analyze_command_dependency_gate",
            "targetCommandShape": "PYTHONPATH=python python -m monogate.cli.explore analyze 'exp(x)'",
            "intendedSignal": "if optional substrate packages are absent, returns a clear dependency-gate error rather than a raw import traceback",
            "blockedInterpretation": "This does not claim analysis correctness or runtime performance.",
        },
        {
            "obligationId": "identify_command_dependency_gate",
            "targetCommandShape": "PYTHONPATH=python python -m monogate.cli.explore identify 'exp(x)'",
            "intendedSignal": "if optional substrate packages are absent, returns a clear dependency-gate error rather than a raw import traceback",
            "blockedInterpretation": "This does not claim registry completeness or semantic preservation.",
        },
    ]


def blocked_paths() -> list[dict[str, str]]:
    return [
        {
            "blockedPathId": "public_release_readiness_from_help_fix",
            "reason": "A help import-boundary fix would not prove the SDK is stable or public-release ready.",
        },
        {
            "blockedPathId": "install_optional_extras_in_contract",
            "reason": "SDK-A5 records source-tree behavior obligations only; installed-extra smoke belongs in a later bounded artifact.",
        },
        {
            "blockedPathId": "claim_explore_semantics",
            "reason": "The contract concerns import boundaries and dependency gates, not command semantic correctness.",
        },
        {
            "blockedPathId": "touch_laptop_owned_repos",
            "reason": "The laptop/electronics repos are outside this research-side SDK remediation lane.",
        },
    ]


def build_payload() -> dict[str, Any]:
    source = load_sdk_a4_result()
    help_obligations = help_boundary_obligations()
    gate_obligations = dependency_gate_obligations()
    blocked = blocked_paths()
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceFindingClassification": source["summary"]["findingClassification"],
        "helpBoundaryObligationCount": len(help_obligations),
        "dependencyGateObligationCount": len(gate_obligations),
        "blockedPathCount": len(blocked),
        "sdkImplementationChanged": False,
        "exploreCliRemediated": False,
        "remediationTestExecuted": False,
        "smokeProbeRerun": False,
        "optionalDependencyInstalled": False,
        "publicReadinessClaim": False,
        "sdkStabilityClaim": False,
        "nextRecommendedArtifact": "SDK-A6 private explore CLI help import-boundary remediation implementation",
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="sdk-a5-private-explore-cli-help-import-boundary-contract",
        artifact_type="private_explore_cli_help_import_boundary_contract",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "helpBoundaryObligations": help_obligations,
            "dependencyGateObligations": gate_obligations,
            "blockedPaths": blocked,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifact"] != "sdk-a4-private-sdk-smoke-result-review-selector":
        raise ValueError("SDK-A5 must consume SDK-A4")
    summary = payload["summary"]
    if summary["sourceFindingClassification"] != "optional_dependency_import_boundary":
        raise ValueError("SDK-A5 must preserve SDK-A4 finding classification")
    if summary["helpBoundaryObligationCount"] != 3:
        raise ValueError("help boundary obligation count drift")
    if summary["dependencyGateObligationCount"] != 3:
        raise ValueError("dependency gate obligation count drift")
    if summary["blockedPathCount"] != 4:
        raise ValueError("blocked path count drift")
    for key in [
        "sdkImplementationChanged",
        "exploreCliRemediated",
        "remediationTestExecuted",
        "smokeProbeRerun",
        "optionalDependencyInstalled",
        "publicReadinessClaim",
        "sdkStabilityClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    help_ids = {item["obligationId"] for item in payload["helpBoundaryObligations"]}
    if help_ids != {
        "top_level_help_no_optional_substrate_import",
        "top_level_version_no_optional_substrate_import",
        "subcommand_help_no_optional_substrate_import",
    }:
        raise ValueError("unexpected help obligation set")
    gate_ids = {item["obligationId"] for item in payload["dependencyGateObligations"]}
    if gate_ids != {
        "witness_command_dependency_gate",
        "analyze_command_dependency_gate",
        "identify_command_dependency_gate",
    }:
        raise ValueError("unexpected dependency gate obligation set")
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
        semantic_strength="private_remediation_contract_no_implementation_or_execution",
        source=f"python/results/sdk_a5_private_explore_cli_help_import_boundary_contract/sdk_a5_private_explore_cli_help_import_boundary_contract_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="sdk_a5_private_explore_cli_help_import_boundary_contract_feed",
        date=DATE,
        status=payload["status"],
        next_action="Implement SDK-A6 private explore CLI help import-boundary remediation against the SDK-A5 contract.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "helpBoundaryObligationCount": payload["summary"]["helpBoundaryObligationCount"],
            "dependencyGateObligationCount": payload["summary"]["dependencyGateObligationCount"],
            "sdkImplementationChanged": payload["summary"]["sdkImplementationChanged"],
            "exploreCliRemediated": payload["summary"]["exploreCliRemediated"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="SDK-A5 Private Explore CLI Help Import-Boundary Contract",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("help boundary obligations", payload["summary"]["helpBoundaryObligationCount"]),
            ("dependency gate obligations", payload["summary"]["dependencyGateObligationCount"]),
            ("blocked paths", payload["summary"]["blockedPathCount"]),
            ("SDK implementation changed", payload["summary"]["sdkImplementationChanged"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Help Boundary Obligations",
                [
                    f"- `{item['obligationId']}`: {item['targetCommandShape']}"
                    for item in payload["helpBoundaryObligations"]
                ],
            ),
            (
                "Dependency Gate Obligations",
                [
                    f"- `{item['obligationId']}`: {item['targetCommandShape']}"
                    for item in payload["dependencyGateObligations"]
                ],
            ),
            (
                "Blocked Paths",
                [f"- `{item['blockedPathId']}`: {item['reason']}" for item in payload["blockedPaths"]],
            ),
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"sdk_a5_private_explore_cli_help_import_boundary_contract_{STAMP}.json"
    report_path = report_dir / f"sdk_a5_private_explore_cli_help_import_boundary_contract_{STAMP}.md"
    evidence_path = evidence_dir / "sdk_a5_private_explore_cli_help_import_boundary_contract.json"
    feed_path = command_feed_dir / f"sdk_a5_private_explore_cli_help_import_boundary_contract_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/sdk_a5_private_explore_cli_help_import_boundary_contract")
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
    print("SDK_A5_PRIVATE_EXPLORE_CLI_HELP_IMPORT_BOUNDARY_CONTRACT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
