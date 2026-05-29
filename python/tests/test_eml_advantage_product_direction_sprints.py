"""Tests for EML Advantage product-direction sprints."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_advantage_product_direction_sprints import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_product_direction_has_three_ordered_sprints():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EML_ADVANTAGE_PRODUCT_DIRECTION_SPRINTS_PASS"
    assert payload["summary"]["sprintCount"] == 3
    assert payload["recommendedOrder"] == [
        "forge_efrog_packet_export_ux",
        "mge_glassbox_evidence_mount",
        "machlib_small_witness_selection",
    ]


def test_forge_efrog_is_first_and_product_facing():
    payload = build_payload()
    first = payload["sprints"][0]
    assert first["sprintId"] == "forge_efrog_packet_export_ux"
    assert first["lane"] == "compiler_decompiler"
    assert first["readyToStart"] is True
    assert "private packet export spec" in first["deliverables"]
    assert "compiler correctness" in first["blockedClaims"]


def test_engine_sprint_records_dirty_worktree_constraint():
    payload = build_payload()
    engine = payload["sprints"][1]
    assert engine["sprintId"] == "mge_glassbox_evidence_mount"
    assert payload["summary"]["engineWorktreeConstraintRecorded"] is True
    assert "dirty engine worktree" in engine["whySecond"]
    assert "production runtime" in engine["blockedClaims"]


def test_machlib_sprint_selects_subtraction_boundary_without_proof_claim():
    payload = build_payload()
    machlib = payload["sprints"][2]
    assert machlib["sprintId"] == "machlib_small_witness_selection"
    assert machlib["recommendedCandidate"]["name"] == "subtraction_boundary"
    assert "v > 0" in machlib["recommendedCandidate"]["statement"]
    assert payload["claimFlags"]["proof_claim"] is False
    assert payload["claimFlags"]["machlib_theorem_discharged"] is False


def test_product_direction_claim_flags_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_payload()
    assert all(value is False for value in payload["claimFlags"].values())
    assert payload["summary"]["publicReady"] is False
    assert payload["summary"]["deploymentPerformed"] is False


def test_product_direction_writes_json_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML Advantage Product Direction")


def test_product_direction_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_advantage_product_direction_sprints.py",
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
    assert "EML_ADVANTAGE_PRODUCT_DIRECTION_SPRINTS_OK" in proc.stdout
