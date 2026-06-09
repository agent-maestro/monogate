#!/usr/bin/env python3
"""PROD-A20 private training-cost estimator skeleton review or hold selector."""

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

from scripts import prod_a19_training_cost_estimator_skeleton_fixture_validator as prod_a19  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-08"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.training_cost_estimator_skeleton_review_or_hold_selector.v0"
STATUS = "PROD_A20_TRAINING_COST_ESTIMATOR_SKELETON_REVIEW_OR_HOLD_SELECTOR_PASS"
ARTIFACT_ID = "prod-a20-training-cost-estimator-skeleton-review-or-hold-selector"
NEXT_RECOMMENDED_ARTIFACT = "PROD-A21 private training-cost estimator skeleton hold digest"

TRUE_CLAIM_FLAGS = {
    "prod_a19_consumed",
    "skeleton_validator_results_reviewed",
    "skeleton_hold_path_selected",
    "executing_estimator_implementation_blocked",
    "public_claims_blocked",
    "next_action_selected",
}

CLAIM_FLAGS = {
    "prod_a19_consumed": True,
    "skeleton_validator_results_reviewed": True,
    "skeleton_hold_path_selected": True,
    "executing_estimator_implementation_blocked": True,
    "public_claims_blocked": True,
    "next_action_selected": True,
    "skeleton_hold_digest_created": False,
    "estimator_implementation_gate_opened": False,
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
    "PROD-A20 is a private review-or-hold selector; it does not implement or execute a training-cost estimator.",
    "PROD-A20 reviews the PROD-A19 skeleton validator result and selects a hold digest before any estimate-producing implementation gate.",
    "PROD-A20 does not produce estimate values, validate estimate values, train models, run benchmarks, calibrate estimates, or infer runtime, savings, accuracy, or model quality.",
    "PROD-A20 does not publish docs, update public/dev surfaces, approve public copy, or claim estimator accuracy, training savings, runtime performance, SDK stability, compiler correctness, semantic preservation, hardware readiness, silicon readiness, public readiness, reviewer approval, or broad EML advantage.",
]


def load_prod_a19_result() -> dict[str, Any]:
    path = (
        ROOT
        / "python/results/prod_a19_training_cost_estimator_skeleton_fixture_validator"
        / f"prod_a19_training_cost_estimator_skeleton_fixture_validator_{STAMP}.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    prod_a19.validate_payload(payload)
    return payload


def review_criteria(source: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "criterionId": "skeleton_validator_executed",
            "status": "pass",
            "detail": "PROD-A19 implemented and executed the private skeleton hold-packet validator.",
        },
        {
            "criterionId": "fixture_expectations_matched",
            "status": "pass",
            "detail": f"{source['summary']['matchedExpectationCount']} of {source['summary']['fixtureValidationResultCount']} fixture expectations matched.",
        },
        {
            "criterionId": "estimate_values_remain_blocked",
            "status": "bounded",
            "detail": "A19 verifies rejection for populated cost-view fields; it does not validate or produce estimate values.",
        },
        {
            "criterionId": "implementation_gate_requires_review",
            "status": "required",
            "detail": "A later estimate-producing gate requires explicit reviewer approval or a new bounded user request.",
        },
    ]


def candidate_actions() -> list[dict[str, str]]:
    return [
        {
            "actionId": "private_skeleton_hold_digest",
            "decision": "selected",
            "reason": "The skeleton and validator are now coherent enough to park as a bounded private hold state before any estimator behavior.",
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
        },
        {
            "actionId": "open_estimator_implementation_gate",
            "decision": "blocked",
            "reason": "No reviewer approval, estimate-value contract, calibration protocol, or real-user usefulness condition exists.",
            "nextArtifact": "Requires separate explicit implementation-gate approval.",
        },
        {
            "actionId": "public_product_or_docs",
            "decision": "blocked",
            "reason": "No public readiness, public-copy approval, or package release gate exists.",
            "nextArtifact": "Requires separate public-copy and product-readiness gates.",
        },
        {
            "actionId": "continue_fixture_expansion",
            "decision": "parked",
            "reason": "Additional fixture expansion has diminishing value unless a reviewer identifies a concrete gap.",
            "nextArtifact": "Reopen only with a named missing fixture or reviewer concern.",
        },
    ]


