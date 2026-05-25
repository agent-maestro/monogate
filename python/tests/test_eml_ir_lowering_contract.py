"""Tests for EML IR lowering contract v0 artifacts."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_lowering_contract_schema_has_required_sections():
    data = json.loads((ROOT / "schemas/eml_ir_lowering_contract_v0.json").read_text())
    required = set(data["required"])
    assert "primitive_set" in required
    assert "determinism_rules" in required
    assert "tree_vs_dag_semantics" in required
    assert "replay_rules" in required
    assert data["properties"]["contract_id"]["const"] == "eml_ir_lowering_contract_v0_2026_05_25"


def test_lowering_contract_boundary_schema_blocks_public_claims():
    data = json.loads((ROOT / "schemas/eml_ir_lowering_contract_v0.json").read_text())
    boundaries = data["properties"]["boundaries"]["properties"]
    assert boundaries["internal_only"]["const"] is True
    assert boundaries["deploy_performed"]["const"] is False
    assert boundaries["package_publish_performed"]["const"] is False
    assert boundaries["public_theorem_claim"]["const"] is False
    assert boundaries["formal_verification_claim"]["const"] is False
    assert boundaries["production_marketplace_modified"]["const"] is False


def test_lowering_contract_doc_states_tree_vs_dag_boundary():
    text = (ROOT / "docs/eml_ir_lowering_contract_v0_2026_05_25.md").read_text()
    assert "Tree SuperBEST cost counts every operation occurrence" in text
    assert "DAG SuperBEST cost counts each structurally identical repeated" in text
    assert "Do not turn DAG savings into public headline claims" in text
    assert "No compiler behavior changed" in text


def test_lowering_contract_v1_schema_names_bridge_rules():
    data = json.loads((ROOT / "schemas/eml_ir_lowering_contract_v1.json").read_text())
    required = set(data["required"])
    assert "node_identity_rules" in required
    assert "dag_cost_rules" in required
    assert "replay_frame_mapping" in required
    assert "field_bridge_rules" in required
    assert data["properties"]["contract_id"]["const"] == "eml_ir_lowering_contract_v1_2026_05_25"
    assert data["properties"]["status"]["const"] == "INTERNAL_LOWERING_CONTRACT_V1_DRAFT"


def test_lowering_contract_v1_boundaries_remain_internal():
    data = json.loads((ROOT / "schemas/eml_ir_lowering_contract_v1.json").read_text())
    boundaries = data["properties"]["boundaries"]["properties"]
    assert boundaries["internal_only"]["const"] is True
    assert boundaries["public_ready"]["const"] is False
    assert boundaries["compiler_behavior_changed"]["const"] is False
    assert boundaries["canonical_row_table_changed"]["const"] is False
    assert boundaries["deploy_performed"]["const"] is False
    assert boundaries["package_publish_performed"]["const"] is False
    assert boundaries["formal_verification_claim"]["const"] is False
    assert boundaries["certified_safety_claim"]["const"] is False
    assert boundaries["production_controller_claim"]["const"] is False
    assert boundaries["public_theorem_claim"]["const"] is False


def test_lowering_contract_v1_doc_links_ir_field_and_replay():
    text = (ROOT / "docs/eml_ir_lowering_contract_v1_2026_05_25.md").read_text()
    assert "expression -> normalized DAG nodes -> guarded replay frames" in text
    assert "Tree SuperBEST cost counts every operation occurrence" in text
    assert "DAG SuperBEST cost counts each structurally identical repeated operation once" in text
    assert "The complex field view is a visual-intuition bridge" in text
    assert "It does not change compiler behavior" in text
