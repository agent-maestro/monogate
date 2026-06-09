#!/usr/bin/env python3
"""PROD-A17 private training-cost estimator skeleton contract seed."""

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

from scripts import prod_a16_training_cost_estimator_implementation_gate_or_hold_selector as prod_a16  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-08"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.training_cost_estimator_skeleton_contract_seed.v0"
STATUS = "PROD_A17_TRAINING_COST_ESTIMATOR_SKELETON_CONTRACT_SEED_PASS"
ARTIFACT_ID = "prod-a17-training-cost-estimator-skeleton-contract-seed"
NEXT_RECOMMENDED_ARTIFACT = "PROD-A18 private training-cost estimator non-executing skeleton implementation"

TRUE_CLAIM_FLAGS = {
    "prod_a16_consumed",
    "estimator_skeleton_contract_created",
    "module_boundary_recorded",
    "api_boundary_recorded",
    "hold_behavior_recorded",
    "execution_blocked",
    "public_claims_blocked",
}

CLAIM_FLAGS = {
    "prod_a16_consumed": True,
    "estimator_skeleton_contract_created": True,
    "module_boundary_recorded": True,
    "api_boundary_recorded": True,
    "hold_behavior_recorded": True,
    "execution_blocked": True,
    "public_claims_blocked": True,
    "estimator_skeleton_implemented": False,
    "estimator_implemented": False,
    "estimator_executed": False,
    "estimate_values_produced": False,
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
    "PROD-A17 creates a private non-executing skeleton contract seed only; it does not implement the skeleton.",
    "PROD-A17 defines module/API/hold boundaries for a future skeleton and explicitly blocks estimate production.",
    "PROD-A17 does not implement or execute a training-cost estimator, validate estimate values, train models, run benchmarks, or calibrate estimates.",
    "PROD-A17 does not publish docs, update public/dev surfaces, approve public copy, or claim estimator accuracy, training savings, runtime performance, SDK stability, compiler correctness, semantic preservation, hardware readiness, silicon readiness, public readiness, reviewer approval, or broad EML advantage.",
]


