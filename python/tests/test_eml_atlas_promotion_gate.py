"""Tests for EML-A7 Atlas promotion gate."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_atlas_annex import build_annex
from scripts.eml_atlas_promotion_gate import build_gate, validate_gate


def test_gate_buckets_entries_and_keeps_promotions_false(tmp_path):
    annex = build_annex(tmp_path / "annex", tmp_path / "reports", tmp_path / "evidence")
    result = build_gate(Path(annex["result_path"]), tmp_path / "gate", tmp_path / "reports", tmp_path / "evidence")["result"]
    assert result["entryCount"] >= 30
    assert result["policy"]["publicPromotionPerformed"] is False
    assert result["bucketCounts"]["blocked_or_conjectural"] >= 1
    assert result["bucketCounts"]["safe_public_education_candidate"] >= 1
    assert all(item["publicPromotionPerformed"] is False for item in result["decisions"])
    validate_gate(result)


def test_gate_records_checked_exp_witness(tmp_path):
    annex = build_annex(tmp_path / "annex", tmp_path / "reports", tmp_path / "evidence")
    result = build_gate(Path(annex["result_path"]), tmp_path / "gate", tmp_path / "reports", tmp_path / "evidence")["result"]
    checked = {item["entryId"]: item for item in result["checkedWitnesses"]}
    assert checked["exp_from_eml"]["machlibName"] == "MachLib.Real.atlas_exp_from_eml_witness"
    assert checked["subtraction_boundary"]["machlibName"] == "MachLib.Real.atlas_subtraction_boundary_witness"
    assert checked["constants_zero_and_e"]["machlibName"] == "MachLib.Real.constants_zero_one_e_boundary_witness"
    exp_decision = next(item for item in result["decisions"] if item["id"] == "exp_from_eml")
    sub_decision = next(item for item in result["decisions"] if item["id"] == "subtraction_boundary")
    constants_decision = next(item for item in result["decisions"] if item["id"] == "constants_zero_and_e")
    assert exp_decision["publicEducationCandidate"] is True
    assert sub_decision["proofStatus"] == "checked_machlib_witness_available"
    assert constants_decision["proofStatus"] == "checked_machlib_witness_available"


def test_gate_writes_json_report_and_evidence(tmp_path):
    annex = build_annex(tmp_path / "annex", tmp_path / "reports", tmp_path / "evidence")
    built = build_gate(Path(annex["result_path"]), tmp_path / "gate", tmp_path / "reports", tmp_path / "evidence")
    result = json.loads(Path(built["result_path"]).read_text(encoding="utf-8"))
    evidence = json.loads(Path(built["evidence_path"]).read_text(encoding="utf-8"))
    assert result["status"] == "EML_ATLAS_PROMOTION_GATE_PASS"
    assert evidence["reviewDecision"] == "candidate_only"
    assert evidence["claimFlags"]["public_atlas_promotion"] is False
    validate_gate(result)


def test_cli_build_strict(tmp_path):
    annex = build_annex(tmp_path / "annex", tmp_path / "reports", tmp_path / "evidence")
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_atlas_promotion_gate.py",
            "--build",
            "--annex-path",
            annex["result_path"],
            "--out-dir",
            str(tmp_path / "gate"),
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
    assert "EML_ATLAS_PROMOTION_GATE_OK" in proc.stdout
