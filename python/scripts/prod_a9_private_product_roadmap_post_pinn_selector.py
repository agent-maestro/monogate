#!/usr/bin/env python3
"""PROD-A9 private product roadmap post-PINN selector."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import pinn_a4_private_pinn_advisor_static_fixture_review_or_pause_selector as pinn_a4  # noqa: E402
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
SCHEMA_VERSION = "monogate.private_product_roadmap_post_pinn_selector.v0"
STATUS = "PROD_A9_PRIVATE_PRODUCT_ROADMAP_POST_PINN_SELECTOR_PASS"
NEXT_RECOMMENDED_ARTIFACT = "PROD-A10 private product roadmap pause digest"

TRUE_CLAIM_FLAGS = {
    "prod_a1_consumed",
    "pinn_a4_consumed",
    "product_roadmap_post_pinn_selector_created",
    "pinn_advisor_lane_paused",
    "product_pause_digest_selected",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "prod_a1_consumed": True,
    "pinn_a4_consumed": True,
    "product_roadmap_post_pinn_selector_created": True,
    "pinn_advisor_lane_paused": True,
    "product_pause_digest_selected": True,
    "d109_hold_respected": True,
    "sdk_implementation_changed": False,
    "sdk_stability_claim": False,
    "sdk_public_ready": False,
    "training_cost_estimator_implemented": False,
    "training_cost_estimator_executed": False,
    "training_savings_claim": False,
    "estimator_accuracy_claim": False,
    "pinn_advisor_implemented": False,
    "pinn_advisor_executed": False,
    "pinn_training_executed": False,
    "scientific_correctness_claim": False,
    "training_improvement_claim": False,
    "compiler_plugin_implemented": False,
    "compiler_plugin_executed": False,
    "compiler_correctness_claim": False,
    "semantic_preservation_claim": False,
    "automatic_lowering_safety_claim": False,
    "runtime_performance_claim": False,
    "public_product_ready": False,
    "public_readiness_claim": False,
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
    "PROD-A9 is a private product-roadmap selector; it does not implement or execute any product.",
    "PROD-A9 selects a pause digest because SDK, compiler-plugin, and PINN lanes are paused, training-cost artifacts are seeded, and hardware/IP lanes require concrete hardware evidence.",
    "PROD-A9 does not claim public readiness, SDK stability, estimator accuracy, training savings, scientific correctness, compiler correctness, runtime performance, hardware readiness, silicon readiness, or broad EML advantage.",
    "PROD-A9 does not touch laptop-owned electronics repositories, start D110, or consume reviewer response.",
]


def lane_states(product_surface: dict[str, Any], pinn_pause: dict[str, Any]) -> list[dict[str, Any]]:
    lane_by_id = {lane["laneId"]: lane for lane in product_surface["productLanes"]}
    return [
        {
            "laneId": "monogate_sdk",
            "state": "paused_as_seeded",
            "evidence": ["SDK-A1 through SDK-A8 smoke chain pause"],
            "nextPolicy": "reopen only on explicit SDK docs/product request",
            "sourceNextPrivateArtifact": lane_by_id["monogate_sdk"]["nextPrivateArtifact"],
        },
        {
            "laneId": "eml_compiler_plugin",
            "state": "paused_as_seeded",
            "evidence": ["CPG-A1 through CPG-A10 compiler-plugin advisory pause"],
            "nextPolicy": "reopen only on explicit reviewer approval or concrete product need",
            "sourceNextPrivateArtifact": lane_by_id["eml_compiler_plugin"]["nextPrivateArtifact"],
        },
        {
            "laneId": "training_cost_estimator",
            "state": "seeded_and_parked",
            "evidence": ["PROD-A2 through PROD-A6 spec/schema/static fixture seed"],
            "nextPolicy": "reopen only with explicit estimator request or real-user validation condition",
            "sourceNextPrivateArtifact": lane_by_id["training_cost_estimator"]["nextPrivateArtifact"],
        },
        {
            "laneId": "pinn_advisor",
            "state": "paused_as_seeded" if pinn_pause["summary"]["lanePausedAsSufficientlyBounded"] else "blocked_until_pause_confirmed",
            "evidence": ["PINN-A1 through PINN-A4 private brief/fixtures/pause"],
            "nextPolicy": "reopen only on explicit bounded product need; no advisor implementation without approval",
            "sourceNextPrivateArtifact": lane_by_id["pinn_advisor"]["nextPrivateArtifact"],
        },
        {
            "laneId": "eml_ip_core_license",
            "state": "blocked_until_hardware_evidence",
            "evidence": ["product roadmap dependency only"],
            "nextPolicy": "wait for concrete hardware/core evidence and legal review",
            "sourceNextPrivateArtifact": lane_by_id["eml_ip_core_license"]["nextPrivateArtifact"],
        },
        {
            "laneId": "eml_accelerator_card",
            "state": "blocked_until_laptop_hardware_evidence",
            "evidence": ["product roadmap dependency only"],
            "nextPolicy": "wait for laptop/electronics Arty proof/capture evidence",
            "sourceNextPrivateArtifact": lane_by_id["eml_accelerator_card"]["nextPrivateArtifact"],
        },
    ]


def candidate_actions() -> list[dict[str, str]]:
    return [
        {
            "actionId": "product_roadmap_pause_digest",
            "decision": "selected",
            "nextArtifact": NEXT_RECOMMENDED_ARTIFACT,
            "reason": "All current product lanes are paused, seeded, or blocked; a compact pause digest prevents drift into implementation.",
        },
        {
            "actionId": "training_cost_estimator_release_gate",
            "decision": "parked",
            "nextArtifact": "PROD-A10-alt training cost estimator release-condition selector",
            "reason": "Estimator release conditions should wait for explicit real-user validation intent.",
        },
        {
            "actionId": "ip_license_scope_memo",
            "decision": "blocked",
            "nextArtifact": "IP-A1 private license-scope memo after hardware evidence",
            "reason": "IP/license wording should wait for concrete hardware/core evidence and legal review.",
        },
        {
            "actionId": "accelerator_dependency_ladder",
            "decision": "blocked",
            "nextArtifact": "ACCEL-A1 dependency ladder after hardware capture evidence",
            "reason": "Accelerator-card feasibility depends on laptop/electronics evidence.",
        },
        {
            "actionId": "public_product_docs",
            "decision": "blocked",
            "nextArtifact": "future public-copy gate only after explicit approval",
            "reason": "No product lane has public readiness approval.",
        },
    ]


def build_payload() -> dict[str, Any]:
    product_surface = prod_a1.build_payload()
    prod_a1.validate_payload(product_surface)
    pinn_pause = pinn_a4.build_payload()
    pinn_a4.validate_payload(pinn_pause)
    states = lane_states(product_surface, pinn_pause)
    actions = candidate_actions()
    selected = [action for action in actions if action["decision"] == "selected"]
    summary = {
        "sourceArtifacts": [product_surface["artifactId"], pinn_pause["artifactId"]],
        "laneStateCount": len(states),
        "pausedLaneCount": sum(1 for state in states if state["state"] == "paused_as_seeded"),
        "seededParkedLaneCount": sum(1 for state in states if state["state"] == "seeded_and_parked"),
        "blockedLaneCount": sum(1 for state in states if state["state"].startswith("blocked")),
        "selectedActionId": selected[0]["actionId"],
        "selectedNextArtifact": selected[0]["nextArtifact"],
        "pinnAdvisorLanePaused": pinn_pause["summary"]["lanePausedAsSufficientlyBounded"],
        "productImplementationStarted": False,
        "publicReadinessClaim": False,
        "nextRecommendedArtifact": selected[0]["nextArtifact"],
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="prod-a9-private-product-roadmap-post-pinn-selector",
        artifact_type="private_product_roadmap_post_pinn_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifacts": summary["sourceArtifacts"],
            "laneStates": states,
            "candidateActions": actions,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifacts"] != [
        "prod-a1-private-product-evidence-surface-seed",
        "pinn-a4-private-pinn-advisor-static-fixture-review-or-pause-selector",
    ]:
        raise ValueError("PROD-A9 must consume PROD-A1 and PINN-A4")
    summary = payload["summary"]
    if summary["selectedActionId"] != "product_roadmap_pause_digest":
        raise ValueError("PROD-A9 must select product roadmap pause digest")
    if summary["selectedNextArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected next artifact")
    if summary["pinnAdvisorLanePaused"] is not True:
        raise ValueError("PINN lane must be paused before post-PINN selector")
    if summary["laneStateCount"] != 6:
        raise ValueError("expected six product lane states")
    states = {state["laneId"]: state["state"] for state in payload["laneStates"]}
    if states != {
        "monogate_sdk": "paused_as_seeded",
        "eml_compiler_plugin": "paused_as_seeded",
        "training_cost_estimator": "seeded_and_parked",
        "pinn_advisor": "paused_as_seeded",
        "eml_ip_core_license": "blocked_until_hardware_evidence",
        "eml_accelerator_card": "blocked_until_laptop_hardware_evidence",
    }:
        raise ValueError("unexpected lane states")
    decisions = {action["actionId"]: action["decision"] for action in payload["candidateActions"]}
    if decisions != {
        "product_roadmap_pause_digest": "selected",
        "training_cost_estimator_release_gate": "parked",
        "ip_license_scope_memo": "blocked",
        "accelerator_dependency_ladder": "blocked",
        "public_product_docs": "blocked",
    }:
        raise ValueError("unexpected candidate action decisions")
    for key in ["productImplementationStarted", "publicReadinessClaim"]:
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
        semantic_strength="private_product_roadmap_selector_no_product_implementation",
        source=f"python/results/prod_a9_private_product_roadmap_post_pinn_selector/prod_a9_private_product_roadmap_post_pinn_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="prod_a9_private_product_roadmap_post_pinn_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Create PROD-A10 private product roadmap pause digest.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifacts": payload["sourceArtifacts"],
            "selectedActionId": payload["summary"]["selectedActionId"],
            "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
            "laneStateCount": payload["summary"]["laneStateCount"],
            "pinnAdvisorLanePaused": payload["summary"]["pinnAdvisorLanePaused"],
            "productImplementationStarted": payload["summary"]["productImplementationStarted"],
            "publicReadinessClaim": payload["summary"]["publicReadinessClaim"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="PROD-A9 Private Product Roadmap Post-PINN Selector",
        status=payload["status"],
        summary_rows=[
            ("source artifacts", ", ".join(payload["sourceArtifacts"])),
            ("lane states", payload["summary"]["laneStateCount"]),
            ("paused lanes", payload["summary"]["pausedLaneCount"]),
            ("seeded/parked lanes", payload["summary"]["seededParkedLaneCount"]),
            ("blocked lanes", payload["summary"]["blockedLaneCount"]),
            ("selected action", payload["summary"]["selectedActionId"]),
            ("selected next artifact", payload["summary"]["selectedNextArtifact"]),
            ("product implementation started", payload["summary"]["productImplementationStarted"]),
            ("public readiness claim", payload["summary"]["publicReadinessClaim"]),
        ],
        sections=[
            (
                "Lane States",
                [f"- `{state['laneId']}`: `{state['state']}` - {state['nextPolicy']}" for state in payload["laneStates"]],
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
    result_path = out_dir / f"prod_a9_private_product_roadmap_post_pinn_selector_{STAMP}.json"
    report_path = report_dir / f"prod_a9_private_product_roadmap_post_pinn_selector_{STAMP}.md"
    evidence_path = evidence_dir / "prod_a9_private_product_roadmap_post_pinn_selector.json"
    feed_path = command_feed_dir / f"prod_a9_private_product_roadmap_post_pinn_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/prod_a9_private_product_roadmap_post_pinn_selector")
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
    print("PROD_A9_PRIVATE_PRODUCT_ROADMAP_POST_PINN_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
