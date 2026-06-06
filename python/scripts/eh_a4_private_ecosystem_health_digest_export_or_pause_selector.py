#!/usr/bin/env python3
"""EH-A4 private ecosystem health digest export or pause selector."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import eh_a1_private_ecosystem_health_report_seed as eh_a1  # noqa: E402
from scripts import eh_a2_private_health_report_fixture_validator as eh_a2  # noqa: E402
from scripts import eh_a3_private_health_report_source_freshness_guard as eh_a3  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_ecosystem_health_digest_export_or_pause_selector.v0"
STATUS = "EH_A4_PRIVATE_ECOSYSTEM_HEALTH_DIGEST_EXPORT_OR_PAUSE_SELECTOR_PASS"

TRUE_CLAIM_FLAGS = {
    "eh_a3_consumed",
    "private_digest_export_created",
    "pause_selector_recorded",
    "eh_lane_pause_recommended",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "eh_a3_consumed": True,
    "private_digest_export_created": True,
    "pause_selector_recorded": True,
    "eh_lane_pause_recommended": True,
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
    "health_report_completeness_claim": False,
    "public_digest_created": False,
    "external_source_checked": False,
    "new_health_report_checks_added": False,
}

NON_CLAIMS = [
    "EH-A4 exports a private digest and pause selector for the EH seed lane; it is not a complete ecosystem auditor.",
    "EH-A4 does not create a dashboard UI, public dashboard, public page, renderer, or public digest.",
    "EH-A4 does not approve public copy, public readiness, compiler correctness, runtime performance, training savings, estimator accuracy, hardware readiness, silicon readiness, or broad EML advantage claims.",
    "EH-A4 respects the D109 hold and does not start D110, consume reviewer response, or record reviewer approval.",
    "EH-A4 does not touch laptop-owned electronics repositories.",
]


def build_digest(health_report: dict[str, Any], fixture_validator: dict[str, Any], freshness_guard: dict[str, Any]) -> dict[str, Any]:
    lane_rows = []
    for lane in health_report["activeLanes"]:
        row = {
            "laneId": lane["laneId"],
            "status": lane["status"],
            "nextAction": lane["nextAction"],
        }
        if lane["laneId"] == "shared-evidence-infrastructure":
            row["status"] = "pause_recommended_after_eh_seed"
            row["nextAction"] = "Pause EH seed lane; return to product/tooling unless real reviewer or laptop artifact arrives."
        lane_rows.append(row)
    blocked_claims = [item["claim"] for item in health_report["blockedClaims"]]
    return {
        "digestId": "private_ecosystem_health_digest_2026_06_06",
        "visibility": "private",
        "snapshotDate": DATE,
        "sourceArtifacts": [
            health_report["artifactId"],
            fixture_validator["artifactId"],
            freshness_guard["artifactId"],
        ],
        "headline": "Private ecosystem health seed is present, validated, and source-feed checked for the 2026-06-06 snapshot.",
        "laneRows": lane_rows,
        "blockedClaims": blocked_claims,
        "verificationSummary": {
            "selectedFeedCount": health_report["summary"]["selectedFeedCount"],
            "fixtureCheckCount": fixture_validator["summary"]["fixtureCheckCount"],
            "passedFixtureCheckCount": fixture_validator["summary"]["passedFixtureCheckCount"],
            "sourceFeedCount": freshness_guard["summary"]["sourceFeedCount"],
            "passedSourceFeedCheckCount": freshness_guard["summary"]["passedSourceFeedCheckCount"],
            "aggregateCheckCount": freshness_guard["summary"]["aggregateCheckCount"],
            "passedAggregateCheckCount": freshness_guard["summary"]["passedAggregateCheckCount"],
        },
        "recommendedPosture": "pause_eh_lane_as_seeded",
        "recommendedNextWork": "Return to product/tooling work, with SDK surface inventory as the cleanest next private product artifact unless a real reviewer or laptop artifact arrives.",
    }


def selector_options() -> list[dict[str, Any]]:
    return [
        {
            "optionId": "pause_eh_lane_as_seeded",
            "selected": True,
            "reason": "EH-A1/EH-A2/EH-A3 now provide seed report, fixture validation, and local source-feed checks.",
        },
        {
            "optionId": "continue_eh_lane_with_dashboard",
            "selected": False,
            "reason": "Dashboard UI remains explicitly out of scope and would create public-readiness risk.",
        },
        {
            "optionId": "continue_eh_lane_with_more_governance_packets",
            "selected": False,
            "reason": "Marginal value is lower than returning to product/tooling work after the digest export.",
        },
    ]


def build_payload() -> dict[str, Any]:
    health_report = eh_a1.build_payload()
    eh_a1.validate_payload(health_report)
    fixture_validator = eh_a2.build_payload()
    eh_a2.validate_payload(fixture_validator)
    freshness_guard = eh_a3.build_payload()
    eh_a3.validate_payload(freshness_guard)
    digest = build_digest(health_report, fixture_validator, freshness_guard)
    options = selector_options()
    summary = {
        "sourceArtifact": freshness_guard["artifactId"],
        "digestExportCreated": True,
        "digestVisibility": "private",
        "selectorOptionCount": len(options),
        "selectedOption": "pause_eh_lane_as_seeded",
        "ehLanePauseRecommended": True,
        "dashboardUiCreated": False,
        "publicReadinessClaim": False,
        "d109HoldRespected": True,
        "d110Started": False,
        "reviewerResponseConsumed": False,
        "nextRecommendedArtifact": "SDK-A1 private SDK surface inventory or real reviewer/laptop artifact intake if supplied",
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="eh-a4-private-ecosystem-health-digest-export-or-pause-selector",
        artifact_type="private_ecosystem_health_digest_export_or_pause_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": freshness_guard["artifactId"],
            "privateDigest": digest,
            "selectorOptions": options,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifact"] != "eh-a3-private-health-report-source-freshness-guard":
        raise ValueError("EH-A4 must consume EH-A3")
    summary = payload["summary"]
    if summary["digestExportCreated"] is not True or summary["digestVisibility"] != "private":
        raise ValueError("private digest export must be recorded")
    if summary["selectedOption"] != "pause_eh_lane_as_seeded":
        raise ValueError("EH-A4 must pause the EH seed lane")
    if summary["selectorOptionCount"] != 3:
        raise ValueError("selector option count drift")
    if payload["privateDigest"]["recommendedPosture"] != "pause_eh_lane_as_seeded":
        raise ValueError("digest posture drift")
    selected = [option for option in payload["selectorOptions"] if option["selected"]]
    if len(selected) != 1 or selected[0]["optionId"] != "pause_eh_lane_as_seeded":
        raise ValueError("selector must choose exactly the pause option")
    for key in ["dashboardUiCreated", "publicReadinessClaim", "d110Started", "reviewerResponseConsumed"]:
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
        semantic_strength="private_digest_export_and_pause_selector_no_completeness_or_public_claim",
        source=f"python/results/eh_a4_private_ecosystem_health_digest_export_or_pause_selector/eh_a4_private_ecosystem_health_digest_export_or_pause_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="eh_a4_private_ecosystem_health_digest_export_or_pause_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Pause EH seed lane; next private product/tooling target is SDK-A1 surface inventory unless a real reviewer or laptop artifact arrives.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "digestVisibility": payload["summary"]["digestVisibility"],
            "selectedOption": payload["summary"]["selectedOption"],
            "ehLanePauseRecommended": payload["summary"]["ehLanePauseRecommended"],
            "d109HoldRespected": payload["summary"]["d109HoldRespected"],
            "dashboardUiCreated": payload["summary"]["dashboardUiCreated"],
            "publicReadinessClaim": payload["summary"]["publicReadinessClaim"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    digest = payload["privateDigest"]
    return render_markdown_report(
        title="EH-A4 Private Ecosystem Health Digest Export Or Pause Selector",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("digest visibility", payload["summary"]["digestVisibility"]),
            ("selected option", payload["summary"]["selectedOption"]),
            ("EH lane pause recommended", payload["summary"]["ehLanePauseRecommended"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Private Digest",
                [
                    f"- headline: {digest['headline']}",
                    f"- recommended posture: `{digest['recommendedPosture']}`",
                    f"- recommended next work: {digest['recommendedNextWork']}",
                ],
            ),
            (
                "Lane Rows",
                [
                    f"- `{lane['laneId']}`: `{lane['status']}`; next: {lane['nextAction']}"
                    for lane in digest["laneRows"]
                ],
            ),
            (
                "Selector Options",
                [
                    f"- `{option['optionId']}`: selected `{option['selected']}`; {option['reason']}"
                    for option in payload["selectorOptions"]
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
    result_path = out_dir / f"eh_a4_private_ecosystem_health_digest_export_or_pause_selector_{STAMP}.json"
    report_path = report_dir / f"eh_a4_private_ecosystem_health_digest_export_or_pause_selector_{STAMP}.md"
    evidence_path = evidence_dir / "eh_a4_private_ecosystem_health_digest_export_or_pause_selector.json"
    feed_path = command_feed_dir / f"eh_a4_private_ecosystem_health_digest_export_or_pause_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eh_a4_private_ecosystem_health_digest_export_or_pause_selector")
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
    print("EH_A4_PRIVATE_ECOSYSTEM_HEALTH_DIGEST_EXPORT_OR_PAUSE_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
