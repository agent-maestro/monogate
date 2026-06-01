"""Tests for FEF-P122 source-preserving expected rows."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p122_source_preserving_expected_rows import (
    CLAIM_FLAGS,
    SELECTED_FIXTURE_ID,
    build_outputs,
    build_payload,
    expected_preservation_rows,
    validate_payload,
    validate_row,
)


def test_fef_p122_records_expected_rows_without_execution():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P122_SOURCE_PRESERVING_EXPECTED_ROWS_PASS"
    assert payload["decision"] == "source_preserving_expected_rows_recorded_support_blocked"
    assert summary["selectedFixtureId"] == SELECTED_FIXTURE_ID
    assert summary["expectedRowCount"] == 8
    assert summary["selectedFixtureStillBlocked"] is True
    assert summary["sourcePreservingRoundtripSupportClaim"] is False


def test_fef_p122_expected_rows_name_preservation_surface():
    rows = expected_preservation_rows()
    assert [row["id"] for row in rows] == [
        "has_block_comment",
        "comment_text_clamp",
        "if_before_else_order",
        "brace_layout_multiline",
        "return_lo_path",
        "return_x_path",
        "else_token_present",
        "line_count",
    ]
    assert [row["category"] for row in rows] == [
        "comment",
        "comment",
        "token_order",
        "layout",
        "return_path",
        "return_path",
        "token_presence",
        "layout",
    ]
    for row in rows:
        validate_row(row)


def test_fef_p122_selected_fixture_is_p121_c_if_else_layout():
    payload = build_payload()
    fixture = payload["selectedFixture"]
    assert fixture["id"] == "c_if_else_source_layout_v0"
    assert fixture["sourceLanguage"] == "c"
    assert fixture["shape"] == "if_else_with_layout_and_comment"
    assert fixture["sourceSketch"] == "/* clamp */\nif (x < lo) {\n  return lo;\n} else {\n  return x;\n}"
    assert fixture["supportClaimAllowed"] is False


def test_fef_p122_category_counts_are_bounded():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["commentExpectationCount"] == 2
    assert summary["layoutExpectationCount"] == 2
    assert summary["tokenExpectationCount"] == 2
    assert summary["returnPathExpectationCount"] == 2
    assert summary["categoryCounts"] == {
        "comment": 2,
        "layout": 2,
        "return_path": 2,
        "token_order": 1,
        "token_presence": 1,
    }


def test_fef_p122_preserves_p121_review_hold():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["p121ValidationPass"] is True
    assert summary["p121ReviewerDecisionRecorded"] is False
    assert summary["p121ImplementationHeldPendingReview"] is True


def test_fef_p122_blocks_parse_reemission_oracle_fidelity_and_support():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["allSourceParseNotPerformed"] is True
    assert summary["allSourceReemissionNotPerformed"] is True
    assert summary["allPreservationOracleNotRun"] is True
    assert summary["allSourceFidelityNotValidated"] is True
    assert summary["allRuntimeExecutionNotPerformed"] is True
    assert summary["sourceParseExecutionClaim"] is False
    assert summary["sourceReemissionClaim"] is False
    assert summary["sourceFidelityValidationClaim"] is False
    assert summary["localPreservationOracleClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p122_release_gates_remain_blocked():
    payload = build_payload()
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["source_preserving_expected_rows"] == "recorded"
    assert gates["source_parse_execution"] == "not_performed"
    assert gates["source_reemission"] == "not_performed"
    assert gates["preservation_oracle"] == "not_run"
    assert gates["source_fidelity_validation"] == "not_performed"
    assert gates["source_preserving_roundtrip_support"] == "blocked"
    assert "A preservation oracle checked source fidelity." in payload["blockedStatements"]


def test_fef_p122_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P122")


def test_fef_p122_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p122_source_preserving_expected_rows.py",
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
    assert "FEF_P122_SOURCE_PRESERVING_EXPECTED_ROWS_OK" in proc.stdout
