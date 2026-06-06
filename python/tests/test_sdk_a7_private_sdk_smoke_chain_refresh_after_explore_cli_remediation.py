"""Tests for SDK-A7 private SDK smoke chain refresh after explore CLI remediation."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.sdk_a7_private_sdk_smoke_chain_refresh_after_explore_cli_remediation import (
    CLAIM_FLAGS,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_sdk_a7_consumes_sdk_a2_and_sdk_a6():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "SDK_A7_PRIVATE_SDK_SMOKE_CHAIN_REFRESH_PASS"
    assert payload["sourceArtifacts"] == [
        "sdk-a2-private-sdk-import-cli-smoke-contract",
        "sdk-a6-private-explore-cli-help-import-boundary-remediation",
    ]


def test_sdk_a7_all_required_smoke_probes_pass_after_remediation():
    payload = build_payload()
    assert payload["summary"]["requiredProbePassCount"] == 5
    assert payload["summary"]["requiredProbeFailureCount"] == 0
    for result in payload["importProbeResults"] + payload["cliProbeResults"]:
        if result["required"]:
            assert result["resultStatus"] == "pass"


def test_sdk_a7_records_explore_cli_help_finding_resolved():
    payload = build_payload()
    results = {result["probeId"]: result for result in payload["cliProbeResults"]}
    assert results["cli_monogate_explore_help"]["resultStatus"] == "pass"
    assert payload["summary"]["exploreCliHelpStatus"] == "pass"
    assert payload["summary"]["historicalSdkA3FindingResolved"] is True


def test_sdk_a7_optional_probes_remain_non_failing():
    payload = build_payload()
    results = {result["probeId"]: result for result in payload["importProbeResults"] + payload["cliProbeResults"]}
    assert results["python_import_monogate_core_optional"]["resultStatus"] == "optional_missing"
    assert results["forge_preview_import_optional"]["resultStatus"] == "pass"
    assert results["cli_forge_preview_help_optional"]["resultStatus"] == "pass"
    assert payload["summary"]["optionalProbeNonFailCount"] == 3


def test_sdk_a7_blocks_public_stability_runtime_and_repo_claims():
    payload = build_payload()
    for key in [
        "sdk_implementation_changed",
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


def test_sdk_a7_claim_flags_are_refresh_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_sdk_a7_selects_pause_or_docs_selector_next():
    payload = build_payload()
    assert (
        payload["summary"]["nextRecommendedArtifact"]
        == "SDK-A8 private SDK smoke chain pause or public-docs selector"
    )


def test_sdk_a7_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# SDK-A7")


def test_sdk_a7_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/sdk_a7_private_sdk_smoke_chain_refresh_after_explore_cli_remediation.py",
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
    assert "SDK_A7_PRIVATE_SDK_SMOKE_CHAIN_REFRESH_OK" in proc.stdout
