"""Tests for EML-D9 MachLib identity witness selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d9_machlib_identity_witness_selector import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def selector_by_id(payload, candidate_id: str):
    return next(item for item in payload["candidateSelectors"] if item["candidateId"] == candidate_id)


def test_d9_consumes_d8_machlib_identity_branch():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EML_D9_MACHLIB_IDENTITY_WITNESS_SELECTOR_PASS"
    assert payload["sourceBranchDecision"] == "eml-d8-discovery-branch-decision"
    assert payload["summary"]["sourceSelectedBranchId"] == "machlib_identity_witness_lane_v0"


def test_d9_selects_constants_witness_target():
    payload = build_payload()
    assert payload["summary"]["selectedCandidateId"] == "constants_zero_one_e_boundary_v0"
    assert payload["summary"]["selectedProofTarget"] == "MachLib.Real.constants_zero_one_e_boundary_witness"
    assert payload["selectedCandidate"]["selectionStatus"] == "selected_next"
    assert payload["summary"]["selectedNextArtifact"] == "EML-D10 constants zero/one/e MachLib witness attempt"


def test_d9_records_three_candidate_selectors():
    payload = build_payload()
    assert payload["summary"]["candidateCount"] == 3
    assert selector_by_id(payload, "constants_zero_one_e_boundary_v0")
    assert selector_by_id(payload, "subtraction_boundary_family_v1")
    assert selector_by_id(payload, "ln_from_eml_boundary_v1")


def test_d9_does_not_reselect_already_checked_subtraction_boundary():
    payload = build_payload()
    subtraction = selector_by_id(payload, "subtraction_boundary_family_v1")
    assert subtraction["selectionStatus"] == "already_checked_not_next"
    assert subtraction["existingWitness"] == "MachLib.Real.atlas_subtraction_boundary_witness"
    assert payload["summary"]["alreadyCheckedCandidateCount"] == 1


def test_d9_keeps_ln_from_eml_as_later_nested_target():
    payload = build_payload()
    ln_target = selector_by_id(payload, "ln_from_eml_boundary_v1")
    assert ln_target["selectionStatus"] == "candidate_later"
    assert ln_target["estimatedDifficulty"] == "medium_nested_rewrite"


def test_d9_claim_flags_remain_false():
    payload = build_payload()
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["publicReady"] is False
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())
    for selector in payload["candidateSelectors"]:
        assert all(value is False for value in selector["claimFlags"].values())


def test_d9_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D9")


def test_d9_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d9_machlib_identity_witness_selector.py",
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
    assert "EML_D9_MACHLIB_IDENTITY_WITNESS_SELECTOR_OK" in proc.stdout
