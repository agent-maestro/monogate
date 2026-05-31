"""Tests for FEF-P51 branch/control-flow blocker gate."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p51_branch_control_flow_blocker_gate import (
    BRANCH_FIXTURES,
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p51_records_branch_blocker_inventory():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P51_BRANCH_CONTROL_FLOW_BLOCKER_GATE_PASS"
    assert payload["decision"] == "branch_control_flow_non_generated_c_rust_blockers_recorded"
    assert summary["fixtureCount"] == len(BRANCH_FIXTURES)
    assert summary["blockedCount"] == len(BRANCH_FIXTURES)
    assert summary["unexpectedPassCount"] == 0
    assert summary["sourceLanguages"] == ["c", "rust"]
    assert summary["p50SourceDerivedReingestPass"] is True


def test_fef_p51_blocker_classes_are_explicit():
    payload = build_payload()
    summary = payload["summary"]
    assert set(summary["blockerClasses"]) == {
        "c_conditional_expression_unsupported",
        "c_statement_control_flow_unsupported",
        "rust_if_expression_unsupported",
    }
    rows = {row["caseId"]: row for row in payload["fixtureRows"]}
    assert rows["c_if_early_return_relu_v0"]["blockerClass"] == (
        "c_statement_control_flow_unsupported"
    )
    assert rows["c_ternary_select_v0"]["blockerClass"] == (
        "c_conditional_expression_unsupported"
    )
    assert rows["rust_if_expr_relu_v0"]["blockerClass"] == "rust_if_expression_unsupported"


def test_fef_p51_rows_record_local_frontend_errors():
    payload = build_payload()
    for row in payload["fixtureRows"]:
        assert row["observedStatus"] == "blocked"
        assert row["errorType"]
        assert row["errorMessage"]
        assert row["emittedEml"] is None
        assert all(value is False for value in row["claimFlags"].values())


def test_fef_p51_claim_boundaries_and_release_gates_remain_blocked():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["branch_control_flow_fixture_attempted"] == "pass"
    assert gates["branch_control_flow_supported"] == "blocked"
    assert gates["branch_control_flow_reingest"] == "blocked"
    assert gates["full_non_generated_source_roundtrip_claim"] == "blocked"
    assert gates["private_reviewer_decision"] == "not_recorded"
    assert summary["branchControlFlowSupported"] is False
    assert summary["branchControlFlowReingestClaim"] is False
    assert summary["selectedBranchFixturePassClaim"] is False
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


def test_fef_p51_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P51")


def test_fef_p51_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p51_branch_control_flow_blocker_gate.py",
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
    assert "FEF_P51_BRANCH_CONTROL_FLOW_BLOCKER_GATE_OK" in proc.stdout
