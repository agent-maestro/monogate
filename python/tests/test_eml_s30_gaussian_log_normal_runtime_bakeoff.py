"""Tests for EML-S30 Gaussian/log-normal runtime bakeoff."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import numpy as np

from scripts.eml_s30_gaussian_log_normal_runtime_bakeoff import (
    CLAIM_FLAGS,
    RUNTIME_FORMS,
    build_outputs,
    build_payload,
    packet_for_form,
    profile_specs,
    reference_pdf,
    validate_packet,
    validate_payload,
)


def test_s30_builds_four_runtime_forms():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EML_S30_GAUSSIAN_LOG_NORMAL_RUNTIME_BAKEOFF_PASS"
    assert payload["summary"]["runtimeFormCount"] == 4
    assert {packet["formId"] for packet in payload["runtimePackets"]} == set(RUNTIME_FORMS)


def test_s30_profile_grid_has_gaussian_and_log_normal_stressors():
    specs = profile_specs()
    names = {spec["profile"] for spec in specs}
    families = {spec["family"] for spec in specs}
    assert "central_gaussian_window" in names
    assert "wide_gaussian_tail" in names
    assert "positive_log_normal_window" in names
    assert "extreme_log_normal_tail" in names
    assert families == {"gaussian_pdf", "log_normal_pdf"}


def test_s30_packets_have_five_profiles_two_dtypes():
    for form_id in RUNTIME_FORMS:
        packet = packet_for_form(form_id)
        validate_packet(packet)
        assert packet["summary"]["profileRunCount"] == 10
        assert {profile["dtype"] for profile in packet["profiles"]} == {"float64", "float32"}


def test_s30_reference_is_nonnegative_and_finite():
    for spec in profile_specs():
        ref = reference_pdf(spec, spec["x"])
        assert np.all(np.isfinite(ref))
        assert np.all(ref >= 0.0)


def test_s30_recommends_log_domain_runtime_and_keeps_caution():
    payload = build_payload()
    assert payload["summary"]["recommendedRuntimeForm"] == "log_domain_pdf"
    assert payload["recommendation"]["representationForm"] == "eml_exponential_quadratic_envelope"
    assert payload["recommendation"]["teachingSearchForm"] == "eml_exponential_quadratic_envelope"
    assert payload["recommendation"]["protectedAlternativeForm"] == "standard_pdf"
    assert "clamp_exponent_caution" in payload["recommendation"]["blockedOrCautionForms"]


def test_s30_clamp_records_tail_semantic_drift():
    packet = packet_for_form("clamp_exponent_caution")
    assert packet["summary"]["clampedTailObserved"] is True
    assert packet["summary"]["clampedTailSampleCount"] > 0
    assert packet["summary"]["semanticDriftSampleCount"] > 0


def test_s30_claim_boundaries_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["publicReady"] is False
    assert summary["publicPerformanceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert summary["broadEmlAdvantageClaim"] is False
    assert summary["sourceFamilyGeneralizationClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False


def test_s30_claim_flags_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_payload()
    assert all(value is False for value in payload["claimFlags"].values())
    for packet in payload["runtimePackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_s30_writes_outputs(tmp_path):
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
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-S30")


def test_s30_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_s30_gaussian_log_normal_runtime_bakeoff.py",
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
    assert "EML_S30_GAUSSIAN_LOG_NORMAL_RUNTIME_BAKEOFF_OK" in proc.stdout
