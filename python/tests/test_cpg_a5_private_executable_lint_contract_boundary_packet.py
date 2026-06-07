"""Tests for CPG-A5 private executable lint contract boundary packet."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.cpg_a5_private_executable_lint_contract_boundary_packet import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_cpg_a5_consumes_cpg_a4():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "CPG_A5_PRIVATE_EXECUTABLE_LINT_CONTRACT_BOUNDARY_PACKET_PASS"
    assert payload["sourceArtifact"] == "cpg-a4-private-compiler-plugin-static-fixture-review-or-lint-contract-selector"


def test_cpg_a5_records_contract_shapes_and_obligations():
    payload = build_payload()
    assert payload["summary"]["inputFieldCount"] == 4
    assert payload["summary"]["outputFieldCount"] == 4
    assert payload["summary"]["rejectionObligationCount"] == 4
    assert payload["summary"]["executionGateCount"] == 4
    assert {item["field"] for item in payload["contractInputShape"]} == {
        "source_snippet",
        "expression_family",
        "evidence_pointer",
        "guard_context",
    }
    assert {item["output"] for item in payload["contractOutputShape"]} == {
        "advisory_notice",
        "guard_checklist_item",
        "evidence_pointer",
        "blocked_claim_notice",
    }


def test_cpg_a5_rejection_obligations_block_dangerous_claims():
    payload = build_payload()
    obligations = {item["obligationId"]: item for item in payload["contractRejectionObligations"]}
    assert "automatic_rewrite" in obligations["reject_automatic_rewrite_or_lowering"]["mustReject"]
    assert "runtime_speedup" in obligations["reject_runtime_or_training_savings_claim"]["mustReject"]
    assert "package_release_ready" in obligations["reject_public_or_package_readiness_claim"]["mustReject"]
    assert "guard_proven" in obligations["reject_guard_proven_or_theorem_discovered_claim"]["mustReject"]


def test_cpg_a5_records_execution_gates_before_implementation():
    payload = build_payload()
    gates = {gate["gateId"]: gate["status"] for gate in payload["executionGates"]}
    assert gates["contract_boundary_review_required"] == "required_before_static_tests"
    assert gates["static_test_fixtures_required"] == "required_before_implementation"
    assert gates["implementation_hold_gate_required"] == "required_before_any_lint_engine"
    assert gates["public_docs_gate_required"] == "required_before_public_copy"


def test_cpg_a5_selects_boundary_review_or_static_test_selector():
    payload = build_payload()
    assert payload["summary"]["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT
    assert "CPG-A6" in payload["summary"]["nextRecommendedArtifact"]


def test_cpg_a5_keeps_execution_implementation_and_claims_false():
    payload = build_payload()
    for key in [
        "executable_lint_contract_created",
        "executable_lint_contract_executed",
        "lint_contract_implementation_created",
        "lint_contract_static_tests_created",
        "lint_contract_static_tests_executed",
        "compiler_plugin_implemented",
        "compiler_plugin_executed",
        "lint_engine_implemented",
        "lint_engine_executed",
        "fixture_runner_implemented",
        "fixture_runner_executed",
        "automatic_rewrite_enabled",
        "compiler_correctness_claim",
        "semantic_preservation_claim",
        "automatic_lowering_safety_claim",
        "runtime_performance_claim",
        "public_readiness_claim",
        "public_package_release_claim",
        "electronics_repo_touched",
        "laptop_owned_repo_touched",
        "d110_started",
        "reviewer_response_consumed",
        "reviewer_approval_recorded",
        "broad_eml_advantage_claim",
    ]:
        assert payload["claimFlags"][key] is False


def test_cpg_a5_claim_flags_are_boundary_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_cpg_a5_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# CPG-A5")
    assert "Contract Input Shape" in report
    assert "Rejection Obligations" in report


def test_cpg_a5_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/cpg_a5_private_executable_lint_contract_boundary_packet.py",
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
    assert "CPG_A5_PRIVATE_EXECUTABLE_LINT_CONTRACT_BOUNDARY_PACKET_OK" in proc.stdout
