"""Tests for EH-A1 private ecosystem health report seed."""

from __future__ import annotations

import pytest

# Blanket-marked heavy: CLI-contract test (subprocess.run of a
# script that loads large JSON evidence). Skipped from the fast
# dev loop via `pytest -m "not heavy"`; runs in CI by default.
# A follow-up measurement pass will UN-mark individual fast files.
pytestmark = pytest.mark.heavy

import json
from pathlib import Path
import subprocess
import sys

from scripts.eh_a1_private_ecosystem_health_report_seed import (
    CLAIM_FLAGS,
    FEED_FILES,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def lane_by_id(payload, lane_id: str):
    return next(item for item in payload["activeLanes"] if item["laneId"] == lane_id)


def feed_by_id(payload, feed_id: str):
    return next(item for item in payload["feedSummaries"] if item["feedId"] == feed_id)


def test_eh_a1_consumes_ea_a2_and_selected_feeds():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EH_A1_PRIVATE_ECOSYSTEM_HEALTH_REPORT_SEED_PASS"
    assert payload["sourceArtifact"] == "ea-a2-single-artifact-toolkit-migration-smoke"
    assert payload["summary"]["selectedFeedCount"] == len(FEED_FILES)
    assert {feed["feedId"] for feed in payload["feedSummaries"]} == {
        "eml_d109_private_reviewer_response_availability_guard_feed",
        "prod_a6_training_cost_estimator_fixture_packet_feed",
        "ea_a1_shared_evidence_artifact_toolkit_seed_feed",
        "ea_a2_single_artifact_toolkit_migration_smoke_feed",
    }


def test_eh_a1_records_active_lanes_and_d109_hold():
    payload = build_payload()
    assert payload["summary"]["activeLaneCount"] == 4
    d_series_lane = lane_by_id(payload, "d-series-private-reviewer")
    assert d_series_lane["status"] == "held"
    assert d_series_lane["blocker"] == "actual_private_reviewer_response_required"
    d109_feed = feed_by_id(payload, "eml_d109_private_reviewer_response_availability_guard_feed")
    assert d109_feed["d110BlockedUntilResponseExists"] is True
    assert payload["summary"]["d109HoldRespected"] is True
    assert payload["summary"]["d110Started"] is False
    assert payload["summary"]["reviewerResponseConsumed"] is False


def test_eh_a1_records_blocked_claims():
    payload = build_payload()
    claims = {item["claim"] for item in payload["blockedClaims"]}
    assert payload["summary"]["blockedClaimCount"] == 12
    assert "public readiness" in claims
    assert "compiler correctness" in claims
    assert "runtime performance" in claims
    assert "training savings" in claims
    assert "D110 reviewer response consumed" in claims


def test_eh_a1_blocks_public_dashboard_runtime_hardware_and_advantage_claims():
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
    ]:
        assert payload["claimFlags"][key] is False


def test_eh_a1_feed_summaries_expose_next_actions_and_guard_flags():
    payload = build_payload()
    for feed in payload["feedSummaries"]:
        assert feed["nextAction"]
        assert feed["sourcePath"].startswith("command_center_feeds/")
        assert isinstance(feed["trueClaimFlags"], list)
        assert isinstance(feed["blockedClaimFlags"], list)
    prod_a6 = feed_by_id(payload, "prod_a6_training_cost_estimator_fixture_packet_feed")
    assert prod_a6["trainingSavingsClaim"] is False
    assert prod_a6["runtimePerformanceClaim"] is False
    assert prod_a6["compilerCorrectnessClaim"] is False


def test_eh_a1_claim_flags_are_private_health_seed_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_eh_a1_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EH-A1")


def test_eh_a1_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eh_a1_private_ecosystem_health_report_seed.py",
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
    assert "EH_A1_PRIVATE_ECOSYSTEM_HEALTH_REPORT_SEED_OK" in proc.stdout
