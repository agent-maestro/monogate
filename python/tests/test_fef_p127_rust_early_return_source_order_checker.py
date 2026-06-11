"""Tests for FEF-P127 Rust early-return source-order checker."""

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

from scripts.fef_p127_rust_early_return_source_order_checker import (
    CLAIM_FLAGS,
    SELECTED_FIXTURE_ID,
    build_outputs,
    build_payload,
    checker_rows,
    expected_rows,
    negative_control_results,
    validate_control,
    validate_payload,
)


SOURCE_SKETCH = "if x < lo {\n    return lo;\n}\n// fall through\nx"


def test_fef_p127_records_rust_early_return_checker_without_support_claim():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P127_RUST_EARLY_RETURN_SOURCE_ORDER_CHECKER_PASS"
    assert payload["decision"] == "rust_early_return_source_order_expected_rows_checker_negative_controls_recorded_support_blocked"
    assert summary["selectedFixtureId"] == SELECTED_FIXTURE_ID
    assert summary["selectedFixtureLanguage"] == "rust"
    assert summary["expectedRowCount"] == 8
    assert summary["checkerPassCount"] == 8
    assert summary["checkerFailCount"] == 0
    assert summary["sourcePreservingRoundtripSupportClaim"] is False


def test_fef_p127_expected_rows_match_rust_early_return_surface():
    rows = expected_rows()
    assert [row["id"] for row in rows] == [
        "if_guard_open_line",
        "return_lo_statement",
        "guard_closing_brace",
        "fallthrough_comment",
        "fallthrough_tail_expr",
        "return_before_fallthrough_order",
        "else_token_absent",
        "line_count",
    ]
    assert [row["category"] for row in rows] == [
        "layout",
        "return_path",
        "layout",
        "comment",
        "expression_tail",
        "token_order",
        "token_absence",
        "layout",
    ]


def test_fef_p127_checker_rows_pass_for_selected_source_sketch():
    checks = checker_rows(SOURCE_SKETCH, expected_rows())
    assert [row["checkStatus"] for row in checks] == ["pass"] * 8
    assert all(row["sourceParsePerformed"] is False for row in checks)
    assert all(row["sourceFidelityValidated"] is False for row in checks)
    assert all(row["supportClaimAllowed"] is False for row in checks)


def test_fef_p127_negative_controls_fail_closed_with_expected_rows():
    controls = negative_control_results(expected_rows())
    assert [control["failedRows"] for control in controls] == [
        ["fallthrough_comment", "return_before_fallthrough_order", "line_count"],
        ["return_lo_statement", "return_before_fallthrough_order"],
        ["fallthrough_comment", "fallthrough_tail_expr", "return_before_fallthrough_order", "else_token_absent"],
    ]
    assert [len(control["passedRows"]) for control in controls] == [5, 6, 4]
    assert [len(control["failedRows"]) for control in controls] == [3, 2, 4]
    for control in controls:
        assert control["failClosed"] is True
        assert control["expectedFailedRowsMatched"] is True
        validate_control(control)


def test_fef_p127_selected_fixture_is_p121_rust_early_return():
    payload = build_payload()
    fixture = payload["selectedFixture"]
    assert fixture["id"] == "rust_early_return_source_order_v0"
    assert fixture["sourceLanguage"] == "rust"
    assert fixture["shape"] == "rust_early_return_source_order"
    assert fixture["sourceSketch"] == SOURCE_SKETCH
    assert fixture["supportClaimAllowed"] is False


def test_fef_p127_preserves_p126_review_hold():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["p126ValidationPass"] is True
    assert summary["p126ReviewerDecisionRecorded"] is False
    assert summary["p126ImplementationHeldPendingReview"] is True
    assert summary["selectedFixtureStillBlocked"] is True


def test_fef_p127_blocks_parse_reemission_oracle_fidelity_and_support():
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


def test_fef_p127_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P127")


def test_fef_p127_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p127_rust_early_return_source_order_checker.py",
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
    assert "FEF_P127_RUST_EARLY_RETURN_SOURCE_ORDER_CHECKER_OK" in proc.stdout
