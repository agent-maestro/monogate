#!/usr/bin/env python3
"""EH-A6 private health digest post-training-cost-hold refresh."""

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

from scripts import prod_a21_training_cost_estimator_skeleton_hold_digest as prod_a21  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-08"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_health_digest_post_training_cost_hold_refresh.v0"
STATUS = "EH_A6_PRIVATE_HEALTH_DIGEST_POST_TRAINING_COST_HOLD_REFRESH_PASS"
ARTIFACT_ID = "eh-a6-private-health-digest-post-training-cost-hold-refresh"
NEXT_RECOMMENDED_ARTIFACT = (
    "choose an explicit non-held implementation/intake lane; do not continue training-cost estimator work by default"
)

TRUE_CLAIM_FLAGS = {
    "eh_a5_consumed",
    "prod_a21_consumed",
    "post_training_cost_hold_digest_created",
    "held_lanes_recorded",
    "private_only_refresh",
    "training_cost_hold_recorded",
    "public_promotion_blocked",
    "runtime_claims_blocked",
}

CLAIM_FLAGS = {
    "eh_a5_consumed": True,
    "prod_a21_consumed": True,
    "post_training_cost_hold_digest_created": True,
    "held_lanes_recorded": True,
    "private_only_refresh": True,
    "training_cost_hold_recorded": True,
    "public_promotion_blocked": True,
    "runtime_claims_blocked": True,
    "dashboard_ui_created": False,
    "public_dashboard_created": False,
    "public_readiness_claim": False,
    "public_copy_approved": False,
    "public_surface_updated": False,
    "renderer_correctness_claim": False,
    "visualization_quality_claim": False,
    "compiler_correctness_claim": False,
    "runtime_performance_claim": False,
    "training_savings_claim": False,
    "estimator_accuracy_claim": False,
    "hardware_readiness_claim": False,
    "silicon_readiness_claim": False,
    "electronics_repo_touched": False,
    "laptop_owned_repo_touched": False,
    "d110_started": False,
    "reviewer_response_consumed": False,
    "reviewer_approval_recorded": False,
    "atlas_public_promotion": False,
    "atlas_catalog_completeness_claim": False,
    "public_math_promotion": False,
    "sdk_compiler_docs_created": False,
    "course_material_created": False,
    "product_implementation_started": False,
    "training_cost_estimator_reopened": False,
    "training_cost_estimator_implemented": False,
    "estimate_values_produced": False,
    "health_report_completeness_claim": False,
    "external_source_checked": False,
    "broad_eml_advantage_claim": False,
}

NON_CLAIMS = [
    "EH-A6 refreshes a private health digest after the PROD-A21 training-cost hold; it is not a complete ecosystem auditor or dashboard.",
    "EH-A6 does not publish, approve public copy, update public/dev surfaces, create SDK/course material, or start product implementation.",
    "EH-A6 does not reopen the training-cost estimator lane, implement or execute an estimator, produce estimate values, or claim savings, accuracy, runtime performance, SDK stability, compiler correctness, hardware readiness, silicon readiness, public readiness, or broad EML advantage.",
    "EH-A6 does not consume reviewer response text, record reviewer approval, start D110, edit MachLib, run Lean, change runtime lowering, or touch laptop-owned repositories.",
]


