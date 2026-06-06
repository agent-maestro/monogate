#!/usr/bin/env python3
"""PROD-A6 training cost estimator validator contract fixture packet."""

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

from scripts import prod_a5_training_cost_estimator_fixture_next_selector as prod_a5  # noqa: E402

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.training_cost_estimator_fixture_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "PROD_A6_TRAINING_COST_ESTIMATOR_FIXTURE_PACKET_PASS"

TRUE_CLAIM_FLAGS = {
    "prod_a5_consumed",
    "fixture_packet_created",
    "accepted_fixtures_created",
    "rejection_fixtures_created",
    "shared_toolkit_next_selected",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "prod_a5_consumed": True,
    "fixture_packet_created": True,
    "accepted_fixtures_created": True,
    "rejection_fixtures_created": True,
    "shared_toolkit_next_selected": True,
    "d109_hold_respected": True,
    "schema_validator_implemented": False,
    "schema_validator_executed": False,
    "executable_validator_tests_created": False,
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
    "PROD-A6 creates static accepted/rejection fixture shapes only; it does not implement or execute a validator.",
    "PROD-A6 creates no estimator code, examples for public use, model training runs, runtime benchmarks, public copy, or public product surface.",
    "PROD-A6 does not claim training savings, estimator accuracy, runtime performance, public readiness, compiler correctness, semantic preservation, hardware readiness, silicon readiness, reviewer approval, or broad EML advantage.",
    "PROD-A6 respects the D109 hold and does not start D110 or consume a reviewer response.",
]

REQUIRED_CAVEATS = [
    "not_wall_clock_runtime",
    "not_training_savings",
    "hardware_context_missing",
    "model_quality_out_of_scope",
    "calibration_required",
]

REQUIRED_BLOCKED_CLAIMS = [
    "training cost savings",
    "estimator accuracy",
    "wall-clock runtime performance",
    "model quality improvement",
    "compiler correctness",
    "semantic preservation",
    "public product readiness",
    "hardware readiness",
    "broad EML advantage",
]


def accepted_fixtures() -> list[dict[str, Any]]:
    base_claim_flags = {
        "public_product_ready": False,
        "training_savings_claim": False,
        "estimator_accuracy_claim": False,
        "runtime_performance_claim": False,
        "broad_eml_advantage_claim": False,
    }
    return [
        {
            "fixtureId": "accepted_static_expression_cost_shape",
            "expectedDisposition": "accept_static_shape",
            "packet": {
                "estimate_id": "private-static-expression-cost-shape-example",
                "input_summary": {
                    "input_type": "sympy_expression_or_expression_list",
                    "missing_optional_context": ["source_file"],
                },
                "static_expression_cost": {
                    "expression_count": 1,
                    "cost_profile_status": "shape_only_no_runtime_truth",
                },
                "graph_cost_profile": None,
                "training_budget_context": None,
                "calibration_caveats": list(REQUIRED_CAVEATS),
                "blocked_claims": list(REQUIRED_BLOCKED_CLAIMS),
                "reviewer_next_steps": ["review static expression cost shape", "confirm caveat carriage"],
                "claim_flags": dict(base_claim_flags),
            },
        },
        {
            "fixtureId": "accepted_training_budget_context_shape",
            "expectedDisposition": "accept_budget_context_shape",
            "packet": {
                "estimate_id": "private-training-budget-context-example",
                "input_summary": {
                    "input_type": "training_loop_metadata",
                    "missing_optional_context": ["precision_policy", "gradient_accumulation_steps"],
                },
                "static_expression_cost": None,
                "graph_cost_profile": None,
                "training_budget_context": {
                    "epoch_count": 1,
                    "batch_size": 32,
                    "budget_context_status": "metadata_only_no_training_outcome",
                },
                "calibration_caveats": list(REQUIRED_CAVEATS),
                "blocked_claims": list(REQUIRED_BLOCKED_CLAIMS),
                "reviewer_next_steps": ["review budget context shape", "confirm no savings claim"],
                "claim_flags": dict(base_claim_flags),
            },
        },
    ]


def rejection_fixtures() -> list[dict[str, Any]]:
    accepted = accepted_fixtures()[0]["packet"]
    return [
        {
            "fixtureId": "missing_blocked_claims",
            "expectedDisposition": "reject",
            "mutation": "remove blocked_claims",
            "packet": {key: value for key, value in accepted.items() if key != "blocked_claims"},
        },
        {
            "fixtureId": "missing_calibration_caveats",
            "expectedDisposition": "reject",
            "mutation": "remove calibration_caveats",
            "packet": {key: value for key, value in accepted.items() if key != "calibration_caveats"},
        },
        {
            "fixtureId": "all_cost_views_null",
            "expectedDisposition": "reject",
            "mutation": "set all cost views to null",
            "packet": {
                **accepted,
                "static_expression_cost": None,
                "graph_cost_profile": None,
                "training_budget_context": None,
            },
        },
        {
            "fixtureId": "training_savings_true",
            "expectedDisposition": "reject",
            "mutation": "set training_savings_claim true",
            "packet": {
                **accepted,
                "claim_flags": {**accepted["claim_flags"], "training_savings_claim": True},
            },
        },
        {
            "fixtureId": "public_product_ready_true",
            "expectedDisposition": "reject",
            "mutation": "set public_product_ready true",
            "packet": {
                **accepted,
                "claim_flags": {**accepted["claim_flags"], "public_product_ready": True},
            },
        },
    ]


