"""Tests for EML-D8 discovery branch decision."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d8_discovery_branch_decision import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def branch_by_id(payload, branch_id: str):
    return next(item for item in payload["branchOptions"] if item["branchId"] == branch_id)


def test_d8_selects_machlib_identity_lane_after_d7():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EML_D8_DISCOVERY_BRANCH_DECISION_PASS"
    assert payload["sourceInterpretationGate"] == "eml-d7-symbolic-search-interpretation-gate"
    assert payload["summary"]["sourceInterpretationLabel"] == "no_replicated_holdout_gain"
    assert payload["summary"]["selectedBranchId"] == "machlib_identity_witness_lane_v0"
    assert payload["selectedBranch"]["decision"] == "selected_next"


def test_d8_parks_deeper_psi_search():
    payload = build_payload()
    assert payload["summary"]["psiSearchParked"] is True
    assert payload["summary"]["deeperPsiSearchAllowed"] is False
    branch = branch_by_id(payload, "park_psi_residual_search_v0")
    assert branch["decision"] == "park_as_ambiguous_until_new_hypothesis"


def test_d8_records_four_branch_options():
    payload = build_payload()
    assert payload["summary"]["branchOptionCount"] == 4
    assert branch_by_id(payload, "machlib_identity_witness_lane_v0")
    assert branch_by_id(payload, "fresh_non_psi_holdout_family_v0")
    assert branch_by_id(payload, "broaden_negative_controls_v0")


def test_d8_selected_branch_points_to_d9_selector():
    payload = build_payload()
    assert payload["summary"]["selectedNextArtifact"] == "EML-D9 MachLib identity witness selector"
    assert payload["selectedBranch"]["priorityScore"] > branch_by_id(payload, "fresh_non_psi_holdout_family_v0")["priorityScore"]


def test_d8_claim_flags_remain_false():
    payload = build_payload()
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["emlAdvantageProved"] is False
    assert payload["summary"]["publicReady"] is False
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())
    for branch in payload["branchOptions"]:
        assert all(value is False for value in branch["claimFlags"].values())


def test_d8_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D8")


def test_d8_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d8_discovery_branch_decision.py",
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
    assert "EML_D8_DISCOVERY_BRANCH_DECISION_OK" in proc.stdout
