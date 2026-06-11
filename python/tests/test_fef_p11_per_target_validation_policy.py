"""Tests for FEF-P11 per-target validation policy."""

from __future__ import annotations

import pytest

# Blanket-marked heavy: CLI-contract test (subprocess.run of a
# script that loads large JSON evidence). Skipped from the fast
# dev loop via `pytest -m "not heavy"`; runs in CI by default.
# A follow-up measurement pass will UN-mark individual fast files.
pytestmark = pytest.mark.heavy

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p11_per_target_validation_policy import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p11_classifies_all_cli_targets():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "FEF_P11_PER_TARGET_VALIDATION_POLICY_PASS"
    assert payload["summary"]["targetCount"] == 36
    assert payload["summary"]["freeTargetCount"] == 13
    assert payload["summary"]["proTargetCount"] == 23
    assert payload["summary"]["unknownTierCount"] == 0


def test_fef_p11_keeps_non_python_javascript_policy_only():
    payload = build_payload()
    assert payload["summary"]["sampleGridValidatedTargets"] == ["javascript", "python"]
    assert payload["summary"]["policyOnlyTargetCount"] == 34
    by_target = {policy["target"]: policy for policy in payload["targetPolicies"]}
    assert by_target["python"]["currentEvidenceStatus"] == "selected_fixture_pass"
    assert by_target["javascript"]["currentEvidenceStatus"] == "selected_fixture_pass"
    assert by_target["c"]["currentEvidenceStatus"] == "policy_defined_evidence_open"
    assert by_target["verilog"]["validationLevel"] == "hardware_syntax_lint_candidate"
    assert by_target["lean"]["validationLevel"] == "formal_artifact_structural_only"
    assert by_target["zkproof"]["validationLevel"] == "zk_ir_structural_only"


def test_fef_p11_blocks_broad_target_claims():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["targetAllReadyClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    for policy in payload["targetPolicies"]:
        assert "target_all_readiness" in policy["blockedClaims"]
        assert "compiler_correctness" in policy["blockedClaims"]


def test_fef_p11_claim_flags_remain_false():
    payload = build_payload()
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p11_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P11")


def test_fef_p11_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p11_per_target_validation_policy.py",
            "--build",
            "--out-dir",
            str(tmp_path / "results"),
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
    assert "FEF_P11_PER_TARGET_VALIDATION_POLICY_OK" in proc.stdout
