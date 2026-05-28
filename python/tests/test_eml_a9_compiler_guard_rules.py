"""Tests for EML-A9 compiler guard rules."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_a9_compiler_guard_rules import CLAIM_FLAGS, build_rules, validate_payload


def build_tmp(tmp_path):
    return build_rules(
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )


def rule_by_id(payload, rule_id):
    return next(packet for packet in payload["rulePackets"] if packet["ruleId"] == rule_id)


def test_build_rules_outputs_registry(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    assert payload["status"] == "EML_A9_COMPILER_GUARD_RULES_PASS"
    assert payload["summary"]["ruleCount"] >= 6
    assert rule_by_id(payload, "block_unstable_deep_tree_v0")
    validate_payload(payload)


def test_rules_cover_required_classes(tmp_path):
    classes = build_tmp(tmp_path)["payload"]["summary"]["byRuleClass"]
    assert classes["protected_runtime_lowering"] >= 2
    assert classes["domain_guard"] >= 1
    assert classes["deep_tree_block"] >= 1
    assert classes["claim_gate"] >= 1


def test_no_compiler_behavior_change_claim(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    assert payload["summary"]["compilerBehaviorChanged"] is False
    assert payload["summary"]["compilerCorrectnessClaim"] is False
    assert payload["summary"]["guardRulesComplete"] is False
    for rule in payload["rulePackets"]:
        assert rule["implementedInCompiler"] is False
        assert rule["publicClaimAllowed"] is False


def test_deep_tree_rule_uses_a8_5_evidence(tmp_path):
    rule = rule_by_id(build_tmp(tmp_path)["payload"], "block_unstable_deep_tree_v0")
    assert rule["ruleClass"] == "deep_tree_block"
    assert any("a8_5" in path for path in rule["sourceEvidence"])


def test_claim_flags_remain_false(tmp_path):
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_tmp(tmp_path)["payload"]
    assert payload["summary"]["claimFlagsAllFalse"] is True
    for rule in payload["rulePackets"]:
        assert all(value is False for value in rule["claimFlags"].values())


def test_generated_json_files_parse(tmp_path):
    built = build_tmp(tmp_path)
    for path in [built["result_path"], built["evidence_path"], built["feed_path"]]:
        json.loads(Path(path).read_text(encoding="utf-8"))
    packets = sorted((tmp_path / "packets").glob("*_guard_rule_*.json"))
    assert len(packets) >= 6


def test_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_a9_compiler_guard_rules.py",
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
    assert "EML_A9_COMPILER_GUARD_RULES_OK" in proc.stdout
