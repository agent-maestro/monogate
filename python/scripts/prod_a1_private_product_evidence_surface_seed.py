#!/usr/bin/env python3
"""PROD-A1 private product evidence surface seed."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_product_evidence_surface_seed.v0"
STATUS = "PROD_A1_PRIVATE_PRODUCT_EVIDENCE_SURFACE_SEED_PASS"

LANE_IDS = {
    "monogate_sdk",
    "eml_compiler_plugin",
    "training_cost_estimator",
    "eml_ip_core_license",
    "eml_accelerator_card",
    "pinn_advisor",
}

TRUE_CLAIM_FLAGS = {
    "private_product_surface_seed_created",
    "six_product_lanes_mapped",
    "d109_hold_respected",
    "public_claims_blocked",
}

CLAIM_FLAGS = {
    "private_product_surface_seed_created": True,
    "six_product_lanes_mapped": True,
    "d109_hold_respected": True,
    "public_claims_blocked": True,
    "public_product_ready": False,
    "public_launch_copy_approved": False,
    "sdk_stability_claim": False,
    "compiler_plugin_implemented": False,
    "compiler_correctness_claim": False,
    "semantic_preservation_claim": False,
    "training_cost_estimator_implemented": False,
    "training_savings_claim": False,
    "runtime_performance_claim": False,
    "pinn_advisor_implemented": False,
    "scientific_correctness_claim": False,
    "ip_license_terms_finalized": False,
    "hardware_core_implemented": False,
    "hardware_capture_consumed": False,
    "accelerator_card_ready": False,
    "silicon_readiness_claim": False,
    "electronics_repo_touched": False,
    "laptop_owned_repo_touched": False,
    "d110_started": False,
    "reviewer_response_consumed": False,
    "reviewer_approval_recorded": False,
    "broad_eml_advantage_claim": False,
}

NON_CLAIMS = [
    "PROD-A1 is a private product evidence surface seed, not a public product page.",
    "PROD-A1 maps candidate product lanes and next private artifacts; it does not implement an SDK, compiler plugin, estimator, PINN advisor, IP license, hardware core, or accelerator card.",
    "PROD-A1 does not claim public readiness, compiler correctness, semantic preservation, runtime performance, training savings, scientific correctness, hardware readiness, silicon readiness, reviewer approval, or broad EML advantage.",
    "PROD-A1 respects the D109 hold and does not start D110 or consume a reviewer response.",
]


def product_lanes() -> list[dict[str, Any]]:
    return [
        {
            "laneId": "monogate_sdk",
            "displayName": "Monogate SDK",
            "currentPosture": "candidate_umbrella_private_inventory_needed",
            "existingEvidence": [
                "monogate package surfaces",
                "eml-cost package history",
                "evidence SDK examples",
                "D-series evidence packets",
            ],
            "nextPrivateArtifact": "SDK surface inventory: stable, experimental, private, and blocked APIs",
            "reviewerQuestion": "What does SDK mean in terms of import paths, commands, schemas, and examples?",
            "dependencies": ["package inventory", "evidence packet schema inventory"],
            "ownerBoundary": "research_tooling_product_side",
            "blockedPublicClaims": [
                "SDK stability",
                "public readiness",
                "complete API coverage",
                "compiler correctness",
            ],
        },
        {
            "laneId": "eml_compiler_plugin",
            "displayName": "EML compiler plugin",
            "currentPosture": "advisory_guard_note_before_compiler_promises",
            "existingEvidence": ["eml-cost", "eml-rewrite", "eml-lint plan", "Forge/eFrog private lanes"],
            "nextPrivateArtifact": "Compiler-plugin guard-note packet: lint/advice boundary versus compile/proof boundary",
            "reviewerQuestion": "Which findings are advisory, and which claims remain blocked?",
            "dependencies": ["eml-cost surface", "eml-rewrite surface", "compiler non-claim language"],
            "ownerBoundary": "research_tooling_product_side",
            "blockedPublicClaims": [
                "compiler correctness",
                "semantic preservation",
                "automatic lowering safety",
                "runtime performance",
            ],
        },
        {
            "laneId": "training_cost_estimator",
            "displayName": "Training cost estimator",
            "currentPosture": "strongest_near_term_private_spec_candidate",
            "existingEvidence": [
                "eml-cost",
                "eml-cost-torch",
                "MNIST cost recomputation",
                "PyTorch profiler history",
            ],
            "nextPrivateArtifact": "Private estimator spec: inputs, output schema, calibration caveats, examples",
            "reviewerQuestion": "What can be estimated honestly without promising savings or accuracy?",
            "dependencies": ["cost model inventory", "calibration caveat inventory", "example model fixtures"],
            "ownerBoundary": "research_tooling_product_side",
            "blockedPublicClaims": [
                "guaranteed training cost savings",
                "runtime acceleration",
                "model quality improvement",
                "estimator accuracy guarantee",
            ],
        },
        {
            "laneId": "eml_ip_core_license",
            "displayName": "EML IP core license",
            "currentPosture": "license_scope_memo_only_until_hardware_evidence_exists",
            "existingEvidence": ["hardware roadmap", "FPGA EML core concept", "bounded witness discipline"],
            "nextPrivateArtifact": "License-scope memo: evaluation-only terms, excluded claims, provenance obligations",
            "reviewerQuestion": "What can be licensed as evaluation scope before any hardware readiness claim?",
            "dependencies": ["future hardware capture", "fixed-point core smoke evidence", "legal review"],
            "ownerBoundary": "research_product_only_no_laptop_repo_touch",
            "blockedPublicClaims": [
                "IP license readiness",
                "hardware core readiness",
                "silicon readiness",
                "performance guarantee",
            ],
        },
        {
            "laneId": "eml_accelerator_card",
            "displayName": "EML accelerator card",
            "currentPosture": "long_horizon_dependency_ladder_only",
            "existingEvidence": ["Arty A7/DGX bridge roadmap", "FPGA EML core concept"],
            "nextPrivateArtifact": "Dependency ladder: Arty proof-of-life, fixed-point smoke, capture packet, card feasibility",
            "reviewerQuestion": "Which prerequisite evidence must exist before card feasibility is meaningful?",
            "dependencies": ["Arty proof-of-life", "fixed-point evaluator", "capture protocol", "bounded performance protocol"],
            "ownerBoundary": "research_product_only_no_laptop_repo_touch",
            "blockedPublicClaims": [
                "accelerator card readiness",
                "hardware readiness",
                "silicon readiness",
                "runtime performance",
            ],
        },
        {
            "laneId": "pinn_advisor",
            "displayName": "PINN advisor",
            "currentPosture": "diagnostic_concept_downstream_of_cost_estimator",
            "existingEvidence": ["eml-cost-torch", "PINN experiments", "training-cost artifacts"],
            "nextPrivateArtifact": "PINN advisor brief: inputs, diagnostics, caveats, examples, blocked claims",
            "reviewerQuestion": "Which PINN diagnostics are useful as advice without claiming scientific correctness?",
            "dependencies": ["training cost estimator spec", "PINN example inventory", "calibration caveats"],
            "ownerBoundary": "research_tooling_product_side",
            "blockedPublicClaims": [
                "scientific correctness",
                "training improvement",
                "runtime performance",
                "automatic solver quality",
            ],
        },
    ]


def build_payload() -> dict[str, Any]:
    lanes = product_lanes()
    summary = {
        "laneCount": len(lanes),
        "laneIds": [lane["laneId"] for lane in lanes],
        "nextRecommendedArtifact": "PROD-A2 training cost estimator private spec",
        "d109HoldRespected": True,
        "d110Started": False,
        "reviewerResponseConsumed": False,
        "publicProductReady": False,
        "publicLaunchCopyApproved": False,
        "compilerCorrectnessClaim": False,
        "runtimePerformanceClaim": False,
        "hardwareReadinessClaim": False,
        "siliconReadinessClaim": False,
        "trainingSavingsClaim": False,
        "broadEmlAdvantageClaim": False,
        "claimFlagsBounded": all(CLAIM_FLAGS[key] is True for key in TRUE_CLAIM_FLAGS)
        and all(value is False for key, value in CLAIM_FLAGS.items() if key not in TRUE_CLAIM_FLAGS),
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="prod-a1-private-product-evidence-surface-seed",
        artifact_type="private_product_evidence_surface_seed",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceOverlay": "monogate-research/roadmap/product-roadmap-current-readiness-overlay.md",
            "productLanes": lanes,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    lanes = payload["productLanes"]
    lane_ids = {lane["laneId"] for lane in lanes}
    if lane_ids != LANE_IDS:
        raise ValueError("product lane drift")
    if payload["summary"]["laneCount"] != 6:
        raise ValueError("expected six product lanes")
    for lane in lanes:
        if not lane["nextPrivateArtifact"]:
            raise ValueError(f"{lane['laneId']} missing next private artifact")
        if len(lane["blockedPublicClaims"]) < 4:
            raise ValueError(f"{lane['laneId']} has too few blocked claims")
    for key in [
        "d109HoldRespected",
        "claimFlagsBounded",
    ]:
        if payload["summary"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "d110Started",
        "reviewerResponseConsumed",
        "publicProductReady",
        "publicLaunchCopyApproved",
        "compilerCorrectnessClaim",
        "runtimePerformanceClaim",
        "hardwareReadinessClaim",
        "siliconReadinessClaim",
        "trainingSavingsClaim",
        "broadEmlAdvantageClaim",
    ]:
        if payload["summary"][key] is not False:
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
        artifact_type="private_product_evidence_surface_seed",
        semantic_strength="private_product_lane_mapping_no_public_readiness_no_implementation",
        source=f"python/results/prod_a1_private_product_evidence_surface_seed/prod_a1_private_product_evidence_surface_seed_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="prod_a1_private_product_evidence_surface_seed_feed",
        date=DATE,
        status=payload["status"],
        next_action="Create PROD-A2 training cost estimator private spec, or hold if product work is paused.",
        claim_flags=payload["claimFlags"],
        fields={
            "laneCount": payload["summary"]["laneCount"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
            "d109HoldRespected": payload["summary"]["d109HoldRespected"],
            "publicProductReady": payload["summary"]["publicProductReady"],
            "compilerCorrectnessClaim": payload["summary"]["compilerCorrectnessClaim"],
            "runtimePerformanceClaim": payload["summary"]["runtimePerformanceClaim"],
            "hardwareReadinessClaim": payload["summary"]["hardwareReadinessClaim"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    lane_lines = ["| Lane | Current posture | Next private artifact |", "|---|---|---|"]
    for lane in payload["productLanes"]:
        lane_lines.append(f"| `{lane['laneId']}` | `{lane['currentPosture']}` | {lane['nextPrivateArtifact']} |")
    return render_markdown_report(
        title="PROD-A1 Private Product Evidence Surface Seed",
        status=payload["status"],
        summary_rows=[
            ("lane count", payload["summary"]["laneCount"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
            ("D109 hold respected", payload["summary"]["d109HoldRespected"]),
            ("D110 started", payload["summary"]["d110Started"]),
            ("public product ready", payload["summary"]["publicProductReady"]),
            ("compiler correctness claim", payload["summary"]["compilerCorrectnessClaim"]),
            ("runtime performance claim", payload["summary"]["runtimePerformanceClaim"]),
            ("hardware readiness claim", payload["summary"]["hardwareReadinessClaim"]),
        ],
        sections=[("Product Lanes", lane_lines)],
        non_claims=payload["nonClaims"],
    )


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"prod_a1_private_product_evidence_surface_seed_{STAMP}.json"
    report_path = report_dir / f"prod_a1_private_product_evidence_surface_seed_{STAMP}.md"
    evidence_path = evidence_dir / "prod_a1_private_product_evidence_surface_seed.json"
    feed_path = command_feed_dir / f"prod_a1_private_product_evidence_surface_seed_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/prod_a1_private_product_evidence_surface_seed")
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
    print("PROD_A1_PRIVATE_PRODUCT_EVIDENCE_SURFACE_SEED_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
