#!/usr/bin/env python3
"""EH-A3 private health report source freshness guard."""

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

from scripts import eh_a1_private_ecosystem_health_report_seed as eh_a1  # noqa: E402
from scripts import eh_a2_private_health_report_fixture_validator as eh_a2  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_health_report_source_freshness_guard.v0"
STATUS = "EH_A3_PRIVATE_HEALTH_REPORT_SOURCE_FRESHNESS_GUARD_PASS"

PRIVATE_ONLY_FALSE_FLAGS = {
    "public_ready",
    "public_product_ready",
    "public_surface_updated",
    "public_copy_approved",
    "public_page_created",
    "public_dashboard_created",
    "public_readiness_claim",
    "dashboard_ui_created",
    "runtime_performance_claim",
    "compiler_correctness_claim",
    "training_savings_claim",
    "hardware_readiness_claim",
    "silicon_readiness_claim",
    "broad_eml_advantage_claim",
}

TRUE_CLAIM_FLAGS = {
    "eh_a2_consumed",
    "source_freshness_guard_created",
    "source_feed_files_checked",
    "source_feed_json_parse_checked",
    "source_feed_date_alignment_checked",
    "source_feed_private_only_flags_checked",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "eh_a2_consumed": True,
    "source_freshness_guard_created": True,
    "source_feed_files_checked": True,
    "source_feed_json_parse_checked": True,
    "source_feed_date_alignment_checked": True,
    "source_feed_private_only_flags_checked": True,
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
    "feed_recency_guarantee_claim": False,
    "external_source_checked": False,
}

NON_CLAIMS = [
    "EH-A3 checks selected local source feeds for the 2026-06-06 private health snapshot; it is not a live recency guarantee.",
    "EH-A3 does not check external systems, remote repositories, dashboards, public pages, or renderer behavior.",
    "EH-A3 does not approve public copy, public readiness, compiler correctness, runtime performance, training savings, estimator accuracy, hardware readiness, silicon readiness, or broad EML advantage claims.",
    "EH-A3 respects the D109 hold and does not start D110, consume reviewer response, or record reviewer approval.",
    "EH-A3 does not touch laptop-owned electronics repositories.",
]


def source_feed_checks(health_report: dict[str, Any]) -> list[dict[str, Any]]:
    checks = []
    for summary in health_report["feedSummaries"]:
        source_path = ROOT / summary["sourcePath"]
        exists = source_path.exists()
        parse_ok = False
        date_aligned = False
        feed_id_matches = False
        private_only_flags_false = False
        parsed_status = None
        parsed_date = None
        parsed_feed_id = None
        if exists:
            with source_path.open(encoding="utf-8") as handle:
                feed = json.load(handle)
            parse_ok = True
            parsed_status = feed.get("status")
            parsed_date = feed.get("date")
            parsed_feed_id = feed.get("feedId")
            date_aligned = parsed_date == DATE
            feed_id_matches = parsed_feed_id == summary["feedId"]
            claim_flags = feed.get("claimFlags", {})
            private_only_flags_false = all(claim_flags.get(flag, False) is False for flag in PRIVATE_ONLY_FALSE_FLAGS)
        checks.append(
            {
                "feedId": summary["feedId"],
                "sourcePath": summary["sourcePath"],
                "status": "pass"
                if exists and parse_ok and date_aligned and feed_id_matches and private_only_flags_false
                else "fail",
                "fileExists": exists,
                "jsonParseOk": parse_ok,
                "dateAligned": date_aligned,
                "feedIdMatches": feed_id_matches,
                "privateOnlyFlagsFalse": private_only_flags_false,
                "parsedDate": parsed_date,
                "parsedFeedId": parsed_feed_id,
                "parsedStatus": parsed_status,
            }
        )
    return checks


def aggregate_checks(source_checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "checkId": "all_source_feed_files_exist",
            "status": "pass" if all(check["fileExists"] for check in source_checks) else "fail",
        },
        {
            "checkId": "all_source_feed_json_parse",
            "status": "pass" if all(check["jsonParseOk"] for check in source_checks) else "fail",
        },
        {
            "checkId": "all_source_feed_dates_match_snapshot",
            "status": "pass" if all(check["dateAligned"] for check in source_checks) else "fail",
            "snapshotDate": DATE,
        },
        {
            "checkId": "all_source_feed_ids_match_health_summary",
            "status": "pass" if all(check["feedIdMatches"] for check in source_checks) else "fail",
        },
        {
            "checkId": "all_source_feed_private_only_flags_false",
            "status": "pass" if all(check["privateOnlyFlagsFalse"] for check in source_checks) else "fail",
            "checkedFlags": sorted(PRIVATE_ONLY_FALSE_FLAGS),
        },
    ]


