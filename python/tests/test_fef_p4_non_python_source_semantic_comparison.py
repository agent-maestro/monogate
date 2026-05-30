"""Tests for FEF-P4 non-Python source semantic comparison."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p4_non_python_source_semantic_comparison import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p4_records_non_python_source_comparisons():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "FEF_P4_NON_PYTHON_SOURCE_SEMANTIC_COMPARISON_PASS"
    assert payload["summary"]["sourceLanguages"] == ["javascript"]
    assert payload["summary"]["caseCount"] == 3
    assert payload["summary"]["passCount"] == 3


def test_fef_p4_compares_original_javascript_to_forge_targets():
    payload = build_payload()
    assert payload["summary"]["targetLanguages"] == ["python", "javascript"]
    assert payload["summary"]["sampleCount"] == 14
    for packet in payload["casePackets"]:
        assert packet["sourceLanguage"] == "javascript"
        assert packet["targetLanguages"] == ["python", "javascript"]
        assert packet["comparisonStatus"] == "pass"
        assert packet["maxAbsError"] <= 1e-9 or packet["maxRelError"] <= 1e-9
        frame = packet["frames"][0]
        assert set(frame["values"]) == {
            "originalJavaScript",
            "forgePython",
            "forgeJavaScript",
        }


def test_fef_p4_claim_flags_remain_false():
    payload = build_payload()
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in payload["claimFlags"].values())
    for packet in payload["casePackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_fef_p4_writes_outputs(tmp_path):
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
    assert len(packets) == 3
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P4")


def test_fef_p4_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p4_non_python_source_semantic_comparison.py",
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
    assert "FEF_P4_NON_PYTHON_SOURCE_SEMANTIC_COMPARISON_OK" in proc.stdout
