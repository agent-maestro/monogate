#!/usr/bin/env python3
"""PROD-A7 private product roadmap return selector."""

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
from scripts import sdk_a8_private_sdk_smoke_chain_pause_or_docs_selector as sdk_a8  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_product_roadmap_return_selector.v0"
STATUS = "PROD_A7_PRIVATE_PRODUCT_ROADMAP_RETURN_SELECTOR_PASS"

TRUE_CLAIM_FLAGS = {
    "prod_a1_consumed",
    "sdk_a8_consumed",
    "product_roadmap_return_selector_created",
    "compiler_plugin_guard_note_selected",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "prod_a1_consumed": True,
    "sdk_a8_consumed": True,
    "product_roadmap_return_selector_created": True,
    "compiler_plugin_guard_note_selected": True,
    "d109_hold_respected": True,
    "compiler_plugin_implemented": False,
    "compiler_plugin_guard_note_created": False,
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
    "training_savings_claim": False,
    "estimator_accuracy_claim": False,
    "scientific_correctness_claim": False,
    "hardware_readiness_claim": False,
    "silicon_readiness_claim": False,
    "ip_license_terms_finalized": False,
    "accelerator_card_ready": False,
    "electronics_repo_touched": False,
    "laptop_owned_repo_touched": False,
    "d110_started": False,
    "reviewer_response_consumed": False,
    "reviewer_approval_recorded": False,
    "broad_eml_advantage_claim": False,
}

NON_CLAIMS = [
    "PROD-A7 is a private product-roadmap selector; it does not implement a compiler plugin or create a guard-note packet.",
    "PROD-A7 selects the compiler-plugin guard-note lane as advisory product work only.",
    "PROD-A7 does not claim compiler correctness, semantic preservation, automatic lowering safety, runtime performance, SDK stability, public readiness, or public package release readiness.",
    "PROD-A7 does not claim training savings, estimator accuracy, scientific correctness, hardware readiness, silicon readiness, IP license readiness, accelerator card readiness, reviewer approval, or broad EML advantage.",
    "PROD-A7 respects the D109 hold and does not start D110, consume reviewer response, or touch laptop-owned electronics repositories.",
]