def build_payload() -> dict[str, Any]:
    source = load_prod_a19_result()
    criteria = review_criteria(source)
    actions = candidate_actions()
    selected = [action for action in actions if action["decision"] == "selected"]
    blocked = [action for action in actions if action["decision"] == "blocked"]
    parked = [action for action in actions if action["decision"] == "parked"]
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceFixtureValidationResultCount": source["summary"]["fixtureValidationResultCount"],
        "sourceMatchedExpectationCount": source["summary"]["matchedExpectationCount"],
        "sourceAllFixtureExpectationsMatched": source["summary"]["allFixtureExpectationsMatched"],
        "reviewCriterionCount": len(criteria),
        "candidateActionCount": len(actions),
        "blockedActionCount": len(blocked),
        "parkedActionCount": len(parked),
        "selectedActionId": selected[0]["actionId"],
        "skeletonValidatorResultsReviewed": True,
        "skeletonHoldPathSelected": True,
        "executingEstimatorImplementationBlocked": True,
        "skeletonHoldDigestCreated": False,
        "estimatorImplementationGateOpened": False,
        "estimatorImplemented": False,
        "estimatorExecuted": False,
        "estimateValuesProduced": False,
        "runtimeBenchmarkExecuted": False,
        "calibrationPerformed": False,
        "publicProductReady": False,
        "trainingSavingsClaim": False,
        "estimatorAccuracyClaim": False,
        "runtimePerformanceClaim": False,
        "nextRecommendedArtifact": selected[0]["nextArtifact"],
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id=ARTIFACT_ID,
        artifact_type="training_cost_estimator_skeleton_review_or_hold_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "reviewCriteria": criteria,
            "candidateActions": actions,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "prod-a19-training-cost-estimator-skeleton-fixture-validator":
        raise ValueError("PROD-A20 must consume PROD-A19")
    summary = payload["summary"]
    if summary["sourceFixtureValidationResultCount"] != 5:
        raise ValueError("fixture validation result count drift")
    if summary["sourceMatchedExpectationCount"] != 5:
        raise ValueError("expected all A19 fixture expectations to match")
    if summary["selectedActionId"] != "private_skeleton_hold_digest":
        raise ValueError("unexpected selected action")
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected next artifact")
    for key in [
        "sourceAllFixtureExpectationsMatched",
        "skeletonValidatorResultsReviewed",
        "skeletonHoldPathSelected",
        "executingEstimatorImplementationBlocked",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "skeletonHoldDigestCreated",
        "estimatorImplementationGateOpened",
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
    decisions = {action["actionId"]: action["decision"] for action in payload["candidateActions"]}
    if decisions["open_estimator_implementation_gate"] != "blocked":
        raise ValueError("estimator implementation gate must remain blocked")
    if decisions["public_product_or_docs"] != "blocked":
        raise ValueError("public product/docs must remain blocked")
    if decisions["continue_fixture_expansion"] != "parked":
        raise ValueError("fixture expansion must be parked")
    statuses = {item["status"] for item in payload["reviewCriteria"]}
    if statuses != {"pass", "bounded", "required"}:
        raise ValueError("unexpected review criteria statuses")
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
        semantic_strength="private_skeleton_review_hold_selector_no_estimator_execution_or_public_claim",
        source=f"python/results/prod_a20_training_cost_estimator_skeleton_review_or_hold_selector/prod_a20_training_cost_estimator_skeleton_review_or_hold_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="prod_a20_training_cost_estimator_skeleton_review_or_hold_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Create a private skeleton hold digest before any estimator implementation gate.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "selectedActionId": payload["summary"]["selectedActionId"],
            "estimatorImplementationGateOpened": payload["summary"]["estimatorImplementationGateOpened"],
            "estimateValuesProduced": payload["summary"]["estimateValuesProduced"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="PROD-A20 Training Cost Estimator Skeleton Review Or Hold Selector",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("review criteria", payload["summary"]["reviewCriterionCount"]),
            ("candidate actions", payload["summary"]["candidateActionCount"]),
            ("selected action", payload["summary"]["selectedActionId"]),
            ("blocked actions", payload["summary"]["blockedActionCount"]),
            ("estimator implementation gate opened", payload["summary"]["estimatorImplementationGateOpened"]),
            ("estimate values produced", payload["summary"]["estimateValuesProduced"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Review Criteria",
                [
                    f"- `{item['criterionId']}`: `{item['status']}` - {item['detail']}"
                    for item in payload["reviewCriteria"]
                ],
            ),
            (
                "Candidate Actions",
                [
                    f"- `{item['actionId']}`: `{item['decision']}` - {item['reason']}"
                    for item in payload["candidateActions"]
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
    result_path = out_dir / f"prod_a20_training_cost_estimator_skeleton_review_or_hold_selector_{STAMP}.json"
    report_path = report_dir / f"prod_a20_training_cost_estimator_skeleton_review_or_hold_selector_{STAMP}.md"
    evidence_path = evidence_dir / "prod_a20_training_cost_estimator_skeleton_review_or_hold_selector.json"
    feed_path = command_feed_dir / f"prod_a20_training_cost_estimator_skeleton_review_or_hold_selector_feed_{STAMP}.json"
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
        default=ROOT / "python/results/prod_a20_training_cost_estimator_skeleton_review_or_hold_selector",
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
    print("PROD_A20_TRAINING_COST_ESTIMATOR_SKELETON_REVIEW_OR_HOLD_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
