"""Tests for PROD-A9 private product roadmap post-PINN selector."""

from __future__ import annotations

import pytest

# Blanket-marked heavy: CLI-contract test (subprocess.run of a
# script that loads large JSON evidence). Skipped from the fast
# dev loop via `pytest -m "not heavy"`; runs in CI by default.
# A follow-up measurement pass will UN-mark individual fast files.
pytestmark = pytest.mark.heavy

import json
from pathlib import Path
import subprocess
import sys

from scripts.prod_a9_private_product_roadmap_post_pinn_selector import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_prod_a9_consumes_prod_a1_and_pinn_a4():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "PROD_A9_PRIVATE_PRODUCT_ROADMAP_POST_PINN_SELECTOR_PASS"
    assert payload["sourceArtifacts"] == [
        "prod-a1-private-product-evidence-surface-seed",
        "pinn-a4-private-pinn-advisor-static-fixture-review-or-pause-selector",
    ]
    assert payload["summary"]["pinnAdvisorLanePaused"] is True


def test_prod_a9_records_all_product_lane_states():
    payload = build_payload()
    states = {state["laneId"]: state["state"] for state in payload["laneStates"]}
    assert states == {
        "monogate_sdk": "paused_as_seeded",
        "eml_compiler_plugin": "paused_as_seeded",
        "training_cost_estimator": "seeded_and_parked",
        "pinn_advisor": "paused_as_seeded",
        "eml_ip_core_license": "blocked_until_hardware_evidence",
        "eml_accelerator_card": "blocked_until_laptop_hardware_evidence",
    }
    assert payload["summary"]["laneStateCount"] == 6
    assert payload["summary"]["pausedLaneCount"] == 3
    assert payload["summary"]["seededParkedLaneCount"] == 1
    assert payload["summary"]["blockedLaneCount"] == 2


def test_prod_a9_selects_pause_digest():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["selectedActionId"] == "product_roadmap_pause_digest"
    assert summary["selectedNextArtifact"] == NEXT_RECOMMENDED_ARTIFACT
    assert summary["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT
    decisions = {action["actionId"]: action["decision"] for action in payload["candidateActions"]}
    assert decisions == {
        "product_roadmap_pause_digest": "selected",
        "training_cost_estimator_release_gate": "parked",
        "ip_license_scope_memo": "blocked",
        "accelerator_dependency_ladder": "blocked",
        "public_product_docs": "blocked",
    }


def test_prod_a9_blocks_product_public_runtime_hardware_and_science_claims():
    payload = build_payload()
    for key in [
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


def test_prod_a9_claim_flags_are_selector_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_prod_a9_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# PROD-A9")
    assert "Lane States" in report
    assert "Candidate Actions" in report


def test_prod_a9_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/prod_a9_private_product_roadmap_post_pinn_selector.py",
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
    assert "PROD_A9_PRIVATE_PRODUCT_ROADMAP_POST_PINN_SELECTOR_OK" in proc.stdout
