"""Tests for EML-D38 bounded identity branch selector."""

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

from scripts.eml_d38_bounded_identity_branch_selector import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def candidate_by_id(payload, candidate_id: str):
    return next(item for item in payload["branchCandidates"] if item["candidateId"] == candidate_id)


def test_d38_consumes_d37_reset_selector():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D38_BOUNDED_IDENTITY_BRANCH_SELECTOR_PASS"
    assert payload["sourceResetSelector"] == "eml-d37-research-lane-reset-selector"
    assert payload["summary"]["researchLaneResetSelected"] is True
    assert payload["summary"]["courseDraftingParkedResearchSide"] is True
    assert payload["summary"]["sourceSelectedOptionId"] == "bounded_eml_identity_branch_selector"


def test_d38_selects_positive_log_exp_roundtrip():
    payload = build_payload(ATLAS_GATE)
    assert payload["decision"] == "select_positive_log_exp_roundtrip_identity"
    assert payload["summary"]["selectedCandidateId"] == "positive_log_exp_roundtrip_identity"
    assert payload["summary"]["selectedFamily"] == "positive_domain_log_exp_roundtrip"
    assert payload["summary"]["selectedNextArtifact"] == "EML-D39 positive log-exp roundtrip witness feasibility packet"
    selected = candidate_by_id(payload, "positive_log_exp_roundtrip_identity")
    assert selected["selectionStatus"] == "selected_next"
    assert selected["guardShape"] == ["0 < x"]
    assert selected["emlShape"] == "exp (log x)"
    assert selected["standardShape"] == "x"


def test_d38_records_three_candidates_and_parks_later_options():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["candidateCount"] == 3
    assert candidate_by_id(payload, "eml_constant_coordinate_refresh")["selectionStatus"] == "candidate_later"
    assert candidate_by_id(payload, "bounded_trig_eml_probe_selector")["selectionStatus"] == "candidate_later"


def test_d38_keeps_course_work_parked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["courseDraftingParkedResearchSide"] is True
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False


def test_d38_starts_no_implementation_or_proof_work():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["proofAttemptStarted"] is False


def test_d38_keeps_runtime_and_broad_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "standard_subtraction_remains_runtime_control"
    assert payload["summary"]["broadNestedSubtractionClaim"] is False
    assert payload["summary"]["broadSubtractionFamilyClaim"] is False
    assert payload["summary"]["arbitraryDepthClaim"] is False
    assert payload["summary"]["publicReady"] is False


def test_d38_keeps_public_surfaces_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False


def test_d38_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsAllBounded"] is True
    assert CLAIM_FLAGS["bounded_identity_branch_selected"] is True
    assert payload["claimFlags"]["bounded_identity_branch_selected"] is True
    for key, value in payload["claimFlags"].items():
        if key != "bounded_identity_branch_selected":
            assert value is False
    for candidate in payload["branchCandidates"]:
        assert candidate["claimFlags"]["bounded_identity_branch_selected"] is True
        for key, value in candidate["claimFlags"].items():
            if key != "bounded_identity_branch_selected":
                assert value is False


def test_d38_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D38")


def test_d38_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d38_bounded_identity_branch_selector.py",
            "--build",
            "--atlas-gate-path",
            str(ATLAS_GATE),
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
    assert "EML_D38_BOUNDED_IDENTITY_BRANCH_SELECTOR_OK" in proc.stdout
