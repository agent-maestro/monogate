#!/usr/bin/env python3
"""PROD-A21 private training-cost estimator skeleton hold digest."""

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

from scripts import prod_a20_training_cost_estimator_skeleton_review_or_hold_selector as prod_a20  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-08"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.training_cost_estimator_skeleton_hold_digest.v0"
STATUS = "PROD_A21_TRAINING_COST_ESTIMATOR_SKELETON_HOLD_DIGEST_PASS"
ARTIFACT_ID = "prod-a21-training-cost-estimator-skeleton-hold-digest"
NEXT_RECOMMENDED_ARTIFACT = "pause training-cost estimator lane unless explicit bounded reviewer or user request arrives"

TRUE_CLAIM_FLAGS = {
    "prod_a20_consumed",
    "skeleton_hold_digest_created",
    "skeleton_lane_state_summarized",
    "blocked_actions_recorded",
    "reopen_conditions_recorded",
    "training_cost_estimator_lane_held",
}

CLAIM_FLAGS = {
    "prod_a20_consumed": True,
    "skeleton_hold_digest_created": True,
    "skeleton_lane_state_summarized": True,
    "blocked_actions_recorded": True,
    "reopen_conditions_recorded": True,
    "training_cost_estimator_lane_held": True,
    "estimator_implementation_gate_opened": False,
    "estimator_implemented": False,
    "estimator_executed": False,
    "estimate_values_produced": False,
    "estimate_values_validated": False,
    "model_training_executed": False,
    "runtime_benchmark_executed": False,
    "calibration_performed": False,
    "training_savings_claim": False,
    "estimator_accuracy_claim": False,
    "runtime_performance_claim": False,
    "model_quality_claim": False,
    "scientific_correctness_claim": False,
    "public_product_ready": False,
    "public_readiness_claim": False,
    "public_docs_created": False,
    "public_package_release_claim": False,
    "sdk_stability_claim": False,
    "compiler_correctness_claim": False,
    "semantic_preservation_claim": False,
    "hardware_readiness_claim": False,
    "silicon_readiness_claim": False,
    "electronics_repo_touched": False,
    "laptop_owned_repo_touched": False,
    "reviewer_response_consumed": False,
    "reviewer_approval_recorded": False,
    "broad_eml_advantage_claim": False,
}

NON_CLAIMS = [
    "PROD-A21 is a private hold digest; it does not implement or execute a training-cost estimator.",
    "PROD-A21 summarizes the non-executing skeleton lane and parks it until an explicit bounded reviewer or user request arrives.",
    "PROD-A21 does not produce or validate estimate values, train models, run benchmarks, calibrate estimates, or infer runtime, savings, accuracy, or model quality.",
    "PROD-A21 does not publish docs, update public/dev surfaces, approve public copy, or claim estimator accuracy, training savings, runtime performance, SDK stability, compiler correctness, semantic preservation, hardware readiness, silicon readiness, public readiness, reviewer approval, or broad EML advantage.",
]

BLOCKED_ACTIONS = [
    {
        "actionId": "open_estimator_implementation_gate",
        "status": "blocked",
        "reason": "Requires explicit reviewer approval or a bounded user request plus estimate-value contract and calibration protocol.",
    },
    {
        "actionId": "execute_estimator",
        "status": "blocked",
        "reason": "No estimator implementation gate is open and no estimate-producing behavior is approved.",
    },
    {
        "actionId": "publish_product_or_docs",
        "status": "blocked",
        "reason": "No public readiness, public-copy approval, package release gate, or user-facing value claim exists.",
    },
    {
        "actionId": "continue_fixture_expansion",
        "status": "parked",
        "reason": "Only reopen if a reviewer names a concrete missing fixture or boundary gap.",
    },
]

BLOCKED_CLAIMS = [
    "estimator accuracy",
    "training cost savings",
    "runtime performance",
    "model quality",
    "calibration validity",
    "scientific correctness",
    "public product readiness",
    "SDK stability",
    "compiler correctness",
    "semantic preservation",
    "hardware readiness",
    "silicon readiness",
    "broad EML advantage",
]


