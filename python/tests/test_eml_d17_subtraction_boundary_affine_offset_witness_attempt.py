"""Tests for EML-D17 subtraction-boundary affine-offset witness attempt."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d17_subtraction_boundary_affine_offset_witness_attempt import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_d17_consumes_d16_selector_and_checks_affine_offset_witness():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D17_SUBTRACTION_BOUNDARY_AFFINE_OFFSET_WITNESS_ATTEMPT_PASS"
    assert payload["sourceSelector"] == "eml-d16-subtraction-boundary-family-selector"
    assert payload["summary"]["selectedStatementId"] == "subtraction_boundary_affine_offset_family_v1"
    assert payload["summary"]["selectedWitnessName"] == "MachLib.Real.subtraction_boundary_affine_offset_witness"
    assert payload["selectedWitness"]["statement"] == "eml (log (x + y)) (exp y) = x under 0 < x + y"


def test_d17_records_observed_lake_build_pass():
    payload = build_payload(ATLAS_GATE)
    assert payload["verification"]["command"] == "cd ../machlib/foundations && lake build"
    assert payload["verification"]["observedStatus"] == "pass"
    assert payload["summary"]["leanTypecheckPerformed"] is True
    assert payload["summary"]["lakeBuildPassed"] is True
    assert payload["summary"]["scopedWitnessChecked"] is True


def test_d17_preserves_d16_guardrails():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["duplicateBaseRejectedBySelector"] is True
    assert payload["summary"]["negativeControlBlockedBySelector"] is True


def test_d17_keeps_standard_subtraction_as_runtime_control():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeLoweringControl"] == "standard_subtraction_remains_runtime_control"
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert "standard subtraction remains the runtime lowering control" in payload["nonClaims"][1]


def test_d17_claim_flags_remain_broadly_false():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["theoremDiscoveryClaim"] is False
    assert payload["summary"]["publicReady"] is False
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_d17_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D17")


def test_d17_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d17_subtraction_boundary_affine_offset_witness_attempt.py",
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
    assert "EML_D17_SUBTRACTION_BOUNDARY_AFFINE_OFFSET_WITNESS_ATTEMPT_OK" in proc.stdout
