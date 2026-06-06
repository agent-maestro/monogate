#!/usr/bin/env python3
"""PROD-A4 training cost estimator schema validator contract."""

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

from scripts import prod_a3_training_cost_estimator_next_selector as prod_a3  # noqa: E402

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.training_cost_estimator_schema_validator_contract.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "PROD_A4_TRAINING_COST_ESTIMATOR_SCHEMA_VALIDATOR_CONTRACT_PASS"

TRUE_CLAIM_FLAGS = {
    "prod_a3_consumed",
    "schema_validator_contract_created",
    "validation_obligations_recorded",
    "rejection_fixtures_recorded",
    "implementation_blocked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "prod_a3_consumed": True,
    "schema_validator_contract_created": True,
    "validation_obligations_recorded": True,
    "rejection_fixtures_recorded": True,
    "implementation_blocked": True,
    "d109_hold_respected": True,
    "schema_validator_implemented": False,
    "schema_validator_executed": False,
    "example_packet_created": False,
    "estimator_implemented": False,
    "estimator_executed": False,
    "model_training_executed": False,
    "runtime_benchmark_executed": False,
    "public_product_ready": False,
    "public_launch_copy_approved": False,
    "training_savings_claim": False,
    "estimator_accuracy_claim": False,
    "runtime_performance_claim": False,
    "model_quality_claim": False,
    "scientific_correctness_claim": False,
    "compiler_correctness_claim": False,
    "semantic_preservation_claim": False,
    "sdk_stability_claim": False,
    "hardware_readiness_claim": False,
    "silicon_readiness_claim": False,
    "electronics_repo_touched": False,
    "laptop_owned_repo_touched": False,
    "d110_started": False,
    "reviewer_response_consumed": False,
    "reviewer_approval_recorded": False,
    "broad_eml_advantage_claim": False,
}

NON_CLAIMS = [
    "PROD-A4 is a private schema validator contract; it does not implement or execute a validator.",
    "PROD-A4 records validation obligations and rejection fixtures for future training-cost estimate packets.",
    "PROD-A4 does not implement or execute an estimator, create examples, run model training, run benchmarks, or claim training savings, estimator accuracy, runtime performance, public readiness, compiler correctness, semantic preservation, hardware readiness, silicon readiness, reviewer approval, or broad EML advantage.",
    "PROD-A4 respects the D109 hold and does not start D110 or consume a reviewer response.",
]


def required_packet_fields() -> list[dict[str, Any]]:
    return [
        {"field": "estimate_id", "type": "string", "required": True},
        {"field": "input_summary", "type": "object", "required": True},
        {"field": "static_expression_cost", "type": "object|null", "required": True},
        {"field": "graph_cost_profile", "type": "object|null", "required": True},
        {"field": "training_budget_context", "type": "object|null", "required": True},
        {"field": "calibration_caveats", "type": "array[string]", "required": True},
        {"field": "blocked_claims", "type": "array[string]", "required": True},
        {"field": "reviewer_next_steps", "type": "array[string]", "required": True},
    ]


def validation_obligations() -> list[dict[str, Any]]:
    return [
        {
            "obligationId": "required_fields_present",
            "severity": "reject_if_missing",
            "description": "All eight PROD-A2 output fields must be present even when nullable fields are null.",
        },
        {
            "obligationId": "at_least_one_cost_view_present",
            "severity": "reject_if_absent",
            "description": "At least one of static_expression_cost, graph_cost_profile, or training_budget_context must be non-null.",
        },
        {
            "obligationId": "calibration_caveats_required",
            "severity": "reject_if_missing",
            "description": "Packet must include not-wall-clock, not-savings, hardware-context, model-quality, and calibration-required caveats.",
        },
        {
            "obligationId": "blocked_claims_required",
            "severity": "reject_if_missing",
            "description": "Packet must carry blocked claims for savings, accuracy, runtime, model quality, compiler correctness, public readiness, hardware readiness, and broad EML advantage.",
        },
        {
            "obligationId": "reviewer_next_steps_required",
            "severity": "reject_if_empty",
            "description": "Packet must provide private reviewer next steps before implementation or public copy.",
        },
        {
            "obligationId": "no_public_or_performance_flags_true",
            "severity": "reject_if_true",
            "description": "Packet must not set public readiness, training savings, estimator accuracy, runtime performance, or broad EML advantage flags true.",
        },
    ]


