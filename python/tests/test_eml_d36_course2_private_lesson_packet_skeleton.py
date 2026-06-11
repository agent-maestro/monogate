"""Tests for EML-D36 Course 2 private lesson packet skeleton."""

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

from scripts.eml_d36_course2_private_lesson_packet_skeleton import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def gate_by_id(payload, gate_id: str):
    return next(item for item in payload["readinessGates"] if item["gateId"] == gate_id)


def action_by_id(payload, action_id: str):
    return next(item for item in payload["nextActions"] if item["actionId"] == action_id)


def module_by_id(payload, module_id: str):
    return next(item for item in payload["skeletonModules"] if item["moduleId"] == module_id)


def test_d36_consumes_d35_outline_packet():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D36_COURSE2_PRIVATE_LESSON_PACKET_SKELETON_PASS"
    assert payload["sourceOutlinePacket"] == "eml-d35-course2-lesson-outline-claim-boundary"
    assert payload["summary"]["courseOutlineStarted"] is True
    assert payload["summary"]["privateOutlineOnly"] is True


def test_d36_starts_private_skeleton_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["decision"] == "course2_private_lesson_packet_skeleton_started"
    assert payload["summary"]["lessonPacketSkeletonStarted"] is True
    assert payload["summary"]["privateSkeletonOnly"] is True
    assert CLAIM_FLAGS["lesson_packet_skeleton_started"] is True
    assert CLAIM_FLAGS["private_skeleton_only"] is True


def test_d36_records_four_skeleton_modules_and_slots():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["skeletonModuleCount"] == 4
    assert payload["summary"]["skeletonSlotKindCount"] == 4
    assert payload["summary"]["totalSkeletonSlotCount"] == 16
    assert module_by_id(payload, "course2_orientation_claim_boundary")["slotCount"] == 4
    assert module_by_id(payload, "course2_nested_chain_boundary")["slotCount"] == 4


def test_d36_references_exactly_frozen_witness_set():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["referencedFrozenWitnessCount"] == 6
    assert payload["summary"]["allSkeletonReferencesFrozen"] is True
    nested = module_by_id(payload, "course2_nested_chain_boundary")
    assert "subtraction_boundary_two_stage_chain" in nested["referenceWitnessIds"]
    assert "subtraction_boundary_affine_nested_chain" in nested["referenceWitnessIds"]
    assert "subtraction_boundary_three_stage_chain" in nested["referenceWitnessIds"]


def test_d36_preserves_d30_caveats_and_blockers():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["d30RequiredCaveatCount"] == 5
    assert payload["summary"]["d30BlockedGlobalPhraseCount"] == 8
    assert len(payload["preservedRequiredCaveats"]) == 5
    assert len(payload["preservedBlockedGlobalPhrases"]) == 8
    assert "theorem discovery" in payload["preservedBlockedGlobalPhrases"]
    assert "broad nested subtraction family" in payload["preservedBlockedGlobalPhrases"]


def test_d36_records_readiness_gates_and_next_actions():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["readinessGateCount"] == 5
    assert payload["summary"]["nextActionCount"] == 3
    assert gate_by_id(payload, "private_skeleton_only")["gateStatus"] == "closed_to_public"
    assert gate_by_id(payload, "no_laptop_artifact_inference")["gateStatus"] == "required"
    assert action_by_id(payload, "course2_private_lesson_draft_packet")["availability"] == "available_next_private_packet"
    assert action_by_id(payload, "human_approved_public_copy_gate")["availability"] == "parked_requires_explicit_human_approval"


def test_d36_does_not_generate_lesson_content_or_publish():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["lessonContentGenerated"] is False
    assert payload["summary"]["coursePublicationStarted"] is False
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["humanApprovalRecorded"] is False
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["publicReady"] is False
    assert all(module["lessonContentGenerated"] is False for module in payload["skeletonModules"])


def test_d36_touches_no_laptop_repo_or_proof_work():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False


def test_d36_keeps_runtime_and_broad_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "standard_subtraction_remains_runtime_control"
    assert payload["summary"]["broadNestedSubtractionClaim"] is False
    assert payload["summary"]["broadSubtractionFamilyClaim"] is False
    assert payload["summary"]["arbitraryDepthClaim"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False


def test_d36_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsAllBounded"] is True
    assert payload["claimFlags"]["lesson_packet_skeleton_started"] is True
    assert payload["claimFlags"]["private_skeleton_only"] is True
    for key, value in payload["claimFlags"].items():
        if key not in {"lesson_packet_skeleton_started", "private_skeleton_only"}:
            assert value is False
    assert all(module["publicPromotionAllowed"] is False for module in payload["skeletonModules"])


def test_d36_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D36")


def test_d36_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d36_course2_private_lesson_packet_skeleton.py",
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
    assert "EML_D36_COURSE2_PRIVATE_LESSON_PACKET_SKELETON_OK" in proc.stdout
