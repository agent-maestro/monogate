"""Tests for EML-S24 sigmoid runtime bakeoff."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import numpy as np

from scripts.eml_s24_sigmoid_runtime_bakeoff import (
    CLAIM_FLAGS,
    RUNTIME_FORMS,
    build_outputs,
    build_payload,
    packet_for_form,
    profile_specs,
    reference_sigmoid,
    validate_packet,
    validate_payload,
)


def test_s24_builds_four_runtime_forms():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EML_S24_SIGMOID_RUNTIME_BAKEOFF_PASS"
    assert payload["summary"]["runtimeFormCount"] == 4
    assert {packet["formId"] for packet in payload["runtimePackets"]} == set(RUNTIME_FORMS)


def test_s24_profile_grid_has_expected_stressors():
    names = {spec["profile"] for spec in profile_specs()}
    assert "transition_window" in names
    assert "safe_float_range" in names
    assert "noisy_transition_inputs" in names
    assert "extreme_overflow_boundary" in names


def test_s24_packets_have_four_profiles_two_dtypes():
    for form_id in RUNTIME_FORMS:
        packet = packet_for_form(form_id)
        validate_packet(packet)
        assert packet["summary"]["profileRunCount"] == 8
        assert {profile["dtype"] for profile in packet["profiles"]} == {"float64", "float32"}


def test_s24_reference_is_bounded_and_finite():
    for spec in profile_specs():
        ref = reference_sigmoid(spec["x"])
        assert np.all(np.isfinite(ref))
        assert np.all(ref >= 0.0)
        assert np.all(ref <= 1.0)


def test_s24_recommends_protected_or_branch_stable_runtime():
    payload = build_payload()
    assert payload["summary"]["recommendedRuntimeForm"] in {
        "branch_stable_sigmoid",
        "logaddexp_protected_sigmoid",
    }
    assert payload["recommendation"]["representationForm"] == "clamp_stable_sigmoid"
    assert payload["recommendation"]["teachingSearchForm"] == "naive_sigmoid"
    assert "naive_sigmoid" in payload["recommendation"]["blockedOrCautionForms"]


def test_s24_claim_boundaries_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["publicReady"] is False
    assert summary["publicPerformanceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert summary["broadEmlAdvantageClaim"] is False
    assert summary["sourceFamilyGeneralizationClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False


def test_s24_claim_flags_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_payload()
    assert all(value is False for value in payload["claimFlags"].values())
    for packet in payload["runtimePackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_s24_writes_outputs(tmp_path):
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
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-S24")


def test_s24_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_s24_sigmoid_runtime_bakeoff.py",
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
    assert "EML_S24_SIGMOID_RUNTIME_BAKEOFF_OK" in proc.stdout
