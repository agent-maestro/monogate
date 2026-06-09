#!/usr/bin/env python3
"""PROD-A11 private training-cost estimator fixture validator implementation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from monogate.training_cost_validator import validate_training_cost_fixture_packet  # noqa: E402
from scripts import prod_a10_private_product_roadmap_pause_digest as prod_a10  # noqa: E402
from scripts import prod_a6_training_cost_estimator_fixture_packet as prod_a6  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-08"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.training_cost_estimator_fixture_validator_implementation.v0"
STATUS = "PROD_A11_TRAINING_COST_ESTIMATOR_FIXTURE_VALIDATOR_IMPLEMENTATION_PASS"
ARTIFACT_ID = "prod-a11-training-cost-estimator-fixture-validator-implementation"
NEXT_RECOMMENDED_ARTIFACT = "PROD-A12 private training-cost estimator validator contract review or estimator hold selector"

TRUE_CLAIM_FLAGS = {
    "prod_a6_consumed",
    "prod_a10_consumed",
    "explicit_product_redirect_consumed",
    "fixture_validator_implemented",
    "fixture_validator_executed",
    "accepted_fixture_results_recorded",
    "rejection_fixture_results_recorded",
    "public_claims_blocked",
}

CLAIM_FLAGS = {
    "prod_a6_consumed": True,
    "prod_a10_consumed": True,
    "explicit_product_redirect_consumed": True,
    "fixture_validator_implemented": True,
    "fixture_validator_executed": True,
    "accepted_fixture_results_recorded": True,
    "rejection_fixture_results_recorded": True,
    "public_claims_blocked": True,
    "estimator_implemented": False,
    "estimator_executed": False,
    "model_training_executed": False,
    "runtime_benchmark_executed": False,
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
    "PROD-A11 implements and executes a private structural validator only for the PROD-A6 training-cost estimator fixture packet shape.",
    "PROD-A11 does not implement or execute a training-cost estimator, train a model, run a runtime benchmark, or calibrate estimates.",
    "PROD-A11 does not claim training savings, estimator accuracy, runtime performance, public product readiness, package release readiness, SDK stability, compiler correctness, semantic preservation, hardware readiness, silicon readiness, reviewer approval, or broad EML advantage.",
    "PROD-A11 does not create public docs, update public/dev surfaces, or touch laptop-owned electronics repositories.",
]


def validate_fixture_set(fixtures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for fixture in fixtures:
        result = validate_training_cost_fixture_packet(fixture["packet"])
        rows.append(
            {
                "fixtureId": fixture["fixtureId"],
                "expectedDisposition": fixture["expectedDisposition"],
                "actualDisposition": result.disposition,
                "errors": list(result.errors),
                "matchedExpectation": (
                    result.disposition == "accept"
                    if fixture["expectedDisposition"].startswith("accept")
                    else result.disposition == "reject"
                ),
            }
        )
    return rows


def build_payload() -> dict[str, Any]:
    fixture_packet = prod_a6.build_payload()
    prod_a6.validate_payload(fixture_packet)
    pause_digest = prod_a10.build_payload()
    prod_a10.validate_payload(pause_digest)

    accepted_results = validate_fixture_set(fixture_packet["acceptedFixtures"])
    rejection_results = validate_fixture_set(fixture_packet["rejectionFixtures"])
    all_results = accepted_results + rejection_results
    passing_results = [row for row in all_results if row["matchedExpectation"]]

    summary = {
        "sourceFixtureArtifact": fixture_packet["artifactId"],
        "sourcePauseArtifact": pause_digest["artifactId"],
        "explicitProductRedirectConsumed": True,
        "acceptedFixtureCount": len(accepted_results),
        "rejectionFixtureCount": len(rejection_results),
        "fixtureValidationResultCount": len(all_results),
        "matchedExpectationCount": len(passing_results),
        "validatorImplemented": True,
        "validatorExecuted": True,
        "allFixtureExpectationsMatched": len(passing_results) == len(all_results),
        "estimatorImplemented": False,
        "estimatorExecuted": False,
        "modelTrainingExecuted": False,
        "runtimeBenchmarkExecuted": False,
        "publicProductReady": False,
        "trainingSavingsClaim": False,
        "estimatorAccuracyClaim": False,
        "runtimePerformanceClaim": False,
        "nextRecommendedArtifact": NEXT_RECOMMENDED_ARTIFACT,
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id=ARTIFACT_ID,
        artifact_type="training_cost_estimator_fixture_validator_implementation",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceFixtureArtifact": fixture_packet["artifactId"],
            "sourcePauseArtifact": pause_digest["artifactId"],
            "acceptedFixtureResults": accepted_results,
            "rejectionFixtureResults": rejection_results,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceFixtureArtifact"] != "prod-a6-training-cost-estimator-fixture-packet":
        raise ValueError("PROD-A11 must consume PROD-A6")
    if payload["sourcePauseArtifact"] != "prod-a10-private-product-roadmap-pause-digest":
        raise ValueError("PROD-A11 must consume PROD-A10")
    summary = payload["summary"]
    if summary["acceptedFixtureCount"] != 2:
        raise ValueError("accepted fixture count drift")
    if summary["rejectionFixtureCount"] != 5:
        raise ValueError("rejection fixture count drift")
    if summary["fixtureValidationResultCount"] != 7:
        raise ValueError("fixture validation result count drift")
    if summary["matchedExpectationCount"] != 7:
        raise ValueError("expected all fixtures to match")
    for key in [
        "explicitProductRedirectConsumed",
        "validatorImplemented",
        "validatorExecuted",
        "allFixtureExpectationsMatched",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "estimatorImplemented",
        "estimatorExecuted",
        "modelTrainingExecuted",
        "runtimeBenchmarkExecuted",
        "publicProductReady",
        "trainingSavingsClaim",
        "estimatorAccuracyClaim",
        "runtimePerformanceClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    for row in payload["acceptedFixtureResults"]:
        if row["actualDisposition"] != "accept" or row["errors"]:
            raise ValueError(f"accepted fixture did not accept cleanly: {row['fixtureId']}")
    for row in payload["rejectionFixtureResults"]:
        if row["actualDisposition"] != "reject" or not row["errors"]:
            raise ValueError(f"rejection fixture did not reject with errors: {row['fixtureId']}")
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
        semantic_strength="private_fixture_validator_implementation_no_estimator_accuracy_or_public_claim",
        source=f"python/results/prod_a11_training_cost_estimator_fixture_validator_implementation/prod_a11_training_cost_estimator_fixture_validator_implementation_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="prod_a11_training_cost_estimator_fixture_validator_implementation_feed",
        date=DATE,
        status=payload["status"],
        next_action="Review the private validator contract result or hold estimator implementation until a concrete estimator request arrives.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceFixtureArtifact": payload["sourceFixtureArtifact"],
            "sourcePauseArtifact": payload["sourcePauseArtifact"],
            "fixtureValidationResultCount": payload["summary"]["fixtureValidationResultCount"],
            "matchedExpectationCount": payload["summary"]["matchedExpectationCount"],
            "validatorImplemented": payload["summary"]["validatorImplemented"],
            "estimatorImplemented": payload["summary"]["estimatorImplemented"],
            "publicProductReady": payload["summary"]["publicProductReady"],
            "trainingSavingsClaim": payload["summary"]["trainingSavingsClaim"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="PROD-A11 Training Cost Estimator Fixture Validator Implementation",
        status=payload["status"],
        summary_rows=[
            ("source fixture artifact", payload["sourceFixtureArtifact"]),
            ("source pause artifact", payload["sourcePauseArtifact"]),
            ("accepted fixtures", payload["summary"]["acceptedFixtureCount"]),
            ("rejection fixtures", payload["summary"]["rejectionFixtureCount"]),
            ("matched expectations", payload["summary"]["matchedExpectationCount"]),
            ("validator implemented", payload["summary"]["validatorImplemented"]),
            ("validator executed", payload["summary"]["validatorExecuted"]),
            ("estimator implemented", payload["summary"]["estimatorImplemented"]),
            ("public product ready", payload["summary"]["publicProductReady"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Accepted Fixture Results",
                [
                    f"- `{row['fixtureId']}`: `{row['actualDisposition']}` matched=`{row['matchedExpectation']}`"
                    for row in payload["acceptedFixtureResults"]
                ],
            ),
            (
                "Rejection Fixture Results",
                [
                    f"- `{row['fixtureId']}`: `{row['actualDisposition']}` matched=`{row['matchedExpectation']}` errors=`{'; '.join(row['errors'])}`"
                    for row in payload["rejectionFixtureResults"]
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
    result_path = out_dir / f"prod_a11_training_cost_estimator_fixture_validator_implementation_{STAMP}.json"
    report_path = report_dir / f"prod_a11_training_cost_estimator_fixture_validator_implementation_{STAMP}.md"
    evidence_path = evidence_dir / "prod_a11_training_cost_estimator_fixture_validator_implementation.json"
    feed_path = command_feed_dir / f"prod_a11_training_cost_estimator_fixture_validator_implementation_feed_{STAMP}.json"
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
        default=ROOT / "python/results/prod_a11_training_cost_estimator_fixture_validator_implementation",
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
    print("PROD_A11_TRAINING_COST_ESTIMATOR_FIXTURE_VALIDATOR_IMPLEMENTATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
