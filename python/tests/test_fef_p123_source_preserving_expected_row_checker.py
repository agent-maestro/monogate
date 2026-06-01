"""Tests for FEF-P123 source-preserving expected-row checker."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p123_source_preserving_expected_row_checker import (
    CLAIM_FLAGS,
    SELECTED_FIXTURE_ID,
    build_outputs,
    build_payload,
    check_row,
    checker_rows,
    validate_checker_row,
    validate_payload,
)
from scripts.fef_p122_source_preserving_expected_rows import expected_preservation_rows


SOURCE_SKETCH = "/* clamp */\nif (x < lo) {\n  return lo;\n} else {\n  return x;\n}"


def test_fef_p123_records_checker_pass_without_support_claim():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P123_SOURCE_PRESERVING_EXPECTED_ROW_CHECKER_PASS"
    assert payload["decision"] == "source_preserving_expected_row_checker_pass_support_blocked"
    assert summary["selectedFixtureId"] == SELECTED_FIXTURE_ID
    assert summary["checkerRowCount"] == 8
    assert summary["checkerPassCount"] == 8
    assert summary["checkerFailCount"] == 0
    assert summary["sourcePreservingRoundtripSupportClaim"] is False


def test_fef_p123_checker_rows_match_expected_fixture_source_sketch():
    rows = checker_rows(SOURCE_SKETCH, expected_preservation_rows())
    assert [row["checkStatus"] for row in rows] == ["pass"] * 8
    assert [row["rowId"] for row in rows] == [
        "has_block_comment",
        "comment_text_clamp",
        "if_before_else_order",
        "brace_layout_multiline",
        "return_lo_path",
        "return_x_path",
        "else_token_present",
        "line_count",
    ]
    for row in rows:
        validate_checker_row(row)


def test_fef_p123_checker_detects_mismatch_without_escalating_claims():
    row = next(item for item in expected_preservation_rows() if item["id"] == "line_count")
    checked = check_row("/* clamp */\nif (x < lo) {\n  return lo;\n}", row)
    assert checked["checkStatus"] == "fail"
    assert checked["matchedExpectedRow"] is False
    assert checked["sourceSketchChecked"] is True
    assert checked["sourceParsePerformed"] is False
    assert checked["sourceFidelityValidated"] is False
    assert checked["supportClaimAllowed"] is False


def test_fef_p123_preserves_p122_review_hold():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["p122ValidationPass"] is True
    assert summary["p122ReviewerDecisionRecorded"] is False
    assert summary["p122ImplementationHeldPendingReview"] is True
    assert summary["selectedFixtureStillBlocked"] is True


def test_fef_p123_blocks_parse_reemission_oracle_fidelity_and_support():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["allRowsSourceSketchChecked"] is True
    assert summary["allSourceParseNotPerformed"] is True
    assert summary["allSourceReemissionNotPerformed"] is True
    assert summary["allPreservationOracleNotRun"] is True
    assert summary["allSourceFidelityNotValidated"] is True
    assert summary["allRuntimeExecutionNotPerformed"] is True
    assert summary["sourceParseExecutionClaim"] is False
    assert summary["sourceReemissionClaim"] is False
    assert summary["sourceFidelityValidationClaim"] is False
    assert summary["preservationOracleClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p123_release_gates_remain_blocked():
    payload = build_payload()
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["source_preserving_expected_row_checker"] == "pass"
    assert gates["source_parse_execution"] == "not_performed"
    assert gates["source_reemission"] == "not_performed"
    assert gates["preservation_oracle"] == "not_run"
    assert gates["source_fidelity_validation"] == "not_performed"
    assert gates["source_preserving_roundtrip_support"] == "blocked"
    assert "A preservation oracle checked source fidelity." in payload["blockedStatements"]


def test_fef_p123_selected_fixture_is_p122_c_if_else_layout():
    payload = build_payload()
    fixture = payload["selectedFixture"]
    assert fixture["id"] == "c_if_else_source_layout_v0"
    assert fixture["sourceLanguage"] == "c"
    assert payload["sourceSketch"] == SOURCE_SKETCH


def test_fef_p123_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P123")


def test_fef_p123_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p123_source_preserving_expected_row_checker.py",
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
    assert "FEF_P123_SOURCE_PRESERVING_EXPECTED_ROW_CHECKER_OK" in proc.stdout
