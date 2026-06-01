"""Tests for FEF-P83 compound-condition short-circuit execution policy."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p83_compound_condition_short_circuit_execution_policy import (
    CLAIM_FLAGS,
    build_execution_policy,
    build_outputs,
    build_payload,
    classify_policy_row,
    read_json,
    validate_payload,
    P77_RESULT,
    P82_RESULT,
)


def test_fef_p83_records_policy_and_keeps_execution_blocked():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P83_COMPOUND_CONDITION_SHORT_CIRCUIT_EXECUTION_POLICY_PASS"
    assert payload["decision"] == "selected_short_circuit_safe_execution_policy_recorded_execution_blocked"
    assert summary["selectedFixtureId"] == "c_and_short_circuit_guard_v0"
    assert summary["rowCount"] == 7
    assert summary["futureComparisonAllowedRowCount"] == 5
    assert summary["futureComparisonBlockedRowCount"] == 2
    assert summary["executionPerformed"] is False
    assert summary["runtimeComparisonPerformed"] is False


def test_fef_p83_policy_blocks_zero_denominator_rows():
    payload = build_payload()
    policy = payload["executionPolicy"]
    assert policy["allowedSampleIds"] == ["sample_00", "sample_02", "sample_04", "sample_05", "sample_06"]
    assert policy["blockedSampleIds"] == ["sample_01", "sample_03"]
    blocked_rows = [row for row in policy["executionPolicyRows"] if row["futureComparisonBlocked"]]
    assert {row["path"] for row in blocked_rows} == {
        "left_false_short_circuit",
        "right_false_zero_denominator_guard",
    }
    assert all(row["inputs"]["y"] == 0.0 for row in blocked_rows)


def test_fef_p83_classify_policy_row_uses_denominator_guard():
    safe = classify_policy_row(
        {
            "sampleId": "safe",
            "path": "and_true_division",
            "inputs": {"x": 2.0, "y": 4.0},
            "expected": 0.5,
            "observed": 0.5,
            "pass": True,
            "rhsEvaluated": True,
        }
    )
    blocked = classify_policy_row(
        {
            "sampleId": "blocked",
            "path": "left_false_short_circuit",
            "inputs": {"x": -2.0, "y": 0.0},
            "expected": 0.0,
            "observed": 0.0,
            "pass": True,
            "rhsEvaluated": False,
        }
    )
    assert safe["futureComparisonAllowed"] is True
    assert safe["policyStatus"] == "eligible_for_future_eager_eml_comparison"
    assert blocked["futureComparisonBlocked"] is True
    assert blocked["policyStatus"] == "blocked_by_short_circuit_eager_division"


def test_fef_p83_policy_sources_p82_and_p77():
    p82_payload = read_json(P82_RESULT)
    p77_payload = read_json(P77_RESULT)
    policy = build_execution_policy(p82_payload, p77_payload)
    assert policy["sourceObligation"] == "short_circuit_eager_division_semantic_obligation"
    assert policy["rowCount"] == 7
    assert policy["futureComparisonAllowedRowCount"] == 5
    assert policy["futureComparisonBlockedRowCount"] == 2
    assert policy["executionPerformed"] is False


def test_fef_p83_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_short_circuit_safe_execution_policy"] == "recorded"
    assert gates["selected_reingest_parse"] == "selected_probe_pass_from_p82"
    assert gates["selected_reingest_execution"] == "blocked_not_executed"
    assert gates["blocked_zero_denominator_rows"] == "requires_guarded_division_or_review_only_policy"
    assert "Compound-condition re-ingest is supported." in payload["blockedStatements"]
    assert summary["compoundConditionReingestSupported"] is False
    assert summary["compoundConditionLoweringImplemented"] is False
    assert summary["compoundConditionSupportClaim"] is False
    assert summary["shortCircuitSemanticsImplemented"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p83_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P83")


def test_fef_p83_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p83_compound_condition_short_circuit_execution_policy.py",
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
    assert "FEF_P83_COMPOUND_CONDITION_SHORT_CIRCUIT_EXECUTION_POLICY_OK" in proc.stdout
