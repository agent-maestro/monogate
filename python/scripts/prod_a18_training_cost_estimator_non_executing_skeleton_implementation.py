#!/usr/bin/env python3
"""PROD-A18 private non-executing training-cost estimator skeleton implementation."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from monogate.training_cost_estimator_skeleton import (  # noqa: E402
    NULL_COST_VIEW_FIELDS,
    REQUIRED_FALSE_CLAIM_FLAGS,
    TrainingCostEstimatorSkeleton,
    build_hold_packet,
    validate_input_shape,
)
from scripts import prod_a17_training_cost_estimator_skeleton_contract_seed as prod_a17  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-08"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.training_cost_estimator_non_executing_skeleton_implementation.v0"
STATUS = "PROD_A18_TRAINING_COST_ESTIMATOR_NON_EXECUTING_SKELETON_IMPLEMENTATION_PASS"
ARTIFACT_ID = "prod-a18-training-cost-estimator-non-executing-skeleton-implementation"
NEXT_RECOMMENDED_ARTIFACT = "PROD-A19 private training-cost estimator skeleton fixture validator"

TRUE_CLAIM_FLAGS = {
    "prod_a17_consumed",
    "estimator_skeleton_implemented",
    "non_executing_hold_packet_implemented",
    "input_shape_validation_implemented",
    "hold_packet_smoke_executed",
    "estimate_values_blocked",
    "execution_blocked",
    "public_claims_blocked",
}

CLAIM_FLAGS = {
    "prod_a17_consumed": True,
    "estimator_skeleton_implemented": True,
    "non_executing_hold_packet_implemented": True,
    "input_shape_validation_implemented": True,
    "hold_packet_smoke_executed": True,
    "estimate_values_blocked": True,
    "execution_blocked": True,
    "public_claims_blocked": True,
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
    "PROD-A18 implements a private non-executing skeleton module only.",
    "PROD-A18 can build hold/no-estimate packets and structural input-shape metadata, but it does not implement or execute a training-cost estimator.",
    "PROD-A18 does not produce estimate values, validate estimate values, train models, run benchmarks, calibrate estimates, or infer runtime, savings, accuracy, or model quality.",
    "PROD-A18 does not publish docs, update public/dev surfaces, approve public copy, or claim estimator accuracy, training savings, runtime performance, SDK stability, compiler correctness, semantic preservation, hardware readiness, silicon readiness, public readiness, reviewer approval, or broad EML advantage.",
]

SAMPLE_ACCEPTED_INPUT = {
    "workload_id": "private_fixture_workload",
    "expression_ref": "eml://private/example",
    "model_family": "unvalidated_private_model_family",
    "training_context": {"source": "private_fixture"},
}


def load_prod_a17_result() -> dict[str, Any]:
    path = (
        ROOT
        / "python/results/prod_a17_training_cost_estimator_skeleton_contract_seed"
        / f"prod_a17_training_cost_estimator_skeleton_contract_seed_{STAMP}.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    prod_a17.validate_payload(payload)
    return payload


def module_import_scan() -> dict[str, Any]:
    blocked = {"torch", "tensorflow", "timeit", "subprocess"}
    before = set(sys.modules)
    module = importlib.import_module("monogate.training_cost_estimator_skeleton")
    after = set(sys.modules)
    imported_blocked = sorted(blocked & (after - before))
    return {
        "module": module.__name__,
        "blockedImportsObserved": imported_blocked,
        "blockedImportsAbsent": not imported_blocked,
    }


def skeleton_smoke_rows() -> list[dict[str, Any]]:
    skeleton = TrainingCostEstimatorSkeleton()
    accepted_validation = validate_input_shape(SAMPLE_ACCEPTED_INPUT)
    rejected_validation = validate_input_shape({"workload_id": "missing_fields"})
    hold = skeleton.hold_packet(SAMPLE_ACCEPTED_INPUT)
    direct_hold = build_hold_packet(SAMPLE_ACCEPTED_INPUT)
    return [
        {
            "fixtureId": "accepted_input_shape_metadata",
            "disposition": accepted_validation.disposition,
            "missingFields": list(accepted_validation.missing_fields),
            "estimateValuesProduced": False,
        },
        {
            "fixtureId": "rejected_input_shape_metadata",
            "disposition": rejected_validation.disposition,
            "missingFields": list(rejected_validation.missing_fields),
            "estimateValuesProduced": False,
        },
        {
            "fixtureId": "hold_packet_from_class",
            "disposition": hold["disposition"],
            "nullCostViewFields": [field for field in NULL_COST_VIEW_FIELDS if hold[field] is None],
            "falseClaimFlags": [key for key, value in hold["claim_flags"].items() if value is False],
            "estimateValuesProduced": False,
        },
        {
            "fixtureId": "hold_packet_from_function",
            "disposition": direct_hold["disposition"],
            "nullCostViewFields": [field for field in NULL_COST_VIEW_FIELDS if direct_hold[field] is None],
            "falseClaimFlags": [key for key, value in direct_hold["claim_flags"].items() if value is False],
            "estimateValuesProduced": False,
        },
    ]


def build_payload() -> dict[str, Any]:
    source = load_prod_a17_result()
    import_scan = module_import_scan()
    smoke_rows = skeleton_smoke_rows()
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceModulePath": source["moduleBoundary"]["modulePath"],
        "implementedModulePath": "python/monogate/training_cost_estimator_skeleton.py",
        "smokeFixtureCount": len(smoke_rows),
        "holdPacketSmokeExecuted": True,
        "blockedImportsAbsent": import_scan["blockedImportsAbsent"],
        "nullCostViewFields": list(NULL_COST_VIEW_FIELDS),
        "requiredFalseClaimFlags": list(REQUIRED_FALSE_CLAIM_FLAGS),
        "estimatorSkeletonImplemented": True,
        "nonExecutingHoldPacketImplemented": True,
        "inputShapeValidationImplemented": True,
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
        artifact_type="training_cost_estimator_non_executing_skeleton_implementation",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "moduleImportScan": import_scan,
            "skeletonSmokeRows": smoke_rows,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "prod-a17-training-cost-estimator-skeleton-contract-seed":
        raise ValueError("PROD-A18 must consume PROD-A17")
    summary = payload["summary"]
    if summary["sourceModulePath"] != summary["implementedModulePath"]:
        raise ValueError("implemented module path must match PROD-A17 contract")
    for key in [
        "holdPacketSmokeExecuted",
        "blockedImportsAbsent",
        "estimatorSkeletonImplemented",
        "nonExecutingHoldPacketImplemented",
        "inputShapeValidationImplemented",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
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
    if summary["nullCostViewFields"] != list(NULL_COST_VIEW_FIELDS):
        raise ValueError("cost-view null field drift")
    if set(summary["requiredFalseClaimFlags"]) != set(REQUIRED_FALSE_CLAIM_FLAGS):
        raise ValueError("required false claim flag drift")
    if payload["moduleImportScan"]["blockedImportsObserved"]:
        raise ValueError("blocked imports observed")
    for row in payload["skeletonSmokeRows"]:
        if row["estimateValuesProduced"] is not False:
            raise ValueError(f"smoke row produced estimate values: {row['fixtureId']}")
        if row["fixtureId"].startswith("hold_packet"):
            if row["disposition"] != "hold_no_estimate":
                raise ValueError("hold packet must keep hold_no_estimate disposition")
            if row["nullCostViewFields"] != list(NULL_COST_VIEW_FIELDS):
                raise ValueError("hold packet must null every cost-view field")
            if set(row["falseClaimFlags"]) != set(REQUIRED_FALSE_CLAIM_FLAGS):
                raise ValueError("hold packet must keep required claim flags false")
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
        semantic_strength="private_non_executing_skeleton_implementation_no_estimator_execution_or_public_claim",
        source=f"python/results/prod_a18_training_cost_estimator_non_executing_skeleton_implementation/prod_a18_training_cost_estimator_non_executing_skeleton_implementation_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="prod_a18_training_cost_estimator_non_executing_skeleton_implementation_feed",
        date=DATE,
        status=payload["status"],
        next_action="Validate the private skeleton fixtures before any estimate-producing behavior is considered.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "implementedModulePath": payload["summary"]["implementedModulePath"],
            "holdPacketSmokeExecuted": payload["summary"]["holdPacketSmokeExecuted"],
            "estimateValuesProduced": payload["summary"]["estimateValuesProduced"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="PROD-A18 Training Cost Estimator Non-Executing Skeleton Implementation",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("implemented module path", payload["summary"]["implementedModulePath"]),
            ("smoke fixtures", payload["summary"]["smokeFixtureCount"]),
            ("hold packet smoke executed", payload["summary"]["holdPacketSmokeExecuted"]),
            ("blocked imports absent", payload["summary"]["blockedImportsAbsent"]),
            ("estimator skeleton implemented", payload["summary"]["estimatorSkeletonImplemented"]),
            ("estimator implemented", payload["summary"]["estimatorImplemented"]),
            ("estimate values produced", payload["summary"]["estimateValuesProduced"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Smoke Rows",
                [
                    f"- `{row['fixtureId']}`: `{row['disposition']}`; estimate values produced: `{row['estimateValuesProduced']}`"
                    for row in payload["skeletonSmokeRows"]
                ],
            ),
            (
                "Blocked Imports",
                [
                    f"- observed blocked imports: `{payload['moduleImportScan']['blockedImportsObserved']}`",
                    f"- blocked imports absent: `{payload['moduleImportScan']['blockedImportsAbsent']}`",
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
    result_path = out_dir / f"prod_a18_training_cost_estimator_non_executing_skeleton_implementation_{STAMP}.json"
    report_path = report_dir / f"prod_a18_training_cost_estimator_non_executing_skeleton_implementation_{STAMP}.md"
    evidence_path = evidence_dir / "prod_a18_training_cost_estimator_non_executing_skeleton_implementation.json"
    feed_path = command_feed_dir / f"prod_a18_training_cost_estimator_non_executing_skeleton_implementation_feed_{STAMP}.json"
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
        default=ROOT / "python/results/prod_a18_training_cost_estimator_non_executing_skeleton_implementation",
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
    print("PROD_A18_TRAINING_COST_ESTIMATOR_NON_EXECUTING_SKELETON_IMPLEMENTATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
