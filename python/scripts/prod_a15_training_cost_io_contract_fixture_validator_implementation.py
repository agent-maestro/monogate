#!/usr/bin/env python3
"""PROD-A15 private training-cost I/O contract fixture validator implementation."""

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

from monogate.training_cost_io_contract_validator import validate_io_contract_fixture  # noqa: E402
from scripts import prod_a13_training_cost_estimator_io_contract_seed as prod_a13  # noqa: E402
from scripts import prod_a14_training_cost_contract_fixture_validator_or_hold_selector as prod_a14  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-08"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.training_cost_io_contract_fixture_validator_implementation.v0"
STATUS = "PROD_A15_TRAINING_COST_IO_CONTRACT_FIXTURE_VALIDATOR_IMPLEMENTATION_PASS"
ARTIFACT_ID = "prod-a15-training-cost-io-contract-fixture-validator-implementation"
NEXT_RECOMMENDED_ARTIFACT = "PROD-A16 private training-cost estimator implementation gate or hold selector"

TRUE_CLAIM_FLAGS = {
    "prod_a14_consumed",
    "prod_a13_consumed",
    "contract_fixture_validator_implemented",
    "contract_fixture_validator_executed",
    "accepted_contract_fixture_results_recorded",
    "rejection_contract_fixture_results_recorded",
    "immediate_estimator_implementation_blocked",
    "public_claims_blocked",
}

CLAIM_FLAGS = {
    "prod_a14_consumed": True,
    "prod_a13_consumed": True,
    "contract_fixture_validator_implemented": True,
    "contract_fixture_validator_executed": True,
    "accepted_contract_fixture_results_recorded": True,
    "rejection_contract_fixture_results_recorded": True,
    "immediate_estimator_implementation_blocked": True,
    "public_claims_blocked": True,
    "estimator_implemented": False,
    "estimator_executed": False,
    "model_training_executed": False,
    "runtime_benchmark_executed": False,
    "calibration_performed": False,
    "training_savings_claim": False,
    "estimator_accuracy_claim": False,
    "runtime_performance_claim": False,
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
    "PROD-A15 implements and executes a private structural validator only for PROD-A13 I/O contract fixture definitions.",
    "PROD-A15 does not implement or execute a training-cost estimator, validate estimate values, train models, run benchmarks, or calibrate estimates.",
    "PROD-A15 does not publish docs, update public/dev surfaces, approve public copy, or claim estimator accuracy, training savings, runtime performance, SDK stability, compiler correctness, semantic preservation, hardware readiness, silicon readiness, public readiness, reviewer approval, or broad EML advantage.",
    "PROD-A15 does not touch laptop-owned electronics repositories.",
]


