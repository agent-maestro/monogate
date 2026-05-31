"""Tests for FEF-P66 assignment/phi fixture gate."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p66_assignment_phi_fixture_gate import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_fixture,
    validate_payload,
)


def test_fef_p66_records_assignment_phi_gate_without_support_claim():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P66_ASSIGNMENT_PHI_FIXTURE_GATE_PASS"
    assert payload["decision"] == "assignment_phi_fixture_gate_recorded_support_blocked"
    assert summary["p61ValidationPass"] is True
    assert summary["p65ValidationPass"] is True
    assert summary["fixtureCount"] == 3
    assert summary["allFixturesBlocked"] is True
    assert summary["assignmentPhiSupportClaim"] is False


def test_fef_p66_matrix_covers_c_and_rust_assignment_phi_shapes():
    payload = build_payload()
    rows = {row["id"]: row for row in payload["assignmentPhiFixtures"]}
    assert set(rows) == {
        "c_branch_assignment_merge_v0",
        "c_if_else_assignment_merge_v0",
        "rust_branch_mut_assignment_v0",
    }
    assert payload["summary"]["cFixtureCount"] == 2
    assert payload["summary"]["rustFixtureCount"] == 1
    assert payload["summary"]["assignmentCount"] == 7
    assert payload["summary"]["mergeCount"] == 3


def test_fef_p66_fixture_fragments_are_schema_shaped_and_blocked():
    payload = build_payload()
    for row in payload["assignmentPhiFixtures"]:
        validate_fixture(row)
        fragment = row["schemaFragment"]
        assert fragment["feature"] == row["shape"]
        assert fragment["blocks"][0]["statements"][0]["constructId"] == "mutable_assignments_across_branches"
        assert fragment["blocks"][0]["terminator"]["kind"] == "unreachable"
        assert row["status"] == "blocked_fixture_defined"
        assert row["supportClaimAllowed"] is False
        assert row["runtimeExecutionPerformed"] is False
        assert all(value is False for value in fragment["claimFlags"].values())


def test_fef_p66_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["assignment_phi_fixture_gate"] == "recorded"
    assert gates["assignment_phi_runtime_execution"] == "not_performed"
    assert gates["assignment_phi_support"] == "blocked"
    assert "Assignment/phi lowering is implemented." in payload["blockedStatements"]
    assert summary["assignmentPhiRuntimeExecutionClaim"] is False
    assert summary["assignmentPhiSupportClaim"] is False
    assert summary["controlFlowIrImplemented"] is False
    assert summary["frontendLoweringChanged"] is False
    assert summary["unsupportedConstructsSupported"] is False
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["branchControlFlowReingestClaim"] is False
    assert summary["fullNonGeneratedSourceRoundtripClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p66_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P66")


def test_fef_p66_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p66_assignment_phi_fixture_gate.py",
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
    assert "FEF_P66_ASSIGNMENT_PHI_FIXTURE_GATE_OK" in proc.stdout
