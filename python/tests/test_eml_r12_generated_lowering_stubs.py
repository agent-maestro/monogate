"""Tests for EML-R12 generated lowering stubs."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_r10_cost_stability_lab import build_lab
from scripts.eml_atlas_annex import build_annex
from scripts.eml_atlas_promotion_gate import build_gate
from scripts.eml_r11_hybrid_lowering_planner import build_planner
from scripts.eml_r12_generated_lowering_stubs import (
    CLAIM_FLAGS,
    build_stubs,
    compile_stub,
    packet_from_plan,
    validate_payload,
)


def build_r11(tmp_path):
    r10 = build_lab(
        tmp_path / "r10",
        tmp_path / "cost_packets",
        tmp_path / "reports",
        tmp_path / "evidence",
    )
    annex = build_annex(tmp_path / "annex", tmp_path / "reports", tmp_path / "evidence")
    gate = build_gate(Path(annex["result_path"]), tmp_path / "gate", tmp_path / "reports", tmp_path / "evidence")
    return build_planner(
        Path(r10["result_path"]),
        Path(gate["result_path"]),
        tmp_path / "r11",
        tmp_path / "plans",
        tmp_path / "reports",
        tmp_path / "evidence",
    )


def plan_by_case(r11, case_id: str):
    return next(plan for plan in r11["payload"]["plans"] if plan["caseId"] == case_id)


def test_packet_from_plan_generates_python_source_and_validates(tmp_path):
    r11 = build_r11(tmp_path)
    packet = packet_from_plan(plan_by_case(r11, "softplus_pair_v0"))
    assert packet["schemaVersion"] == "monogate.eml_generated_stub_packet.v0"
    assert packet["pythonFunctionName"] == "lower_softplus_pair_v0"
    assert "np.logaddexp" in packet["pythonSource"]
    assert packet["validation"]["status"] == "pass"
    assert packet["claimFlags"]["compiler_correctness_claim"] is False


def test_generated_python_source_compiles(tmp_path):
    r11 = build_r11(tmp_path)
    packet = packet_from_plan(plan_by_case(r11, "exp_from_eml_v0"))
    fn = compile_stub(packet["caseId"], packet["pythonSource"])
    assert callable(fn)


def test_bose_boundary_uses_expm1(tmp_path):
    r11 = build_r11(tmp_path)
    packet = packet_from_plan(plan_by_case(r11, "bose_boundary_expm1_v0"))
    assert packet["loweredExpression"] == "np.expm1(x)"
    assert "np.expm1" in packet["pythonSource"]
    assert packet["validation"]["maxAbsError"] <= 1.0e-9


def test_sigmoid_derivative_uses_stable_sigmoid(tmp_path):
    r11 = build_r11(tmp_path)
    packet = packet_from_plan(plan_by_case(r11, "sigmoid_derivative_v0"))
    assert "stable_sigmoid" in packet["pythonSource"]
    assert packet["validation"]["status"] == "pass"


def test_build_stubs_outputs_all_packets(tmp_path):
    r11 = build_r11(tmp_path)
    built = build_stubs(
        Path(r11["result_path"]),
        tmp_path / "r12",
        tmp_path / "stubs",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    payload = built["payload"]
    assert payload["status"] == "EML_R12_GENERATED_LOWERING_STUBS_PASS"
    assert payload["summary"]["stubPacketCount"] >= 7
    assert payload["summary"]["validationPassCount"] == payload["summary"]["stubPacketCount"]
    assert payload["summary"]["validationFailCount"] == 0
    assert payload["summary"]["compilerBehaviorChanged"] is False
    assert payload["summary"]["productionLoweringClaim"] is False
    assert payload["summary"]["semanticEquivalenceClaim"] is False
    validate_payload(payload)


def test_generated_stub_json_files_parse(tmp_path):
    r11 = build_r11(tmp_path)
    build_stubs(
        Path(r11["result_path"]),
        tmp_path / "r12",
        tmp_path / "stubs",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    paths = sorted((tmp_path / "stubs").glob("*_generated_stub_*.json"))
    assert len(paths) >= 7
    for path in paths:
        packet = json.loads(path.read_text(encoding="utf-8"))
        assert packet["schemaVersion"] == "monogate.eml_generated_stub_packet.v0"
        assert packet["validation"]["status"] == "pass"


def test_evidence_and_feed_keep_claim_flags_false(tmp_path):
    r11 = build_r11(tmp_path)
    built = build_stubs(
        Path(r11["result_path"]),
        tmp_path / "r12",
        tmp_path / "stubs",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    assert all(value is False for value in built["evidence"]["claimFlags"].values())
    assert all(value is False for value in built["feed"]["claimFlags"].values())
    assert built["evidence"]["semanticReview"]["compilerBehaviorChanged"] is False
    assert built["evidence"]["semanticReview"]["productionLoweringClaim"] is False


def test_claim_flags_are_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())


def test_cli_build_strict(tmp_path):
    r11 = build_r11(tmp_path)
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_r12_generated_lowering_stubs.py",
            "--build",
            "--r11-path",
            r11["result_path"],
            "--out-dir",
            str(tmp_path / "r12"),
            "--stub-dir",
            str(tmp_path / "stubs"),
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
    assert "EML_R12_GENERATED_LOWERING_STUBS_OK" in proc.stdout
