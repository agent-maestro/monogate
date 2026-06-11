"""Tests for EML-D96 log1p affine-scaled checked-witness copy review packet."""

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

from scripts.eml_d96_log1p_affine_scaled_checked_witness_copy_review_packet import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_d96_consumes_d95_selector():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D96_LOG1P_AFFINE_SCALED_CHECKED_WITNESS_COPY_REVIEW_PACKET_PASS"
    assert payload["sourceSelector"] == "eml-d95-log1p-affine-scaled-surface-next-selector"
    assert payload["summary"]["selectedOptionId"] == "log1p_affine_scaled_checked_witness_copy_review_packet"


def test_d96_preserves_checked_witness_guard_and_duplicate_block():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["selectedWitnessName"] == "MachLib.Real.log1p_affine_scaled_boundary_coordinate_witness"
    assert payload["summary"]["checkedStatement"] == "0 < 1 + a * x -> eml (log (1 + a * x)) (exp 1) = a * x"
    assert payload["summary"]["machlibFile"] == "foundations/MachLib/EMLAtlasWitness.lean"
    assert payload["summary"]["guardCount"] == 1
    assert payload["summary"]["sourceNegativeControlCount"] == 5
    assert payload["summary"]["sourceBlockerCount"] == 5
    assert payload["summary"]["duplicateShiftedBlocksPreserved"] is True


def test_d96_records_private_copy_review_boundaries():
    payload = build_payload(ATLAS_GATE)
    row = payload["witnessCopyRows"][0]
    assert payload["summary"]["copyReviewStarted"] is True
    assert payload["summary"]["privateCopyReviewOnly"] is True
    assert payload["summary"]["checkedWitnessCopyReviewOnly"] is True
    assert payload["summary"]["witnessRowCount"] == 1
    assert payload["summary"]["requiredCaveatCount"] == 10
    assert payload["summary"]["blockedGlobalPhraseCount"] == 14
    assert payload["summary"]["rowRequiredCaveatCount"] == 7
    assert payload["summary"]["rowBlockedPhraseCount"] == 13
    assert row["copyStatus"] == "private_checked_witness_copy_reviewable"
    assert row["publicPromotionAllowed"] is False


def test_d96_freezes_guard_runtime_and_duplicate_copy_language():
    payload = build_payload(ATLAS_GATE)
    row = payload["witnessCopyRows"][0]
    assert "affine positive-domain guard" in " ".join(payload["requiredCaveats"])
    assert "0 < 1 + a * x" in " ".join(payload["requiredCaveats"])
    assert "Protected log and log1p remain" in " ".join(payload["requiredCaveats"])
    assert "duplicate shifted-coordinate blocks" in " ".join(payload["requiredCaveats"])
    assert "broad log1p-family statements remain blocked" in " ".join(row["requiredCaveats"])
    assert payload["summary"]["runtimeLoweringControl"] == "protected_log_and_log1p_remain_runtime_controls"
    assert payload["summary"]["runtimeGuardrailStatus"] == "protected_log_and_log1p_runtime_controls_required"
    assert payload["summary"]["publicAtlasStatus"] == "held_private"


def test_d96_blocks_public_runtime_and_broad_claims():
    payload = build_payload(ATLAS_GATE)
    assert "log replacement" in payload["blockedGlobalPhrases"]
    assert "log1p replacement" in payload["blockedGlobalPhrases"]
    assert "broad log1p family" in payload["blockedGlobalPhrases"]
    assert "broad EML advantage" in payload["blockedGlobalPhrases"]
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["protectedLogReplacementClaim"] is False
    assert payload["summary"]["protectedLog1pReplacementClaim"] is False
    assert payload["summary"]["publicReady"] is False


def test_d96_starts_no_machlib_proof_reviewer_or_laptop_work():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["proofAttemptStarted"] is False
    assert payload["summary"]["newBoundedBranchSelected"] is False
    assert payload["summary"]["privateReviewerResponseIntakeSelected"] is False
    assert payload["summary"]["humanPublicCopyGateSelected"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False


def test_d96_claim_flags_are_copy_review_only_with_duplicate_block():
    payload = build_payload(ATLAS_GATE)
    allowed_true = {
        "copy_review_started",
        "private_copy_review_only",
        "checked_witness_copy_review_only",
        "duplicate_shifted_blocks_preserved",
    }
    assert payload["summary"]["claimFlagsAllBounded"] is True
    for key in allowed_true:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in allowed_true:
            assert value is False


def test_d96_points_to_next_selector():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["nextAction"] == (
        "EML-D97 choose log1p affine-scaled branch pause/freeze, next bounded branch, private reviewer response intake, or human-approved public copy gate."
    )


def test_d96_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D96")


def test_d96_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d96_log1p_affine_scaled_checked_witness_copy_review_packet.py",
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
    assert "EML_D96_LOG1P_AFFINE_SCALED_CHECKED_WITNESS_COPY_REVIEW_PACKET_OK" in proc.stdout
