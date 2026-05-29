"""Tests for EML-A13.2 semantic output comparison."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_a13_2_semantic_output_comparison import (
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


def test_a13_2_builds_semantic_comparison_packets(tmp_path):
    built = build_tmp(tmp_path)
    payload = built["payload"]
    assert payload["status"] == "EML_A13_2_SEMANTIC_OUTPUT_COMPARISON_PASS"
    assert payload["summary"]["caseCount"] >= 6
    assert payload["summary"]["passCount"] == payload["summary"]["caseCount"]
    assert payload["summary"]["sampleCount"] >= 20
    validate_payload(payload)


def test_a13_2_compares_python_and_javascript_targets(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    assert payload["summary"]["targetLanguages"] == ["python", "javascript"]
    for packet in payload["casePackets"]:
        assert packet["targetLanguages"] == ["python", "javascript"]
        assert packet["comparisonStatus"] == "pass"
        assert packet["maxAbsError"] <= 1.0e-9 or packet["maxRelError"] <= 1.0e-9


def test_a13_2_frames_include_three_values_and_errors(tmp_path):
    packet = build_tmp(tmp_path)["payload"]["casePackets"][0]
    frame = packet["frames"][0]
    assert set(frame["values"]) == {"original", "forgePython", "forgeJavaScript"}
    assert "javascriptVsPython" in frame["absErrors"]
    assert frame["withinTolerance"] is True


def test_a13_2_claim_flags_remain_false(tmp_path):
    built = build_tmp(tmp_path)
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in built["payload"]["claimFlags"].values())
    assert all(value is False for value in built["evidence"]["claimFlags"].values())
    for packet in built["payload"]["casePackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_a13_2_generated_json_files_parse(tmp_path):
    built = build_tmp(tmp_path)
    paths = [built["result_path"], built["evidence_path"], built["feed_path"]]
    paths.extend(str(path) for path in (tmp_path / "packets").glob("*.json"))
    assert len(paths) >= 9
    for path in paths:
        json.loads(Path(path).read_text(encoding="utf-8"))


def test_a13_2_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_a13_2_semantic_output_comparison.py",
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
    assert "EML_A13_2_SEMANTIC_OUTPUT_COMPARISON_OK" in proc.stdout
