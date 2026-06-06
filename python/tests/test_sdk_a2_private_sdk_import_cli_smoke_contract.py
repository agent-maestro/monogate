"""Tests for SDK-A2 private SDK import and CLI smoke contract."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.sdk_a2_private_sdk_import_cli_smoke_contract import (
    CLAIM_FLAGS,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_sdk_a2_consumes_sdk_a1_and_records_probe_contracts():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "SDK_A2_PRIVATE_SDK_IMPORT_CLI_SMOKE_CONTRACT_PASS"
    assert payload["sourceArtifact"] == "sdk-a1-private-sdk-surface-inventory"
    assert payload["summary"]["importProbeContractCount"] == 4
    assert payload["summary"]["cliProbeContractCount"] == 4
    assert payload["summary"]["blockedProbeContractCount"] == 4


def test_sdk_a2_records_expected_import_and_cli_probe_ids():
    payload = build_payload()
    import_ids = {probe["probeId"] for probe in payload["importProbeContracts"]}
    cli_ids = {probe["probeId"] for probe in payload["cliProbeContracts"]}
    assert import_ids == {
        "python_import_monogate",
        "python_import_monogate_validate",
        "python_import_monogate_core_optional",
        "forge_preview_import_optional",
    }
    assert cli_ids == {
        "cli_monogate_capability_card_help",
        "cli_monogate_explore_help",
        "cli_monogate_validate_help",
        "cli_forge_preview_help_optional",
    }


def test_sdk_a2_executes_no_imports_or_clis():
    payload = build_payload()
    assert payload["summary"]["importProbeExecuted"] is False
    assert payload["summary"]["cliProbeExecuted"] is False
    for probe in payload["importProbeContracts"] + payload["cliProbeContracts"]:
        assert probe["executionStatus"] == "not_executed_contract_only"


def test_sdk_a2_blocks_risky_probe_contracts():
    payload = build_payload()
    blocked_ids = {probe["blockedProbeId"] for probe in payload["blockedProbeContracts"]}
    assert blocked_ids == {
        "native_benchmark_execution",
        "forge_emit_or_check_execution",
        "electronics_repo_cli_probe",
        "public_package_install_probe",
    }


def test_sdk_a2_blocks_stability_public_compiler_runtime_and_repo_touch_claims():
    payload = build_payload()
    for key in [
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
        "sdk_implementation_changed",
        "native_extension_required",
        "forge_preview_public_ready",
    ]:
        assert payload["claimFlags"][key] is False


def test_sdk_a2_selects_private_dry_run_next():
    payload = build_payload()
    assert payload["summary"]["nextRecommendedArtifact"] == "SDK-A3 private SDK import and CLI smoke dry run"


def test_sdk_a2_claim_flags_are_contract_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_sdk_a2_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# SDK-A2")


def test_sdk_a2_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/sdk_a2_private_sdk_import_cli_smoke_contract.py",
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
    assert "SDK_A2_PRIVATE_SDK_IMPORT_CLI_SMOKE_CONTRACT_OK" in proc.stdout
