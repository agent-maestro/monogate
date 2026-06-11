"""Tests for FEF-P71 compound-condition expected samples."""

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

from scripts.fef_p71_compound_condition_expected_samples import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    expected_value,
    validate_payload,
    validate_sample,
)


def test_fef_p71_records_source_semantics_samples_without_support_claim():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P71_COMPOUND_CONDITION_EXPECTED_SAMPLES_PASS"
    assert payload["decision"] == "compound_condition_expected_samples_recorded_support_blocked"
    assert summary["p70ValidationPass"] is True
    assert summary["selectedFixtureId"] == "c_and_short_circuit_guard_v0"
    assert summary["selectedFixtureStillBlocked"] is True
    assert summary["sampleCount"] == 7
    assert summary["compoundConditionSupportClaim"] is False


def test_fef_p71_samples_cover_true_short_circuit_and_guard_paths():
    payload = build_payload()
    samples = payload["expectedSamples"]
    paths = [sample["path"] for sample in samples]
    assert paths.count("and_true_division") == 3
    assert paths.count("left_false_short_circuit") == 3
    assert paths.count("right_false_zero_denominator_guard") == 1
    assert payload["summary"]["rightConditionEvaluationCount"] == 4
    assert payload["summary"]["divisionPerformedCount"] == 3
    assert all(sample["sourceSemanticsOnly"] is True for sample in samples)


def test_fef_p71_expected_values_match_source_semantics():
    payload = build_payload()
    for sample in payload["expectedSamples"]:
        validate_sample(sample)
        x = sample["inputs"]["x"]
        y = sample["inputs"]["y"]
        assert sample["expected"] == expected_value(x, y)
        if sample["path"] == "left_false_short_circuit":
            assert sample["leftCondition"] is False
            assert sample["rightConditionEvaluated"] is False
            assert sample["rightCondition"] is None
            assert sample["divisionPerformed"] is False
        if sample["path"] == "right_false_zero_denominator_guard":
            assert sample["leftCondition"] is True
            assert sample["rightConditionEvaluated"] is True
            assert sample["rightCondition"] is False
            assert sample["divisionPerformed"] is False


def test_fef_p71_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["compound_condition_expected_samples"] == "recorded"
    assert gates["compound_condition_runtime_execution"] == "not_performed"
    assert gates["compound_condition_lowering"] == "blocked"
    assert gates["compound_condition_support"] == "blocked"
    assert gates["short_circuit_semantics_implementation"] == "not_performed"
    assert "Short-circuit condition semantics are implemented." in payload["blockedStatements"]
    assert summary["compoundConditionRuntimeExecutionClaim"] is False
    assert summary["compoundConditionLoweringClaim"] is False
    assert summary["compoundConditionSupportClaim"] is False
    assert summary["shortCircuitSemanticsImplemented"] is False
    assert summary["controlFlowIrImplemented"] is False
    assert summary["frontendLoweringChanged"] is False
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["branchControlFlowReingestClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p71_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P71")


def test_fef_p71_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p71_compound_condition_expected_samples.py",
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
    assert "FEF_P71_COMPOUND_CONDITION_EXPECTED_SAMPLES_OK" in proc.stdout
