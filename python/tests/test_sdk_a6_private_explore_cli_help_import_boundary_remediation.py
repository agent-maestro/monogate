"""Tests for SDK-A6 private explore CLI help import-boundary remediation."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.sdk_a6_private_explore_cli_help_import_boundary_remediation import (
    CLAIM_FLAGS,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_sdk_a6_consumes_sdk_a5_and_records_implementation_scope():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "SDK_A6_PRIVATE_EXPLORE_CLI_HELP_IMPORT_BOUNDARY_REMEDIATION_PASS"
    assert payload["sourceArtifact"] == "sdk-a5-private-explore-cli-help-import-boundary-contract"
    assert payload["summary"]["implementationChangedFiles"] == ["python/monogate/cli/explore.py"]
    assert payload["summary"]["testFilesAdded"] == ["python/tests/test_cli_explore_import_boundary.py"]


def test_sdk_a6_help_boundary_commands_pass_without_tracebacks():
    payload = build_payload()
    results = {item["commandId"]: item for item in payload["commandResults"]}
    for command_id in [
        "top_level_help_no_optional_substrate_import",
        "top_level_version_no_optional_substrate_import",
        "subcommand_help_no_optional_substrate_import",
    ]:
        assert results[command_id]["resultStatus"] == "pass"
        assert results[command_id]["returnCode"] == 0
        assert "Traceback" not in results[command_id]["stderrPreview"]


def test_sdk_a6_dependency_gate_commands_pass_or_gate_cleanly():
    payload = build_payload()
    results = {item["commandId"]: item for item in payload["commandResults"]}
    for command_id in [
        "witness_command_dependency_gate",
        "analyze_command_dependency_gate",
        "identify_command_dependency_gate",
    ]:
        assert results[command_id]["resultStatus"] == "pass"
        assert results[command_id]["returnCode"] in {0, 2}
        combined = results[command_id]["stdoutPreview"] + results[command_id]["stderrPreview"]
        assert "Traceback" not in combined
        if results[command_id]["returnCode"] == 2:
            assert "optional dependency" in combined


def test_sdk_a6_blocks_public_stability_performance_and_repo_claims():
    payload = build_payload()
    for key in [
        "optional_dependency_installed",
        "public_package_install_executed",
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
        "benchmark_executed",
        "forge_emit_check_executed",
    ]:
        assert payload["claimFlags"][key] is False


def test_sdk_a6_true_claim_flags_are_bounded_to_import_boundary_remediation():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_sdk_a6_selects_smoke_chain_refresh_next():
    payload = build_payload()
    assert (
        payload["summary"]["nextRecommendedArtifact"]
        == "SDK-A7 private SDK smoke chain refresh after explore CLI remediation"
    )


def test_sdk_a6_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# SDK-A6")


def test_sdk_a6_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/sdk_a6_private_explore_cli_help_import_boundary_remediation.py",
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
    assert "SDK_A6_PRIVATE_EXPLORE_CLI_HELP_IMPORT_BOUNDARY_REMEDIATION_OK" in proc.stdout
