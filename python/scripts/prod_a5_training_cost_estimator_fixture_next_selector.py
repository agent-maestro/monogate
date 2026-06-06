#!/usr/bin/env python3
"""PROD-A5 training cost estimator fixture/test next-action selector."""

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

from scripts import prod_a4_training_cost_estimator_schema_validator_contract as prod_a4  # noqa: E402

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.training_cost_estimator_fixture_next_selector.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "PROD_A5_TRAINING_COST_ESTIMATOR_FIXTURE_NEXT_SELECTOR_PASS"

TRUE_CLAIM_FLAGS = {
    "prod_a4_consumed",
    "private_next_action_selected",
    "static_fixture_packet_selected",
    "executable_validator_tests_parked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "prod_a4_consumed": True,
    "private_next_action_selected": True,
    "static_fixture_packet_selected": True,
    "executable_validator_tests_parked": True,
    "d109_hold_respected": True,
    "fixture_packet_created": False,
    "accepted_fixture_created": False,
    "rejection_fixture_created": False,
    "schema_validator_implemented": False,
    "schema_validator_executed": False,
    "executable_validator_tests_created": False,
    "example_packet_created": False,
    "estimator_implemented": False,
    "estimator_executed": False,
    "model_training_executed": False,
    "runtime_benchmark_executed": False,
    "public_product_ready": False,
    "training_savings_claim": False,
    "estimator_accuracy_claim": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "semantic_preservation_claim": False,
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
    "PROD-A5 selects the next private fixture/test artifact; it does not create fixtures or executable validator tests.",
    "PROD-A5 selects a static fixture packet before executable validator tests so accepted and rejection shapes are reviewable first.",
    "PROD-A5 does not implement or execute a schema validator or estimator, create examples, run model training, run benchmarks, or claim training savings, estimator accuracy, runtime performance, public readiness, compiler correctness, semantic preservation, hardware readiness, silicon readiness, reviewer approval, or broad EML advantage.",
    "PROD-A5 respects the D109 hold and does not start D110 or consume a reviewer response.",
]


def next_action_options() -> list[dict[str, Any]]:
    return [
        {
            "optionId": "static_fixture_packet",
            "status": "selected",
            "nextArtifact": "PROD-A6 training cost estimator validator contract fixture packet",
            "reason": "Static accepted/rejection fixtures make the A4 contract reviewable before executable validator tests.",
            "requires": ["PROD-A4 required fields", "PROD-A4 validation obligations", "PROD-A4 rejection fixtures"],
            "blockedClaims": ["validator implemented", "validator executed", "estimator accuracy", "training savings"],
        },
        {
            "optionId": "executable_validator_tests",
            "status": "parked_until_static_fixtures_exist",
            "nextArtifact": "Future executable validator tests after static fixtures",
            "reason": "Executable tests should be derived from reviewed fixtures rather than invented directly.",
            "requires": ["PROD-A6 static accepted/rejection fixture packet"],
            "blockedClaims": ["validator correctness", "production readiness"],
        },
        {
            "optionId": "implementation_hold_gate",
            "status": "blocked_until_fixtures_and_tests_reviewed",
            "nextArtifact": "Future implementation hold gate after fixture/test review",
            "reason": "Implementation remains premature before fixtures and executable tests are reviewed.",
            "requires": ["fixture packet", "executable validator tests", "explicit implementation approval"],
            "blockedClaims": ["implementation approved", "public product readiness"],
        },
    ]


def selector_criteria() -> list[dict[str, str]]:
    return [
        {
            "criterionId": "make_contract_reviewable",
            "result": "static_fixture_packet",
            "note": "Fixtures provide concrete accepted/rejected shapes for human review.",
        },
        {
            "criterionId": "avoid_executable_claims",
            "result": "static_fixture_packet",
            "note": "Static fixtures avoid implying validator implementation or correctness.",
        },
        {
            "criterionId": "preserve_rejection_coverage",
            "result": "static_fixture_packet",
            "note": "The A4 rejection fixtures should be materialized before code.",
        },
        {
            "criterionId": "keep_estimator_unimplemented",
            "result": "static_fixture_packet",
            "note": "The selected path does not implement estimator code or execute training workloads.",
        },
    ]


