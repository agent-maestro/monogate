"""Tests for FEF-P109 side-effect original C stubbed-runtime gate."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p109_side_effect_original_c_stubbed_runtime_gate import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    c_harness_source,
    parse_runtime_output,
    validate_payload,
)


def test_fef_p109_records_stubbed_original_c_runtime():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P109_SIDE_EFFECT_ORIGINAL_C_STUBBED_RUNTIME_GATE_PASS"
    assert payload["decision"] == "side_effect_original_c_stubbed_runtime_gate_recorded_support_blocked"
    assert summary["selectedFixtureId"] == "c_global_state_update_v0"
    assert summary["comparisonCount"] == 7
    assert summary["passCount"] == 7
    assert summary["failCount"] == 0
    assert summary["maxAbsError"] == 0.0


def test_fef_p109_c_harness_uses_deterministic_update_stub():
    source = c_harness_source(
        [
            {
                "sampleId": "sample_x",
                "inputs": {"x": 1.0, "initialState": 0.0, "externalCallReturn": 4.0},
            }
        ]
    )
    assert "static double update_state(double x)" in source
    assert "return deterministic_update_return;" in source
    assert "state = update_state(x);" in source
    assert "run_sample(\"sample_x\", 1.0, 0.0, 4.0);" in source


def test_fef_p109_runtime_rows_match_stub_and_write_counts():
    payload = build_payload()
    rows = payload["originalCSourceExecution"]["rows"]
    assert sum(row["stubbedCallCount"] for row in rows) == 4
    assert sum(row["boundedStateWriteCount"] for row in rows) == 4
    assert all(row["pass"] for row in rows)
    for row in rows:
        if row["guardTrue"]:
            assert row["stubbedCallCount"] == 1
            assert row["boundedStateWriteCount"] == 1
        else:
            assert row["stubbedCallCount"] == 0
            assert row["boundedStateWriteCount"] == 0


def test_fef_p109_parse_runtime_output():
    parsed = parse_runtime_output("sample_00 5 5 0 0\nsample_01 4 4 1 1\n")
    assert parsed["sample_00"]["observed"] == 5.0
    assert parsed["sample_00"]["stubbedCallCount"] == 0
    assert parsed["sample_01"]["boundedStateWriteCount"] == 1


def test_fef_p109_blocks_generated_reingest_lowering_and_support():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["allLiveExternalCallsNotPerformed"] is True
    assert summary["allBoundedHarnessStateCaptured"] is True
    assert summary["allUnboundedMemoryMutationNotPerformed"] is True
    assert summary["generatedTargetExecuted"] is False
    assert summary["reingestedTargetExecuted"] is False
    assert summary["sideEffectLoweringImplemented"] is False
    assert summary["effectOrderPolicyImplemented"] is False
    assert summary["externalCallPolicyImplemented"] is False
    assert summary["memoryAliasPolicyImplemented"] is False
    assert summary["sideEffectMemorySupportClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p109_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P109")


def test_fef_p109_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p109_side_effect_original_c_stubbed_runtime_gate.py",
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
    assert "FEF_P109_SIDE_EFFECT_ORIGINAL_C_STUBBED_RUNTIME_GATE_OK" in proc.stdout
