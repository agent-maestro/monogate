"""Tests for PROD-A8 private product roadmap post-CPG selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.prod_a8_private_product_roadmap_post_cpg_selector import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_prod_a8_consumes_prod_a1_and_cpg_a10():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "PROD_A8_PRIVATE_PRODUCT_ROADMAP_POST_CPG_SELECTOR_PASS"
    assert payload["sourceArtifacts"] == [
        "prod-a1-private-product-evidence-surface-seed",
        "cpg-a10-private-lint-contract-implementation-hold-review-or-pause-selector",
    ]
    assert payload["summary"]["compilerPluginLanePaused"] is True


def test_prod_a8_selects_pinn_advisor_brief():
    payload = build_payload()
    assert payload["summary"]["selectedLaneId"] == "pinn_advisor"
    assert payload["summary"]["selectedNextArtifact"] == NEXT_RECOMMENDED_ARTIFACT
    assert payload["summary"]["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_prod_a8_records_all_lane_decisions():
    payload = build_payload()
    decisions = {action["laneId"]: action["decision"] for action in payload["candidateLaneActions"]}
    assert decisions == {
        "pinn_advisor": "selected",
        "training_cost_estimator": "parked_as_seeded",
        "eml_compiler_plugin": "paused_as_seeded",
        "monogate_sdk": "paused_as_seeded",
        "eml_ip_core_license": "blocked_until_hardware_evidence",
        "eml_accelerator_card": "blocked_until_laptop_hardware_evidence",
    }


def test_prod_a8_blocks_pinn_science_public_runtime_and_hardware_claims():
    payload = build_payload()
    for key in [
        "pinn_advisor_implemented",
        "pinn_advisor_executed",
        "pinn_diagnostic_claim",
        "scientific_correctness_claim",
        "training_improvement_claim",
        "training_cost_estimator_implemented",
        "training_savings_claim",
        "estimator_accuracy_claim",
        "compiler_plugin_implemented",
        "compiler_plugin_executed",
        "compiler_correctness_claim",
        "semantic_preservation_claim",
        "runtime_performance_claim",
        "sdk_stability_claim",
        "public_product_ready",
        "public_readiness_claim",
        "public_package_release_claim",
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


def test_prod_a8_claim_flags_are_selector_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_prod_a8_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# PROD-A8")
    assert "Candidate Lane Actions" in report


def test_prod_a8_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/prod_a8_private_product_roadmap_post_cpg_selector.py",
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
    assert "PROD_A8_PRIVATE_PRODUCT_ROADMAP_POST_CPG_SELECTOR_OK" in proc.stdout
