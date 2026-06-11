"""Tests for FEF-P111 side-effect lowering/codegen proposal."""

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

from scripts.fef_p111_side_effect_lowering_codegen_proposal import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    build_proposal,
    validate_payload,
)


def test_fef_p111_records_proposal_without_applying_it():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P111_SIDE_EFFECT_LOWERING_CODEGEN_PROPOSAL_PASS"
    assert payload["decision"] == "selected_side_effect_lowering_codegen_proposal_recorded_not_applied"
    assert summary["selectedFixtureId"] == "c_global_state_update_v0"
    assert summary["proposalStatus"] == "proposal_recorded_not_applied"
    assert summary["proposalApplied"] is False
    assert summary["implementationDiffProduced"] is False


def test_fef_p111_proposal_names_ordered_effect_lowering_intent():
    payload = build_payload()
    proposal = payload["loweringCodegenProposal"]
    intent = proposal["loweringIntent"]
    assert intent["loweringKind"] == "ordered_effect_region_with_guarded_state_update"
    assert intent["effectOrder"] == [
        "evaluate_guard",
        "call_deterministic_update_stub_if_guard_true",
        "write_bounded_state_cell_if_call_occurs",
        "return_bounded_state_cell",
    ]
    assert intent["stateModel"] == "single_explicit_state_cell_no_alias_escape"
    assert intent["externalCallModel"] == "deterministic_stubbed_update_state_only"


def test_fef_p111_pipeline_hooks_and_review_checks_are_complete():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["intendedPipelineHookCount"] == 4
    assert summary["requiredApprovalGateCount"] == 6
    assert summary["rollbackCriteriaCount"] == 5
    assert summary["reviewCheckCount"] == 12
    assert summary["reviewCheckPassCount"] == 12
    assert summary["reviewCheckFailCount"] == 0


def test_fef_p111_build_proposal_remains_not_applied():
    p110_payload = {
        "summary": {
            "selectedFixtureId": "c_global_state_update_v0",
        }
    }
    proposal = build_proposal(p110_payload)
    assert proposal["scope"] == "selected_c_global_state_update_v0_only"
    assert proposal["proposalApplied"] is False
    assert proposal["implementationDiffProduced"] is False
    assert proposal["generatedFixtureTextProduced"] is False
    assert proposal["generatedTargetExecuted"] is False
    assert proposal["reingestedTargetExecuted"] is False
    assert proposal["installedInForge"] is False
    assert proposal["installedInEfrog"] is False


def test_fef_p111_blocks_execution_lowering_codegen_reingest_and_support():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["generatedFixtureTextProduced"] is False
    assert summary["generatedTargetExecuted"] is False
    assert summary["reingestedTargetExecuted"] is False
    assert summary["sideEffectLoweringImplemented"] is False
    assert summary["sideEffectCodegenPolicyImplemented"] is False
    assert summary["sideEffectReingestPolicyClaim"] is False
    assert summary["sideEffectMemorySupportClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p111_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P111")


def test_fef_p111_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p111_side_effect_lowering_codegen_proposal.py",
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
    assert "FEF_P111_SIDE_EFFECT_LOWERING_CODEGEN_PROPOSAL_OK" in proc.stdout
