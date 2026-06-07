"""Tests for CPG-A7 private lint contract static test fixture packet."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.cpg_a7_private_lint_contract_static_test_fixture_packet import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_cpg_a7_consumes_cpg_a6():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "CPG_A7_PRIVATE_LINT_CONTRACT_STATIC_TEST_FIXTURE_PACKET_PASS"
    assert payload["sourceArtifact"] == "cpg-a6-private-lint-contract-boundary-review-or-static-test-selector"


def test_cpg_a7_records_static_fixture_counts():
    payload = build_payload()
    assert payload["summary"]["acceptedStaticFixtureCount"] == 4
    assert payload["summary"]["rejectionStaticFixtureCount"] == 4
    assert payload["summary"]["staticFixtureCount"] == 8
    assert payload["summary"]["reviewerQuestionCount"] == 3


def test_cpg_a7_accepted_fixtures_cover_allowed_output_kinds():
    payload = build_payload()
    assert {fixture["expectedOutputKind"] for fixture in payload["acceptedStaticFixtures"]} == {
        "advisory_notice",
        "guard_checklist_item",
        "evidence_pointer",
        "blocked_claim_notice",
    }


def test_cpg_a7_rejection_fixtures_cover_blocked_output_kinds():
    payload = build_payload()
    assert {fixture["blockedOutputKind"] for fixture in payload["rejectionStaticFixtures"]} == {
        "automatic_rewrite",
        "runtime_speedup",
        "package_release_ready",
        "guard_proven",
    }


def test_cpg_a7_points_to_review_or_hold_selector():
    payload = build_payload()
    assert payload["summary"]["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT
    assert "CPG-A8" in payload["summary"]["nextRecommendedArtifact"]


def test_cpg_a7_keeps_static_test_execution_implementation_and_claims_false():
    payload = build_payload()
    for key in [
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


def test_cpg_a7_claim_flags_are_fixture_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_cpg_a7_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# CPG-A7")
    assert "Accepted Static Fixtures" in report
    assert "Rejection Static Fixtures" in report


def test_cpg_a7_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/cpg_a7_private_lint_contract_static_test_fixture_packet.py",
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
    assert "CPG_A7_PRIVATE_LINT_CONTRACT_STATIC_TEST_FIXTURE_PACKET_OK" in proc.stdout
