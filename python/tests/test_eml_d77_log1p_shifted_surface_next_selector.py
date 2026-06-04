"""Tests for EML-D77 log1p shifted surface next selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d77_log1p_shifted_surface_next_selector import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def option_by_id(payload, option_id: str):
    return next(item for item in payload["selectorOptions"] if item["optionId"] == option_id)


def test_d77_consumes_d76_surface_review():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D77_LOG1P_SHIFTED_SURFACE_NEXT_SELECTOR_PASS"
    assert payload["sourceSurfaceReview"] == "eml-d76-log1p-shifted-witness-surface-review"
    assert payload["summary"]["selectedWitnessName"] == "MachLib.Real.log1p_shifted_boundary_coordinate_witness"


def test_d77_preserves_log1p_shifted_surface_boundaries():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["checkedStatement"] == "0 < 1 + x -> eml (log (1 + x)) (exp 1) = x"
    assert payload["summary"]["guardCount"] == 1
    assert payload["summary"]["sourceDerivedDomainObligationCount"] == 2
    assert payload["summary"]["sourceNegativeControlCount"] == 4
    assert payload["summary"]["sourceBlockerCount"] == 4
    assert payload["summary"]["guardBoundaryStatus"] == "shifted_positive_domain_boundary_required"
    assert payload["summary"]["runtimeGuardrailStatus"] == "protected_log_and_log1p_runtime_controls_required"
    assert payload["summary"]["publicAtlasStatus"] == "held_private"


def test_d77_selects_copy_review_packet_next():
    payload = build_payload(ATLAS_GATE)
    selected = option_by_id(payload, "log1p_shifted_checked_witness_copy_review_packet")
    assert payload["decision"] == "select_log1p_shifted_checked_witness_copy_review_packet"
    assert payload["summary"]["selectedOptionId"] == "log1p_shifted_checked_witness_copy_review_packet"
    assert payload["summary"]["selectedNextArtifact"] == "EML-D78 log1p-shifted checked-witness copy review packet"
    assert selected["selectionStatus"] == "selected_next"
    assert payload["summary"]["checkedWitnessCopyReviewSelected"] is True
    assert payload["summary"]["copyReviewStarted"] is False


def test_d77_parks_other_options():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["optionCount"] == 4
    assert option_by_id(payload, "next_bounded_identity_branch_selector")["selectionStatus"] == (
        "candidate_later_after_copy_review"
    )
    assert option_by_id(payload, "bounded_trig_identity_feasibility_selector")["selectionStatus"] == "candidate_later"
    assert option_by_id(payload, "human_approved_public_copy_gate")["selectionStatus"] == (
        "candidate_later_requires_human_approval"
    )
    assert payload["summary"]["nextBoundedBranchSelected"] is False
    assert payload["summary"]["boundedTrigFeasibilitySelected"] is False
    assert payload["summary"]["humanPublicCopyGateSelected"] is False


def test_d77_keeps_public_runtime_proof_and_laptop_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["protectedLogReplacementClaim"] is False
    assert payload["summary"]["protectedLog1pReplacementClaim"] is False
    assert payload["summary"]["protectedExpm1ReplacementClaim"] is False
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["proofAttemptStarted"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d77_claim_flags_are_selector_only():
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


def test_d77_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D77")


def test_d77_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d77_log1p_shifted_surface_next_selector.py",
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
    assert "EML_D77_LOG1P_SHIFTED_SURFACE_NEXT_SELECTOR_OK" in proc.stdout
