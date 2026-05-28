"""Tests for EML-A11.1 mock compiler holdouts."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from scripts.eml_a11_1_mock_compiler_holdouts import build_holdouts, validate_payload


def build_tmp(tmp_path):
    return build_holdouts(
        Path("python/fixtures/eml_expression_holdout_packets"),
        tmp_path / "results",
        tmp_path / "holdout_packets",
        tmp_path / "decision_packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )


def decisions_by_program(payload):
    return {packet["programId"]: packet for packet in payload["decisionPackets"]}


def test_holdout_set_covers_decision_classes(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    assert payload["status"] == "EML_A11_1_MOCK_COMPILER_HOLDOUTS_PASS"
    assert payload["summary"]["holdoutCount"] >= 6
    assert payload["summary"]["protectedRuntimeLoweringCount"] >= 2
    assert payload["summary"]["blockedRequiresEvidenceCount"] >= 2
    assert payload["summary"]["proofShapeOnlyCount"] >= 2
    validate_payload(payload)


def test_expm1_holdout_routes_to_protected_lowering(tmp_path):
    packet = decisions_by_program(build_tmp(tmp_path)["payload"])["expm1_near_zero_holdout_v0"]
    assert packet["guardDecision"] == "recommend_protected_lowering"
    assert packet["compilerDecision"] == "protected_runtime_lowering"
    assert packet["runtimeTarget"] == "expm1-style protected lowering"


def test_deep_fold_holdout_blocks_for_evidence(tmp_path):
    packet = decisions_by_program(build_tmp(tmp_path)["payload"])["deep_fold_holdout_v0"]
    assert packet["guardDecision"] == "block_unstable_deep_tree"
    assert packet["compilerDecision"] == "blocked_requires_evidence"


def test_subtraction_boundary_holdout_stays_proof_shape(tmp_path):
    packet = decisions_by_program(build_tmp(tmp_path)["payload"])["subtraction_boundary_holdout_v0"]
    assert packet["guardDecision"] == "allow_proof_shape"
    assert packet["compilerDecision"] == "proof_shape_only"
    assert "subtraction_boundary_guarded_v0" in packet["matchedRuleIds"]


def test_holdout_claims_remain_false(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    assert payload["summary"]["realCompilerBehaviorChanged"] is False
    assert payload["summary"]["compilerCorrectnessClaim"] is False
    assert payload["summary"]["productionReady"] is False
    assert payload["summary"]["claimFlagsAllFalse"] is True


def test_holdout_cli(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_a11_1_mock_compiler_holdouts.py",
            "--build",
            "--out-dir",
            str(tmp_path / "results"),
            "--holdout-packet-dir",
            str(tmp_path / "holdout_packets"),
            "--decision-packet-dir",
            str(tmp_path / "decision_packets"),
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
    assert "EML_A11_1_MOCK_COMPILER_HOLDOUTS_OK" in proc.stdout
