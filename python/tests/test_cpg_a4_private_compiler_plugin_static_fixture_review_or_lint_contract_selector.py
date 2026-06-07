"""Tests for CPG-A4 private static fixture review/lint contract selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.cpg_a4_private_compiler_plugin_static_fixture_review_or_lint_contract_selector import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_cpg_a4_consumes_cpg_a3():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "CPG_A4_PRIVATE_COMPILER_PLUGIN_STATIC_FIXTURE_REVIEW_OR_LINT_CONTRACT_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "cpg-a3-private-compiler-plugin-guard-note-static-fixture-packet"


def test_cpg_a4_review_checks_pass():
    payload = build_payload()
    assert payload["summary"]["reviewCheckCount"] == 6
    assert payload["summary"]["reviewPassCount"] == 6
    assert payload["summary"]["reviewFailCount"] == 0
    assert {check["status"] for check in payload["reviewChecks"]} == {"pass"}


def test_cpg_a4_selects_lint_contract_boundary_packet():
    payload = build_payload()
    assert payload["summary"]["selectedActionId"] == "executable_lint_contract_boundary_packet"
    assert payload["summary"]["selectedNextArtifact"] == NEXT_RECOMMENDED_ARTIFACT
    assert payload["summary"]["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_cpg_a4_parks_revision_and_blocks_implementation_and_public_docs():
    payload = build_payload()
    decisions = {action["actionId"]: action["decision"] for action in payload["candidateNextActions"]}
    assert decisions["static_fixture_revision_packet"] == "parked"
    assert decisions["compiler_plugin_implementation"] == "blocked"
    assert decisions["public_docs_or_package"] == "blocked"


def test_cpg_a4_blocks_contract_execution_plugin_lint_runtime_and_public_claims():
    payload = build_payload()
    for key in [
        "executable_lint_contract_created",
        "executable_lint_contract_executed",
        "compiler_plugin_implemented",
        "compiler_plugin_executed",
        "lint_engine_implemented",
        "lint_engine_executed",
        "fixture_runner_implemented",
        "fixture_runner_executed",
        "fixture_revision_created",
        "compiler_correctness_claim",
        "semantic_preservation_claim",
        "automatic_lowering_safety_claim",
        "runtime_performance_claim",
        "code_generation_claim",
        "runtime_lowering_changed",
        "sdk_stability_claim",
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


def test_cpg_a4_claim_flags_are_selector_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_cpg_a4_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# CPG-A4")
    assert "Review Checks" in report


def test_cpg_a4_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/cpg_a4_private_compiler_plugin_static_fixture_review_or_lint_contract_selector.py",
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
    assert "CPG_A4_PRIVATE_COMPILER_PLUGIN_STATIC_FIXTURE_REVIEW_OR_LINT_CONTRACT_SELECTOR_OK" in proc.stdout
