"""Tests for EML-S21 native holdout."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import numpy as np

from scripts.eml_s21_native_holdout import (
    CLAIM_FLAGS,
    build_holdout_packet,
    build_outputs,
    build_payload,
    eml_stretched_exponential,
    profile_specs,
    standard_stretched_exponential,
    validate_packet,
    validate_payload,
)


def test_s21_builds_payload_from_eml_native_lane():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EML_S21_NATIVE_HOLDOUT_PASS"
    assert payload["selectedStyleLane"] == "eml_native"
    assert payload["summary"]["s20NativePrimaryCount"] >= 2


def test_s21_holdout_packet_profiles_pass():
    packet = build_holdout_packet()
    validate_packet(packet)
    assert packet["sourceFamily"] == "stretched_exponential"
    assert packet["summary"]["profileCount"] == 4
    assert packet["summary"]["passingProfiles"] == 4
    assert packet["summary"]["emlNativeSemanticTie"] is True


def test_s21_standard_and_eml_forms_match_on_profiles():
    for spec in profile_specs():
        standard = standard_stretched_exponential(
            spec["amplitude"],
            spec["scale"],
            spec["shape"],
            spec["t"],
        )
        eml = eml_stretched_exponential(
            spec["amplitude"],
            spec["scale"],
            spec["shape"],
            spec["t"],
        )
        np.testing.assert_allclose(eml, standard, rtol=1.0e-12, atol=1.0e-12)


def test_s21_profiles_cover_domain_stressors():
    packet = build_holdout_packet()
    profile_names = {profile["profile"] for profile in packet["profiles"]}
    assert "noisy_input_stretched_exponential_grid" in profile_names
    assert "long_tail_stretched_exponential_grid" in profile_names
    assert "shape_sweep_stretched_exponential_grid" in profile_names
    for profile in packet["profiles"]:
        assert "scale > 0" in profile["domainRequirements"]
        assert "shape > 0" in profile["domainRequirements"]


def test_s21_claim_boundaries_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["publicReady"] is False
    assert summary["broadEmlAdvantageClaim"] is False
    assert summary["emlNativeGeneralizationClaim"] is False
    assert summary["sourceFamilyGeneralizationClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False


def test_s21_claim_flags_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_payload()
    assert all(value is False for value in payload["claimFlags"].values())
    assert all(value is False for value in payload["holdoutPacket"]["claimFlags"].values())


def test_s21_is_deterministic():
    first = build_payload()
    second = build_payload()
    assert first["summary"] == second["summary"]
    assert first["holdoutPacket"]["profiles"] == second["holdoutPacket"]["profiles"]


def test_s21_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-S21")


def test_s21_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_s21_native_holdout.py",
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
    assert "EML_S21_NATIVE_HOLDOUT_OK" in proc.stdout
