"""Tests for EML-A9.3 guard CI contract."""

from __future__ import annotations

import subprocess
import sys

from scripts.eml_a9_3_guard_ci_contract import CLAIM_FLAGS, build_contract, validate_contract


def build_tmp(tmp_path):
    return build_contract(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds", dev_copy_root=tmp_path / "missing-dev")


def test_guard_ci_contract_passes(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    assert payload["status"] == "EML_A9_3_GUARD_CI_CONTRACT_PASS"
    assert payload["summary"]["allPassed"] is True
    assert payload["summary"]["failedCount"] == 0
    validate_contract(payload)


def test_guard_contract_claim_flags_false(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert payload["summary"]["compilerBehaviorChanged"] is False
    assert payload["summary"]["compilerCorrectnessClaim"] is False
    assert payload["summary"]["productionReady"] is False


def test_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [sys.executable, "python/scripts/eml_a9_3_guard_ci_contract.py", "--build", "--out-dir", str(tmp_path / "results"), "--report-dir", str(tmp_path / "reports"), "--evidence-dir", str(tmp_path / "evidence"), "--command-feed-dir", str(tmp_path / "feeds"), "--dev-copy-root", str(tmp_path / "missing-dev"), "--strict"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "EML_A9_3_GUARD_CI_CONTRACT_OK" in proc.stdout
