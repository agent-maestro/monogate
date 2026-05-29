"""Tests for EML-ADV-PCC7 oscillatory holdout."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_advantage_pcc7_oscillatory_holdout import (
    CLAIM_FLAGS,
    SOURCE_PATH,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_pcc7_payload_links_damped_wave_source_family():
    payload = build_payload()
    validate_payload(payload)
    assert SOURCE_PATH.exists()
    assert payload["status"] == "EML_ADV_PCC7_OSCILLATORY_HOLDOUT_PASS"
    assert payload["summary"]["holdoutCount"] == 1
    assert payload["summary"]["sourceFamilyCount"] == 3
    assert "damped_wave" in payload["summary"]["sourceFamilies"]
    packet = payload["holdoutPacket"]
    assert packet["sourceRepo"] == "efrog"
    assert packet["sourcePath"] == "examples/damped_wave.py"
    assert packet["sourceSha256"].startswith("sha256:")


def test_pcc7_profiles_preserve_partial_eml_envelope_agreement():
    packet = build_payload()["holdoutPacket"]
    assert packet["summary"]["profileCount"] == 4
    assert packet["summary"]["passingProfiles"] == 4
    assert packet["summary"]["allProfilesPass"] is True
    assert packet["emlCoverage"] == "exponential_damping_envelope_only"
    assert packet["standardCoverage"] == "sine_oscillation_and_runtime_surface"
    noise_kinds = {profile["noiseKind"] for profile in packet["profiles"]}
    assert {"none", "phase_sweep", "input_perturbation", "output_observation"} <= noise_kinds
    for profile in packet["profiles"]:
        assert profile["winner"] == "partial_eml_envelope_semantic_tie"
        assert profile["emlShapedVsSource"]["pass"] is True
        assert profile["emlShapedVsSource"]["finiteRatio"] == 1.0
        assert profile["emlShapedVsNoisyObservation"]["reportedAsClaim"] is False


def test_pcc7_keeps_standard_runtime_surface_required():
    payload = build_payload()
    assert payload["summary"]["standardRuntimeSurfaceStillRequired"] is True
    assert payload["summary"]["partialEmlCoverage"] == "exponential_damping_envelope_only"
    assert payload["summary"]["runtimePerformanceClaim"] is False
    assert payload["summary"]["oscillatoryGeneralizationClaim"] is False


def test_pcc7_claim_flags_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_payload()
    for key in [
        "broadEmlAdvantageClaim",
        "sourceFamilyGeneralizationClaim",
        "oscillatoryGeneralizationClaim",
        "runtimePerformanceClaim",
        "noiseRobustnessGeneralClaim",
        "predictionAccuracyClaim",
        "publicReady",
    ]:
        assert payload["summary"][key] is False
    assert all(value is False for value in payload["claimFlags"].values())
    assert all(value is False for value in payload["holdoutPacket"]["claimFlags"].values())


def test_pcc7_writes_json_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "packet_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-ADV-PCC7")


def test_pcc7_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_advantage_pcc7_oscillatory_holdout.py",
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
    assert "EML_ADV_PCC7_OSCILLATORY_HOLDOUT_OK" in proc.stdout
