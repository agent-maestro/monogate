"""Tests for EML-R10C scoped semantic proof."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_atlas_annex import build_annex
from scripts.eml_atlas_promotion_gate import build_gate
from scripts.eml_r10_cost_stability_lab import build_lab
from scripts.eml_r10b_runtime_bakeoff import build_bakeoff
from scripts.eml_r10c_scoped_semantic_proof import (
    CERTIFICATES,
    CLAIM_FLAGS,
    build_proofs,
    packet_from_stub,
    validate_certificate_shape,
    validate_payload,
)
from scripts.eml_r11_hybrid_lowering_planner import build_planner
from scripts.eml_r12_generated_lowering_stubs import build_stubs


def build_r12_and_r10b(tmp_path):
    r10 = build_lab(
        tmp_path / "r10",
        tmp_path / "cost_packets",
        tmp_path / "reports",
        tmp_path / "evidence",
    )
    annex = build_annex(tmp_path / "annex", tmp_path / "reports", tmp_path / "evidence")
    gate = build_gate(Path(annex["result_path"]), tmp_path / "gate", tmp_path / "reports", tmp_path / "evidence")
    r11 = build_planner(
        Path(r10["result_path"]),
        Path(gate["result_path"]),
        tmp_path / "r11",
        tmp_path / "plans",
        tmp_path / "reports",
        tmp_path / "evidence",
    )
    r12 = build_stubs(
        Path(r11["result_path"]),
        tmp_path / "r12",
        tmp_path / "stubs",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    r10b = build_bakeoff(
        Path(r12["result_path"]),
        tmp_path / "r10b",
        tmp_path / "bakeoff_packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    return r12, r10b


def test_certificate_shapes_are_valid():
    assert {"exp_from_eml_v0", "subtraction_boundary_v0", "bose_boundary_expm1_v0", "ln_from_eml_v0"}.issubset(
        CERTIFICATES
    )
    for case_id, certificate in CERTIFICATES.items():
        validate_certificate_shape(case_id, certificate)
        assert certificate["domainGuards"]
        assert certificate["rewriteSteps"]


def test_subtraction_boundary_certificate_has_positive_domain_guard():
    certificate = CERTIFICATES["subtraction_boundary_v0"]
    assert "v > 0" in certificate["domainGuards"]
    assert certificate["rewriteSteps"][-1]["after"] == "v - u"


def test_packet_from_stub_uses_bakeoff_pass_status(tmp_path):
    r12, r10b = build_r12_and_r10b(tmp_path)
    stubs = {packet["caseId"]: packet for packet in r12["payload"]["stubPackets"]}
    bakeoffs = {packet["caseId"]: packet for packet in r10b["payload"]["bakeoffPackets"]}
    packet = packet_from_stub(stubs["bose_boundary_expm1_v0"], bakeoffs["bose_boundary_expm1_v0"])
    assert packet["schemaVersion"] == "monogate.eml_scoped_semantic_proof_packet.v0"
    assert packet["proofStatus"] == "scoped_proof_pass"
    assert packet["loweredExpression"] == "expm1(x)"
    assert packet["normalForm"] == "exp(x) - 1"
    assert packet["claimFlags"]["compiler_correctness_claim"] is False


def test_build_proofs_outputs_scoped_packets(tmp_path):
    r12, r10b = build_r12_and_r10b(tmp_path)
    built = build_proofs(
        Path(r12["result_path"]),
        Path(r10b["result_path"]),
        tmp_path / "r10c",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    payload = built["payload"]
    assert payload["status"] == "EML_R10C_SCOPED_SEMANTIC_PROOF_PASS"
    assert payload["summary"]["proofPacketCount"] >= 4
    assert payload["summary"]["scopedProofPassCount"] == payload["summary"]["proofPacketCount"]
    assert payload["summary"]["compilerCorrectnessClaim"] is False
    assert payload["summary"]["formalCompilerProofClaim"] is False
    validate_payload(payload)
    assert Path(built["result_path"]).exists()
    assert Path(built["report_path"]).exists()
    assert Path(built["evidence_path"]).exists()
    assert Path(built["feed_path"]).exists()


def test_generated_proof_packet_files_parse(tmp_path):
    r12, r10b = build_r12_and_r10b(tmp_path)
    build_proofs(
        Path(r12["result_path"]),
        Path(r10b["result_path"]),
        tmp_path / "r10c",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    paths = sorted((tmp_path / "packets").glob("*_scoped_semantic_proof_packet_*.json"))
    assert len(paths) >= 4
    for path in paths:
        packet = json.loads(path.read_text(encoding="utf-8"))
        assert packet["schemaVersion"] == "monogate.eml_scoped_semantic_proof_packet.v0"
        assert packet["proofStatus"] == "scoped_proof_pass"


def test_claim_flags_are_all_false(tmp_path):
    assert all(value is False for value in CLAIM_FLAGS.values())
    r12, r10b = build_r12_and_r10b(tmp_path)
    payload = build_proofs(
        Path(r12["result_path"]),
        Path(r10b["result_path"]),
        tmp_path / "r10c",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )["payload"]
    assert all(value is False for value in payload["claimFlags"].values())
    for packet in payload["proofPackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_evidence_and_feed_keep_compiler_claims_false(tmp_path):
    r12, r10b = build_r12_and_r10b(tmp_path)
    built = build_proofs(
        Path(r12["result_path"]),
        Path(r10b["result_path"]),
        tmp_path / "r10c",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    assert built["evidence"]["semanticReview"]["compilerCorrectnessClaim"] is False
    assert built["evidence"]["semanticReview"]["formalCompilerProofClaim"] is False
    assert built["feed"]["topFollowup"] == "R10E formal compiler proof skeleton or next MachLib witness"
    assert all(value is False for value in built["feed"]["claimFlags"].values())


def test_cli_build_strict(tmp_path):
    r12, r10b = build_r12_and_r10b(tmp_path)
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_r10c_scoped_semantic_proof.py",
            "--build",
            "--r12-path",
            r12["result_path"],
            "--r10b-path",
            r10b["result_path"],
            "--out-dir",
            str(tmp_path / "r10c"),
            "--packet-dir",
            str(tmp_path / "packets"),
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
    assert "EML_R10C_SCOPED_SEMANTIC_PROOF_OK" in proc.stdout