def rejection_fixtures() -> list[dict[str, str]]:
    return [
        {
            "fixtureId": "missing_blocked_claims",
            "reason": "A packet without blocked_claims can be mistaken for public product copy.",
        },
        {
            "fixtureId": "missing_calibration_caveats",
            "reason": "A packet without calibration caveats can be mistaken for measured runtime truth.",
        },
        {
            "fixtureId": "all_cost_views_null",
            "reason": "A packet with no cost view has no estimate surface to review.",
        },
        {
            "fixtureId": "training_savings_true",
            "reason": "A savings claim is explicitly blocked by PROD-A2.",
        },
        {
            "fixtureId": "public_product_ready_true",
            "reason": "Public readiness requires separate review and approval.",
        },
    ]


def next_reviewer_questions() -> list[dict[str, str]]:
    return [
        {
            "questionId": "validator_contract_enough",
            "question": "Are these obligations sufficient before creating example packets?",
        },
        {
            "questionId": "fixture_count_enough",
            "question": "Do the rejection fixtures cover the highest-risk missing caveat and false-claim paths?",
        },
        {
            "questionId": "a5_path",
            "question": "Should PROD-A5 create example packets from this contract, or first create executable validator tests?",
        },
    ]


def build_payload() -> dict[str, Any]:
    selector = prod_a3.build_payload()
    prod_a3.validate_payload(selector)
    fields = required_packet_fields()
    obligations = validation_obligations()
    fixtures = rejection_fixtures()
    questions = next_reviewer_questions()
    summary = {
        "sourceArtifact": selector["artifactId"],
        "prodA3SelectedOptionId": selector["summary"]["selectedOptionId"],
        "prodA3SelectedNextArtifact": selector["summary"]["selectedNextArtifact"],
        "requiredFieldCount": len(fields),
        "validationObligationCount": len(obligations),
        "rejectionFixtureCount": len(fixtures),
        "reviewerQuestionCount": len(questions),
        "nextRecommendedArtifact": "PROD-A5 training cost estimator validator contract fixture packet or executable validator test selector",
        "schemaValidatorContractCreated": True,
        "schemaValidatorImplemented": False,
        "schemaValidatorExecuted": False,
        "examplePacketCreated": False,
        "estimatorImplemented": False,
        "estimatorExecuted": False,
        "modelTrainingExecuted": False,
        "runtimeBenchmarkExecuted": False,
        "d109HoldRespected": True,
        "d110Started": False,
        "reviewerResponseConsumed": False,
        "publicProductReady": False,
        "trainingSavingsClaim": False,
        "estimatorAccuracyClaim": False,
        "runtimePerformanceClaim": False,
        "compilerCorrectnessClaim": False,
        "semanticPreservationClaim": False,
        "hardwareReadinessClaim": False,
        "siliconReadinessClaim": False,
        "broadEmlAdvantageClaim": False,
        "claimFlagsBounded": all(CLAIM_FLAGS[key] is True for key in TRUE_CLAIM_FLAGS)
        and all(value is False for key, value in CLAIM_FLAGS.items() if key not in TRUE_CLAIM_FLAGS),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "artifactId": "prod-a4-training-cost-estimator-schema-validator-contract",
        "artifactType": "training_cost_estimator_schema_validator_contract",
        "status": STATUS,
        "date": DATE,
        "sourceArtifact": selector["artifactId"],
        "requiredPacketFields": fields,
        "validationObligations": obligations,
        "rejectionFixtures": fixtures,
        "nextReviewerQuestions": questions,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    summary = payload["summary"]
    if payload["sourceArtifact"] != "prod-a3-training-cost-estimator-next-selector":
        raise ValueError("PROD-A4 must consume PROD-A3")
    if summary["prodA3SelectedOptionId"] != "schema_validator":
        raise ValueError("PROD-A3 selected option drift")
    if summary["prodA3SelectedNextArtifact"] != "PROD-A4 training cost estimator schema validator contract":
        raise ValueError("PROD-A3 selected artifact drift")
    if summary["requiredFieldCount"] != 8:
        raise ValueError("required field drift")
    if summary["validationObligationCount"] != 6:
        raise ValueError("validation obligation drift")
    if summary["rejectionFixtureCount"] != 5:
        raise ValueError("rejection fixture drift")
    if summary["reviewerQuestionCount"] != 3:
        raise ValueError("reviewer question drift")
    for key in ["schemaValidatorContractCreated", "d109HoldRespected", "claimFlagsBounded"]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "schemaValidatorImplemented",
        "schemaValidatorExecuted",
        "examplePacketCreated",
        "estimatorImplemented",
        "estimatorExecuted",
        "modelTrainingExecuted",
        "runtimeBenchmarkExecuted",
        "d110Started",
        "reviewerResponseConsumed",
        "publicProductReady",
        "trainingSavingsClaim",
        "estimatorAccuracyClaim",
        "runtimePerformanceClaim",
        "compilerCorrectnessClaim",
        "semanticPreservationClaim",
        "hardwareReadinessClaim",
        "siliconReadinessClaim",
        "broadEmlAdvantageClaim",
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
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "training_cost_estimator_schema_validator_contract",
        "validationStatus": "pass",
        "semanticStrength": "private_schema_validator_contract_no_validator_implementation",
        "source": f"python/results/prod_a4_training_cost_estimator_schema_validator_contract/prod_a4_training_cost_estimator_schema_validator_contract_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "prod_a4_training_cost_estimator_schema_validator_contract_feed",
        "date": DATE,
        "status": payload["status"],
        "sourceArtifact": payload["sourceArtifact"],
        "requiredFieldCount": payload["summary"]["requiredFieldCount"],
        "validationObligationCount": payload["summary"]["validationObligationCount"],
        "rejectionFixtureCount": payload["summary"]["rejectionFixtureCount"],
        "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        "schemaValidatorImplemented": payload["summary"]["schemaValidatorImplemented"],
        "estimatorImplemented": payload["summary"]["estimatorImplemented"],
        "trainingSavingsClaim": payload["summary"]["trainingSavingsClaim"],
        "nextAction": "Create PROD-A5 fixture packet or executable validator test selector.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# PROD-A4 Training Cost Estimator Schema Validator Contract",
        "",
        f"Status: `{payload['status']}`",
        "",
        "PROD-A4 defines private validation obligations for future training-cost estimate packets.",
        "It does not implement or execute a validator.",
        "",
        "## Required Fields",
        "",
        "| Field | Type | Required |",
        "|---|---|---|",
    ]
    for field in payload["requiredPacketFields"]:
        lines.append(f"| `{field['field']}` | `{field['type']}` | `{field['required']}` |")
    lines.extend(["", "## Validation Obligations", "", "| Obligation | Severity | Description |", "|---|---|---|"])
    for item in payload["validationObligations"]:
        lines.append(f"| `{item['obligationId']}` | `{item['severity']}` | {item['description']} |")
    lines.extend(["", "## Rejection Fixtures", ""])
    lines.extend(f"- `{item['fixtureId']}`: {item['reason']}" for item in payload["rejectionFixtures"])
    lines.extend(["", "## Non-Claims", ""])
    lines.extend(f"- {item}" for item in payload["nonClaims"])
    return "\n".join(lines) + "\n"


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"prod_a4_training_cost_estimator_schema_validator_contract_{STAMP}.json"
    report_path = report_dir / f"prod_a4_training_cost_estimator_schema_validator_contract_{STAMP}.md"
    evidence_path = evidence_dir / "prod_a4_training_cost_estimator_schema_validator_contract.json"
    feed_path = command_feed_dir / f"prod_a4_training_cost_estimator_schema_validator_contract_feed_{STAMP}.json"
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
        "--out-dir", type=Path, default=ROOT / "python/results/prod_a4_training_cost_estimator_schema_validator_contract"
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
    print("PROD_A4_TRAINING_COST_ESTIMATOR_SCHEMA_VALIDATOR_CONTRACT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
