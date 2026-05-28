"""Tests for EML-A11 mock compiler decisions."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from scripts.eml_a11_mock_compiler_decision import build_mock_decisions, validate_payload


def build_tmp(tmp_path):
    return build_mock_decisions(
        Path("python/fixtures/eml_expression_packets"),
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )


def decisions_by_program(payload):
    return {packet["programId"]: packet for packet in payload["decisionPackets"]}


def test_mock_compiler_decisions_cover_all_guard_outcomes(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    assert payload["status"] == "EML_A11_MOCK_COMPILER_DECISION_PASS"
    assert payload["summary"]["protectedRuntimeLoweringCount"] >= 1
    assert payload["summary"]["blockedRequiresEvidenceCount"] >= 1
    assert payload["summary"]["proofShapeOnlyCount"] >= 1
    validate_payload(payload)


def test_softplus_routes_to_protected_lowering(tmp_path):
    softplus = decisions_by_program(build_tmp(tmp_path)["payload"])["softplus_pair_v0"]
    assert softplus["compilerDecision"] == "protected_runtime_lowering"
    assert softplus["runtimeTarget"] == "logaddexp-style protected lowering"


def test_sigmoid_is_blocked_for_evidence(tmp_path):
    sigmoid = decisions_by_program(build_tmp(tmp_path)["payload"])["sigmoid_derivative_v0"]
    assert sigmoid["compilerDecision"] == "blocked_requires_evidence"
    assert sigmoid["realCompilerBehaviorChanged"] is False


def test_gaussian_remains_proof_shape_only(tmp_path):
    gaussian = decisions_by_program(build_tmp(tmp_path)["payload"])["gaussian_energy_v0"]
    assert gaussian["compilerDecision"] == "proof_shape_only"
    assert gaussian["compilerCorrectnessClaim"] is False


def test_mock_compiler_cli(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_a11_mock_compiler_decision.py",
            "--build",
            "--out-dir",
            str(tmp_path / "results"),
            "--decision-packet-dir",
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
    assert "EML_A11_MOCK_COMPILER_DECISION_OK" in proc.stdout
