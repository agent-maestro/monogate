"""Tests for PINN-A3 private PINN advisor static fixture packet."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.pinn_a3_private_pinn_advisor_static_fixture_packet import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    REQUIRED_BLOCKED_CLAIMS,
    REQUIRED_CAVEATS,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_pinn_a3_consumes_pinn_a2():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "PINN_A3_PRIVATE_PINN_ADVISOR_STATIC_FIXTURE_PACKET_PASS"
    assert payload["sourceArtifact"] == "pinn-a2-private-pinn-advisor-fixture-or-hold-selector"
    assert payload["summary"]["pinnA2SelectedNextArtifact"] == "PINN-A3 private PINN advisor static fixture packet"


def test_pinn_a3_fixture_counts_and_next_artifact():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["acceptedFixtureCount"] == 3
    assert summary["rejectionFixtureCount"] == 6
    assert summary["staticFixtureCount"] == 9
    assert summary["requiredCaveatCount"] == len(REQUIRED_CAVEATS)
    assert summary["requiredBlockedClaimCount"] == len(REQUIRED_BLOCKED_CLAIMS)
    assert summary["reviewerQuestionCount"] == 3
    assert summary["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_pinn_a3_accepted_fixture_ids_and_required_boundaries():
    payload = build_payload()
    accepted_ids = {fixture["fixtureId"] for fixture in payload["acceptedFixtures"]}
    assert accepted_ids == {
        "accepted_loss_balance_warning_note",
        "accepted_residual_sampling_gap_note",
        "accepted_cost_caveat_attachment_note",
    }
    for fixture in payload["acceptedFixtures"]:
        assert fixture["expectedDisposition"] == "accept_private_advisory_note"
        packet = fixture["packet"]
        assert packet["required_caveats"] == REQUIRED_CAVEATS
        assert packet["blocked_claims"] == REQUIRED_BLOCKED_CLAIMS
        assert set(packet["claim_flags"].values()) == {False}


def test_pinn_a3_rejection_fixture_ids():
    payload = build_payload()
    rejection_ids = {fixture["fixtureId"] for fixture in payload["rejectionFixtures"]}
    assert rejection_ids == {
        "missing_blocked_claims",
        "missing_required_caveats",
        "scientific_correctness_true",
        "training_improvement_true",
        "runtime_performance_true",
        "public_product_ready_true",
    }
    assert {fixture["expectedDisposition"] for fixture in payload["rejectionFixtures"]} == {"reject"}


def test_pinn_a3_creates_no_runner_execution_or_implementation():
    payload = build_payload()
    for key in [
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


def test_pinn_a3_claim_flags_are_fixture_packet_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_pinn_a3_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# PINN-A3")
    assert "Accepted Fixtures" in report
    assert "Rejection Fixtures" in report


def test_pinn_a3_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/pinn_a3_private_pinn_advisor_static_fixture_packet.py",
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
    assert "PINN_A3_PRIVATE_PINN_ADVISOR_STATIC_FIXTURE_PACKET_OK" in proc.stdout
