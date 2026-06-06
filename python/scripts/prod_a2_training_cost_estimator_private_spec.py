#!/usr/bin/env python3
"""PROD-A2 training cost estimator private spec."""

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

from scripts import prod_a1_private_product_evidence_surface_seed as prod_a1  # noqa: E402

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.training_cost_estimator_private_spec.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "PROD_A2_TRAINING_COST_ESTIMATOR_PRIVATE_SPEC_PASS"

TRUE_CLAIM_FLAGS = {
    "private_training_cost_spec_created",
    "prod_a1_consumed",
    "supported_inputs_recorded",
    "output_schema_recorded",
    "calibration_caveats_recorded",
    "blocked_claims_recorded",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "private_training_cost_spec_created": True,
    "prod_a1_consumed": True,
    "supported_inputs_recorded": True,
    "output_schema_recorded": True,
    "calibration_caveats_recorded": True,
    "blocked_claims_recorded": True,
    "d109_hold_respected": True,
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
    "PROD-A2 is a private specification for a training cost estimator; it does not implement or execute an estimator.",
    "PROD-A2 defines supported inputs, output fields, calibration caveats, example boundaries, and blocked claims only.",
    "PROD-A2 does not claim training savings, estimator accuracy, runtime performance, model-quality improvement, compiler correctness, semantic preservation, public product readiness, hardware readiness, silicon readiness, reviewer approval, or broad EML advantage.",
    "PROD-A2 respects the D109 hold and does not start D110 or consume a reviewer response.",
]


def supported_inputs() -> list[dict[str, Any]]:
    return [
        {
            "inputId": "sympy_expression_or_expression_list",
            "status": "supported_for_static_cost_shape_spec",
            "requiredFields": ["expression", "variable_names"],
            "optionalFields": ["expression_label", "batch_role", "source_file"],
            "boundary": "Static expression cost shape only; no runtime measurement or training outcome prediction.",
        },
        {
            "inputId": "torch_fx_graph_summary",
            "status": "supported_for_private_profiler_spec",
            "requiredFields": ["node_kinds", "layer_labels"],
            "optionalFields": ["parameter_counts", "activation_shapes", "dtype", "device_label"],
            "boundary": "Profiler-shape input only; no guarantee that traced graph captures all runtime work.",
        },
        {
            "inputId": "training_loop_metadata",
            "status": "supported_for_budget_context_spec",
            "requiredFields": ["epoch_count", "batch_count_or_dataset_size", "batch_size"],
            "optionalFields": ["optimizer_name", "loss_name", "precision_policy", "gradient_accumulation_steps"],
            "boundary": "Budget-context metadata only; no claim that training dynamics, convergence, or data pipeline cost are fully modeled.",
        },
        {
            "inputId": "manual_operation_count_packet",
            "status": "supported_for_reviewer_supplied_estimate_spec",
            "requiredFields": ["operation_rows", "source_note"],
            "optionalFields": ["confidence_label", "calibration_reference"],
            "boundary": "Reviewer-supplied rows must remain labeled as supplied estimates, not measured truth.",
        },
    ]


def output_schema_fields() -> list[dict[str, Any]]:
    return [
        {
            "field": "estimate_id",
            "type": "string",
            "meaning": "Stable identifier for the private estimate packet.",
        },
        {
            "field": "input_summary",
            "type": "object",
            "meaning": "Compact description of accepted inputs and missing optional context.",
        },
        {
            "field": "static_expression_cost",
            "type": "object|null",
            "meaning": "Expression-level cost profile when symbolic expressions are supplied.",
        },
        {
            "field": "graph_cost_profile",
            "type": "object|null",
            "meaning": "Layer/node-level profile when graph-summary input is supplied.",
        },
        {
            "field": "training_budget_context",
            "type": "object|null",
            "meaning": "Epoch/batch/parameter context used to scale a private advisory estimate.",
        },
        {
            "field": "calibration_caveats",
            "type": "array[string]",
            "meaning": "Required caveats attached to the estimate.",
        },
        {
            "field": "blocked_claims",
            "type": "array[string]",
            "meaning": "Claims that the estimate must not imply.",
        },
        {
            "field": "reviewer_next_steps",
            "type": "array[string]",
            "meaning": "Private reviewer actions before implementation or public copy.",
        },
    ]


