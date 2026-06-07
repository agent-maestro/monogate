"""Tests for CPG-A3 private compiler-plugin guard-note static fixture packet."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.cpg_a3_private_compiler_plugin_guard_note_static_fixture_packet import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_cpg_a3_consumes_cpg_a2():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "CPG_A3_PRIVATE_COMPILER_PLUGIN_GUARD_NOTE_STATIC_FIXTURE_PACKET_PASS"
    assert payload["sourceArtifact"] == "cpg-a2-private-compiler-plugin-guard-note-fixture-or-lint-contract-selector"


def test_cpg_a3_records_three_accepted_and_three_rejection_fixtures():
    payload = build_payload()
    assert payload["summary"]["acceptedFixtureCount"] == 3
    assert payload["summary"]["rejectionFixtureCount"] == 3
    assert payload["summary"]["fixtureCount"] == 6


def test_cpg_a3_accepted_fixture_families_match_selector():
    payload = build_payload()
    assert {fixture["family"] for fixture in payload["acceptedFixtures"]} == {
        "accepted_advisory_expression_surface_detection",
        "accepted_guard_requirement_note",
        "accepted_evidence_packet_link_hint",
    }
    assert {fixture["allowedOutput"] for fixture in payload["acceptedFixtures"]} == {
        "lint_warning",
        "guard_checklist_item",
        "evidence_pointer",
    }


def test_cpg_a3_rejection_fixture_families_block_forbidden_outputs():
    payload = build_payload()
    assert {fixture["family"] for fixture in payload["rejectionFixtures"]} == {
        "rejected_automatic_rewrite_or_lowering",
        "rejected_runtime_performance_claim",
        "rejected_public_readiness_claim",
    }
    assert {fixture["blockedOutput"] for fixture in payload["rejectionFixtures"]} == {
        "automatic_rewrite_or_lowering",
        "runtime_benchmark_claim",
        "public_docs_or_copy",
    }


def test_cpg_a3_blocks_plugin_lint_fixture_runner_runtime_and_public_claims():
    payload = build_payload()
    for key in [
        "executable_lint_contract_created",
        "compiler_plugin_implemented",
        "compiler_plugin_executed",
        "lint_engine_implemented",
        "lint_engine_executed",
        "fixture_runner_implemented",
        "fixture_runner_executed",
        "compiler_correctness_claim",
        "semantic_preservation_claim",
        "automatic_lowering_safety_claim",
        "runtime_performance_claim",
        "code_generation_claim",
        "runtime_lowering_changed",
        "sdk_stability_claim",
        "public_readiness_claim",
        "public_package_release_claim",
        "electronics_repo_touched",
        "laptop_owned_repo_touched",
        "d110_started",
        "reviewer_response_consumed",
        "reviewer_approval_recorded",
        "broad_eml_advantage_claim",
    ]:
        assert payload["claimFlags"][key] is False


def test_cpg_a3_claim_flags_are_static_fixture_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_cpg_a3_next_recommended_artifact():
    payload = build_payload()
    assert payload["summary"]["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT
    assert "CPG-A4" in payload["summary"]["nextRecommendedArtifact"]


def test_cpg_a3_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# CPG-A3")
    assert "Rejection Fixtures" in report


def test_cpg_a3_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/cpg_a3_private_compiler_plugin_guard_note_static_fixture_packet.py",
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
    assert "CPG_A3_PRIVATE_COMPILER_PLUGIN_GUARD_NOTE_STATIC_FIXTURE_PACKET_OK" in proc.stdout
