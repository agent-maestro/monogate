"""Tests for FEF-P113 compound-condition fixture gate."""

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

from scripts.fef_p113_compound_condition_fixture_gate import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    matrix_rows,
    validate_payload,
)


def test_fef_p113_records_compound_condition_fixture_gate_without_execution():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P113_COMPOUND_CONDITION_FIXTURE_GATE_PASS"
    assert payload["decision"] == "compound_condition_fixture_gate_recorded_support_blocked_review_hold_preserved"
    assert summary["fixtureCount"] == 4
    assert summary["operatorKinds"] == ["and", "or"]
    assert summary["totalAtomicPredicateCount"] == 9
    assert summary["allRuntimeExecutionNotPerformed"] is True


def test_fef_p113_fixture_matrix_covers_c_and_rust_boolean_shapes():
    rows = matrix_rows()
    assert {row["sourceLanguage"] for row in rows} == {"c", "rust"}
    assert [row["id"] for row in rows] == [
        "c_and_guard_return_v0",
        "c_or_clamp_guard_v0",
        "rust_and_if_expr_v0",
        "rust_mixed_and_or_return_v0",
    ]
    assert all(row["constructId"] == "boolean_compound_conditions" for row in rows)
    assert {kind for row in rows for kind in row["booleanOperatorKinds"]} == {"and", "or"}
    assert all(row["shortCircuitRelevant"] is True for row in rows)


def test_fef_p113_preserves_p112_review_hold():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["p112ValidationPass"] is True
    assert summary["p112ReviewerDecisionRecorded"] is False
    assert summary["p112ImplementationHeldPendingReview"] is True
    assert summary["implementationChangeApproved"] is False
    assert summary["implementationChangeApplied"] is False


def test_fef_p113_blocks_boolean_policies_lowering_and_support():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["fixturesWithShortCircuitSemantics"] == 4
    assert summary["allLoweringNotPerformed"] is True
    assert summary["allPoliciesNotImplemented"] is True
    assert summary["compoundConditionLoweringImplemented"] is False
    assert summary["compoundConditionSupportClaim"] is False
    for row in payload["compoundConditionFixtures"]:
        assert row["shortCircuitPolicyImplemented"] is False
        assert row["booleanNormalizationPolicyImplemented"] is False
        assert row["loweringPerformed"] is False
        assert row["supportClaimAllowed"] is False


def test_fef_p113_release_gates_and_claim_flags_remain_false():
    payload = build_payload()
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["compound_condition_fixture_gate"] == "recorded"
    assert gates["compound_condition_runtime_execution"] == "not_performed"
    assert gates["compound_condition_lowering"] == "not_performed"
    assert gates["short_circuit_policy"] == "blocked"
    assert gates["boolean_normalization_policy"] == "blocked"
    assert gates["compound_condition_support"] == "blocked"
    assert gates["p112_private_reviewer_hold"] == "preserved"
    assert "Compound-condition constructs are supported." in payload["blockedStatements"]
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p113_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P113")


def test_fef_p113_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p113_compound_condition_fixture_gate.py",
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
    assert "FEF_P113_COMPOUND_CONDITION_FIXTURE_GATE_OK" in proc.stdout
