"""Tests for FEF-P6 broader original-runtime semantic comparison."""

from __future__ import annotations

import pytest

# Blanket-marked heavy: CLI-contract test (subprocess.run of a
# script that loads large JSON evidence). Skipped from the fast
# dev loop via `pytest -m "not heavy"`; runs in CI by default.
# A follow-up measurement pass will UN-mark individual fast files.
pytestmark = pytest.mark.heavy

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p6_broader_original_runtime_semantic_comparison import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p6_records_c_and_rust_original_runtime_comparisons():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "FEF_P6_BROADER_ORIGINAL_RUNTIME_SEMANTIC_COMPARISON_PASS"
    assert payload["summary"]["sourceLanguages"] == ["c", "rust"]
    assert payload["summary"]["caseCount"] == 5
    assert payload["summary"]["passCount"] == 5


def test_fef_p6_compares_original_runtimes_to_forge_targets():
    payload = build_payload()
    assert payload["summary"]["targetLanguages"] == ["python", "javascript"]
    assert payload["summary"]["sampleCount"] == 23
    for packet in payload["casePackets"]:
        assert packet["sourceLanguage"] in {"c", "rust"}
        assert packet["targetLanguages"] == ["python", "javascript"]
        assert packet["comparisonStatus"] == "pass"
        assert packet["maxAbsError"] <= 1e-9 or packet["maxRelError"] <= 1e-9
        frame = packet["frames"][0]
        assert set(frame["values"]) == {
            "originalRuntime",
            "forgePython",
            "forgeJavaScript",
        }


def test_fef_p6_records_matlab_runtime_unavailable():
    payload = build_payload()
    unavailable = payload["summary"]["unavailableOriginalRuntimes"]
    assert unavailable == [
        {
            "sourceLanguage": "matlab",
            "status": "not_executed",
            "reason": "No local octave or matlab runtime found on PATH.",
        }
    ]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["matlab_original_runtime_available"] == "blocked"


def test_fef_p6_claim_flags_remain_false():
    payload = build_payload()
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in payload["claimFlags"].values())
    for packet in payload["casePackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_fef_p6_writes_outputs(tmp_path):
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
    assert len(packets) == 5
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P6")


def test_fef_p6_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p6_broader_original_runtime_semantic_comparison.py",
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
    assert "FEF_P6_BROADER_ORIGINAL_RUNTIME_SEMANTIC_COMPARISON_OK" in proc.stdout
