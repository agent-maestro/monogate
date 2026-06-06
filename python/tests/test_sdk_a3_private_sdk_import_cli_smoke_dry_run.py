"""Tests for SDK-A3 private SDK import and CLI smoke dry run."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.sdk_a3_private_sdk_import_cli_smoke_dry_run import (
    CLAIM_FLAGS,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_sdk_a3_consumes_sdk_a2_and_executes_expected_probe_counts():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "SDK_A3_PRIVATE_SDK_IMPORT_CLI_SMOKE_DRY_RUN_FINDING"
    assert payload["sourceArtifact"] == "sdk-a2-private-sdk-import-cli-smoke-contract"
    assert payload["summary"]["importProbeDryRunCount"] == 4
    assert payload["summary"]["cliProbeDryRunCount"] == 4
    assert payload["summary"]["blockedProbeExecutionCount"] == 0


def test_sdk_a3_required_import_probes_pass_and_native_optional_is_missing():
    payload = build_payload()
    results = {result["probeId"]: result for result in payload["importProbeResults"]}
    assert results["python_import_monogate"]["resultStatus"] == "pass"
    assert results["python_import_monogate_validate"]["resultStatus"] == "pass"
    assert results["python_import_monogate_core_optional"]["resultStatus"] == "optional_missing"
    assert results["forge_preview_import_optional"]["resultStatus"] == "pass"


def test_sdk_a3_cli_smoke_records_one_current_required_finding():
    payload = build_payload()
    results = {result["probeId"]: result for result in payload["cliProbeResults"]}
    assert results["cli_monogate_capability_card_help"]["resultStatus"] == "pass"
    assert results["cli_monogate_explore_help"]["resultStatus"] == "required_probe_failed"
    assert "eml_discover" in results["cli_monogate_explore_help"]["stderrPreview"]
    assert results["cli_monogate_validate_help"]["resultStatus"] == "pass"
    assert results["cli_forge_preview_help_optional"]["resultStatus"] == "pass"
    assert payload["summary"]["requiredProbeFailureCount"] == 1


def test_sdk_a3_executes_no_blocked_probe_contracts():
    payload = build_payload()
    blocked_ids = {probe["blockedProbeId"] for probe in payload["blockedProbeContracts"]}
    assert blocked_ids == {
        "native_benchmark_execution",
        "forge_emit_or_check_execution",
        "electronics_repo_cli_probe",
        "public_package_install_probe",
    }
    assert payload["summary"]["blockedProbeExecutionCount"] == 0


def test_sdk_a3_blocks_stability_public_compiler_runtime_and_repo_touch_claims():
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
        "public_package_install_executed",
        "benchmark_executed",
        "forge_emit_check_executed",
    ]:
        assert payload["claimFlags"][key] is False


def test_sdk_a3_selects_review_selector_next():
    payload = build_payload()
    assert (
        payload["summary"]["nextRecommendedArtifact"]
        == "SDK-A4 private SDK smoke result review and explore CLI surface selector"
    )


def test_sdk_a3_claim_flags_are_dry_run_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_sdk_a3_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# SDK-A3")


def test_sdk_a3_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/sdk_a3_private_sdk_import_cli_smoke_dry_run.py",
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
    assert "SDK_A3_PRIVATE_SDK_IMPORT_CLI_SMOKE_DRY_RUN_OK" in proc.stdout
