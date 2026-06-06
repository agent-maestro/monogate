#!/usr/bin/env python3
"""PROD-A3 training cost estimator next-action selector."""

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

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.training_cost_estimator_next_selector.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "PROD_A3_TRAINING_COST_ESTIMATOR_NEXT_SELECTOR_PASS"

TRUE_CLAIM_FLAGS = {
    "prod_a2_consumed",
    "private_next_action_selected",
    "schema_validator_path_selected",
    "implementation_path_blocked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "prod_a2_consumed": True,
    "private_next_action_selected": True,
    "schema_validator_path_selected": True,
    "implementation_path_blocked": True,
    "d109_hold_respected": True,
    "schema_validator_implemented": False,
    "example_packet_created": False,
    "implementation_hold_gate_created": False,
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
    "ip_license_terms_finalized": False,
    "electronics_repo_touched": False,
    "laptop_owned_repo_touched": False,
    "d110_started": False,
    "reviewer_response_consumed": False,
    "reviewer_approval_recorded": False,
    "broad_eml_advantage_claim": False,
}

NON_CLAIMS = [
    "PROD-A3 selects the next private training cost estimator artifact; it does not implement the selected artifact.",
    "PROD-A3 selects a schema validator path because it hardens the PROD-A2 spec before examples or implementation.",
    "PROD-A3 does not implement or execute an estimator, create examples, run model training, run benchmarks, or claim training savings, estimator accuracy, runtime performance, public readiness, compiler correctness, semantic preservation, hardware readiness, silicon readiness, reviewer approval, or broad EML advantage.",
    "PROD-A3 respects the D109 hold and does not start D110 or consume a reviewer response.",
]


def next_action_options() -> list[dict[str, Any]]:
    return [
        {
            "optionId": "schema_validator",
            "status": "selected",
            "nextArtifact": "PROD-A4 training cost estimator schema validator contract",
            "reason": "Validate the required shape and caveat/blocked-claim carriage before examples or implementation.",
            "requires": ["PROD-A2 supported inputs", "PROD-A2 output schema fields", "PROD-A2 blocked claims"],
            "blockedClaims": ["estimator implementation", "estimator accuracy", "training savings"],
        },
        {
            "optionId": "example_packet",
            "status": "parked_until_schema_contract_exists",
            "nextArtifact": "Future PROD-A5 example packet after schema validator contract",
            "reason": "Examples should use a validator contract first so caveats and blocked claims cannot be omitted.",
            "requires": ["PROD-A4 schema validator contract"],
            "blockedClaims": ["example proves savings", "example proves runtime performance"],
        },
        {
            "optionId": "implementation_hold_gate",
            "status": "blocked_until_schema_and_examples_reviewed",
            "nextArtifact": "Future implementation hold gate after schema/example review",
            "reason": "Implementation discussion is premature before schema and example boundaries are reviewed.",
            "requires": ["schema validator contract", "example packet", "explicit implementation approval"],
            "blockedClaims": ["implementation approved", "public product readiness"],
        },
    ]


def selector_criteria() -> list[dict[str, str]]:
    return [
        {
            "criterionId": "minimize_claim_surface",
            "result": "schema_validator",
            "note": "A schema validator contract narrows claims rather than expanding product behavior.",
        },
        {
            "criterionId": "preserve_caveat_carriage",
            "result": "schema_validator",
            "note": "Every future estimate/example should carry calibration caveats and blocked claims.",
        },
        {
            "criterionId": "avoid_estimator_implementation",
            "result": "schema_validator",
            "note": "The selected path does not implement estimator code or execute training workloads.",
        },
        {
            "criterionId": "support_reviewer_readability",
            "result": "schema_validator",
            "note": "A validator contract gives reviewers a stable checklist before examples.",
        },
    ]


