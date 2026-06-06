#!/usr/bin/env python3
"""SDK-A4 private SDK smoke result review and explore CLI surface selector."""

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

from scripts import sdk_a3_private_sdk_import_cli_smoke_dry_run as sdk_a3  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_sdk_smoke_result_review_selector.v0"
STATUS = "SDK_A4_PRIVATE_SDK_SMOKE_RESULT_REVIEW_SELECTOR_PASS"
SDK_A3_RESULT_PATH = (
    ROOT
    / "python/results/sdk_a3_private_sdk_import_cli_smoke_dry_run"
    / f"sdk_a3_private_sdk_import_cli_smoke_dry_run_{STAMP}.json"
)

TRUE_CLAIM_FLAGS = {
    "sdk_a3_consumed",
    "smoke_finding_reviewed",
    "explore_cli_finding_classified",
    "next_action_selected",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "sdk_a3_consumed": True,
    "smoke_finding_reviewed": True,
    "explore_cli_finding_classified": True,
    "next_action_selected": True,
    "d109_hold_respected": True,
    "sdk_implementation_changed": False,
    "explore_cli_remediated": False,
    "smoke_probe_rerun": False,
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
    "SDK-A4 reviews the private SDK-A3 smoke finding; it does not change SDK implementation or remediate the explore CLI.",
    "SDK-A4 does not rerun smoke probes, build native extensions, install optional dependencies, or install public packages.",
    "SDK-A4 does not claim SDK stability, public readiness, public package release readiness, API compatibility, or semantic-versioning commitments.",
    "SDK-A4 does not claim compiler correctness, semantic preservation, runtime performance, training savings, estimator accuracy, hardware readiness, silicon readiness, or broad EML advantage.",
    "SDK-A4 respects the D109 hold and does not start D110, consume reviewer response, or touch laptop-owned electronics repositories.",
]


def load_sdk_a3_result(path: Path = SDK_A3_RESULT_PATH) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    sdk_a3.validate_payload(payload)
    return payload


def finding_review(source: dict[str, Any]) -> dict[str, Any]:
    cli_results = {result["probeId"]: result for result in source["cliProbeResults"]}
    explore = cli_results["cli_monogate_explore_help"]
    return {
        "findingId": "sdk_a3_cli_monogate_explore_help_required_probe_failed",
        "sourceProbeId": explore["probeId"],
        "sourceResultStatus": explore["resultStatus"],
        "classification": "optional_dependency_import_boundary",
        "observedSignal": "monogate.cli.explore imports eml_discover at module import time, so --help fails when only PYTHONPATH=python is supplied.",
        "packagingContext": [
            "python/pyproject.toml lists eml-discover under the witness optional dependency extra.",
            "python/pyproject.toml defines the cli optional dependency extra as monogate[witness] plus eml-graph.",
            "SDK-A3 used the private source-tree smoke path rather than installing optional extras.",
        ],
        "blockedInterpretations": [
            "Do not interpret this as SDK instability.",
            "Do not interpret this as public package release readiness failure.",
            "Do not interpret this as compiler correctness, semantic preservation, or runtime performance evidence.",
        ],
    }


def candidate_actions() -> list[dict[str, Any]]:
    return [
        {
            "actionId": "explore_cli_help_import_boundary_remediation_contract",
            "decision": "selected",
            "nextArtifact": "SDK-A5 private explore CLI help import-boundary remediation contract",
            "reason": "A contract can bound the intended behavior before implementation: help/version paths should remain inspectable, while commands that need eml-discover stay gated by optional dependencies.",
            "implementationStarted": False,
        },
        {
            "actionId": "reclassify_explore_probe_optional",
            "decision": "parked",
            "reason": "Reclassification may be correct for source-tree smoke, but it should not be chosen before deciding whether help should work without optional extras.",
            "implementationStarted": False,
        },
        {
            "actionId": "install_cli_extra_and_rerun_smoke",
            "decision": "parked",
            "reason": "Installing extras would test a different environment and could hide the source-tree help import boundary.",
            "implementationStarted": False,
        },
        {
            "actionId": "direct_code_fix",
            "decision": "blocked_in_sdk_a4",
            "reason": "SDK-A4 is a review selector only; implementation belongs after the remediation contract.",
            "implementationStarted": False,
        },
    ]


