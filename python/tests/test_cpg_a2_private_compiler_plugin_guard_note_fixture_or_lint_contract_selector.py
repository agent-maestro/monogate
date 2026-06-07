"""Tests for CPG-A2 private compiler-plugin guard-note fixture/lint selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.cpg_a2_private_compiler_plugin_guard_note_fixture_or_lint_contract_selector import (
    CLAIM_FLAGS,
    NEXT_RECOMMENDED_ARTIFACT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_cpg_a2_consumes_cpg_a1():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "CPG_A2_PRIVATE_COMPILER_PLUGIN_GUARD_NOTE_FIXTURE_OR_LINT_CONTRACT_SELECTOR_PASS"
    assert payload["sourceArtifact"] == "cpg-a1-private-compiler-plugin-guard-note-packet"


def test_cpg_a2_selects_static_fixture_packet_next():
    payload = build_payload()
    assert payload["summary"]["selectedActionId"] == "static_guard_note_fixture_packet"
    assert payload["summary"]["selectedNextArtifact"] == NEXT_RECOMMENDED_ARTIFACT
    assert payload["summary"]["nextRecommendedArtifact"] == NEXT_RECOMMENDED_ARTIFACT


def test_cpg_a2_parks_executable_lint_contract_and_blocks_implementation():
    payload = build_payload()
    decisions = {action["actionId"]: action["decision"] for action in payload["candidateNextActions"]}
    assert decisions["executable_lint_contract"] == "parked_until_static_fixtures_reviewed"
    assert decisions["compiler_plugin_implementation"] == "blocked"
    assert decisions["public_docs_or_package"] == "blocked"


def test_cpg_a2_records_expected_static_fixture_families():
    payload = build_payload()
    assert set(payload["selectedFixtureFamilies"]) == {
        "accepted_advisory_expression_surface_detection",
        "accepted_guard_requirement_note",
        "accepted_evidence_packet_link_hint",
        "rejected_automatic_rewrite_or_lowering",
        "rejected_runtime_performance_claim",
        "rejected_public_readiness_claim",
    }
    assert payload["summary"]["expectedFixtureFamilyCount"] == 6


def test_cpg_a2_blocks_compiler_lint_runtime_and_public_claims():
    payload = build_payload()
    for key in [
        "static_fixture_packet_created",
        "executable_lint_contract_created",
        "compiler_plugin_implemented",
        "compiler_plugin_executed",
        "lint_engine_implemented",
        "lint_engine_executed",
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


def test_cpg_a2_claim_flags_are_selector_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_cpg_a2_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# CPG-A2")
    assert "Selected Fixture Families" in report


def test_cpg_a2_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/cpg_a2_private_compiler_plugin_guard_note_fixture_or_lint_contract_selector.py",
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
    assert "CPG_A2_PRIVATE_COMPILER_PLUGIN_GUARD_NOTE_FIXTURE_OR_LINT_CONTRACT_SELECTOR_OK" in proc.stdout
