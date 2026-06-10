"""Tests for PUB-R0 canonical brake-side ledger generator."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.pub_r0_brake_side_ledger_generator import (
    CLAIM_FLAGS,
    STANDING_CLAIM_RULE,
    TRUE_CLAIM_FLAGS,
    assert_standing_rule_matches_welcome,
    build_outputs,
    build_payload,
    parse_lean_status_text,
    validate_payload,
)


FAKE_LEAN_TEXT = (
    "  LEAN:        468 theorems, 5 sorries, 18 files (live)\n"
    "  MACHLIB:     3418 records, 279 files (8 core / 271 discovered), "
    "0 core sorries, 222 discovered sorries, 18971 lines (live)\n"
)


def test_pub_r0_builds_canonical_ledger_from_canonical_sources():
    payload = build_payload(lean_status_text=FAKE_LEAN_TEXT)
    validate_payload(payload)
    assert payload["status"] == "PUB_R0_BRAKE_SIDE_LEDGER_GENERATOR_PASS"
    ledger = payload["ledger"]
    assert ledger["standingClaimRule"] == STANDING_CLAIM_RULE
    assert ledger["heldLanes"], "held lanes must be enumerated"
    assert ledger["retractedClaims"], "retracted claims must be enumerated"
    assert ledger["negativeResults"], "negative results must be enumerated"
    assert ledger["leanStatus"]["leanTheoremCount"] == 468
    assert ledger["leanStatus"]["leanSorryCount"] == 5
    assert ledger["leanStatus"]["machlibCoreSorryCount"] == 0
    assert ledger["leanStatus"]["machlibDiscoveredSorryCount"] == 222


def test_pub_r0_held_lanes_carry_required_fields():
    payload = build_payload(lean_status_text=FAKE_LEAN_TEXT)
    for row in payload["ledger"]["heldLanes"]:
        assert row["laneId"]
        assert row["holdingArtifactId"]
        assert row["oneLineReason"]
        assert (
            row["oneLineReason"].startswith("held")
            or row["oneLineReason"].startswith("paused")
            or row["oneLineReason"].startswith("pending")
        )


def test_pub_r0_claims_carry_id_source_and_one_line_text():
    payload = build_payload(lean_status_text=FAKE_LEAN_TEXT)
    for row in payload["ledger"]["retractedClaims"] + payload["ledger"]["negativeResults"]:
        assert row["claimId"].startswith("claim:")
        assert row["source"]
        assert row["oneLineText"]
        # one-line text never contains newlines
        assert "\n" not in row["oneLineText"]


def test_pub_r0_standing_rule_matches_welcome_md_verbatim():
    # Will raise if STANDING_CLAIM_RULE has drifted from WELCOME.md
    assert_standing_rule_matches_welcome()


def test_pub_r0_parse_lean_status_text_handles_canonical_summary():
    parsed = parse_lean_status_text(FAKE_LEAN_TEXT)
    assert parsed == {
        "leanTheoremCount": 468,
        "leanSorryCount": 5,
        "machlibCoreSorryCount": 0,
        "machlibDiscoveredSorryCount": 222,
    }


def test_pub_r0_boundaries_closed():
    payload = build_payload(lean_status_text=FAKE_LEAN_TEXT)
    summary = payload["summary"]
    assert summary["pageRendered"] is False
    assert summary["pagePublished"] is False
    assert summary["htmlRendered"] is False
    assert summary["liveDeployExecuted"] is False
    assert summary["driftGuardImplemented"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["trainingCostEstimatorReopened"] is False
    assert summary["productRoadmapReopened"] is False
    assert summary["laptopOwnedRepoTouched"] is False


def test_pub_r0_blocks_publication_and_substance_claims():
    payload = build_payload(lean_status_text=FAKE_LEAN_TEXT)
    for key in [
        "page_rendered",
        "page_published",
        "html_rendered",
        "live_deploy_executed",
        "drift_guard_implemented",
        "post_deploy_probe_executed",
        "dashboard_ui_created",
        "public_dashboard_created",
        "public_surface_updated",
        "public_readiness_claim",
        "public_copy_approved",
        "ledger_completeness_claim",
        "renderer_correctness_claim",
        "visualization_quality_claim",
        "training_cost_estimator_reopened",
        "product_roadmap_reopened",
        "atlas_public_promotion",
        "public_math_promotion",
        "d110_started",
        "reviewer_response_consumed",
        "reviewer_approval_recorded",
        "electronics_inbox_reopened",
        "electronics_repo_touched",
        "laptop_owned_repo_touched",
        "machlib_file_changed",
        "lean_typecheck_performed",
        "runtime_lowering_changed",
        "runtime_performance_claim",
        "compiler_correctness_claim",
        "hardware_readiness_claim",
        "silicon_readiness_claim",
        "broad_eml_advantage_claim",
    ]:
        assert payload["claimFlags"][key] is False


def test_pub_r0_claim_flags_are_generator_only():
    payload = build_payload(lean_status_text=FAKE_LEAN_TEXT)
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_pub_r0_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        lean_status_text=FAKE_LEAN_TEXT,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# PUB-R0")
    assert "Held Lanes" in report
    assert "Retracted Claims" in report
    assert "Negative Results" in report
    assert "Standing Claim Rule" in report
    assert STANDING_CLAIM_RULE.split(".")[0] in report
