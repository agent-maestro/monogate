"""Tests for FEF-P79 compound-condition re-ingest execution probe."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p79_compound_condition_reingest_execution_probe import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    classify_failure,
    run_reingest_probe,
    validate_payload,
    validate_probe,
)


def test_fef_p79_records_fail_closed_reingest_probe():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P79_COMPOUND_CONDITION_REINGEST_EXECUTION_PROBE_PASS"
    assert payload["decision"] == "selected_compound_condition_reingest_probe_blocked_expected_surface"
    assert summary["selectedFixtureId"] == "c_and_short_circuit_guard_v0"
    assert summary["probeInvocationPerformed"] is True
    assert summary["probeStatus"] == "blocked_expected_unsupported_surface"
    assert summary["probeBlockedExpectedUnsupportedSurface"] is True
    assert summary["reingestExecuted"] is False


def test_fef_p79_probe_captures_efrog_error_blocker():
    payload = build_payload()
    probe = payload["reingestProbe"]
    validate_probe(probe)
    assert probe["errorType"] == "EFrogError"
    assert probe["failure"]["failureClass"] == "efrog_selected_generated_compound_condition_surface_blocked"
    assert probe["failure"]["detectedBlockers"]
    assert probe["recompiledPythonExecuted"] is False


def test_fef_p79_reingest_probe_is_actual_invocation():
    payload = build_payload()
    source = payload["selectedCodegenFixture"]["source"]
    probe = run_reingest_probe(source)
    assert probe["invocationPerformed"] is True
    assert probe["status"] == "blocked_expected_unsupported_surface"
    assert probe["reingestExecuted"] is False
    assert probe["errorType"] == "EFrogError"


def test_fef_p79_failure_classifier_names_known_surfaces():
    classified = classify_failure("BinaryOp unsupported as C branch condition")
    assert "nonzero_comparison_condition_unsupported" in classified["detectedBlockers"]
    helper = classify_failure("call to non-math function `mg_step01` unsupported in E2")
    assert "selected_guard_helper_call_unsupported" in helper["detectedBlockers"]
    unknown = classify_failure("something else")
    assert unknown["detectedBlockers"] == ["unclassified_reingest_blocker"]


def test_fef_p79_blocker_requirements_are_explicit():
    payload = build_payload()
    requirements = payload["blockerRequirements"]
    assert [item["requirementId"] for item in requirements] == [
        "support_selected_nonzero_predicate_condition",
        "support_selected_guard_helper_calls",
        "support_selected_if_assignment_shape",
        "compile_reingested_eml_to_python_and_compare_p77_rows",
    ]
    assert all(item["status"] in {"required_before_reingest_execution", "blocked_until_reingest_parse_passes"} for item in requirements)


def test_fef_p79_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_reingest_probe_invocation"] == "performed_blocked_expected_surface"
    assert gates["selected_reingest_execution"] == "blocked_not_executed"
    assert gates["recompiled_python_execution"] == "blocked_not_executed"
    assert gates["compound_condition_support"] == "blocked"
    assert "Re-ingested compound-condition code was executed successfully." in payload["blockedStatements"]
    assert summary["compoundConditionReingestSupported"] is False
    assert summary["compoundConditionLoweringImplemented"] is False
    assert summary["compoundConditionSupportClaim"] is False
    assert summary["shortCircuitSemanticsImplemented"] is False
    assert summary["helperRuntimeInstalled"] is False
    assert summary["controlFlowIrImplemented"] is False
    assert summary["frontendLoweringChanged"] is False
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p79_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P79")


def test_fef_p79_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p79_compound_condition_reingest_execution_probe.py",
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
    assert "FEF_P79_COMPOUND_CONDITION_REINGEST_EXECUTION_PROBE_OK" in proc.stdout
