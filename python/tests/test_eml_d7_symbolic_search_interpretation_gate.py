"""Tests for EML-D7 symbolic-search interpretation gate."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d7_symbolic_search_interpretation_gate import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def criterion_by_id(payload, criterion_id: str):
    return next(item for item in payload["criterionResults"] if item["criterionId"] == criterion_id)


def test_d7_interprets_d6_against_d5_without_threshold_changes():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EML_D7_SYMBOLIC_SEARCH_INTERPRETATION_GATE_PASS"
    assert payload["sourcePreregistration"] == "eml-d5-symbolic-search-preregistration"
    assert payload["sourceRun"] == "eml-d6-preregistered-symbolic-search-run"
    assert payload["summary"]["thresholdsChanged"] is False
    assert payload["summary"]["d5CriteriaPreserved"] is True
    assert payload["summary"]["d6RunInterpreted"] is True


def test_d7_assigns_no_replicated_holdout_gain_label():
    payload = build_payload()
    assert payload["summary"]["interpretationLabel"] == "no_replicated_holdout_gain"
    assert payload["interpretation"]["label"] == "no_replicated_holdout_gain"
    assert payload["summary"]["positiveInterpretationAllowed"] is False
    assert "holdout_mse_improvement_replicated" in payload["interpretation"]["failedCriterionIds"]


def test_d7_records_failed_and_passed_criteria():
    payload = build_payload()
    assert payload["summary"]["criterionCount"] == 6
    assert payload["summary"]["failedCriterionCount"] >= 3
    assert criterion_by_id(payload, "holdout_mse_improvement_replicated")["passed"] is False
    assert criterion_by_id(payload, "complexity_not_higher")["passed"] is False
    assert criterion_by_id(payload, "negative_controls_do_not_promote_eml")["passed"] is False
    assert criterion_by_id(payload, "wrong_exponent_control_not_better")["passed"] is True
    assert criterion_by_id(payload, "protected_runtime_controls_respected")["passed"] is True
    assert criterion_by_id(payload, "localization_and_mse_both_reported")["passed"] is True


def test_d7_observed_rows_explain_holdout_failure():
    payload = build_payload()
    criterion = criterion_by_id(payload, "holdout_mse_improvement_replicated")
    rows = criterion["observed"]["rows"]
    assert len(rows) == 3
    assert any(row["passed"] is False for row in rows)
    assert all("requiredMaxMse" in row for row in rows)


def test_d7_claim_flags_remain_false():
    payload = build_payload()
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["emlAdvantageProved"] is False
    assert payload["summary"]["rhProofClaim"] is False
    assert payload["summary"]["zetaZeroDiscoveryClaim"] is False
    assert payload["summary"]["runtimePerformanceClaim"] is False
    assert payload["summary"]["publicReady"] is False
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_d7_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D7")


def test_d7_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d7_symbolic_search_interpretation_gate.py",
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
    assert "EML_D7_SYMBOLIC_SEARCH_INTERPRETATION_GATE_OK" in proc.stdout
