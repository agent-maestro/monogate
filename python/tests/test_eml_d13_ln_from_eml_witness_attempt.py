"""Tests for EML-D13 ln-from-EML witness attempt."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d13_ln_from_eml_witness_attempt import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_d13_consumes_d12_selector_and_checks_ln_witness():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D13_LN_FROM_EML_WITNESS_ATTEMPT_PASS"
    assert payload["sourceSelector"] == "eml-d12-next-identity-witness-selector"
    assert payload["summary"]["selectedCandidateId"] == "ln_from_eml_boundary_v1"
    assert payload["summary"]["selectedWitnessName"] == "MachLib.Real.ln_from_eml_boundary_witness"


def test_d13_records_observed_lake_build_pass():
    payload = build_payload(ATLAS_GATE)
    assert payload["verification"]["command"] == "cd ../machlib/foundations && lake build"
    assert payload["verification"]["observedStatus"] == "pass"
    assert payload["summary"]["leanTypecheckPerformed"] is True
    assert payload["summary"]["lakeBuildPassed"] is True
    assert payload["summary"]["scopedWitnessChecked"] is True


def test_d13_keeps_standard_log_as_runtime_control():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeLoweringControl"] == "standard_log_remains_runtime_control"
    assert "standard log remains the runtime lowering control" in payload["nonClaims"][1]


def test_d13_claim_flags_remain_broadly_false():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["theoremDiscoveryClaim"] is False
    assert payload["summary"]["publicReady"] is False
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_d13_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D13")


def test_d13_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d13_ln_from_eml_witness_attempt.py",
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
    assert "EML_D13_LN_FROM_EML_WITNESS_ATTEMPT_OK" in proc.stdout
