"""Tests for EML-A11.2 protected lowering benchmark."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from scripts.eml_a11_2_protected_lowering_benchmark import build_benchmark, validate_payload


def build_tmp(tmp_path):
    return build_benchmark(
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )


def case_by_id(payload, case_id):
    return next(case for case in payload["cases"] if case["caseId"] == case_id)


def test_protected_lowering_benchmark_records_two_cases(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    assert payload["status"] == "EML_A11_2_PROTECTED_LOWERING_BENCHMARK_PASS"
    assert payload["summary"]["caseCount"] == 2
    assert payload["summary"]["sampleCount"] >= 18
    validate_payload(payload)


def test_expm1_is_no_worse_on_near_zero_grid(tmp_path):
    case = case_by_id(build_tmp(tmp_path)["payload"], "expm1_near_zero")
    assert case["recommendedLowering"] == "expm1-style protected lowering"
    assert case["protectedNoWorseCount"] == case["sampleCount"]
    assert case["protectedNonFiniteCount"] == 0


def test_logsumexp_avoids_naive_nonfinite_edges(tmp_path):
    case = case_by_id(build_tmp(tmp_path)["payload"], "logsumexp_edge_grid")
    assert case["recommendedLowering"] == "logaddexp-style protected lowering"
    assert case["naiveNonFiniteCount"] >= 1
    assert case["protectedNonFiniteCount"] == 0


def test_runtime_and_compiler_claims_remain_false(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    summary = payload["summary"]
    assert summary["runtimePerformanceClaim"] is False
    assert summary["compilerImplementationClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["productionReady"] is False
    assert summary["claimFlagsAllFalse"] is True


def test_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_a11_2_protected_lowering_benchmark.py",
            "--build",
            "--out-dir",
            str(tmp_path / "results"),
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
    assert "EML_A11_2_PROTECTED_LOWERING_BENCHMARK_OK" in proc.stdout
