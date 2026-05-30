"""Tests for FEF-P14 Lean structural validator."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p14_lean_structural_validator import (
    CASES,
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p14_records_selected_lean_structural_validation():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "FEF_P14_LEAN_STRUCTURAL_VALIDATOR_PASS"
    assert payload["summary"]["caseCount"] == len(CASES)
    assert payload["summary"]["packetCount"] == len(CASES)
    assert payload["summary"]["passCount"] == len(CASES)


def test_fef_p14_counts_theorems_and_sorry_placeholders():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["generatedTargetLanguages"] == ["lean"]
    assert summary["expectedTheoremCount"] == 5
    assert summary["declaredTheoremCount"] == 5
    assert summary["sorryCount"] >= 5
    for packet in payload["structuralPackets"]:
        assert packet["structuralStatus"] == "pass"
        assert not packet["missingTheorems"]
        assert packet["sorryCount"] >= len(packet["expectedTheorems"])
        assert any(name.startswith("MachLib.") for name in packet["machlibImports"])


def test_fef_p14_records_toolchain_boundary_without_proof_claim():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["leanTypecheckClaim"] is False
    assert summary["leanProofClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_lean_structural_validation"] == "pass"
    assert gates["lean_typecheck_in_configured_machlib_project"] == "blocked"
    assert gates["lean_proofs_discharged"] == "blocked"


def test_fef_p14_claim_flags_remain_false():
    payload = build_payload()
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in payload["claimFlags"].values())
    for packet in payload["structuralPackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_fef_p14_writes_outputs(tmp_path):
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
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P14")


def test_fef_p14_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p14_lean_structural_validator.py",
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
    assert "FEF_P14_LEAN_STRUCTURAL_VALIDATOR_OK" in proc.stdout
