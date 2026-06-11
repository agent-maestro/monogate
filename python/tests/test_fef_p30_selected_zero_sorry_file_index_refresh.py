"""Tests for FEF-P30 selected zero-sorry file index refresh."""

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

from scripts.fef_p30_selected_zero_sorry_file_index_refresh import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p30_indexes_refreshed_selected_zero_sorry_files():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P30_SELECTED_ZERO_SORRY_FILE_INDEX_REFRESH_PASS"
    assert summary["indexedSelectedFileCount"] == 4
    assert summary["selectedZeroSorryFileCount"] == 4
    assert summary["selectedZeroSorryFiles"] == ["verified_add", "voltage_divider", "mosfet_iv", "rc_filter"]
    assert summary["selectedRemainingSorryFiles"] == []
    assert summary["remainingPlaceholderTheoremCount"] == 0


def test_fef_p30_includes_rc_filter_after_p29():
    payload = build_payload()
    rows = {row["selectedFile"]: row for row in payload["indexedFiles"]}
    assert rows["rc_filter"]["artifactId"] == "fef-p29-rc-filter-full-lean-proof-discharge"
    assert rows["rc_filter"]["status"] == "selected_file_zero_sorry"
    assert rows["rc_filter"]["remainingPlaceholderTheoremCount"] == 0
    assert payload["summary"]["rcFilterIncludedAsZeroSorry"] is True
    assert payload["summary"]["rcStepResponseAtZeroStillBlocked"] is False


def test_fef_p30_keeps_broad_claims_false():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["zeroSorryIndexRefreshClaim"] is False
    assert summary["leanProofClaim"] is False
    assert summary["allGeneratedLeanFilesProvedClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p30_release_gates_keep_remaining_work_blocked():
    payload = build_payload()
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_zero_sorry_files_indexed"] == "pass"
    assert gates["rc_filter_included_as_zero_sorry"] == "pass"
    assert gates["all_generated_lean_files_zero_sorry"] == "blocked"
    assert gates["machlib_foundational_audit"] == "blocked"


def test_fef_p30_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P30")


def test_fef_p30_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p30_selected_zero_sorry_file_index_refresh.py",
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
    assert "FEF_P30_SELECTED_ZERO_SORRY_FILE_INDEX_REFRESH_OK" in proc.stdout
