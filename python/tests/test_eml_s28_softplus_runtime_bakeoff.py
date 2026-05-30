"""Tests for EML-S28 softplus runtime bakeoff."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import numpy as np

from scripts.eml_s28_softplus_runtime_bakeoff import (
    CLAIM_FLAGS,
    RUNTIME_FORMS,
    build_outputs,
    build_payload,
    packet_for_form,
    profile_specs,
    reference_softplus,
    validate_packet,
    validate_payload,
)


def test_s28_builds_four_runtime_forms():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EML_S28_SOFTPLUS_RUNTIME_BAKEOFF_PASS"
    assert payload["summary"]["runtimeFormCount"] == 4
    assert {packet["formId"] for packet in payload["runtimePackets"]} == set(RUNTIME_FORMS)


def test_s28_profile_grid_has_expected_stressors():
    names = {spec["profile"] for spec in profile_specs()}
    assert "transition_window" in names
    assert "safe_float_range" in names
    assert "noisy_transition_inputs" in names
    assert "extreme_overflow_boundary" in names


def test_s28_packets_have_four_profiles_two_dtypes():
    for form_id in RUNTIME_FORMS:
        packet = packet_for_form(form_id)
        validate_packet(packet)
        assert packet["summary"]["profileRunCount"] == 8
        assert {profile["dtype"] for profile in packet["profiles"]} == {"float64", "float32"}


def test_s28_reference_is_nonnegative_and_finite():
    for spec in profile_specs():
        ref = reference_softplus(spec["x"])
        assert np.all(np.isfinite(ref))
        assert np.all(ref >= 0.0)


def test_s28_recommends_logaddexp_runtime_and_keeps_cautions():
    payload = build_payload()
    assert payload["summary"]["recommendedRuntimeForm"] == "logaddexp_softplus"
    assert payload["recommendation"]["representationForm"] == "softplus_logsumexp"
    assert payload["recommendation"]["teachingSearchForm"] == "naive_softplus"
    assert payload["recommendation"]["protectedAlternativeForm"] == "branch_stable_softplus"
    assert "naive_softplus" in payload["recommendation"]["blockedOrCautionForms"]
    assert "clamp60_softplus_caution" in payload["recommendation"]["blockedOrCautionForms"]


def test_s28_naive_records_dangerous_exponents():
    packet = packet_for_form("naive_softplus")
    assert packet["summary"]["dangerousExponentInputObserved"] is True
    assert packet["summary"]["dangerousExponentInputCount"] > 0


def test_s28_claim_boundaries_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["publicReady"] is False
    assert summary["publicPerformanceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert summary["broadEmlAdvantageClaim"] is False
    assert summary["sourceFamilyGeneralizationClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False


def test_s28_claim_flags_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_payload()
    assert all(value is False for value in payload["claimFlags"].values())
    for packet in payload["runtimePackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_s28_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    packet_paths = sorted((tmp_path / "packets").glob("*.json"))
    assert len(packet_paths) == 4
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-S28")


def test_s28_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_s28_softplus_runtime_bakeoff.py",
            "--build",
            "--out-dir",
            str(tmp_path / "results"),
            "--packet-dir",
            str(tmp_path / "packets"),
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
    assert "EML_S28_SOFTPLUS_RUNTIME_BAKEOFF_OK" in proc.stdout
