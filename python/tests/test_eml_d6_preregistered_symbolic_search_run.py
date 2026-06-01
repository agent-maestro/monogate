"""Tests for EML-D6 preregistered symbolic-search run."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d6_preregistered_symbolic_search_run import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def packets_for(payload, dataset_id: str, grammar_id: str):
    return [
        packet
        for packet in payload["runPackets"]
        if packet["datasetId"] == dataset_id and packet["grammarId"] == grammar_id
    ]


def control_by_id(payload, control_id: str):
    return next(item for item in payload["negativeControlOutcomes"] if item["controlId"] == control_id)


def test_d6_runs_preregistered_search_and_defers_interpretation():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EML_D6_PREREGISTERED_SYMBOLIC_SEARCH_RUN_PASS"
    assert payload["sourcePreregistration"] == "eml-d5-symbolic-search-preregistration"
    assert payload["summary"]["experimentRunPerformed"] is True
    assert payload["summary"]["d5CriteriaPreserved"] is True
    assert payload["summary"]["d7InterpretationRequired"] is True


def test_d6_records_all_target_grammar_split_packets():
    payload = build_payload()
    assert payload["summary"]["runPacketCount"] == 18
    assert payload["summary"]["psiRunPacketCount"] == 9
    assert payload["summary"]["dampedRunPacketCount"] == 9
    assert len(packets_for(payload, "psi_residual", "eml_native_guarded_v1")) == 3
    assert len(packets_for(payload, "psi_residual", "standard_exp_log_trig_v1")) == 3
    assert len(packets_for(payload, "damped_oscillator", "wrong_exponent_eml_control_v1")) == 3


def test_d6_reports_mse_complexity_and_expressions():
    payload = build_payload()
    for packet in payload["runPackets"]:
        assert packet["bestComplexity"] > 0
        assert packet["metrics"]["trainMse"] >= 0.0
        assert packet["metrics"]["holdoutMse"] >= 0.0
        assert packet["metrics"]["bestExpression"]


def test_d6_psi_packets_report_localization_metrics():
    payload = build_payload()
    for packet in packets_for(payload, "psi_residual", "eml_native_guarded_v1"):
        assert "bestGamma" in packet["metrics"]
        assert "errorFromFirstKnownZero" in packet["metrics"]


def test_d6_negative_controls_are_present_and_blocking_until_d7():
    payload = build_payload()
    assert payload["summary"]["negativeControlOutcomeCount"] == 5
    assert control_by_id(payload, "wrong_exponent_two_zero_v0")["blocksPositiveInterpretationUntilD7"] is True
    assert control_by_id(payload, "shuffled_residual_control_v1")["blocksPositiveInterpretationUntilD7"] is True
    assert control_by_id(payload, "ordinary_polynomial_failure_v0")["status"] == "satisfied_by_d4_failure_atlas"


def test_d6_claim_flags_remain_false():
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
    for packet in payload["runPackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_d6_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D6")


def test_d6_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d6_preregistered_symbolic_search_run.py",
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
    assert "EML_D6_PREREGISTERED_SYMBOLIC_SEARCH_RUN_OK" in proc.stdout
