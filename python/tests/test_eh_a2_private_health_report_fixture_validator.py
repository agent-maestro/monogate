"""Tests for EH-A2 private health report fixture validator."""

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

from scripts.eh_a2_private_health_report_fixture_validator import (
    CLAIM_FLAGS,
    EXPECTED_BLOCKED_CLAIMS,
    EXPECTED_FEED_IDS,
    EXPECTED_LANE_IDS,
    FORBIDDEN_TRUE_FLAGS,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def check_by_id(payload, check_id: str):
    return next(item for item in payload["fixtureChecks"] if item["checkId"] == check_id)


def test_eh_a2_consumes_eh_a1_and_validates_expected_sets():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EH_A2_PRIVATE_HEALTH_REPORT_FIXTURE_VALIDATOR_PASS"
    assert payload["sourceArtifact"] == "eh-a1-private-ecosystem-health-report-seed"
    assert set(payload["expectedFeedIds"]) == EXPECTED_FEED_IDS
    assert set(payload["expectedLaneIds"]) == EXPECTED_LANE_IDS
    assert set(payload["expectedBlockedClaims"]) == EXPECTED_BLOCKED_CLAIMS


def test_eh_a2_fixture_checks_all_pass():
    payload = build_payload()
    assert payload["summary"]["fixtureCheckCount"] == 6
    assert payload["summary"]["passedFixtureCheckCount"] == 6
    for check_id in [
        "expected_feed_ids_present",
        "expected_lane_ids_present",
        "expected_blocked_claims_present",
        "d109_hold_preserved",
        "forbidden_claim_flags_remain_false",
        "next_action_points_to_eh_a2",
    ]:
        assert check_by_id(payload, check_id)["status"] == "pass"


def test_eh_a2_preserves_d109_hold_and_next_action():
    payload = build_payload()
    assert check_by_id(payload, "d109_hold_preserved")["laneStatus"] == "held"
    assert check_by_id(payload, "d109_hold_preserved")["d110BlockedUntilResponseExists"] is True
    assert payload["summary"]["d109HoldRespected"] is True
    assert payload["summary"]["d110Started"] is False
    assert payload["summary"]["reviewerResponseConsumed"] is False
    assert payload["summary"]["nextRecommendedArtifact"] == "EH-A3 private health report source freshness guard"


def test_eh_a2_blocks_dashboard_public_runtime_hardware_and_advantage_claims():
    payload = build_payload()
    assert set(payload["forbiddenTrueFlags"]) == FORBIDDEN_TRUE_FLAGS
    for key in FORBIDDEN_TRUE_FLAGS | {"schema_validator_implemented", "dashboard_renderer_implemented"}:
        assert payload["claimFlags"][key] is False


def test_eh_a2_claim_flags_are_fixture_validator_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_eh_a2_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EH-A2")


def test_eh_a2_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eh_a2_private_health_report_fixture_validator.py",
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
    assert "EH_A2_PRIVATE_HEALTH_REPORT_FIXTURE_VALIDATOR_OK" in proc.stdout
