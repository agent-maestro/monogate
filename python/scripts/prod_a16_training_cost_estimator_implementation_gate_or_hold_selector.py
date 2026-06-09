#!/usr/bin/env python3
"""PROD-A16 private training-cost estimator implementation gate or hold selector."""

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

from scripts import prod_a15_training_cost_io_contract_fixture_validator_implementation as prod_a15  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-08"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.training_cost_estimator_implementation_gate_or_hold_selector.v0"
STATUS = "PROD_A16_TRAINING_COST_ESTIMATOR_IMPLEMENTATION_GATE_OR_HOLD_SELECTOR_PASS"
ARTIFACT_ID = "prod-a16-training-cost-estimator-implementation-gate-or-hold-selector"
NEXT_RECOMMENDED_ARTIFACT = "PROD-A17 private training-cost estimator skeleton contract seed"

TRUE_CLAIM_FLAGS = {
    "prod_a15_consumed",
    "implementation_gate_created",
    "fixture_validator_results_reviewed",
    "skeleton_contract_path_selected",
    "executing_estimator_implementation_blocked",
    "public_claims_blocked",
    "next_action_selected",
}

CLAIM_FLAGS = {
    "prod_a15_consumed": True,
    "implementation_gate_created": True,
    "fixture_validator_results_reviewed": True,
    "skeleton_contract_path_selected": True,
    "executing_estimator_implementation_blocked": True,
    "public_claims_blocked": True,
    "next_action_selected": True,
    "estimator_skeleton_contract_created": False,
    "estimator_implemented": False,
    "estimator_executed": False,
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
    "PROD-A16 is a private implementation gate selector; it does not create an estimator skeleton or implement an estimator.",
    "PROD-A16 selects only a non-executing estimator skeleton contract seed as the next bounded step.",
    "PROD-A16 does not implement or execute a training-cost estimator, validate estimate values, train models, run benchmarks, or calibrate estimates.",
    "PROD-A16 does not publish docs, update public/dev surfaces, approve public copy, or claim estimator accuracy, training savings, runtime performance, SDK stability, compiler correctness, semantic preservation, hardware readiness, silicon readiness, public readiness, reviewer approval, or broad EML advantage.",
]


def load_prod_a15_result() -> dict[str, Any]:
    path = (
        ROOT
        / "python/results/prod_a15_training_cost_io_contract_fixture_validator_implementation"
        / f"prod_a15_training_cost_io_contract_fixture_validator_implementation_{STAMP}.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    prod_a15.validate_payload(payload)
    return payload


def gate_criteria(source: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "criterionId": "contract_fixture_validator_executed",
            "status": "pass",
            "detail": "PROD-A15 implemented and executed the private I/O contract fixture validator.",
        },
        {
            "criterionId": "fixture_expectations_matched",
            "status": "pass",
            "detail": f"{source['summary']['matchedExpectationCount']} of {source['summary']['fixtureValidationResultCount']} fixture expectations matched.",
        },
        {
            "criterionId": "semantic_scope_limited",
            "status": "bounded",
            "detail": "Fixture validation covers contract metadata only; estimator values, calibration, savings, accuracy, and runtime remain unvalidated.",
        },
        {
            "criterionId": "skeleton_before_execution",
            "status": "required",
            "detail": "The next implementation step must be a non-executing skeleton contract seed before any estimator execution.",
        },
    ]


def candidate_actions() -> list[dict[str, str]]:
    return [
        {
            "actionId": "private_estimator_skeleton_contract_seed",
            "decision": "selected",
            "reason": "A non-executing skeleton contract can define module/API boundaries without producing estimates or implying product readiness.",
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
        },
        {
            "actionId": "executing_estimator_implementation",
            "decision": "blocked",
            "reason": "Executing estimator code would imply estimate behavior before skeleton boundaries, fixture expectations, and hold gates are reviewed.",
            "nextArtifact": "Requires a separate post-skeleton implementation gate.",
        },
        {
            "actionId": "public_product_or_docs",
            "decision": "blocked",
            "reason": "No public readiness, public-copy approval, or package release gate exists.",
            "nextArtifact": "Requires separate public-copy and product-readiness gates.",
        },
        {
            "actionId": "hold_training_cost_lane",
            "decision": "parked",
            "reason": "Hold remains available if the next request shifts away from product/tooling implementation.",
            "nextArtifact": "Hold only if no explicit product/tooling request remains.",
        },
    ]


