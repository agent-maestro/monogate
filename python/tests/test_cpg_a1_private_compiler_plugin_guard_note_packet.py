"""Tests for CPG-A1 private compiler-plugin guard-note packet."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.cpg_a1_private_compiler_plugin_guard_note_packet import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_cpg_a1_consumes_prod_a7_and_stays_on_compiler_plugin_lane():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "CPG_A1_PRIVATE_COMPILER_PLUGIN_GUARD_NOTE_PACKET_PASS"
    assert payload["sourceArtifact"] == "prod-a7-private-product-roadmap-return-selector"
    assert payload["summary"]["selectedLaneId"] == "eml_compiler_plugin"


def test_cpg_a1_records_advisory_capabilities():
    payload = build_payload()
    capability_ids = {item["capabilityId"] for item in payload["advisoryCapabilities"]}
    assert capability_ids == {
        "expression_surface_detection",
        "static_cost_profile_hint",
        "rewrite_opportunity_hint",
        "guard_requirement_note",
        "evidence_packet_link_hint",
    }
    assert payload["summary"]["advisoryCapabilityCount"] == 5
    assert all(
        any(
            boundary in item["mustSay"].lower()
            for boundary in [
                "advisory",
                "hint only",
                "review suggestion only",
                "reminder only",
                "pointer only",
            ]
        )
        for item in payload["advisoryCapabilities"]
    )


def test_cpg_a1_blocks_core_compiler_claims():
    payload = build_payload()
    blocked_ids = {item["claimId"] for item in payload["blockedCompilerClaims"]}
    assert {
        "compiler_correctness",
        "semantic_preservation",
        "automatic_lowering_safety",
        "runtime_performance",
        "code_generation_correctness",
        "all_target_readiness",
        "public_package_release_readiness",
        "broad_eml_advantage",
    } == blocked_ids
    assert payload["summary"]["blockedCompilerClaimCount"] == 8


def test_cpg_a1_records_allowed_and_blocked_outputs():
    payload = build_payload()
    allowed_ids = {item["outputId"] for item in payload["allowedOutputs"]}
    blocked_ids = {item["outputId"] for item in payload["blockedOutputs"]}
    assert allowed_ids == {
        "lint_warning",
        "review_note",
        "cost_profile_hint",
        "guard_checklist_item",
        "evidence_pointer",
    }
    assert blocked_ids == {
        "generated_code_replacement",
        "automatic_rewrite_or_lowering",
        "proof_certificate",
        "runtime_benchmark_claim",
        "public_docs_or_copy",
    }


def test_cpg_a1_blocks_compiler_public_runtime_and_laptop_claims():
    payload = build_payload()
    for key in [
        "compiler_plugin_implemented",
        "compiler_plugin_executed",
        "compiler_correctness_claim",
        "semantic_preservation_claim",
        "automatic_lowering_safety_claim",
        "runtime_performance_claim",
        "code_generation_claim",
        "runtime_lowering_changed",
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


def test_cpg_a1_claim_flags_are_guard_note_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_cpg_a1_next_recommended_artifact():
    payload = build_payload()
    assert payload["summary"]["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT
    assert "CPG-A2" in payload["summary"]["nextRecommendedArtifact"]
    assert payload["summary"]["compilerPluginImplemented"] is False
    assert payload["summary"]["compilerPluginExecuted"] is False


def test_cpg_a1_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# CPG-A1")
    assert "Blocked Compiler Claims" in report


def test_cpg_a1_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/cpg_a1_private_compiler_plugin_guard_note_packet.py",
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
    assert "CPG_A1_PRIVATE_COMPILER_PLUGIN_GUARD_NOTE_PACKET_OK" in proc.stdout
