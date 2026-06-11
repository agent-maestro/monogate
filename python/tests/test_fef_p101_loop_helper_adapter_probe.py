"""Tests for FEF-P101 loop helper adapter probe."""

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

from scripts.fef_p101_loop_helper_adapter_probe import (
    CLAIM_FLAGS,
    adapt_selected_loop_helper,
    build_outputs,
    build_payload,
    validate_adapter,
    validate_payload,
    validate_probe,
)


def test_fef_p101_records_helper_adapter_parse_pass_without_execution():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P101_LOOP_HELPER_ADAPTER_PROBE_PASS"
    assert payload["decision"] == "selected_loop_helper_adapter_clears_blocker_parse_pass_execution_blocked"
    assert summary["selectedFixtureId"] == "c_while_accumulate_v0"
    assert summary["previousBlockerCleared"] is True
    assert summary["reingestParseSucceeded"] is True
    assert summary["probeStatus"] == "parse_pass_execution_blocked"


def test_fef_p101_adapter_inlines_selected_helper_call():
    payload = build_payload()
    adapter = payload["adapterProbe"]
    validate_adapter(adapter)
    replacements = {item["replacementId"]: item for item in adapter["replacements"]}
    assert replacements["remove_selected_loop_helper_definition"]["applied"] is True
    assert replacements["inline_selected_loop_effective_iterations_call"]["applied"] is True
    source = adapt_selected_loop_helper(payload["selectedCodegenFixture"]["source"])["adaptedSource"]
    assert "mg_loop_effective_iterations" not in source
    assert "int k = n > 0 ? n : 0;" in source


def test_fef_p101_probe_parses_but_does_not_execute_recompiled_python():
    payload = build_payload()
    probe = payload["reingestProbe"]
    validate_probe(probe)
    assert probe["reingestParseSucceeded"] is True
    assert probe["recompiledPythonExecuted"] is False
    assert probe["runtimeComparisonExecuted"] is False
    assert probe["failure"]["detectedBlockers"] == []
    assert "c_while_accumulate_v0_generated_fixture" in probe["emlPreview"]
    assert "let k =" in probe["emlPreview"]


def test_fef_p101_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_loop_helper_adapter_probe"] == "recorded_parse_pass"
    assert gates["selected_loop_reingest_execution"] == "blocked_not_executed"
    assert gates["loop_backedge_support"] == "blocked"
    assert "Re-ingested Python comparison rows were executed." in payload["blockedStatements"]
    assert summary["reingestExecuted"] is False
    assert summary["recompiledPythonExecuted"] is False
    assert summary["runtimeComparisonExecuted"] is False
    assert summary["loopReingestSupported"] is False
    assert summary["selectedCodegenFixtureInstalled"] is False
    assert summary["compilerBehaviorChanged"] is False
    assert summary["loopLoweringImplemented"] is False
    assert summary["loopBackedgeSupportClaim"] is False
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p101_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P101")


def test_fef_p101_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p101_loop_helper_adapter_probe.py",
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
    assert "FEF_P101_LOOP_HELPER_ADAPTER_PROBE_OK" in proc.stdout
