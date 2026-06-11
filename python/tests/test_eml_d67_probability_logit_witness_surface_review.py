"""Tests for EML-D67 probability logit witness surface review."""

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

from scripts.eml_d67_probability_logit_witness_surface_review import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def row_by_id(payload, surface_id: str):
    return next(item for item in payload["surfaceRows"] if item["surfaceId"] == surface_id)


def test_d67_consumes_d66_witness_attempt():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D67_PROBABILITY_LOGIT_WITNESS_SURFACE_REVIEW_PASS"
    assert payload["sourceWitnessAttempt"] == "eml-d66-probability-logit-boundary-coordinate-witness-attempt"
    assert payload["summary"]["selectedWitnessName"] == "MachLib.Real.probability_logit_boundary_coordinate_witness"


def test_d67_preserves_checked_statement_guards_and_runtime_control():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["checkedStatement"] == (
        "0 < p -> p < 1 -> eml (log p) (exp (log (1 - p))) = p - log (1 - p)"
    )
    assert payload["summary"]["machlibFile"] == "foundations/MachLib/EMLAtlasWitness.lean"
    assert payload["summary"]["guardCount"] == 2
    assert payload["summary"]["sourceDerivedDomainObligationCount"] == 2
    assert payload["summary"]["runtimeLoweringControl"] == "protected_log_and_log1p_remain_runtime_controls"
    runtime = row_by_id(payload, "probability_logit_runtime_control_guardrail")
    assert runtime["surfaceStatus"] == "protected_log_and_log1p_runtime_controls_required"
    assert "logit runtime replacement" in runtime["blockedClaims"]


def test_d67_records_five_private_surface_rows():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["surfaceRowCount"] == 5
    assert row_by_id(payload, "machlib_witness_index_probability_logit_boundary")["surfaceKind"] == "machlib_private_index"
    assert row_by_id(payload, "probability_logit_guard_boundary")["surfaceKind"] == "candidate_boundary"
    assert row_by_id(payload, "probability_logit_runtime_control_guardrail")["surfaceKind"] == "runtime_control_guardrail"
    assert row_by_id(payload, "advantage_lab_probability_logit_boundary")["surfaceKind"] == "advantage_lab"
    assert row_by_id(payload, "public_atlas_probability_logit_boundary")["surfaceKind"] == "public_surface"


def test_d67_preserves_d65_negative_controls_and_blockers():
    payload = build_payload(ATLAS_GATE)
    boundary = row_by_id(payload, "probability_logit_guard_boundary")
    assert payload["summary"]["sourceNegativeControlCount"] == 4
    assert payload["summary"]["sourceBlockerCount"] == 4
    assert boundary["surfaceStatus"] == "guarded_domain_boundary_required"
    assert "p = 0 boundary" in boundary["blockedClaims"]
    assert "p = 1 boundary" in boundary["blockedClaims"]
    assert "unguarded statements remain blocked" in " ".join(boundary["rationale"])


def test_d67_records_checked_witness_privately_without_new_proof_work():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["checkedWitnessRecordedPrivately"] is True
    assert payload["summary"]["candidateProved"] is True
    assert payload["summary"]["buildPassed"] is True
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProvedThisPhase"] is False
    assert payload["summary"]["proofAttemptStarted"] is False


def test_d67_keeps_public_advantage_runtime_and_laptop_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationCandidate"] is False
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["protectedLogReplacementClaim"] is False
    assert payload["summary"]["protectedLog1pReplacementClaim"] is False
    assert payload["summary"]["protectedExpm1ReplacementClaim"] is False
    assert payload["summary"]["surfaceUpdated"] is False
    assert payload["summary"]["boundedTrigFeasibilitySelected"] is False
    assert payload["summary"]["humanPublicCopyGateSelected"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d67_claim_flags_are_all_false():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())
    for row in payload["surfaceRows"]:
        assert all(value is False for value in row["claimFlags"].values())


def test_d67_points_to_next_selector():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["nextAction"] == (
        "EML-D68 choose probability-logit checked-witness copy review, next bounded branch, or human-approved public copy gate without public promotion."
    )


def test_d67_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D67")


def test_d67_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d67_probability_logit_witness_surface_review.py",
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
    assert "EML_D67_PROBABILITY_LOGIT_WITNESS_SURFACE_REVIEW_OK" in proc.stdout
