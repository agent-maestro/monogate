"""Tests for FEF-P26 rc_step_response_at_zero proof-blocker analysis."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p26_rc_step_response_proof_blocker_analysis import (
    CLAIM_FLAGS,
    TARGET_THEOREM,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p26_records_rc_step_response_blocker():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P26_RC_STEP_RESPONSE_PROOF_BLOCKER_ANALYSIS_PASS"
    assert summary["targetTheorem"] == TARGET_THEOREM
    assert summary["attemptCount"] == 3
    assert summary["passingCandidateCount"] == 0
    assert summary["blockedCandidateCount"] == 3
    assert summary["blockerStatus"] == "blocked_no_candidate_passed"


def test_fef_p26_attempts_are_all_blocked_and_no_sorry_free_claim():
    payload = build_payload()
    packet = payload["blockerPackets"][0]
    assert packet["targetTheorem"] == "rc_step_response_at_zero"
    assert packet["generatedFileSorryCount"] == 5
    assert packet["passingCandidateCount"] == 0
    assert all(attempt["leanCheck"]["status"] == "candidate_typecheck_fail" for attempt in packet["attempts"])
    assert any("exp" in item for item in packet["neededProofSurface"])


def test_fef_p26_keeps_broad_claims_false():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["rcStepResponseProvedClaim"] is False
    assert summary["proofBlockerAnalysisClaim"] is False
    assert summary["leanProofClaim"] is False
    assert summary["allGeneratedLeanFilesProvedClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p26_release_gates_keep_target_blocked():
    payload = build_payload()
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["target_blocker_analyzed"] == "pass"
    assert gates["rc_step_response_candidate_found"] == "blocked"
    assert gates["selected_zero_sorry_files_unchanged"] == "pass"
    assert gates["all_generated_lean_files_zero_sorry"] == "blocked"


def test_fef_p26_writes_outputs(tmp_path):
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
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P26")


def test_fef_p26_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p26_rc_step_response_proof_blocker_analysis.py",
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
    assert "FEF_P26_RC_STEP_RESPONSE_PROOF_BLOCKER_ANALYSIS_OK" in proc.stdout
