#!/usr/bin/env python3
"""EH-A7 private command-feed lane-state aggregation."""

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

from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-08"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_command_feed_lane_state_aggregation.v0"
STATUS = "EH_A7_PRIVATE_COMMAND_FEED_LANE_STATE_AGGREGATION_PASS"
ARTIFACT_ID = "eh-a7-private-command-feed-lane-state-aggregation"
NEXT_RECOMMENDED_ARTIFACT = (
    "use the aggregated lane states to choose one explicit non-held implementation/intake lane"
)

SOURCE_FEEDS = [
    {
        "laneId": "ecosystem-health",
        "path": ROOT
        / "command_center_feeds/eh_a6_private_health_digest_post_training_cost_hold_refresh_feed_2026_06_08.json",
        "expectedFeedId": "eh_a6_private_health_digest_post_training_cost_hold_refresh_feed",
    },
    {
        "laneId": "training-cost-estimator",
        "path": ROOT
        / "command_center_feeds/prod_a21_training_cost_estimator_skeleton_hold_digest_feed_2026_06_08.json",
        "expectedFeedId": "prod_a21_training_cost_estimator_skeleton_hold_digest_feed",
    },
    {
        "laneId": "private-atlas-v0",
        "path": ROOT
        / "command_center_feeds/atlas_a51_private_atlas_reviewer_response_hold_selector_feed_2026_06_08.json",
        "expectedFeedId": "atlas_a51_private_atlas_reviewer_response_hold_selector_feed",
    },
    {
        "laneId": "public-math-review",
        "path": ROOT
        / "command_center_feeds/eml_d109_private_reviewer_response_availability_guard_feed_2026_06_06.json",
        "expectedFeedId": "eml_d109_private_reviewer_response_availability_guard_feed",
    },
    {
        "laneId": "product-roadmap",
        "path": ROOT / "command_center_feeds/prod_a10_private_product_roadmap_pause_digest_feed_2026_06_06.json",
        "expectedFeedId": "prod_a10_private_product_roadmap_pause_digest_feed",
    },
    {
        "laneId": "electronics-inbox",
        "path": ROOT
        / "command_center_feeds/ee_bridge_a4_electronics_artifact_inbox_gate_feed_2026_06_01.json",
        "expectedFeedId": "ee_bridge_a4_electronics_artifact_inbox_gate_feed",
    },
    {
        "laneId": "electronics-guard",
        "path": ROOT
        / "command_center_feeds/ee_bridge_a6_electronics_bridge_regression_guard_feed_2026_06_01.json",
        "expectedFeedId": "ee_bridge_a6_electronics_bridge_regression_guard_feed",
    },
]

TRUE_CLAIM_FLAGS = {
    "eh_a6_feed_consumed",
    "selected_command_feeds_loaded",
    "lane_state_rows_aggregated",
    "held_and_paused_states_recorded",
    "private_only_aggregation",
    "public_surface_blocked",
    "next_action_recorded",
}

CLAIM_FLAGS = {
    "eh_a6_feed_consumed": True,
    "selected_command_feeds_loaded": True,
    "lane_state_rows_aggregated": True,
    "held_and_paused_states_recorded": True,
    "private_only_aggregation": True,
    "public_surface_blocked": True,
    "next_action_recorded": True,
    "all_feeds_scanned": False,
    "dashboard_ui_created": False,
    "public_dashboard_created": False,
    "public_surface_updated": False,
    "renderer_correctness_claim": False,
    "visualization_quality_claim": False,
    "health_report_completeness_claim": False,
    "external_source_checked": False,
    "training_cost_estimator_reopened": False,
    "training_cost_estimator_implemented": False,
    "estimate_values_produced": False,
    "training_savings_claim": False,
    "estimator_accuracy_claim": False,
    "product_implementation_started": False,
    "public_readiness_claim": False,
    "public_copy_approved": False,
    "sdk_compiler_docs_created": False,
    "course_material_created": False,
    "reviewer_response_consumed": False,
    "reviewer_approval_recorded": False,
    "d110_started": False,
    "atlas_public_promotion": False,
    "atlas_catalog_completeness_claim": False,
    "public_math_promotion": False,
    "laptop_artifact_consumed": False,
    "electronics_repo_touched": False,
    "laptop_owned_repo_touched": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "hardware_readiness_claim": False,
    "silicon_readiness_claim": False,
    "broad_eml_advantage_claim": False,
}

NON_CLAIMS = [
    "EH-A7 aggregates a bounded list of existing local command feeds into a private lane-state view; it is not a complete ecosystem auditor.",
    "EH-A7 does not scan every feed, check external sources, create a dashboard, verify renderer correctness, or claim visualization quality.",
    "EH-A7 does not publish, approve public copy, update public/dev surfaces, create SDK/course material, or start product implementation.",
    "EH-A7 does not reopen training-cost, produce estimate values, consume reviewer response text, record reviewer approval, start D110, edit MachLib, run Lean, change runtime lowering, or touch laptop-owned repositories.",
    "EH-A7 does not claim estimator accuracy, training savings, runtime performance, compiler correctness, hardware readiness, silicon readiness, public readiness, catalog completeness, or broad EML advantage.",
]


