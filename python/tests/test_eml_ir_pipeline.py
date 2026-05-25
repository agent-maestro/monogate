"""Tests for EML IR v0 substrate pipeline."""

from __future__ import annotations

import json
import subprocess
import sys

from scripts.eml_ir_pipeline import build_ir, run_pipeline, validate_ir


def test_build_ir_emits_dag_nodes_and_output():
    ir = build_ir("sigmoid_v0", "1 / (1 + exp(-x))")
    validate_ir(ir)
    assert ir["schema_version"] == "eml-ir.v0"
    assert ir["output_node"] in {node["id"] for node in ir["nodes"]}
    assert any(node["op"] == "exp" for node in ir["nodes"])
    assert ir["boundaries"]["compiler_behavior_changed"] is False


def test_ir_reuses_superbest_lowering_metrics():
    ir = build_ir("double_exp_v0", "exp(x) + exp(x)")
    assert ir["tree_superbest_nodes"] == 4
    assert ir["dag_superbest_nodes"] == 3
    assert ir["extra_superbest_savings_nodes"] == 1
    assert ir["lowering"]["temporary_count"] == 1


def test_replay_packet_has_end_then_parked_and_hash_chain():
    ir = build_ir("gaussian_v0", "exp(-(x * x))")
    frames = ir["replay_packet"]["frames"]
    assert frames[-2]["lifecycle_state"] == "END"
    assert frames[-1]["lifecycle_state"] == "PARKED"
    assert frames[0]["replay_hash_prev"] is None
    for prev, cur in zip(frames, frames[1:]):
        assert cur["replay_hash_prev"] == prev["replay_hash"]


def test_division_nodes_are_guard_annotated():
    ir = build_ir("rational_v0", "x / (x + 1)")
    div_frames = [f for f in ir["replay_packet"]["frames"] if f["kernel_id"] == "div"]
    assert div_frames
    assert div_frames[0]["guard_action"] == "ANNOTATE"
    assert "denominator domain" in div_frames[0]["guard_reason"]


def test_pipeline_reuses_existing_work_inventory():
    payload = run_pipeline()
    assert payload["status"] == "EML_IR_SUBSTRATE_PIPELINE_READY"
    assert payload["program_count"] == 10
    assert payload["source_inventory"]["reused_superbest_dag_lowering"].endswith("superbest_dag_lowering.py")
    assert payload["best_extra_superbest_savings_nodes"] > 0


def test_pipeline_preserves_boundaries():
    payload = run_pipeline()
    assert payload["boundaries"]["internal_only"] is True
    assert payload["boundaries"]["compiler_behavior_changed"] is False
    assert payload["boundaries"]["canonical_row_table_changed"] is False
    assert payload["boundaries"]["package_publish_performed"] is False
    assert payload["boundaries"]["deploy_performed"] is False


def test_cli_single_expression_outputs_valid_json():
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_ir_pipeline.py",
            "exp(x) + exp(x)",
            "--program-id",
            "double_exp_v0",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    ir = json.loads(proc.stdout)
    assert ir["program_id"] == "double_exp_v0"
    assert ir["replay_packet"]["terminal_state"] == "PARKED"


def test_cli_strict_writes_payload():
    proc = subprocess.run(
        [sys.executable, "python/scripts/eml_ir_pipeline.py", "--strict"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "EML_IR_SUBSTRATE_PIPELINE_OK" in proc.stdout
