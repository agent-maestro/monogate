"""Tests for FEF-P91 loop/back-edge expected samples."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p91_loop_backedge_expected_samples import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    expected_value,
    validate_payload,
    validate_sample,
)


def test_fef_p91_records_source_semantics_samples_without_support_claim():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P91_LOOP_BACKEDGE_EXPECTED_SAMPLES_PASS"
    assert payload["decision"] == "loop_backedge_expected_samples_recorded_support_blocked"
    assert summary["p90ValidationPass"] is True
    assert summary["selectedFixtureId"] == "c_while_accumulate_v0"
    assert summary["selectedFixtureStillBlocked"] is True
    assert summary["sampleCount"] == 7
    assert summary["loopBackedgeSupportClaim"] is False


def test_fef_p91_samples_cover_zero_single_and_multi_iteration_paths():
    payload = build_payload()
    samples = payload["expectedSamples"]
    paths = [sample["path"] for sample in samples]
    assert paths.count("zero_iterations") == 2
    assert paths.count("single_iteration") == 1
    assert paths.count("multi_iteration") == 4
    assert payload["summary"]["maxIterationCount"] == 8
    assert payload["summary"]["totalBackEdgeTakenCount"] == 21
    assert all(sample["sourceSemanticsOnly"] is True for sample in samples)


def test_fef_p91_expected_values_match_source_semantics():
    payload = build_payload()
    for sample in payload["expectedSamples"]:
        validate_sample(sample)
        x = sample["inputs"]["x"]
        n = int(sample["inputs"]["n"])
        assert sample["expected"] == expected_value(x, n)
        assert sample["runtimeExecutionPerformed"] is False
        assert sample["boundednessPolicyApplied"] is False
        if sample["path"] == "zero_iterations":
            assert sample["iterationCount"] == 0
            assert sample["loopConditionInitiallyTrue"] is False


def test_fef_p91_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["loop_backedge_expected_samples"] == "recorded"
    assert gates["loop_runtime_execution"] == "not_performed"
    assert gates["loop_lowering"] == "blocked"
    assert gates["loop_boundedness_policy"] == "not_applied"
    assert gates["loop_backedge_support"] == "blocked"
    assert gates["p89_private_reviewer_hold"] == "preserved"
    assert "Loop fixtures were executed." in payload["blockedStatements"]
    assert summary["loopRuntimeExecutionClaim"] is False
    assert summary["loopLoweringClaim"] is False
    assert summary["loopBackedgeSupportClaim"] is False
    assert summary["loopBoundednessPolicyClaim"] is False
    assert summary["controlFlowIrImplemented"] is False
    assert summary["frontendLoweringChanged"] is False
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["branchControlFlowReingestClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p91_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P91")


def test_fef_p91_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p91_loop_backedge_expected_samples.py",
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
    assert "FEF_P91_LOOP_BACKEDGE_EXPECTED_SAMPLES_OK" in proc.stdout
