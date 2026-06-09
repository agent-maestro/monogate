#!/usr/bin/env python3
"""PROD-A19 private training-cost estimator skeleton fixture validator."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from monogate.training_cost_estimator_skeleton import build_hold_packet  # noqa: E402
from monogate.training_cost_estimator_skeleton_validator import validate_skeleton_hold_packet  # noqa: E402
from scripts import prod_a18_training_cost_estimator_non_executing_skeleton_implementation as prod_a18  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-08"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.training_cost_estimator_skeleton_fixture_validator.v0"
STATUS = "PROD_A19_TRAINING_COST_ESTIMATOR_SKELETON_FIXTURE_VALIDATOR_PASS"
ARTIFACT_ID = "prod-a19-training-cost-estimator-skeleton-fixture-validator"
NEXT_RECOMMENDED_ARTIFACT = "PROD-A20 private training-cost estimator skeleton review or hold selector"

TRUE_CLAIM_FLAGS = {
    "prod_a18_consumed",
    "skeleton_fixture_validator_implemented",
    "skeleton_fixture_validator_executed",
    "accepted_skeleton_fixture_results_recorded",
    "rejection_skeleton_fixture_results_recorded",
    "estimate_values_blocked",
    "execution_blocked",
    "public_claims_blocked",
}

CLAIM_FLAGS = {
    "prod_a18_consumed": True,
    "skeleton_fixture_validator_implemented": True,
    "skeleton_fixture_validator_executed": True,
    "accepted_skeleton_fixture_results_recorded": True,
    "rejection_skeleton_fixture_results_recorded": True,
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
    "PROD-A19 implements and executes a private structural validator only for non-executing skeleton hold packets.",
    "PROD-A19 validates hold-packet shape and rejection mutations; it does not implement or execute a training-cost estimator.",
    "PROD-A19 does not produce estimate values, validate estimate values, train models, run benchmarks, calibrate estimates, or infer runtime, savings, accuracy, or model quality.",
    "PROD-A19 does not publish docs, update public/dev surfaces, approve public copy, or claim estimator accuracy, training savings, runtime performance, SDK stability, compiler correctness, semantic preservation, hardware readiness, silicon readiness, public readiness, reviewer approval, or broad EML advantage.",
]


def load_prod_a18_result() -> dict[str, Any]:
    path = (
        ROOT
        / "python/results/prod_a18_training_cost_estimator_non_executing_skeleton_implementation"
        / f"prod_a18_training_cost_estimator_non_executing_skeleton_implementation_{STAMP}.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    prod_a18.validate_payload(payload)
    return payload


def base_input() -> dict[str, Any]:
    return copy.deepcopy(prod_a18.SAMPLE_ACCEPTED_INPUT)


def accepted_fixture() -> dict[str, Any]:
    return {
        "fixtureId": "accepted_non_executing_hold_packet",
        "expectedDisposition": "accept_skeleton_hold_packet",
        "packet": build_hold_packet(base_input()),
    }


def rejection_fixtures() -> list[dict[str, Any]]:
    base = build_hold_packet(base_input())
    populated_cost = copy.deepcopy(base)
    populated_cost["static_expression_cost"] = {"value": 1}

    true_claim = copy.deepcopy(base)
    true_claim["claim_flags"]["estimator_accuracy_claim"] = True

    missing_hold_reason = copy.deepcopy(base)
    missing_hold_reason.pop("hold_reason", None)

    wrong_disposition = copy.deepcopy(base)
    wrong_disposition["disposition"] = "estimate_ready"

    return [
        {
            "fixtureId": "reject_cost_view_value_present",
            "expectedDisposition": "reject_skeleton_hold_packet",
            "packet": populated_cost,
            "mutation": "populate static_expression_cost with a value",
        },
        {
            "fixtureId": "reject_true_accuracy_claim_flag",
            "expectedDisposition": "reject_skeleton_hold_packet",
            "packet": true_claim,
            "mutation": "set estimator_accuracy_claim true",
        },
        {
            "fixtureId": "reject_missing_hold_reason",
            "expectedDisposition": "reject_skeleton_hold_packet",
            "packet": missing_hold_reason,
            "mutation": "remove hold_reason",
        },
        {
            "fixtureId": "reject_non_hold_disposition",
            "expectedDisposition": "reject_skeleton_hold_packet",
            "packet": wrong_disposition,
            "mutation": "replace hold_no_estimate disposition",
        },
    ]


def validate_fixture_set(fixtures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for fixture in fixtures:
        result = validate_skeleton_hold_packet(fixture["packet"])
        expected = fixture["expectedDisposition"]
        matched = (
            result.disposition == "accept"
            if expected == "accept_skeleton_hold_packet"
            else result.disposition == "reject"
        )
        rows.append(
            {
                "fixtureId": fixture["fixtureId"],
                "expectedDisposition": expected,
                "actualDisposition": result.disposition,
                "errors": list(result.errors),
                "matchedExpectation": matched,
            }
        )
    return rows


def build_payload() -> dict[str, Any]:
    source = load_prod_a18_result()
    accepted = [accepted_fixture()]
    rejected = rejection_fixtures()
    accepted_results = validate_fixture_set(accepted)
    rejection_results = validate_fixture_set(rejected)
    all_results = accepted_results + rejection_results
    matched = [row for row in all_results if row["matchedExpectation"]]
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceImplementedModulePath": source["summary"]["implementedModulePath"],
        "acceptedSkeletonFixtureCount": len(accepted_results),
        "rejectionSkeletonFixtureCount": len(rejection_results),
        "fixtureValidationResultCount": len(all_results),
        "matchedExpectationCount": len(matched),
        "allFixtureExpectationsMatched": len(matched) == len(all_results),
        "skeletonFixtureValidatorImplemented": True,
        "skeletonFixtureValidatorExecuted": True,
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
        artifact_type="training_cost_estimator_skeleton_fixture_validator",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "acceptedSkeletonFixtureResults": accepted_results,
            "rejectionSkeletonFixtureResults": rejection_results,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "prod-a18-training-cost-estimator-non-executing-skeleton-implementation":
        raise ValueError("PROD-A19 must consume PROD-A18")
    summary = payload["summary"]
    if summary["acceptedSkeletonFixtureCount"] != 1:
        raise ValueError("expected one accepted skeleton fixture")
    if summary["rejectionSkeletonFixtureCount"] != 4:
        raise ValueError("expected four rejection skeleton fixtures")
    if summary["fixtureValidationResultCount"] != 5:
        raise ValueError("expected five fixture validation results")
    if summary["matchedExpectationCount"] != 5 or summary["allFixtureExpectationsMatched"] is not True:
        raise ValueError("all fixture expectations must match")
    for key in ["skeletonFixtureValidatorImplemented", "skeletonFixtureValidatorExecuted"]:
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
    for row in payload["acceptedSkeletonFixtureResults"]:
        if row["actualDisposition"] != "accept" or row["errors"]:
            raise ValueError(f"accepted fixture failed: {row['fixtureId']}")
    for row in payload["rejectionSkeletonFixtureResults"]:
        if row["actualDisposition"] != "reject" or not row["errors"]:
            raise ValueError(f"rejection fixture failed: {row['fixtureId']}")
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
        semantic_strength="private_skeleton_fixture_validator_no_estimator_execution_or_public_claim",
        source=f"python/results/prod_a19_training_cost_estimator_skeleton_fixture_validator/prod_a19_training_cost_estimator_skeleton_fixture_validator_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="prod_a19_training_cost_estimator_skeleton_fixture_validator_feed",
        date=DATE,
        status=payload["status"],
        next_action="Review the private skeleton validator result before any estimator implementation gate.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "fixtureValidationResultCount": payload["summary"]["fixtureValidationResultCount"],
            "matchedExpectationCount": payload["summary"]["matchedExpectationCount"],
            "estimateValuesProduced": payload["summary"]["estimateValuesProduced"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="PROD-A19 Training Cost Estimator Skeleton Fixture Validator",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("accepted skeleton fixtures", payload["summary"]["acceptedSkeletonFixtureCount"]),
            ("rejection skeleton fixtures", payload["summary"]["rejectionSkeletonFixtureCount"]),
            ("fixture validation results", payload["summary"]["fixtureValidationResultCount"]),
            ("matched expectations", payload["summary"]["matchedExpectationCount"]),
            ("estimator implemented", payload["summary"]["estimatorImplemented"]),
            ("estimate values produced", payload["summary"]["estimateValuesProduced"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Accepted Skeleton Fixture Results",
                [
                    f"- `{row['fixtureId']}`: `{row['actualDisposition']}`; matched: `{row['matchedExpectation']}`"
                    for row in payload["acceptedSkeletonFixtureResults"]
                ],
            ),
            (
                "Rejection Skeleton Fixture Results",
                [
                    f"- `{row['fixtureId']}`: `{row['actualDisposition']}`; errors: `{row['errors']}`"
                    for row in payload["rejectionSkeletonFixtureResults"]
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
    result_path = out_dir / f"prod_a19_training_cost_estimator_skeleton_fixture_validator_{STAMP}.json"
    report_path = report_dir / f"prod_a19_training_cost_estimator_skeleton_fixture_validator_{STAMP}.md"
    evidence_path = evidence_dir / "prod_a19_training_cost_estimator_skeleton_fixture_validator.json"
    feed_path = command_feed_dir / f"prod_a19_training_cost_estimator_skeleton_fixture_validator_feed_{STAMP}.json"
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
        default=ROOT / "python/results/prod_a19_training_cost_estimator_skeleton_fixture_validator",
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
    print("PROD_A19_TRAINING_COST_ESTIMATOR_SKELETON_FIXTURE_VALIDATOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
