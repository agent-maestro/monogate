"""Tests for EML-A9.1 guard rule fixtures."""

from __future__ import annotations

import subprocess
import sys

from scripts.eml_a9_1_guard_rule_fixtures import CLAIM_FLAGS, build_fixtures, validate_payload


def build_tmp(tmp_path):
    return build_fixtures(tmp_path / "results", tmp_path / "packets", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")


def test_fixtures_cover_guard_decisions(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    assert payload["status"] == "EML_A9_1_GUARD_RULE_FIXTURES_PASS"
    assert payload["summary"]["fixtureCount"] >= 6
    assert payload["summary"]["byExpectedDecision"]["recommend_protected_lowering"] >= 2
    assert payload["summary"]["byExpectedDecision"]["block_unstable_deep_tree"] >= 1
    validate_payload(payload)


def test_fixture_layer_changes_no_compiler_behavior(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    assert payload["summary"]["compilerBehaviorChanged"] is False
    assert payload["summary"]["guardAnalyzerImplemented"] is False
    assert payload["summary"]["compilerCorrectnessClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())


def test_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [sys.executable, "python/scripts/eml_a9_1_guard_rule_fixtures.py", "--build", "--out-dir", str(tmp_path / "results"), "--packet-dir", str(tmp_path / "packets"), "--report-dir", str(tmp_path / "reports"), "--evidence-dir", str(tmp_path / "evidence"), "--command-feed-dir", str(tmp_path / "feeds"), "--strict"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "EML_A9_1_GUARD_RULE_FIXTURES_OK" in proc.stdout
