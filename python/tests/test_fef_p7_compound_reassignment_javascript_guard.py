"""Tests for FEF-P7 compound-reassignment JavaScript guard."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p7_compound_reassignment_javascript_guard import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p7_records_poly_horner_compound_reassignment_guard():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "FEF_P7_COMPOUND_REASSIGNMENT_JAVASCRIPT_GUARD_PASS"
    assert payload["summary"]["sourceLanguages"] == ["c", "rust"]
    assert payload["summary"]["caseCount"] == 2
    assert payload["summary"]["passCount"] == 2
    assert payload["summary"]["javascriptRebindGuardPass"] is True


def test_fef_p7_records_scoped_forge_implementation_change():
    payload = build_payload()
    change = payload["summary"]["forgeImplementationChange"]
    assert change["changed"] is True
    assert change["scope"] == "JavaScript backend repeated local EML binding emission only"
    assert "assignments" in change["newEmissionShape"]


def test_fef_p7_compares_original_runtimes_to_forge_targets():
    payload = build_payload()
    assert payload["summary"]["targetLanguages"] == ["python", "javascript"]
    assert payload["summary"]["sampleCount"] == 8
    for packet in payload["casePackets"]:
        assert packet["sourceLanguage"] in {"c", "rust"}
        assert packet["functionName"] == "quad"
        assert packet["comparisonStatus"] == "pass"
        assert packet["javascriptRebindGuard"]["status"] == "pass"
        assert packet["javascriptRebindGuard"]["hasRepeatedConstY"] is False
        assert packet["javascriptRebindGuard"]["letYCount"] == 1
        assert packet["maxAbsError"] <= 1e-9 or packet["maxRelError"] <= 1e-9
        assert set(packet["frames"][0]["values"]) == {
            "originalRuntime",
            "forgePython",
            "forgeJavaScript",
        }


def test_fef_p7_claim_flags_remain_false():
    payload = build_payload()
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in payload["claimFlags"].values())
    for packet in payload["casePackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_fef_p7_writes_outputs(tmp_path):
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
    assert len(packets) == 2
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P7")


def test_fef_p7_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p7_compound_reassignment_javascript_guard.py",
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
    assert "FEF_P7_COMPOUND_REASSIGNMENT_JAVASCRIPT_GUARD_OK" in proc.stdout
