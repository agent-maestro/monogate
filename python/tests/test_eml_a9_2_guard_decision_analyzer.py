"""Tests for EML-A9.2 guard decision analyzer."""

from __future__ import annotations

import subprocess
import sys

from scripts.eml_a9_2_guard_decision_analyzer import CLAIM_FLAGS, build_decisions, validate_payload


def build_tmp(tmp_path):
    return build_decisions(tmp_path / "results", tmp_path / "packets", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")


def test_decisions_match_fixtures(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    assert payload["status"] == "EML_A9_2_GUARD_DECISION_ANALYZER_PASS"
    assert payload["summary"]["decisionCount"] >= 6
    assert payload["summary"]["allFixturesMatched"] is True
    validate_payload(payload)


def test_decision_classes_include_blocks_and_lowerings(tmp_path):
    decisions = build_tmp(tmp_path)["payload"]["summary"]["byDecision"]
    assert decisions["recommend_protected_lowering"] >= 2
    assert decisions["block_missing_domain_guard"] >= 1
    assert decisions["block_unstable_deep_tree"] >= 1
    assert decisions["block_claim_until_evidence"] >= 1


def test_analyzer_changes_no_compiler_behavior(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    assert payload["summary"]["compilerBehaviorChanged"] is False
    assert payload["summary"]["compilerCorrectnessClaim"] is False
    assert payload["summary"]["productionReady"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())


def test_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [sys.executable, "python/scripts/eml_a9_2_guard_decision_analyzer.py", "--build", "--out-dir", str(tmp_path / "results"), "--packet-dir", str(tmp_path / "packets"), "--report-dir", str(tmp_path / "reports"), "--evidence-dir", str(tmp_path / "evidence"), "--command-feed-dir", str(tmp_path / "feeds"), "--strict"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "EML_A9_2_GUARD_DECISION_ANALYZER_OK" in proc.stdout