def load_prod_a20_result() -> dict[str, Any]:
    path = (
        ROOT
        / "python/results/prod_a20_training_cost_estimator_skeleton_review_or_hold_selector"
        / f"prod_a20_training_cost_estimator_skeleton_review_or_hold_selector_{STAMP}.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    prod_a20.validate_payload(payload)
    return payload


def lane_state_rows(source: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "rowId": "skeleton_module",
            "state": "implemented_private_non_executing",
            "evidence": "PROD-A18 implemented the private skeleton module with hold/no-estimate packets.",
        },
        {
            "rowId": "skeleton_validator",
            "state": "implemented_and_executed_private_structural",
            "evidence": "PROD-A19 validated one accepted hold packet and four rejection mutations.",
        },
        {
            "rowId": "review_selector",
            "state": "hold_selected",
            "evidence": f"PROD-A20 selected `{source['summary']['selectedActionId']}`.",
        },
        {
            "rowId": "estimator_behavior",
            "state": "blocked",
            "evidence": "No estimator implementation gate is open; no estimate values are produced or validated.",
        },
    ]


def reopen_conditions() -> list[dict[str, str]]:
    return [
        {
            "conditionId": "explicit_bounded_user_request",
            "status": "allowed_reopen_trigger",
            "description": "A new request explicitly asks for the estimator lane and preserves claim boundaries.",
        },
        {
            "conditionId": "actual_private_reviewer_approval",
            "status": "allowed_reopen_trigger",
            "description": "A reviewer approves a specific next estimator gate with blocked claims intact.",
        },
        {
            "conditionId": "estimate_value_contract_and_calibration_plan",
            "status": "required_before_estimator_gate",
            "description": "Any estimate-producing gate needs a value contract, calibration protocol, and usefulness criterion.",
        },
        {
            "conditionId": "public_launch_impulse",
            "status": "blocked_reopen_trigger",
            "description": "General desire for public docs, savings claims, or launch copy is not sufficient.",
        },
    ]


