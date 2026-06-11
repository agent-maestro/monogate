"""Tests for EML-D10 MachLib identity witness attempt."""

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

from scripts.eml_d10_machlib_identity_witness_attempt import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_d10_consumes_d9_selector_and_checks_constants_witness():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EML_D10_MACHLIB_IDENTITY_WITNESS_ATTEMPT_PASS"
    assert payload["sourceSelector"] == "eml-d9-machlib-identity-witness-selector"
    assert payload["summary"]["selectedCandidateId"] == "constants_zero_one_e_boundary_v0"
    assert payload["summary"]["selectedWitnessName"] == "MachLib.Real.constants_zero_one_e_boundary_witness"


def test_d10_records_supporting_machlib_lemmas():
    payload = build_payload()
    names = {item["name"] for item in payload["supportingLemmas"]}
    assert names == {"eml_zero_exp_one_zero", "eml_zero_one_one", "eml_one_one_exp_one"}
    assert payload["summary"]["supportingLemmaCount"] == 3
    assert payload["summary"]["supportingLemmasPresent"] == 3
    assert all(item["present"] is True for item in payload["supportingLemmas"])


def test_d10_records_observed_lake_build_pass():
    payload = build_payload()
    assert payload["verification"]["command"] == "cd ../machlib/foundations && lake build"
    assert payload["verification"]["observedStatus"] == "pass"
    assert payload["summary"]["leanTypecheckPerformed"] is True
    assert payload["summary"]["lakeBuildPassed"] is True
    assert payload["summary"]["scopedWitnessChecked"] is True


def test_d10_claim_flags_remain_broadly_false():
    payload = build_payload()
    assert payload["summary"]["theoremDiscoveryClaim"] is False
    assert payload["summary"]["publicReady"] is False
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_d10_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D10")


def test_d10_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d10_machlib_identity_witness_attempt.py",
            "--build",
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
    assert "EML_D10_MACHLIB_IDENTITY_WITNESS_ATTEMPT_OK" in proc.stdout