def load_prod_a13_result() -> dict[str, Any]:
    path = (
        ROOT
        / "python/results/prod_a13_training_cost_estimator_io_contract_seed"
        / f"prod_a13_training_cost_estimator_io_contract_seed_{STAMP}.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    prod_a13.validate_payload(payload)
    return payload


def load_prod_a14_result() -> dict[str, Any]:
    path = (
        ROOT
        / "python/results/prod_a14_training_cost_contract_fixture_validator_or_hold_selector"
        / f"prod_a14_training_cost_contract_fixture_validator_or_hold_selector_{STAMP}.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    prod_a14.validate_payload(payload)
    return payload


def validate_fixture_set(fixtures: list[dict[str, Any]], contract: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for fixture in fixtures:
        result = validate_io_contract_fixture(fixture, contract)
        expected = fixture["expectedDisposition"]
        rows.append(
            {
                "fixtureId": fixture["fixtureId"],
                "expectedDisposition": expected,
                "actualDisposition": result.disposition,
                "errors": list(result.errors),
                "matchedExpectation": (
                    result.disposition == "accept"
                    if expected == "accept_contract_shape"
                    else result.disposition == "reject"
                ),
            }
        )
    return rows


def build_payload() -> dict[str, Any]:
    selector = load_prod_a14_result()
    contract_seed = load_prod_a13_result()
    fixtures = contract_seed["contractFixtures"]
    accepted = [fixture for fixture in fixtures if fixture["expectedDisposition"] == "accept_contract_shape"]
    rejected = [fixture for fixture in fixtures if fixture["expectedDisposition"] == "reject_contract_shape"]
    accepted_results = validate_fixture_set(accepted, contract_seed["outputContract"])
    rejection_results = validate_fixture_set(rejected, contract_seed["outputContract"])
    all_results = accepted_results + rejection_results
    matched = [row for row in all_results if row["matchedExpectation"]]
    summary = {
        "sourceSelectorArtifact": selector["artifactId"],
        "sourceContractArtifact": contract_seed["artifactId"],
        "sourceSelectedActionId": selector["summary"]["selectedActionId"],
        "acceptedContractFixtureCount": len(accepted_results),
        "rejectionContractFixtureCount": len(rejection_results),
        "fixtureValidationResultCount": len(all_results),
        "matchedExpectationCount": len(matched),
        "allFixtureExpectationsMatched": len(matched) == len(all_results),
        "contractFixtureValidatorImplemented": True,
        "contractFixtureValidatorExecuted": True,
        "immediateEstimatorImplementationBlocked": True,
        "estimatorImplemented": False,
        "estimatorExecuted": False,
        "modelTrainingExecuted": False,
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
        artifact_type="training_cost_io_contract_fixture_validator_implementation",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceSelectorArtifact": selector["artifactId"],
            "sourceContractArtifact": contract_seed["artifactId"],
            "acceptedContractFixtureResults": accepted_results,
            "rejectionContractFixtureResults": rejection_results,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceSelectorArtifact"] != "prod-a14-training-cost-contract-fixture-validator-or-hold-selector":
        raise ValueError("PROD-A15 must consume PROD-A14")
    if payload["sourceContractArtifact"] != "prod-a13-training-cost-estimator-io-contract-seed":
        raise ValueError("PROD-A15 must consume PROD-A13")
    summary = payload["summary"]
    if summary["sourceSelectedActionId"] != "implement_private_contract_fixture_validator":
        raise ValueError("PROD-A14 selected action drift")
    if summary["acceptedContractFixtureCount"] != 2:
        raise ValueError("expected two accepted contract fixtures")
    if summary["rejectionContractFixtureCount"] != 4:
        raise ValueError("expected four rejection contract fixtures")
    if summary["fixtureValidationResultCount"] != 6:
        raise ValueError("expected six fixture validation results")
    if summary["matchedExpectationCount"] != 6:
        raise ValueError("expected all fixture expectations to match")
    for key in [
        "allFixtureExpectationsMatched",
        "contractFixtureValidatorImplemented",
        "contractFixtureValidatorExecuted",
        "immediateEstimatorImplementationBlocked",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "estimatorImplemented",
        "estimatorExecuted",
        "modelTrainingExecuted",
        "runtimeBenchmarkExecuted",
        "calibrationPerformed",
        "publicProductReady",
        "trainingSavingsClaim",
        "estimatorAccuracyClaim",
        "runtimePerformanceClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    for row in payload["acceptedContractFixtureResults"]:
        if row["actualDisposition"] != "accept" or row["errors"]:
            raise ValueError(f"accepted fixture failed: {row['fixtureId']}")
    for row in payload["rejectionContractFixtureResults"]:
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
        semantic_strength="private_io_contract_fixture_validator_no_estimator_or_public_claim",
        source=f"python/results/prod_a15_training_cost_io_contract_fixture_validator_implementation/prod_a15_training_cost_io_contract_fixture_validator_implementation_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="prod_a15_training_cost_io_contract_fixture_validator_implementation_feed",
        date=DATE,
        status=payload["status"],
        next_action="Review the private fixture validator result before any estimator implementation gate.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceSelectorArtifact": payload["sourceSelectorArtifact"],
            "sourceContractArtifact": payload["sourceContractArtifact"],
            "fixtureValidationResultCount": payload["summary"]["fixtureValidationResultCount"],
            "matchedExpectationCount": payload["summary"]["matchedExpectationCount"],
            "contractFixtureValidatorImplemented": payload["summary"]["contractFixtureValidatorImplemented"],
            "estimatorImplemented": payload["summary"]["estimatorImplemented"],
            "publicProductReady": payload["summary"]["publicProductReady"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="PROD-A15 Training Cost I/O Contract Fixture Validator Implementation",
        status=payload["status"],
        summary_rows=[
            ("source selector artifact", payload["sourceSelectorArtifact"]),
            ("source contract artifact", payload["sourceContractArtifact"]),
            ("accepted fixtures", payload["summary"]["acceptedContractFixtureCount"]),
            ("rejection fixtures", payload["summary"]["rejectionContractFixtureCount"]),
            ("matched expectations", payload["summary"]["matchedExpectationCount"]),
            ("contract fixture validator implemented", payload["summary"]["contractFixtureValidatorImplemented"]),
            ("contract fixture validator executed", payload["summary"]["contractFixtureValidatorExecuted"]),
            ("estimator implemented", payload["summary"]["estimatorImplemented"]),
            ("public product ready", payload["summary"]["publicProductReady"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Accepted Contract Fixture Results",
                [
                    f"- `{row['fixtureId']}`: `{row['actualDisposition']}` matched=`{row['matchedExpectation']}`"
                    for row in payload["acceptedContractFixtureResults"]
                ],
            ),
            (
                "Rejection Contract Fixture Results",
                [
                    f"- `{row['fixtureId']}`: `{row['actualDisposition']}` matched=`{row['matchedExpectation']}` errors=`{'; '.join(row['errors'])}`"
                    for row in payload["rejectionContractFixtureResults"]
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
    result_path = out_dir / f"prod_a15_training_cost_io_contract_fixture_validator_implementation_{STAMP}.json"
    report_path = report_dir / f"prod_a15_training_cost_io_contract_fixture_validator_implementation_{STAMP}.md"
    evidence_path = evidence_dir / "prod_a15_training_cost_io_contract_fixture_validator_implementation.json"
    feed_path = command_feed_dir / f"prod_a15_training_cost_io_contract_fixture_validator_implementation_feed_{STAMP}.json"
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
        default=ROOT / "python/results/prod_a15_training_cost_io_contract_fixture_validator_implementation",
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
    print("PROD_A15_TRAINING_COST_IO_CONTRACT_FIXTURE_VALIDATOR_IMPLEMENTATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
