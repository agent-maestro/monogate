"""Tests for FEF-P114 compound-condition expected samples."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p114_compound_condition_expected_samples import (
    CLAIM_FLAGS,
    SELECTED_FIXTURE_ID,
    build_outputs,
    build_payload,
    expected_samples,
    expected_value,
    validate_payload,
    validate_sample,
)


def test_fef_p114_records_expected_samples_without_execution():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P114_COMPOUND_CONDITION_EXPECTED_SAMPLES_PASS"
    assert payload["decision"] == "compound_condition_expected_samples_recorded_support_blocked"
    assert summary["selectedFixtureId"] == SELECTED_FIXTURE_ID
    assert summary["sampleCount"] == 7
    assert summary["selectedFixtureStillBlocked"] is True
    assert summary["compoundConditionRuntimeExecutionClaim"] is False
    assert summary["compoundConditionSupportClaim"] is False


def test_fef_p114_expected_samples_match_source_semantics_and_short_circuit():
    samples = expected_samples()
    assert [sample["path"] for sample in samples] == [
        "left_true_right_true_return_sum",
        "left_true_right_false_return_zero",
        "left_false_short_circuit_return_zero",
        "left_false_short_circuit_return_zero",
        "left_true_right_false_return_zero",
        "left_true_right_true_return_sum",
        "left_false_short_circuit_return_zero",
    ]
    assert [sample["rightPredicateEvaluated"] for sample in samples] == [True, True, False, False, True, True, False]
    assert [sample["expected"] for sample in samples] == [5.0, 0.0, 0.0, 0.0, 0.0, 2.0, 0.0]
    for sample in samples:
        validate_sample(sample)
        x = sample["inputs"]["x"]
        y = sample["inputs"]["y"]
        assert sample["expected"] == expected_value(x, y)


def test_fef_p114_selected_fixture_is_p113_c_and_guard_return():
    payload = build_payload()
    fixture = payload["selectedFixture"]
    assert fixture["id"] == "c_and_guard_return_v0"
    assert fixture["constructId"] == "boolean_compound_conditions"
    assert fixture["booleanOperatorKinds"] == ["and"]
    assert fixture["shortCircuitRelevant"] is True
    assert fixture["supportClaimAllowed"] is False


def test_fef_p114_blocks_boolean_policies_execution_and_support():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["rightPredicateEvaluatedCount"] == 4
    assert summary["shortCircuitExpectedCount"] == 3
    assert summary["allRuntimeExecutionNotPerformed"] is True
    assert summary["allLoweringNotPerformed"] is True
    assert summary["allPoliciesNotApplied"] is True
    assert summary["compoundConditionLoweringImplemented"] is False
    assert summary["shortCircuitPolicyImplemented"] is False
    assert summary["booleanNormalizationPolicyImplemented"] is False
    assert summary["compoundConditionSupportClaim"] is False


def test_fef_p114_release_gates_and_claim_flags_remain_false():
    payload = build_payload()
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["compound_condition_expected_samples"] == "recorded"
    assert gates["compound_condition_runtime_execution"] == "not_performed"
    assert gates["compound_condition_lowering"] == "blocked"
    assert gates["short_circuit_policy"] == "not_applied"
    assert gates["boolean_normalization_policy"] == "not_applied"
    assert gates["compound_condition_support"] == "blocked"
    assert "Compound-condition code was executed." in payload["blockedStatements"]
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p114_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P114")


def test_fef_p114_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p114_compound_condition_expected_samples.py",
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
    assert "FEF_P114_COMPOUND_CONDITION_EXPECTED_SAMPLES_OK" in proc.stdout
