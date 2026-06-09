#!/usr/bin/env python3
"""PROD-A13 private training-cost estimator input/output contract seed."""

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

from scripts import prod_a2_training_cost_estimator_private_spec as prod_a2  # noqa: E402
from scripts import prod_a12_training_cost_validator_contract_review_selector as prod_a12  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-08"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.training_cost_estimator_io_contract_seed.v0"
STATUS = "PROD_A13_TRAINING_COST_ESTIMATOR_IO_CONTRACT_SEED_PASS"
ARTIFACT_ID = "prod-a13-training-cost-estimator-io-contract-seed"
NEXT_RECOMMENDED_ARTIFACT = "PROD-A14 private training-cost estimator contract fixture validator or implementation-hold selector"

TRUE_CLAIM_FLAGS = {
    "prod_a12_consumed",
    "prod_a2_referenced",
    "estimator_io_contract_created",
    "input_contract_recorded",
    "output_contract_recorded",
    "contract_fixtures_recorded",
    "implementation_blocked",
    "public_claims_blocked",
}

CLAIM_FLAGS = {
    "prod_a12_consumed": True,
    "prod_a2_referenced": True,
    "estimator_io_contract_created": True,
    "input_contract_recorded": True,
    "output_contract_recorded": True,
    "contract_fixtures_recorded": True,
    "implementation_blocked": True,
    "public_claims_blocked": True,
    "estimator_implemented": False,
    "estimator_executed": False,
    "schema_validator_changed": False,
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
    "PROD-A13 creates a private input/output contract seed only; it does not implement or execute a training-cost estimator.",
    "PROD-A13 does not change the PROD-A11 fixture validator or validate the new contract fixtures with executable code.",
    "PROD-A13 does not train models, run benchmarks, calibrate estimates, publish docs, update public/dev surfaces, or approve public copy.",
    "PROD-A13 does not claim estimator accuracy, training savings, runtime performance, model quality, scientific correctness, SDK stability, compiler correctness, semantic preservation, hardware readiness, silicon readiness, public readiness, reviewer approval, or broad EML advantage.",
]


