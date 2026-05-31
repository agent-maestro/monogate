"""Tests for FEF-P67 assignment/phi expected samples."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p67_assignment_phi_expected_samples import (
    CLAIM_FLAGS,
    SELECTED_FIXTURE_ID,
    build_outputs,
    build_payload,
    expected_value,
    validate_payload,
    validate_sample,
)


def test_fef_p67_records_expected_samples_without_execution_claim():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P67_ASSIGNMENT_PHI_EXPECTED_SAMPLES_PASS"
    assert payload["decision"] == "assignment_phi_expected_samples_recorded_support_blocked"
    assert summary["selectedFixtureId"] == SELECTED_FIXTURE_ID
    assert summary["sampleCount"] == 7
    assert summary["selectedFixtureStillBlocked"] is True
    assert summary["assignmentPhiRuntimeExecutionClaim"] is False
    assert summary["assignmentPhiSupportClaim"] is False


def test_fef_p67_expected_samples_match_source_semantics():
    payload = build_payload()
    for sample in payload["expectedSamples"]:
        validate_sample(sample)
        x = sample["inputs"]["x"]
        y = sample["inputs"]["y"]
        assert sample["expected"] == expected_value(x, y)
        assert sample["assignmentTaken"] == (x > 0.0)
        assert sample["sourceSemanticsOnly"] is True
    assert payload["summary"]["assignmentTakenCount"] == 3
    assert payload["summary"]["fallthroughCount"] == 4


def test_fef_p67_selected_fixture_remains_blocked_and_schema_shaped():
    payload = build_payload()
    fixture = payload["selectedFixture"]
    assert fixture["id"] == "c_branch_assignment_merge_v0"
    assert fixture["status"] == "blocked_fixture_defined"
    assert fixture["supportClaimAllowed"] is False
    assert fixture["runtimeExecutionPerformed"] is False
    assert fixture["schemaFragment"]["blocks"][0]["statements"][0]["constructId"] == "mutable_assignments_across_branches"
    assert all(value is False for value in fixture["schemaFragment"]["claimFlags"].values())


def test_fef_p67_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["assignment_phi_expected_samples"] == "recorded"
    assert gates["assignment_phi_runtime_execution"] == "not_performed"
    assert gates["assignment_phi_lowering"] == "blocked"
    assert "Assignment/phi fixtures were executed." in payload["blockedStatements"]
    assert summary["assignmentPhiLoweringClaim"] is False
    assert summary["assignmentPhiSupportClaim"] is False
    assert summary["controlFlowIrImplemented"] is False
    assert summary["frontendLoweringChanged"] is False
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p67_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P67")


def test_fef_p67_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p67_assignment_phi_expected_samples.py",
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
    assert "FEF_P67_ASSIGNMENT_PHI_EXPECTED_SAMPLES_OK" in proc.stdout
