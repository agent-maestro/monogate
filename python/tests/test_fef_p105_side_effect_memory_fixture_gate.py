"""Tests for FEF-P105 side-effect/call/memory fixture gate."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p105_side_effect_memory_fixture_gate import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    matrix_rows,
    validate_payload,
)


def test_fef_p105_records_side_effect_fixture_gate_without_execution():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P105_SIDE_EFFECT_MEMORY_FIXTURE_GATE_PASS"
    assert payload["decision"] == "side_effect_memory_fixture_gate_recorded_support_blocked_review_hold_preserved"
    assert summary["fixtureCount"] == 4
    assert summary["sideEffectingCallCount"] == 2
    assert summary["memoryWriteCount"] == 3
    assert summary["effectBoundaryCount"] == 6
    assert summary["allRuntimeExecutionNotPerformed"] is True


def test_fef_p105_fixture_matrix_covers_c_and_rust_effect_shapes():
    rows = matrix_rows()
    assert {row["sourceLanguage"] for row in rows} == {"c", "rust"}
    assert [row["id"] for row in rows] == [
        "c_global_state_update_v0",
        "c_array_write_guard_v0",
        "rust_mut_ref_update_v0",
        "rust_external_call_guard_v0",
    ]
    assert {row["effectKind"] for row in rows} == {
        "global_state_write_and_external_call",
        "indexed_memory_write_and_read",
        "mutable_reference_write",
        "external_method_call",
    }
    assert all(row["constructId"] == "side_effecting_calls_or_memory" for row in rows)


def test_fef_p105_preserves_p104_review_hold():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["p104ValidationPass"] is True
    assert summary["p104ReviewerDecisionRecorded"] is False
    assert summary["p104ImplementationHeldPendingReview"] is True
    assert summary["implementationChangeApproved"] is False
    assert summary["implementationChangeApplied"] is False


def test_fef_p105_blocks_effect_policies_lowering_and_support():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["fixturesRequiringEffectOrderPolicy"] == 4
    assert summary["fixturesRequiringExternalCallPolicy"] == 2
    assert summary["fixturesRequiringMemoryAliasPolicy"] == 3
    assert summary["allLoweringNotPerformed"] is True
    assert summary["allEffectPoliciesNotImplemented"] is True
    assert summary["sideEffectLoweringImplemented"] is False
    assert summary["sideEffectMemorySupportClaim"] is False
    for row in payload["sideEffectMemoryFixtures"]:
        assert row["effectOrderPolicyImplemented"] is False
        assert row["externalCallPolicyImplemented"] is False
        assert row["memoryAliasPolicyImplemented"] is False
        assert row["loweringPerformed"] is False
        assert row["supportClaimAllowed"] is False


def test_fef_p105_release_gates_and_claim_flags_remain_false():
    payload = build_payload()
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["side_effect_memory_fixture_gate"] == "recorded"
    assert gates["side_effect_runtime_execution"] == "not_performed"
    assert gates["side_effect_lowering"] == "not_performed"
    assert gates["effect_order_policy"] == "blocked"
    assert gates["external_call_policy"] == "blocked"
    assert gates["memory_alias_policy"] == "blocked"
    assert gates["side_effect_memory_support"] == "blocked"
    assert gates["p104_private_reviewer_hold"] == "preserved"
    assert "Side-effecting calls or memory operations are supported." in payload["blockedStatements"]
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p105_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P105")


def test_fef_p105_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p105_side_effect_memory_fixture_gate.py",
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
    assert "FEF_P105_SIDE_EFFECT_MEMORY_FIXTURE_GATE_OK" in proc.stdout
