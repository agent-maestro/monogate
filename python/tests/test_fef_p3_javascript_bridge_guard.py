"""Tests for FEF-P3 JavaScript bridge guard evidence."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p3_javascript_bridge_guard import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p3_records_javascript_bridge_runtime_guard():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "FEF_P3_JAVASCRIPT_BRIDGE_GUARD_PASS"
    assert payload["summary"]["bridgeGuardStatus"] == "pass"
    assert payload["summary"]["roundtripMatrixPassed"] is True
    assert payload["summary"]["targetLanguages"] == ["python", "javascript"]


def test_fef_p3_runtime_counts_are_bounded():
    payload = build_payload()
    assert payload["summary"]["resultCount"] == 10
    assert payload["summary"]["pythonResultCount"] == 5
    assert payload["summary"]["javascriptResultCount"] == 5
    assert payload["summary"]["javascriptRuntimeExecutionPassCount"] == 5
    assert {
        result["runtime_validation"]
        for result in payload["roundtripMatrix"]["results"]
        if result["target_language"] == "javascript"
    } == {"javascript_runtime_execution_passed"}


def test_fef_p3_release_gates_and_claim_flags_are_bounded():
    payload = build_payload()
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["bridge_guard_runs_python_and_javascript"] == "pass"
    assert gates["javascript_runtime_execution_guard_passed"] == "pass"
    assert gates["public_package_published"] == "blocked"
    assert gates["checkout_remains_disabled"] == "required"
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p3_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P3")


def test_fef_p3_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p3_javascript_bridge_guard.py",
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
    assert "FEF_P3_JAVASCRIPT_BRIDGE_GUARD_OK" in proc.stdout