def calibration_caveats() -> list[dict[str, str]]:
    return [
        {
            "caveatId": "not_wall_clock_runtime",
            "text": "The estimate is not a wall-clock runtime benchmark.",
        },
        {
            "caveatId": "not_training_savings",
            "text": "The estimate does not claim lower cost, lower spend, or faster training.",
        },
        {
            "caveatId": "hardware_context_missing",
            "text": "Hardware, kernel fusion, memory bandwidth, dataloader, and compiler effects may dominate real runtime.",
        },
        {
            "caveatId": "model_quality_out_of_scope",
            "text": "The estimate says nothing about accuracy, convergence, stability, or scientific validity.",
        },
        {
            "caveatId": "calibration_required",
            "text": "Any numeric estimator implementation must later carry calibration source, version, and residual/error notes.",
        },
    ]


def example_boundaries() -> list[dict[str, Any]]:
    return [
        {
            "exampleId": "mnist_mlp_budget_shape",
            "allowedUse": "private example of how batch/epoch/parameter metadata could shape a budget estimate",
            "blockedUse": "public claim about MNIST training savings or estimator accuracy",
        },
        {
            "exampleId": "torch_fx_layer_profile",
            "allowedUse": "private example of graph/layer cost visibility",
            "blockedUse": "claim that traced graph cost equals full runtime cost",
        },
        {
            "exampleId": "pinn_diagnostic_context",
            "allowedUse": "downstream advisory input for PINN diagnostics",
            "blockedUse": "claim of better PDE solution quality or scientific correctness",
        },
    ]


def reviewer_next_steps() -> list[dict[str, str]]:
    return [
        {
            "stepId": "review_supported_inputs",
            "status": "open_private_review",
            "question": "Are these inputs enough for a useful private estimator MVP without implying runtime truth?",
        },
        {
            "stepId": "review_output_schema",
            "status": "open_private_review",
            "question": "Do the output fields force caveats and blocked claims to travel with every estimate?",
        },
        {
            "stepId": "select_a3_path",
            "status": "open_private_review",
            "question": "Should PROD-A3 be a schema validator, example packet, or implementation hold gate?",
        },
    ]


def blocked_claims() -> list[str]:
    return [
        "training cost savings",
        "estimator accuracy",
        "wall-clock runtime performance",
        "model quality improvement",
        "scientific correctness",
        "compiler correctness",
        "semantic preservation",
        "public product readiness",
        "SDK stability",
        "hardware readiness",
        "silicon readiness",
        "broad EML advantage",
    ]


