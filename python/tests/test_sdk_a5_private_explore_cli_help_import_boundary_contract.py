"""Tests for SDK-A5 private explore CLI help import-boundary contract."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.sdk_a5_private_explore_cli_help_import_boundary_contract import (
    CLAIM_FLAGS,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_sdk_a5_consumes_sdk_a4_and_records_contract_counts():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "SDK_A5_PRIVATE_EXPLORE_CLI_HELP_IMPORT_BOUNDARY_CONTRACT_PASS"
    assert payload["sourceArtifact"] == "sdk-a4-private-sdk-smoke-result-review-selector"
    assert payload["summary"]["sourceFindingClassification"] == "optional_dependency_import_boundary"
    assert payload["summary"]["helpBoundaryObligationCount"] == 3
    assert payload["summary"]["dependencyGateObligationCount"] == 3
    assert payload["summary"]["blockedPathCount"] == 4


def test_sdk_a5_records_help_paths_that_should_not_import_optional_substrate():
    payload = build_payload()
    ids = {item["obligationId"] for item in payload["helpBoundaryObligations"]}
    assert ids == {
        "top_level_help_no_optional_substrate_import",
        "top_level_version_no_optional_substrate_import",
        "subcommand_help_no_optional_substrate_import",
    }
    assert all("optional substrate" in item["intendedSignal"] for item in payload["helpBoundaryObligations"])


def test_sdk_a5_records_dependency_gate_obligations_for_expression_commands():
    payload = build_payload()
    ids = {item["obligationId"] for item in payload["dependencyGateObligations"]}
    assert ids == {
        "witness_command_dependency_gate",
        "analyze_command_dependency_gate",
        "identify_command_dependency_gate",
    }
    assert all("clear dependency-gate error" in item["intendedSignal"] for item in payload["dependencyGateObligations"])


def test_sdk_a5_blocks_public_release_semantic_and_laptop_paths():
    payload = build_payload()
    blocked_ids = {item["blockedPathId"] for item in payload["blockedPaths"]}
    assert blocked_ids == {
        "public_release_readiness_from_help_fix",
        "install_optional_extras_in_contract",
        "claim_explore_semantics",
        "touch_laptop_owned_repos",
    }


def test_sdk_a5_blocks_implementation_execution_public_stability_runtime_and_repo_claims():
    payload = build_payload()
    for key in [
        "sdk_implementation_changed",
        "explore_cli_remediated",
        "remediation_test_executed",
        "smoke_probe_rerun",
        "optional_dependency_installed",
        "sdk_stability_claim",
        "sdk_public_ready",
        "public_readiness_claim",
        "public_package_release_claim",
        "api_compatibility_claim",
        "semantic_versioning_commitment",
        "compiler_correctness_claim",
        "semantic_preservation_claim",
        "runtime_performance_claim",
        "training_savings_claim",
        "hardware_readiness_claim",
        "silicon_readiness_claim",
        "electronics_repo_touched",
        "laptop_owned_repo_touched",
        "d110_started",
        "reviewer_response_consumed",
        "reviewer_approval_recorded",
        "broad_eml_advantage_claim",
        "public_package_install_executed",
        "benchmark_executed",
        "forge_emit_check_executed",
    ]:
        assert payload["claimFlags"][key] is False


def test_sdk_a5_selects_sdk_a6_implementation_next():
    payload = build_payload()
    assert (
        payload["summary"]["nextRecommendedArtifact"]
        == "SDK-A6 private explore CLI help import-boundary remediation implementation"
    )


def test_sdk_a5_claim_flags_are_contract_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_sdk_a5_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# SDK-A5")


def test_sdk_a5_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/sdk_a5_private_explore_cli_help_import_boundary_contract.py",
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
    assert "SDK_A5_PRIVATE_EXPLORE_CLI_HELP_IMPORT_BOUNDARY_CONTRACT_OK" in proc.stdout
