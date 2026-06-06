#!/usr/bin/env python3
"""EH-A1 private ecosystem health report seed."""

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

from scripts import ea_a2_single_artifact_toolkit_migration_smoke as ea_a2  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_ecosystem_health_report_seed.v0"
STATUS = "EH_A1_PRIVATE_ECOSYSTEM_HEALTH_REPORT_SEED_PASS"

FEED_FILES = [
    "eml_d109_private_reviewer_response_availability_guard_feed_2026_06_06.json",
    "prod_a6_training_cost_estimator_fixture_packet_feed_2026_06_06.json",
    "ea_a1_shared_evidence_artifact_toolkit_seed_feed_2026_06_06.json",
    "ea_a2_single_artifact_toolkit_migration_smoke_feed_2026_06_06.json",
]

TRUE_CLAIM_FLAGS = {
    "ea_a2_consumed",
    "private_health_report_seed_created",
    "command_feeds_aggregated",
    "active_lanes_recorded",
    "blocked_claims_recorded",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "ea_a2_consumed": True,
    "private_health_report_seed_created": True,
    "command_feeds_aggregated": True,
    "active_lanes_recorded": True,
    "blocked_claims_recorded": True,
    "d109_hold_respected": True,
    "dashboard_ui_created": False,
    "public_dashboard_created": False,
    "public_readiness_claim": False,
    "public_copy_approved": False,
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
    "broad_eml_advantage_claim": False,
}

NON_CLAIMS = [
    "EH-A1 is a private health report seed over selected existing command feeds, not a complete ecosystem state oracle.",
    "EH-A1 does not create a dashboard UI, public page, renderer, visualization-quality claim, or public-readiness claim.",
    "EH-A1 does not approve public copy, product readiness, compiler correctness, runtime performance, training savings, estimator accuracy, hardware readiness, silicon readiness, or broad EML advantage claims.",
    "EH-A1 respects the D109 hold and does not start D110, consume a reviewer response, or record reviewer approval.",
    "EH-A1 does not touch laptop-owned electronics repositories.",
]


def load_selected_feeds(feed_dir: Path = ROOT / "command_center_feeds") -> list[dict[str, Any]]:
    feeds = []
    for filename in FEED_FILES:
        path = feed_dir / filename
        with path.open(encoding="utf-8") as handle:
            feed = json.load(handle)
        feed["_sourcePath"] = str(path.relative_to(ROOT))
        feeds.append(feed)
    return feeds


def summarize_feed(feed: dict[str, Any]) -> dict[str, Any]:
    claim_flags = feed.get("claimFlags", {})
    return {
        "feedId": feed["feedId"],
        "status": feed["status"],
        "nextAction": feed["nextAction"],
        "sourcePath": feed["_sourcePath"],
        "trueClaimFlags": sorted(key for key, value in claim_flags.items() if value is True),
        "blockedClaimFlags": sorted(key for key, value in claim_flags.items() if value is False),
        "d110BlockedUntilResponseExists": feed.get("d110BlockedUntilResponseExists")
        or claim_flags.get("d110_blocked_until_response_exists", False),
        "publicReady": feed.get("publicSurfaceUpdated", False)
        or claim_flags.get("public_ready", False)
        or claim_flags.get("public_product_ready", False),
        "trainingSavingsClaim": feed.get("trainingSavingsClaim", False)
        or claim_flags.get("training_savings_claim", False),
        "runtimePerformanceClaim": claim_flags.get("runtime_performance_claim", False),
        "compilerCorrectnessClaim": claim_flags.get("compiler_correctness_claim", False),
        "hardwareReadinessClaim": claim_flags.get("hardware_readiness_claim", False),
    }


def active_lanes() -> list[dict[str, Any]]:
    return [
        {
            "laneId": "d-series-private-reviewer",
            "status": "held",
            "currentArtifact": "EML-D109 private reviewer response availability guard",
            "blocker": "actual_private_reviewer_response_required",
            "nextAction": "Start EML-D110 only after an actual private reviewer response exists.",
        },
        {
            "laneId": "product-training-cost-estimator",
            "status": "parked_after_static_fixtures",
            "currentArtifact": "PROD-A6 training cost estimator fixture packet",
            "blocker": "implementation_and_accuracy_claims_blocked",
            "nextAction": "Keep behind shared evidence infrastructure and executable validator work.",
        },
        {
            "laneId": "shared-evidence-infrastructure",
            "status": "active",
            "currentArtifact": "EA-A2 single-artifact toolkit migration smoke",
            "blocker": None,
            "nextAction": "Create EH-A2 private health report fixture or feed aggregation validator.",
        },
        {
            "laneId": "electronics-course-and-capture",
            "status": "owner_boundary_active",
            "currentArtifact": "laptop-agent-owned course and electronics work",
            "blocker": "research_side_must_not_touch_laptop_owned_repos",
            "nextAction": "Receive laptop-agent packets through claim-bounded bridge artifacts only.",
        },
    ]


