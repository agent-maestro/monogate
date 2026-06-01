"""Tests for EE-GUARD-A1 electronics guard obligation inventory."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.ee_guard_a1_electronics_guard_obligation_inventory import (
    CLAIM_FLAGS,
    build_inventory,
    build_obligations,
    build_outputs,
    validate_inventory,
)


def test_ee_guard_a1_records_guard_inventory_without_proof_or_hardware_claim():
    inventory = build_inventory()
    validate_inventory(inventory)
    assert inventory["status"] == "EE_GUARD_A1_ELECTRONICS_GUARD_OBLIGATION_INVENTORY_PASS"
    assert inventory["decision"] == "electronics_guard_obligation_inventory_recorded_no_proof_or_hardware_claim"
    assert inventory["summary"]["hardwareObserved"] is False
    assert inventory["summary"]["liveCapturePerformed"] is False
    assert inventory["summary"]["proofClaim"] is False


def test_ee_guard_a1_names_three_expected_obligations():
    obligations = build_obligations()
    assert [item["obligationId"] for item in obligations] == [
        "voltage_divider_positive_resistance_sum_v0",
        "rc_decay_positive_time_constant_v0",
        "logic_guard_output_bounds_v0",
    ]
    assert {item["kernelId"] for item in obligations} == {
        "voltage_divider_v0",
        "rc_decay_v0",
        "logic_guard_v0",
    }


def test_ee_guard_a1_links_only_selected_voltage_divider_prior_evidence():
    inventory = build_inventory()
    by_id = {item["obligationId"]: item for item in inventory["obligations"]}
    voltage = by_id["voltage_divider_positive_resistance_sum_v0"]
    assert voltage["status"] == "prior_selected_witness_linked"
    assert "FEF-P23" in " ".join(voltage["priorEvidence"])
    assert by_id["rc_decay_positive_time_constant_v0"]["status"] == "open_guard_obligation"
    assert by_id["logic_guard_output_bounds_v0"]["status"] == "open_guard_obligation"


def test_ee_guard_a1_summary_counts_open_and_linked_obligations():
    inventory = build_inventory()
    summary = inventory["summary"]
    assert summary["obligationCount"] == 3
    assert summary["selectedProofLinkedCount"] == 1
    assert summary["openObligationCount"] == 2
    assert summary["recommendedFirstClosure"] == "voltage_divider_positive_resistance_sum_v0"


def test_ee_guard_a1_claim_flags_remain_false():
    inventory = build_inventory()
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in inventory["claimFlags"].values())
    assert inventory["summary"]["claimFlagsAllFalse"] is True


def test_ee_guard_a1_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EE-GUARD-A1")


def test_ee_guard_a1_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/ee_guard_a1_electronics_guard_obligation_inventory.py",
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
    assert "EE_GUARD_A1_ELECTRONICS_GUARD_OBLIGATION_INVENTORY_OK" in proc.stdout
