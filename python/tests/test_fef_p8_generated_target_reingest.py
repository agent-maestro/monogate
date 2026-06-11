"""Tests for FEF-P8 generated-target re-ingest."""

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

from scripts.fef_p8_generated_target_reingest import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p8_records_generated_target_reingest():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "FEF_P8_GENERATED_TARGET_REINGEST_PASS"
    assert payload["summary"]["packetCount"] == 6
    assert payload["summary"]["passCount"] == 6
    assert payload["summary"]["generatedTargetLanguages"] == ["javascript", "python"]


def test_fef_p8_compares_generated_outputs_to_reingested_outputs():
    payload = build_payload()
    assert payload["summary"]["sampleCount"] == 26
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


def test_fef_p8_records_pow_expression_holdout():
    payload = build_payload()
    held_out = payload["summary"]["heldOutGeneratedTargetShapes"]
    assert held_out == [
        "power-expression generated Python/JavaScript re-ingest where eFrog emits `^`, which Forge reserves for unit expressions"
    ]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["power_expression_generated_target_reingest"] == "held_out"


def test_fef_p8_claim_flags_remain_false():
    payload = build_payload()
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in payload["claimFlags"].values())
    for packet in payload["reingestPackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_fef_p8_writes_outputs(tmp_path):
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
    assert len(packets) == 6
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P8")


def test_fef_p8_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p8_generated_target_reingest.py",
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
    assert "FEF_P8_GENERATED_TARGET_REINGEST_OK" in proc.stdout