def blocked_claims() -> list[dict[str, str]]:
    return [
        {"claim": "public readiness", "reason": "No public release approval is recorded."},
        {"claim": "public copy approval", "reason": "No reviewer approval or public-copy gate has been satisfied."},
        {"claim": "renderer correctness", "reason": "EH-A1 creates no renderer and proves no renderer property."},
        {"claim": "visualization quality", "reason": "EH-A1 creates no visualization surface."},
        {"claim": "compiler correctness", "reason": "No compiler proof or validation is part of this artifact."},
        {"claim": "runtime performance", "reason": "No benchmark or runtime execution is part of this artifact."},
        {"claim": "training savings", "reason": "PROD-A6 fixtures do not estimate or prove savings."},
        {"claim": "estimator accuracy", "reason": "No estimator implementation or real-user validation is present."},
        {"claim": "hardware readiness", "reason": "Research side does not validate electronics hardware readiness."},
        {"claim": "silicon readiness", "reason": "No IP core or accelerator readiness evidence is present."},
        {"claim": "broad EML advantage", "reason": "Selected artifacts remain bounded and claim-limited."},
        {"claim": "D110 reviewer response consumed", "reason": "D109 says D110 is blocked until a real response exists."},
    ]


def build_payload() -> dict[str, Any]:
    ea_a2_payload = ea_a2.build_payload()
    ea_a2.validate_payload(ea_a2_payload)
    feed_summaries = [summarize_feed(feed) for feed in load_selected_feeds()]
    lanes = active_lanes()
    blocks = blocked_claims()
    summary = {
        "sourceArtifact": ea_a2_payload["artifactId"],
        "selectedFeedCount": len(feed_summaries),
        "activeLaneCount": len(lanes),
        "blockedClaimCount": len(blocks),
        "privateHealthReportSeedCreated": True,
        "dashboardUiCreated": False,
        "publicReadinessClaim": False,
        "laptopOwnedRepoTouched": False,
        "d109HoldRespected": True,
        "d110Started": False,
        "reviewerResponseConsumed": False,
        "nextRecommendedArtifact": "EH-A2 private health report fixture or feed aggregation validator",
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="eh-a1-private-ecosystem-health-report-seed",
        artifact_type="private_ecosystem_health_report_seed",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": ea_a2_payload["artifactId"],
            "feedSummaries": feed_summaries,
            "activeLanes": lanes,
            "blockedClaims": blocks,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifact"] != "ea-a2-single-artifact-toolkit-migration-smoke":
        raise ValueError("EH-A1 must consume EA-A2")
    summary = payload["summary"]
    if summary["selectedFeedCount"] != len(FEED_FILES):
        raise ValueError("selected feed count drift")
    if summary["activeLaneCount"] != 4:
        raise ValueError("active lane count drift")
    if summary["blockedClaimCount"] != 12:
        raise ValueError("blocked claim count drift")
    for key in [
        "dashboardUiCreated",
        "publicReadinessClaim",
        "laptopOwnedRepoTouched",
        "d110Started",
        "reviewerResponseConsumed",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    d_series_lane = next(lane for lane in payload["activeLanes"] if lane["laneId"] == "d-series-private-reviewer")
    if d_series_lane["status"] != "held":
        raise ValueError("D-series lane must remain held")
    d109_feed = next(feed for feed in payload["feedSummaries"] if feed["feedId"].startswith("eml_d109"))
    if d109_feed["d110BlockedUntilResponseExists"] is not True:
        raise ValueError("D109 feed must keep D110 blocked")
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
        semantic_strength="private_selected_feed_health_seed_not_complete_state_or_public_surface",
        source=f"python/results/eh_a1_private_ecosystem_health_report_seed/eh_a1_private_ecosystem_health_report_seed_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="eh_a1_private_ecosystem_health_report_seed_feed",
        date=DATE,
        status=payload["status"],
        next_action="Create EH-A2 private health report fixture or feed aggregation validator.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "selectedFeedCount": payload["summary"]["selectedFeedCount"],
            "activeLaneCount": payload["summary"]["activeLaneCount"],
            "blockedClaimCount": payload["summary"]["blockedClaimCount"],
            "dashboardUiCreated": payload["summary"]["dashboardUiCreated"],
            "publicReadinessClaim": payload["summary"]["publicReadinessClaim"],
            "d109HoldRespected": payload["summary"]["d109HoldRespected"],
            "d110Started": payload["summary"]["d110Started"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="EH-A1 Private Ecosystem Health Report Seed",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("selected feeds", payload["summary"]["selectedFeedCount"]),
            ("active lanes", payload["summary"]["activeLaneCount"]),
            ("blocked claims", payload["summary"]["blockedClaimCount"]),
            ("dashboard UI created", payload["summary"]["dashboardUiCreated"]),
            ("public readiness claim", payload["summary"]["publicReadinessClaim"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Active Lanes",
                [
                    f"- `{lane['laneId']}`: `{lane['status']}`; next: {lane['nextAction']}"
                    for lane in payload["activeLanes"]
                ],
            ),
            (
                "Selected Feeds",
                [
                    f"- `{feed['feedId']}`: `{feed['status']}`; next: {feed['nextAction']}"
                    for feed in payload["feedSummaries"]
                ],
            ),
            (
                "Blocked Claims",
                [f"- {item['claim']}: {item['reason']}" for item in payload["blockedClaims"]],
            ),
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"eh_a1_private_ecosystem_health_report_seed_{STAMP}.json"
    report_path = report_dir / f"eh_a1_private_ecosystem_health_report_seed_{STAMP}.md"
    evidence_path = evidence_dir / "eh_a1_private_ecosystem_health_report_seed.json"
    feed_path = command_feed_dir / f"eh_a1_private_ecosystem_health_report_seed_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eh_a1_private_ecosystem_health_report_seed")
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
    print("EH_A1_PRIVATE_ECOSYSTEM_HEALTH_REPORT_SEED_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
