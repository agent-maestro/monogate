"""Tests for EA-A2 single-artifact toolkit migration smoke."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.ea_a2_single_artifact_toolkit_migration_smoke import (
    CLAIM_FLAGS,
    MIGRATED_ARTIFACT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def check_by_id(payload, check_id: str):
    return next(item for item in payload["migrationChecks"] if item["checkId"] == check_id)


def test_ea_a2_consumes_ea_a1_and_migrates_only_prod_a1():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EA_A2_SINGLE_ARTIFACT_TOOLKIT_MIGRATION_SMOKE_PASS"
    assert payload["sourceArtifact"] == "ea-a1-shared-evidence-artifact-toolkit-seed"
    assert payload["summary"]["migratedArtifact"] == MIGRATED_ARTIFACT
    assert payload["summary"]["bulkMigrationPerformed"] is False
    assert payload["summary"]["oldArtifactsRewritten"] is False


def test_ea_a2_records_toolkit_helper_usage_checks():
    payload = build_payload()
    assert payload["summary"]["migrationCheckCount"] == 4
    assert payload["summary"]["passedMigrationCheckCount"] == 4
    assert check_by_id(payload, "toolkit_import_present")["status"] == "pass"
    assert check_by_id(payload, "expected_helpers_referenced")["status"] == "pass"
    assert check_by_id(payload, "prod_a1_payload_still_validates")["status"] == "pass"


def test_ea_a2_next_recommended_artifact_is_health_report_seed():
    payload = build_payload()
    assert payload["summary"]["nextRecommendedArtifact"] == "EH-A1 private ecosystem health report seed"


def test_ea_a2_blocks_framework_product_runtime_d110_and_advantage_claims():
    payload = build_payload()
    for key in [
        "bulk_migration_performed",
        "toolkit_surface_expanded",
        "production_framework_claim",
        "schema_validator_implemented",
        "estimator_implemented",
        "public_product_ready",
        "runtime_performance_claim",
        "compiler_correctness_claim",
        "hardware_readiness_claim",
        "d110_started",
        "reviewer_response_consumed",
        "broad_eml_advantage_claim",
    ]:
        assert payload["claimFlags"][key] is False


def test_ea_a2_claim_flags_are_migration_smoke_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_ea_a2_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EA-A2")


def test_ea_a2_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/ea_a2_single_artifact_toolkit_migration_smoke.py",
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
    assert "EA_A2_SINGLE_ARTIFACT_TOOLKIT_MIGRATION_SMOKE_OK" in proc.stdout
