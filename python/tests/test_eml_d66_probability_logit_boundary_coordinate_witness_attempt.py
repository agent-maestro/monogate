"""Tests for EML-D66 probability logit boundary coordinate witness attempt."""

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

from scripts.eml_d66_probability_logit_boundary_coordinate_witness_attempt import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_d66_consumes_d65_feasibility_packet():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D66_PROBABILITY_LOGIT_BOUNDARY_COORDINATE_WITNESS_ATTEMPT_PASS"
    assert payload["sourceFeasibilityPacket"] == "eml-d65-probability-logit-boundary-coordinate-feasibility-packet"
    assert payload["summary"]["sourceSelectedCandidateId"] == "probability_logit_boundary_coordinate"
    assert payload["summary"]["sourceFeasibilityStatus"] == "feasible_for_guarded_scoped_witness_attempt"


def test_d66_records_checked_probability_logit_witness():
    payload = build_payload(ATLAS_GATE)
    witness = payload["checkedWitness"]
    assert payload["decision"] == "checked_probability_logit_boundary_coordinate_witness"
    assert payload["summary"]["machlibName"] == "MachLib.Real.probability_logit_boundary_coordinate_witness"
    assert payload["summary"]["machlibFile"] == "foundations/MachLib/EMLAtlasWitness.lean"
    assert payload["summary"]["checkedStatement"] == (
        "0 < p -> p < 1 -> eml (log p) (exp (log (1 - p))) = p - log (1 - p)"
    )
    assert witness["guardShape"] == ["0 < p", "p < 1"]
    assert witness["derivedDomainObligations"] == ["0 < p", "0 < 1 - p"]


def test_d66_preserves_d65_controls_and_blockers():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["sourceGuardCount"] == 2
    assert payload["summary"]["sourceDerivedDomainObligationCount"] == 2
    assert payload["summary"]["sourceNegativeControlCount"] == 4
    assert payload["summary"]["sourceBlockerCount"] == 4
    assert payload["summary"]["sourceRuntimeLoweringControl"] == "protected_log_and_log1p_remain_runtime_controls"


def test_d66_records_checked_build_status():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["implementationStarted"] is True
    assert payload["summary"]["machlibFileChanged"] is True
    assert payload["summary"]["leanTypecheckPerformed"] is True
    assert payload["summary"]["candidateProved"] is True
    assert payload["summary"]["proofAttemptStarted"] is True
    assert payload["summary"]["buildPassed"] is True
    assert payload["checkedWitness"]["buildCommand"] == "cd foundations && lake build"
    assert payload["checkedWitness"]["buildStatus"] == "passed"
    assert payload["summary"]["knownUnrelatedWarningCount"] == 3


def test_d66_keeps_protected_log_runtime_controls_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeLoweringControl"] == "protected_log_and_log1p_remain_runtime_controls"
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["protectedLogReplacementClaim"] is False
    assert payload["summary"]["protectedLog1pReplacementClaim"] is False
    assert payload["summary"]["protectedExpm1ReplacementClaim"] is False


def test_d66_keeps_public_laptop_and_electronics_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False
    assert payload["summary"]["boundedTrigFeasibilitySelected"] is False
    assert payload["summary"]["humanPublicCopyGateSelected"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d66_next_artifact_is_private_surface_review():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["nextArtifact"] == "EML-D67 probability logit checked-witness private surface review"


def test_d66_claim_flags_are_checked_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsCheckedOnly"] is True
    for key in [
        "witness_feasibility_recorded",
        "bounded_identity_candidate_selected",
        "probability_logit_boundary_candidate_selected",
        "guarded_domain_obligations_recorded",
        "negative_controls_recorded",
        "implementation_started",
        "machlib_file_changed",
        "lean_typecheck_performed",
        "candidate_proved",
        "proof_attempt_started",
    ]:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in {
            "witness_feasibility_recorded",
            "bounded_identity_candidate_selected",
            "probability_logit_boundary_candidate_selected",
            "guarded_domain_obligations_recorded",
            "negative_controls_recorded",
            "implementation_started",
            "machlib_file_changed",
            "lean_typecheck_performed",
            "candidate_proved",
            "proof_attempt_started",
        }:
            assert value is False


def test_d66_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D66")


def test_d66_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d66_probability_logit_boundary_coordinate_witness_attempt.py",
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
    assert "EML_D66_PROBABILITY_LOGIT_BOUNDARY_COORDINATE_WITNESS_ATTEMPT_OK" in proc.stdout
