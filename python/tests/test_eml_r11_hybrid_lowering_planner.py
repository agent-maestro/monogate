"""Tests for the EML-R11 hybrid lowering planner."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_atlas_annex import build_annex
from scripts.eml_atlas_promotion_gate import build_gate
from scripts.eml_r10_cost_stability_lab import build_lab
from scripts.eml_r11_hybrid_lowering_planner import build_planner, validate_planner


def build_sources(tmp_path):
    r10 = build_lab(
        tmp_path / "r10",
        tmp_path / "cost_packets",
        tmp_path / "reports",
        tmp_path / "evidence",
    )
    annex = build_annex(tmp_path / "annex", tmp_path / "reports", tmp_path / "evidence")
    gate = build_gate(Path(annex["result_path"]), tmp_path / "gate", tmp_path / "reports", tmp_path / "evidence")
    return r10, gate


def test_r11_builds_lowering_plans(tmp_path):
    r10, gate = build_sources(tmp_path)
    built = build_planner(
        Path(r10["result_path"]),
        Path(gate["result_path"]),
        tmp_path / "r11",
        tmp_path / "plans",
        tmp_path / "reports",
        tmp_path / "evidence",
    )
    payload = built["payload"]
    assert payload["status"] == "EML_R11_HYBRID_LOWERING_PLANNER_PASS"
    assert payload["summary"]["planCount"] >= 7
    assert payload["summary"]["compilerBehaviorChanged"] is False
    validate_planner(payload)


def test_bose_boundary_lowers_to_expm1(tmp_path):
    r10, gate = build_sources(tmp_path)
    payload = build_planner(
        Path(r10["result_path"]),
        Path(gate["result_path"]),
        tmp_path / "r11",
        tmp_path / "plans",
        tmp_path / "reports",
        tmp_path / "evidence",
    )["payload"]
    plan = next(item for item in payload["plans"] if item["caseId"] == "bose_boundary_expm1_v0")
    assert plan["loweringDecision"] == "emit_standard"
    assert plan["selectedImplementation"] == "expm1(x)"
    assert "near_zero_requires_expm1_lowering" in plan["requiredGuards"]


def test_exp_from_eml_is_hybrid_not_pure_eml(tmp_path):
    r10, gate = build_sources(tmp_path)
    payload = build_planner(
        Path(r10["result_path"]),
        Path(gate["result_path"]),
        tmp_path / "r11",
        tmp_path / "plans",
        tmp_path / "reports",
        tmp_path / "evidence",
    )["payload"]
    plan = next(item for item in payload["plans"] if item["caseId"] == "exp_from_eml_v0")
    assert plan["loweringDecision"] == "emit_hybrid"
    assert "lower runtime call to exp(x)" in plan["selectedImplementation"]
    assert plan["atlasGate"]["proofStatus"] == "checked_machlib_witness_available"


def test_lowering_plans_keep_claim_flags_false(tmp_path):
    r10, gate = build_sources(tmp_path)
    payload = build_planner(
        Path(r10["result_path"]),
        Path(gate["result_path"]),
        tmp_path / "r11",
        tmp_path / "plans",
        tmp_path / "reports",
        tmp_path / "evidence",
    )["payload"]
    assert all(value is False for value in payload["claimFlags"].values())
    for plan in payload["plans"]:
        assert all(value is False for value in plan["claimFlags"].values())
        assert plan["atlasGate"]["publicPromotionPerformed"] is False


def test_generated_plan_json_files_parse(tmp_path):
    r10, gate = build_sources(tmp_path)
    build_planner(
        Path(r10["result_path"]),
        Path(gate["result_path"]),
        tmp_path / "r11",
        tmp_path / "plans",
        tmp_path / "reports",
        tmp_path / "evidence",
    )
    paths = sorted((tmp_path / "plans").glob("*_lowering_plan_*.json"))
    assert len(paths) >= 7
    for path in paths:
        plan = json.loads(path.read_text(encoding="utf-8"))
        assert plan["schemaVersion"] == "monogate.eml_lowering_plan_packet.v0"


def test_cli_build_strict(tmp_path):
    r10, gate = build_sources(tmp_path)
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_r11_hybrid_lowering_planner.py",
            "--build",
            "--cost-lab-path",
            r10["result_path"],
            "--atlas-gate-path",
            gate["result_path"],
            "--out-dir",
            str(tmp_path / "r11"),
            "--plan-dir",
            str(tmp_path / "plans"),
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
    assert "EML_R11_HYBRID_LOWERING_PLANNER_OK" in proc.stdout
