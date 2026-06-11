"""Tests for EML-D35 Course 2 lesson-outline claim boundary."""

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

from scripts.eml_d35_course2_lesson_outline_claim_boundary import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def rule_by_id(payload, rule_id: str):
    return next(item for item in payload["claimBoundaryRules"] if item["ruleId"] == rule_id)


def action_by_id(payload, action_id: str):
    return next(item for item in payload["nextActions"] if item["actionId"] == action_id)


def module_by_id(payload, module_id: str):
    return next(item for item in payload["outlineModules"] if item["moduleId"] == module_id)


def test_d35_consumes_d34_reference_packet():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D35_COURSE2_LESSON_OUTLINE_CLAIM_BOUNDARY_PASS"
    assert payload["sourceReferencePacket"] == "eml-d34-course2-private-reference-packet"
    assert payload["summary"]["courseReferencePacketStarted"] is True
    assert payload["summary"]["privateCourseReferenceOnly"] is True


def test_d35_starts_private_outline_boundary():
    payload = build_payload(ATLAS_GATE)
    assert payload["decision"] == "course2_private_lesson_outline_claim_boundary_started"
    assert payload["summary"]["courseOutlineStarted"] is True
    assert payload["summary"]["privateOutlineOnly"] is True
    assert CLAIM_FLAGS["course_outline_started"] is True
    assert CLAIM_FLAGS["private_outline_only"] is True


def test_d35_records_four_outline_modules():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["outlineModuleCount"] == 4
    assert module_by_id(payload, "course2_orientation_claim_boundary")["moduleOrder"] == 1
    assert module_by_id(payload, "course2_single_stage_subtraction_boundary")["moduleOrder"] == 2
    assert module_by_id(payload, "course2_nested_chain_boundary")["moduleOrder"] == 3
    assert module_by_id(payload, "course2_runtime_and_public_copy_hold")["moduleOrder"] == 4


def test_d35_references_exactly_frozen_witness_index():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["courseReferenceRowCount"] == 6
    assert payload["summary"]["referencedFrozenWitnessCount"] == 6
    assert payload["summary"]["allModuleReferencesFrozen"] is True
    nested = module_by_id(payload, "course2_nested_chain_boundary")
    assert "subtraction_boundary_two_stage_chain" in nested["referenceWitnessIds"]
    assert "subtraction_boundary_affine_nested_chain" in nested["referenceWitnessIds"]
    assert "subtraction_boundary_three_stage_chain" in nested["referenceWitnessIds"]


def test_d35_preserves_d30_caveats_and_blockers():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["d30RequiredCaveatCount"] == 5
    assert payload["summary"]["d30BlockedGlobalPhraseCount"] == 8
    assert len(payload["preservedRequiredCaveats"]) == 5
    assert len(payload["preservedBlockedGlobalPhrases"]) == 8
    assert "theorem discovery" in payload["preservedBlockedGlobalPhrases"]
    assert "broad nested subtraction family" in payload["preservedBlockedGlobalPhrases"]


def test_d35_records_claim_boundary_rules_and_next_actions():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimBoundaryRuleCount"] == 5
    assert payload["summary"]["nextActionCount"] == 3
    assert rule_by_id(payload, "private_outline_only")["ruleStatus"] == "required"
    assert rule_by_id(payload, "no_laptop_repo_touch")["ruleStatus"] == "required"
    assert action_by_id(payload, "course2_private_lesson_packet_skeleton")["availability"] == "available_next_private_packet"
    assert action_by_id(payload, "human_approved_public_copy_gate")["availability"] == "parked_requires_explicit_human_approval"


def test_d35_does_not_generate_lesson_or_publish_course():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["lessonPacketGenerated"] is False
    assert payload["summary"]["coursePublicationStarted"] is False
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["humanApprovalRecorded"] is False
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["publicReady"] is False


def test_d35_touches_no_laptop_repo_or_proof_work():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False


def test_d35_keeps_runtime_and_broad_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "standard_subtraction_remains_runtime_control"
    assert payload["summary"]["broadNestedSubtractionClaim"] is False
    assert payload["summary"]["broadSubtractionFamilyClaim"] is False
    assert payload["summary"]["arbitraryDepthClaim"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False


def test_d35_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsAllBounded"] is True
    assert payload["claimFlags"]["course_outline_started"] is True
    assert payload["claimFlags"]["private_outline_only"] is True
    for key, value in payload["claimFlags"].items():
        if key not in {"course_outline_started", "private_outline_only"}:
            assert value is False


def test_d35_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D35")


def test_d35_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d35_course2_lesson_outline_claim_boundary.py",
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
    assert "EML_D35_COURSE2_LESSON_OUTLINE_CLAIM_BOUNDARY_OK" in proc.stdout
