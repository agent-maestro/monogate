"""Tests for EML-A13 Forge/eFrog roundtrip advantage lab."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_a13_forge_efrog_roundtrip_advantage import (
    CLAIM_FLAGS,
    build_lab,
    validate_payload,
)


def build_tmp(tmp_path):
    return build_lab(
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )


def test_a13_builds_roundtrip_packets_for_many_frontends(tmp_path):
    built = build_tmp(tmp_path)
    payload = built["payload"]
    assert payload["status"] == "EML_A13_FORGE_EFROG_ROUNDTRIP_ADVANTAGE_PASS"
    assert payload["summary"]["caseCount"] >= 30
    assert payload["summary"]["roundtripPassCount"] >= 30 or payload["summary"]["allRoundtripsBlockedByExpiredLicense"] is True
    assert payload["summary"]["holdoutCaseCount"] >= 12
    assert payload["summary"]["targetLanguages"] == ["javascript", "python"]
    validate_payload(payload)


def test_a13_packets_have_hashes_and_shape_identity(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    for packet in payload["casePackets"]:
        assert packet["canonicalEmlHash"].startswith("sha256:")
        assert packet["normalizedShapeHash"]
        assert packet["canonicalEmlBytes"] > 0
        assert packet["functionCount"] >= 1
        assert packet["roundtripStatus"] == "pass" or packet["licenseBlocked"] is True
        assert packet["targetLanguage"] in {"python", "javascript"}


def test_a13_has_holdout_and_default_frontend_slices(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    source_classes = {packet["sourceClass"] for packet in payload["casePackets"]}
    assert source_classes == {"default_frontend", "holdout"}
    holdout_packets = [packet for packet in payload["casePackets"] if packet["sourceClass"] == "holdout"]
    assert {packet["targetLanguage"] for packet in holdout_packets} == {"python", "javascript"}
    assert "python_holdout_stretched_exponential" in {
        packet["sourceLanguage"] for packet in holdout_packets
    }
    assert "python_holdout_stable_sigmoid" in {
        packet["sourceLanguage"] for packet in holdout_packets
    }


def test_a13_classification_is_bounded_not_triumphal(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    classes = {packet["advantageClass"] for packet in payload["casePackets"]}
    assert classes <= {
        "eml_toolchain_surface_win",
        "roundtrip_pass_standard_surface_smaller",
        "roundtrip_blocked",
    }
    assert payload["summary"]["broadEmlAdvantageClaim"] is False
    assert payload["summary"]["compilerCorrectnessClaim"] is False


def test_a13_claim_flags_remain_false(tmp_path):
    built = build_tmp(tmp_path)
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in built["payload"]["claimFlags"].values())
    assert all(value is False for value in built["evidence"]["claimFlags"].values())
    for packet in built["payload"]["casePackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_a13_generated_json_files_parse(tmp_path):
    built = build_tmp(tmp_path)
    paths = [built["result_path"], built["evidence_path"], built["feed_path"]]
    paths.extend(str(path) for path in (tmp_path / "packets").glob("*.json"))
    assert len(paths) >= 35
    for path in paths:
        json.loads(Path(path).read_text(encoding="utf-8"))


def test_a13_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_a13_forge_efrog_roundtrip_advantage.py",
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
    assert "EML_A13_FORGE_EFROG_ROUNDTRIP_ADVANTAGE_OK" in proc.stdout
