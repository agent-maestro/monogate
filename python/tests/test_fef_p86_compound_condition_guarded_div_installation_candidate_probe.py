"""Tests for FEF-P86 guarded-div installation candidate probe."""

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

from scripts.fef_p86_compound_condition_guarded_div_installation_candidate_probe import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    build_probe_result,
    installation_candidate,
    read_json,
    validate_payload,
    P85_RESULT,
)


def test_fef_p86_records_uninstalled_installation_candidate():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P86_COMPOUND_CONDITION_GUARDED_DIV_INSTALLATION_CANDIDATE_PROBE_PASS"
    assert payload["decision"] == "selected_guarded_div_installation_candidate_probe_pass_not_installed"
    assert summary["selectedFixtureId"] == "c_and_short_circuit_guard_v0"
    assert summary["candidateStatus"] == "candidate_probe_recorded_not_installed"
    assert summary["intendedPipelineHookCount"] == 3
    assert summary["requiredFailClosedCheckCount"] == 5
    assert summary["candidateInstalled"] is False
    assert summary["reingestProbePerformed"] is False


def test_fef_p86_candidate_hooks_are_specific_and_fail_closed():
    candidate = installation_candidate()
    assert candidate["candidateId"] == "selected_guarded_div_local_adapter_installation_candidate_v0"
    assert candidate["scope"] == "selected_c_and_short_circuit_guard_v0_only"
    assert [hook["hookId"] for hook in candidate["intendedPipelineHooks"]] == [
        "rewrite_selected_nonzero_condition",
        "rewrite_selected_guarded_division",
        "preserve_short_circuit_non_evaluation",
    ]
    assert candidate["installedInEfrog"] is False
    assert candidate["installedInForge"] is False
    assert len(candidate["requiredFailClosedChecks"]) == 5


def test_fef_p86_probe_replays_all_rows_and_preserves_non_evaluation():
    payload = build_payload()
    probe = payload["probeResult"]
    assert probe["rowCount"] == 7
    assert probe["executedRowCount"] == 7
    assert probe["passCount"] == 7
    assert probe["failCount"] == 0
    assert probe["maxAbsError"] == 0.0
    assert probe["zeroDenominatorRowCount"] == 2
    assert probe["zeroDenominatorRowsWithDivisionSkipped"] == 2
    assert probe["nonEvaluationBoundaryPreserved"] is True
    zero_rows = [row for row in probe["rows"] if row["zeroDenominator"]]
    assert all(row["divisionEvaluated"] is False for row in zero_rows)
    assert all(row["nonEvaluationPreserved"] is True for row in zero_rows)


def test_fef_p86_probe_result_sources_p85_rows():
    p85_payload = read_json(P85_RESULT)
    result = build_probe_result(installation_candidate(), p85_payload)
    assert result["candidateInstalled"] is False
    assert result["reingestProbePerformed"] is False
    assert result["allRowsPass"] is True
    assert result["zeroDenominatorRowsWithDivisionSkipped"] == 2


def test_fef_p86_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_guarded_div_installation_candidate"] == "candidate_probe_pass_not_installed"
    assert gates["source_primitive_installation"] == "not_performed"
    assert gates["reingest_probe"] == "blocked_not_performed"
    assert "The selected guarded-div primitive is installed in eFrog or Forge." in payload["blockedStatements"]
    assert summary["sourcePrimitiveInstalled"] is False
    assert summary["compoundConditionReingestSupported"] is False
    assert summary["compoundConditionLoweringImplemented"] is False
    assert summary["compoundConditionSupportClaim"] is False
    assert summary["shortCircuitSemanticsImplemented"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p86_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P86")


def test_fef_p86_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p86_compound_condition_guarded_div_installation_candidate_probe.py",
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
    assert "FEF_P86_COMPOUND_CONDITION_GUARDED_DIV_INSTALLATION_CANDIDATE_PROBE_OK" in proc.stdout
