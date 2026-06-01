"""Tests for FEF-P76 compound-condition helper/codegen fixture."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p76_compound_condition_helper_codegen_fixture import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_codegen,
    validate_helpers,
    validate_payload,
    validate_row,
)


def test_fef_p76_records_helper_codegen_fixture_without_behavior_change():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P76_COMPOUND_CONDITION_HELPER_CODEGEN_FIXTURE_PASS"
    assert payload["decision"] == "selected_helper_codegen_fixture_recorded_runtime_blocked"
    assert summary["selectedFixtureId"] == "c_and_short_circuit_guard_v0"
    assert summary["helperFixtureCount"] == 3
    assert summary["codegenFixtureStatus"] == "codegen_fixture_recorded_runtime_not_executed"
    assert summary["compilerBehaviorChanged"] is False
    assert summary["compoundConditionLoweringImplemented"] is False


def test_fef_p76_helper_fixtures_are_not_installed():
    payload = build_payload()
    helpers = payload["helperFixtures"]
    validate_helpers(helpers)
    assert [helper["helperId"] for helper in helpers] == ["step01", "nonzero01", "guarded_div"]
    assert all(helper["installedInRuntime"] is False for helper in helpers)
    assert payload["summary"]["helpersInstalledInRuntime"] is False


def test_fef_p76_codegen_fixture_shape_is_selected_and_not_executed():
    payload = build_payload()
    codegen = payload["selectedCodegenFixture"]
    validate_codegen(codegen)
    assert codegen["selectedFixtureId"] == "c_and_short_circuit_guard_v0"
    assert codegen["targetLanguage"] == "c"
    assert codegen["usesHelpers"] == ["step01", "nonzero01", "guarded_div"]
    assert "if (lhs != 0.0)" in codegen["source"]
    assert codegen["generatedTargetExecuted"] is False
    assert codegen["installedInForge"] is False


def test_fef_p76_fixture_validation_matches_existing_samples():
    payload = build_payload()
    rows = payload["fixtureValidationRows"]
    assert len(rows) == 7
    for row in rows:
        validate_row(row)
        assert row["codegenFixtureValue"] == row["expected"]
        assert row["absError"] == 0.0
        assert row["generatedTargetExecuted"] is False
    assert payload["summary"]["fixtureValidationPassCount"] == 7
    assert payload["summary"]["fixtureValidationFailCount"] == 0


def test_fef_p76_short_circuit_shape_remains_visible():
    payload = build_payload()
    left_false = [row for row in payload["fixtureValidationRows"] if row["path"] == "left_false_short_circuit"]
    right_guard = [row for row in payload["fixtureValidationRows"] if row["path"] == "right_false_zero_denominator_guard"]
    assert len(left_false) == 3
    assert all(row["rhsEvaluated"] is False for row in left_false)
    assert len(right_guard) == 1
    assert right_guard[0]["selected"] == 0.0


def test_fef_p76_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_helper_codegen_fixture"] == "recorded_runtime_blocked"
    assert gates["generated_target_runtime_execution"] == "blocked_not_run"
    assert gates["compound_condition_support"] == "blocked"
    assert "Generated compound-condition target code was executed." in payload["blockedStatements"]
    assert summary["helpersInstalledInRuntime"] is False
    assert summary["codegenFixtureInstalledInForge"] is False
    assert summary["compoundConditionGeneratedTargetExecuted"] is False
    assert summary["compoundConditionReingestExecuted"] is False
    assert summary["compoundConditionSupportClaim"] is False
    assert summary["shortCircuitSemanticsImplemented"] is False
    assert summary["guardedDivisionRuntimeHelperImplemented"] is False
    assert summary["controlFlowIrImplemented"] is False
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p76_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P76")


def test_fef_p76_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p76_compound_condition_helper_codegen_fixture.py",
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
    assert "FEF_P76_COMPOUND_CONDITION_HELPER_CODEGEN_FIXTURE_OK" in proc.stdout