def build_payload() -> dict[str, Any]:
    source = load_prod_a15_result()
    criteria = gate_criteria(source)
    actions = candidate_actions()
    selected = [action for action in actions if action["decision"] == "selected"]
    blocked = [action for action in actions if action["decision"] == "blocked"]
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceFixtureValidationResultCount": source["summary"]["fixtureValidationResultCount"],
        "sourceMatchedExpectationCount": source["summary"]["matchedExpectationCount"],
        "sourceAllFixtureExpectationsMatched": source["summary"]["allFixtureExpectationsMatched"],
        "gateCriterionCount": len(criteria),
        "candidateActionCount": len(actions),
        "blockedActionCount": len(blocked),
        "selectedActionId": selected[0]["actionId"],
        "implementationGateCreated": True,
        "skeletonContractPathSelected": True,
        "executingEstimatorImplementationBlocked": True,
        "estimatorSkeletonContractCreated": False,
        "estimatorImplemented": False,
        "estimatorExecuted": False,
        "modelTrainingExecuted": False,
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
        artifact_type="training_cost_estimator_implementation_gate_or_hold_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "gateCriteria": criteria,
            "candidateActions": actions,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "prod-a15-training-cost-io-contract-fixture-validator-implementation":
        raise ValueError("PROD-A16 must consume PROD-A15")
    summary = payload["summary"]
    if summary["sourceFixtureValidationResultCount"] != 6:
        raise ValueError("fixture validation result count drift")
    if summary["sourceMatchedExpectationCount"] != 6:
        raise ValueError("expected all A15 fixture expectations to match")
    if summary["selectedActionId"] != "private_estimator_skeleton_contract_seed":
        raise ValueError("unexpected selected action")
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected next artifact")
    for key in [
        "sourceAllFixtureExpectationsMatched",
        "implementationGateCreated",
        "skeletonContractPathSelected",
        "executingEstimatorImplementationBlocked",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "estimatorSkeletonContractCreated",
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
    decisions = {action["actionId"]: action["decision"] for action in payload["candidateActions"]}
    if decisions["executing_estimator_implementation"] != "blocked":
        raise ValueError("executing estimator implementation must remain blocked")
    if decisions["public_product_or_docs"] != "blocked":
        raise ValueError("public product/docs must remain blocked")
    statuses = {item["status"] for item in payload["gateCriteria"]}
    if statuses != {"pass", "bounded", "required"}:
        raise ValueError("unexpected gate criteria statuses")
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
        semantic_strength="private_estimator_implementation_gate_selector_no_estimator_execution_or_public_claim",
        source=f"python/results/prod_a16_training_cost_estimator_implementation_gate_or_hold_selector/prod_a16_training_cost_estimator_implementation_gate_or_hold_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="prod_a16_training_cost_estimator_implementation_gate_or_hold_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Create a private non-executing estimator skeleton contract seed; keep estimator execution blocked.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "selectedActionId": payload["summary"]["selectedActionId"],
            "executingEstimatorImplementationBlocked": payload["summary"]["executingEstimatorImplementationBlocked"],
            "estimatorSkeletonContractCreated": payload["summary"]["estimatorSkeletonContractCreated"],
            "estimatorImplemented": payload["summary"]["estimatorImplemented"],
            "publicProductReady": payload["summary"]["publicProductReady"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="PROD-A16 Training Cost Estimator Implementation Gate Or Hold Selector",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("source matched expectations", payload["summary"]["sourceMatchedExpectationCount"]),
            ("selected action", payload["summary"]["selectedActionId"]),
            ("skeleton contract path selected", payload["summary"]["skeletonContractPathSelected"]),
            ("executing estimator implementation blocked", payload["summary"]["executingEstimatorImplementationBlocked"]),
            ("estimator skeleton contract created", payload["summary"]["estimatorSkeletonContractCreated"]),
            ("estimator implemented", payload["summary"]["estimatorImplemented"]),
            ("public product ready", payload["summary"]["publicProductReady"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Gate Criteria",
                [f"- `{item['criterionId']}`: `{item['status']}` - {item['detail']}" for item in payload["gateCriteria"]],
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
    result_path = out_dir / f"prod_a16_training_cost_estimator_implementation_gate_or_hold_selector_{STAMP}.json"
    report_path = report_dir / f"prod_a16_training_cost_estimator_implementation_gate_or_hold_selector_{STAMP}.md"
    evidence_path = evidence_dir / "prod_a16_training_cost_estimator_implementation_gate_or_hold_selector.json"
    feed_path = command_feed_dir / f"prod_a16_training_cost_estimator_implementation_gate_or_hold_selector_feed_{STAMP}.json"
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
        default=ROOT / "python/results/prod_a16_training_cost_estimator_implementation_gate_or_hold_selector",
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
    print("PROD_A16_TRAINING_COST_ESTIMATOR_IMPLEMENTATION_GATE_OR_HOLD_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
