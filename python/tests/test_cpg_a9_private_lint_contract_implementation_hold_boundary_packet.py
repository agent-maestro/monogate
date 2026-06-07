"""Tests for CPG-A9 private lint contract implementation hold boundary packet."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.cpg_a9_private_lint_contract_implementation_hold_boundary_packet import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_cpg_a9_consumes_cpg_a8():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "CPG_A9_PRIVATE_LINT_CONTRACT_IMPLEMENTATION_HOLD_BOUNDARY_PACKET_PASS"
    assert payload["sourceArtifact"] == "cpg-a8-private-lint-contract-static-fixture-review-or-implementation-hold-selector"


def test_cpg_a9_records_preconditions_and_blocked_surfaces():
    payload = build_payload()
    assert payload["summary"]["implementationPreconditionCount"] == 4
    assert payload["summary"]["blockedImplementationSurfaceCount"] == 4
    assert payload["summary"]["reviewerQuestionCount"] == 4
    assert {item["preconditionId"] for item in payload["implementationPreconditions"]} == {
        "review_cpg_a7_static_fixtures",
        "draft_executable_static_test_contract",
        "separate_reviewer_approval_required",
        "public_docs_gate_required",
    }
    assert {item["surfaceId"] for item in payload["blockedImplementationSurfaces"]} == {
        "compiler_plugin_runtime_behavior",
        "lint_engine_execution",
        "automatic_rewrite_or_lowering",
        "public_release_surface",
    }


def test_cpg_a9_points_to_hold_review_or_pause_selector():
    payload = build_payload()
    assert payload["summary"]["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT
    assert "CPG-A10" in payload["summary"]["nextRecommendedArtifact"]


def test_cpg_a9_does_not_approve_implementation_or_scope():
    payload = build_payload()
    assert payload["summary"]["implementationHoldApproved"] is False
    assert payload["summary"]["implementationScopeApproved"] is False
    for key in [
        "implementation_hold_approved",
        "implementation_scope_approved",
        "lint_contract_static_tests_created",
        "lint_contract_static_tests_executed",
        "executable_lint_contract_created",
        "executable_lint_contract_executed",
        "lint_contract_implementation_created",
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


def test_cpg_a9_claim_flags_are_boundary_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_cpg_a9_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# CPG-A9")
    assert "Implementation Preconditions" in report
    assert "Blocked Implementation Surfaces" in report


def test_cpg_a9_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/cpg_a9_private_lint_contract_implementation_hold_boundary_packet.py",
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
    assert "CPG_A9_PRIVATE_LINT_CONTRACT_IMPLEMENTATION_HOLD_BOUNDARY_PACKET_OK" in proc.stdout
