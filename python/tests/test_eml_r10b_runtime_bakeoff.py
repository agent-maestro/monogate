"""Tests for EML-R10B runtime bakeoff."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_atlas_annex import build_annex
from scripts.eml_atlas_promotion_gate import build_gate
from scripts.eml_r10_cost_stability_lab import build_lab
from scripts.eml_r10b_runtime_bakeoff import (
    CLAIM_FLAGS,
    broader_inputs,
    build_bakeoff,
    dtype_result,
    packet_from_stub,
    validate_payload,
)
from scripts.eml_r11_hybrid_lowering_planner import build_planner
from scripts.eml_r12_generated_lowering_stubs import build_stubs, compile_stub


def build_r12(tmp_path):
    r10 = build_lab(
        tmp_path / "r10",
        tmp_path / "cost_packets",
        tmp_path / "reports",
        tmp_path / "evidence",
    )
    annex = build_annex(tmp_path / "annex", tmp_path / "reports", tmp_path / "evidence")
    gate = build_gate(Path(annex["result_path"]), tmp_path / "gate", tmp_path / "reports", tmp_path / "evidence")
    r11 = build_planner(
        Path(r10["result_path"]),
        Path(gate["result_path"]),
        tmp_path / "r11",
        tmp_path / "plans",
        tmp_path / "reports",
        tmp_path / "evidence",
    )
    return build_stubs(
        Path(r11["result_path"]),
        tmp_path / "r12",
        tmp_path / "stubs",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )


def stub_by_case(r12, case_id: str):
    return next(packet for packet in r12["payload"]["stubPackets"] if packet["caseId"] == case_id)


def test_broader_inputs_include_more_samples_than_r10_default():
    values = broader_inputs("exp_from_eml_v0", __import__("numpy").float64)
    assert values["x"].size > 2048
    assert values["x"].dtype.name == "float64"


def test_dtype_result_passes_for_exp_stub(tmp_path):
    r12 = build_r12(tmp_path)
    stub = stub_by_case(r12, "exp_from_eml_v0")
    fn = compile_stub(stub["caseId"], stub["pythonSource"])
    result = dtype_result(stub["caseId"], fn, "float64")
    assert result["status"] == "pass"
    assert result["finiteRatio"] == 1.0
    assert result["maxRelError"] <= 1.0e-9


def test_packet_from_stub_records_float64_and_float32(tmp_path):
    r12 = build_r12(tmp_path)
    packet = packet_from_stub(stub_by_case(r12, "softplus_pair_v0"))
    assert packet["schemaVersion"] == "monogate.eml_runtime_bakeoff_packet.v0"
    assert packet["packetType"] == "eml_runtime_bakeoff_packet_v0"
    assert {item["dtype"] for item in packet["dtypeResults"]} == {"float64", "float32"}
    assert packet["runtimeStatus"] == "pass"
    assert packet["claimFlags"]["compiler_correctness_claim"] is False


def test_build_bakeoff_outputs_all_packets(tmp_path):
    r12 = build_r12(tmp_path)
    built = build_bakeoff(
        Path(r12["result_path"]),
        tmp_path / "r10b",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    payload = built["payload"]
    assert payload["status"] == "EML_R10B_RUNTIME_BAKEOFF_PASS"
    assert payload["summary"]["bakeoffPacketCount"] >= 7
    assert payload["summary"]["passCount"] == payload["summary"]["bakeoffPacketCount"]
    assert payload["summary"]["failCount"] == 0
    assert payload["summary"]["dtypeRunCount"] >= 14
    assert payload["summary"]["runtimeBakeoffPerformed"] is True
    assert payload["summary"]["compilerCorrectnessClaim"] is False
    assert payload["summary"]["semanticEquivalenceClaim"] is False
    validate_payload(payload)


def test_generated_bakeoff_packet_files_parse(tmp_path):
    r12 = build_r12(tmp_path)
    build_bakeoff(
        Path(r12["result_path"]),
        tmp_path / "r10b",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    paths = sorted((tmp_path / "packets").glob("*_runtime_bakeoff_packet_*.json"))
    assert len(paths) >= 7
    for path in paths:
        packet = json.loads(path.read_text(encoding="utf-8"))
        assert packet["schemaVersion"] == "monogate.eml_runtime_bakeoff_packet.v0"
        assert packet["runtimeStatus"] == "pass"


def test_claim_flags_are_all_false(tmp_path):
    assert all(value is False for value in CLAIM_FLAGS.values())
    r12 = build_r12(tmp_path)
    payload = build_bakeoff(
        Path(r12["result_path"]),
        tmp_path / "r10b",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )["payload"]
    assert all(value is False for value in payload["claimFlags"].values())
    for packet in payload["bakeoffPackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_evidence_and_feed_keep_boundaries_false(tmp_path):
    r12 = build_r12(tmp_path)
    built = build_bakeoff(
        Path(r12["result_path"]),
        tmp_path / "r10b",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    assert built["evidence"]["semanticReview"]["compilerBehaviorChanged"] is False
    assert built["evidence"]["semanticReview"]["semanticEquivalenceClaim"] is False
    assert built["evidence"]["semanticReview"]["publicPerformanceClaim"] is False
    assert built["feed"]["topFollowup"] == "R10C scoped semantic proof"
    assert all(value is False for value in built["feed"]["claimFlags"].values())


def test_cli_build_strict(tmp_path):
    r12 = build_r12(tmp_path)
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_r10b_runtime_bakeoff.py",
            "--build",
            "--r12-path",
            r12["result_path"],
            "--out-dir",
            str(tmp_path / "r10b"),
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
    assert "EML_R10B_RUNTIME_BAKEOFF_OK" in proc.stdout
