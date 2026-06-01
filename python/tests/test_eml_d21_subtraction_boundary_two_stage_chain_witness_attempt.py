"""Tests for EML-D21 two-stage subtraction-boundary witness attempt."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d21_subtraction_boundary_two_stage_chain_witness_attempt import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_d21_consumes_d20_selector():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D21_SUBTRACTION_BOUNDARY_TWO_STAGE_CHAIN_WITNESS_ATTEMPT_PASS"
    assert payload["sourceSelector"] == "eml-d20-nested-subtraction-boundary-chain-selector"
    assert payload["summary"]["selectedStatementId"] == "subtraction_boundary_two_stage_chain_v1"


def test_d21_records_checked_two_stage_witness():
    payload = build_payload(ATLAS_GATE)
    selected = payload["selectedWitness"]
    assert selected["machlibName"] == "MachLib.Real.subtraction_boundary_two_stage_chain_witness"
    assert selected["present"] is True
    assert payload["summary"]["selectedWitnessPresent"] is True
    assert payload["summary"]["scopedWitnessChecked"] is True


def test_d21_records_lake_build_pass():
    payload = build_payload(ATLAS_GATE)
    assert payload["verification"]["observedStatus"] == "pass"
    assert payload["summary"]["leanTypecheckPerformed"] is True
    assert payload["summary"]["lakeBuildPassed"] is True
    assert payload["summary"]["machlibFileChanged"] is True


def test_d21_preserves_d20_guardrails():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["negativeControlBlockedBySelector"] is True
    assert payload["summary"]["affineNestedChainParkedBySelector"] is True
    assert payload["summary"]["deeperChainParkedBySelector"] is True


def test_d21_keeps_broad_nested_and_runtime_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["broadNestedSubtractionClaim"] is False
    assert payload["summary"]["broadSubtractionFamilyClaim"] is False
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["runtimeLoweringControl"] == "standard_subtraction_remains_runtime_control"


def test_d21_claim_flags_remain_false():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert payload["summary"]["theoremDiscoveryClaim"] is False
    assert payload["summary"]["publicReady"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_d21_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D21")


def test_d21_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d21_subtraction_boundary_two_stage_chain_witness_attempt.py",
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
    assert "EML_D21_SUBTRACTION_BOUNDARY_TWO_STAGE_CHAIN_WITNESS_ATTEMPT_OK" in proc.stdout