def build_payload() -> dict[str, Any]:
    selector = prod_a5.build_payload()
    prod_a5.validate_payload(selector)
    accepted = accepted_fixtures()
    rejected = rejection_fixtures()
    summary = {
        "sourceArtifact": selector["artifactId"],
        "prodA5SelectedOptionId": selector["summary"]["selectedOptionId"],
        "prodA5SelectedNextArtifact": selector["summary"]["selectedNextArtifact"],
        "acceptedFixtureCount": len(accepted),
        "rejectionFixtureCount": len(rejected),
        "requiredCaveatCount": len(REQUIRED_CAVEATS),
        "requiredBlockedClaimCount": len(REQUIRED_BLOCKED_CLAIMS),
        "nextRecommendedArtifact": "EA-A1 shared evidence artifact toolkit seed",
        "fixturePacketCreated": True,
        "acceptedFixturesCreated": True,
        "rejectionFixturesCreated": True,
        "sharedToolkitNextSelected": True,
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
        "artifactId": "prod-a6-training-cost-estimator-fixture-packet",
        "artifactType": "training_cost_estimator_fixture_packet",
        "status": STATUS,
        "date": DATE,
        "sourceArtifact": selector["artifactId"],
        "requiredCaveats": list(REQUIRED_CAVEATS),
        "requiredBlockedClaims": list(REQUIRED_BLOCKED_CLAIMS),
        "acceptedFixtures": accepted,
        "rejectionFixtures": rejected,
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
    if payload["sourceArtifact"] != "prod-a5-training-cost-estimator-fixture-next-selector":
        raise ValueError("PROD-A6 must consume PROD-A5")
    if summary["prodA5SelectedOptionId"] != "static_fixture_packet":
        raise ValueError("PROD-A5 selected option drift")
    if summary["prodA5SelectedNextArtifact"] != "PROD-A6 training cost estimator validator contract fixture packet":
        raise ValueError("PROD-A5 selected artifact drift")
    if summary["acceptedFixtureCount"] != 2:
        raise ValueError("accepted fixture drift")
    if summary["rejectionFixtureCount"] != 5:
        raise ValueError("rejection fixture drift")
    for fixture in payload["acceptedFixtures"]:
        packet = fixture["packet"]
        if not any(packet[field] is not None for field in ["static_expression_cost", "graph_cost_profile", "training_budget_context"]):
            raise ValueError(f"{fixture['fixtureId']} must have at least one cost view")
        if packet["calibration_caveats"] != REQUIRED_CAVEATS:
            raise ValueError(f"{fixture['fixtureId']} missing caveats")
        if packet["blocked_claims"] != REQUIRED_BLOCKED_CLAIMS:
            raise ValueError(f"{fixture['fixtureId']} missing blocked claims")
        if any(packet["claim_flags"].values()):
            raise ValueError(f"{fixture['fixtureId']} claim flags must remain false")
    if {fixture["fixtureId"] for fixture in payload["rejectionFixtures"]} != {
        "missing_blocked_claims",
        "missing_calibration_caveats",
        "all_cost_views_null",
        "training_savings_true",
        "public_product_ready_true",
    }:
        raise ValueError("rejection fixture id drift")
    for key in [
        "fixturePacketCreated",
        "acceptedFixturesCreated",
        "rejectionFixturesCreated",
        "sharedToolkitNextSelected",
        "d109HoldRespected",
        "claimFlagsBounded",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
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
        "artifactType": "training_cost_estimator_fixture_packet",
        "validationStatus": "pass",
        "semanticStrength": "private_static_fixtures_no_validator_implementation",
        "source": f"python/results/prod_a6_training_cost_estimator_fixture_packet/prod_a6_training_cost_estimator_fixture_packet_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "prod_a6_training_cost_estimator_fixture_packet_feed",
        "date": DATE,
        "status": payload["status"],
        "sourceArtifact": payload["sourceArtifact"],
        "acceptedFixtureCount": payload["summary"]["acceptedFixtureCount"],
        "rejectionFixtureCount": payload["summary"]["rejectionFixtureCount"],
        "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        "schemaValidatorImplemented": payload["summary"]["schemaValidatorImplemented"],
        "estimatorImplemented": payload["summary"]["estimatorImplemented"],
        "trainingSavingsClaim": payload["summary"]["trainingSavingsClaim"],
        "nextAction": "Create EA-A1 shared evidence artifact toolkit seed.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# PROD-A6 Training Cost Estimator Fixture Packet",
        "",
        f"Status: `{payload['status']}`",
        "",
        "PROD-A6 creates static accepted/rejection fixtures for the training cost estimator validator contract.",
        "It does not implement or execute a validator.",
        "",
        "## Accepted Fixtures",
        "",
        "| Fixture | Expected disposition |",
        "|---|---|",
    ]
    for fixture in payload["acceptedFixtures"]:
        lines.append(f"| `{fixture['fixtureId']}` | `{fixture['expectedDisposition']}` |")
    lines.extend(["", "## Rejection Fixtures", "", "| Fixture | Mutation |", "|---|---|"])
    for fixture in payload["rejectionFixtures"]:
        lines.append(f"| `{fixture['fixtureId']}` | {fixture['mutation']} |")
    lines.extend(["", "## Non-Claims", ""])
    lines.extend(f"- {item}" for item in payload["nonClaims"])
    return "\n".join(lines) + "\n"


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"prod_a6_training_cost_estimator_fixture_packet_{STAMP}.json"
    report_path = report_dir / f"prod_a6_training_cost_estimator_fixture_packet_{STAMP}.md"
    evidence_path = evidence_dir / "prod_a6_training_cost_estimator_fixture_packet.json"
    feed_path = command_feed_dir / f"prod_a6_training_cost_estimator_fixture_packet_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/prod_a6_training_cost_estimator_fixture_packet")
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
    print("PROD_A6_TRAINING_COST_ESTIMATOR_FIXTURE_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
