"""Tests for FEF-P29 rc_filter full Lean proof discharge."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p29_rc_filter_full_lean_proof_discharge import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p29_records_full_rc_filter_discharge():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P29_RC_FILTER_FULL_LEAN_PROOF_DISCHARGE_PASS"
    assert payload["decision"] == "rc_filter_generated_file_reviewed_and_all_placeholders_discharged"
    assert summary["selectedDischargedTheoremCount"] == 5
    assert summary["remainingPlaceholderTheoremCount"] == 0


def test_fef_p29_discharges_rc_step_response_at_zero():
    payload = build_payload()
    packet = payload["rcFilterProofPackets"][0]
    proofs = {proof["theoremName"]: proof for proof in packet["selectedDischargedTheorems"]}
    assert "rc_step_response_at_zero" in proofs
    body = "\n".join(proofs["rc_step_response_at_zero"]["dischargedProofBody"])
    assert "zero_div_of_pos h1" in body
    assert "exp_zero" in body
    assert "mul_zero" in body


def test_fef_p29_selected_file_typechecks_zero_sorry():
    payload = build_payload()
    packet = payload["rcFilterProofPackets"][0]
    summary = payload["summary"]
    assert packet["generatedFileSorryCount"] == 5
    assert packet["dischargedFileSorryCount"] == 0
    assert packet["configuredLeanCheck"]["status"] == "typecheck_selected_file_zero_sorry_pass"
    assert summary["leanCheckStatuses"] == ["typecheck_selected_file_zero_sorry_pass"]


def test_fef_p29_keeps_broad_claims_false():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["selectedRcFilterFileZeroSorryClaim"] is False
    assert summary["leanProofClaim"] is False
    assert summary["allGeneratedLeanFilesProvedClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p29_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P29")


def test_fef_p29_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p29_rc_filter_full_lean_proof_discharge.py",
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
    assert "FEF_P29_RC_FILTER_FULL_LEAN_PROOF_DISCHARGE_OK" in proc.stdout
