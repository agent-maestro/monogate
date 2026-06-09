#!/usr/bin/env python3
"""EH-A5 private health digest post-Atlas-hold refresh."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

sys.setrecursionlimit(10000)

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import atlas_a51_private_atlas_reviewer_response_hold_selector as atlas_a51  # noqa: E402
from scripts import eh_a4_private_ecosystem_health_digest_export_or_pause_selector as eh_a4  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    assert_claim_flags_bounded,
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-08"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_health_digest_post_atlas_hold_refresh.v0"
STATUS = "EH_A5_PRIVATE_HEALTH_DIGEST_POST_ATLAS_HOLD_REFRESH_PASS"
ARTIFACT_ID = "eh-a5-private-health-digest-post-atlas-hold-refresh"
NEXT_RECOMMENDED_ARTIFACT = "hold private Atlas/public-math lanes or proceed only by explicit product/tooling redirect"

TRUE_CLAIM_FLAGS = {
    "eh_a4_consumed",
    "atlas_a51_consumed",
    "post_atlas_hold_digest_created",
    "held_lanes_recorded",
    "private_only_refresh",
    "public_promotion_blocked",
    "runtime_claims_blocked",
}

CLAIM_FLAGS = {
    "eh_a4_consumed": True,
    "atlas_a51_consumed": True,
    "post_atlas_hold_digest_created": True,
    "held_lanes_recorded": True,
    "private_only_refresh": True,
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
    "broad_eml_advantage_claim": False,
    "health_report_completeness_claim": False,
    "external_source_checked": False,
}

NON_CLAIMS = [
    "EH-A5 refreshes a private health digest after the ATLAS-A51 hold; it is not a complete ecosystem auditor or dashboard.",
    "EH-A5 does not publish, approve public copy, update public/dev surfaces, create SDK/course material, or start product implementation.",
    "EH-A5 does not claim public readiness, renderer correctness, visualization quality, compiler correctness, runtime performance, training savings, estimator accuracy, hardware readiness, silicon readiness, catalog completeness, or broad EML advantage.",
    "EH-A5 does not consume reviewer response text, record reviewer approval, start D110, edit MachLib, run Lean, change runtime lowering, or touch laptop-owned repositories.",
]


def refreshed_lane_rows(eh_payload: dict[str, Any], atlas_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        {
            "laneId": "private-atlas-v0",
            "status": "held_pending_reviewer_response_or_explicit_redirect",
            "currentArtifact": atlas_payload["artifactId"],
            "nextAction": atlas_payload["summary"]["nextRecommendedArtifact"],
        },
        {
            "laneId": "public-math",
            "status": "held_pending_human_review_decision",
            "currentArtifact": "PUBMATH-A6 no-review-response hold selector",
            "nextAction": "Resume only with actual human review decision or explicit private-lane redirect.",
        },
        {
            "laneId": "product-roadmap",
            "status": "paused_by_prod_a10",
            "currentArtifact": "PROD-A10 private product roadmap pause digest",
            "nextAction": "Resume only for explicit bounded product request, real reviewer response, or concrete laptop/electronics artifact.",
        },
        {
            "laneId": "ecosystem-health",
            "status": "refreshed_after_atlas_hold",
            "currentArtifact": eh_payload["artifactId"],
            "nextAction": "Do not create more health governance by default; use this digest to choose a real implementation or intake lane.",
        },
        {
            "laneId": "laptop-electronics",
            "status": "owner_boundary_active",
            "currentArtifact": "laptop-agent-owned electronics/course work",
            "nextAction": "Research side receives packets only through claim-bounded bridge artifacts.",
        },
    ]
    return rows


def build_payload() -> dict[str, Any]:
    eh_payload = eh_a4.build_payload()
    eh_a4.validate_payload(eh_payload)
    atlas_payload = atlas_a51.build_payload(
        ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json",
        ROOT.parent / "machlib",
    )
    atlas_a51.validate_payload(atlas_payload)
    lanes = refreshed_lane_rows(eh_payload, atlas_payload)
    held_lanes = [lane for lane in lanes if lane["status"].startswith("held") or lane["status"].startswith("paused")]
    summary = {
        "sourceEcosystemHealthArtifact": eh_payload["artifactId"],
        "sourceAtlasArtifact": atlas_payload["artifactId"],
        "postAtlasHoldDigestCreated": True,
        "digestVisibility": "private",
        "laneRowCount": len(lanes),
        "heldLaneCount": len(held_lanes),
        "atlasHeld": True,
        "publicMathHeld": True,
        "productRoadmapPaused": True,
        "privateOnlyRefresh": True,
        "dashboardUiCreated": False,
        "publicSurfaceUpdated": False,
        "reviewerResponseConsumed": False,
        "reviewerApprovalRecorded": False,
        "d110Started": False,
        "laptopOwnedRepoTouched": False,
        "nextRecommendedArtifact": NEXT_RECOMMENDED_ARTIFACT,
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id=ARTIFACT_ID,
        artifact_type="private_health_digest_post_atlas_hold_refresh",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceEcosystemHealthArtifact": eh_payload["artifactId"],
            "sourceAtlasArtifact": atlas_payload["artifactId"],
            "refreshedLaneRows": lanes,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    assert_claim_flags_bounded(CLAIM_FLAGS, TRUE_CLAIM_FLAGS)
    assert_claim_flags_bounded(payload["claimFlags"], TRUE_CLAIM_FLAGS)
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    if payload["sourceEcosystemHealthArtifact"] != "eh-a4-private-ecosystem-health-digest-export-or-pause-selector":
        raise ValueError("EH-A5 must consume EH-A4")
    if payload["sourceAtlasArtifact"] != "atlas-a51-private-atlas-reviewer-response-hold-selector":
        raise ValueError("EH-A5 must consume ATLAS-A51")
    if summary["laneRowCount"] != 5:
        raise ValueError("lane row count drift")
    if summary["heldLaneCount"] < 3:
        raise ValueError("expected held lanes to be recorded")
    for key in [
        "postAtlasHoldDigestCreated",
        "atlasHeld",
        "publicMathHeld",
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
        "laptopOwnedRepoTouched",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    lanes = {lane["laneId"]: lane for lane in payload["refreshedLaneRows"]}
    if lanes["private-atlas-v0"]["status"] != "held_pending_reviewer_response_or_explicit_redirect":
        raise ValueError("Atlas lane must remain held")
    if lanes["public-math"]["status"] != "held_pending_human_review_decision":
        raise ValueError("public-math lane must remain held")
    if lanes["product-roadmap"]["status"] != "paused_by_prod_a10":
        raise ValueError("product roadmap must remain paused")
    for key in set(CLAIM_FLAGS) - TRUE_CLAIM_FLAGS:
        if payload["claimFlags"][key] is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return build_evidence_packet(
        artifact_id=payload["artifactId"],
        artifact_type=payload["artifactType"],
        semantic_strength="private_health_digest_refresh_after_atlas_hold_no_public_dashboard_or_completeness_claim",
        source=f"python/results/eh_a5_private_health_digest_post_atlas_hold_refresh/eh_a5_private_health_digest_post_atlas_hold_refresh_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="eh_a5_private_health_digest_post_atlas_hold_refresh_feed",
        date=DATE,
        status=payload["status"],
        next_action="Use the private digest to choose an explicit implementation/intake lane; do not create more Atlas/public-math review packets without reviewer response or explicit redirect.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceEcosystemHealthArtifact": payload["sourceEcosystemHealthArtifact"],
            "sourceAtlasArtifact": payload["sourceAtlasArtifact"],
            "digestVisibility": payload["summary"]["digestVisibility"],
            "laneRowCount": payload["summary"]["laneRowCount"],
            "heldLaneCount": payload["summary"]["heldLaneCount"],
            "atlasHeld": payload["summary"]["atlasHeld"],
            "publicMathHeld": payload["summary"]["publicMathHeld"],
            "productRoadmapPaused": payload["summary"]["productRoadmapPaused"],
            "publicSurfaceUpdated": payload["summary"]["publicSurfaceUpdated"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    lane_lines = [
        f"- `{lane['laneId']}`: `{lane['status']}`; next: {lane['nextAction']}"
        for lane in payload["refreshedLaneRows"]
    ]
    return render_markdown_report(
        title="EH-A5 Private Health Digest Post-Atlas-Hold Refresh",
        status=payload["status"],
        summary_rows=[
            ("source ecosystem health artifact", payload["sourceEcosystemHealthArtifact"]),
            ("source Atlas artifact", payload["sourceAtlasArtifact"]),
            ("digest visibility", payload["summary"]["digestVisibility"]),
            ("lane rows", payload["summary"]["laneRowCount"]),
            ("held lanes", payload["summary"]["heldLaneCount"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            ("Refreshed Lane Rows", lane_lines),
            (
                "Blocked Follow-Ups",
                [
                    "- no public dashboard or public surface",
                    "- no reviewer approval or reviewer response consumption",
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
    result_path = out_dir / f"eh_a5_private_health_digest_post_atlas_hold_refresh_{STAMP}.json"
    report_path = report_dir / f"eh_a5_private_health_digest_post_atlas_hold_refresh_{STAMP}.md"
    evidence_path = evidence_dir / "eh_a5_private_health_digest_post_atlas_hold_refresh.json"
    feed_path = command_feed_dir / f"eh_a5_private_health_digest_post_atlas_hold_refresh_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eh_a5_private_health_digest_post_atlas_hold_refresh")
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
    print("EH_A5_PRIVATE_HEALTH_DIGEST_POST_ATLAS_HOLD_REFRESH_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