def build_payload() -> dict[str, Any]:
    seed = prod_a1.build_payload()
    prod_a1.validate_payload(seed)
    inputs = supported_inputs()
    outputs = output_schema_fields()
    caveats = calibration_caveats()
    examples = example_boundaries()
    steps = reviewer_next_steps()
    summary = {
        "sourceArtifact": seed["artifactId"],
        "selectedLane": "training_cost_estimator",
        "prodA1NextRecommendedArtifact": seed["summary"]["nextRecommendedArtifact"],
        "supportedInputCount": len(inputs),
        "outputFieldCount": len(outputs),
        "calibrationCaveatCount": len(caveats),
        "exampleBoundaryCount": len(examples),
        "reviewerNextStepCount": len(steps),
        "blockedClaimCount": len(blocked_claims()),
        "nextRecommendedArtifact": "PROD-A3 training cost estimator schema validator or example packet selector",
        "d109HoldRespected": True,
        "d110Started": False,
        "reviewerResponseConsumed": False,
        "estimatorImplemented": False,
        "estimatorExecuted": False,
        "modelTrainingExecuted": False,
        "runtimeBenchmarkExecuted": False,
        "publicProductReady": False,
        "trainingSavingsClaim": False,
        "estimatorAccuracyClaim": False,
        "runtimePerformanceClaim": False,
        "modelQualityClaim": False,
        "scientificCorrectnessClaim": False,
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
        "artifactId": "prod-a2-training-cost-estimator-private-spec",
        "artifactType": "training_cost_estimator_private_spec",
        "status": STATUS,
        "date": DATE,
        "sourceArtifact": seed["artifactId"],
        "selectedLane": "training_cost_estimator",
        "supportedInputs": inputs,
        "outputSchemaFields": outputs,
        "calibrationCaveats": caveats,
        "exampleBoundaries": examples,
        "blockedClaims": blocked_claims(),
        "reviewerNextSteps": steps,
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
    if payload["sourceArtifact"] != "prod-a1-private-product-evidence-surface-seed":
        raise ValueError("PROD-A2 must consume PROD-A1")
    if payload["selectedLane"] != "training_cost_estimator":
        raise ValueError("PROD-A2 must select the training cost estimator lane")
    if summary["prodA1NextRecommendedArtifact"] != "PROD-A2 training cost estimator private spec":
        raise ValueError("PROD-A1 next artifact drift")
    if summary["supportedInputCount"] != 4:
        raise ValueError("supported input drift")
    if summary["outputFieldCount"] != 8:
        raise ValueError("output schema drift")
    if summary["calibrationCaveatCount"] != 5:
        raise ValueError("calibration caveat drift")
    if summary["exampleBoundaryCount"] != 3:
        raise ValueError("example boundary drift")
    if summary["reviewerNextStepCount"] != 3:
        raise ValueError("reviewer next-step drift")
    if summary["blockedClaimCount"] != 12:
        raise ValueError("blocked claim drift")
    for key in ["d109HoldRespected", "claimFlagsBounded"]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "d110Started",
        "reviewerResponseConsumed",
        "estimatorImplemented",
        "estimatorExecuted",
        "modelTrainingExecuted",
        "runtimeBenchmarkExecuted",
        "publicProductReady",
        "trainingSavingsClaim",
        "estimatorAccuracyClaim",
        "runtimePerformanceClaim",
        "modelQualityClaim",
        "scientificCorrectnessClaim",
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
        "artifactType": "training_cost_estimator_private_spec",
        "validationStatus": "pass",
        "semanticStrength": "private_training_cost_estimator_spec_no_implementation_no_savings_claim",
        "source": f"python/results/prod_a2_training_cost_estimator_private_spec/prod_a2_training_cost_estimator_private_spec_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "prod_a2_training_cost_estimator_private_spec_feed",
        "date": DATE,
        "status": payload["status"],
        "sourceArtifact": payload["sourceArtifact"],
        "selectedLane": payload["selectedLane"],
        "supportedInputCount": payload["summary"]["supportedInputCount"],
        "outputFieldCount": payload["summary"]["outputFieldCount"],
        "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        "estimatorImplemented": payload["summary"]["estimatorImplemented"],
        "trainingSavingsClaim": payload["summary"]["trainingSavingsClaim"],
        "runtimePerformanceClaim": payload["summary"]["runtimePerformanceClaim"],
        "nextAction": "Choose PROD-A3 as schema validator, example packet, or implementation hold gate.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# PROD-A2 Training Cost Estimator Private Spec",
        "",
        f"Status: `{payload['status']}`",
        "",
        "PROD-A2 defines a private advisory specification for a training cost estimator.",
        "It does not implement or execute an estimator.",
        "",
        "## Supported Inputs",
        "",
        "| Input | Status | Boundary |",
        "|---|---|---|",
    ]
    for item in payload["supportedInputs"]:
        lines.append(f"| `{item['inputId']}` | `{item['status']}` | {item['boundary']} |")
    lines.extend(["", "## Output Fields", "", "| Field | Type | Meaning |", "|---|---|---|"])
    for field in payload["outputSchemaFields"]:
        lines.append(f"| `{field['field']}` | `{field['type']}` | {field['meaning']} |")
    lines.extend(["", "## Calibration Caveats", ""])
    lines.extend(f"- `{item['caveatId']}`: {item['text']}" for item in payload["calibrationCaveats"])
    lines.extend(["", "## Blocked Claims", ""])
    lines.extend(f"- {item}" for item in payload["blockedClaims"])
    lines.extend(["", "## Summary", ""])
    lines.extend(
        [
            f"- source artifact: `{payload['summary']['sourceArtifact']}`",
            f"- selected lane: `{payload['summary']['selectedLane']}`",
            f"- next recommended artifact: `{payload['summary']['nextRecommendedArtifact']}`",
            f"- estimator implemented: `{payload['summary']['estimatorImplemented']}`",
            f"- training savings claim: `{payload['summary']['trainingSavingsClaim']}`",
            f"- runtime performance claim: `{payload['summary']['runtimePerformanceClaim']}`",
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
    result_path = out_dir / f"prod_a2_training_cost_estimator_private_spec_{STAMP}.json"
    report_path = report_dir / f"prod_a2_training_cost_estimator_private_spec_{STAMP}.md"
    evidence_path = evidence_dir / "prod_a2_training_cost_estimator_private_spec.json"
    feed_path = command_feed_dir / f"prod_a2_training_cost_estimator_private_spec_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/prod_a2_training_cost_estimator_private_spec")
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
    print("PROD_A2_TRAINING_COST_ESTIMATOR_PRIVATE_SPEC_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