def load_sdk_a8_result() -> dict[str, Any]:
    path = (
        ROOT
        / "python/results/sdk_a8_private_sdk_smoke_chain_pause_or_docs_selector"
        / f"sdk_a8_private_sdk_smoke_chain_pause_or_docs_selector_{STAMP}.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    sdk_a8.validate_payload(payload)
    return payload


def candidate_lane_actions(product_surface: dict[str, Any]) -> list[dict[str, Any]]:
    lane_by_id = {lane["laneId"]: lane for lane in product_surface["productLanes"]}
    return [
        {
            "laneId": "eml_compiler_plugin",
            "decision": "selected",
            "nextArtifact": "CPG-A1 private compiler-plugin guard-note packet",
            "reason": "The SDK smoke lane is seeded; the next roadmap item is an advisory compiler-plugin guard-note that can clarify lint/advice boundaries without compiler-correctness claims.",
            "sourceNextPrivateArtifact": lane_by_id["eml_compiler_plugin"]["nextPrivateArtifact"],
        },
        {
            "laneId": "training_cost_estimator",
            "decision": "parked",
            "nextArtifact": "PROD-A9 training cost estimator executable validator or hold-gate selector",
            "reason": "Training-cost governance is already seeded through PROD-A6; implementation hold-gate should wait until the compiler-plugin guard-note boundary is captured or an explicit estimator request arrives.",
            "sourceNextPrivateArtifact": lane_by_id["training_cost_estimator"]["nextPrivateArtifact"],
        },
        {
            "laneId": "pinn_advisor",
            "decision": "parked",
            "nextArtifact": "PINN-A1 private PINN advisor brief",
            "reason": "PINN advisor remains downstream of estimator caveats and should not precede the guard-note boundary.",
            "sourceNextPrivateArtifact": lane_by_id["pinn_advisor"]["nextPrivateArtifact"],
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
        {
            "laneId": "monogate_sdk",
            "decision": "paused_as_seeded",
            "nextArtifact": "SDK smoke lane resumes only on new concrete SDK surface or docs request",
            "reason": "SDK-A8 paused the SDK smoke lane as sufficiently seeded.",
            "sourceNextPrivateArtifact": lane_by_id["monogate_sdk"]["nextPrivateArtifact"],
        },
    ]


def build_payload() -> dict[str, Any]:
    product_surface = prod_a1.build_payload()
    prod_a1.validate_payload(product_surface)
    sdk_pause = load_sdk_a8_result()
    actions = candidate_lane_actions(product_surface)
    selected = [action for action in actions if action["decision"] == "selected"]
    summary = {
        "sourceArtifacts": [product_surface["artifactId"], sdk_pause["artifactId"]],
        "candidateLaneActionCount": len(actions),
        "selectedLaneId": selected[0]["laneId"],
        "selectedNextArtifact": selected[0]["nextArtifact"],
        "sdkSmokeLanePaused": sdk_pause["summary"]["sdkSmokeChainSeeded"],
        "compilerPluginImplemented": False,
        "compilerPluginGuardNoteCreated": False,
        "publicReadinessClaim": False,
        "compilerCorrectnessClaim": False,
        "semanticPreservationClaim": False,
        "runtimePerformanceClaim": False,
        "nextRecommendedArtifact": selected[0]["nextArtifact"],
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="prod-a7-private-product-roadmap-return-selector",
        artifact_type="private_product_roadmap_return_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifacts": [product_surface["artifactId"], sdk_pause["artifactId"]],
            "candidateLaneActions": actions,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifacts"] != [
        "prod-a1-private-product-evidence-surface-seed",
        "sdk-a8-private-sdk-smoke-chain-pause-or-docs-selector",
    ]:
        raise ValueError("PROD-A7 must consume PROD-A1 and SDK-A8")
    summary = payload["summary"]
    if summary["selectedLaneId"] != "eml_compiler_plugin":
        raise ValueError("compiler-plugin lane should be selected")
    if summary["selectedNextArtifact"] != "CPG-A1 private compiler-plugin guard-note packet":
        raise ValueError("unexpected next artifact")
    if summary["sdkSmokeLanePaused"] is not True:
        raise ValueError("SDK smoke lane must be paused before returning to roadmap")
    for key in [
        "compilerPluginImplemented",
        "compilerPluginGuardNoteCreated",
        "publicReadinessClaim",
        "compilerCorrectnessClaim",
        "semanticPreservationClaim",
        "runtimePerformanceClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    actions = payload["candidateLaneActions"]
    if sum(1 for action in actions if action["decision"] == "selected") != 1:
        raise ValueError("exactly one lane must be selected")
    decisions = {action["laneId"]: action["decision"] for action in actions}
    if decisions["monogate_sdk"] != "paused_as_seeded":
        raise ValueError("SDK lane must remain paused")
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
        source=f"python/results/prod_a7_private_product_roadmap_return_selector/prod_a7_private_product_roadmap_return_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="prod_a7_private_product_roadmap_return_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Create CPG-A1 private compiler-plugin guard-note packet.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifacts": payload["sourceArtifacts"],
            "selectedLaneId": payload["summary"]["selectedLaneId"],
            "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
            "compilerCorrectnessClaim": payload["summary"]["compilerCorrectnessClaim"],
            "publicReadinessClaim": payload["summary"]["publicReadinessClaim"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="PROD-A7 Private Product Roadmap Return Selector",
        status=payload["status"],
        summary_rows=[
            ("source artifacts", ", ".join(payload["sourceArtifacts"])),
            ("selected lane", payload["summary"]["selectedLaneId"]),
            ("selected next artifact", payload["summary"]["selectedNextArtifact"]),
            ("compiler correctness claim", payload["summary"]["compilerCorrectnessClaim"]),
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
    result_path = out_dir / f"prod_a7_private_product_roadmap_return_selector_{STAMP}.json"
    report_path = report_dir / f"prod_a7_private_product_roadmap_return_selector_{STAMP}.md"
    evidence_path = evidence_dir / "prod_a7_private_product_roadmap_return_selector.json"
    feed_path = command_feed_dir / f"prod_a7_private_product_roadmap_return_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/prod_a7_private_product_roadmap_return_selector")
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
    print("PROD_A7_PRIVATE_PRODUCT_ROADMAP_RETURN_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