def build_payload() -> dict[str, Any]:
    contract = prod_a4.build_payload()
    prod_a4.validate_payload(contract)
    options = next_action_options()
    criteria = selector_criteria()
    selected = next(item for item in options if item["status"] == "selected")
    summary = {
        "sourceArtifact": contract["artifactId"],
        "prodA4NextRecommendedArtifact": contract["summary"]["nextRecommendedArtifact"],
        "selectedOptionId": selected["optionId"],
        "selectedNextArtifact": selected["nextArtifact"],
        "optionCount": len(options),
        "selectorCriterionCount": len(criteria),
        "staticFixturePacketSelected": True,
        "executableValidatorTestsParked": True,
        "fixturePacketCreated": False,
        "schemaValidatorImplemented": False,
        "schemaValidatorExecuted": False,
        "executableValidatorTestsCreated": False,
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
        "artifactId": "prod-a5-training-cost-estimator-fixture-next-selector",
        "artifactType": "training_cost_estimator_fixture_next_selector",
        "status": STATUS,
        "date": DATE,
        "sourceArtifact": contract["artifactId"],
        "nextActionOptions": options,
        "selectorCriteria": criteria,
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
    if payload["sourceArtifact"] != "prod-a4-training-cost-estimator-schema-validator-contract":
        raise ValueError("PROD-A5 must consume PROD-A4")
    if summary["prodA4NextRecommendedArtifact"] != (
        "PROD-A5 training cost estimator validator contract fixture packet or executable validator test selector"
    ):
        raise ValueError("PROD-A4 next artifact drift")
    if summary["selectedOptionId"] != "static_fixture_packet":
        raise ValueError("static fixture packet must be selected")
    if summary["selectedNextArtifact"] != "PROD-A6 training cost estimator validator contract fixture packet":
        raise ValueError("unexpected selected next artifact")
    if summary["optionCount"] != 3 or summary["selectorCriterionCount"] != 4:
        raise ValueError("selector shape drift")
    for key in ["staticFixturePacketSelected", "executableValidatorTestsParked", "d109HoldRespected", "claimFlagsBounded"]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "fixturePacketCreated",
        "schemaValidatorImplemented",
        "schemaValidatorExecuted",
        "executableValidatorTestsCreated",
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
        "artifactType": "training_cost_estimator_fixture_next_selector",
        "validationStatus": "pass",
        "semanticStrength": "private_fixture_next_selector_static_fixtures_selected_no_validator_implementation",
        "source": f"python/results/prod_a5_training_cost_estimator_fixture_next_selector/prod_a5_training_cost_estimator_fixture_next_selector_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "prod_a5_training_cost_estimator_fixture_next_selector_feed",
        "date": DATE,
        "status": payload["status"],
        "sourceArtifact": payload["sourceArtifact"],
        "selectedOptionId": payload["summary"]["selectedOptionId"],
        "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
        "fixturePacketCreated": payload["summary"]["fixturePacketCreated"],
        "schemaValidatorImplemented": payload["summary"]["schemaValidatorImplemented"],
        "trainingSavingsClaim": payload["summary"]["trainingSavingsClaim"],
        "nextAction": "Create PROD-A6 training cost estimator validator contract fixture packet.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# PROD-A5 Training Cost Estimator Fixture/Test Next Selector",
        "",
        f"Status: `{payload['status']}`",
        "",
        "PROD-A5 selects static validator-contract fixtures as the next private artifact.",
        "It does not create fixtures or implement validator tests.",
        "",
        "## Options",
        "",
        "| Option | Status | Next artifact |",
        "|---|---|---|",
    ]
    for item in payload["nextActionOptions"]:
        lines.append(f"| `{item['optionId']}` | `{item['status']}` | {item['nextArtifact']} |")
    lines.extend(["", "## Criteria", ""])
    lines.extend(f"- `{item['criterionId']}` -> `{item['result']}`: {item['note']}" for item in payload["selectorCriteria"])
    lines.extend(["", "## Non-Claims", ""])
    lines.extend(f"- {item}" for item in payload["nonClaims"])
    return "\n".join(lines) + "\n"


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"prod_a5_training_cost_estimator_fixture_next_selector_{STAMP}.json"
    report_path = report_dir / f"prod_a5_training_cost_estimator_fixture_next_selector_{STAMP}.md"
    evidence_path = evidence_dir / "prod_a5_training_cost_estimator_fixture_next_selector.json"
    feed_path = command_feed_dir / f"prod_a5_training_cost_estimator_fixture_next_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/prod_a5_training_cost_estimator_fixture_next_selector")
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
    print("PROD_A5_TRAINING_COST_ESTIMATOR_FIXTURE_NEXT_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
