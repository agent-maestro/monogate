"""Tests for SDK-A8 private SDK smoke chain pause or docs selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.sdk_a8_private_sdk_smoke_chain_pause_or_docs_selector import (
    CLAIM_FLAGS,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_sdk_a8_consumes_sdk_a7_and_selects_pause():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "SDK_A8_PRIVATE_SDK_SMOKE_CHAIN_PAUSE_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "sdk-a7-private-sdk-smoke-chain-refresh-after-explore-cli-remediation"
    assert payload["summary"]["sourceRequiredProbeFailureCount"] == 0
    assert payload["summary"]["sourceExploreCliHelpStatus"] == "pass"
    assert payload["summary"]["selectedActionId"] == "pause_sdk_smoke_lane_as_seeded"


def test_sdk_a8_records_expected_candidate_actions():
    payload = build_payload()
    decisions = {action["actionId"]: action["decision"] for action in payload["candidateActions"]}
    assert decisions == {
        "pause_sdk_smoke_lane_as_seeded": "selected",
        "private_docs_note_packet": "parked",
        "public_docs_packet": "blocked",
        "more_smoke_chain_expansion": "parked",
    }


def test_sdk_a8_blocks_docs_public_and_more_smoke_side_effects():
    payload = build_payload()
    assert payload["summary"]["sdkSmokeChainSeeded"] is True
    assert payload["summary"]["docsNoteCreated"] is False
    assert payload["summary"]["publicDocsCreated"] is False
    assert payload["summary"]["smokeProbeRerun"] is False


def test_sdk_a8_blocks_public_stability_runtime_and_repo_claims():
    payload = build_payload()
    for key in [
        "sdk_implementation_changed",
        "docs_note_created",
        "public_docs_created",
        "smoke_probe_rerun",
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


def test_sdk_a8_claim_flags_are_selector_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_sdk_a8_next_action_returns_to_product_selector():
    payload = build_payload()
    assert (
        payload["summary"]["nextRecommendedArtifact"]
        == "Return to product-roadmap selector or next concrete private product/tooling lane."
    )


def test_sdk_a8_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# SDK-A8")


def test_sdk_a8_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/sdk_a8_private_sdk_smoke_chain_pause_or_docs_selector.py",
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
    assert "SDK_A8_PRIVATE_SDK_SMOKE_CHAIN_PAUSE_OR_DOCS_SELECTOR_OK" in proc.stdout
