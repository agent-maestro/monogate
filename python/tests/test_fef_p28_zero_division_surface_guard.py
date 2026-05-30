"""Tests for FEF-P28 zero-division MachLib proof-surface guard."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p28_zero_division_surface_guard import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p28_records_zero_division_surface_guard():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P28_ZERO_DIVISION_SURFACE_GUARD_PASS"
    assert payload["decision"] == "zero_division_surface_guard_closed"
    assert summary["helperIdentifierCount"] == 2
    assert summary["helperIdentifierAvailableCount"] == 2


def test_fef_p28_helpers_available_under_generated_imports():
    payload = build_payload()
    rows = {row["identifier"]: row for row in payload["helperIdentifiers"]}
    assert rows["zero_div_of_ne_zero"]["available"] is True
    assert rows["zero_div_of_pos"]["available"] is True
    assert rows["zero_div_of_ne_zero"]["status"] == "lean_check_pass"
    assert rows["zero_div_of_pos"]["status"] == "lean_check_pass"


def test_fef_p28_zero_time_probe_typechecks_without_broad_claims():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["rcStepZeroDivisionSurfaceProbePass"] is True
    assert summary["newMachlibAxiomClaim"] is False
    assert summary["rcStepResponseProvedClaim"] is False
    assert summary["leanProofClaim"] is False
    assert summary["allGeneratedLeanFilesProvedClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p28_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P28")


def test_fef_p28_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p28_zero_division_surface_guard.py",
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
    assert "FEF_P28_ZERO_DIVISION_SURFACE_GUARD_OK" in proc.stdout
