"""Tests for FEF-P124 source-preserving negative-control checker."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p124_source_preserving_negative_control_checker import (
    CLAIM_FLAGS,
    NEGATIVE_CONTROLS,
    build_outputs,
    build_payload,
    negative_control_results,
    validate_control,
    validate_payload,
)


def test_fef_p124_records_negative_controls_fail_closed():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P124_SOURCE_PRESERVING_NEGATIVE_CONTROL_CHECKER_PASS"
    assert payload["decision"] == "source_preserving_negative_controls_fail_closed_support_blocked"
    assert summary["negativeControlCount"] == 4
    assert summary["negativeControlRowCheckCount"] == 32
    assert summary["negativeControlExpectedFailureCount"] == 12
    assert summary["negativeControlPassRowCount"] == 20
    assert summary["allNegativeControlsFailClosed"] is True


def test_fef_p124_negative_controls_match_expected_failed_rows():
    controls = negative_control_results()
    assert [control["id"] for control in controls] == [control["id"] for control in NEGATIVE_CONTROLS]
    assert [control["failedRows"] for control in controls] == [
        ["has_block_comment", "comment_text_clamp", "line_count"],
        ["if_before_else_order", "brace_layout_multiline", "else_token_present", "line_count"],
        ["return_lo_path"],
        ["brace_layout_multiline", "return_lo_path", "return_x_path", "line_count"],
    ]
    for control in controls:
        assert control["failClosed"] is True
        assert control["expectedFailedRowsMatched"] is True
        validate_control(control)


def test_fef_p124_negative_controls_keep_some_rows_passing():
    controls = negative_control_results()
    pass_counts = [len(control["passedRows"]) for control in controls]
    fail_counts = [len(control["failedRows"]) for control in controls]
    assert pass_counts == [5, 4, 7, 4]
    assert fail_counts == [3, 4, 1, 4]
    assert sum(pass_counts) == 20
    assert sum(fail_counts) == 12


def test_fef_p124_preserves_p123_review_hold():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["p123ValidationPass"] is True
    assert summary["p123ReviewerDecisionRecorded"] is False
    assert summary["p123ImplementationHeldPendingReview"] is True
    assert summary["selectedFixtureStillBlocked"] is True


def test_fef_p124_blocks_parse_reemission_oracle_fidelity_and_support():
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


def test_fef_p124_release_gates_remain_blocked():
    payload = build_payload()
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["source_preserving_negative_controls"] == "fail_closed_pass"
    assert gates["source_parse_execution"] == "not_performed"
    assert gates["source_reemission"] == "not_performed"
    assert gates["preservation_oracle"] == "not_run"
    assert gates["source_fidelity_validation"] == "not_performed"
    assert gates["source_preserving_roundtrip_support"] == "blocked"
    assert "A preservation oracle checked source fidelity." in payload["blockedStatements"]


def test_fef_p124_control_sources_are_intentionally_mutated():
    controls = negative_control_results()
    assert controls[0]["mutation"] == "remove_leading_block_comment"
    assert controls[1]["mutation"] == "remove_else_token_and_block_layout"
    assert controls[2]["mutation"] == "change_low_return_statement"
    assert controls[3]["mutation"] == "collapse_multiline_layout"
    assert all(control["supportClaimAllowed"] is False for control in controls)


def test_fef_p124_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P124")


def test_fef_p124_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p124_source_preserving_negative_control_checker.py",
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
    assert "FEF_P124_SOURCE_PRESERVING_NEGATIVE_CONTROL_CHECKER_OK" in proc.stdout
