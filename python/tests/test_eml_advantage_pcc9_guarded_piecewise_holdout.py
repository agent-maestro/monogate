"""Tests for EML-ADV-PCC9 guarded/piecewise holdout."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_advantage_pcc9_guarded_piecewise_holdout import (
    CLAIM_FLAGS,
    SOURCE_PATH,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_pcc9_payload_links_clamp_guard_source_family():
    payload = build_payload()
    validate_payload(payload)
    assert SOURCE_PATH.exists()
    assert payload["status"] == "EML_ADV_PCC9_GUARDED_PIECEWISE_HOLDOUT_PASS"
    assert payload["summary"]["holdoutCount"] == 1
    assert payload["summary"]["sourceFamilyCount"] == 5
    assert "clamp_guard" in payload["summary"]["sourceFamilies"]
    packet = payload["holdoutPacket"]
    assert packet["sourceRepo"] == "efrog"
    assert packet["sourcePath"] == "examples/clamp_guard.py"
    assert packet["sourceSha256"].startswith("sha256:")


def test_pcc9_valid_profiles_match_guarded_representation():
    packet = build_payload()["holdoutPacket"]
    assert packet["summary"]["profileCount"] == 5
    assert packet["summary"]["validProfileCount"] == 4
    assert packet["summary"]["passingValidProfiles"] == 4
    valid_profiles = [profile for profile in packet["profiles"] if not profile["blocked"]]
    for profile in valid_profiles:
        assert profile["winner"] == "guarded_piecewise_semantic_tie"
        assert profile["guardedVsSource"]["pass"] is True
        assert profile["guardedVsSource"]["maxAbsError"] == 0.0
        counts = profile["transitionCounts"]
        assert counts["lowerClampCount"] + counts["upperClampCount"] + counts["passThroughCount"] >= profile["sampleCount"]


def test_pcc9_invalid_bounds_are_blocked():
    packet = build_payload()["holdoutPacket"]
    invalid = next(profile for profile in packet["profiles"] if profile["noiseKind"] == "invalid_bounds")
    assert invalid["blocked"] is True
    assert invalid["validBounds"] is False
    assert invalid["winner"] == "blocked_invalid_guard_domain"
    assert invalid["blockReason"] == "lo_must_be_less_than_or_equal_to_hi"
    assert packet["summary"]["invalidBoundsBlockedProfiles"] == 1


def test_pcc9_claim_flags_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_payload()
    for key in [
        "broadEmlAdvantageClaim",
        "sourceFamilyGeneralizationClaim",
        "guardSemanticsGeneralizationClaim",
        "branchCorrectnessClaim",
        "protectedLoweringCorrectnessClaim",
        "runtimePerformanceClaim",
        "noiseRobustnessGeneralClaim",
        "predictionAccuracyClaim",
        "publicReady",
    ]:
        assert payload["summary"][key] is False
    assert all(value is False for value in payload["claimFlags"].values())
    assert all(value is False for value in payload["holdoutPacket"]["claimFlags"].values())


def test_pcc9_writes_json_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "packet_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-ADV-PCC9")


def test_pcc9_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_advantage_pcc9_guarded_piecewise_holdout.py",
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
    assert "EML_ADV_PCC9_GUARDED_PIECEWISE_HOLDOUT_OK" in proc.stdout
