"""Tests for SDK-A4 private SDK smoke result review selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.sdk_a4_private_sdk_smoke_result_review_selector import (
    CLAIM_FLAGS,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_sdk_a4_consumes_sdk_a3_and_reviews_single_finding():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "SDK_A4_PRIVATE_SDK_SMOKE_RESULT_REVIEW_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "sdk-a3-private-sdk-import-cli-smoke-dry-run"
    assert payload["summary"]["requiredProbeFailureCount"] == 1
    assert payload["summary"]["selectedFindingId"] == "sdk_a3_cli_monogate_explore_help_required_probe_failed"


def test_sdk_a4_classifies_explore_help_as_optional_dependency_import_boundary():
    payload = build_payload()
    review = payload["findingReview"]
    assert review["sourceProbeId"] == "cli_monogate_explore_help"
    assert review["sourceResultStatus"] == "required_probe_failed"
    assert review["classification"] == "optional_dependency_import_boundary"
    assert "eml_discover" in review["observedSignal"]
    assert any("eml-discover" in item for item in review["packagingContext"])


def test_sdk_a4_selects_remediation_contract_before_implementation():
    payload = build_payload()
    selected = [action for action in payload["candidateActions"] if action["decision"] == "selected"]
    assert len(selected) == 1
    assert selected[0]["actionId"] == "explore_cli_help_import_boundary_remediation_contract"
    assert selected[0]["nextArtifact"] == "SDK-A5 private explore CLI help import-boundary remediation contract"
    assert all(action["implementationStarted"] is False for action in payload["candidateActions"])


def test_sdk_a4_parks_reclassification_install_and_direct_fix_paths():
    payload = build_payload()
    decisions = {action["actionId"]: action["decision"] for action in payload["candidateActions"]}
    assert decisions["reclassify_explore_probe_optional"] == "parked"
    assert decisions["install_cli_extra_and_rerun_smoke"] == "parked"
    assert decisions["direct_code_fix"] == "blocked_in_sdk_a4"


def test_sdk_a4_blocks_implementation_public_stability_runtime_and_repo_touch_claims():
    payload = build_payload()
    for key in [
        "sdk_implementation_changed",
        "explore_cli_remediated",
        "smoke_probe_rerun",
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


def test_sdk_a4_selects_sdk_a5_next():
    payload = build_payload()
    assert (
        payload["summary"]["nextRecommendedArtifact"]
        == "SDK-A5 private explore CLI help import-boundary remediation contract"
    )


def test_sdk_a4_claim_flags_are_selector_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_sdk_a4_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# SDK-A4")


def test_sdk_a4_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/sdk_a4_private_sdk_smoke_result_review_selector.py",
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
    assert "SDK_A4_PRIVATE_SDK_SMOKE_RESULT_REVIEW_SELECTOR_OK" in proc.stdout
