"""Tests for PROD-A7 private product roadmap return selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.prod_a7_private_product_roadmap_return_selector import (
    CLAIM_FLAGS,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_prod_a7_consumes_prod_a1_and_sdk_a8():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "PROD_A7_PRIVATE_PRODUCT_ROADMAP_RETURN_SELECTOR_PASS"
    assert payload["sourceArtifacts"] == [
        "prod-a1-private-product-evidence-surface-seed",
        "sdk-a8-private-sdk-smoke-chain-pause-or-docs-selector",
    ]
    assert payload["summary"]["sdkSmokeLanePaused"] is True


def test_prod_a7_selects_compiler_plugin_guard_note_next():
    payload = build_payload()
    assert payload["summary"]["selectedLaneId"] == "eml_compiler_plugin"
    assert payload["summary"]["selectedNextArtifact"] == "CPG-A1 private compiler-plugin guard-note packet"
    assert payload["summary"]["nextRecommendedArtifact"] == "CPG-A1 private compiler-plugin guard-note packet"


def test_prod_a7_records_all_lane_decisions():
    payload = build_payload()
    decisions = {action["laneId"]: action["decision"] for action in payload["candidateLaneActions"]}
    assert decisions == {
        "eml_compiler_plugin": "selected",
        "training_cost_estimator": "parked",
        "pinn_advisor": "parked",
        "eml_ip_core_license": "blocked_until_hardware_evidence",
        "eml_accelerator_card": "blocked_until_laptop_hardware_evidence",
        "monogate_sdk": "paused_as_seeded",
    }


def test_prod_a7_blocks_compiler_public_runtime_and_product_claims():
    payload = build_payload()
    for key in [
        "compiler_plugin_implemented",
        "compiler_plugin_guard_note_created",
        "compiler_correctness_claim",
        "semantic_preservation_claim",
        "automatic_lowering_safety_claim",
        "runtime_performance_claim",
        "sdk_stability_claim",
        "sdk_public_ready",
        "public_product_ready",
        "public_readiness_claim",
        "public_package_release_claim",
        "training_savings_claim",
        "estimator_accuracy_claim",
        "scientific_correctness_claim",
        "hardware_readiness_claim",
        "silicon_readiness_claim",
        "ip_license_terms_finalized",
        "accelerator_card_ready",
        "electronics_repo_touched",
        "laptop_owned_repo_touched",
        "d110_started",
        "reviewer_response_consumed",
        "reviewer_approval_recorded",
        "broad_eml_advantage_claim",
    ]:
        assert payload["claimFlags"][key] is False


def test_prod_a7_claim_flags_are_selector_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_prod_a7_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# PROD-A7")


def test_prod_a7_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/prod_a7_private_product_roadmap_return_selector.py",
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
    assert "PROD_A7_PRIVATE_PRODUCT_ROADMAP_RETURN_SELECTOR_OK" in proc.stdout