def load_source_feed(spec: dict[str, Any]) -> dict[str, Any]:
    payload = json.loads(spec["path"].read_text(encoding="utf-8"))
    if payload["feedId"] != spec["expectedFeedId"]:
        raise ValueError(f"unexpected feed id for {spec['laneId']}")
    if "status" not in payload or "nextAction" not in payload or "claimFlags" not in payload:
        raise ValueError(f"feed missing required fields for {spec['laneId']}")
    return payload


def summarize_lane_state(spec: dict[str, Any], feed: dict[str, Any]) -> dict[str, Any]:
    flags = feed["claimFlags"]
    lane_id = spec["laneId"]
    if lane_id == "training-cost-estimator":
        lane_status = "held_by_prod_a21"
        blocker = "trainingCostEstimatorLaneHeld"
    elif lane_id == "private-atlas-v0":
        lane_status = "held_pending_reviewer_response_or_explicit_redirect"
        blocker = "privateHoldSelected"
    elif lane_id == "public-math-review":
        lane_status = "held_pending_actual_reviewer_response"
        blocker = "d110BlockedUntilResponseExists"
    elif lane_id == "product-roadmap":
        lane_status = "paused_by_product_roadmap_pause_digest"
        blocker = "productRoadmapLanePaused"
    elif lane_id == "electronics-inbox":
        lane_status = feed.get("inboxStatus", "pending_no_artifact")
        blocker = "artifactProvided"
    elif lane_id == "electronics-guard":
        lane_status = feed.get("decision", "electronics_bridge_guard_status_recorded")
        blocker = "defaultInboxStatus"
    else:
        lane_status = "refreshed_after_training_cost_hold"
        blocker = "productRoadmapPaused"

    blocked_claims = [
        key
        for key in [
            "public_surface_updated",
            "public_ready",
            "public_readiness_claim",
            "runtime_performance_claim",
            "compiler_correctness_claim",
            "hardware_readiness_claim",
            "silicon_readiness_claim",
            "broad_eml_advantage_claim",
            "laptop_owned_repo_touched",
            "electronics_repo_touched",
            "source_repo_modified",
            "training_cost_estimator_implemented",
            "estimator_implemented",
            "estimate_values_produced",
            "reviewer_response_consumed",
            "reviewer_approval_recorded",
            "d110_started",
        ]
        if flags.get(key) is False
    ]
    return {
        "laneId": lane_id,
        "feedId": feed["feedId"],
        "feedDate": feed["date"],
        "feedStatus": feed["status"],
        "laneStatus": lane_status,
        "nextAction": feed["nextAction"],
        "sourcePath": str(spec["path"].relative_to(ROOT)),
        "blockedClaimCount": len(blocked_claims),
        "blockedClaimSample": blocked_claims[:8],
        "blockerField": blocker,
        "blockerValue": feed.get(blocker),
        "publicSurfaceUpdated": flags.get("public_surface_updated", flags.get("public_ready", False)),
        "laptopOwnedRepoTouched": flags.get("laptop_owned_repo_touched", flags.get("source_repo_modified", False)),
        "runtimePerformanceClaim": flags.get("runtime_performance_claim", False),
        "compilerCorrectnessClaim": flags.get("compiler_correctness_claim", False),
    }


