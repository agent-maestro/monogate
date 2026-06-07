#!/usr/bin/env python3
"""PINN-A1 private PINN advisor brief."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import prod_a2_training_cost_estimator_private_spec as prod_a2  # noqa: E402
from scripts import prod_a8_private_product_roadmap_post_cpg_selector as prod_a8  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_pinn_advisor_brief.v0"
STATUS = "PINN_A1_PRIVATE_PINN_ADVISOR_BRIEF_PASS"
NEXT_RECOMMENDED_ARTIFACT = "PINN-A2 private PINN advisor fixture packet or hold selector"

TRUE_CLAIM_FLAGS = {
    "pinn_advisor_brief_created",
    "prod_a8_consumed",
    "prod_a2_caveats_consumed",
    "supported_inputs_recorded",
    "diagnostics_recorded",
    "caveats_recorded",
    "examples_recorded",
    "dependencies_recorded",
    "blocked_claims_recorded",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "pinn_advisor_brief_created": True,
    "prod_a8_consumed": True,
    "prod_a2_caveats_consumed": True,
    "supported_inputs_recorded": True,
    "diagnostics_recorded": True,
    "caveats_recorded": True,
    "examples_recorded": True,
    "dependencies_recorded": True,
    "blocked_claims_recorded": True,
    "d109_hold_respected": True,
    "pinn_advisor_implemented": False,
    "pinn_advisor_executed": False,
    "pinn_training_executed": False,
    "pinn_solver_invoked": False,
    "pinn_diagnostic_claim": False,
    "scientific_correctness_claim": False,
    "training_improvement_claim": False,
    "training_savings_claim": False,
    "estimator_accuracy_claim": False,
    "model_quality_claim": False,
    "runtime_performance_claim": False,
    "compiler_plugin_implemented": False,
    "compiler_plugin_executed": False,
    "compiler_correctness_claim": False,
    "semantic_preservation_claim": False,
    "automatic_lowering_safety_claim": False,
    "sdk_stability_claim": False,
    "sdk_public_ready": False,
    "public_product_ready": False,
    "public_readiness_claim": False,
    "public_copy_approved": False,
    "public_docs_created": False,
    "public_package_release_claim": False,
    "ip_license_terms_finalized": False,
    "hardware_readiness_claim": False,
    "silicon_readiness_claim": False,
    "accelerator_card_ready": False,
    "electronics_repo_touched": False,
    "laptop_owned_repo_touched": False,
    "d110_started": False,
    "reviewer_response_consumed": False,
    "reviewer_approval_recorded": False,
    "broad_eml_advantage_claim": False,
}

NON_CLAIMS = [
    "PINN-A1 is a private brief for a possible PINN advisor; it does not implement or execute an advisor.",
    "PINN-A1 records advisory inputs, diagnostics, caveats, examples, dependencies, blocked claims, and reviewer questions only.",
    "PINN-A1 does not run training, invoke a PINN solver, benchmark runtime, or evaluate scientific correctness.",
    "PINN-A1 does not claim training improvement, training savings, estimator accuracy, model quality, public readiness, SDK stability, compiler correctness, hardware readiness, silicon readiness, or broad EML advantage.",
    "PINN-A1 does not touch laptop-owned electronics repositories, start D110, or consume reviewer response.",
]


def supported_inputs() -> list[dict[str, Any]]:
    return [
        {
            "inputId": "pde_problem_summary",
            "status": "supported_for_private_advisory_shape",
            "requiredFields": ["equation_family", "domain_summary", "boundary_condition_summary"],
            "optionalFields": ["initial_condition_summary", "parameter_symbols", "units_note"],
            "boundary": "Problem-shape context only; no claim that the PDE is correctly solved or fully specified.",
        },
        {
            "inputId": "training_loop_metadata",
            "status": "supported_for_training_context_advice",
            "requiredFields": ["epoch_count", "batch_count_or_dataset_size", "batch_size"],
            "optionalFields": ["optimizer_name", "learning_rate", "precision_policy", "gradient_accumulation_steps"],
            "boundary": "Training-context metadata only; no convergence, stability, or cost-savings claim.",
        },
        {
            "inputId": "loss_component_history_summary",
            "status": "supported_for_balance_warning_advice",
            "requiredFields": ["data_loss_summary", "physics_loss_summary"],
            "optionalFields": ["boundary_loss_summary", "regularization_loss_summary", "residual_scale_note"],
            "boundary": "Loss-shape summary only; no guarantee that loss trends diagnose the true physical error.",
        },
        {
            "inputId": "residual_sampling_summary",
            "status": "supported_for_sampling_gap_advice",
            "requiredFields": ["collocation_count", "sampling_strategy"],
            "optionalFields": ["domain_regions", "resampling_policy", "known_singularity_notes"],
            "boundary": "Sampling-context advice only; no coverage or solution-quality guarantee.",
        },
        {
            "inputId": "cost_estimator_packet_summary",
            "status": "supported_for_cost_context_advice",
            "requiredFields": ["estimate_id", "calibration_caveats", "blocked_claims"],
            "optionalFields": ["static_expression_cost", "graph_cost_profile", "training_budget_context"],
            "boundary": "Consumes cost context as caveated advice, not as runtime truth or savings proof.",
        },
    ]


def advisory_diagnostics() -> list[dict[str, str]]:
    return [
        {
            "diagnosticId": "loss_balance_warning",
            "adviceShape": "Flag large imbalance or unexplained drift between data, physics, and boundary loss summaries.",
            "boundary": "Warning only; not evidence of correct or incorrect PDE solution.",
        },
        {
            "diagnosticId": "residual_sampling_gap",
            "adviceShape": "Point out sparse, static, or poorly described collocation sampling relative to the domain summary.",
            "boundary": "Review prompt only; not a coverage guarantee.",
        },
        {
            "diagnosticId": "boundary_condition_visibility",
            "adviceShape": "Check whether boundary/initial conditions are explicit enough for review.",
            "boundary": "Completeness prompt only; not formal problem validation.",
        },
        {
            "diagnosticId": "cost_context_caveat_check",
            "adviceShape": "Require calibration caveats and blocked claims to remain attached to any cost-context note.",
            "boundary": "Evidence hygiene only; not estimator accuracy.",
        },
        {
            "diagnosticId": "reproducibility_packet_prompt",
            "adviceShape": "Suggest private capture of seeds, package versions, device label, and training metadata before comparing runs.",
            "boundary": "Reviewer next step only; not a reproducibility guarantee.",
        },
    ]


def caveats() -> list[dict[str, str]]:
    return [
        {
            "caveatId": "not_solver_correctness",
            "text": "The brief does not validate a PINN solver or prove that a learned solution satisfies a PDE.",
        },
        {
            "caveatId": "not_scientific_claim",
            "text": "Advisor output must not be framed as scientific correctness, physical validity, or publication-quality evidence.",
        },
        {
            "caveatId": "not_training_improvement",
            "text": "The brief does not claim faster convergence, lower loss, better accuracy, or improved generalization.",
        },
        {
            "caveatId": "cost_context_is_caveated",
            "text": "Any cost context inherited from training-cost artifacts remains caveated and is not wall-clock truth.",
        },
        {
            "caveatId": "human_review_required",
            "text": "Any advisor implementation or public copy requires a separate review gate.",
        },
    ]


def example_boundaries() -> list[dict[str, str]]:
    return [
        {
            "exampleId": "harmonic_oscillator_loss_balance_note",
            "allowedUse": "Private example of loss-balance wording for a simple equation family.",
            "blockedUse": "Claim that the model learned the true harmonic solution.",
        },
        {
            "exampleId": "burgers_residual_sampling_note",
            "allowedUse": "Private example of collocation/sampling review prompts.",
            "blockedUse": "Claim that sampling coverage is sufficient or the PDE residual is globally controlled.",
        },
        {
            "exampleId": "cost_caveat_attachment_note",
            "allowedUse": "Private example showing that cost caveats travel with advisor notes.",
            "blockedUse": "Claim that the advisor predicts wall-clock runtime or training savings.",
        },
    ]


def dependencies() -> list[dict[str, str]]:
    return [
        {
            "dependencyId": "prod_a8_selector",
            "status": "required_and_consumed",
            "reason": "PROD-A8 selected PINN-A1 after SDK and compiler-plugin lanes were paused.",
        },
        {
            "dependencyId": "prod_a2_training_cost_caveats",
            "status": "required_and_consumed",
            "reason": "PINN advisor cost context must inherit training-cost estimator caveats and blocked claims.",
        },
        {
            "dependencyId": "private_pinn_example_inventory",
            "status": "future_private_review_needed",
            "reason": "Concrete example packets should be reviewed before any advisor implementation.",
        },
        {
            "dependencyId": "human_implementation_gate",
            "status": "blocked_pending_review",
            "reason": "Implementation, execution, public docs, and claims require explicit approval.",
        },
    ]


def reviewer_questions() -> list[dict[str, str]]:
    return [
        {
            "questionId": "diagnostics_useful_without_science_claims",
            "question": "Which diagnostics are genuinely useful as review prompts without implying PDE solution quality?",
        },
        {
            "questionId": "minimum_example_packet",
            "question": "What is the smallest private example packet that can test the advisor language safely?",
        },
        {
            "questionId": "implementation_gate_condition",
            "question": "What must be true before a PINN advisor implementation is worth building?",
        },
    ]


def blocked_claims() -> list[str]:
    return [
        "PINN solver correctness",
        "scientific correctness",
        "PDE solution validity",
        "training improvement",
        "training cost savings",
        "estimator accuracy",
        "model quality improvement",
        "wall-clock runtime performance",
        "compiler correctness",
        "semantic preservation",
        "SDK stability",
        "public product readiness",
        "hardware readiness",
        "silicon readiness",
        "broad EML advantage",
    ]


def build_payload() -> dict[str, Any]:
    selector = prod_a8.build_payload()
    prod_a8.validate_payload(selector)
    cost_spec = prod_a2.build_payload()
    prod_a2.validate_payload(cost_spec)
    inputs = supported_inputs()
    diagnostics = advisory_diagnostics()
    caveat_rows = caveats()
    examples = example_boundaries()
    dependency_rows = dependencies()
    questions = reviewer_questions()
    summary = {
        "sourceArtifacts": [selector["artifactId"], cost_spec["artifactId"]],
        "selectedLaneId": selector["summary"]["selectedLaneId"],
        "briefScope": "private_diagnostic_brief_only",
        "supportedInputCount": len(inputs),
        "diagnosticCount": len(diagnostics),
        "caveatCount": len(caveat_rows),
        "exampleBoundaryCount": len(examples),
        "dependencyCount": len(dependency_rows),
        "reviewerQuestionCount": len(questions),
        "blockedClaimCount": len(blocked_claims()),
        "advisorImplemented": False,
        "advisorExecuted": False,
        "trainingExecuted": False,
        "solverInvoked": False,
        "scientificCorrectnessClaim": False,
        "trainingImprovementClaim": False,
        "runtimePerformanceClaim": False,
        "publicReadinessClaim": False,
        "nextRecommendedArtifact": NEXT_RECOMMENDED_ARTIFACT,
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="pinn-a1-private-pinn-advisor-brief",
        artifact_type="private_pinn_advisor_brief",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifacts": summary["sourceArtifacts"],
            "supportedInputs": inputs,
            "advisoryDiagnostics": diagnostics,
            "caveats": caveat_rows,
            "exampleBoundaries": examples,
            "dependencies": dependency_rows,
            "reviewerQuestions": questions,
            "blockedClaims": blocked_claims(),
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifacts"] != [
        "prod-a8-private-product-roadmap-post-cpg-selector",
        "prod-a2-training-cost-estimator-private-spec",
    ]:
        raise ValueError("PINN-A1 must consume PROD-A8 and PROD-A2")
    summary = payload["summary"]
    if summary["selectedLaneId"] != "pinn_advisor":
        raise ValueError("PINN-A1 must remain in the PINN advisor lane")
    if summary["briefScope"] != "private_diagnostic_brief_only":
        raise ValueError("PINN-A1 scope must remain brief-only")
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected next recommended artifact")
    expected_counts = {
        "supportedInputCount": len(payload["supportedInputs"]),
        "diagnosticCount": len(payload["advisoryDiagnostics"]),
        "caveatCount": len(payload["caveats"]),
        "exampleBoundaryCount": len(payload["exampleBoundaries"]),
        "dependencyCount": len(payload["dependencies"]),
        "reviewerQuestionCount": len(payload["reviewerQuestions"]),
        "blockedClaimCount": len(payload["blockedClaims"]),
    }
    for key, expected in expected_counts.items():
        if summary[key] != expected:
            raise ValueError(f"{key} mismatch")
    for key in [
        "advisorImplemented",
        "advisorExecuted",
        "trainingExecuted",
        "solverInvoked",
        "scientificCorrectnessClaim",
        "trainingImprovementClaim",
        "runtimePerformanceClaim",
        "publicReadinessClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    for key in TRUE_CLAIM_FLAGS:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS and value is not False:
            raise ValueError(f"{key} must remain false")
    for required in [
        "PINN solver correctness",
        "scientific correctness",
        "training improvement",
        "training cost savings",
        "wall-clock runtime performance",
        "public product readiness",
        "broad EML advantage",
    ]:
        if required not in payload["blockedClaims"]:
            raise ValueError(f"missing blocked claim: {required}")
    if not any(item["dependencyId"] == "human_implementation_gate" for item in payload["dependencies"]):
        raise ValueError("human implementation gate dependency must be recorded")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return build_evidence_packet(
        artifact_id=payload["artifactId"],
        artifact_type=payload["artifactType"],
        semantic_strength="private_pinn_advisor_brief_no_implementation_or_science_claim",
        source=f"python/results/pinn_a1_private_pinn_advisor_brief/pinn_a1_private_pinn_advisor_brief_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="pinn_a1_private_pinn_advisor_brief_feed",
        date=DATE,
        status=payload["status"],
        next_action="Review PINN-A1 brief or create PINN-A2 fixture packet/hold selector.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifacts": payload["sourceArtifacts"],
            "selectedLaneId": payload["summary"]["selectedLaneId"],
            "briefScope": payload["summary"]["briefScope"],
            "supportedInputCount": payload["summary"]["supportedInputCount"],
            "diagnosticCount": payload["summary"]["diagnosticCount"],
            "blockedClaimCount": payload["summary"]["blockedClaimCount"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
            "advisorImplemented": payload["summary"]["advisorImplemented"],
            "advisorExecuted": payload["summary"]["advisorExecuted"],
            "scientificCorrectnessClaim": payload["summary"]["scientificCorrectnessClaim"],
            "trainingImprovementClaim": payload["summary"]["trainingImprovementClaim"],
            "publicReadinessClaim": payload["summary"]["publicReadinessClaim"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="PINN-A1 Private PINN Advisor Brief",
        status=payload["status"],
        summary_rows=[
            ("source artifacts", ", ".join(payload["sourceArtifacts"])),
            ("selected lane", payload["summary"]["selectedLaneId"]),
            ("brief scope", payload["summary"]["briefScope"]),
            ("supported inputs", payload["summary"]["supportedInputCount"]),
            ("diagnostics", payload["summary"]["diagnosticCount"]),
            ("caveats", payload["summary"]["caveatCount"]),
            ("example boundaries", payload["summary"]["exampleBoundaryCount"]),
            ("dependencies", payload["summary"]["dependencyCount"]),
            ("blocked claims", payload["summary"]["blockedClaimCount"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
            ("advisor implemented", payload["summary"]["advisorImplemented"]),
            ("advisor executed", payload["summary"]["advisorExecuted"]),
            ("scientific correctness claim", payload["summary"]["scientificCorrectnessClaim"]),
            ("public readiness claim", payload["summary"]["publicReadinessClaim"]),
        ],
        sections=[
            (
                "Supported Inputs",
                [
                    f"- `{item['inputId']}`: `{item['status']}` - {item['boundary']}"
                    for item in payload["supportedInputs"]
                ],
            ),
            (
                "Advisory Diagnostics",
                [
                    f"- `{item['diagnosticId']}`: {item['adviceShape']} Boundary: {item['boundary']}"
                    for item in payload["advisoryDiagnostics"]
                ],
            ),
            (
                "Dependencies",
                [
                    f"- `{item['dependencyId']}`: `{item['status']}` - {item['reason']}"
                    for item in payload["dependencies"]
                ],
            ),
            (
                "Reviewer Questions",
                [f"- `{item['questionId']}`: {item['question']}" for item in payload["reviewerQuestions"]],
            ),
            ("Blocked Claims", [f"- {item}" for item in payload["blockedClaims"]]),
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"pinn_a1_private_pinn_advisor_brief_{STAMP}.json"
    report_path = report_dir / f"pinn_a1_private_pinn_advisor_brief_{STAMP}.md"
    evidence_path = evidence_dir / "pinn_a1_private_pinn_advisor_brief.json"
    feed_path = command_feed_dir / f"pinn_a1_private_pinn_advisor_brief_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/pinn_a1_private_pinn_advisor_brief")
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
    print("PINN_A1_PRIVATE_PINN_ADVISOR_BRIEF_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
