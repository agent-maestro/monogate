"""Tests for PINN-A4 private PINN advisor static fixture review/pause selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.pinn_a4_private_pinn_advisor_static_fixture_review_or_pause_selector import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_pinn_a4_consumes_pinn_a3_and_passes_review():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "PINN_A4_PRIVATE_PINN_ADVISOR_STATIC_FIXTURE_REVIEW_OR_PAUSE_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "pinn-a3-private-pinn-advisor-static-fixture-packet"
    assert payload["summary"]["reviewCheckCount"] == 7
    assert payload["summary"]["reviewPassCount"] == 7
    assert payload["summary"]["reviewFailCount"] == 0
    assert {check["status"] for check in payload["reviewChecks"]} == {"pass"}


def test_pinn_a4_selects_lane_pause():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["selectedActionId"] == "pause_pinn_advisor_lane"
    assert summary["selectedNextArtifact"] == NEXT_RECOMMENDED_ARTIFACT
    assert summary["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT
    assert summary["lanePausedAsSufficientlyBounded"] is True


def test_pinn_a4_candidate_actions_are_bounded():
    payload = build_payload()
    decisions = {action["actionId"]: action["decision"] for action in payload["candidateActions"]}
    assert decisions == {
        "pause_pinn_advisor_lane": "selected",
        "static_fixture_revision": "parked",
        "fixture_runner": "blocked",
        "advisor_implementation": "blocked",
        "public_docs_gate": "blocked",
    }


def test_pinn_a4_blocks_runner_execution_implementation_and_claims():
    payload = build_payload()
    for key in [
        "static_fixture_revision_created",
        "fixture_runner_created",
        "static_fixtures_executed",
        "pinn_advisor_implemented",
        "pinn_advisor_executed",
        "pinn_training_executed",
        "pinn_solver_invoked",
        "pinn_diagnostic_claim",
        "scientific_correctness_claim",
        "pde_solution_validity_claim",
        "training_improvement_claim",
        "training_savings_claim",
        "estimator_accuracy_claim",
        "model_quality_claim",
        "runtime_performance_claim",
        "compiler_plugin_implemented",
        "compiler_plugin_executed",
        "compiler_correctness_claim",
        "semantic_preservation_claim",
        "sdk_stability_claim",
        "public_product_ready",
        "public_readiness_claim",
        "public_docs_created",
        "public_package_release_claim",
        "hardware_readiness_claim",
        "silicon_readiness_claim",
        "electronics_repo_touched",
        "laptop_owned_repo_touched",
        "d110_started",
        "reviewer_response_consumed",
        "reviewer_approval_recorded",
        "broad_eml_advantage_claim",
    ]:
        assert payload["claimFlags"][key] is False


def test_pinn_a4_claim_flags_are_review_pause_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_pinn_a4_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# PINN-A4")
    assert "Review Checks" in report
    assert "Candidate Actions" in report


def test_pinn_a4_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/pinn_a4_private_pinn_advisor_static_fixture_review_or_pause_selector.py",
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
    assert "PINN_A4_PRIVATE_PINN_ADVISOR_STATIC_FIXTURE_REVIEW_OR_PAUSE_SELECTOR_OK" in proc.stdout
