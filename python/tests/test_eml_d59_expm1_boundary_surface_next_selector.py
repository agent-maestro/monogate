"""Tests for EML-D59 expm1 boundary surface next selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d59_expm1_boundary_surface_next_selector import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def option_by_id(payload, option_id: str):
    return next(item for item in payload["selectorOptions"] if item["optionId"] == option_id)


def test_d59_consumes_d58_surface_review():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D59_EXPM1_BOUNDARY_SURFACE_NEXT_SELECTOR_PASS"
    assert payload["sourceSurfaceReview"] == "eml-d58-expm1-boundary-witness-surface-review"
    assert payload["summary"]["d58SurfaceRowCount"] == 5


def test_d59_preserves_checked_witness_and_runtime_control():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["selectedWitnessName"] == "MachLib.Real.expm1_boundary_identity_witness"
    assert payload["summary"]["checkedStatement"] == "eml x (exp 1) = exp x - 1"
    assert payload["summary"]["machlibFile"] == "foundations/MachLib/EMLAtlasWitness.lean"
    assert payload["summary"]["runtimeLoweringControl"] == "protected_expm1_remains_runtime_control"
    assert payload["summary"]["runtimeGuardrailStatus"] == "protected_expm1_runtime_control_required"
    assert payload["summary"]["publicAtlasStatus"] == "held_private"


def test_d59_selects_checked_witness_copy_review_packet():
    payload = build_payload(ATLAS_GATE)
    selected = option_by_id(payload, "expm1_boundary_checked_witness_copy_review_packet")
    assert payload["decision"] == "select_expm1_boundary_checked_witness_copy_review_packet"
    assert payload["summary"]["selectedOptionId"] == "expm1_boundary_checked_witness_copy_review_packet"
    assert payload["summary"]["selectedNextArtifact"] == "EML-D60 expm1-boundary checked-witness copy review packet"
    assert payload["summary"]["nextActionSelected"] is True
    assert payload["summary"]["checkedWitnessCopyReviewSelected"] is True
    assert selected["selectionStatus"] == "selected_next"
    assert selected["lane"] == "private_copy_review_lane"


def test_d59_parks_bounded_branch_trig_and_public_gate():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["optionCount"] == 4
    assert option_by_id(payload, "next_bounded_identity_branch_selector")["selectionStatus"] == "candidate_later_after_copy_review"
    assert option_by_id(payload, "bounded_trig_identity_feasibility_selector")["selectionStatus"] == "candidate_later"
    assert option_by_id(payload, "human_approved_public_copy_gate")["selectionStatus"] == "candidate_later_requires_human_approval"
    assert payload["summary"]["nextBoundedBranchSelected"] is False
    assert payload["summary"]["boundedTrigFeasibilitySelected"] is False
    assert payload["summary"]["humanPublicCopyGateSelected"] is False
    assert payload["summary"]["humanApprovalRecorded"] is False


def test_d59_starts_no_copy_review_public_update_or_proof_work():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["copyReviewStarted"] is False
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["candidateProvedThisPhase"] is False
    assert payload["summary"]["proofAttemptStarted"] is False


def test_d59_keeps_runtime_and_laptop_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["protectedExpm1ReplacementClaim"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d59_claim_flags_are_selector_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsSelectorOnly"] is True
    for key in ["next_action_selected", "checked_witness_copy_review_selected"]:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in {"next_action_selected", "checked_witness_copy_review_selected"}:
            assert value is False
    for option in payload["selectorOptions"]:
        assert option["claimFlags"]["next_action_selected"] is True
        assert option["claimFlags"]["checked_witness_copy_review_selected"] is True
        for key, value in option["claimFlags"].items():
            if key not in {"next_action_selected", "checked_witness_copy_review_selected"}:
                assert value is False


def test_d59_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D59")


def test_d59_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d59_expm1_boundary_surface_next_selector.py",
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
    assert "EML_D59_EXPM1_BOUNDARY_SURFACE_NEXT_SELECTOR_OK" in proc.stdout
