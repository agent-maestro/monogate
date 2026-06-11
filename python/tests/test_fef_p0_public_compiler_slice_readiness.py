"""Tests for FEF-P0 public compiler slice readiness."""

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

from scripts.fef_p0_public_compiler_slice_readiness import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p0_records_private_slice_but_blocks_public_readiness():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "FEF_P0_PUBLIC_COMPILER_SLICE_READINESS_RECORDED"
    assert payload["decision"] == "not_public_ready_yet"
    assert payload["summary"]["privateCompilerSlicePresent"] is True
    assert payload["summary"]["publicReady"] is False
    assert payload["summary"]["safeToPublishPublicly"] is False
    assert payload["summary"]["publicCompilerPackageAvailable"] is False


def test_fef_p0_preserves_selected_slice_counts():
    payload = build_payload()
    slice_info = payload["minimumCompilerSlice"]
    assert slice_info["targetScope"] == ["python", "javascript"]
    assert slice_info["roundtripCases"] >= 32
    assert slice_info["roundtripPasses"] == slice_info["roundtripCases"]
    assert slice_info["semanticCases"] == 8
    assert slice_info["semanticPasses"] == 8
    assert slice_info["exportPacketCount"] == 8
    assert slice_info["policyCount"] == 7


def test_fef_p0_public_gates_keep_checkout_and_package_blocked():
    payload = build_payload()
    gates = {gate["id"]: gate["status"] for gate in payload["publicReleaseGates"]}
    assert gates["internal_selected_slice_exists"] == "pass"
    assert gates["public_claim_copy_is_aligned"] == "pass"
    assert gates["public_install_path_exists"] == "fail"
    assert gates["clean_room_quickstart_exists"] == "fail"
    assert gates["target_runtime_execution_guard_exists"] == "partial"
    assert payload["summary"]["failGateCount"] == 2
    blocker_ids = {blocker["id"] for blocker in payload["publicBlockers"]}
    assert "public_compiler_package_missing" in blocker_ids
    assert "clean_room_quickstart_missing" in blocker_ids
    assert "javascript_runtime_execution_missing" in blocker_ids


def test_fef_p0_claim_flags_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_payload()
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p0_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P0")


def test_fef_p0_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p0_public_compiler_slice_readiness.py",
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
    assert "FEF_P0_PUBLIC_COMPILER_SLICE_READINESS_OK" in proc.stdout
