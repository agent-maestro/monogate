"""Tests for FEF-P21 rc_filter Lean proof-discharge validator."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p21_rc_filter_lean_proof_discharge import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p21_records_reviewed_rc_filter_discharges():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P21_RC_FILTER_LEAN_PROOF_DISCHARGE_PASS"
    assert summary["selectedDischargedTheoremCount"] == 4
    assert summary["remainingPlaceholderTheoremCount"] == 1
    assert summary["generatedFileSorryCount"] == 5
    assert summary["dischargedFileSorryCount"] == 1
    assert summary["leanCheckStatuses"] == ["typecheck_selected_proofs_with_remaining_sorry_pass"]


def test_fef_p21_packet_keeps_rc_filter_blocker_visible():
    payload = build_payload()
    packet = payload["rcFilterProofPackets"][0]
    theorem_names = [theorem["theoremName"] for theorem in packet["selectedDischargedTheorems"]]
    assert theorem_names == [
        "rc_time_constant_def",
        "rc_steady_state_equals_input",
        "rc_initial_output_zero",
        "rc_step_response_form",
    ]
    assert packet["remainingPlaceholderTheorems"] == ["rc_step_response_at_zero"]
    for theorem in packet["selectedDischargedTheorems"]:
        assert theorem["dischargedProofBody"] == ["  rfl"]


def test_fef_p21_keeps_broad_claims_false():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["candidateReviewedProofClaim"] is False
    assert summary["leanProofClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())
    for packet in payload["rcFilterProofPackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_fef_p21_release_gates_keep_remaining_work_blocked():
    payload = build_payload()
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["candidate_found_obligations_reviewed"] == "pass"
    assert gates["selected_rc_filter_theorems_typecheck"] == "pass"
    assert gates["same_file_remaining_placeholder_visible"] == "pass"
    assert gates["remaining_generated_lean_proofs_discharged"] == "blocked"
    assert gates["machlib_foundational_audit"] == "blocked"


def test_fef_p21_writes_outputs(tmp_path):
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
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P21")


def test_fef_p21_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p21_rc_filter_lean_proof_discharge.py",
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
    assert "FEF_P21_RC_FILTER_LEAN_PROOF_DISCHARGE_OK" in proc.stdout
