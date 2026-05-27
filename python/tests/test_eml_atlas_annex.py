"""Tests for EML-A1 Atlas Evidence Annex."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_atlas_annex import (
    SEED_ENTRIES,
    analyze_entry,
    build_annex,
    validate_annex,
)


def entry(entry_id: str) -> dict:
    for item in SEED_ENTRIES:
        if item["id"] == entry_id:
            return item
    raise AssertionError(f"missing entry {entry_id}")


def test_seed_entries_cover_expected_classifications():
    classifications = {item["classification"] for item in SEED_ENTRIES}
    assert "exact_identity" in classifications
    assert "standard_rewrite" in classifications
    assert "conjectural_or_blocked" in classifications
    assert len(SEED_ENTRIES) >= 10


def test_exp_and_boundary_entries_validate():
    for entry_id in ["exp_from_eml", "bose_boundary", "fermi_boundary", "subtraction_boundary"]:
        result = analyze_entry(entry(entry_id))
        assert result["validationStatus"] == "pass"
        assert all(sample["pass"] is True for sample in result["numericChecks"])


def test_mellin_polylog_correction_catches_missing_lambda_factor():
    result = analyze_entry(entry("mellin_polylog_correction"))
    assert result["validationStatus"] == "pass"
    missing_factor_checks = [
        item for item in result["numericChecks"]
        if item["label"].startswith("missing-factor-check")
    ]
    assert missing_factor_checks
    assert all(item["pass"] is True for item in missing_factor_checks)
    assert all(item["absError"] > 1e-3 for item in missing_factor_checks)


def test_rh_modulus_boundary_is_blocked_not_promoted():
    result = analyze_entry(entry("rh_modulus_boundary"))
    assert result["classification"] == "conjectural_or_blocked"
    assert result["validationStatus"] == "pass"
    assert result["promoteToPublicAtlas"] is False
    assert "Blocked as a public theorem claim" in result["claimBoundary"]


def test_build_annex_writes_result_report_and_evidence(tmp_path):
    built = build_annex(tmp_path / "out", tmp_path / "reports", tmp_path / "evidence")
    payload = json.loads(Path(built["result_path"]).read_text(encoding="utf-8"))
    evidence = json.loads(Path(built["evidence_path"]).read_text(encoding="utf-8"))
    assert payload["status"] == "EML_ATLAS_ANNEX_PASS"
    assert payload["publicAtlasSource"] == "https://monogate.org/atlas"
    assert evidence["reviewDecision"] == "candidate_only"
    assert evidence["claimFlags"]["rh_proof_claim"] is False
    validate_annex(payload)


def test_no_claim_flags_flip(tmp_path):
    built = build_annex(tmp_path / "out", tmp_path / "reports", tmp_path / "evidence")
    payload = built["payload"]
    assert all(value is False for value in payload["claimFlags"].values())
    for item in payload["entries"]:
        assert item["promoteToPublicAtlas"] is False
        assert all(value is False for value in item["claimFlags"].values())


def test_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_atlas_annex.py",
            "--build",
            "--out-dir",
            str(tmp_path / "out"),
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
    assert "EML_ATLAS_ANNEX_OK" in proc.stdout