def build_payload() -> dict[str, Any]:
    source = load_sdk_a3_result()
    review = finding_review(source)
    actions = candidate_actions()
    selected = [action for action in actions if action["decision"] == "selected"]
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceStatus": source["status"],
        "requiredProbeFailureCount": source["summary"]["requiredProbeFailureCount"],
        "selectedFindingId": review["findingId"],
        "findingClassification": review["classification"],
        "candidateActionCount": len(actions),
        "selectedActionId": selected[0]["actionId"],
        "sdkImplementationChanged": False,
        "exploreCliRemediated": False,
        "smokeProbeRerun": False,
        "publicReadinessClaim": False,
        "sdkStabilityClaim": False,
        "nextRecommendedArtifact": selected[0]["nextArtifact"],
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="sdk-a4-private-sdk-smoke-result-review-selector",
        artifact_type="private_sdk_smoke_result_review_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "findingReview": review,
            "candidateActions": actions,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifact"] != "sdk-a3-private-sdk-import-cli-smoke-dry-run":
        raise ValueError("SDK-A4 must consume SDK-A3")
    summary = payload["summary"]
    if summary["requiredProbeFailureCount"] != 1:
        raise ValueError("SDK-A4 expects the single SDK-A3 required smoke finding")
    if summary["findingClassification"] != "optional_dependency_import_boundary":
        raise ValueError("unexpected finding classification")
    if summary["selectedActionId"] != "explore_cli_help_import_boundary_remediation_contract":
        raise ValueError("unexpected selected action")
    for key in [
        "sdkImplementationChanged",
        "exploreCliRemediated",
        "smokeProbeRerun",
        "publicReadinessClaim",
        "sdkStabilityClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    actions = payload["candidateActions"]
    if sum(1 for action in actions if action["decision"] == "selected") != 1:
        raise ValueError("exactly one action must be selected")
    if any(action["implementationStarted"] is not False for action in actions):
        raise ValueError("SDK-A4 must not start implementation")
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
        semantic_strength="private_smoke_finding_review_selector_no_implementation_change",
        source=f"python/results/sdk_a4_private_sdk_smoke_result_review_selector/sdk_a4_private_sdk_smoke_result_review_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="sdk_a4_private_sdk_smoke_result_review_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Create SDK-A5 private explore CLI help import-boundary remediation contract.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "selectedFindingId": payload["summary"]["selectedFindingId"],
            "findingClassification": payload["summary"]["findingClassification"],
            "selectedActionId": payload["summary"]["selectedActionId"],
            "sdkImplementationChanged": payload["summary"]["sdkImplementationChanged"],
            "exploreCliRemediated": payload["summary"]["exploreCliRemediated"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="SDK-A4 Private SDK Smoke Result Review Selector",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("required probe failures", payload["summary"]["requiredProbeFailureCount"]),
            ("finding classification", payload["summary"]["findingClassification"]),
            ("selected action", payload["summary"]["selectedActionId"]),
            ("SDK implementation changed", payload["summary"]["sdkImplementationChanged"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Finding Review",
                [
                    f"- finding: `{payload['findingReview']['findingId']}`",
                    f"- observed signal: {payload['findingReview']['observedSignal']}",
                ],
            ),
            (
                "Candidate Actions",
                [
                    f"- `{action['actionId']}`: `{action['decision']}` - {action['reason']}"
                    for action in payload["candidateActions"]
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
    result_path = out_dir / f"sdk_a4_private_sdk_smoke_result_review_selector_{STAMP}.json"
    report_path = report_dir / f"sdk_a4_private_sdk_smoke_result_review_selector_{STAMP}.md"
    evidence_path = evidence_dir / "sdk_a4_private_sdk_smoke_result_review_selector.json"
    feed_path = command_feed_dir / f"sdk_a4_private_sdk_smoke_result_review_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/sdk_a4_private_sdk_smoke_result_review_selector")
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
    print("SDK_A4_PRIVATE_SDK_SMOKE_RESULT_REVIEW_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