def build_payload() -> dict[str, Any]:
    spec = prod_a2.build_payload()
    prod_a2.validate_payload(spec)
    options = next_action_options()
    criteria = selector_criteria()
    selected = next(item for item in options if item["status"] == "selected")
    summary = {
        "sourceArtifact": spec["artifactId"],
        "prodA2NextRecommendedArtifact": spec["summary"]["nextRecommendedArtifact"],
        "selectedOptionId": selected["optionId"],
        "selectedNextArtifact": selected["nextArtifact"],
        "optionCount": len(options),
        "selectorCriterionCount": len(criteria),
        "schemaValidatorPathSelected": True,
        "examplePacketCreated": False,
        "implementationHoldGateCreated": False,
        "schemaValidatorImplemented": False,
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
        "artifactId": "prod-a3-training-cost-estimator-next-selector",
        "artifactType": "training_cost_estimator_next_selector",
        "status": STATUS,
        "date": DATE,
        "sourceArtifact": spec["artifactId"],
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
    if payload["sourceArtifact"] != "prod-a2-training-cost-estimator-private-spec":
        raise ValueError("PROD-A3 must consume PROD-A2")
    if summary["prodA2NextRecommendedArtifact"] != "PROD-A3 training cost estimator schema validator or example packet selector":
        raise ValueError("PROD-A2 next artifact drift")
    if summary["selectedOptionId"] != "schema_validator":
        raise ValueError("schema validator path must be selected")
    if summary["selectedNextArtifact"] != "PROD-A4 training cost estimator schema validator contract":
        raise ValueError("unexpected selected next artifact")
    if summary["optionCount"] != 3 or summary["selectorCriterionCount"] != 4:
        raise ValueError("selector shape drift")
    for key in ["schemaValidatorPathSelected", "d109HoldRespected", "claimFlagsBounded"]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "examplePacketCreated",
        "implementationHoldGateCreated",
        "schemaValidatorImplemented",
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
        "artifactType": "training_cost_estimator_next_selector",
        "validationStatus": "pass",
        "semanticStrength": "private_next_action_selector_schema_validator_selected_no_implementation",
        "source": f"python/results/prod_a3_training_cost_estimator_next_selector/prod_a3_training_cost_estimator_next_selector_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "prod_a3_training_cost_estimator_next_selector_feed",
        "date": DATE,
        "status": payload["status"],
        "sourceArtifact": payload["sourceArtifact"],
        "selectedOptionId": payload["summary"]["selectedOptionId"],
        "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
        "schemaValidatorImplemented": payload["summary"]["schemaValidatorImplemented"],
        "estimatorImplemented": payload["summary"]["estimatorImplemented"],
        "trainingSavingsClaim": payload["summary"]["trainingSavingsClaim"],
        "nextAction": "Create PROD-A4 training cost estimator schema validator contract.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# PROD-A3 Training Cost Estimator Next Selector",
        "",
        f"Status: `{payload['status']}`",
        "",
        "PROD-A3 selects the schema validator contract as the next private artifact.",
        "It does not implement a validator or estimator.",
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
    lines.extend(["", "## Summary", ""])
    lines.extend(
        [
            f"- source artifact: `{payload['summary']['sourceArtifact']}`",
            f"- selected option: `{payload['summary']['selectedOptionId']}`",
            f"- selected next artifact: `{payload['summary']['selectedNextArtifact']}`",
            f"- schema validator implemented: `{payload['summary']['schemaValidatorImplemented']}`",
            f"- estimator implemented: `{payload['summary']['estimatorImplemented']}`",
            f"- training savings claim: `{payload['summary']['trainingSavingsClaim']}`",
        ]
    )
    lines.extend(["", "## Non-Claims", ""])
    lines.extend(f"- {item}" for item in payload["nonClaims"])
    return "\n".join(lines) + "\n"


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"prod_a3_training_cost_estimator_next_selector_{STAMP}.json"
    report_path = report_dir / f"prod_a3_training_cost_estimator_next_selector_{STAMP}.md"
    evidence_path = evidence_dir / "prod_a3_training_cost_estimator_next_selector.json"
    feed_path = command_feed_dir / f"prod_a3_training_cost_estimator_next_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/prod_a3_training_cost_estimator_next_selector")
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
    print("PROD_A3_TRAINING_COST_ESTIMATOR_NEXT_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
