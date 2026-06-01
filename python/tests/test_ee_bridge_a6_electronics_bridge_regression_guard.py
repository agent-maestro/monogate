"""Tests for EE-BRIDGE-A6 electronics bridge regression guard."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.ee_bridge_a6_electronics_bridge_regression_guard import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_ee_bridge_a6_records_regression_guard_pass():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EE_BRIDGE_A6_ELECTRONICS_BRIDGE_REGRESSION_GUARD_PASS"
    assert payload["decision"] == "electronics_bridge_regression_guard_pass_real_artifact_still_pending"
    assert payload["summary"]["guardFailCount"] == 0
    assert payload["summary"]["defaultInboxStatus"] == "pending_no_artifact"


def test_ee_bridge_a6_checks_expected_artifact_chain():
    payload = build_payload()
    ids = [item["id"] for item in payload["checkedArtifacts"]]
    assert ids == [
        "ee-bridge-a1-electronics-evidence-intake-contract",
        "ee-guard-a1-electronics-guard-obligation-inventory",
        "ee-bridge-a2-electronics-artifact-intake-validation",
        "ee-bridge-a4-electronics-artifact-inbox-gate",
    ]
    assert payload["summary"]["checkedArtifactCount"] == 4


def test_ee_bridge_a6_guard_rows_cover_counts_and_boundaries():
    payload = build_payload()
    rows = {row["id"]: row for row in payload["guardRows"]}
    assert rows["a1_contract_artifact_types"]["passed"] is True
    assert rows["a1_required_fields"]["passed"] is True
    assert rows["guard_a1_obligation_counts"]["passed"] is True
    assert rows["a2_simulated_handoff_accepts_one"]["passed"] is True
    assert rows["a2_negative_controls_pass"]["passed"] is True
    assert rows["a4_default_inbox_pending"]["passed"] is True
    assert rows["all_claim_flags_false"]["passed"] is True
    assert rows["electronics_ownership_boundary"]["passed"] is True


def test_ee_bridge_a6_keeps_real_artifact_and_hardware_pending():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["realLaptopAgentArtifactReceived"] is False
    assert summary["hardwareObserved"] is False
    assert summary["liveCapturePerformed"] is False
    assert summary["monogateElectronicsRepoTouched"] is False
    assert summary["electronicsSurfaceTouched"] is False


def test_ee_bridge_a6_claim_flags_remain_false():
    payload = build_payload()
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_ee_bridge_a6_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EE-BRIDGE-A6")


def test_ee_bridge_a6_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/ee_bridge_a6_electronics_bridge_regression_guard.py",
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
    assert "EE_BRIDGE_A6_ELECTRONICS_BRIDGE_REGRESSION_GUARD_OK" in proc.stdout
