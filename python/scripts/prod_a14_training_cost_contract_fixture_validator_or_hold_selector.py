#!/usr/bin/env python3
"""PROD-A14 private training-cost contract fixture validator or hold selector."""

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

from scripts import prod_a13_training_cost_estimator_io_contract_seed as prod_a13  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-08"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.training_cost_contract_fixture_validator_or_hold_selector.v0"
STATUS = "PROD_A14_TRAINING_COST_CONTRACT_FIXTURE_VALIDATOR_OR_HOLD_SELECTOR_PASS"
ARTIFACT_ID = "prod-a14-training-cost-contract-fixture-validator-or-hold-selector"
NEXT_RECOMMENDED_ARTIFACT = "PROD-A15 private training-cost estimator I/O contract fixture validator implementation"

TRUE_CLAIM_FLAGS = {
    "prod_a13_consumed",
    "contract_fixture_path_reviewed",
    "validator_implementation_path_selected",
    "immediate_estimator_implementation_blocked",
    "public_claims_blocked",
    "next_action_selected",
}

CLAIM_FLAGS = {
    "prod_a13_consumed": True,
    "contract_fixture_path_reviewed": True,
    "validator_implementation_path_selected": True,
    "immediate_estimator_implementation_blocked": True,
    "public_claims_blocked": True,
    "next_action_selected": True,
    "contract_fixture_validator_implemented": False,
    "contract_fixture_validator_executed": False,
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
    "PROD-A14 is a private selector; it does not implement or execute a contract fixture validator.",
    "PROD-A14 selects a bounded validator implementation path before any training-cost estimator implementation.",
    "PROD-A14 does not implement or execute an estimator, train models, run benchmarks, calibrate estimates, publish docs, update public/dev surfaces, or approve public copy.",
    "PROD-A14 does not claim estimator accuracy, training savings, runtime performance, SDK stability, compiler correctness, semantic preservation, hardware readiness, silicon readiness, public readiness, reviewer approval, or broad EML advantage.",
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


def decision_criteria(source: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "criterionId": "contract_fixtures_exist",
            "status": "pass",
            "detail": f"{source['summary']['contractFixtureCount']} contract fixtures exist in PROD-A13.",
        },
        {
            "criterionId": "accepted_and_rejection_balance",
            "status": "pass",
            "detail": f"{source['summary']['acceptedContractFixtureCount']} accepted and {source['summary']['rejectionContractFixtureCount']} rejection fixtures are recorded.",
        },
        {
            "criterionId": "output_boundary_carried",
            "status": "pass",
            "detail": "Output contract carries required fields, caveats, blocked claims, and false claim flags.",
        },
        {
            "criterionId": "estimator_still_blocked",
            "status": "bounded",
            "detail": "Fixture validation can harden the contract, but cannot justify estimator implementation, accuracy, savings, or runtime claims.",
        },
    ]


def candidate_actions() -> list[dict[str, str]]:
    return [
        {
            "actionId": "implement_private_contract_fixture_validator",
            "decision": "selected",
            "reason": "The PROD-A13 contract fixtures are stable enough to validate structurally before estimator work.",
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
        },
        {
            "actionId": "immediate_estimator_implementation",
            "decision": "blocked",
            "reason": "A contract seed without executable fixture validation is not enough to implement an estimator.",
            "nextArtifact": "Requires PROD-A15 validator implementation first.",
        },
        {
            "actionId": "public_product_or_docs",
            "decision": "blocked",
            "reason": "No public readiness, package release, or public-copy approval exists.",
            "nextArtifact": "Requires separate public-copy and product-readiness gates.",
        },
        {
            "actionId": "hold_estimator_lane",
            "decision": "parked",
            "reason": "Hold remains available if the next request shifts away from this product lane.",
            "nextArtifact": "Hold only if no explicit product/tooling request remains.",
        },
    ]


