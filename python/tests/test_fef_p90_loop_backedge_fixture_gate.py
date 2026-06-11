"""Tests for FEF-P90 loop/back-edge fixture gate."""

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

from scripts.fef_p90_loop_backedge_fixture_gate import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    matrix_rows,
    validate_payload,
)


def test_fef_p90_records_loop_fixture_gate_without_execution():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P90_LOOP_BACKEDGE_FIXTURE_GATE_PASS"
    assert payload["decision"] == "loop_backedge_fixture_gate_recorded_support_blocked_review_hold_preserved"
    assert summary["fixtureCount"] == 4
    assert summary["loopCount"] == 4
    assert summary["backEdgeCount"] == 4
    assert summary["allRuntimeExecutionNotPerformed"] is True
    assert summary["loopRuntimeExecutionClaim"] is False


def test_fef_p90_fixture_matrix_covers_c_and_rust_while_and_for_shapes():
    rows = matrix_rows()
    assert {row["sourceLanguage"] for row in rows} == {"c", "rust"}
    assert {row["loopKind"] for row in rows} == {"while", "for", "for_range"}
    assert [row["id"] for row in rows] == [
        "c_while_accumulate_v0",
        "c_for_bounded_sum_v0",
        "rust_while_decay_v0",
        "rust_for_range_sum_v0",
    ]
    assert all(row["constructId"] == "loops_and_back_edges" for row in rows)


def test_fef_p90_preserves_p89_review_hold():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["p89ValidationPass"] is True
    assert summary["p89ReviewerDecisionRecorded"] is False
    assert summary["p89ImplementationHeldPendingReview"] is True
    assert summary["implementationChangeApproved"] is False
    assert summary["implementationChangeApplied"] is False


def test_fef_p90_blocks_boundedness_lowering_and_support():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["fixturesRequiringBoundednessPolicy"] == 4
    assert summary["allLoweringNotPerformed"] is True
    assert summary["allBoundednessPolicyNotImplemented"] is True
    assert summary["loopLoweringImplemented"] is False
    assert summary["loopBoundednessPolicyClaim"] is False
    assert summary["loopBackedgeSupportClaim"] is False
    for row in payload["loopBackedgeFixtures"]:
        assert row["requiresBoundednessPolicy"] is True
        assert row["boundednessPolicyImplemented"] is False
        assert row["loweringPerformed"] is False
        assert row["supportClaimAllowed"] is False


def test_fef_p90_release_gates_and_claim_flags_remain_false():
    payload = build_payload()
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["loop_backedge_fixture_gate"] == "recorded"
    assert gates["loop_runtime_execution"] == "not_performed"
    assert gates["loop_lowering"] == "not_performed"
    assert gates["loop_boundedness_policy"] == "blocked"
    assert gates["loop_backedge_support"] == "blocked"
    assert gates["p89_private_reviewer_hold"] == "preserved"
    assert "Loops are supported." in payload["blockedStatements"]
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p90_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P90")


def test_fef_p90_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p90_loop_backedge_fixture_gate.py",
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
    assert "FEF_P90_LOOP_BACKEDGE_FIXTURE_GATE_OK" in proc.stdout
