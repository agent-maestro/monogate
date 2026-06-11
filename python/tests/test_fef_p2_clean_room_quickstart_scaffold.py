"""Tests for FEF-P2 clean-room quickstart scaffold."""

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

from scripts.fef_p2_clean_room_quickstart_scaffold import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p2_records_scaffold_and_cleanroom_pass():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "FEF_P2_CLEAN_ROOM_QUICKSTART_SCAFFOLD_PASS"
    assert payload["summary"]["packageScaffoldCreated"] is True
    assert payload["summary"]["cleanRoomQuickstartPassed"] is True
    assert payload["summary"]["packagePublished"] is False
    assert payload["summary"]["publicReady"] is False


def test_fef_p2_cleanroom_executes_both_targets():
    payload = build_payload()
    assert payload["summary"]["pythonTargetExecuted"] is True
    assert payload["summary"]["javascriptTargetExecuted"] is True
    assert payload["summary"]["sampleCount"] == 6
    assert payload["summary"]["maxAbsError"] <= 1e-12


def test_fef_p2_release_gates_are_bounded():
    payload = build_payload()
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["package_scaffold_created"] == "pass"
    assert gates["clean_room_quickstart_passed"] == "pass"
    assert gates["python_target_execution_passed"] == "pass"
    assert gates["javascript_target_execution_passed"] == "pass"
    assert gates["public_copy_review_passed"] == "pending"
    assert gates["package_published"] == "blocked"


def test_fef_p2_claim_flags_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_payload()
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p2_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P2")


def test_fef_p2_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p2_clean_room_quickstart_scaffold.py",
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
    assert "FEF_P2_CLEAN_ROOM_QUICKSTART_SCAFFOLD_OK" in proc.stdout