def build_payload() -> dict[str, Any]:
    loaded = [{"spec": spec, "feed": load_source_feed(spec)} for spec in SOURCE_FEEDS]
    lane_rows = [summarize_lane_state(item["spec"], item["feed"]) for item in loaded]
    held_or_paused = [
        row
        for row in lane_rows
        if row["laneStatus"].startswith(("held", "paused", "pending"))
        or "pending" in row["laneStatus"]
        or "held" in row["laneStatus"]
    ]
    summary = {
        "digestVisibility": "private",
        "sourceFeedCount": len(loaded),
        "laneStateRowCount": len(lane_rows),
        "heldOrPausedRowCount": len(held_or_paused),
        "allFeedsScanned": False,
        "dashboardUiCreated": False,
        "publicSurfaceUpdated": False,
        "trainingCostEstimatorReopened": False,
        "reviewerResponseConsumed": False,
        "reviewerApprovalRecorded": False,
        "d110Started": False,
        "laptopOwnedRepoTouched": False,
        "nextRecommendedArtifact": NEXT_RECOMMENDED_ARTIFACT,
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id=ARTIFACT_ID,
        artifact_type="private_command_feed_lane_state_aggregation",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceFeeds": [
                {
                    "laneId": item["spec"]["laneId"],
                    "feedId": item["feed"]["feedId"],
                    "path": str(item["spec"]["path"].relative_to(ROOT)),
                }
                for item in loaded
            ],
            "laneStateRows": lane_rows,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    summary = payload["summary"]
    if summary["sourceFeedCount"] != len(SOURCE_FEEDS):
        raise ValueError("source feed count drift")
    if summary["laneStateRowCount"] != len(SOURCE_FEEDS):
        raise ValueError("lane state row count drift")
    if summary["heldOrPausedRowCount"] < 5:
        raise ValueError("expected held/paused/pending states to be visible")
    for key in [
        "allFeedsScanned",
        "dashboardUiCreated",
        "publicSurfaceUpdated",
        "trainingCostEstimatorReopened",
        "reviewerResponseConsumed",
        "reviewerApprovalRecorded",
        "d110Started",
        "laptopOwnedRepoTouched",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    rows = {row["laneId"]: row for row in payload["laneStateRows"]}
    expected_lanes = {spec["laneId"] for spec in SOURCE_FEEDS}
    if set(rows) != expected_lanes:
        raise ValueError("lane set drift")
    if rows["training-cost-estimator"]["laneStatus"] != "held_by_prod_a21":
        raise ValueError("training-cost estimator must remain held")
    if rows["public-math-review"]["laneStatus"] != "held_pending_actual_reviewer_response":
        raise ValueError("public math review must remain held")
    if rows["electronics-inbox"]["laneStatus"] != "pending_no_artifact":
        raise ValueError("electronics inbox must remain pending")
    if rows["electronics-inbox"]["laptopOwnedRepoTouched"] is not False:
        raise ValueError("laptop-owned repos must not be touched")
    for row in payload["laneStateRows"]:
        if row["publicSurfaceUpdated"] is not False:
            raise ValueError("public surfaces must remain untouched")
        if row["runtimePerformanceClaim"] is not False:
            raise ValueError("runtime performance claims must remain blocked")
        if row["compilerCorrectnessClaim"] is not False:
            raise ValueError("compiler correctness claims must remain blocked")
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
        semantic_strength="private_bounded_command_feed_aggregation_no_dashboard_or_completeness_claim",
        source=f"python/results/eh_a7_private_command_feed_lane_state_aggregation/eh_a7_private_command_feed_lane_state_aggregation_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="eh_a7_private_command_feed_lane_state_aggregation_feed",
        date=DATE,
        status=payload["status"],
        next_action="Use the private lane-state aggregation to choose one explicit non-held implementation/intake lane.",
        claim_flags=payload["claimFlags"],
        fields={
            "digestVisibility": payload["summary"]["digestVisibility"],
            "sourceFeedCount": payload["summary"]["sourceFeedCount"],
            "laneStateRowCount": payload["summary"]["laneStateRowCount"],
            "heldOrPausedRowCount": payload["summary"]["heldOrPausedRowCount"],
            "allFeedsScanned": payload["summary"]["allFeedsScanned"],
            "dashboardUiCreated": payload["summary"]["dashboardUiCreated"],
            "publicSurfaceUpdated": payload["summary"]["publicSurfaceUpdated"],
            "trainingCostEstimatorReopened": payload["summary"]["trainingCostEstimatorReopened"],
            "laptopOwnedRepoTouched": payload["summary"]["laptopOwnedRepoTouched"],
            "nextRecommendedArtifact": payload["summary"]["nextRecommendedArtifact"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="EH-A7 Private Command-Feed Lane-State Aggregation",
        status=payload["status"],
        summary_rows=[
            ("digest visibility", payload["summary"]["digestVisibility"]),
            ("source feeds", payload["summary"]["sourceFeedCount"]),
            ("lane-state rows", payload["summary"]["laneStateRowCount"]),
            ("held/paused/pending rows", payload["summary"]["heldOrPausedRowCount"]),
            ("all feeds scanned", payload["summary"]["allFeedsScanned"]),
            ("dashboard UI created", payload["summary"]["dashboardUiCreated"]),
            ("public surface updated", payload["summary"]["publicSurfaceUpdated"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Lane State Rows",
                [
                    f"- `{row['laneId']}`: `{row['laneStatus']}` from `{row['feedId']}`; next: {row['nextAction']}"
                    for row in payload["laneStateRows"]
                ],
            ),
            (
                "Source Feeds",
                [f"- `{item['laneId']}`: `{item['path']}`" for item in payload["sourceFeeds"]],
            ),
            (
                "Guardrails",
                [
                    "- selected local command feeds only; no all-feed scan",
                    "- private aggregation only; no dashboard or public surface",
                    "- held lanes remain held unless an explicit bounded trigger arrives",
                    "- no laptop-owned repo touch",
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
    result_path = out_dir / f"eh_a7_private_command_feed_lane_state_aggregation_{STAMP}.json"
    report_path = report_dir / f"eh_a7_private_command_feed_lane_state_aggregation_{STAMP}.md"
    evidence_path = evidence_dir / "eh_a7_private_command_feed_lane_state_aggregation.json"
    feed_path = command_feed_dir / f"eh_a7_private_command_feed_lane_state_aggregation_feed_{STAMP}.json"
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
        default=ROOT / "python/results/eh_a7_private_command_feed_lane_state_aggregation",
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
    print("EH_A7_PRIVATE_COMMAND_FEED_LANE_STATE_AGGREGATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
