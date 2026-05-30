"""Tests for FEF-P10 broader generated-target re-ingest."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p10_broader_generated_target_reingest import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p10_records_broader_reingest_family():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "FEF_P10_BROADER_GENERATED_TARGET_REINGEST_PASS"
    assert payload["summary"]["caseCount"] == 9
    assert payload["summary"]["packetCount"] == 18
    assert payload["summary"]["passCount"] == 18


def test_fef_p10_covers_expected_source_and_target_languages():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["sourceLanguages"] == ["c", "javascript", "python", "rust"]
    assert summary["generatedTargetLanguages"] == ["javascript", "python"]
    assert summary["recompiledTargetLanguages"] == ["python"]
    assert summary["sampleCount"] == 58


def test_fef_p10_packets_compare_generated_to_reingested_outputs():
    payload = build_payload()
    for packet in payload["reingestPackets"]:
        assert packet["generatedTargetLanguage"] in {"python", "javascript"}
        assert packet["recompiledTargetLanguage"] == "python"
        assert packet["reingestStatus"] == "pass"
        assert packet["reingestedFunctionCount"] == 1
        assert packet["maxAbsError"] <= 1e-9 or packet["maxRelError"] <= 1e-9
        assert set(packet["frames"][0]["values"]) == {
            "generatedTarget",
            "reingestedRecompiledPython",
        }


def test_fef_p10_claim_flags_remain_false():
    payload = build_payload()
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in payload["claimFlags"].values())
    for packet in payload["reingestPackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_fef_p10_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    packets = sorted((tmp_path / "packets").glob("*.json"))
    assert len(packets) == 18
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P10")


def test_fef_p10_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p10_broader_generated_target_reingest.py",
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
    assert "FEF_P10_BROADER_GENERATED_TARGET_REINGEST_OK" in proc.stdout
