"""Tests for EML-R10E formal compiler proof skeleton."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_atlas_annex import build_annex
from scripts.eml_atlas_promotion_gate import build_gate
from scripts.eml_r10_cost_stability_lab import build_lab
from scripts.eml_r10b_runtime_bakeoff import build_bakeoff
from scripts.eml_r10c_scoped_semantic_proof import build_proofs
from scripts.eml_r10e_formal_compiler_proof_skeleton import (
    CLAIM_FLAGS,
    COMPILER_OBLIGATIONS,
    build_skeleton,
    build_skeleton_payload,
    validate_payload,
)
from scripts.eml_r11_hybrid_lowering_planner import build_planner
from scripts.eml_r12_generated_lowering_stubs import build_stubs


def build_r10c(tmp_path):
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
    r12 = build_stubs(
        Path(r11["result_path"]),
        tmp_path / "r12",
        tmp_path / "stubs",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    r10b = build_bakeoff(
        Path(r12["result_path"]),
        tmp_path / "r10b",
        tmp_path / "bakeoff_packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    return build_proofs(
        Path(r12["result_path"]),
        Path(r10b["result_path"]),
        tmp_path / "r10c",
        tmp_path / "proof_packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )


def test_obligation_template_keeps_compiler_wide_work_open():
    obligation_ids = {item["obligationId"] for item in COMPILER_OBLIGATIONS}
    assert "per-case-semantic-preservation" in obligation_ids
    assert "compiler-wide-induction" in obligation_ids
    assert any(item["status"] == "open" for item in COMPILER_OBLIGATIONS)


def test_build_skeleton_payload_maps_r10c_covered_cases(tmp_path):
    r10c = build_r10c(tmp_path)
    payload = build_skeleton_payload(Path(r10c["result_path"]), r10c["payload"])
    assert payload["schemaVersion"] == "monogate.eml_formal_compiler_proof_skeleton.v0"
    assert payload["summary"]["coveredCaseCount"] >= 4
    assert payload["summary"]["openObligationCount"] > 0
    assert payload["summary"]["compilerCorrectnessProved"] is False
    assert payload["summary"]["formalCompilerProofComplete"] is False


def test_build_skeleton_outputs_artifacts(tmp_path):
    r10c = build_r10c(tmp_path)
    built = build_skeleton(
        Path(r10c["result_path"]),
        tmp_path / "r10e",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    payload = built["payload"]
    assert payload["status"] == "EML_R10E_FORMAL_COMPILER_PROOF_SKELETON_PASS"
    assert payload["summary"]["obligationCount"] >= 6
    assert payload["summary"]["coveredObligationCount"] >= 1
    assert payload["summary"]["openObligationCount"] > 0
    assert payload["summary"]["compilerCorrectnessProved"] is False
    assert payload["summary"]["formalCompilerProofComplete"] is False
    validate_payload(payload)
    assert Path(built["result_path"]).exists()
    assert Path(built["skeleton_path"]).exists()
    assert Path(built["report_path"]).exists()
    assert Path(built["evidence_path"]).exists()
    assert Path(built["feed_path"]).exists()


def test_claim_flags_are_all_false(tmp_path):
    assert all(value is False for value in CLAIM_FLAGS.values())
    r10c = build_r10c(tmp_path)
    built = build_skeleton(
        Path(r10c["result_path"]),
        tmp_path / "r10e",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    assert all(value is False for value in built["payload"]["claimFlags"].values())
    assert all(value is False for value in built["skeleton"]["claimFlags"].values())
    assert all(value is False for value in built["evidence"]["claimFlags"].values())


def test_generated_json_files_parse(tmp_path):
    r10c = build_r10c(tmp_path)
    built = build_skeleton(
        Path(r10c["result_path"]),
        tmp_path / "r10e",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for path in [built["result_path"], built["skeleton_path"], built["evidence_path"], built["feed_path"]]:
        json.loads(Path(path).read_text(encoding="utf-8"))


def test_cli_build_strict(tmp_path):
    r10c = build_r10c(tmp_path)
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_r10e_formal_compiler_proof_skeleton.py",
            "--build",
            "--r10c-path",
            r10c["result_path"],
            "--out-dir",
            str(tmp_path / "r10e"),
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
    assert "EML_R10E_FORMAL_COMPILER_PROOF_SKELETON_OK" in proc.stdout
