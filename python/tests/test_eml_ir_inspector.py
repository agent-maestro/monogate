"""Tests for EML IR inspector v0."""

from __future__ import annotations

import json
import subprocess
import sys

from scripts.eml_ir_inspector import (
    build_action_queue,
    build_inspector_model,
    build_observatory_card,
    render_html,
    validate_model,
    write_explorer_model,
    write_outputs,
)


def test_inspector_model_validates_and_preserves_boundaries():
    model = build_inspector_model()
    validate_model(model)
    assert model["status"] == "EML_IR_INSPECTOR_READY"
    assert model["program_count"] == 10
    assert model["boundaries"]["compiler_behavior_changed"] is False
    assert model["boundaries"]["deploy_performed"] is False
    assert model["public_safe_mode"]["new_public_savings_claim"] is False


def test_inspector_model_has_replay_timeline_and_terminal_parked():
    model = build_inspector_model()
    program = model["programs"][0]
    assert program["timeline"][0]["state"] == "INIT"
    assert program["timeline"][-2]["state"] == "END"
    assert program["timeline"][-1]["state"] == "PARKED"
    assert "what_happened" in program["timeline"][0]


def test_inspector_edges_reference_existing_nodes():
    model = build_inspector_model()
    for program in model["programs"]:
        node_ids = {node["id"] for node in program["nodes"]}
        assert program["edge_count"] == len(program["edges"])
        for edge in program["edges"]:
            assert edge["from"] in node_ids
            assert edge["to"] in node_ids


def test_inspector_highlights_reused_softmax_nodes():
    model = build_inspector_model()
    softmax = next(p for p in model["programs"] if p["program_id"] == "attention_three_logits_three_outputs_v0")
    assert softmax["extra_superbest_savings_nodes"] > 0
    assert softmax["reused_nodes"]
    assert any(node["reuse_count"] > 1 for node in softmax["reused_nodes"])


def test_observatory_card_is_internal_only():
    card = build_observatory_card(build_inspector_model())
    assert card["status"] == "INTERNAL_EVIDENCE_CARD_READY"
    assert card["internal_only"] is True
    assert card["public_ready"] is False
    assert card["production_marketplace_modified"] is False


def test_action_queue_names_browser_bridge_and_contract():
    queue = build_action_queue(build_inspector_model())
    item_ids = {item["id"] for item in queue["items"]}
    assert "eml_ir_browser_bridge" in item_ids
    assert "eml_ir_lowering_contract" in item_ids
    assert queue["deploy_performed"] is False


def test_html_is_static_and_embeds_model():
    html = render_html(build_inspector_model())
    assert "EML IR Inspector v0" in html
    assert "inspector-data" in html
    assert "http://" not in html
    assert "https://" not in html


def test_write_outputs_creates_json_and_html(tmp_path):
    model = build_inspector_model()
    out_dir = tmp_path / "inspector"
    report = tmp_path / "report.md"
    write_outputs(model, out_dir, report)
    parsed = json.loads((out_dir / "inspector_model_2026_05_25.json").read_text())
    assert parsed["status"] == "EML_IR_INSPECTOR_READY"
    assert (out_dir / "index.html").read_text().startswith("<!doctype html>")
    assert "EML IR Inspector v0" in report.read_text()


def test_write_explorer_model_creates_importable_json(tmp_path):
    model = build_inspector_model()
    out = tmp_path / "src" / "data" / "eml_ir_inspector_model.json"
    write_explorer_model(model, out)
    parsed = json.loads(out.read_text())
    assert parsed["status"] == "EML_IR_INSPECTOR_READY"
    assert parsed["boundaries"]["external_network_required"] is False


def test_cli_strict_writes_demo_packet(tmp_path):
    out_dir = tmp_path / "demo"
    report = tmp_path / "report.md"
    explorer_model = tmp_path / "explorer" / "model.json"
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_ir_inspector.py",
            "--out-dir",
            str(out_dir),
            "--report",
            str(report),
            "--explorer-model",
            str(explorer_model),
            "--strict",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "EML_IR_INSPECTOR_OK" in proc.stdout
    assert (out_dir / "index.html").exists()
    assert explorer_model.exists()
    assert json.loads((out_dir / "observatory_card_2026_05_25.json").read_text())["public_ready"] is False
