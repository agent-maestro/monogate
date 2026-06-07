#!/usr/bin/env python3
"""PROD-A8 private product roadmap post-CPG selector."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import cpg_a10_private_lint_contract_implementation_hold_review_or_pause_selector as cpg_a10  # noqa: E402
from scripts import prod_a1_private_product_evidence_surface_seed as prod_a1  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_product_roadmap_post_cpg_selector.v0"
STATUS = "PROD_A8_PRIVATE_PRODUCT_ROADMAP_POST_CPG_SELECTOR_PASS"

NEXT_RECOMMENDED_ARTIFACT = "PINN-A1 private PINN advisor brief"

TRUE_CLAIM_FLAGS = {
    "prod_a1_consumed",
    "cpg_a10_consumed",
    "product_roadmap_post_cpg_selector_created",
    "pinn_advisor_brief_selected",
    "compiler_plugin_lane_paused",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "prod_a1_consumed": True,
    "cpg_a10_consumed": True,
    "product_roadmap_post_cpg_selector_created": True,
    "pinn_advisor_brief_selected": True,
    "compiler_plugin_lane_paused": True,
    "d109_hold_respected": True,
    "pinn_advisor_implemented": False,
    "pinn_advisor_executed": False,
    "pinn_diagnostic_claim": False,
    "scientific_correctness_claim": False,
    "training_improvement_claim": False,
    "training_cost_estimator_implemented": False,
    "training_savings_claim": False,
    "estimator_accuracy_claim": False,
    "compiler_plugin_implemented": False,
    "compiler_plugin_executed": False,
    "compiler_correctness_claim": False,
    "semantic_preservation_claim": False,
    "automatic_lowering_safety_claim": False,
    "runtime_performance_claim": False,
    "sdk_stability_claim": False,
    "sdk_public_ready": False,
    "public_product_ready": False,
    "public_readiness_claim": False,
    "public_copy_approved": False,
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
    "PROD-A8 is a private product-roadmap selector; it does not implement a PINN advisor.",
    "PROD-A8 selects a PINN advisor brief only because SDK and compiler-plugin lanes are paused and the training-cost caveat lane is seeded.",
    "PROD-A8 does not claim scientific correctness, training improvement, estimator accuracy, runtime performance, public readiness, SDK stability, hardware readiness, silicon readiness, or broad EML advantage.",
    "PROD-A8 does not touch laptop-owned electronics repositories and does not start D110 or consume reviewer response.",
]


def candidate_lane_actions(product_surface: dict[str, Any], cpg_pause: dict[str, Any]) -> list[dict[str, Any]]:
    lane_by_id = {lane["laneId"]: lane for lane in product_surface["productLanes"]}
    compiler_paused = cpg_pause["summary"]["compilerPluginLanePaused"]
    return [
        {
            "laneId": "pinn_advisor",
            "decision": "selected",
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
            "reason": "PINN advisor can advance as a private diagnostic brief downstream of training-cost caveats without claiming solver correctness or training improvement.",
            "sourceNextPrivateArtifact": lane_by_id["pinn_advisor"]["nextPrivateArtifact"],
        },
        {
            "laneId": "training_cost_estimator",
            "decision": "parked_as_seeded",
            "nextArtifact": "PROD-A9 training cost estimator executable validator or release-condition selector",
            "reason": "Training-cost spec/schema/fixtures are seeded through PROD-A6; further estimator work should wait for an explicit estimator request or real-user validation condition.",
            "sourceNextPrivateArtifact": lane_by_id["training_cost_estimator"]["nextPrivateArtifact"],
        },
        {
            "laneId": "eml_compiler_plugin",
            "decision": "paused_as_seeded" if compiler_paused else "blocked_until_pause_confirmed",
            "nextArtifact": "reopen only with explicit reviewer approval or concrete product need",
            "reason": "CPG-A10 pauses the compiler-plugin lane as sufficiently bounded with no implementation approval.",
            "sourceNextPrivateArtifact": lane_by_id["eml_compiler_plugin"]["nextPrivateArtifact"],
        },
        {
            "laneId": "monogate_sdk",
            "decision": "paused_as_seeded",
            "nextArtifact": "reopen only on concrete SDK docs/product request",
            "reason": "SDK-A8 already paused the SDK smoke lane as sufficiently seeded.",
            "sourceNextPrivateArtifact": lane_by_id["monogate_sdk"]["nextPrivateArtifact"],
        },
        {
            "laneId": "eml_ip_core_license",
            "decision": "blocked_until_hardware_evidence",
            "nextArtifact": "IP-A1 license-scope memo after concrete hardware evidence",
            "reason": "IP/license wording should wait for concrete hardware/core evidence and legal review.",
            "sourceNextPrivateArtifact": lane_by_id["eml_ip_core_license"]["nextPrivateArtifact"],
        },
        {
            "laneId": "eml_accelerator_card",
            "decision": "blocked_until_laptop_hardware_evidence",
            "nextArtifact": "ACCEL-A1 dependency ladder after Arty proof-of-life/capture evidence",
            "reason": "Accelerator-card feasibility depends on hardware evidence owned by the laptop/electronics lane.",
            "sourceNextPrivateArtifact": lane_by_id["eml_accelerator_card"]["nextPrivateArtifact"],
        },
    ]


def build_payload() -> dict[str, Any]:
    product_surface = prod_a1.build_payload()
    prod_a1.validate_payload(product_surface)
    cpg_pause = cpg_a10.build_payload()
    cpg_a10.validate_payload(cpg_pause)
    actions = candidate_lane_actions(product_surface, cpg_pause)
    selected = [action for action in actions if action["decision"] == "selected"]
    summary = {
        "sourceArtifacts": [product_surface["artifactId"], cpg_pause["artifactId"]],
        "candidateLaneActionCount": len(actions),
        "selectedLaneId": selected[0]["laneId"],
        "selectedNextArtifact": selected[0]["nextArtifact"],
        "compilerPluginLanePaused": cpg_pause["summary"]["compilerPluginLanePaused"],
        "pinnAdvisorImplemented": False,
        "pinnAdvisorExecuted": False,
        "scientificCorrectnessClaim": False,
        "trainingImprovementClaim": False,
        "trainingSavingsClaim": False,
        "estimatorAccuracyClaim": False,
        "runtimePerformanceClaim": False,
        "publicReadinessClaim": False,
        "nextRecommendedArtifact": selected[0]["nextArtifact"],
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="prod-a8-private-product-roadmap-post-cpg-selector",
        artifact_type="private_product_roadmap_post_cpg_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifacts": [product_surface["artifactId"], cpg_pause["artifactId"]],
            "candidateLaneActions": actions,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifacts"] != [
        "prod-a1-private-product-evidence-surface-seed",
        "cpg-a10-private-lint-contract-implementation-hold-review-or-pause-selector",
    ]:
        raise ValueError("PROD-A8 must consume PROD-A1 and CPG-A10")
    summary = payload["summary"]
    if summary["selectedLaneId"] != "pinn_advisor":
        raise ValueError("PINN advisor lane should be selected")
    if summary["selectedNextArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected next artifact")
    if summary["compilerPluginLanePaused"] is not True:
        raise ValueError("compiler-plugin lane must be paused before selecting PINN advisor")
    for key in [
        "pinnAdvisorImplemented",
        "pinnAdvisorExecuted",
        "scientificCorrectnessClaim",
        "trainingImprovementClaim",
        "trainingSavingsClaim",
        "estimatorAccuracyClaim",
        "runtimePerformanceClaim",
        "publicReadinessClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    actions = payload["candidateLaneActions"]
    if sum(1 for action in actions if action["decision"] == "selected") != 1:
        raise ValueError("exactly one lane must be selected")
    decisions = {action["laneId"]: action["decision"] for action in actions}
    if decisions["eml_compiler_plugin"] != "paused_as_seeded":
        raise ValueError("compiler-plugin lane must remain paused")
    if decisions["monogate_sdk"] != "paused_as_seeded":
        raise ValueError("SDK lane must remain paused")
    if decisions["training_cost_estimator"] != "parked_as_seeded":
        raise ValueError("training cost estimator must remain parked as seeded")
    if decisions["eml_ip_core_license"] != "blocked_until_hardware_evidence":
        raise ValueError("IP core license must wait for hardware evidence")
    if decisions["eml_accelerator_card"] != "blocked_until_laptop_hardware_evidence":
        raise ValueError("accelerator card must wait for laptop/hardware evidence")
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
        semantic_strength="private_product_roadmap_selector_no_product_or_public_claim",
        source=f"python/results/prod_a8_private_product_roadmap_post_cpg_selector/prod_a8_private_product_roadmap_post_cpg_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="prod_a8_private_product_roadmap_post_cpg_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Create PINN-A1 private PINN advisor brief.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifacts": payload["sourceArtifacts"],
            "selectedLaneId": payload["summary"]["selectedLaneId"],
            "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
            "compilerPluginLanePaused": payload["summary"]["compilerPluginLanePaused"],
            "scientificCorrectnessClaim": payload["summary"]["scientificCorrectnessClaim"],
            "publicReadinessClaim": payload["summary"]["publicReadinessClaim"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="PROD-A8 Private Product Roadmap Post-CPG Selector",
        status=payload["status"],
        summary_rows=[
            ("source artifacts", ", ".join(payload["sourceArtifacts"])),
            ("selected lane", payload["summary"]["selectedLaneId"]),
            ("selected next artifact", payload["summary"]["selectedNextArtifact"]),
            ("compiler plugin lane paused", payload["summary"]["compilerPluginLanePaused"]),
            ("scientific correctness claim", payload["summary"]["scientificCorrectnessClaim"]),
            ("public readiness claim", payload["summary"]["publicReadinessClaim"]),
        ],
        sections=[
            (
                "Candidate Lane Actions",
                [
                    f"- `{action['laneId']}`: `{action['decision']}` - {action['reason']}"
                    for action in payload["candidateLaneActions"]
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
    result_path = out_dir / f"prod_a8_private_product_roadmap_post_cpg_selector_{STAMP}.json"
    report_path = report_dir / f"prod_a8_private_product_roadmap_post_cpg_selector_{STAMP}.md"
    evidence_path = evidence_dir / "prod_a8_private_product_roadmap_post_cpg_selector.json"
    feed_path = command_feed_dir / f"prod_a8_private_product_roadmap_post_cpg_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/prod_a8_private_product_roadmap_post_cpg_selector")
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
    print("PROD_A8_PRIVATE_PRODUCT_ROADMAP_POST_CPG_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
