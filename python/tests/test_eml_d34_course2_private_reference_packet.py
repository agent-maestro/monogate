"""Tests for EML-D34 Course 2 private reference packet."""

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

from scripts.eml_d34_course2_private_reference_packet import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def guard_by_id(payload, guard_id: str):
    return next(item for item in payload["course2ReferenceGuards"] if item["guardId"] == guard_id)


def action_by_id(payload, action_id: str):
    return next(item for item in payload["nextCourse2Actions"] if item["actionId"] == action_id)


def test_d34_consumes_d33_and_d32():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D34_COURSE2_PRIVATE_REFERENCE_PACKET_PASS"
    assert payload["sourceSelector"] == "eml-d33-post-freeze-next-selector"
    assert payload["sourceFreezePacket"] == "eml-d32-subtraction-family-pause-freeze-packet"
    assert payload["summary"]["selectedOptionId"] == "course_scaling_private_reference"


def test_d34_starts_private_course_reference_packet():
    payload = build_payload(ATLAS_GATE)
    assert payload["decision"] == "course2_private_checked_witness_reference_packet_started"
    assert payload["summary"]["courseReferencePacketStarted"] is True
    assert payload["summary"]["privateCourseReferenceOnly"] is True
    assert CLAIM_FLAGS["course_reference_packet_started"] is True
    assert CLAIM_FLAGS["private_course_reference_only"] is True


def test_d34_records_six_course_reference_rows():
    payload = build_payload(ATLAS_GATE)
    witness_ids = {row["witnessId"] for row in payload["courseReferenceRows"]}
    assert payload["summary"]["frozenWitnessCount"] == 6
    assert payload["summary"]["courseReferenceRowCount"] == 6
    assert "constants_zero_one_e_boundary" in witness_ids
    assert "ln_from_eml_boundary" in witness_ids
    assert "subtraction_boundary_affine_offset" in witness_ids
    assert "subtraction_boundary_two_stage_chain" in witness_ids
    assert "subtraction_boundary_affine_nested_chain" in witness_ids
    assert "subtraction_boundary_three_stage_chain" in witness_ids
    assert all(row["course2ReferenceRole"] == "private_reference_only" for row in payload["courseReferenceRows"])


def test_d34_preserves_d30_caveats_and_blockers():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["d30RequiredCaveatCount"] == 5
    assert payload["summary"]["d30BlockedGlobalPhraseCount"] == 8
    assert len(payload["preservedRequiredCaveats"]) == 5
    assert len(payload["preservedBlockedGlobalPhrases"]) == 8
    assert "theorem discovery" in payload["preservedBlockedGlobalPhrases"]
    assert "broad nested subtraction family" in payload["preservedBlockedGlobalPhrases"]


def test_d34_records_course2_guards_and_next_actions():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["course2GuardCount"] == 5
    assert payload["summary"]["nextCourse2ActionCount"] == 3
    assert guard_by_id(payload, "private_reference_only")["guardStatus"] == "required"
    assert guard_by_id(payload, "no_laptop_repo_touch")["guardStatus"] == "required"
    assert action_by_id(payload, "course2_lesson_outline_claim_boundary")["availability"] == "available_next_private_packet"
    assert action_by_id(payload, "human_approved_public_copy_gate")["availability"] == "parked_requires_explicit_human_approval"


def test_d34_does_not_publish_or_generate_lesson_packet():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["coursePublicationStarted"] is False
    assert payload["summary"]["lessonPacketGenerated"] is False
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["humanApprovalRecorded"] is False
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["publicReady"] is False


def test_d34_touches_no_laptop_repo_or_proof_work():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False


def test_d34_keeps_runtime_and_broad_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "standard_subtraction_remains_runtime_control"
    assert payload["summary"]["broadNestedSubtractionClaim"] is False
    assert payload["summary"]["broadSubtractionFamilyClaim"] is False
    assert payload["summary"]["arbitraryDepthClaim"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False


def test_d34_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsAllBounded"] is True
    assert payload["claimFlags"]["course_reference_packet_started"] is True
    assert payload["claimFlags"]["private_course_reference_only"] is True
    for key, value in payload["claimFlags"].items():
        if key not in {"course_reference_packet_started", "private_course_reference_only"}:
            assert value is False
    assert all(row["publicPromotionAllowed"] is False for row in payload["courseReferenceRows"])


def test_d34_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D34")


def test_d34_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d34_course2_private_reference_packet.py",
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
    assert "EML_D34_COURSE2_PRIVATE_REFERENCE_PACKET_OK" in proc.stdout
