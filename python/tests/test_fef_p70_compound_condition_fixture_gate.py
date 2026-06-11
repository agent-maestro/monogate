"""Tests for FEF-P70 compound-condition fixture gate."""

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

from scripts.fef_p70_compound_condition_fixture_gate import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_fixture,
    validate_payload,
)


def test_fef_p70_records_compound_condition_gate_without_support_claim():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P70_COMPOUND_CONDITION_FIXTURE_GATE_PASS"
    assert payload["decision"] == "compound_condition_fixture_gate_recorded_support_blocked"
    assert summary["p61ValidationPass"] is True
    assert summary["p69ValidationPass"] is True
    assert summary["fixtureCount"] == 3
    assert summary["allFixturesBlocked"] is True
    assert summary["compoundConditionSupportClaim"] is False


def test_fef_p70_matrix_covers_c_and_rust_short_circuit_shapes():
    payload = build_payload()
    rows = {row["id"]: row for row in payload["compoundConditionFixtures"]}
    assert set(rows) == {
        "c_and_short_circuit_guard_v0",
        "c_or_short_circuit_default_v0",
        "rust_and_short_circuit_guard_v0",
    }
    assert payload["summary"]["cFixtureCount"] == 2
    assert payload["summary"]["rustFixtureCount"] == 1
    assert payload["summary"]["andFixtureCount"] == 2
    assert payload["summary"]["orFixtureCount"] == 1
    assert payload["summary"]["conditionCount"] == 6
    assert payload["summary"]["shortCircuitSiteCount"] == 3


def test_fef_p70_fixture_fragments_are_schema_shaped_and_blocked():
    payload = build_payload()
    for row in payload["compoundConditionFixtures"]:
        validate_fixture(row)
        fragment = row["schemaFragment"]
        assert fragment["feature"] == row["shape"]
        assert fragment["blocks"][0]["statements"][0]["constructId"] == "boolean_compound_conditions"
        assert fragment["blocks"][0]["terminator"]["kind"] == "unreachable"
        assert row["status"] == "blocked_fixture_defined"
        assert row["supportClaimAllowed"] is False
        assert row["runtimeExecutionPerformed"] is False
        assert all(value is False for value in fragment["claimFlags"].values())


def test_fef_p70_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["compound_condition_fixture_gate"] == "recorded"
    assert gates["compound_condition_runtime_execution"] == "not_performed"
    assert gates["compound_condition_support"] == "blocked"
    assert "Compound-condition lowering is implemented." in payload["blockedStatements"]
    assert summary["compoundConditionRuntimeExecutionClaim"] is False
    assert summary["compoundConditionSupportClaim"] is False
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


def test_fef_p70_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P70")


def test_fef_p70_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p70_compound_condition_fixture_gate.py",
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
    assert "FEF_P70_COMPOUND_CONDITION_FIXTURE_GATE_OK" in proc.stdout
