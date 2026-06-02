"""Tests for EML-D37 research lane reset selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d37_research_lane_reset_selector import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def option_by_id(payload, option_id: str):
    return next(item for item in payload["laneOptions"] if item["optionId"] == option_id)


def test_d37_consumes_d36_skeleton():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D37_RESEARCH_LANE_RESET_SELECTOR_PASS"
    assert payload["sourceSkeletonPacket"] == "eml-d36-course2-private-lesson-packet-skeleton"
    assert payload["summary"]["lessonPacketSkeletonStarted"] is True
    assert payload["summary"]["privateSkeletonOnly"] is True


def test_d37_parks_research_side_course_drafting():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["researchLaneResetSelected"] is True
    assert payload["summary"]["courseDraftingParkedResearchSide"] is True
    assert payload["summary"]["courseOwner"] == "user_and_laptop_agent"
    assert payload["summary"]["courseDraftPacketStarted"] is False
    assert payload["summary"]["lessonContentGenerated"] is False


def test_d37_selects_bounded_eml_identity_branch_selector():
    payload = build_payload(ATLAS_GATE)
    assert payload["decision"] == "select_bounded_eml_identity_branch_selector"
    assert payload["summary"]["selectedOptionId"] == "bounded_eml_identity_branch_selector"
    assert payload["summary"]["selectedNextArtifact"] == "EML-D38 bounded EML identity branch selector"
    selected = option_by_id(payload, "bounded_eml_identity_branch_selector")
    assert selected["selectionStatus"] == "selected_next"
    assert selected["lane"] == "eml_research_lane"
    assert payload["summary"]["boundedIdentitySelectorSelected"] is True


def test_d37_parks_other_lanes():
    payload = build_payload(ATLAS_GATE)
    tooling = option_by_id(payload, "monogate_evidence_pipeline_hardening")
    course_intake = option_by_id(payload, "course_artifact_reviewer_intake")
    assert tooling["selectionStatus"] == "candidate_later"
    assert course_intake["selectionStatus"] == "parked_until_laptop_artifact"
    assert payload["summary"]["optionCount"] == 3


def test_d37_starts_no_public_or_course_work():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["coursePublicationStarted"] is False
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["humanApprovalRecorded"] is False
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["publicReady"] is False


def test_d37_touches_no_laptop_repo_or_proof_work():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False


def test_d37_keeps_runtime_and_broad_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "standard_subtraction_remains_runtime_control"
    assert payload["summary"]["broadNestedSubtractionClaim"] is False
    assert payload["summary"]["broadSubtractionFamilyClaim"] is False
    assert payload["summary"]["arbitraryDepthClaim"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False


def test_d37_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsAllBounded"] is True
    for key in [
        "research_lane_reset_selected",
        "course_drafting_parked_research_side",
        "bounded_identity_selector_selected",
    ]:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in {
            "research_lane_reset_selected",
            "course_drafting_parked_research_side",
            "bounded_identity_selector_selected",
        }:
            assert value is False


def test_d37_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D37")


def test_d37_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d37_research_lane_reset_selector.py",
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
    assert "EML_D37_RESEARCH_LANE_RESET_SELECTOR_OK" in proc.stdout
