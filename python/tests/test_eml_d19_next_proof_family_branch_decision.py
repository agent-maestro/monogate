"""Tests for EML-D19 next proof-family branch decision."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d19_next_proof_family_branch_decision import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def option_by_id(payload, option_id: str):
    return next(item for item in payload["decisionOptions"] if item["optionId"] == option_id)


def test_d19_consumes_d18_surface_review():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D19_NEXT_PROOF_FAMILY_BRANCH_DECISION_PASS"
    assert payload["sourceSurfaceReview"] == "eml-d18-subtraction-boundary-affine-offset-surface-review"
    assert payload["summary"]["affineOffsetWitnessRecordedPrivately"] is True


def test_d19_selects_nested_chain_selector():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["selectedOptionId"] == "nested_subtraction_boundary_chain_selector"
    assert payload["summary"]["selectedNextArtifact"] == "EML-D20 nested subtraction-boundary chain selector"
    assert payload["selectedOption"]["selectionStatus"] == "selected_next"
    assert payload["selectedOption"]["lane"] == "private_proof_family_lane"


def test_d19_parks_copy_review_prime_and_fresh_identity():
    payload = build_payload(ATLAS_GATE)
    assert option_by_id(payload, "checked_witness_copy_review_packet")["selectionStatus"] == "candidate_later"
    assert option_by_id(payload, "prime_signature_log_recovery_feasibility_selector")["selectionStatus"] == "candidate_later"
    assert option_by_id(payload, "fresh_identity_family_selector")["selectionStatus"] == "candidate_later"


def test_d19_does_not_start_implementation_or_copy_review():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["copyReviewStarted"] is False
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False


def test_d19_keeps_runtime_and_family_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["broadSubtractionFamilyClaim"] is False
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "standard_subtraction_remains_runtime_control"


def test_d19_claim_flags_remain_false():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())
    for option in payload["decisionOptions"]:
        assert all(value is False for value in option["claimFlags"].values())


def test_d19_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D19")


def test_d19_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d19_next_proof_family_branch_decision.py",
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
    assert "EML_D19_NEXT_PROOF_FAMILY_BRANCH_DECISION_OK" in proc.stdout
