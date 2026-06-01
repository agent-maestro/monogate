"""Tests for FEF-P108 side-effect reference-runtime gate."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p108_side_effect_reference_runtime_gate import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    modeled_reference_runtime,
    validate_payload,
)


def test_fef_p108_records_reference_runtime_without_live_effects():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P108_SIDE_EFFECT_REFERENCE_RUNTIME_GATE_PASS"
    assert payload["decision"] == "side_effect_reference_runtime_gate_recorded_support_blocked"
    assert summary["selectedFixtureId"] == "c_global_state_update_v0"
    assert summary["comparisonCount"] == 7
    assert summary["passCount"] == 7
    assert summary["failCount"] == 0
    assert summary["maxAbsError"] == 0.0


def test_fef_p108_modeled_reference_runtime_orders_call_write_return():
    sample = {
        "inputs": {"x": 1.0, "initialState": 0.0, "externalCallReturn": 4.0},
    }
    runtime = modeled_reference_runtime(sample)
    assert runtime["observed"] == 4.0
    assert runtime["orderedEvents"] == [
        "evaluate_guard",
        "perform_modeled_call_if_guard_true",
        "write_modeled_state_if_call_occurs",
        "return_final_state",
    ]
    assert runtime["liveExternalCallPerformed"] is False
    assert runtime["realMemoryMutationPerformed"] is False


def test_fef_p108_modeled_reference_runtime_guard_false_no_effect():
    sample = {
        "inputs": {"x": -1.0, "initialState": 9.0, "externalCallReturn": None},
    }
    runtime = modeled_reference_runtime(sample)
    assert runtime["observed"] == 9.0
    assert runtime["modeledCallExpected"] is False
    assert runtime["modeledStateWriteExpected"] is False
    assert runtime["orderedEvents"] == ["evaluate_guard", "return_final_state"]


def test_fef_p108_comparison_rows_preserve_effect_distribution():
    payload = build_payload()
    rows = payload["runtimeComparison"]["rows"]
    assert sum(1 for row in rows if row["guardTrue"]) == 4
    assert sum(1 for row in rows if not row["guardTrue"]) == 3
    assert sum(1 for row in rows if row["modeledCallExpected"]) == 4
    assert sum(1 for row in rows if row["modeledStateWriteExpected"]) == 4
    assert all(row["pass"] for row in rows)
    assert all(row["liveExternalCallPerformed"] is False for row in rows)
    assert all(row["realMemoryMutationPerformed"] is False for row in rows)


def test_fef_p108_blocks_original_generated_reingest_and_support():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["originalSourceExecuted"] is False
    assert summary["generatedTargetExecuted"] is False
    assert summary["reingestedTargetExecuted"] is False
    assert summary["sideEffectLoweringImplemented"] is False
    assert summary["effectOrderPolicyImplemented"] is False
    assert summary["externalCallPolicyImplemented"] is False
    assert summary["memoryAliasPolicyImplemented"] is False
    assert summary["sideEffectMemorySupportClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p108_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P108")


def test_fef_p108_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p108_side_effect_reference_runtime_gate.py",
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
    assert "FEF_P108_SIDE_EFFECT_REFERENCE_RUNTIME_GATE_OK" in proc.stdout
