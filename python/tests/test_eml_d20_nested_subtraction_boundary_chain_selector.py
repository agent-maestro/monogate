"""Tests for EML-D20 nested subtraction-boundary chain selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d20_nested_subtraction_boundary_chain_selector import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def statement_by_id(payload, statement_id: str):
    return next(item for item in payload["candidateStatements"] if item["statementId"] == statement_id)


def test_d20_consumes_d19_decision():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D20_NESTED_SUBTRACTION_BOUNDARY_CHAIN_SELECTOR_PASS"
    assert payload["sourceDecision"] == "eml-d19-next-proof-family-branch-decision"
    assert payload["summary"]["sourceSelectedOptionId"] == "nested_subtraction_boundary_chain_selector"


def test_d20_selects_two_stage_chain_statement():
    payload = build_payload(ATLAS_GATE)
    selected = payload["selectedStatement"]
    assert payload["summary"]["selectedStatementId"] == "subtraction_boundary_two_stage_chain_v1"
    assert payload["summary"]["selectedProofTarget"] == "MachLib.Real.subtraction_boundary_two_stage_chain_witness"
    assert payload["summary"]["selectedNextArtifact"] == "EML-D21 subtraction-boundary two-stage chain witness attempt"
    assert selected["selectionStatus"] == "selected_next"
    assert selected["domainGuards"] == ["0 < v", "0 < w"]
    assert len(selected["expectedRewriteSteps"]) == 2


def test_d20_parks_harder_nested_variants():
    payload = build_payload(ATLAS_GATE)
    affine = statement_by_id(payload, "subtraction_boundary_affine_nested_chain_v1")
    three_stage = statement_by_id(payload, "subtraction_boundary_three_stage_chain_v1")
    assert affine["selectionStatus"] == "candidate_later"
    assert three_stage["selectionStatus"] == "candidate_later"
    assert payload["summary"]["affineNestedChainParked"] is True
    assert payload["summary"]["deeperChainParked"] is True


def test_d20_blocks_unguarded_nested_negative_control():
    payload = build_payload(ATLAS_GATE)
    negative = statement_by_id(payload, "subtraction_boundary_nested_unguarded_negative_control_v1")
    assert negative["selectionStatus"] == "blocked_negative_control"
    assert negative["domainGuards"] == []
    assert payload["summary"]["negativeControlBlocked"] is True


def test_d20_does_not_start_proof_or_change_runtime_lowering():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "standard_subtraction_remains_runtime_control"


def test_d20_keeps_nested_family_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["broadNestedSubtractionClaim"] is False
    assert payload["summary"]["broadSubtractionFamilyClaim"] is False
    assert payload["summary"]["publicReady"] is False


def test_d20_claim_flags_remain_false():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())
    for statement in payload["candidateStatements"]:
        assert all(value is False for value in statement["claimFlags"].values())


def test_d20_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D20")


def test_d20_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d20_nested_subtraction_boundary_chain_selector.py",
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
    assert "EML_D20_NESTED_SUBTRACTION_BOUNDARY_CHAIN_SELECTOR_OK" in proc.stdout
