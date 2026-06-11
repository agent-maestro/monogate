"""Tests for EML-D93 log1p affine-scaled boundary coordinate witness attempt."""

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

from scripts.eml_d93_log1p_affine_scaled_boundary_coordinate_witness_attempt import (
    CLAIM_FLAGS,
    ROOT,
    TRUE_CLAIM_KEYS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_d93_consumes_d92_feasibility_packet():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D93_LOG1P_AFFINE_SCALED_BOUNDARY_COORDINATE_WITNESS_ATTEMPT_PASS"
    assert payload["sourceFeasibilityPacket"] == (
        "eml-d92-log1p-affine-scaled-boundary-coordinate-feasibility-packet"
    )
    assert payload["summary"]["sourceSelectedCandidateId"] == "log1p_affine_scaled_boundary_coordinate"
    assert payload["summary"]["sourceFeasibilityStatus"] == "feasible_for_guarded_scoped_witness_attempt"


def test_d93_records_checked_affine_scaled_witness():
    payload = build_payload(ATLAS_GATE)
    witness = payload["checkedWitness"]
    assert payload["decision"] == "checked_log1p_affine_scaled_boundary_coordinate_witness"
    assert payload["summary"]["machlibName"] == "MachLib.Real.log1p_affine_scaled_boundary_coordinate_witness"
    assert payload["summary"]["machlibFile"] == "foundations/MachLib/EMLAtlasWitness.lean"
    assert payload["summary"]["checkedStatement"] == (
        "0 < 1 + a * x -> eml (log (1 + a * x)) (exp 1) = a * x"
    )
    assert witness["guardShape"] == ["0 < 1 + a * x"]
    assert witness["derivedDomainObligations"] == ["0 < 1 + a * x", "0 < exp 1"]


def test_d93_preserves_d92_controls_blockers_and_duplicate_blocks():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["sourceSelectedFamily"] == "guarded_log1p_affine_scaled_coordinate"
    assert summary["sourceGuardCount"] == 1
    assert summary["sourceDerivedDomainObligationCount"] == 2
    assert summary["sourceNegativeControlCount"] == 5
    assert summary["sourceBlockerCount"] == 5
    assert summary["sourceRuntimeLoweringControl"] == "protected_log_and_log1p_remain_runtime_controls"
    assert summary["sourceDuplicateShiftedBlocksPreserved"] is True
    assert summary["duplicateShiftedBlocksPreserved"] is True


def test_d93_records_checked_build_status():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["implementationStarted"] is True
    assert payload["summary"]["machlibFileChanged"] is True
    assert payload["summary"]["leanTypecheckPerformed"] is True
    assert payload["summary"]["candidateProved"] is True
    assert payload["summary"]["candidateProvedThisPhase"] is True
    assert payload["summary"]["proofAttemptStarted"] is True
    assert payload["summary"]["buildPassed"] is True
    assert payload["checkedWitness"]["buildCommand"] == "cd foundations && lake build"
    assert payload["checkedWitness"]["buildStatus"] == "passed"
    assert payload["summary"]["guardCount"] == 1
    assert payload["summary"]["proofStepCount"] == 4
    assert payload["summary"]["knownUnrelatedWarningCount"] == 3


def test_d93_keeps_protected_log1p_runtime_controls_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeLoweringControl"] == "protected_log_and_log1p_remain_runtime_controls"
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["protectedLogReplacementClaim"] is False
    assert payload["summary"]["protectedLog1pReplacementClaim"] is False
    assert payload["summary"]["protectedExpm1ReplacementClaim"] is False


def test_d93_keeps_public_reviewer_laptop_and_electronics_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["publicCopyApproved"] is False
    assert summary["publicPromotionPerformed"] is False
    assert summary["publicEducationPromotionPerformed"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["advantageLabCaseAdded"] is False
    assert summary["boundedTrigFeasibilitySelected"] is False
    assert summary["privateReviewerResponseIntakeSelected"] is False
    assert summary["humanPublicCopyGateSelected"] is False
    assert summary["humanApprovalRecorded"] is False
    assert summary["reviewerDecisionRecorded"] is False
    assert summary["reviewerApprovalRecorded"] is False
    assert summary["reviewerRejectionRecorded"] is False
    assert summary["electronicsRepoTouched"] is False
    assert summary["laptopArtifactConsumed"] is False
    assert summary["publicReady"] is False


def test_d93_next_artifact_is_private_surface_review():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["nextArtifact"] == (
        "EML-D94 log1p affine-scaled checked-witness private surface review"
    )


def test_d93_claim_flags_are_checked_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsCheckedOnly"] is True
    for key in TRUE_CLAIM_KEYS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_KEYS:
            assert value is False


def test_d93_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D93")


def test_d93_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d93_log1p_affine_scaled_boundary_coordinate_witness_attempt.py",
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
    assert "EML_D93_LOG1P_AFFINE_SCALED_BOUNDARY_COORDINATE_WITNESS_ATTEMPT_OK" in proc.stdout
