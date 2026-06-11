"""Tests for FEF-P60 control-flow IR schema."""

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

from scripts.fef_p60_control_flow_ir_schema import (
    CLAIM_FLAGS,
    CONTROL_FLOW_IR_SCHEMA_VERSION,
    build_outputs,
    build_payload,
    validate_fragment,
    validate_payload,
    validate_schema_object,
)


def test_fef_p60_records_schema_without_implementation_claim():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P60_CONTROL_FLOW_IR_SCHEMA_PASS"
    assert payload["decision"] == "control_flow_ir_schema_recorded_implementation_blocked"
    assert payload["controlFlowIrSchema"]["$id"] == CONTROL_FLOW_IR_SCHEMA_VERSION
    assert summary["p59ValidationPass"] is True
    assert summary["p59ClaimFlagsAllFalse"] is True
    assert summary["controlFlowIrSchemaWritten"] is True
    assert summary["controlFlowIrImplemented"] is False
    assert summary["frontendLoweringChanged"] is False


def test_fef_p60_schema_surface_has_expected_required_shapes():
    payload = build_payload()
    schema = payload["controlFlowIrSchema"]
    validate_schema_object(schema)
    assert set(schema["required"]) == {
        "schemaVersion",
        "programId",
        "sourceLanguage",
        "functionName",
        "entryBlockId",
        "exitBlockId",
        "blocks",
        "unsupportedConstructs",
        "semanticObligations",
        "claimFlags",
        "nonClaims",
    }
    assert set(schema["$defs"]["block"]["properties"]["kind"]["enum"]) == {
        "cfg_entry",
        "basic_block",
        "merge",
        "cfg_exit",
    }
    assert set(schema["$defs"]["statement"]["properties"]["kind"]["enum"]) == {
        "assignment",
        "phi_or_select",
        "unsupported_construct",
    }
    assert set(schema["$defs"]["terminator"]["properties"]["kind"]["enum"]) == {
        "branch",
        "return_value",
        "jump",
        "unreachable",
    }


def test_fef_p60_selected_fragments_cover_all_branch_closures():
    payload = build_payload()
    fragments = {fragment["programId"]: fragment for fragment in payload["selectedIrFragments"]}
    assert set(fragments) == {
        "c_ternary_select_v0",
        "c_if_early_return_relu_v0",
        "c_if_else_clamp_v0",
        "rust_if_expr_relu_v0",
        "rust_if_return_clamp_v0",
    }
    for fragment in fragments.values():
        validate_fragment(fragment)
        assert fragment["schemaVersion"] == CONTROL_FLOW_IR_SCHEMA_VERSION
        assert any(block["kind"] == "cfg_entry" for block in fragment["blocks"])
        assert any(block["kind"] == "cfg_exit" for block in fragment["blocks"])
        assert all(value is False for value in fragment["claimFlags"].values())
    assert fragments["c_ternary_select_v0"]["blocks"][0]["statements"][0]["kind"] == "phi_or_select"
    assert fragments["c_if_else_clamp_v0"]["sourceLanguage"] == "c"
    assert fragments["rust_if_return_clamp_v0"]["sourceLanguage"] == "rust"


def test_fef_p60_preserves_p59_inventory_totals():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["selectedIrFragmentCount"] == 5
    assert summary["selectedBranchClosureCount"] == 5
    assert summary["p59IrNodeCount"] == 10
    assert summary["p59UnsupportedFormCount"] == 6
    assert summary["p59OpenSemanticObligationCount"] == 6
    assert summary["schemaRequiredFieldCount"] == 11
    assert summary["schemaBlockKindCount"] == 4
    assert summary["schemaStatementKindCount"] == 3
    assert summary["schemaTerminatorKindCount"] == 4


def test_fef_p60_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["control_flow_ir_schema"] == "recorded"
    assert gates["control_flow_ir_implementation"] == "blocked"
    assert gates["frontend_lowering_change"] == "not_performed"
    assert "The control-flow IR is implemented in Forge/eFrog." in payload["blockedStatements"]
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


def test_fef_p60_writes_outputs_and_schema(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        tmp_path / "schemas",
    )
    for key in ["result_path", "evidence_path", "feed_path", "schema_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    schema = json.loads(Path(built["schema_path"]).read_text(encoding="utf-8"))
    assert schema["$id"] == CONTROL_FLOW_IR_SCHEMA_VERSION
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P60")


def test_fef_p60_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p60_control_flow_ir_schema.py",
            "--build",
            "--out-dir",
            str(tmp_path / "results"),
            "--report-dir",
            str(tmp_path / "reports"),
            "--evidence-dir",
            str(tmp_path / "evidence"),
            "--command-feed-dir",
            str(tmp_path / "feeds"),
            "--schema-dir",
            str(tmp_path / "schemas"),
            "--strict",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "FEF_P60_CONTROL_FLOW_IR_SCHEMA_OK" in proc.stdout
