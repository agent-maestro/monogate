"""Tests for EML-ADV-PCC5 second source-family holdout."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_advantage_pcc5_second_source_family_holdout import (
    CLAIM_FLAGS,
    SOURCE_PATH,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_pcc5_payload_links_gaussian_source_family():
    payload = build_payload()
    validate_payload(payload)
    assert SOURCE_PATH.exists()
    assert payload["status"] == "EML_ADV_PCC5_SECOND_SOURCE_FAMILY_HOLDOUT_PASS"
    assert payload["summary"]["holdoutCount"] == 1
    assert payload["summary"]["sourceFamilyCount"] == 2
    assert "gaussian_stable" in payload["summary"]["sourceFamilies"]
    packet = payload["holdoutPacket"]
    assert packet["sourceRepo"] == "efrog"
    assert packet["sourcePath"] == "examples/gaussian_stable.py"
    assert packet["sourceSha256"].startswith("sha256:")


def test_pcc5_profiles_preserve_gaussian_model_agreement():
    packet = build_payload()["holdoutPacket"]
    assert packet["summary"]["profileCount"] == 4
    assert packet["summary"]["passingProfiles"] == 4
    assert packet["summary"]["allProfilesPass"] is True
    noise_kinds = {profile["noiseKind"] for profile in packet["profiles"]}
    assert "input_perturbation" in noise_kinds
    assert "output_observation" in noise_kinds
    assert "input_edge_perturbation" in noise_kinds
    for profile in packet["profiles"]:
        assert profile["winner"] == "semantic_tie_for_second_source_family"
        assert profile["emlShapedVsSource"]["pass"] is True
        assert profile["emlShapedVsSource"]["finiteRatio"] == 1.0
        assert profile["emlShapedVsNoisyObservation"]["reportedAsClaim"] is False


def test_pcc5_output_noise_is_residual_not_prediction_claim():
    packet = build_payload()["holdoutPacket"]
    noisy_profile = next(profile for profile in packet["profiles"] if profile["noiseKind"] == "output_observation")
    assert noisy_profile["emlShapedVsNoisyObservation"]["rmse"] > 0.0
    assert packet["summary"]["predictionAccuracyClaim"] is False
    assert packet["summary"]["sourceFamilyGeneralizationClaim"] is False


def test_pcc5_claim_flags_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_payload()
    for key in [
        "broadEmlAdvantageClaim",
        "sourceFamilyGeneralizationClaim",
        "runtimePerformanceClaim",
        "noiseRobustnessGeneralClaim",
        "predictionAccuracyClaim",
        "publicReady",
    ]:
        assert payload["summary"][key] is False
    assert all(value is False for value in payload["claimFlags"].values())
    assert all(value is False for value in payload["holdoutPacket"]["claimFlags"].values())


def test_pcc5_writes_json_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "packet_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-ADV-PCC5")


def test_pcc5_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_advantage_pcc5_second_source_family_holdout.py",
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
    assert "EML_ADV_PCC5_SECOND_SOURCE_FAMILY_HOLDOUT_OK" in proc.stdout
