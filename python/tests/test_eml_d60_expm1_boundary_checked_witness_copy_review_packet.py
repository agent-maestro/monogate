"""Tests for EML-D60 expm1 boundary checked-witness copy review packet."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d60_expm1_boundary_checked_witness_copy_review_packet import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_d60_consumes_d59_next_selector():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D60_EXPM1_BOUNDARY_CHECKED_WITNESS_COPY_REVIEW_PACKET_PASS"
    assert payload["sourceSelector"] == "eml-d59-expm1-boundary-surface-next-selector"
    assert payload["summary"]["selectedOptionId"] == "expm1_boundary_checked_witness_copy_review_packet"


def test_d60_reviews_one_expm1_witness_row():
    payload = build_payload(ATLAS_GATE)
    row = payload["witnessCopyRows"][0]
    assert payload["summary"]["witnessRowCount"] == 1
    assert row["witnessId"] == "expm1_boundary_identity"
    assert row["machlibName"] == "MachLib.Real.expm1_boundary_identity_witness"
    assert row["copyStatus"] == "private_checked_witness_copy_reviewable"
    assert row["publicPromotionAllowed"] is False
    assert "eml x (exp 1) = exp x - 1" in row["safePrivatePhrase"]
    assert "protected expm1 remains" in row["safePrivatePhrase"]


def test_d60_preserves_checked_statement_and_surface_boundaries():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["selectedWitnessName"] == "MachLib.Real.expm1_boundary_identity_witness"
    assert payload["summary"]["checkedStatement"] == "eml x (exp 1) = exp x - 1"
    assert payload["summary"]["machlibFile"] == "foundations/MachLib/EMLAtlasWitness.lean"
    assert payload["summary"]["guardCount"] == 0
    assert payload["summary"]["d58SurfaceRowCount"] == 5
    assert payload["summary"]["runtimeGuardrailStatus"] == "protected_expm1_runtime_control_required"
    assert payload["summary"]["publicAtlasStatus"] == "held_private"


def test_d60_records_required_caveats_and_blocked_phrases():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["requiredCaveatCount"] == 8
    assert payload["summary"]["blockedGlobalPhraseCount"] == 10
    assert "The checked statement is eml x (exp 1) = exp x - 1." in payload["requiredCaveats"]
    assert "protected expm1 replacement" in payload["blockedGlobalPhrases"]
    row = payload["witnessCopyRows"][0]
    assert len(row["requiredCaveats"]) == 6
    assert "duplicate exp branch witness" in row["blockedPhrases"]


def test_d60_is_private_checked_witness_copy_review_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["copyReviewStarted"] is True
    assert payload["summary"]["privateCopyReviewOnly"] is True
    assert payload["summary"]["checkedWitnessCopyReviewOnly"] is True
    assert payload["summary"]["runtimeLoweringControl"] == "protected_expm1_remains_runtime_control"


def test_d60_keeps_public_runtime_work_and_laptop_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["protectedExpm1ReplacementClaim"] is False
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["candidateProvedThisPhase"] is False
    assert payload["summary"]["proofAttemptStarted"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d60_keeps_future_options_parked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["newBoundedBranchSelected"] is False
    assert payload["summary"]["boundedTrigFeasibilitySelected"] is False
    assert payload["summary"]["humanPublicCopyGateSelected"] is False
    assert payload["summary"]["humanApprovalRecorded"] is False
    assert payload["summary"]["nextAction"] == (
        "EML-D61 choose expm1-boundary pause/freeze, next bounded branch, or human-approved public copy gate."
    )


def test_d60_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsAllBounded"] is True
    for key in ["copy_review_started", "private_copy_review_only", "checked_witness_copy_review_only"]:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in {"copy_review_started", "private_copy_review_only", "checked_witness_copy_review_only"}:
            assert value is False
    for row in payload["witnessCopyRows"]:
        for key, value in row["claimFlags"].items():
            if key not in {"copy_review_started", "private_copy_review_only", "checked_witness_copy_review_only"}:
                assert value is False


def test_d60_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D60")


def test_d60_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d60_expm1_boundary_checked_witness_copy_review_packet.py",
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
    assert "EML_D60_EXPM1_BOUNDARY_CHECKED_WITNESS_COPY_REVIEW_PACKET_OK" in proc.stdout
