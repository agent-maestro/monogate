"""Tests for FEF-P20 Lean proof-candidate scanner."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p17_broader_lean_typecheck_with_sorry import CASES as P17_CASES
from scripts.fef_p20_lean_proof_candidate_scanner import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p20_scans_selected_p17_family():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P20_LEAN_PROOF_CANDIDATE_SCANNER_PASS"
    assert summary["caseCount"] == len(P17_CASES)
    assert summary["proofObligationCount"] == 15
    assert summary["candidateFoundCount"] >= 1
    assert summary["blockedCandidateCount"] >= 1
    assert 0.0 < summary["candidateCoverageRatio"] < 1.0


def test_fef_p20_records_candidate_and_blocker_examples():
    payload = build_payload()
    obligations = [
        obligation
        for packet in payload["candidatePackets"]
        for obligation in packet["obligations"]
    ]
    found = [obligation for obligation in obligations if obligation["candidateStatus"] == "candidate_found"]
    blocked = [obligation for obligation in obligations if obligation["candidateStatus"] == "blocked_no_candidate_passed"]
    assert any(obligation["theoremName"] == "add_nonneg_is_nonneg" for obligation in found)
    assert any(obligation["theoremName"] == "clamp_in_unit_interval" for obligation in blocked)
    for obligation in found:
        assert obligation["selectedCandidate"] is not None
        assert obligation["selectedCandidate"]["leanCheck"]["status"] == "candidate_typecheck_pass"
    for obligation in blocked:
        assert obligation["selectedCandidate"] is None


def test_fef_p20_candidate_bodies_do_not_use_sorry():
    payload = build_payload()
    for packet in payload["candidatePackets"]:
        for obligation in packet["obligations"]:
            for attempt in obligation["attempts"]:
                assert all("sorry" not in line for line in attempt["proofBody"])


def test_fef_p20_keeps_broad_claims_false():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["candidateScannerProofClaim"] is False
    assert summary["leanProofClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())
    for packet in payload["candidatePackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_fef_p20_writes_outputs(tmp_path):
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
    assert len(packets) == len(P17_CASES)
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P20")


def test_fef_p20_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p20_lean_proof_candidate_scanner.py",
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
    assert "FEF_P20_LEAN_PROOF_CANDIDATE_SCANNER_OK" in proc.stdout