def load_eh_a5_result() -> dict[str, Any]:
    path = (
        ROOT
        / "python/results/eh_a5_private_health_digest_post_atlas_hold_refresh"
        / f"eh_a5_private_health_digest_post_atlas_hold_refresh_{STAMP}.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload["artifactId"] != "eh-a5-private-health-digest-post-atlas-hold-refresh":
        raise ValueError("EH-A6 must consume EH-A5")
    if payload["summary"]["digestVisibility"] != "private":
        raise ValueError("EH-A5 digest must be private")
    if payload["summary"]["productRoadmapPaused"] is not True:
        raise ValueError("EH-A5 product roadmap must be paused")
    return payload


def load_prod_a21_result() -> dict[str, Any]:
    path = (
        ROOT
        / "python/results/prod_a21_training_cost_estimator_skeleton_hold_digest"
        / f"prod_a21_training_cost_estimator_skeleton_hold_digest_{STAMP}.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    prod_a21.validate_payload(payload)
    return payload


def refreshed_lane_rows(eh_a5_payload: dict[str, Any], prod_a21_payload: dict[str, Any]) -> list[dict[str, Any]]:
    prior_rows = {row["laneId"]: row for row in eh_a5_payload["refreshedLaneRows"]}
    return [
        {
            "laneId": "private-atlas-v0",
            "status": prior_rows["private-atlas-v0"]["status"],
            "currentArtifact": prior_rows["private-atlas-v0"]["currentArtifact"],
            "nextAction": prior_rows["private-atlas-v0"]["nextAction"],
        },
        {
            "laneId": "public-math",
            "status": prior_rows["public-math"]["status"],
            "currentArtifact": prior_rows["public-math"]["currentArtifact"],
            "nextAction": prior_rows["public-math"]["nextAction"],
        },
        {
            "laneId": "training-cost-estimator",
            "status": "held_by_prod_a21",
            "currentArtifact": prod_a21_payload["artifactId"],
            "nextAction": prod_a21_payload["summary"]["nextRecommendedArtifact"],
        },
        {
            "laneId": "product-roadmap",
            "status": "paused_with_training_cost_held",
            "currentArtifact": "PROD-A21 private training-cost estimator skeleton hold digest",
            "nextAction": "Resume only by explicit bounded non-held lane request, reviewer response, or concrete laptop/electronics artifact.",
        },
        {
            "laneId": "ecosystem-health",
            "status": "refreshed_after_training_cost_hold",
            "currentArtifact": ARTIFACT_ID,
            "nextAction": "Use this digest to choose an explicit non-held implementation/intake lane.",
        },
        {
            "laneId": "laptop-electronics",
            "status": prior_rows["laptop-electronics"]["status"],
            "currentArtifact": prior_rows["laptop-electronics"]["currentArtifact"],
            "nextAction": prior_rows["laptop-electronics"]["nextAction"],
        },
    ]


def build_payload() -> dict[str, Any]:
    eh_a5_payload = load_eh_a5_result()
    prod_a21_payload = load_prod_a21_result()
    lanes = refreshed_lane_rows(eh_a5_payload, prod_a21_payload)
    held_lanes = [lane for lane in lanes if lane["status"].startswith(("held", "paused"))]
    summary = {
        "sourceHealthArtifact": eh_a5_payload["artifactId"],
        "sourceTrainingCostArtifact": prod_a21_payload["artifactId"],
        "postTrainingCostHoldDigestCreated": True,
        "digestVisibility": "private",
        "laneRowCount": len(lanes),
        "heldLaneCount": len(held_lanes),
        "atlasHeld": True,
        "publicMathHeld": True,
        "trainingCostEstimatorHeld": True,
        "productRoadmapPaused": True,
        "privateOnlyRefresh": True,
        "dashboardUiCreated": False,
        "publicSurfaceUpdated": False,
        "reviewerResponseConsumed": False,
        "reviewerApprovalRecorded": False,
        "d110Started": False,
        "trainingCostEstimatorReopened": False,
        "laptopOwnedRepoTouched": False,
        "nextRecommendedArtifact": NEXT_RECOMMENDED_ARTIFACT,
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id=ARTIFACT_ID,
        artifact_type="private_health_digest_post_training_cost_hold_refresh",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceHealthArtifact": eh_a5_payload["artifactId"],
            "sourceTrainingCostArtifact": prod_a21_payload["artifactId"],
            "refreshedLaneRows": lanes,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceHealthArtifact"] != "eh-a5-private-health-digest-post-atlas-hold-refresh":
        raise ValueError("EH-A6 must consume EH-A5")
    if payload["sourceTrainingCostArtifact"] != "prod-a21-training-cost-estimator-skeleton-hold-digest":
        raise ValueError("EH-A6 must consume PROD-A21")
    summary = payload["summary"]
    if summary["laneRowCount"] != 6:
        raise ValueError("lane row count drift")
    if summary["heldLaneCount"] < 4:
        raise ValueError("expected held lanes to be recorded")
    for key in [
        "postTrainingCostHoldDigestCreated",
        "atlasHeld",
        "publicMathHeld",
        "trainingCostEstimatorHeld",
        "productRoadmapPaused",
        "privateOnlyRefresh",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "dashboardUiCreated",
        "publicSurfaceUpdated",
        "reviewerResponseConsumed",
        "reviewerApprovalRecorded",
        "d110Started",
        "trainingCostEstimatorReopened",
        "laptopOwnedRepoTouched",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    lanes = {lane["laneId"]: lane for lane in payload["refreshedLaneRows"]}
    if lanes["training-cost-estimator"]["status"] != "held_by_prod_a21":
        raise ValueError("training-cost estimator lane must remain held")
    if lanes["product-roadmap"]["status"] != "paused_with_training_cost_held":
        raise ValueError("product roadmap must remain paused with training-cost held")
    if lanes["private-atlas-v0"]["status"] != "held_pending_reviewer_response_or_explicit_redirect":
        raise ValueError("Atlas lane must remain held")
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
        semantic_strength="private_health_digest_refresh_after_training_cost_hold_no_public_dashboard_or_completeness_claim",
        source=f"python/results/eh_a6_private_health_digest_post_training_cost_hold_refresh/eh_a6_private_health_digest_post_training_cost_hold_refresh_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="eh_a6_private_health_digest_post_training_cost_hold_refresh_feed",
        date=DATE,
        status=payload["status"],
        next_action="Choose an explicit non-held implementation/intake lane; do not continue training-cost estimator work by default.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceHealthArtifact": payload["sourceHealthArtifact"],
            "sourceTrainingCostArtifact": payload["sourceTrainingCostArtifact"],
            "digestVisibility": payload["summary"]["digestVisibility"],
            "laneRowCount": payload["summary"]["laneRowCount"],
            "heldLaneCount": payload["summary"]["heldLaneCount"],
            "trainingCostEstimatorHeld": payload["summary"]["trainingCostEstimatorHeld"],
            "productRoadmapPaused": payload["summary"]["productRoadmapPaused"],
            "trainingCostEstimatorReopened": payload["summary"]["trainingCostEstimatorReopened"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="EH-A6 Private Health Digest Post-Training-Cost-Hold Refresh",
        status=payload["status"],
        summary_rows=[
            ("source health artifact", payload["sourceHealthArtifact"]),
            ("source training-cost artifact", payload["sourceTrainingCostArtifact"]),
            ("digest visibility", payload["summary"]["digestVisibility"]),
            ("lane rows", payload["summary"]["laneRowCount"]),
            ("held lanes", payload["summary"]["heldLaneCount"]),
            ("training-cost estimator held", payload["summary"]["trainingCostEstimatorHeld"]),
            ("product roadmap paused", payload["summary"]["productRoadmapPaused"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Refreshed Lane Rows",
                [
                    f"- `{lane['laneId']}`: `{lane['status']}`; next: {lane['nextAction']}"
                    for lane in payload["refreshedLaneRows"]
                ],
            ),
            (
                "Blocked Follow-Ups",
                [
                    "- no public dashboard or public surface",
                    "- no reviewer approval or reviewer response consumption",
                    "- no training-cost estimator reopening by default",
                    "- no SDK/course/product implementation",
                    "- no runtime, compiler, hardware, silicon, or broad EML advantage claim",
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
    result_path = out_dir / f"eh_a6_private_health_digest_post_training_cost_hold_refresh_{STAMP}.json"
    report_path = report_dir / f"eh_a6_private_health_digest_post_training_cost_hold_refresh_{STAMP}.md"
    evidence_path = evidence_dir / "eh_a6_private_health_digest_post_training_cost_hold_refresh.json"
    feed_path = command_feed_dir / f"eh_a6_private_health_digest_post_training_cost_hold_refresh_feed_{STAMP}.json"
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
        "--out-dir",
        type=Path,
        default=ROOT / "python/results/eh_a6_private_health_digest_post_training_cost_hold_refresh",
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
    print("EH_A6_PRIVATE_HEALTH_DIGEST_POST_TRAINING_COST_HOLD_REFRESH_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
