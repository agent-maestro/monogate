"""Tests for FEF-P1 public compiler preview package/CLI decision."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p1_public_compiler_preview_decision import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p1_selects_preview_package_without_publishing():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "FEF_P1_PUBLIC_COMPILER_PREVIEW_DECISION_RECORDED"
    assert payload["decision"] == "select_monogate_forge_preview_package"
    assert payload["selectedPackage"]["name"] == "monogate-forge-preview"
    assert payload["selectedPackage"]["distributionStatus"] == "not_created_not_published"
    assert payload["summary"]["packageCreated"] is False
    assert payload["summary"]["packagePublished"] is False


def test_fef_p1_keeps_preview_scope_to_python_javascript():
    payload = build_payload()
    assert payload["previewScope"]["targetScope"] == ["python", "javascript"]
    assert "Verilog" in payload["previewScope"]["explicitlyOutOfScope"]
    assert "compiler correctness" in payload["previewScope"]["explicitlyOutOfScope"]
    assert "paid Forge Pro checkout" in payload["previewScope"]["explicitlyOutOfScope"]


def test_fef_p1_records_allowed_and_blocked_commands():
    payload = build_payload()
    allowed = " ".join(command["command"] for command in payload["allowedCommands"])
    blocked = " ".join(command["command"] for command in payload["blockedCommands"])
    assert "capabilities" in allowed
    assert "--target python" in allowed
    assert "--target javascript" in allowed
    assert "--target verilog" in blocked
    assert "--target all" in blocked
    assert "prove-correct" in blocked


def test_fef_p1_links_to_fef_p0_readiness_gate():
    payload = build_payload()
    link = payload["fefP0Link"]
    assert link["decision"] == "not_public_ready_yet"
    assert link["privateCompilerSlicePresent"] is True
    assert link["publicReady"] is False


def test_fef_p1_claim_flags_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_payload()
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p1_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P1")


def test_fef_p1_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p1_public_compiler_preview_decision.py",
            "--build",
            "--out-dir",
            str(tmp_path / "results"),
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
    assert "FEF_P1_PUBLIC_COMPILER_PREVIEW_DECISION_OK" in proc.stdout
