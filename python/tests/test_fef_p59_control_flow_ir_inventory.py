"""Tests for FEF-P59 control-flow IR inventory."""

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

from scripts.fef_p59_control_flow_ir_inventory import (
    CLAIM_FLAGS,
    IR_NODES,
    SELECTED_MAPPINGS,
    SEMANTIC_OBLIGATIONS,
    SOURCE_PACKETS,
    UNSUPPORTED_FORMS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p59_links_source_packets_and_preserves_p57_totals():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P59_CONTROL_FLOW_IR_INVENTORY_PASS"
    assert payload["decision"] == "control_flow_ir_inventory_recorded_general_support_blocked"
    assert set(payload["sourcePackets"]) == set(SOURCE_PACKETS)
    assert summary["sourcePacketCount"] == 3
    assert summary["allSourcePacketsValidationPass"] is True
    assert summary["allSourcePacketClaimFlagsFalse"] is True
    assert summary["selectedBranchCaseCount"] == 5
    assert summary["selectedBranchClosureCount"] == 5
    assert summary["selectedBranchReingestPacketCount"] == 10
    assert summary["selectedBranchPacketSampleComparisons"] == 58
    assert summary["p51SelectedBlockedCount"] == 0
    assert summary["p58BlockedGapCount"] == 6


def test_fef_p59_candidate_ir_nodes_are_required_and_reviewable():
    payload = build_payload()
    summary = payload["summary"]
    nodes = {node["id"]: node for node in payload["irNodes"]}
    assert summary["irNodeCount"] == len(IR_NODES) == 10
    assert summary["requiredIrNodeCount"] == 10
    for node_id in [
        "cfg_entry",
        "cfg_exit",
        "basic_block",
        "condition_expr",
        "branch",
        "merge",
        "return_value",
        "assignment",
        "phi_or_select",
        "unsupported_construct",
    ]:
        assert node_id in nodes
        assert nodes[node_id]["requiredForGeneralSupport"] is True


def test_fef_p59_maps_all_selected_branch_closures_to_ir_paths():
    payload = build_payload()
    mappings = {row["caseId"]: row for row in payload["selectedClosureMappings"]}
    assert len(mappings) == len(SELECTED_MAPPINGS) == 5
    assert mappings["c_ternary_select_v0"]["candidateIrPath"] == [
        "condition_expr",
        "phi_or_select",
        "return_value",
    ]
    assert "branch" in mappings["c_if_early_return_relu_v0"]["candidateIrPath"]
    assert "merge" in mappings["c_if_else_clamp_v0"]["candidateIrPath"]
    assert "phi_or_select" in mappings["rust_if_expr_relu_v0"]["candidateIrPath"]
    assert "cfg_exit" in mappings["rust_if_return_clamp_v0"]["candidateIrPath"]
    for row in mappings.values():
        assert row["currentLowering"].endswith("step01")
        assert row["missingForGeneralization"]


def test_fef_p59_unsupported_forms_and_obligations_remain_blocked_or_open():
    payload = build_payload()
    summary = payload["summary"]
    unsupported = {row["id"]: row for row in payload["unsupportedForms"]}
    obligations = {row["id"]: row for row in payload["semanticObligations"]}
    assert summary["unsupportedFormCount"] == len(UNSUPPORTED_FORMS) == 6
    assert summary["semanticObligationCount"] == len(SEMANTIC_OBLIGATIONS) == 6
    assert summary["openSemanticObligationCount"] == 6
    assert unsupported["loops_and_back_edges"]["nextValidator"] == "loop_construct_blocker_gate"
    assert unsupported["source_preserving_roundtrip"]["status"] == "blocked"
    assert obligations["condition_truth_semantics"]["status"] == "open"
    assert obligations["unsupported_construct_fail_closed"]["status"] == "open"
    for row in unsupported.values():
        assert row["status"] == "blocked"
    for row in obligations.values():
        assert row["status"] == "open"


def test_fef_p59_statement_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["control_flow_ir_inventory"] == "recorded"
    assert gates["control_flow_ir_implementation"] == "not_started"
    assert gates["general_branch_control_flow_support"] == "blocked"
    assert "The control-flow IR is implemented." in payload["blockedStatements"]
    assert summary["controlFlowIrImplemented"] is False
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["branchControlFlowReingestClaim"] is False
    assert summary["fullNonGeneratedSourceRoundtripClaim"] is False
    assert summary["arbitrarySourceFamilyClaim"] is False
    assert summary["publicReady"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p59_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P59")


def test_fef_p59_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p59_control_flow_ir_inventory.py",
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
    assert "FEF_P59_CONTROL_FLOW_IR_INVENTORY_OK" in proc.stdout
