"""Tests for EML-D16 subtraction-boundary family selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d16_subtraction_boundary_family_selector import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def statement_by_id(payload, statement_id: str):
    return next(item for item in payload["candidateStatements"] if item["statementId"] == statement_id)


def test_d16_consumes_d15_decision():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D16_SUBTRACTION_BOUNDARY_FAMILY_SELECTOR_PASS"
    assert payload["sourceDecision"] == "eml-d15-checked-witness-next-decision"
    assert payload["summary"]["sourceSelectedCandidateId"] == "subtraction_boundary_family_v1"


def test_d16_selects_affine_offset_family_statement():
    payload = build_payload(ATLAS_GATE)
    selected = payload["selectedStatement"]
    assert payload["summary"]["selectedStatementId"] == "subtraction_boundary_affine_offset_family_v1"
    assert payload["summary"]["selectedProofTarget"] == "MachLib.Real.subtraction_boundary_affine_offset_witness"
    assert payload["summary"]["selectedNextArtifact"] == "EML-D17 subtraction-boundary affine-offset witness attempt"
    assert selected["selectionStatus"] == "selected_next"
    assert selected["statement"] == "eml (log (x + y)) (exp y) = x, under 0 < x + y"
    assert selected["domainGuards"] == ["0 < x + y"]


def test_d16_rejects_duplicate_base_and_blocks_unguarded_control():
    payload = build_payload(ATLAS_GATE)
    duplicate = statement_by_id(payload, "subtraction_boundary_base_duplicate_v0")
    negative = statement_by_id(payload, "subtraction_boundary_unguarded_negative_control_v1")
    assert duplicate["selectionStatus"] == "rejected_duplicate_checked_base"
    assert negative["selectionStatus"] == "blocked_negative_control"
    assert payload["summary"]["duplicateBaseRejected"] is True
    assert payload["summary"]["negativeControlBlocked"] is True


def test_d16_keeps_two_stage_chain_for_later():
    payload = build_payload(ATLAS_GATE)
    chain = statement_by_id(payload, "subtraction_boundary_two_stage_chain_v1")
    assert chain["selectionStatus"] == "candidate_later"
    assert "nested rewrite surface" in chain["blockers"]


def test_d16_does_not_start_proof_or_change_runtime_lowering():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "standard_subtraction_remains_runtime_control"


def test_d16_claim_flags_remain_false():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())
    for statement in payload["candidateStatements"]:
        assert all(value is False for value in statement["claimFlags"].values())


def test_d16_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D16")


def test_d16_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d16_subtraction_boundary_family_selector.py",
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
    assert "EML_D16_SUBTRACTION_BOUNDARY_FAMILY_SELECTOR_OK" in proc.stdout
