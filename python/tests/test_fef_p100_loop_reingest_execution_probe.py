"""Tests for FEF-P100 loop re-ingest execution probe."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p100_loop_reingest_execution_probe import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    classify_failure,
    validate_payload,
    validate_probe,
)


def test_fef_p100_invokes_reingest_probe_and_records_expected_blocker():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P100_LOOP_REINGEST_EXECUTION_PROBE_PASS"
    assert payload["decision"] == "selected_loop_reingest_probe_blocked_expected_surface"
    assert summary["selectedFixtureId"] == "c_while_accumulate_v0"
    assert summary["probeInvocationPerformed"] is True
    assert summary["probeStatus"] == "blocked_expected_unsupported_surface"
    assert summary["probeBlockedExpectedUnsupportedSurface"] is True


def test_fef_p100_detects_selected_loop_helper_call_blocker():
    payload = build_payload()
    probe = payload["reingestProbe"]
    validate_probe(probe)
    assert probe["errorType"] == "EFrogError"
    assert "mg_loop_effective_iterations" in probe["errorMessage"]
    assert probe["failure"]["failureClass"] == "efrog_selected_generated_loop_surface_blocked"
    assert probe["failure"]["detectedBlockers"] == ["selected_loop_helper_call_unsupported"]


def test_fef_p100_failure_classifier_is_specific():
    classified = classify_failure("call to non-math function `mg_loop_effective_iterations` unsupported in E2")
    assert classified["detectedBlockers"] == ["selected_loop_helper_call_unsupported"]
    fallback = classify_failure("mysterious parse failure")
    assert fallback["detectedBlockers"] == ["unclassified_reingest_blocker"]


def test_fef_p100_blocker_requirements_are_linked():
    payload = build_payload()
    requirements = payload["blockerRequirements"]
    assert [item["requirementId"] for item in requirements] == [
        "support_selected_loop_effective_iteration_helper",
        "support_selected_closed_form_loop_return",
        "reject_unbounded_or_data_dependent_loop_surfaces",
        "compile_reingested_eml_to_python_and_compare_p98_rows",
    ]
    assert payload["summary"]["requirementCount"] == 4
    assert payload["summary"]["linkedRequirementCount"] >= 3


def test_fef_p100_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_loop_reingest_probe_invocation"] == "performed_blocked_expected_surface"
    assert gates["selected_loop_reingest_execution"] == "blocked_not_executed"
    assert gates["loop_backedge_support"] == "blocked"
    assert "Re-ingested loop code was executed successfully." in payload["blockedStatements"]
    assert summary["reingestExecuted"] is False
    assert summary["recompiledPythonExecuted"] is False
    assert summary["runtimeComparisonExecuted"] is False
    assert summary["loopReingestSupported"] is False
    assert summary["loopLoweringImplemented"] is False
    assert summary["loopBackedgeSupportClaim"] is False
    assert summary["selectedCodegenFixtureInstalled"] is False
    assert summary["controlFlowIrImplemented"] is False
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p100_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P100")


def test_fef_p100_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p100_loop_reingest_execution_probe.py",
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
    assert "FEF_P100_LOOP_REINGEST_EXECUTION_PROBE_OK" in proc.stdout
