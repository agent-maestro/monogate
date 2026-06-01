"""Tests for FEF-P106 side-effect expected samples."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p106_side_effect_expected_samples import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    expected_samples,
    selected_fixture,
    validate_payload,
)


def test_fef_p106_records_expected_samples_without_execution():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P106_SIDE_EFFECT_EXPECTED_SAMPLES_PASS"
    assert payload["decision"] == "side_effect_expected_samples_recorded_support_blocked"
    assert summary["selectedFixtureId"] == "c_global_state_update_v0"
    assert summary["sampleCount"] == 7
    assert summary["callExpectedCount"] == 4
    assert summary["guardFalseNoCallCount"] == 3
    assert summary["allRuntimeExecutionNotPerformed"] is True


def test_fef_p106_expected_samples_model_guarded_call_and_state_write():
    samples = expected_samples()
    assert [sample["path"] for sample in samples] == [
        "guard_false_no_call",
        "guard_false_no_call",
        "call_and_state_write",
        "call_and_state_write",
        "call_and_state_write",
        "guard_false_no_call",
        "call_and_state_write",
    ]
    assert [sample["expectedReturn"] for sample in samples] == [5.0, -1.0, 1.5, 4.0, 8.0, 9.0, 21.0]
    assert sum(1 for sample in samples if sample["stateWriteExpected"]) == 4
    assert all(sample["externalCallPerformed"] is False for sample in samples)
    assert all(sample["memoryWritePerformed"] is False for sample in samples)


def test_fef_p106_selected_fixture_is_p105_global_state_update():
    payload = build_payload()
    fixture = selected_fixture({"sideEffectMemoryFixtures": [payload["selectedFixture"]]})
    assert fixture["id"] == "c_global_state_update_v0"
    assert fixture["effectKind"] == "global_state_write_and_external_call"
    assert fixture["requiresEffectOrderPolicy"] is True
    assert fixture["requiresExternalCallPolicy"] is True
    assert fixture["requiresMemoryAliasPolicy"] is True


def test_fef_p106_blocks_effect_policies_execution_and_support():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["effectBoundaryExpectedCount"] == 8
    assert summary["allEffectPoliciesNotApplied"] is True
    assert summary["sideEffectRuntimeExecutionClaim"] is False
    assert summary["sideEffectLoweringImplemented"] is False
    assert summary["effectOrderPolicyImplemented"] is False
    assert summary["externalCallPolicyImplemented"] is False
    assert summary["memoryAliasPolicyImplemented"] is False
    assert summary["sideEffectMemorySupportClaim"] is False


def test_fef_p106_release_gates_and_claim_flags_remain_false():
    payload = build_payload()
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["side_effect_expected_samples"] == "recorded"
    assert gates["side_effect_runtime_execution"] == "not_performed"
    assert gates["external_call_execution"] == "not_performed"
    assert gates["memory_write_execution"] == "not_performed"
    assert gates["side_effect_memory_support"] == "blocked"
    assert "An external call was performed." in payload["blockedStatements"]
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p106_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P106")


def test_fef_p106_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p106_side_effect_expected_samples.py",
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
    assert "FEF_P106_SIDE_EFFECT_EXPECTED_SAMPLES_OK" in proc.stdout
