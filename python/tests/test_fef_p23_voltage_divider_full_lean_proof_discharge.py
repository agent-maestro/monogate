"""Tests for FEF-P23 voltage_divider full Lean proof-discharge validator."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p23_voltage_divider_full_lean_proof_discharge import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p23_records_reviewed_voltage_divider_discharges():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P23_VOLTAGE_DIVIDER_FULL_LEAN_PROOF_DISCHARGE_PASS"
    assert summary["selectedDischargedTheoremCount"] == 3
    assert summary["remainingPlaceholderTheoremCount"] == 0
    assert summary["generatedFileSorryCount"] == 3
    assert summary["dischargedFileSorryCount"] == 0
    assert summary["leanCheckStatuses"] == ["typecheck_selected_file_zero_sorry_pass"]


def test_fef_p23_packet_records_zero_sorry_selected_file():
    payload = build_payload()
    packet = payload["voltageDividerProofPackets"][0]
    theorem_names = [theorem["theoremName"] for theorem in packet["selectedDischargedTheorems"]]
    assert theorem_names == [
        "voltage_divider_law",
        "voltage_divider_denom_pos",
        "voltage_divider_symmetric_half",
    ]
    assert packet["remainingPlaceholderTheorems"] == []
    proofs = {theorem["theoremName"]: theorem["dischargedProofBody"] for theorem in packet["selectedDischargedTheorems"]}
    assert proofs["voltage_divider_law"] == ["  rfl"]
    assert proofs["voltage_divider_denom_pos"] == ["  unfold rsum", "  exact add_pos h1 h2"]
    assert proofs["voltage_divider_symmetric_half"] == ["  rfl"]


def test_fef_p23_keeps_broad_claims_false():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["candidateReviewedProofClaim"] is False
    assert summary["leanProofClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())
    for packet in payload["voltageDividerProofPackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_fef_p23_release_gates_keep_remaining_work_blocked():
    payload = build_payload()
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_voltage_divider_obligations_reviewed"] == "pass"
    assert gates["selected_voltage_divider_file_typechecks"] == "pass"
    assert gates["selected_voltage_divider_file_zero_sorry"] == "pass"
    assert gates["remaining_generated_lean_proofs_discharged"] == "blocked"
    assert gates["machlib_foundational_audit"] == "blocked"


def test_fef_p23_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    packets = sorted((tmp_path / "packets").glob("*.json"))
    assert len(packets) == 1
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P23")


def test_fef_p23_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p23_voltage_divider_full_lean_proof_discharge.py",
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
    assert "FEF_P23_VOLTAGE_DIVIDER_FULL_LEAN_PROOF_DISCHARGE_OK" in proc.stdout