def load_prod_a12_result() -> dict[str, Any]:
    path = (
        ROOT
        / "python/results/prod_a12_training_cost_validator_contract_review_selector"
        / f"prod_a12_training_cost_validator_contract_review_selector_{STAMP}.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    prod_a12.validate_payload(payload)
    return payload


def input_contracts() -> list[dict[str, Any]]:
    return [
        {
            "inputId": item["inputId"],
            "requiredFields": item["requiredFields"],
            "optionalFields": item["optionalFields"],
            "contractBoundary": item["boundary"],
            "acceptedWhen": [
                "required fields are present",
                "input_summary records missing optional context",
                "no runtime, savings, accuracy, or public-readiness claim is attached",
            ],
        }
        for item in prod_a2.supported_inputs()
    ]


def output_contract() -> dict[str, Any]:
    return {
        "packetIdField": "estimate_id",
        "requiredFields": [field["field"] for field in prod_a2.output_schema_fields()],
        "requiredCaveats": [item["caveatId"] for item in prod_a2.calibration_caveats()],
        "requiredBlockedClaims": prod_a2.blocked_claims(),
        "requiredFalseClaimFlags": [
            "public_product_ready",
            "training_savings_claim",
            "estimator_accuracy_claim",
            "runtime_performance_claim",
            "broad_eml_advantage_claim",
        ],
        "costViewRule": "At least one of static_expression_cost, graph_cost_profile, or training_budget_context must be non-null.",
        "reviewRule": "reviewer_next_steps must be non-empty before implementation or public copy.",
    }


def contract_fixtures() -> list[dict[str, Any]]:
    return [
        {
            "fixtureId": "accepted_static_expression_input_output_shape",
            "expectedDisposition": "accept_contract_shape",
            "inputRef": "sympy_expression_or_expression_list",
            "outputViews": ["static_expression_cost"],
            "requiredBoundary": "static cost shape only; not runtime truth",
        },
        {
            "fixtureId": "accepted_training_budget_input_output_shape",
            "expectedDisposition": "accept_contract_shape",
            "inputRef": "training_loop_metadata",
            "outputViews": ["training_budget_context"],
            "requiredBoundary": "budget metadata only; not convergence or savings",
        },
        {
            "fixtureId": "reject_output_without_caveats",
            "expectedDisposition": "reject_contract_shape",
            "mutation": "remove calibration_caveats from output envelope",
        },
        {
            "fixtureId": "reject_output_without_blocked_claims",
            "expectedDisposition": "reject_contract_shape",
            "mutation": "remove blocked_claims from output envelope",
        },
        {
            "fixtureId": "reject_true_accuracy_or_savings_flag",
            "expectedDisposition": "reject_contract_shape",
            "mutation": "set estimator_accuracy_claim or training_savings_claim true",
        },
        {
            "fixtureId": "reject_missing_cost_view",
            "expectedDisposition": "reject_contract_shape",
            "mutation": "set all cost view fields to null",
        },
    ]


def reviewer_questions() -> list[dict[str, str]]:
    return [
        {
            "questionId": "input_contract_enough",
            "question": "Are the four PROD-A2 input variants enough for a first private estimator contract?",
        },
        {
            "questionId": "output_caveat_carriage",
            "question": "Does the output contract force caveats and blocked claims to travel with every estimate?",
        },
        {
            "questionId": "a14_path",
            "question": "Should PROD-A14 validate these contract fixtures or hold before estimator implementation?",
        },
    ]


def build_payload() -> dict[str, Any]:
    selector = load_prod_a12_result()
    inputs = input_contracts()
    output = output_contract()
    fixtures = contract_fixtures()
    questions = reviewer_questions()
    accepted = [fixture for fixture in fixtures if fixture["expectedDisposition"].startswith("accept")]
    rejected = [fixture for fixture in fixtures if fixture["expectedDisposition"].startswith("reject")]
    summary = {
        "sourceArtifact": selector["artifactId"],
        "sourceSelectedActionId": selector["summary"]["selectedActionId"],
        "inputContractCount": len(inputs),
        "outputRequiredFieldCount": len(output["requiredFields"]),
        "requiredCaveatCount": len(output["requiredCaveats"]),
        "requiredBlockedClaimCount": len(output["requiredBlockedClaims"]),
        "contractFixtureCount": len(fixtures),
        "acceptedContractFixtureCount": len(accepted),
        "rejectionContractFixtureCount": len(rejected),
        "reviewerQuestionCount": len(questions),
        "estimatorIoContractCreated": True,
        "estimatorImplemented": False,
        "estimatorExecuted": False,
        "schemaValidatorChanged": False,
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
        artifact_type="training_cost_estimator_io_contract_seed",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": selector["artifactId"],
            "inputContracts": inputs,
            "outputContract": output,
            "contractFixtures": fixtures,
            "reviewerQuestions": questions,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceArtifact"] != "prod-a12-training-cost-validator-contract-review-selector":
        raise ValueError("PROD-A13 must consume PROD-A12")
    summary = payload["summary"]
    if summary["sourceSelectedActionId"] != "private_estimator_io_contract_seed":
        raise ValueError("PROD-A12 selected action drift")
    if summary["inputContractCount"] != 4:
        raise ValueError("expected four input contracts")
    if summary["outputRequiredFieldCount"] != 8:
        raise ValueError("expected eight output fields")
    if summary["requiredCaveatCount"] != 5:
        raise ValueError("expected five caveats")
    if summary["requiredBlockedClaimCount"] != len(prod_a2.blocked_claims()):
        raise ValueError("blocked claim count drift")
    if summary["acceptedContractFixtureCount"] != 2:
        raise ValueError("expected two accepted contract fixtures")
    if summary["rejectionContractFixtureCount"] != 4:
        raise ValueError("expected four rejection contract fixtures")
    output = payload["outputContract"]
    for field in [
        "estimate_id",
        "input_summary",
        "static_expression_cost",
        "graph_cost_profile",
        "training_budget_context",
        "calibration_caveats",
        "blocked_claims",
        "reviewer_next_steps",
    ]:
        if field not in output["requiredFields"]:
            raise ValueError(f"missing output field: {field}")
    for key in [
        "estimatorIoContractCreated",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "estimatorImplemented",
        "estimatorExecuted",
        "schemaValidatorChanged",
        "runtimeBenchmarkExecuted",
        "calibrationPerformed",
        "publicProductReady",
        "trainingSavingsClaim",
        "estimatorAccuracyClaim",
        "runtimePerformanceClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
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
        semantic_strength="private_estimator_io_contract_seed_no_estimator_execution_or_public_claim",
        source=f"python/results/prod_a13_training_cost_estimator_io_contract_seed/prod_a13_training_cost_estimator_io_contract_seed_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="prod_a13_training_cost_estimator_io_contract_seed_feed",
        date=DATE,
        status=payload["status"],
        next_action="Review or validate the private estimator I/O contract fixtures before any estimator implementation.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "inputContractCount": payload["summary"]["inputContractCount"],
            "contractFixtureCount": payload["summary"]["contractFixtureCount"],
            "estimatorImplemented": payload["summary"]["estimatorImplemented"],
            "publicProductReady": payload["summary"]["publicProductReady"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="PROD-A13 Training Cost Estimator I/O Contract Seed",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("input contracts", payload["summary"]["inputContractCount"]),
            ("output required fields", payload["summary"]["outputRequiredFieldCount"]),
            ("contract fixtures", payload["summary"]["contractFixtureCount"]),
            ("estimator I/O contract created", payload["summary"]["estimatorIoContractCreated"]),
            ("estimator implemented", payload["summary"]["estimatorImplemented"]),
            ("public product ready", payload["summary"]["publicProductReady"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Input Contracts",
                [
                    f"- `{item['inputId']}`: required=`{len(item['requiredFields'])}` optional=`{len(item['optionalFields'])}`"
                    for item in payload["inputContracts"]
                ],
            ),
            (
                "Contract Fixtures",
                [
                    f"- `{fixture['fixtureId']}`: `{fixture['expectedDisposition']}`"
                    for fixture in payload["contractFixtures"]
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
    result_path = out_dir / f"prod_a13_training_cost_estimator_io_contract_seed_{STAMP}.json"
    report_path = report_dir / f"prod_a13_training_cost_estimator_io_contract_seed_{STAMP}.md"
    evidence_path = evidence_dir / "prod_a13_training_cost_estimator_io_contract_seed.json"
    feed_path = command_feed_dir / f"prod_a13_training_cost_estimator_io_contract_seed_feed_{STAMP}.json"
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
        default=ROOT / "python/results/prod_a13_training_cost_estimator_io_contract_seed",
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
    print("PROD_A13_TRAINING_COST_ESTIMATOR_IO_CONTRACT_SEED_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
