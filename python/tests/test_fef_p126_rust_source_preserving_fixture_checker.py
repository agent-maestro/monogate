"""Tests for FEF-P126 Rust source-preserving fixture checker."""

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

from scripts.fef_p126_rust_source_preserving_fixture_checker import (
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


SOURCE_SKETCH = "if x > 0.0 {\n    x\n} else {\n    0.0\n}"


def test_fef_p126_records_rust_fixture_checker_without_support_claim():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P126_RUST_SOURCE_PRESERVING_FIXTURE_CHECKER_PASS"
    assert payload["decision"] == "rust_source_preserving_fixture_expected_rows_checker_negative_controls_recorded_support_blocked"
    assert summary["selectedFixtureId"] == SELECTED_FIXTURE_ID
    assert summary["selectedFixtureLanguage"] == "rust"
    assert summary["expectedRowCount"] == 7
    assert summary["checkerPassCount"] == 7
    assert summary["checkerFailCount"] == 0
    assert summary["sourcePreservingRoundtripSupportClaim"] is False


def test_fef_p126_expected_rows_match_rust_if_expression_surface():
    rows = expected_rows()
    assert [row["id"] for row in rows] == [
        "if_expression_open_line",
        "then_tail_expr_line",
        "else_opening_line",
        "else_tail_expr_line",
        "if_before_else_order",
        "else_token_present",
        "line_count",
    ]
    assert [row["category"] for row in rows] == [
        "layout",
        "expression_tail",
        "layout",
        "expression_tail",
        "token_order",
        "token_presence",
        "layout",
    ]


def test_fef_p126_checker_rows_pass_for_selected_source_sketch():
    checks = checker_rows(SOURCE_SKETCH, expected_rows())
    assert [row["checkStatus"] for row in checks] == ["pass"] * 7
    assert all(row["sourceParsePerformed"] is False for row in checks)
    assert all(row["sourceFidelityValidated"] is False for row in checks)
    assert all(row["supportClaimAllowed"] is False for row in checks)


def test_fef_p126_negative_controls_fail_closed_with_expected_rows():
    controls = negative_control_results(expected_rows())
    assert [control["failedRows"] for control in controls] == [
        ["else_opening_line", "if_before_else_order", "else_token_present", "line_count"],
        ["then_tail_expr_line"],
        ["if_expression_open_line", "then_tail_expr_line", "else_opening_line", "else_tail_expr_line", "line_count"],
    ]
    assert [len(control["passedRows"]) for control in controls] == [3, 6, 2]
    assert [len(control["failedRows"]) for control in controls] == [4, 1, 5]
    for control in controls:
        assert control["failClosed"] is True
        assert control["expectedFailedRowsMatched"] is True
        validate_control(control)


def test_fef_p126_selected_fixture_is_p121_rust_if_expression():
    payload = build_payload()
    fixture = payload["selectedFixture"]
    assert fixture["id"] == "rust_if_expr_source_layout_v0"
    assert fixture["sourceLanguage"] == "rust"
    assert fixture["shape"] == "rust_if_expression_layout"
    assert fixture["sourceSketch"] == SOURCE_SKETCH
    assert fixture["supportClaimAllowed"] is False


def test_fef_p126_preserves_p125_review_hold():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["p125ValidationPass"] is True
    assert summary["p125ReviewerDecisionRecorded"] is False
    assert summary["p125ImplementationHeldPendingReview"] is True
    assert summary["selectedFixtureStillBlocked"] is True


def test_fef_p126_blocks_parse_reemission_oracle_fidelity_and_support():
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


def test_fef_p126_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P126")


def test_fef_p126_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p126_rust_source_preserving_fixture_checker.py",
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
    assert "FEF_P126_RUST_SOURCE_PRESERVING_FIXTURE_CHECKER_OK" in proc.stdout