def build_payload() -> dict[str, Any]:
    fixture_validator = eh_a2.build_payload()
    eh_a2.validate_payload(fixture_validator)
    health_report = eh_a1.build_payload()
    eh_a1.validate_payload(health_report)
    source_checks = source_feed_checks(health_report)
    aggregate = aggregate_checks(source_checks)
    summary = {
        "sourceArtifact": fixture_validator["artifactId"],
        "healthReportArtifact": health_report["artifactId"],
        "sourceFeedCount": len(source_checks),
        "passedSourceFeedCheckCount": sum(1 for check in source_checks if check["status"] == "pass"),
        "aggregateCheckCount": len(aggregate),
        "passedAggregateCheckCount": sum(1 for check in aggregate if check["status"] == "pass"),
        "snapshotDate": DATE,
        "dashboardUiCreated": False,
        "publicReadinessClaim": False,
        "d109HoldRespected": True,
        "d110Started": False,
        "reviewerResponseConsumed": False,
        "nextRecommendedArtifact": "EH-A4 private ecosystem health digest export or pause selector",
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="eh-a3-private-health-report-source-freshness-guard",
        artifact_type="private_health_report_source_freshness_guard",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": fixture_validator["artifactId"],
            "healthReportArtifact": health_report["artifactId"],
            "sourceFeedChecks": source_checks,
            "aggregateChecks": aggregate,
            "privateOnlyFalseFlags": sorted(PRIVATE_ONLY_FALSE_FLAGS),
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifact"] != "eh-a2-private-health-report-fixture-validator":
        raise ValueError("EH-A3 must consume EH-A2")
    if payload["healthReportArtifact"] != "eh-a1-private-ecosystem-health-report-seed":
        raise ValueError("EH-A3 must check EH-A1 source feeds")
    summary = payload["summary"]
    if summary["sourceFeedCount"] != 4 or summary["passedSourceFeedCheckCount"] != 4:
        raise ValueError("source feed check drift")
    if summary["aggregateCheckCount"] != 5 or summary["passedAggregateCheckCount"] != 5:
        raise ValueError("aggregate check drift")
    if summary["snapshotDate"] != DATE:
        raise ValueError("snapshot date drift")
    for key in ["dashboardUiCreated", "publicReadinessClaim", "d110Started", "reviewerResponseConsumed"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    for check in payload["sourceFeedChecks"]:
        if check["status"] != "pass":
            raise ValueError(f"source feed check failed: {check['feedId']}")
    for check in payload["aggregateChecks"]:
        if check["status"] != "pass":
            raise ValueError(f"aggregate check failed: {check['checkId']}")
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
        semantic_strength="private_local_source_feed_freshness_guard_no_live_recency_or_public_claim",
        source=f"python/results/eh_a3_private_health_report_source_freshness_guard/eh_a3_private_health_report_source_freshness_guard_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="eh_a3_private_health_report_source_freshness_guard_feed",
        date=DATE,
        status=payload["status"],
        next_action="Create EH-A4 private ecosystem health digest export or pause selector.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "healthReportArtifact": payload["healthReportArtifact"],
            "sourceFeedCount": payload["summary"]["sourceFeedCount"],
            "passedSourceFeedCheckCount": payload["summary"]["passedSourceFeedCheckCount"],
            "snapshotDate": payload["summary"]["snapshotDate"],
            "d109HoldRespected": payload["summary"]["d109HoldRespected"],
            "dashboardUiCreated": payload["summary"]["dashboardUiCreated"],
            "publicReadinessClaim": payload["summary"]["publicReadinessClaim"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="EH-A3 Private Health Report Source Freshness Guard",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("health report artifact", payload["healthReportArtifact"]),
            ("source feeds", payload["summary"]["sourceFeedCount"]),
            ("passed source feed checks", payload["summary"]["passedSourceFeedCheckCount"]),
            ("aggregate checks", payload["summary"]["aggregateCheckCount"]),
            ("snapshot date", payload["summary"]["snapshotDate"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Source Feed Checks",
                [
                    f"- `{check['feedId']}`: `{check['status']}`; path `{check['sourcePath']}`"
                    for check in payload["sourceFeedChecks"]
                ],
            ),
            (
                "Aggregate Checks",
                [f"- `{check['checkId']}`: `{check['status']}`" for check in payload["aggregateChecks"]],
            ),
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"eh_a3_private_health_report_source_freshness_guard_{STAMP}.json"
    report_path = report_dir / f"eh_a3_private_health_report_source_freshness_guard_{STAMP}.md"
    evidence_path = evidence_dir / "eh_a3_private_health_report_source_freshness_guard.json"
    feed_path = command_feed_dir / f"eh_a3_private_health_report_source_freshness_guard_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eh_a3_private_health_report_source_freshness_guard")
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
    print("EH_A3_PRIVATE_HEALTH_REPORT_SOURCE_FRESHNESS_GUARD_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
