"""Tests for PINN-A1 private PINN advisor brief."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.pinn_a1_private_pinn_advisor_brief import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_pinn_a1_consumes_prod_a8_and_prod_a2():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "PINN_A1_PRIVATE_PINN_ADVISOR_BRIEF_PASS"
    assert payload["sourceArtifacts"] == [
        "prod-a8-private-product-roadmap-post-cpg-selector",
        "prod-a2-training-cost-estimator-private-spec",
    ]
    assert payload["summary"]["selectedLaneId"] == "pinn_advisor"


def test_pinn_a1_records_brief_shape_counts():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["briefScope"] == "private_diagnostic_brief_only"
    assert summary["supportedInputCount"] == 5
    assert summary["diagnosticCount"] == 5
    assert summary["caveatCount"] == 5
    assert summary["exampleBoundaryCount"] == 3
    assert summary["dependencyCount"] == 4
    assert summary["reviewerQuestionCount"] == 3
    assert summary["blockedClaimCount"] == 15
    assert summary["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_pinn_a1_records_expected_inputs_diagnostics_and_dependencies():
    payload = build_payload()
    input_ids = {item["inputId"] for item in payload["supportedInputs"]}
    diagnostic_ids = {item["diagnosticId"] for item in payload["advisoryDiagnostics"]}
    dependency_ids = {item["dependencyId"] for item in payload["dependencies"]}
    assert {
        "pde_problem_summary",
        "training_loop_metadata",
        "loss_component_history_summary",
        "residual_sampling_summary",
        "cost_estimator_packet_summary",
    } == input_ids
    assert {
        "loss_balance_warning",
        "residual_sampling_gap",
        "boundary_condition_visibility",
        "cost_context_caveat_check",
        "reproducibility_packet_prompt",
    } == diagnostic_ids
    assert "human_implementation_gate" in dependency_ids


def test_pinn_a1_blocks_science_training_runtime_public_and_hardware_claims():
    payload = build_payload()
    for key in [
        "pinn_advisor_implemented",
        "pinn_advisor_executed",
        "pinn_training_executed",
        "pinn_solver_invoked",
        "pinn_diagnostic_claim",
        "scientific_correctness_claim",
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


def test_pinn_a1_claim_flags_are_brief_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_pinn_a1_blocked_claims_include_public_science_and_advantage():
    payload = build_payload()
    blocked = set(payload["blockedClaims"])
    assert "PINN solver correctness" in blocked
    assert "scientific correctness" in blocked
    assert "training improvement" in blocked
    assert "training cost savings" in blocked
    assert "wall-clock runtime performance" in blocked
    assert "public product readiness" in blocked
    assert "broad EML advantage" in blocked


def test_pinn_a1_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# PINN-A1")
    assert "Supported Inputs" in report
    assert "Advisory Diagnostics" in report
    assert "Blocked Claims" in report


def test_pinn_a1_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/pinn_a1_private_pinn_advisor_brief.py",
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
    assert "PINN_A1_PRIVATE_PINN_ADVISOR_BRIEF_OK" in proc.stdout
