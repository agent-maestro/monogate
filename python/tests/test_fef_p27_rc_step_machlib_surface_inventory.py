"""Tests for FEF-P27 rc_step_response_at_zero MachLib surface inventory."""

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

from scripts.fef_p27_rc_step_machlib_surface_inventory import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p27_records_surface_inventory():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P27_RC_STEP_MACHLIB_SURFACE_INVENTORY_PASS"
    assert summary["surfaceItemCount"] == 8
    assert summary["zeroDivisionLemmaMissing"] is True
    assert summary["subSelfRequiresRingImport"] is True
    assert summary["rcStepResponseProofSurfaceComplete"] is False


def test_fef_p27_generated_surface_availability():
    payload = build_payload()
    rows = {row["identifier"]: row for row in payload["surfaceItems"]}
    assert rows["exp_zero"]["generatedImportSurface"]["available"] is True
    assert rows["mul_zero"]["generatedImportSurface"]["available"] is True
    assert rows["zero_mul"]["generatedImportSurface"]["available"] is True
    assert rows["sub_def"]["generatedImportSurface"]["available"] is True
    assert rows["add_neg"]["generatedImportSurface"]["available"] is True
    assert rows["sub_self"]["generatedImportSurface"]["available"] is False
    assert rows["zero_div"]["generatedImportSurface"]["available"] is False
    assert rows["div_zero"]["generatedImportSurface"]["available"] is False


def test_fef_p27_ring_surface_delta():
    payload = build_payload()
    rows = {row["identifier"]: row for row in payload["surfaceItems"]}
    assert rows["sub_self"]["ringImportSurface"]["available"] is True
    assert rows["zero_div"]["ringImportSurface"]["available"] is False
    assert rows["div_zero"]["ringImportSurface"]["available"] is False


def test_fef_p27_keeps_broad_claims_false():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["machlibSurfaceInventoryClaim"] is False
    assert summary["newMachlibLemmaClaim"] is False
    assert summary["rcStepResponseProvedClaim"] is False
    assert summary["leanProofClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p27_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P27")


def test_fef_p27_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p27_rc_step_machlib_surface_inventory.py",
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
    assert "FEF_P27_RC_STEP_MACHLIB_SURFACE_INVENTORY_OK" in proc.stdout
