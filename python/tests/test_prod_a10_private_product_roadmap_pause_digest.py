"""Tests for PROD-A10 private product roadmap pause digest."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.prod_a10_private_product_roadmap_pause_digest import (
    BLOCKED_CLAIMS,
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_prod_a10_consumes_prod_a9_and_pauses_lane():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "PROD_A10_PRIVATE_PRODUCT_ROADMAP_PAUSE_DIGEST_PASS"
    assert payload["sourceArtifact"] == "prod-a9-private-product-roadmap-post-pinn-selector"
    assert payload["summary"]["productRoadmapLanePaused"] is True
    assert payload["summary"]["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_prod_a10_digest_rows_cover_product_lanes():
    payload = build_payload()
    states = {row["laneId"]: row["state"] for row in payload["digestRows"]}
    assert states == {
        "monogate_sdk": "paused_as_seeded",
        "eml_compiler_plugin": "paused_as_seeded",
        "training_cost_estimator": "seeded_and_parked",
        "pinn_advisor": "paused_as_seeded",
        "eml_ip_core_license": "blocked_until_hardware_evidence",
        "eml_accelerator_card": "blocked_until_laptop_hardware_evidence",
    }
    assert payload["summary"]["digestRowCount"] == 6
    assert payload["summary"]["pausedLaneCount"] == 3
    assert payload["summary"]["seededParkedLaneCount"] == 1
    assert payload["summary"]["blockedLaneCount"] == 2


def test_prod_a10_reopen_conditions_are_bounded():
    payload = build_payload()
    statuses = {condition["conditionId"]: condition["status"] for condition in payload["reopenConditions"]}
    assert statuses == {
        "explicit_bounded_product_request": "allowed_reopen_trigger",
        "actual_private_reviewer_response": "allowed_reopen_trigger",
        "laptop_electronics_artifact": "allowed_reopen_trigger",
        "public_launch_impulse": "blocked_reopen_trigger",
    }


def test_prod_a10_blocked_claims_are_recorded():
    payload = build_payload()
    assert payload["summary"]["blockedClaimCount"] == len(BLOCKED_CLAIMS)
    assert set(payload["blockedClaims"]) == set(BLOCKED_CLAIMS)
    assert "public product readiness" in payload["blockedClaims"]
    assert "broad EML advantage" in payload["blockedClaims"]


def test_prod_a10_blocks_all_product_implementation_and_public_claims():
    payload = build_payload()
    for key in [
        "product_implementation_started",
        "sdk_implementation_changed",
        "sdk_stability_claim",
        "sdk_public_ready",
        "training_cost_estimator_implemented",
        "training_cost_estimator_executed",
        "training_savings_claim",
        "estimator_accuracy_claim",
        "pinn_advisor_implemented",
        "pinn_advisor_executed",
        "pinn_training_executed",
        "scientific_correctness_claim",
        "training_improvement_claim",
        "compiler_plugin_implemented",
        "compiler_plugin_executed",
        "compiler_correctness_claim",
        "semantic_preservation_claim",
        "runtime_performance_claim",
        "public_product_ready",
        "public_readiness_claim",
        "public_docs_created",
        "public_package_release_claim",
        "ip_license_terms_finalized",
        "hardware_readiness_claim",
        "silicon_readiness_claim",
        "accelerator_card_ready",
        "electronics_repo_touched",
        "laptop_owned_repo_touched",
        "d110_started",
        "reviewer_response_consumed",
        "reviewer_approval_recorded",
        "broad_eml_advantage_claim",
    ]:
        assert payload["claimFlags"][key] is False
    assert payload["summary"]["productImplementationStarted"] is False
    assert payload["summary"]["publicReadinessClaim"] is False


def test_prod_a10_claim_flags_are_digest_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_prod_a10_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# PROD-A10")
    assert "Digest Rows" in report
    assert "Reopen Conditions" in report
    assert "Blocked Claims" in report


def test_prod_a10_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/prod_a10_private_product_roadmap_pause_digest.py",
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
    assert "PROD_A10_PRIVATE_PRODUCT_ROADMAP_PAUSE_DIGEST_OK" in proc.stdout
