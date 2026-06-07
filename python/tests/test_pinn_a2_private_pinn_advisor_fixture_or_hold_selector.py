"""Tests for PINN-A2 private PINN advisor fixture/hold selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.pinn_a2_private_pinn_advisor_fixture_or_hold_selector import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_pinn_a2_consumes_pinn_a1():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "PINN_A2_PRIVATE_PINN_ADVISOR_FIXTURE_OR_HOLD_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "pinn-a1-private-pinn-advisor-brief"


def test_pinn_a2_review_checks_all_pass():
    payload = build_payload()
    assert payload["summary"]["reviewCheckCount"] == 7
    assert payload["summary"]["reviewFailureCount"] == 0
    assert {check["status"] for check in payload["reviewChecks"]} == {"pass"}
    assert {check["checkId"] for check in payload["reviewChecks"]} == {
        "brief_scope_is_private",
        "supported_inputs_present",
        "advisory_diagnostics_present",
        "blocked_claims_present",
        "human_gate_present",
        "implementation_flags_false",
        "public_and_science_claims_false",
    }


def test_pinn_a2_selects_static_fixture_packet():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["selectedActionId"] == "draft_static_fixture_packet"
    assert summary["selectedNextArtifact"] == NEXT_RECOMMENDED_ARTIFACT
    assert summary["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT
    decisions = {action["actionId"]: action["decision"] for action in payload["selectorActions"]}
    assert decisions == {
        "draft_static_fixture_packet": "selected",
        "pause_pinn_advisor_lane": "parked",
        "implementation_gate": "blocked",
        "public_docs_gate": "blocked",
    }


def test_pinn_a2_creates_no_fixtures_or_implementation():
    payload = build_payload()
    for key in [
        "static_fixtures_created",
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
        "electronics_repo_touched",
        "laptop_owned_repo_touched",
        "d110_started",
        "reviewer_response_consumed",
        "reviewer_approval_recorded",
        "broad_eml_advantage_claim",
    ]:
        assert payload["claimFlags"][key] is False


def test_pinn_a2_claim_flags_are_selector_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_pinn_a2_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# PINN-A2")
    assert "Review Checks" in report
    assert "Selector Actions" in report


def test_pinn_a2_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/pinn_a2_private_pinn_advisor_fixture_or_hold_selector.py",
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
    assert "PINN_A2_PRIVATE_PINN_ADVISOR_FIXTURE_OR_HOLD_SELECTOR_OK" in proc.stdout
