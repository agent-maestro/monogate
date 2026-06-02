"""Tests for GB-VIS-A1 claim topology renderer contract."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.gb_vis_a1_claim_topology_renderer_contract import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def node_by_id(payload, node_id: str):
    return next(item for item in payload["topologyNodes"] if item["nodeId"] == node_id)


def edge_by_id(payload, edge_id: str):
    return next(item for item in payload["topologyEdges"] if item["edgeId"] == edge_id)


def test_gb_vis_a1_consumes_act_sources():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "GB_VIS_A1_CLAIM_TOPOLOGY_RENDERER_CONTRACT_PASS"
    assert payload["sourceContract"] == "act-a1-abstract-concrete-trace-contract"
    assert payload["sourceObligationsPacket"] == "act-a2-alpha-gamma-validator-obligations"
    assert payload["sourceDryRunPacket"] == "act-a3-alpha-gamma-dry-run-validator-skeleton"


def test_gb_vis_a1_records_topology_counts():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["nodeCount"] == 23
    assert payload["summary"]["edgeCount"] == 16
    assert payload["summary"]["artifactClassNodeCount"] == 4
    assert payload["summary"]["validatorObligationNodeCount"] == 6
    assert payload["summary"]["dryRunCheckNodeCount"] == 6
    assert payload["summary"]["failureModeNodeCount"] == 5
    assert payload["summary"]["visualEncodingCount"] == 5
    assert payload["summary"]["rendererGuardrailCount"] == 4


def test_gb_vis_a1_preserves_source_boundaries():
    payload = build_payload(ATLAS_GATE)
    source = node_by_id(payload, "source_freeze_packet")
    abstract = node_by_id(payload, "abstract_claim_object")
    assert payload["summary"]["sourceCheckedStatement"] == "eml x (exp 1) = exp x - 1"
    assert payload["summary"]["sourceRuntimeControl"] == "protected_expm1_remains_runtime_control"
    assert payload["summary"]["sourcePublicStatus"] == "held_private"
    assert source["runtimeControl"] == "protected_expm1_remains_runtime_control"
    assert abstract["publicStatus"] == "held_private"


def test_gb_vis_a1_records_alpha_gamma_and_dry_run_edges():
    payload = build_payload(ATLAS_GATE)
    alpha_edge = edge_by_id(payload, "source_freeze_to_abstract_claim_alpha")
    gamma_edge = edge_by_id(payload, "abstract_claim_to_artifact_class:evidence_packet")
    dry_run_edge = edge_by_id(payload, "obligation_to_dry_run:alpha_traceability_complete")
    assert alpha_edge["operator"] == "alpha"
    assert "runtimeControl" in alpha_edge["preserves"]
    assert gamma_edge["operator"] == "gamma"
    assert gamma_edge["target"] == "artifact_class:evidence_packet"
    assert dry_run_edge["edgeKind"] == "validated_by_dry_run_skeleton"


def test_gb_vis_a1_records_failure_mode_block_edges():
    payload = build_payload(ATLAS_GATE)
    edge = edge_by_id(payload, "failure_mode_blocks:public_gate_bypass")
    node = node_by_id(payload, "failure_mode:public_gate_bypass")
    assert edge["edgeKind"] == "blocks_claim_escalation"
    assert edge["target"] == "abstract_claim_object"
    assert node["severity"] == "block"


def test_gb_vis_a1_records_visual_encodings_and_guardrails():
    payload = build_payload(ATLAS_GATE)
    encodings = {item["encodingId"] for item in payload["visualEncodings"]}
    guardrails = {item["guardrailId"] for item in payload["rendererGuardrails"]}
    assert "claim_strength_weight" in encodings
    assert "runtime_boundary_marker" in encodings
    assert "failure_mode_block_marker" in encodings
    assert "no_public_surface_without_gate" in guardrails
    assert "no_soundness_by_visual_pattern" in guardrails
    assert "no_runtime_change_by_renderer" in guardrails


def test_gb_vis_a1_records_contract_without_renderer_or_public_claim():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimTopologyContractRecorded"] is True
    assert payload["summary"]["actSourcesConsumed"] is True
    assert payload["summary"]["topologyNodesRecorded"] is True
    assert payload["summary"]["topologyEdgesRecorded"] is True
    assert payload["summary"]["visualEncodingContractRecorded"] is True
    assert payload["summary"]["rendererGuardrailsRecorded"] is True
    assert payload["summary"]["rendererImplemented"] is False
    assert payload["summary"]["visualizationStarted"] is False
    assert payload["summary"]["visualizationRendered"] is False
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["productionValidatorImplemented"] is False
    assert payload["summary"]["validatorSoundnessProved"] is False
    assert payload["summary"]["soundnessProved"] is False
    assert payload["summary"]["fullGaloisConnectionClaim"] is False
    assert payload["summary"]["abstractInterpretationSoundnessProved"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["proofAttemptStarted"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_gb_vis_a1_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    true_keys = {
        "claim_topology_contract_recorded",
        "act_sources_consumed",
        "topology_nodes_recorded",
        "topology_edges_recorded",
        "visual_encoding_contract_recorded",
        "renderer_guardrails_recorded",
    }
    for key in true_keys:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in true_keys:
            assert value is False


def test_gb_vis_a1_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# GB-VIS-A1")


def test_gb_vis_a1_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/gb_vis_a1_claim_topology_renderer_contract.py",
            "--build",
            "--atlas-gate-path",
            str(ATLAS_GATE),
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
    assert "GB_VIS_A1_CLAIM_TOPOLOGY_RENDERER_CONTRACT_OK" in proc.stdout