def build_payload() -> dict[str, Any]:
    source = load_prod_a13_result()
    criteria = decision_criteria(source)
    actions = candidate_actions()
    selected = [action for action in actions if action["decision"] == "selected"]
    blocked = [action for action in actions if action["decision"] == "blocked"]
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceContractFixtureCount": source["summary"]["contractFixtureCount"],
        "sourceAcceptedContractFixtureCount": source["summary"]["acceptedContractFixtureCount"],
        "sourceRejectionContractFixtureCount": source["summary"]["rejectionContractFixtureCount"],
        "decisionCriterionCount": len(criteria),
        "candidateActionCount": len(actions),
        "blockedActionCount": len(blocked),
        "selectedActionId": selected[0]["actionId"],
        "validatorImplementationPathSelected": True,
        "immediateEstimatorImplementationBlocked": True,
        "contractFixtureValidatorImplemented": False,
        "contractFixtureValidatorExecuted": False,
        "estimatorImplemented": False,
        "estimatorExecuted": False,
        "publicProductReady": False,
        "trainingSavingsClaim": False,
        "estimatorAccuracyClaim": False,
        "runtimePerformanceClaim": False,
        "nextRecommendedArtifact": selected[0]["nextArtifact"],
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id=ARTIFACT_ID,
        artifact_type="training_cost_contract_fixture_validator_or_hold_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "decisionCriteria": criteria,
            "candidateActions": actions,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "prod-a13-training-cost-estimator-io-contract-seed":
        raise ValueError("PROD-A14 must consume PROD-A13")
    summary = payload["summary"]
    if summary["sourceContractFixtureCount"] != 6:
        raise ValueError("contract fixture count drift")
    if summary["selectedActionId"] != "implement_private_contract_fixture_validator":
        raise ValueError("unexpected selected action")
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected next artifact")
    for key in ["validatorImplementationPathSelected", "immediateEstimatorImplementationBlocked"]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "contractFixtureValidatorImplemented",
        "contractFixtureValidatorExecuted",
        "estimatorImplemented",
        "estimatorExecuted",
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
    if {item["status"] for item in payload["decisionCriteria"]} != {"pass", "bounded"}:
        raise ValueError("unexpected decision criteria statuses")
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
        semantic_strength="private_contract_fixture_validator_path_selector_no_estimator_or_public_claim",
        source=f"python/results/prod_a14_training_cost_contract_fixture_validator_or_hold_selector/prod_a14_training_cost_contract_fixture_validator_or_hold_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="prod_a14_training_cost_contract_fixture_validator_or_hold_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Implement a private training-cost estimator I/O contract fixture validator before any estimator implementation.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "selectedActionId": payload["summary"]["selectedActionId"],
            "contractFixtureValidatorImplemented": payload["summary"]["contractFixtureValidatorImplemented"],
            "estimatorImplemented": payload["summary"]["estimatorImplemented"],
            "publicProductReady": payload["summary"]["publicProductReady"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="PROD-A14 Training Cost Contract Fixture Validator Or Hold Selector",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("contract fixtures", payload["summary"]["sourceContractFixtureCount"]),
            ("selected action", payload["summary"]["selectedActionId"]),
            ("validator implementation path selected", payload["summary"]["validatorImplementationPathSelected"]),
            ("immediate estimator implementation blocked", payload["summary"]["immediateEstimatorImplementationBlocked"]),
            ("contract fixture validator implemented", payload["summary"]["contractFixtureValidatorImplemented"]),
            ("estimator implemented", payload["summary"]["estimatorImplemented"]),
            ("public product ready", payload["summary"]["publicProductReady"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Decision Criteria",
                [
                    f"- `{item['criterionId']}`: `{item['status']}` - {item['detail']}"
                    for item in payload["decisionCriteria"]
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
    result_path = out_dir / f"prod_a14_training_cost_contract_fixture_validator_or_hold_selector_{STAMP}.json"
    report_path = report_dir / f"prod_a14_training_cost_contract_fixture_validator_or_hold_selector_{STAMP}.md"
    evidence_path = evidence_dir / "prod_a14_training_cost_contract_fixture_validator_or_hold_selector.json"
    feed_path = command_feed_dir / f"prod_a14_training_cost_contract_fixture_validator_or_hold_selector_feed_{STAMP}.json"
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
        default=ROOT / "python/results/prod_a14_training_cost_contract_fixture_validator_or_hold_selector",
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
    print("PROD_A14_TRAINING_COST_CONTRACT_FIXTURE_VALIDATOR_OR_HOLD_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
