"""Tests for EML-ADV-PCC4 noisy real-source holdout."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_advantage_pcc4_noisy_real_source_holdout import (
    CLAIM_FLAGS,
    SOURCE_PATH,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_pcc4_payload_links_noisy_rc_decay_source():
    payload = build_payload()
    validate_payload(payload)
    assert SOURCE_PATH.exists()
    assert payload["status"] == "EML_ADV_PCC4_NOISY_REAL_SOURCE_HOLDOUT_PASS"
    assert payload["summary"]["holdoutCount"] == 1
    assert payload["summary"]["sourceLinked"] is True
    assert payload["summary"]["noisyOutputProfileCount"] == 1
    packet = payload["holdoutPacket"]
    assert packet["sourceRepo"] == "efrog"
    assert packet["sourcePath"] == "examples/rc_decay_stable.py"
    assert packet["sourceSha256"].startswith("sha256:")


def test_pcc4_profiles_preserve_model_agreement_under_noise():
    payload = build_payload()
    packet = payload["holdoutPacket"]
    assert packet["summary"]["profileCount"] == 4
    assert packet["summary"]["passingProfiles"] == 4
    assert packet["summary"]["allProfilesPass"] is True
    noise_kinds = {profile["noiseKind"] for profile in packet["profiles"]}
    assert "input_perturbation" in noise_kinds
    assert "output_observation" in noise_kinds
    for profile in packet["profiles"]:
        assert profile["winner"] == "semantic_tie_under_noise"
        assert profile["emlShapedVsSource"]["pass"] is True
        assert profile["emlShapedVsSource"]["finiteRatio"] == 1.0
        assert profile["emlShapedVsNoisyObservation"]["reportedAsClaim"] is False


def test_pcc4_output_noise_is_residual_not_prediction_claim():
    packet = build_payload()["holdoutPacket"]
    noisy_profile = next(profile for profile in packet["profiles"] if profile["noiseKind"] == "output_observation")
    assert noisy_profile["emlShapedVsNoisyObservation"]["rmse"] > 0.0
    assert packet["summary"]["predictionAccuracyClaim"] is False
    assert packet["summary"]["noiseRobustnessGeneralClaim"] is False


def test_pcc4_claim_flags_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_payload()
    for key in [
        "broadEmlAdvantageClaim",
        "runtimePerformanceClaim",
        "noiseRobustnessGeneralClaim",
        "predictionAccuracyClaim",
        "publicReady",
    ]:
        assert payload["summary"][key] is False
    assert all(value is False for value in payload["claimFlags"].values())
    assert all(value is False for value in payload["holdoutPacket"]["claimFlags"].values())


def test_pcc4_writes_json_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "packet_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-ADV-PCC4")


def test_pcc4_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_advantage_pcc4_noisy_real_source_holdout.py",
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
    assert "EML_ADV_PCC4_NOISY_REAL_SOURCE_HOLDOUT_OK" in proc.stdout
