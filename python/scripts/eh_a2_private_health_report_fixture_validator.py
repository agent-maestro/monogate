#!/usr/bin/env python3
"""EH-A2 private health report fixture validator."""

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
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_health_report_fixture_validator.v0"
STATUS = "EH_A2_PRIVATE_HEALTH_REPORT_FIXTURE_VALIDATOR_PASS"

EXPECTED_FEED_IDS = {
    "eml_d109_private_reviewer_response_availability_guard_feed",
    "prod_a6_training_cost_estimator_fixture_packet_feed",
    "ea_a1_shared_evidence_artifact_toolkit_seed_feed",
    "ea_a2_single_artifact_toolkit_migration_smoke_feed",
}

EXPECTED_LANE_IDS = {
    "d-series-private-reviewer",
    "product-training-cost-estimator",
    "shared-evidence-infrastructure",
    "electronics-course-and-capture",
}

EXPECTED_BLOCKED_CLAIMS = {
    "public readiness",
    "public copy approval",
    "renderer correctness",
    "visualization quality",
    "compiler correctness",
    "runtime performance",
    "training savings",
    "estimator accuracy",
    "hardware readiness",
    "silicon readiness",
    "broad EML advantage",
    "D110 reviewer response consumed",
}

FORBIDDEN_TRUE_FLAGS = {
    "dashboard_ui_created",
    "public_dashboard_created",
    "public_readiness_claim",
    "public_copy_approved",
    "renderer_correctness_claim",
    "visualization_quality_claim",
    "compiler_correctness_claim",
    "runtime_performance_claim",
    "training_savings_claim",
    "estimator_accuracy_claim",
    "hardware_readiness_claim",
    "silicon_readiness_claim",
    "electronics_repo_touched",
    "laptop_owned_repo_touched",
    "d110_started",
    "reviewer_response_consumed",
    "reviewer_approval_recorded",
    "broad_eml_advantage_claim",
}

TRUE_CLAIM_FLAGS = {
    "eh_a1_consumed",
    "fixture_validator_created",
    "feed_invariants_checked",
    "lane_invariants_checked",
    "blocked_claim_invariants_checked",
    "forbidden_claim_flags_checked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "eh_a1_consumed": True,
    "fixture_validator_created": True,
    "feed_invariants_checked": True,
    "lane_invariants_checked": True,
    "blocked_claim_invariants_checked": True,
    "forbidden_claim_flags_checked": True,
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
    "schema_validator_implemented": False,
    "dashboard_renderer_implemented": False,
    "health_report_completeness_claim": False,
}

NON_CLAIMS = [
    "EH-A2 validates a narrow private fixture shape for EH-A1; it is not a complete ecosystem auditor.",
    "EH-A2 does not implement a schema validator framework, dashboard UI, dashboard renderer, public page, or public dashboard.",
    "EH-A2 does not approve public copy, public readiness, compiler correctness, runtime performance, training savings, estimator accuracy, hardware readiness, silicon readiness, or broad EML advantage claims.",
    "EH-A2 respects the D109 hold and does not start D110, consume reviewer response, or record reviewer approval.",
    "EH-A2 does not touch laptop-owned electronics repositories.",
]


def check_equal_set(actual: set[str], expected: set[str], check_id: str) -> dict[str, Any]:
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    return {
        "checkId": check_id,
        "status": "pass" if not missing and not unexpected else "fail",
        "missing": missing,
        "unexpected": unexpected,
    }


def build_checks(health_report: dict[str, Any]) -> list[dict[str, Any]]:
    feed_ids = {feed["feedId"] for feed in health_report["feedSummaries"]}
    lane_ids = {lane["laneId"] for lane in health_report["activeLanes"]}
    blocked_claims = {item["claim"] for item in health_report["blockedClaims"]}
    claim_flags = health_report["claimFlags"]
    d_series_lane = next(lane for lane in health_report["activeLanes"] if lane["laneId"] == "d-series-private-reviewer")
    d109_feed = next(feed for feed in health_report["feedSummaries"] if feed["feedId"].startswith("eml_d109"))
    return [
        check_equal_set(feed_ids, EXPECTED_FEED_IDS, "expected_feed_ids_present"),
        check_equal_set(lane_ids, EXPECTED_LANE_IDS, "expected_lane_ids_present"),
        check_equal_set(blocked_claims, EXPECTED_BLOCKED_CLAIMS, "expected_blocked_claims_present"),
        {
            "checkId": "d109_hold_preserved",
            "status": "pass"
            if d_series_lane["status"] == "held" and d109_feed["d110BlockedUntilResponseExists"] is True
            else "fail",
            "laneStatus": d_series_lane["status"],
            "d110BlockedUntilResponseExists": d109_feed["d110BlockedUntilResponseExists"],
        },
        {
            "checkId": "forbidden_claim_flags_remain_false",
            "status": "pass" if all(claim_flags.get(flag) is False for flag in FORBIDDEN_TRUE_FLAGS) else "fail",
            "checkedFlags": sorted(FORBIDDEN_TRUE_FLAGS),
        },
        {
            "checkId": "next_action_points_to_eh_a2",
            "status": "pass"
            if health_report["summary"]["nextRecommendedArtifact"]
            == "EH-A2 private health report fixture or feed aggregation validator"
            else "fail",
            "nextRecommendedArtifact": health_report["summary"]["nextRecommendedArtifact"],
        },
    ]


