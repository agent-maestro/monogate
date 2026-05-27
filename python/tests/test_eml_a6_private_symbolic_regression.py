"""Tests for EML-A6 private symbolic-regression harness."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_a6_private_symbolic_regression import build_private_run, validate_private_run


def test_private_run_records_no_full_pysr_claim(tmp_path):
    result = build_private_run(tmp_path / "out", tmp_path / "reports", tmp_path / "evidence")["result"]
    assert result["visibility"] == "private_only"
    assert result["pysr"]["fullRunPerformed"] is False
    assert result["claimFlags"]["pysr_run_claim"] is False
    assert result["fallback"]["status"] == "EML_SYMBOLIC_REGRESSION_TEMPLATE_SEARCH_PASS"
    validate_private_run(result)


def test_private_run_writes_json_report_and_evidence(tmp_path):
    built = build_private_run(tmp_path / "out", tmp_path / "reports", tmp_path / "evidence")
    result = json.loads(Path(built["result_path"]).read_text(encoding="utf-8"))
    evidence = json.loads(Path(built["evidence_path"]).read_text(encoding="utf-8"))
    assert result["status"].startswith("EML_A6_PRIVATE_SYMBOLIC_REGRESSION")
    assert evidence["reviewDecision"] == "blocked_environment_dependency"
    assert evidence["claimFlags"]["autonomous_discovery_claim"] is False
    validate_private_run(result)


def test_validate_private_run_allows_captured_pysr_run(tmp_path):
    result = build_private_run(tmp_path / "out", tmp_path / "reports", tmp_path / "evidence")["result"]
    result["status"] = "EML_A6_PRIVATE_SYMBOLIC_REGRESSION_PYSR_RUN_PASS"
    result["pysr"]["fullRunPerformed"] = True
    result["claimFlags"]["pysr_run_claim"] = True
    result["pysrRun"] = {"runs": [{}, {}, {}, {}, {}, {}], "targetComparison": {}}
    validate_private_run(result)


def test_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_a6_private_symbolic_regression.py",
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
    assert "EML_A6_PRIVATE_SYMBOLIC_REGRESSION_OK" in proc.stdout
