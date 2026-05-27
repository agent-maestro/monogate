"""Tests for the EML-L3 language cost lab."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_language_cost_lab import analyze_program, build_cost_lab
from scripts.eml_language_kernel import canonicalize_expression, parse_program


FIXTURES = Path("python/fixtures/eml_language_programs")


def load_program(name: str) -> dict:
    return parse_program((FIXTURES / name).read_text(encoding="utf-8"))


def test_eml_surface_cost_less_than_expanded():
    result = analyze_program(load_program("raw_eml_primitive_v0.eml"))
    assert result["surfaceOperatorCount"] == 1
    assert result["expandedOperatorCount"] > result["surfaceOperatorCount"]
    assert result["expansionDelta"] > 0


def test_softplus_surface_cost_less_than_expanded():
    result = analyze_program(load_program("guarded_eml_softplus_v0.eml"))
    assert result["expandedOperatorCount"] > result["surfaceOperatorCount"]
    assert result["expansionDelta"] > 0


def test_canonical_hash_stable_across_equivalent_programs():
    left = canonicalize_expression("eml(x, y)")
    right = canonicalize_expression("exp(x) - ln(y)")
    assert left["canonicalHash"] == right["canonicalHash"]


def test_dag_reuse_detects_repeated_gaussian_subtree():
    result = analyze_program(load_program("gaussian_energy_v0.eml"))
    assert result["expandedOperatorCount"] > result["dagUniqueOperatorCount"]
    assert result["repeatedCanonicalSubtreeCount"] >= 1
    assert any(item["op"] == "exp" for item in result["repeatedCanonicalSubtrees"])


def test_no_public_savings_or_cost_claim_flips(tmp_path):
    built = build_cost_lab(FIXTURES, tmp_path / "out", tmp_path / "reports")
    payload = built["payload"]
    assert payload["summary"]["publicCostClaimChanged"] is False
    assert all(value is False for value in payload["claimFlags"].values())
    for item in payload["programs"]:
        assert item["publicCostClaimChanged"] is False
        assert all(value is False for value in item["claimFlags"].values())


def test_build_cost_lab_writes_json_and_report(tmp_path):
    built = build_cost_lab(FIXTURES, tmp_path / "out", tmp_path / "reports")
    result_path = Path(built["result_path"])
    report_path = Path(built["report_path"])
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    assert payload["status"] == "EML_LANGUAGE_COST_LAB_PASS"
    assert payload["summary"]["programCount"] >= 5
    assert report_path.exists()


def test_cli_build_fixtures(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_language_cost_lab.py",
            "--build-fixtures",
            "--out-dir",
            str(tmp_path / "out"),
            "--report-dir",
            str(tmp_path / "reports"),
            "--strict",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "EML_LANGUAGE_COST_LAB_OK" in proc.stdout
