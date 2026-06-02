"""Tests for EML-D51 constant-coordinate delta copy review packet."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d51_constant_coordinate_delta_copy_review_packet import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_d51_consumes_d50_next_action_selector():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D51_CONSTANT_COORDINATE_DELTA_COPY_REVIEW_PACKET_PASS"
    assert payload["sourceSelector"] == "eml-d50-constant-coordinate-next-action-selector"
    assert payload["summary"]["selectedOptionId"] == "constant_coordinate_delta_copy_review_packet"


def test_d51_reviews_one_constant_coordinate_witness_row():
    payload = build_payload(ATLAS_GATE)
    row = payload["witnessCopyRows"][0]
    assert payload["summary"]["witnessRowCount"] == 1
    assert row["witnessId"] == "constant_coordinate_zero_exp_two"
    assert row["machlibName"] == "MachLib.Real.constant_coordinate_zero_exp_two_witness"
    assert row["copyStatus"] == "private_delta_copy_reviewable"
    assert row["publicPromotionAllowed"] is False
    assert "eml 0 (exp (1 + 1)) = -1" in row["safePrivatePhrase"]


def test_d51_preserves_source_checked_and_non_duplicate_boundaries():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["sourceProposedStatement"] == "eml 0 (exp 2) = -1"
    assert payload["summary"]["checkedLeanStatement"] == "eml 0 (exp (1 + 1)) = -1"
    assert payload["summary"]["localSpellingUsesOnePlusOne"] is True
    assert payload["summary"]["existingConstantWitnessName"] == "MachLib.Real.constants_zero_one_e_boundary_witness"
    assert payload["summary"]["duplicatesExistingConstantWitness"] is False
    assert payload["summary"]["guardCount"] == 0


def test_d51_records_required_caveats_and_blocked_phrases():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["requiredCaveatCount"] == 8
    assert payload["summary"]["blockedGlobalPhraseCount"] == 10
    assert "The checked Lean statement is eml 0 (exp (1 + 1)) = -1." in payload["requiredCaveats"]
    assert "duplicate constants bundle" in payload["blockedGlobalPhrases"]
    row = payload["witnessCopyRows"][0]
    assert len(row["requiredCaveats"]) == 6
    assert "unchecked exp 2 Lean theorem" in row["blockedPhrases"]


def test_d51_is_private_delta_copy_review_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["copyReviewStarted"] is True
    assert payload["summary"]["privateCopyReviewOnly"] is True
    assert payload["summary"]["deltaCopyReviewOnly"] is True
    assert payload["summary"]["publicHoldPreserved"] is True
    assert payload["summary"]["runtimeBoundaryPreserved"] is True


def test_d51_keeps_public_runtime_work_and_laptop_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "standard_log_exp_and_arithmetic_remain_runtime_controls"
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProvedThisPhase"] is False
    assert payload["summary"]["proofAttemptStarted"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d51_keeps_future_options_parked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["newBoundedBranchSelected"] is False
    assert payload["summary"]["boundedTrigFeasibilitySelected"] is False
    assert payload["summary"]["humanPublicCopyGateSelected"] is False
    assert payload["summary"]["nextAction"] == (
        "EML-D52 choose constant-coordinate pause/freeze, next bounded branch, or human-approved public copy gate."
    )


def test_d51_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsAllBounded"] is True
    for key in ["copy_review_started", "private_copy_review_only", "delta_copy_review_only"]:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in {"copy_review_started", "private_copy_review_only", "delta_copy_review_only"}:
            assert value is False
    for row in payload["witnessCopyRows"]:
        for key, value in row["claimFlags"].items():
            if key not in {"copy_review_started", "private_copy_review_only", "delta_copy_review_only"}:
                assert value is False


def test_d51_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D51")


def test_d51_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d51_constant_coordinate_delta_copy_review_packet.py",
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
    assert "EML_D51_CONSTANT_COORDINATE_DELTA_COPY_REVIEW_PACKET_OK" in proc.stdout
