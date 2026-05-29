"""Tests for EML-ADV-PCC8 log-domain holdout."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_advantage_pcc8_log_domain_holdout import (
    CLAIM_FLAGS,
    SOURCE_PATH,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_pcc8_payload_links_numpy_softplus_source_family():
    payload = build_payload()
    validate_payload(payload)
    assert SOURCE_PATH.exists()
    assert payload["status"] == "EML_ADV_PCC8_LOG_DOMAIN_HOLDOUT_PASS"
    assert payload["summary"]["holdoutCount"] == 1
    assert payload["summary"]["sourceFamilyCount"] == 4
    assert "numpy_softplus" in payload["summary"]["sourceFamilies"]
    packet = payload["holdoutPacket"]
    assert packet["sourceRepo"] == "efrog"
    assert packet["sourcePath"] == "examples/numpy_softplus.py"
    assert packet["sourceSha256"].startswith("sha256:")


def test_pcc8_separates_safe_semantic_tie_from_protected_lowering():
    packet = build_payload()["holdoutPacket"]
    assert packet["summary"]["profileCount"] == 5
    assert packet["summary"]["safeSemanticTieProfiles"] >= 3
    assert packet["summary"]["protectedLoweringRecommendedProfiles"] >= 1
    assert packet["summary"]["allProtectedProfilesFinite"] is True
    overflow = next(profile for profile in packet["profiles"] if profile["noiseKind"] == "overflow_guard")
    assert overflow["protectedLoweringRecommended"] is True
    assert overflow["winner"] == "protected_lowering_required"
    assert overflow["protectedFinite"]["finiteRatio"] == 1.0
    assert overflow["sourceFinite"]["finiteRatio"] < 1.0


def test_pcc8_noisy_output_is_residual_not_prediction_claim():
    packet = build_payload()["holdoutPacket"]
    noisy = next(profile for profile in packet["profiles"] if profile["noiseKind"] == "output_observation")
    assert noisy["protectedVsNoisyObservation"]["rmse"] > 0.0
    assert noisy["protectedVsNoisyObservation"]["reportedAsClaim"] is False
    assert packet["summary"]["predictionAccuracyClaim"] is False


def test_pcc8_claim_flags_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_payload()
    for key in [
        "broadEmlAdvantageClaim",
        "sourceFamilyGeneralizationClaim",
        "logDomainGeneralizationClaim",
        "protectedLoweringCorrectnessClaim",
        "runtimePerformanceClaim",
        "noiseRobustnessGeneralClaim",
        "predictionAccuracyClaim",
        "publicReady",
    ]:
        assert payload["summary"][key] is False
    assert all(value is False for value in payload["claimFlags"].values())
    assert all(value is False for value in payload["holdoutPacket"]["claimFlags"].values())


def test_pcc8_writes_json_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "packet_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-ADV-PCC8")


def test_pcc8_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_advantage_pcc8_log_domain_holdout.py",
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
    assert "EML_ADV_PCC8_LOG_DOMAIN_HOLDOUT_OK" in proc.stdout
