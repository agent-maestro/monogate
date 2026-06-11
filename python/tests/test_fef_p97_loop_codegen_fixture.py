"""Tests for FEF-P97 loop codegen fixture."""

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

from scripts.fef_p97_loop_codegen_fixture import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_codegen,
    validate_payload,
    validate_row,
)


def test_fef_p97_records_codegen_fixture_without_behavior_change():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P97_LOOP_CODEGEN_FIXTURE_PASS"
    assert payload["decision"] == "selected_loop_codegen_fixture_recorded_runtime_blocked"
    assert summary["selectedFixtureId"] == "c_while_accumulate_v0"
    assert summary["codegenFixtureStatus"] == "codegen_fixture_recorded_runtime_not_executed"
    assert summary["codegenRequiresPolicyGate"] == "selected_c_while_accumulate_boundedness_policy_v0"
    assert summary["compilerBehaviorChanged"] is False
    assert summary["frontendLoweringChanged"] is False
    assert summary["loopLoweringImplemented"] is False


def test_fef_p97_codegen_fixture_shape_is_selected_and_not_executed():
    payload = build_payload()
    codegen = payload["selectedCodegenFixture"]
    validate_codegen(codegen)
    assert codegen["selectedFixtureId"] == "c_while_accumulate_v0"
    assert codegen["targetLanguage"] == "c"
    assert codegen["usesHelpers"] == ["loop_effective_iterations"]
    assert "mg_loop_effective_iterations" in codegen["source"]
    assert "return x * (double)k;" in codegen["source"]
    assert codegen["generatedTargetCompiled"] is False
    assert codegen["generatedTargetExecuted"] is False
    assert codegen["installedInForge"] is False


def test_fef_p97_fixture_validation_matches_existing_samples():
    payload = build_payload()
    rows = payload["fixtureValidationRows"]
    assert len(rows) == 7
    for row in rows:
        validate_row(row)
        assert row["codegenFixtureValue"] == row["expected"]
        assert row["absError"] == 0.0
        assert row["generatedTargetCompiled"] is False
        assert row["generatedTargetExecuted"] is False
    assert payload["summary"]["fixtureValidationPassCount"] == 7
    assert payload["summary"]["fixtureValidationFailCount"] == 0
    assert payload["summary"]["fixtureValidationMaxAbsError"] == 0.0


def test_fef_p97_iteration_distribution_remains_visible():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["zeroIterationCount"] == 2
    assert summary["singleIterationCount"] == 1
    assert summary["multiIterationCount"] == 4
    assert summary["maxEffectiveIterationCount"] == 8


def test_fef_p97_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_loop_codegen_fixture"] == "recorded_runtime_blocked"
    assert gates["generated_target_runtime_execution"] == "blocked_not_run"
    assert gates["loop_backedge_support"] == "blocked"
    assert "Generated loop target code was compiled or executed." in payload["blockedStatements"]
    assert summary["codegenFixtureInstalledInForge"] is False
    assert summary["loopGeneratedTargetCompiled"] is False
    assert summary["loopGeneratedTargetExecuted"] is False
    assert summary["loopReingestExecuted"] is False
    assert summary["loopBackedgeSupportClaim"] is False
    assert summary["loopBackedgeSemanticsImplemented"] is False
    assert summary["loopBoundednessPolicyGeneralClaim"] is False
    assert summary["controlFlowIrImplemented"] is False
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p97_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P97")


def test_fef_p97_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p97_loop_codegen_fixture.py",
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
    assert "FEF_P97_LOOP_CODEGEN_FIXTURE_OK" in proc.stdout
