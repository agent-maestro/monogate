"""Tests for EML Advantage focused sprint closure."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_advantage_product_sprint_closure import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_sprint_closure_records_all_three_lanes():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EML_ADVANTAGE_PRODUCT_SPRINT_CLOSURE_PASS"
    assert {sprint["sprintId"] for sprint in payload["sprints"]} == {
        "forge_efrog_packet_export_ux",
        "mge_glassbox_evidence_mount",
        "machlib_small_witness_selection",
    }
    assert payload["summary"]["sprintCount"] == 3


def test_forge_efrog_export_contract_has_required_fields():
    payload = build_payload()
    sprint = payload["sprints"][0]
    assert sprint["status"] == "handoff_ready"
    assert sprint["result"] == "packet_export_contract_defined"
    for field in ["source_path", "eml_surface_summary", "forge_target", "blocked_claims"]:
        assert field in sprint["exportFields"]


def test_engine_handoff_records_worktree_constraint_without_behavior_change():
    payload = build_payload()
    sprint = payload["sprints"][1]
    assert sprint["status"] == "handoff_ready"
    assert "unrelated uncommitted work" in sprint["worktreeConstraint"]
    assert payload["claimFlags"]["engine_behavior_changed"] is False
    assert payload["summary"]["behaviorChangeCount"] == 0


def test_machlib_existing_witness_is_referenced_not_duplicated():
    payload = build_payload()
    sprint = payload["sprints"][2]
    assert sprint["status"] == "existing_witness_recorded"
    assert sprint["result"] == "subtraction_boundary_already_checked"
    names = {witness["name"] for witness in sprint["witnesses"]}
    assert "atlas_subtraction_boundary_witness" in names
    assert "eml_log_exp_subtraction_boundary" in names
    assert payload["claimFlags"]["machlib_source_changed"] is False
    assert payload["claimFlags"]["new_proof_claim"] is False


def test_sprint_closure_claim_flags_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_payload()
    assert all(value is False for value in payload["claimFlags"].values())
    assert payload["summary"]["publicReady"] is False
    assert payload["summary"]["deploymentPerformed"] is False


def test_sprint_closure_writes_json_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML Advantage Focused Sprint Closure")


def test_sprint_closure_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_advantage_product_sprint_closure.py",
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
    assert "EML_ADVANTAGE_PRODUCT_SPRINT_CLOSURE_OK" in proc.stdout
