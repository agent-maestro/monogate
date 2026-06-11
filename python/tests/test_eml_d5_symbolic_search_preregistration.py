"""Tests for EML-D5 symbolic-search preregistration."""

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

from scripts.eml_d5_symbolic_search_preregistration import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def criterion_by_id(payload, criterion_id: str):
    return next(item for item in payload["successCriteria"] if item["criterionId"] == criterion_id)


def control_by_id(payload, control_id: str):
    return next(item for item in payload["negativeControls"] if item["controlId"] == control_id)


def test_d5_records_preregistration_without_running_experiment():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EML_D5_SYMBOLIC_SEARCH_PREREGISTRATION_PASS"
    assert payload["summary"]["preregistrationRecorded"] is True
    assert payload["summary"]["experimentRunPerformed"] is False
    assert payload["experimentPlan"]["runPerformed"] is False
    assert payload["sourceHoldoutTrial"] == "eml-d3-discovery-holdout-search-trials"
    assert payload["sourceFailureAtlas"] == "eml-d4-discovery-failure-atlas"


def test_d5_targets_psi_and_damped_oscillator():
    payload = build_payload()
    targets = payload["experimentPlan"]["targetCandidates"]
    assert "psi_residual_two_zero_holdout_v1" in targets
    assert "damped_oscillator_eml_phase_v0" in targets
    assert payload["experimentPlan"]["primaryTarget"]["interpretationBeforeRun"] == "ambiguous_requires_preregistered_a6_1"


def test_d5_success_criteria_are_required_and_specific():
    payload = build_payload()
    assert payload["summary"]["successCriteriaCount"] >= 6
    assert payload["summary"]["requiredSuccessCriteriaCount"] == payload["summary"]["successCriteriaCount"]
    assert criterion_by_id(payload, "holdout_mse_improvement_replicated")
    assert criterion_by_id(payload, "wrong_exponent_control_not_better")
    assert criterion_by_id(payload, "protected_runtime_controls_respected")
    assert criterion_by_id(payload, "localization_and_mse_both_reported")


def test_d5_negative_controls_include_failure_atlas_and_wrong_exponent():
    payload = build_payload()
    assert payload["summary"]["negativeControlCount"] >= 5
    assert control_by_id(payload, "wrong_exponent_two_zero_v0")
    assert control_by_id(payload, "ordinary_polynomial_failure_v0")
    assert control_by_id(payload, "expm1_logaddexp_runtime_controls_v1")


def test_d5_null_result_policy_blocks_posthoc_reinterpretation():
    payload = build_payload()
    policy = payload["nullResultPolicy"]
    assert policy["nullResultAccepted"] is True
    assert "ambiguous_control_failure" in policy["nullLabels"]
    assert "changing success thresholds after seeing results" in policy["forbiddenPostHocMoves"]
    assert "turning localization-only wins into theorem or zeta claims" in policy["forbiddenPostHocMoves"]


def test_d5_claim_flags_remain_false():
    payload = build_payload()
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["emlAdvantageProved"] is False
    assert payload["summary"]["publicReady"] is False
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_d5_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D5")


def test_d5_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d5_symbolic_search_preregistration.py",
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
    assert "EML_D5_SYMBOLIC_SEARCH_PREREGISTRATION_OK" in proc.stdout
