"""Tests for FEF-P57 selected branch closure matrix."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p57_selected_branch_closure_matrix import (
    BRANCH_PHASES,
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p57_records_all_selected_branch_closures():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P57_SELECTED_BRANCH_CLOSURE_MATRIX_PASS"
    assert payload["decision"] == "all_selected_branch_closures_recorded_general_branch_blocked"
    assert summary["selectedBranchCaseCount"] == 5
    assert summary["selectedBranchClosureCount"] == 5
    assert summary["selectedLoweringPassCount"] == 5
    assert summary["p51BlockedCount"] == 0
    assert set(summary["p51LaterPhasePassCaseIds"]) == {spec["caseId"] for spec in BRANCH_PHASES}


def test_fef_p57_closure_rows_have_expected_shape():
    payload = build_payload()
    rows = {row["caseId"]: row for row in payload["closureRows"]}
    assert set(rows) == {spec["caseId"] for spec in BRANCH_PHASES}
    for spec in BRANCH_PHASES:
        row = rows[spec["caseId"]]
        assert row["phase"] == spec["phase"]
        assert row["sourceLanguage"] == spec["sourceLanguage"]
        assert row["feature"] == spec["feature"]
        assert row["selectedLoweringPass"] is True
        assert row["p51BlockerClosed"] is True
        assert row["packetCount"] == spec["expectedPacketCount"]
        assert row["packetSampleCount"] == spec["expectedPacketSampleCount"]
        assert row["generatedTargetLanguages"] == ["c", "rust"]
        assert row["recompiledTargetLanguages"] == ["python"]
        assert row["maxAbsError"] == 0.0
        assert row["maxRelError"] == 0.0
        assert all(value is False for value in row["claimFlags"].values())


def test_fef_p57_totals_and_boundaries_remain_blocked():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_branch_closure_matrix"] == "pass"
    assert gates["p51_selected_branch_blockers_remaining"] == "zero_selected_blockers"
    assert gates["general_branch_control_flow_support"] == "blocked"
    assert summary["totalReingestPacketCount"] == 10
    assert summary["totalPacketSampleComparisons"] == 58
    assert summary["sourceLanguages"] == ["c", "rust"]
    assert summary["generatedTargetLanguages"] == ["c", "rust"]
    assert summary["recompiledTargetLanguages"] == ["python"]
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["fullNonGeneratedSourceRoundtripClaim"] is False
    assert summary["fullCRustRoundtripClaim"] is False
    assert summary["arbitrarySourceFamilyClaim"] is False
    assert summary["reviewerDecisionRecorded"] is False
    assert summary["packagePublished"] is False
    assert summary["checkoutEnabled"] is False
    assert summary["publicReady"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p57_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P57")


def test_fef_p57_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p57_selected_branch_closure_matrix.py",
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
    assert "FEF_P57_SELECTED_BRANCH_CLOSURE_MATRIX_OK" in proc.stdout
