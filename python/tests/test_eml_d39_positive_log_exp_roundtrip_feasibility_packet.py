"""Tests for EML-D39 positive log-exp roundtrip feasibility packet."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d39_positive_log_exp_roundtrip_feasibility_packet import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_d39_consumes_d38_branch_selector():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D39_POSITIVE_LOG_EXP_ROUNDTRIP_FEASIBILITY_PASS"
    assert payload["sourceBranchSelector"] == "eml-d38-bounded-identity-branch-selector"
    assert payload["summary"]["sourceSelectedCandidateId"] == "positive_log_exp_roundtrip_identity"
    assert payload["summary"]["sourceSelectedFamily"] == "positive_domain_log_exp_roundtrip"


def test_d39_records_guarded_statement_feasibility():
    payload = build_payload(ATLAS_GATE)
    witness = payload["proposedWitness"]
    assert payload["decision"] == "record_positive_log_exp_roundtrip_feasibility"
    assert payload["summary"]["feasibilityRecorded"] is True
    assert payload["summary"]["feasibilityStatus"] == "feasible_for_scoped_witness_attempt"
    assert witness["proposedMachlibName"] == "MachLib.Real.positive_log_exp_roundtrip_witness"
    assert witness["proposedStatement"] == "0 < x -> exp (log x) = x"
    assert witness["guardShape"] == ["0 < x"]
    assert witness["emlShape"] == "exp (log x)"
    assert witness["standardShape"] == "x"


def test_d39_feasibility_items_are_satisfied():
    payload = build_payload(ATLAS_GATE)
    assert len(payload["feasibilityItems"]) == 4
    assert {item["itemId"] for item in payload["feasibilityItems"]} == {
        "selected_branch_matches_d38",
        "positive_domain_guard_explicit",
        "statement_shape_small",
        "runtime_boundary_preserved",
    }
    assert all(item["status"] == "satisfied" for item in payload["feasibilityItems"])


def test_d39_records_hard_blockers():
    payload = build_payload(ATLAS_GATE)
    assert len(payload["blockers"]) == 3
    assert {item["blockerId"] for item in payload["blockers"]} == {
        "guard_omitted",
        "runtime_relabeling",
        "broad_family_language",
    }
    assert all(item["severity"] == "hard_blocker" for item in payload["blockers"])


def test_d39_starts_no_implementation_or_proof_work():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["proofAttemptStarted"] is False


def test_d39_keeps_runtime_log_exp_and_public_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "standard_subtraction_remains_runtime_control"
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["publicReady"] is False


def test_d39_keeps_course_and_laptop_work_parked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False


def test_d39_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsAllBounded"] is True
    assert CLAIM_FLAGS["witness_feasibility_recorded"] is True
    assert CLAIM_FLAGS["bounded_identity_branch_selected"] is True
    for key, value in payload["claimFlags"].items():
        if key not in {"witness_feasibility_recorded", "bounded_identity_branch_selected"}:
            assert value is False


def test_d39_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D39")


def test_d39_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d39_positive_log_exp_roundtrip_feasibility_packet.py",
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
    assert "EML_D39_POSITIVE_LOG_EXP_ROUNDTRIP_FEASIBILITY_OK" in proc.stdout
