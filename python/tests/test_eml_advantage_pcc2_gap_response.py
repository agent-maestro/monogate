"""Tests for EML-ADV-PCC2 gap response."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_advantage_pcc2_gap_response import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_pcc2_payload_records_protected_runtime_negative_control():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EML_ADV_PCC2_GAP_RESPONSE_PASS"
    assert payload["summary"]["negativeControlCount"] == 1
    assert payload["summary"]["profileCount"] == 3
    assert payload["summary"]["standardWinProfiles"] == 3
    assert payload["summary"]["allProfilesFavorProtectedStandard"] is True
    assert payload["negativeControlPacket"]["caseId"] == "protected_expm1_cancellation_negative_control_v0"


def test_pcc2_profiles_show_standard_improvement():
    packet = build_payload()["negativeControlPacket"]
    for profile in packet["profiles"]:
        assert profile["winner"] == "standard"
        assert profile["meanRelativeErrorImprovementFactor"] >= 10.0
        assert profile["standardProtected"]["finiteRatio"] == 1.0


def test_pcc2_claim_flags_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_payload()
    assert payload["summary"]["broadEmlAdvantageClaim"] is False
    assert payload["summary"]["runtimePerformanceClaim"] is False
    assert payload["summary"]["publicReady"] is False
    assert all(value is False for value in payload["claimFlags"].values())
    assert all(value is False for value in payload["negativeControlPacket"]["claimFlags"].values())


def test_pcc2_writes_json_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "packet_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-ADV-PCC2")


def test_pcc2_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_advantage_pcc2_gap_response.py",
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
    assert "EML_ADV_PCC2_GAP_RESPONSE_OK" in proc.stdout
