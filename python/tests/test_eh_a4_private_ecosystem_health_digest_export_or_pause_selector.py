"""Tests for EH-A4 private ecosystem health digest export or pause selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eh_a4_private_ecosystem_health_digest_export_or_pause_selector import (
    CLAIM_FLAGS,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_eh_a4_consumes_eh_a3_and_exports_private_digest():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EH_A4_PRIVATE_ECOSYSTEM_HEALTH_DIGEST_EXPORT_OR_PAUSE_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "eh-a3-private-health-report-source-freshness-guard"
    assert payload["summary"]["digestExportCreated"] is True
    assert payload["summary"]["digestVisibility"] == "private"
    assert payload["privateDigest"]["visibility"] == "private"
    assert payload["privateDigest"]["snapshotDate"] == "2026-06-06"


def test_eh_a4_digest_summarizes_lanes_claims_and_verification():
    payload = build_payload()
    digest = payload["privateDigest"]
    assert len(digest["laneRows"]) == 4
    assert len(digest["blockedClaims"]) == 12
    assert digest["verificationSummary"]["selectedFeedCount"] == 4
    assert digest["verificationSummary"]["passedFixtureCheckCount"] == 6
    assert digest["verificationSummary"]["passedSourceFeedCheckCount"] == 4
    assert digest["verificationSummary"]["passedAggregateCheckCount"] == 5
    shared_lane = next(lane for lane in digest["laneRows"] if lane["laneId"] == "shared-evidence-infrastructure")
    assert shared_lane["status"] == "pause_recommended_after_eh_seed"
    assert "Pause EH seed lane" in shared_lane["nextAction"]


def test_eh_a4_selects_pause_not_dashboard_or_more_governance():
    payload = build_payload()
    assert payload["summary"]["selectedOption"] == "pause_eh_lane_as_seeded"
    assert payload["summary"]["ehLanePauseRecommended"] is True
    selected = [option for option in payload["selectorOptions"] if option["selected"]]
    assert len(selected) == 1
    assert selected[0]["optionId"] == "pause_eh_lane_as_seeded"
    rejected = {option["optionId"] for option in payload["selectorOptions"] if not option["selected"]}
    assert "continue_eh_lane_with_dashboard" in rejected
    assert "continue_eh_lane_with_more_governance_packets" in rejected


def test_eh_a4_next_work_returns_to_product_tooling_or_real_intake():
    payload = build_payload()
    assert payload["summary"]["nextRecommendedArtifact"] == (
        "SDK-A1 private SDK surface inventory or real reviewer/laptop artifact intake if supplied"
    )
    assert "SDK surface inventory" in payload["privateDigest"]["recommendedNextWork"]


def test_eh_a4_blocks_public_dashboard_runtime_hardware_and_advantage_claims():
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
        "public_digest_created",
        "external_source_checked",
        "new_health_report_checks_added",
    ]:
        assert payload["claimFlags"][key] is False


def test_eh_a4_claim_flags_are_digest_and_pause_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_eh_a4_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EH-A4")


def test_eh_a4_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eh_a4_private_ecosystem_health_digest_export_or_pause_selector.py",
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
    assert "EH_A4_PRIVATE_ECOSYSTEM_HEALTH_DIGEST_EXPORT_OR_PAUSE_SELECTOR_OK" in proc.stdout
