"""Tests for EH-A3 private health report source freshness guard."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eh_a3_private_health_report_source_freshness_guard import (
    CLAIM_FLAGS,
    PRIVATE_ONLY_FALSE_FLAGS,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def aggregate_by_id(payload, check_id: str):
    return next(item for item in payload["aggregateChecks"] if item["checkId"] == check_id)


def test_eh_a3_consumes_eh_a2_and_checks_eh_a1_sources():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EH_A3_PRIVATE_HEALTH_REPORT_SOURCE_FRESHNESS_GUARD_PASS"
    assert payload["sourceArtifact"] == "eh-a2-private-health-report-fixture-validator"
    assert payload["healthReportArtifact"] == "eh-a1-private-ecosystem-health-report-seed"
    assert payload["summary"]["sourceFeedCount"] == 4
    assert payload["summary"]["passedSourceFeedCheckCount"] == 4


def test_eh_a3_source_feed_checks_are_present_parseable_and_date_aligned():
    payload = build_payload()
    for check in payload["sourceFeedChecks"]:
        assert check["status"] == "pass"
        assert check["fileExists"] is True
        assert check["jsonParseOk"] is True
        assert check["dateAligned"] is True
        assert check["feedIdMatches"] is True
        assert check["privateOnlyFlagsFalse"] is True
        assert check["parsedDate"] == "2026-06-06"
        assert check["parsedFeedId"] == check["feedId"]


def test_eh_a3_aggregate_checks_all_pass():
    payload = build_payload()
    assert payload["summary"]["aggregateCheckCount"] == 5
    assert payload["summary"]["passedAggregateCheckCount"] == 5
    for check_id in [
        "all_source_feed_files_exist",
        "all_source_feed_json_parse",
        "all_source_feed_dates_match_snapshot",
        "all_source_feed_ids_match_health_summary",
        "all_source_feed_private_only_flags_false",
    ]:
        assert aggregate_by_id(payload, check_id)["status"] == "pass"


def test_eh_a3_preserves_private_only_boundaries_and_d109_hold():
    payload = build_payload()
    assert set(payload["privateOnlyFalseFlags"]) == PRIVATE_ONLY_FALSE_FLAGS
    assert payload["summary"]["d109HoldRespected"] is True
    assert payload["summary"]["d110Started"] is False
    assert payload["summary"]["reviewerResponseConsumed"] is False
    assert payload["summary"]["dashboardUiCreated"] is False
    assert payload["summary"]["publicReadinessClaim"] is False


def test_eh_a3_blocks_public_runtime_hardware_recency_and_advantage_claims():
    payload = build_payload()
    for key in [
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
        "health_report_completeness_claim",
        "feed_recency_guarantee_claim",
        "external_source_checked",
    ]:
        assert payload["claimFlags"][key] is False


def test_eh_a3_claim_flags_are_source_freshness_guard_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_eh_a3_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EH-A3")


def test_eh_a3_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eh_a3_private_health_report_source_freshness_guard.py",
            "--build",
            "--out-dir",
            str(tmp_path / "results"),
            "--report-dir",
            str(tmp_path / "reports"),
            "--evidence-dir",
            str(tmp_path / "evidence"),
            "--command-feed-dir",
            str(tmp_path / "feeds"),
            "--strict",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "EH_A3_PRIVATE_HEALTH_REPORT_SOURCE_FRESHNESS_GUARD_OK" in proc.stdout