def build_payload() -> dict[str, Any]:
    health_report = eh_a1.build_payload()
    eh_a1.validate_payload(health_report)
    checks = build_checks(health_report)
    summary = {
        "sourceArtifact": health_report["artifactId"],
        "fixtureCheckCount": len(checks),
        "passedFixtureCheckCount": sum(1 for check in checks if check["status"] == "pass"),
        "expectedFeedCount": len(EXPECTED_FEED_IDS),
        "expectedLaneCount": len(EXPECTED_LANE_IDS),
        "expectedBlockedClaimCount": len(EXPECTED_BLOCKED_CLAIMS),
        "forbiddenClaimFlagCount": len(FORBIDDEN_TRUE_FLAGS),
        "dashboardUiCreated": False,
        "publicReadinessClaim": False,
        "d109HoldRespected": True,
        "d110Started": False,
        "reviewerResponseConsumed": False,
        "nextRecommendedArtifact": "EH-A3 private health report source freshness guard",
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="eh-a2-private-health-report-fixture-validator",
        artifact_type="private_health_report_fixture_validator",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": health_report["artifactId"],
            "fixtureChecks": checks,
            "expectedFeedIds": sorted(EXPECTED_FEED_IDS),
            "expectedLaneIds": sorted(EXPECTED_LANE_IDS),
            "expectedBlockedClaims": sorted(EXPECTED_BLOCKED_CLAIMS),
            "forbiddenTrueFlags": sorted(FORBIDDEN_TRUE_FLAGS),
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifact"] != "eh-a1-private-ecosystem-health-report-seed":
        raise ValueError("EH-A2 must consume EH-A1")
    summary = payload["summary"]
    if summary["fixtureCheckCount"] != 6 or summary["passedFixtureCheckCount"] != 6:
        raise ValueError("fixture check drift")
    if summary["expectedFeedCount"] != 4 or summary["expectedLaneCount"] != 4:
        raise ValueError("expected feed/lane count drift")
    if summary["expectedBlockedClaimCount"] != 12:
        raise ValueError("blocked claim count drift")
    for key in ["dashboardUiCreated", "publicReadinessClaim", "d110Started", "reviewerResponseConsumed"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    for check in payload["fixtureChecks"]:
        if check["status"] != "pass":
            raise ValueError(f"fixture check failed: {check['checkId']}")
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
        semantic_strength="private_health_report_fixture_validator_no_completeness_or_public_claim",
        source=f"python/results/eh_a2_private_health_report_fixture_validator/eh_a2_private_health_report_fixture_validator_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="eh_a2_private_health_report_fixture_validator_feed",
        date=DATE,
        status=payload["status"],
        next_action="Create EH-A3 private health report source freshness guard.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "fixtureCheckCount": payload["summary"]["fixtureCheckCount"],
            "passedFixtureCheckCount": payload["summary"]["passedFixtureCheckCount"],
            "d109HoldRespected": payload["summary"]["d109HoldRespected"],
            "dashboardUiCreated": payload["summary"]["dashboardUiCreated"],
            "publicReadinessClaim": payload["summary"]["publicReadinessClaim"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="EH-A2 Private Health Report Fixture Validator",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("fixture checks", payload["summary"]["fixtureCheckCount"]),
            ("passed checks", payload["summary"]["passedFixtureCheckCount"]),
            ("expected feeds", payload["summary"]["expectedFeedCount"]),
            ("expected lanes", payload["summary"]["expectedLaneCount"]),
            ("expected blocked claims", payload["summary"]["expectedBlockedClaimCount"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Fixture Checks",
                [
                    f"- `{check['checkId']}`: `{check['status']}`"
                    for check in payload["fixtureChecks"]
                ],
            ),
            (
                "Forbidden True Flags",
                [f"- `{flag}` must remain false" for flag in payload["forbiddenTrueFlags"]],
            ),
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"eh_a2_private_health_report_fixture_validator_{STAMP}.json"
    report_path = report_dir / f"eh_a2_private_health_report_fixture_validator_{STAMP}.md"
    evidence_path = evidence_dir / "eh_a2_private_health_report_fixture_validator.json"
    feed_path = command_feed_dir / f"eh_a2_private_health_report_fixture_validator_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eh_a2_private_health_report_fixture_validator")
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
    print("EH_A2_PRIVATE_HEALTH_REPORT_FIXTURE_VALIDATOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
