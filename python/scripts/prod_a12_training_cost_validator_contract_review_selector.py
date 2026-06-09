#!/usr/bin/env python3
"""PROD-A12 private training-cost validator contract review selector."""

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

from scripts import prod_a11_training_cost_estimator_fixture_validator_implementation as prod_a11  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-08"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.training_cost_validator_contract_review_selector.v0"
STATUS = "PROD_A12_TRAINING_COST_VALIDATOR_CONTRACT_REVIEW_SELECTOR_PASS"
ARTIFACT_ID = "prod-a12-training-cost-validator-contract-review-selector"
NEXT_RECOMMENDED_ARTIFACT = "PROD-A13 private training-cost estimator input-output contract seed"

TRUE_CLAIM_FLAGS = {
    "prod_a11_consumed",
    "validator_contract_review_created",
    "fixture_expectations_reviewed",
    "private_validator_boundary_accepted",
    "next_action_selected",
    "immediate_estimator_implementation_blocked",
    "public_claims_blocked",
}

CLAIM_FLAGS = {
    "prod_a11_consumed": True,
    "validator_contract_review_created": True,
    "fixture_expectations_reviewed": True,
    "private_validator_boundary_accepted": True,
    "next_action_selected": True,
    "immediate_estimator_implementation_blocked": True,
    "public_claims_blocked": True,
    "estimator_implemented": False,
    "estimator_executed": False,
    "estimator_contract_created": False,
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
    "PROD-A12 is a private review selector for the PROD-A11 fixture validator boundary; it does not implement or execute an estimator.",
    "PROD-A12 accepts the private validator boundary only for the existing PROD-A6 accepted/rejection fixture shape.",
    "PROD-A12 does not claim estimator accuracy, training savings, runtime performance, public product readiness, SDK stability, compiler correctness, semantic preservation, hardware readiness, silicon readiness, reviewer approval, or broad EML advantage.",
    "PROD-A12 does not create public docs, update public/dev surfaces, run benchmarks, calibrate estimates, train models, or touch laptop-owned electronics repositories.",
]


def load_prod_a11_result() -> dict[str, Any]:
    path = (
        ROOT
        / "python/results/prod_a11_training_cost_estimator_fixture_validator_implementation"
        / f"prod_a11_training_cost_estimator_fixture_validator_implementation_{STAMP}.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    prod_a11.validate_payload(payload)
    return payload


def candidate_actions() -> list[dict[str, str]]:
    return [
        {
            "actionId": "private_estimator_io_contract_seed",
            "decision": "selected",
            "reason": "The fixture validator matched all current expectations, so the next useful step is to define the estimator input/output contract before any estimator code.",
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
        },
        {
            "actionId": "immediate_estimator_implementation",
            "decision": "blocked",
            "reason": "The fixture validator proves only structural packet acceptance/rejection, not estimator semantics, calibration, accuracy, savings, or runtime behavior.",
            "nextArtifact": "Requires a bounded private estimator input/output contract first.",
        },
        {
            "actionId": "public_product_or_docs",
            "decision": "blocked",
            "reason": "No public readiness, package release, or documentation approval exists.",
            "nextArtifact": "Requires separate public-copy and product-readiness gates.",
        },
        {
            "actionId": "hold_estimator_lane",
            "decision": "parked",
            "reason": "A hold remains available if the next request is not estimator-specific, but the current explicit product/tooling redirect supports one more private contract step.",
            "nextArtifact": "Hold only if no explicit product/tooling request remains.",
        },
    ]


def review_rows(source: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "reviewId": "accepted_fixtures_clean",
            "status": "pass",
            "detail": f"{source['summary']['acceptedFixtureCount']} accepted fixtures returned accept with no errors.",
        },
        {
            "reviewId": "rejection_fixtures_blocked",
            "status": "pass",
            "detail": f"{source['summary']['rejectionFixtureCount']} rejection fixtures returned reject with errors.",
        },
        {
            "reviewId": "expectation_match_count",
            "status": "pass",
            "detail": f"{source['summary']['matchedExpectationCount']} of {source['summary']['fixtureValidationResultCount']} fixture expectations matched.",
        },
        {
            "reviewId": "semantic_scope",
            "status": "bounded",
            "detail": "Validator covers private structural fixture shape only; estimator semantics and accuracy remain out of scope.",
        },
    ]


