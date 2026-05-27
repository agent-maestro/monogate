"""Tests for the EML-R10 cost and stability lab."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_r10_cost_stability_lab import analyze_case, build_lab, case_specs


def case_by_id(case_id: str):
    return next(spec for spec in case_specs() if spec.case_id == case_id)


def test_r10_builds_at_least_seven_cost_packets(tmp_path):
    built = build_lab(
        tmp_path / "out",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
    )
    payload = built["payload"]
    assert payload["status"] == "EML_R10_COST_STABILITY_LAB_PASS"
    assert payload["summary"]["packetCount"] >= 7
    assert payload["summary"]["publicCostClaimChanged"] is False


def test_bose_boundary_prefers_protected_standard_near_zero():
    packet = analyze_case(case_by_id("bose_boundary_expm1_v0"))
    assert packet["recommendation"] in {"use_standard", "research_only"}
    assert packet["comparison"]["standard"]["maxRelError"] <= packet["comparison"]["eml"]["maxRelError"]


def test_subtraction_boundary_is_finite_but_not_a_public_savings_claim():
    packet = analyze_case(case_by_id("subtraction_boundary_v0"))
    assert packet["comparison"]["eml"]["finiteRatio"] == 1.0
    assert packet["claimFlags"]["public_savings_claim"] is False
    assert "No public performance or energy savings claim." in packet["blockedClaims"]


def test_ln_from_eml_records_deeper_operator_count_than_standard_log():
    packet = analyze_case(case_by_id("ln_from_eml_v0"))
    assert packet["comparison"]["eml"]["operatorCount"] > packet["comparison"]["standard"]["operatorCount"]
    assert packet["recommendation"] in {"use_standard", "research_only", "use_hybrid"}


def test_softplus_pair_uses_standard_or_hybrid_not_plain_eml_win():
    packet = analyze_case(case_by_id("softplus_pair_v0"))
    assert packet["recommendation"] != "use_eml"
    assert packet["comparison"]["standard"]["finiteRatio"] == 1.0


def test_generated_cost_packets_parse_as_json(tmp_path):
    build_lab(
        tmp_path / "out",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
    )
    paths = sorted((tmp_path / "packets").glob("*_cost_packet_*.json"))
    assert len(paths) >= 7
    for path in paths:
        packet = json.loads(path.read_text(encoding="utf-8"))
        assert packet["schemaVersion"] == "monogate.eml_cost_packet.v0"


def test_claim_flags_remain_false(tmp_path):
    payload = build_lab(
        tmp_path / "out",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
    )["payload"]
    assert all(value is False for value in payload["claimFlags"].values())
    for packet in payload["costPackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_r10_cost_stability_lab.py",
            "--build",
            "--out-dir",
            str(tmp_path / "out"),
            "--packet-dir",
            str(tmp_path / "packets"),
            "--report-dir",
            str(tmp_path / "reports"),
            "--evidence-dir",
            str(tmp_path / "evidence"),
            "--strict",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "EML_R10_COST_STABILITY_LAB_OK" in proc.stdout
