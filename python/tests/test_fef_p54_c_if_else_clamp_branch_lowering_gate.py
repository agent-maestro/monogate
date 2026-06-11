"""Tests for FEF-P54 C if/else clamp branch lowering gate."""

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

from scripts.fef_p54_c_if_else_clamp_branch_lowering_gate import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p54_records_selected_c_if_else_clamp_gate():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P54_C_IF_ELSE_CLAMP_BRANCH_LOWERING_GATE_PASS"
    assert payload["decision"] == (
        "selected_c_if_else_clamp_lowering_reingest_passed_general_branch_blocked"
    )
    assert summary["selectedCIfElseClampLoweringPass"] is True
    assert summary["cIfElseClampBlockerClosed"] is True
    assert summary["sourceCaseCount"] == 1
    assert summary["packetCount"] == 2
    assert summary["passCount"] == 2
    assert summary["packetSampleCount"] == 14


def test_fef_p54_source_fixture_shape_is_guarded_selector():
    payload = build_payload()
    fixture = payload["sourceFixture"]
    assert fixture["sourceLanguage"] == "c"
    assert fixture["feature"] == "if_else_clamp"
    assert fixture["loweringForm"] == "affine_selector_with_step01_guard"
    assert {"fn step01", "clamp(", "step01(", "clamp"} <= set(
        fixture["sourceEmlContains"]
    )


def test_fef_p54_packets_compare_generated_runtime_to_reingested_python():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["generatedTargetLanguages"] == ["c", "rust"]
    assert summary["recompiledTargetLanguages"] == ["python"]
    for packet in payload["reingestPackets"]:
        assert packet["sourceLanguage"] == "c"
        assert packet["sourceFeature"] == "if_else_clamp"
        assert packet["generatedTargetLanguage"] in {"c", "rust"}
        assert packet["recompiledTargetLanguage"] == "python"
        assert packet["sourceFunctionCount"] == 2
        assert packet["reingestedFunctionCount"] == 2
        assert packet["reingestStatus"] == "pass"
        assert packet["maxAbsError"] <= 1e-9 or packet["maxRelError"] <= 1e-9
        assert set(packet["frames"][0]["values"]) == {
            "sourceDerivedGeneratedTargetRuntime",
            "reingestedRecompiledPython",
            "expectedClampReference",
        }


def test_fef_p54_claim_boundaries_and_gates_remain_blocked():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_c_if_else_clamp_lowering"] == "pass"
    assert gates["selected_c_if_else_clamp_generated_c_reingest"] == "pass"
    assert gates["selected_c_if_else_clamp_generated_rust_reingest"] == "pass"
    assert gates["c_if_statement_support"] == "blocked"
    assert gates["rust_if_support"] == "blocked"
    assert gates["general_branch_control_flow_support"] == "blocked"
    assert summary["cIfStatementSupportClaim"] is False
    assert summary["rustIfSupportClaim"] is False
    assert summary["generalBranchControlFlowSupportClaim"] is False
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


def test_fef_p54_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    packets = sorted((tmp_path / "packets").glob("*.json"))
    assert len(packets) == 2
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P54")


def test_fef_p54_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p54_c_if_else_clamp_branch_lowering_gate.py",
            "--build",
            "--out-dir",
            str(tmp_path / "results"),
            "--packet-dir",
            str(tmp_path / "packets"),
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
    assert "FEF_P54_C_IF_ELSE_CLAMP_BRANCH_LOWERING_GATE_OK" in proc.stdout
