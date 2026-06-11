"""Tests for FEF-P19 additional selected Lean proof-discharge validator."""

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

from scripts.fef_p19_additional_lean_proof_discharge import (
    CASES,
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p19_records_one_additional_selected_proof():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P19_ADDITIONAL_LEAN_PROOF_DISCHARGE_PASS"
    assert summary["caseCount"] == len(CASES)
    assert summary["additionalSelectedProofPassCount"] == len(CASES)
    assert summary["additionalSelectedProofBlockedCount"] == 0
    assert summary["generatedFileSorryCount"] == 2
    assert summary["dischargedFileSorryCount"] == 1
    assert summary["remainingPlaceholderTheoremCount"] == 1


def test_fef_p19_packet_records_remaining_same_file_placeholder():
    payload = build_payload()
    packet = payload["additionalProofPackets"][0]
    assert packet["sourcePath"] == "examples/carriers/electronics/mosfet_iv.eml"
    assert packet["theoremName"] == "mosfet_zero_overdrive_zero_current"
    assert packet["remainingPlaceholderTheorems"] == ["mosfet_prefactor_positive"]
    assert packet["dischargedProofBody"] == [
        "  unfold id_at_threshold",
        "  rfl",
    ]
    assert packet["configuredLeanCheck"]["status"] == "typecheck_selected_proof_with_remaining_sorry_pass"


def test_fef_p19_keeps_broad_claims_false():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["additionalSelectedLeanProofClaim"] is False
    assert summary["leanProofClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())
    for packet in payload["additionalProofPackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_fef_p19_release_gates_keep_remaining_work_blocked():
    payload = build_payload()
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["machlib_build_lib_found"] == "pass"
    assert gates["one_additional_selected_theorem_typechecks"] == "pass"
    assert gates["same_file_remaining_placeholder_visible"] == "pass"
    assert gates["remaining_generated_lean_proofs_discharged"] == "blocked"
    assert gates["machlib_foundational_audit"] == "blocked"
    assert gates["public_package_published"] == "blocked"


def test_fef_p19_writes_outputs(tmp_path):
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
    assert len(packets) == len(CASES)
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P19")


def test_fef_p19_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p19_additional_lean_proof_discharge.py",
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
    assert "FEF_P19_ADDITIONAL_LEAN_PROOF_DISCHARGE_OK" in proc.stdout