def build_payload() -> dict[str, Any]:
    source = load_prod_a20_result()
    rows = lane_state_rows(source)
    conditions = reopen_conditions()
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceSelectedActionId": source["summary"]["selectedActionId"],
        "laneStateRowCount": len(rows),
        "blockedActionCount": len(BLOCKED_ACTIONS),
        "blockedClaimCount": len(BLOCKED_CLAIMS),
        "reopenConditionCount": len(conditions),
        "trainingCostEstimatorLaneHeld": True,
        "skeletonHoldDigestCreated": True,
        "estimatorImplementationGateOpened": False,
        "estimatorImplemented": False,
        "estimatorExecuted": False,
        "estimateValuesProduced": False,
        "estimateValuesValidated": False,
        "runtimeBenchmarkExecuted": False,
        "calibrationPerformed": False,
        "publicProductReady": False,
        "trainingSavingsClaim": False,
        "estimatorAccuracyClaim": False,
        "runtimePerformanceClaim": False,
        "nextRecommendedArtifact": NEXT_RECOMMENDED_ARTIFACT,
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id=ARTIFACT_ID,
        artifact_type="training_cost_estimator_skeleton_hold_digest",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "laneStateRows": rows,
            "blockedActions": list(BLOCKED_ACTIONS),
            "blockedClaims": list(BLOCKED_CLAIMS),
            "reopenConditions": conditions,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "prod-a20-training-cost-estimator-skeleton-review-or-hold-selector":
        raise ValueError("PROD-A21 must consume PROD-A20")
    summary = payload["summary"]
    if summary["sourceSelectedActionId"] != "private_skeleton_hold_digest":
        raise ValueError("PROD-A20 selected action drift")
    if summary["laneStateRowCount"] != 4:
        raise ValueError("expected four lane state rows")
    if summary["blockedActionCount"] != 4:
        raise ValueError("expected four blocked/parked actions")
    if summary["blockedClaimCount"] != len(BLOCKED_CLAIMS):
        raise ValueError("blocked claim count drift")
    if summary["reopenConditionCount"] != 4:
        raise ValueError("expected four reopen conditions")
    for key in ["trainingCostEstimatorLaneHeld", "skeletonHoldDigestCreated"]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "estimatorImplementationGateOpened",
        "estimatorImplemented",
        "estimatorExecuted",
        "estimateValuesProduced",
        "estimateValuesValidated",
        "runtimeBenchmarkExecuted",
        "calibrationPerformed",
        "publicProductReady",
        "trainingSavingsClaim",
        "estimatorAccuracyClaim",
        "runtimePerformanceClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    row_states = {row["rowId"]: row["state"] for row in payload["laneStateRows"]}
    if row_states["estimator_behavior"] != "blocked":
        raise ValueError("estimator behavior must remain blocked")
    action_statuses = {action["actionId"]: action["status"] for action in payload["blockedActions"]}
    if action_statuses["open_estimator_implementation_gate"] != "blocked":
        raise ValueError("implementation gate must remain blocked")
    if action_statuses["continue_fixture_expansion"] != "parked":
        raise ValueError("fixture expansion must remain parked")
    condition_statuses = {condition["conditionId"]: condition["status"] for condition in payload["reopenConditions"]}
    if condition_statuses["public_launch_impulse"] != "blocked_reopen_trigger":
        raise ValueError("public launch impulse must remain blocked")
    if condition_statuses["estimate_value_contract_and_calibration_plan"] != "required_before_estimator_gate":
        raise ValueError("estimate contract and calibration plan must be required")
    if set(payload["blockedClaims"]) != set(BLOCKED_CLAIMS):
        raise ValueError("blocked claims mismatch")
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected next artifact")
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
        semantic_strength="private_training_cost_estimator_skeleton_hold_digest_no_estimator_execution_or_public_claim",
        source=f"python/results/prod_a21_training_cost_estimator_skeleton_hold_digest/prod_a21_training_cost_estimator_skeleton_hold_digest_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="prod_a21_training_cost_estimator_skeleton_hold_digest_feed",
        date=DATE,
        status=payload["status"],
        next_action="Training-cost estimator skeleton lane held; resume only with explicit bounded reviewer or user request.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "trainingCostEstimatorLaneHeld": payload["summary"]["trainingCostEstimatorLaneHeld"],
            "estimatorImplementationGateOpened": payload["summary"]["estimatorImplementationGateOpened"],
            "estimateValuesProduced": payload["summary"]["estimateValuesProduced"],
            "blockedActionCount": payload["summary"]["blockedActionCount"],
            "reopenConditionCount": payload["summary"]["reopenConditionCount"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="PROD-A21 Training Cost Estimator Skeleton Hold Digest",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("lane state rows", payload["summary"]["laneStateRowCount"]),
            ("blocked actions", payload["summary"]["blockedActionCount"]),
            ("blocked claims", payload["summary"]["blockedClaimCount"]),
            ("reopen conditions", payload["summary"]["reopenConditionCount"]),
            ("training-cost estimator lane held", payload["summary"]["trainingCostEstimatorLaneHeld"]),
            ("estimator implementation gate opened", payload["summary"]["estimatorImplementationGateOpened"]),
            ("estimate values produced", payload["summary"]["estimateValuesProduced"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Lane State Rows",
                [f"- `{row['rowId']}`: `{row['state']}` - {row['evidence']}" for row in payload["laneStateRows"]],
            ),
            (
                "Blocked Actions",
                [
                    f"- `{action['actionId']}`: `{action['status']}` - {action['reason']}"
                    for action in payload["blockedActions"]
                ],
            ),
            (
                "Reopen Conditions",
                [
                    f"- `{condition['conditionId']}`: `{condition['status']}` - {condition['description']}"
                    for condition in payload["reopenConditions"]
                ],
            ),
            ("Blocked Claims", [f"- {claim}" for claim in payload["blockedClaims"]]),
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"prod_a21_training_cost_estimator_skeleton_hold_digest_{STAMP}.json"
    report_path = report_dir / f"prod_a21_training_cost_estimator_skeleton_hold_digest_{STAMP}.md"
    evidence_path = evidence_dir / "prod_a21_training_cost_estimator_skeleton_hold_digest.json"
    feed_path = command_feed_dir / f"prod_a21_training_cost_estimator_skeleton_hold_digest_feed_{STAMP}.json"
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
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "python/results/prod_a21_training_cost_estimator_skeleton_hold_digest",
    )
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
    print("PROD_A21_TRAINING_COST_ESTIMATOR_SKELETON_HOLD_DIGEST_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
