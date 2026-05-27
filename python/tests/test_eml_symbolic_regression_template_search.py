"""Tests for EML-A5 symbolic-regression-style template search."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_symbolic_regression_template_search import (
    FIRST_ZETA_ZERO_GAMMA,
    build_search,
    template_specs,
    validate_search,
)


def test_template_library_has_controls_and_baseline():
    specs = template_specs()
    ids = {item["id"] for item in specs}
    assert len(specs) >= 6
    assert "eml_critical_one_node" in ids
    assert "standard_profiled_sqrt_cos_sin" in ids
    assert "eml_wrong_exponent_03" in ids
    assert "eml_wrong_exponent_07" in ids
    assert "constant_baseline" in ids


def test_eml_critical_template_localizes_first_known_zero(tmp_path):
    result = build_search(tmp_path / "out", tmp_path / "reports", tmp_path / "evidence")["result"]
    eml = next(item for item in result["templates"] if item["id"] == "eml_critical_one_node")
    assert abs(eml["bestGamma"] - FIRST_ZETA_ZERO_GAMMA) < 0.06
    assert result["rankings"]["byCandidateComplexityAdjustedScore"][0] == "eml_critical_one_node"


def test_wrong_exponent_control_exposes_localization_ambiguity(tmp_path):
    result = build_search(tmp_path / "out", tmp_path / "reports", tmp_path / "evidence")["result"]
    eml = next(item for item in result["templates"] if item["id"] == "eml_critical_one_node")
    wrong = next(item for item in result["templates"] if item["id"] == "eml_wrong_exponent_03")
    assert wrong["errorFromFirstKnownZero"] < eml["errorFromFirstKnownZero"]
    assert result["interpretation"]["reviewFinding"] == "promising_but_not_decisive"


def test_profiled_standard_remains_lower_mse_baseline(tmp_path):
    result = build_search(tmp_path / "out", tmp_path / "reports", tmp_path / "evidence")["result"]
    eml = next(item for item in result["templates"] if item["id"] == "eml_critical_one_node")
    standard = next(item for item in result["templates"] if item["id"] == "standard_profiled_sqrt_cos_sin")
    assert standard["bestMse"] < eml["bestMse"]
    assert standard["grammarOperatorNodes"] > eml["grammarOperatorNodes"]
    assert standard["freeParameterCount"] > eml["freeParameterCount"]


def test_build_search_writes_json_report_and_evidence(tmp_path):
    built = build_search(tmp_path / "out", tmp_path / "reports", tmp_path / "evidence")
    result = json.loads(Path(built["result_path"]).read_text(encoding="utf-8"))
    evidence = json.loads(Path(built["evidence_path"]).read_text(encoding="utf-8"))
    assert result["status"] == "EML_SYMBOLIC_REGRESSION_TEMPLATE_SEARCH_PASS"
    assert result["interpretation"]["fullPysrRunPerformed"] is False
    assert evidence["reviewDecision"] == "candidate_only"
    assert evidence["claimFlags"]["pysr_run_claim"] is False
    validate_search(result)


def test_claim_flags_remain_false(tmp_path):
    result = build_search(tmp_path / "out", tmp_path / "reports", tmp_path / "evidence")["result"]
    assert all(value is False for value in result["claimFlags"].values())
    assert "full PySR" in " ".join(result["nonClaims"])


def test_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_symbolic_regression_template_search.py",
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
    assert "EML_SYMBOLIC_REGRESSION_TEMPLATE_SEARCH_OK" in proc.stdout
