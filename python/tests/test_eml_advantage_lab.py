"""Tests for EML Advantage Lab."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_advantage_lab import (
    CLAIM_FLAGS,
    build_lab,
    validate_payload,
)
from scripts.eml_language_kernel import DATE


ROOT = Path(__file__).resolve().parents[2]
STAMP = DATE.replace("-", "_")
R10 = ROOT / f"python/results/eml_r10_cost_stability_lab/eml_r10_cost_stability_lab_{STAMP}.json"
R10B = ROOT / f"python/results/eml_r10b_runtime_bakeoff/eml_r10b_runtime_bakeoff_{STAMP}.json"
R10C = ROOT / f"python/results/eml_r10c_scoped_semantic_proof/eml_r10c_scoped_semantic_proof_{STAMP}.json"
R10E = ROOT / f"python/results/eml_r10e_formal_compiler_proof_skeleton/eml_r10e_formal_compiler_proof_skeleton_{STAMP}.json"
A5 = ROOT / f"python/results/eml_symbolic_regression_template_search/eml_symbolic_regression_template_search_{STAMP}.json"


def build_tmp(tmp_path):
    return build_lab(
        R10,
        R10B,
        R10C,
        R10E,
        A5,
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )


def packet_by_id(payload, case_id: str):
    return next(packet for packet in payload["advantagePackets"] if packet["caseId"] == case_id)


def test_build_advantage_lab_outputs_expected_packets(tmp_path):
    built = build_tmp(tmp_path)
    payload = built["payload"]
    assert payload["status"] == "EML_ADVANTAGE_LAB_PASS"
    assert payload["summary"]["packetCount"] >= 9
    assert packet_by_id(payload, "exp_from_eml_v0")
    assert packet_by_id(payload, "prime_signature_log_recovery_v0")
    assert packet_by_id(payload, "psi_residual_template_v0")
    validate_payload(payload)


def test_advantage_classes_include_truthful_mixed_and_losses(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    classes = {packet["advantageClass"] for packet in payload["advantagePackets"]}
    assert "standard_win" in classes
    assert "mixed" in classes
    assert "research_only" in classes
    assert payload["summary"]["standardWinCount"] >= 1


def test_scoped_certificate_is_visible_for_covered_cases(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    packet = packet_by_id(payload, "exp_from_eml_v0")
    assert packet["axes"]["proof"]["scopedSemanticCertificate"] is True
    assert packet["axes"]["proof"]["compilerCorrectnessProved"] is False


def test_psi_residual_remains_research_only(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    packet = packet_by_id(payload, "psi_residual_template_v0")
    assert packet["advantageClass"] == "research_only"
    assert packet["axes"]["search"]["included"] is True
    assert "No public product-readiness claim for this case." in packet["blockedClaims"]


def test_claim_flags_are_all_false(tmp_path):
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_tmp(tmp_path)["payload"]
    assert payload["summary"]["claimFlagsAllFalse"] is True
    for packet in payload["advantagePackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_generated_json_files_parse(tmp_path):
    built = build_tmp(tmp_path)
    for path in [built["result_path"], built["evidence_path"], built["feed_path"]]:
        json.loads(Path(path).read_text(encoding="utf-8"))
    packet_paths = sorted((tmp_path / "packets").glob("*_advantage_packet_*.json"))
    assert len(packet_paths) >= 9
    for path in packet_paths:
        packet = json.loads(path.read_text(encoding="utf-8"))
        assert packet["schemaVersion"] == "monogate.eml_advantage_packet.v0"


def test_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_advantage_lab.py",
            "--build",
            "--out-dir",
            str(tmp_path / "results"),
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
    assert "EML_ADVANTAGE_LAB_OK" in proc.stdout