def build_payload() -> dict[str, Any]:
    source = load_prod_a11_result()
    rows = review_rows(source)
    actions = candidate_actions()
    selected = [action for action in actions if action["decision"] == "selected"]
    blocked = [action for action in actions if action["decision"] == "blocked"]
    summary = {
        "sourceArtifact": source["artifactId"],
        "fixtureValidationResultCount": source["summary"]["fixtureValidationResultCount"],
        "matchedExpectationCount": source["summary"]["matchedExpectationCount"],
        "allFixtureExpectationsMatched": source["summary"]["allFixtureExpectationsMatched"],
        "reviewRowCount": len(rows),
        "candidateActionCount": len(actions),
        "blockedActionCount": len(blocked),
        "selectedActionId": selected[0]["actionId"],
        "privateValidatorBoundaryAccepted": True,
        "immediateEstimatorImplementationBlocked": True,
        "estimatorImplemented": False,
        "estimatorExecuted": False,
        "estimatorContractCreated": False,
        "publicProductReady": False,
        "trainingSavingsClaim": False,
        "estimatorAccuracyClaim": False,
        "runtimePerformanceClaim": False,
        "nextRecommendedArtifact": selected[0]["nextArtifact"],
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id=ARTIFACT_ID,
        artifact_type="training_cost_validator_contract_review_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "reviewRows": rows,
            "candidateActions": actions,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "prod-a11-training-cost-estimator-fixture-validator-implementation":
        raise ValueError("PROD-A12 must consume PROD-A11")
    summary = payload["summary"]
    if summary["fixtureValidationResultCount"] != 7:
        raise ValueError("fixture validation count drift")
    if summary["matchedExpectationCount"] != 7:
        raise ValueError("expected all fixture expectations to match")
    if summary["selectedActionId"] != "private_estimator_io_contract_seed":
        raise ValueError("unexpected selected action")
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected next artifact")
    for key in [
        "allFixtureExpectationsMatched",
        "privateValidatorBoundaryAccepted",
        "immediateEstimatorImplementationBlocked",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "estimatorImplemented",
        "estimatorExecuted",
        "estimatorContractCreated",
        "publicProductReady",
        "trainingSavingsClaim",
        "estimatorAccuracyClaim",
        "runtimePerformanceClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    decisions = {action["actionId"]: action["decision"] for action in payload["candidateActions"]}
    if decisions["immediate_estimator_implementation"] != "blocked":
        raise ValueError("immediate estimator implementation must remain blocked")
    if decisions["public_product_or_docs"] != "blocked":
        raise ValueError("public product/docs must remain blocked")
    if {row["status"] for row in payload["reviewRows"]} != {"pass", "bounded"}:
        raise ValueError("unexpected review statuses")
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
        semantic_strength="private_validator_contract_review_selector_no_estimator_or_public_claim",
        source=f"python/results/prod_a12_training_cost_validator_contract_review_selector/prod_a12_training_cost_validator_contract_review_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="prod_a12_training_cost_validator_contract_review_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Create a private training-cost estimator input/output contract seed before any estimator implementation.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "selectedActionId": payload["summary"]["selectedActionId"],
            "privateValidatorBoundaryAccepted": payload["summary"]["privateValidatorBoundaryAccepted"],
            "immediateEstimatorImplementationBlocked": payload["summary"]["immediateEstimatorImplementationBlocked"],
            "estimatorImplemented": payload["summary"]["estimatorImplemented"],
            "publicProductReady": payload["summary"]["publicProductReady"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="PROD-A12 Training Cost Validator Contract Review Selector",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("fixture validation results", payload["summary"]["fixtureValidationResultCount"]),
            ("matched expectations", payload["summary"]["matchedExpectationCount"]),
            ("selected action", payload["summary"]["selectedActionId"]),
            ("private validator boundary accepted", payload["summary"]["privateValidatorBoundaryAccepted"]),
            ("immediate estimator implementation blocked", payload["summary"]["immediateEstimatorImplementationBlocked"]),
            ("estimator implemented", payload["summary"]["estimatorImplemented"]),
            ("public product ready", payload["summary"]["publicProductReady"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Review Rows",
                [f"- `{row['reviewId']}`: `{row['status']}` - {row['detail']}" for row in payload["reviewRows"]],
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
    result_path = out_dir / f"prod_a12_training_cost_validator_contract_review_selector_{STAMP}.json"
    report_path = report_dir / f"prod_a12_training_cost_validator_contract_review_selector_{STAMP}.md"
    evidence_path = evidence_dir / "prod_a12_training_cost_validator_contract_review_selector.json"
    feed_path = command_feed_dir / f"prod_a12_training_cost_validator_contract_review_selector_feed_{STAMP}.json"
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
        default=ROOT / "python/results/prod_a12_training_cost_validator_contract_review_selector",
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
    print("PROD_A12_TRAINING_COST_VALIDATOR_CONTRACT_REVIEW_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