def load_prod_a16_result() -> dict[str, Any]:
    path = (
        ROOT
        / "python/results/prod_a16_training_cost_estimator_implementation_gate_or_hold_selector"
        / f"prod_a16_training_cost_estimator_implementation_gate_or_hold_selector_{STAMP}.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    prod_a16.validate_payload(payload)
    return payload


def module_boundary() -> dict[str, Any]:
    return {
        "modulePath": "python/monogate/training_cost_estimator_skeleton.py",
        "status": "future_private_module_contract",
        "allowedImports": [
            "dataclasses",
            "typing",
            "monogate.training_cost_io_contract_validator",
        ],
        "blockedImports": [
            "torch",
            "tensorflow",
            "timeit",
            "subprocess",
            "network",
        ],
        "boundary": "Future module may expose contract-shaped dataclasses and hold errors only; it must not compute estimates.",
    }


def api_boundaries() -> list[dict[str, Any]]:
    return [
        {
            "apiId": "TrainingCostEstimatorSkeleton",
            "kind": "class",
            "allowedBehavior": "constructs with contract metadata and exposes no estimate-producing method",
            "blockedBehavior": "no training, benchmarking, calibration, runtime probing, or estimate value generation",
        },
        {
            "apiId": "build_hold_packet",
            "kind": "function",
            "allowedBehavior": "returns a claim-bounded hold packet with caveats and blocked claims",
            "blockedBehavior": "must not return static_expression_cost, graph_cost_profile, or training_budget_context values",
        },
        {
            "apiId": "validate_input_shape",
            "kind": "function",
            "allowedBehavior": "checks required input metadata and returns accept/reject metadata only",
            "blockedBehavior": "must not infer numeric cost, runtime, savings, accuracy, or model quality",
        },
    ]


def hold_behavior() -> dict[str, Any]:
    return {
        "requiredDisposition": "hold_no_estimate",
        "requiredReason": "estimator implementation remains blocked pending a later explicit gate",
        "requiredFalseClaimFlags": [
            "public_product_ready",
            "training_savings_claim",
            "estimator_accuracy_claim",
            "runtime_performance_claim",
            "broad_eml_advantage_claim",
        ],
        "requiredOutputNulls": [
            "static_expression_cost",
            "graph_cost_profile",
            "training_budget_context",
        ],
        "requiredReviewerNextStep": "review skeleton implementation before enabling estimate-producing behavior",
    }


def skeleton_contract_fixtures() -> list[dict[str, Any]]:
    return [
        {
            "fixtureId": "accepted_hold_packet_shape",
            "expectedDisposition": "accept_skeleton_hold_shape",
            "requiredDisposition": "hold_no_estimate",
        },
        {
            "fixtureId": "reject_estimate_values_present",
            "expectedDisposition": "reject_skeleton_shape",
            "mutation": "populate one cost-view field with estimate values",
        },
        {
            "fixtureId": "reject_true_public_or_accuracy_flag",
            "expectedDisposition": "reject_skeleton_shape",
            "mutation": "set public_product_ready or estimator_accuracy_claim true",
        },
        {
            "fixtureId": "reject_missing_hold_reason",
            "expectedDisposition": "reject_skeleton_shape",
            "mutation": "remove hold reason from skeleton output",
        },
    ]


def reviewer_questions() -> list[dict[str, str]]:
    return [
        {
            "questionId": "module_path_ok",
            "question": "Is the proposed private module path acceptable for a non-executing skeleton?",
        },
        {
            "questionId": "hold_packet_enough",
            "question": "Does the hold packet shape force non-estimate behavior clearly enough?",
        },
        {
            "questionId": "a18_path",
            "question": "Should PROD-A18 implement only this skeleton, or hold before any module code?",
        },
    ]


def build_payload() -> dict[str, Any]:
    source = load_prod_a16_result()
    module = module_boundary()
    apis = api_boundaries()
    hold = hold_behavior()
    fixtures = skeleton_contract_fixtures()
    questions = reviewer_questions()
    rejected = [fixture for fixture in fixtures if fixture["expectedDisposition"].startswith("reject")]
    accepted = [fixture for fixture in fixtures if fixture["expectedDisposition"].startswith("accept")]
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceSelectedActionId": source["summary"]["selectedActionId"],
        "moduleBoundaryRecorded": True,
        "apiBoundaryCount": len(apis),
        "skeletonContractFixtureCount": len(fixtures),
        "acceptedSkeletonFixtureCount": len(accepted),
        "rejectionSkeletonFixtureCount": len(rejected),
        "reviewerQuestionCount": len(questions),
        "holdDisposition": hold["requiredDisposition"],
        "estimatorSkeletonContractCreated": True,
        "estimatorSkeletonImplemented": False,
        "estimatorImplemented": False,
        "estimatorExecuted": False,
        "estimateValuesProduced": False,
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
        artifact_type="training_cost_estimator_skeleton_contract_seed",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "moduleBoundary": module,
            "apiBoundaries": apis,
            "holdBehavior": hold,
            "skeletonContractFixtures": fixtures,
            "reviewerQuestions": questions,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "prod-a16-training-cost-estimator-implementation-gate-or-hold-selector":
        raise ValueError("PROD-A17 must consume PROD-A16")
    summary = payload["summary"]
    if summary["sourceSelectedActionId"] != "private_estimator_skeleton_contract_seed":
        raise ValueError("PROD-A16 selected action drift")
    if summary["apiBoundaryCount"] != 3:
        raise ValueError("expected three API boundaries")
    if summary["skeletonContractFixtureCount"] != 4:
        raise ValueError("expected four skeleton fixtures")
    if summary["acceptedSkeletonFixtureCount"] != 1:
        raise ValueError("expected one accepted skeleton fixture")
    if summary["rejectionSkeletonFixtureCount"] != 3:
        raise ValueError("expected three rejection skeleton fixtures")
    if summary["holdDisposition"] != "hold_no_estimate":
        raise ValueError("skeleton must hold with no estimate")
    for key in ["moduleBoundaryRecorded", "estimatorSkeletonContractCreated"]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "estimatorSkeletonImplemented",
        "estimatorImplemented",
        "estimatorExecuted",
        "estimateValuesProduced",
        "runtimeBenchmarkExecuted",
        "calibrationPerformed",
        "publicProductReady",
        "trainingSavingsClaim",
        "estimatorAccuracyClaim",
        "runtimePerformanceClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    hold = payload["holdBehavior"]
    if hold["requiredOutputNulls"] != ["static_expression_cost", "graph_cost_profile", "training_budget_context"]:
        raise ValueError("hold behavior must null all cost views")
    if "torch" not in payload["moduleBoundary"]["blockedImports"]:
        raise ValueError("heavy training imports must remain blocked")
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
        semantic_strength="private_estimator_skeleton_contract_seed_no_estimator_execution_or_public_claim",
        source=f"python/results/prod_a17_training_cost_estimator_skeleton_contract_seed/prod_a17_training_cost_estimator_skeleton_contract_seed_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="prod_a17_training_cost_estimator_skeleton_contract_seed_feed",
        date=DATE,
        status=payload["status"],
        next_action="Implement only the private non-executing estimator skeleton, preserving hold/no-estimate behavior.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "modulePath": payload["moduleBoundary"]["modulePath"],
            "holdDisposition": payload["summary"]["holdDisposition"],
            "estimatorSkeletonImplemented": payload["summary"]["estimatorSkeletonImplemented"],
            "estimatorImplemented": payload["summary"]["estimatorImplemented"],
            "estimateValuesProduced": payload["summary"]["estimateValuesProduced"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="PROD-A17 Training Cost Estimator Skeleton Contract Seed",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("module path", payload["moduleBoundary"]["modulePath"]),
            ("API boundaries", payload["summary"]["apiBoundaryCount"]),
            ("skeleton fixtures", payload["summary"]["skeletonContractFixtureCount"]),
            ("hold disposition", payload["summary"]["holdDisposition"]),
            ("estimator skeleton implemented", payload["summary"]["estimatorSkeletonImplemented"]),
            ("estimator implemented", payload["summary"]["estimatorImplemented"]),
            ("estimate values produced", payload["summary"]["estimateValuesProduced"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "API Boundaries",
                [f"- `{item['apiId']}`: `{item['kind']}` - {item['allowedBehavior']}" for item in payload["apiBoundaries"]],
            ),
            (
                "Skeleton Fixtures",
                [
                    f"- `{fixture['fixtureId']}`: `{fixture['expectedDisposition']}`"
                    for fixture in payload["skeletonContractFixtures"]
                ],
            ),
            (
                "Reviewer Questions",
                [f"- `{item['questionId']}`: {item['question']}" for item in payload["reviewerQuestions"]],
            ),
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"prod_a17_training_cost_estimator_skeleton_contract_seed_{STAMP}.json"
    report_path = report_dir / f"prod_a17_training_cost_estimator_skeleton_contract_seed_{STAMP}.md"
    evidence_path = evidence_dir / "prod_a17_training_cost_estimator_skeleton_contract_seed.json"
    feed_path = command_feed_dir / f"prod_a17_training_cost_estimator_skeleton_contract_seed_feed_{STAMP}.json"
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
        default=ROOT / "python/results/prod_a17_training_cost_estimator_skeleton_contract_seed",
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
    print("PROD_A17_TRAINING_COST_ESTIMATOR_SKELETON_CONTRACT_SEED_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
