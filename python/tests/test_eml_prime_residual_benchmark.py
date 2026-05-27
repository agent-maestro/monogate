"""Tests for EML-A2 prime residual benchmark."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_prime_residual_benchmark import (
    FIRST_ZETA_ZERO_GAMMA,
    build_benchmark,
    fixture,
    scan_gamma,
    validate_benchmark,
)


def test_fixture_is_deterministic_and_nontrivial():
    fx = fixture()
    assert fx["summary"]["sampleCount"] == 800
    assert fx["summary"]["primeCountUpToMax"] == 30
    assert fx["summary"]["residualMin"] < -7
    assert fx["summary"]["residualMax"] > 4


def test_eml_scan_localizes_first_known_zero_on_fixed_fixture():
    fx = fixture()
    scan = scan_gamma(fx["x"], fx["residual"])
    assert abs(scan["eml"]["bestGamma"] - FIRST_ZETA_ZERO_GAMMA) < 0.06
    assert scan["comparison"]["emlCloserToFirstKnownZero"] is True


def test_profiled_standard_basis_has_lower_mse_but_more_complexity():
    fx = fixture()
    scan = scan_gamma(fx["x"], fx["residual"])
    assert scan["comparison"]["standardLowerMse"] is True
    assert scan["standard"]["grammarOperatorNodes"] > scan["eml"]["grammarOperatorNodes"]
    assert scan["standard"]["freeParameterCount"] > scan["eml"]["freeParameterCount"]


def test_build_benchmark_writes_json_report_and_evidence(tmp_path):
    built = build_benchmark(tmp_path / "out", tmp_path / "reports", tmp_path / "evidence")
    result = json.loads(Path(built["result_path"]).read_text(encoding="utf-8"))
    evidence = json.loads(Path(built["evidence_path"]).read_text(encoding="utf-8"))
    assert result["status"] == "EML_PRIME_RESIDUAL_BENCHMARK_PASS"
    assert result["interpretation"]["nullResultAcceptable"] is True
    assert len(result["negativeControls"]) == 2
    assert evidence["reviewDecision"] == "candidate_only"
    validate_benchmark(result)


def test_claim_flags_remain_false(tmp_path):
    result = build_benchmark(tmp_path / "out", tmp_path / "reports", tmp_path / "evidence")["result"]
    assert all(value is False for value in result["claimFlags"].values())
    assert "does not prove RH" in " ".join(result["nonClaims"])


def test_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_prime_residual_benchmark.py",
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
    assert "EML_PRIME_RESIDUAL_BENCHMARK_OK" in proc.stdout
