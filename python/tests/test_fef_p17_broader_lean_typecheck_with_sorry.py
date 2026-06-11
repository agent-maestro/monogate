"""Tests for FEF-P17 Broader Lean typecheck-with-sorry validator."""

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

from scripts.fef_p17_broader_lean_typecheck_with_sorry import (
    CASES,
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p17_records_configured_import_path():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "FEF_P17_BROADER_LEAN_TYPECHECK_WITH_SORRY_PASS"
    assert payload["summary"]["caseCount"] == len(CASES)
    assert payload["summary"]["caseCount"] == 8
    assert payload["summary"]["machlibBuildLibExists"] is True
    assert payload["summary"]["machlibImportResolvedCount"] == len(CASES)


def test_fef_p17_broadens_selected_typecheck_with_sorry_family():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["typecheckWithSorryPassCount"] == len(CASES)
    assert summary["typecheckBlockedCount"] == 0
    assert "blocked_generated_name_ambiguity" not in summary["typecheckWithSorryStatuses"]
    assert summary["typecheckWithSorryStatuses"] == ["typecheck_with_sorry_pass"]
    assert summary["declaredTheoremCount"] == 15
    assert summary["sorryCount"] == 15


def test_fef_p17_keeps_proof_and_correctness_claims_false():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["leanImportResolutionClaim"] is False
    assert summary["leanTypecheckWithSorryClaim"] is False
    assert summary["leanProofClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["machlib_build_lib_found"] == "pass"
    assert gates["selected_lean_import_resolution"] == "pass"
    assert gates["selected_broader_lean_typecheck"] == "pass"
    assert gates["all_selected_lean_typecheck_with_sorry"] == "pass"
    assert gates["lean_proofs_discharged"] == "blocked"


def test_fef_p17_claim_flags_remain_false():
    payload = build_payload()
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in payload["claimFlags"].values())
    for packet in payload["broaderTypecheckPackets"]:
        assert packet["missingTheorems"] == []
        assert all(value is False for value in packet["claimFlags"].values())


def test_fef_p17_writes_outputs(tmp_path):
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
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P17")


def test_fef_p17_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p17_broader_lean_typecheck_with_sorry.py",
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
    assert "FEF_P17_BROADER_LEAN_TYPECHECK_WITH_SORRY_OK" in proc.stdout
