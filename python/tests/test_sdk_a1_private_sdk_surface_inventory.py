"""Tests for SDK-A1 private SDK surface inventory."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.sdk_a1_private_sdk_surface_inventory import (
    CLAIM_FLAGS,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def row_by_id(payload, surface_id: str):
    return next(item for item in payload["surfaceRows"] if item["surfaceId"] == surface_id)


def test_sdk_a1_consumes_eh_a4_and_records_inventory():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "SDK_A1_PRIVATE_SDK_SURFACE_INVENTORY_PASS"
    assert payload["sourceArtifact"] == "eh-a4-private-ecosystem-health-digest-export-or-pause-selector"
    assert payload["summary"]["surfaceRowCount"] == 6
    assert payload["summary"]["blockedSdkClaimCount"] == 8
    assert payload["summary"]["stableSurfaceCount"] == 0


def test_sdk_a1_records_expected_surface_rows():
    payload = build_payload()
    surface_ids = {row["surfaceId"] for row in payload["surfaceRows"]}
    assert surface_ids == {
        "python_package_core",
        "rust_extension_core",
        "forge_preview_package",
        "schemas_and_evidence_packets",
        "research_artifact_scripts",
        "blocked_electronics_and_dev_repos",
    }
    assert "monogate-optimize" in row_by_id(payload, "python_package_core")["knownEntryPoints"]
    assert "monogate_core.eval_eml_batch" in row_by_id(payload, "rust_extension_core")["knownEntryPoints"]
    assert row_by_id(payload, "blocked_electronics_and_dev_repos")["surfaceType"] == "blocked_boundary"


def test_sdk_a1_blocks_sdk_stability_public_and_compiler_claims():
    payload = build_payload()
    blocked = {item["claim"] for item in payload["blockedSdkClaims"]}
    assert "SDK stability" in blocked
    assert "public readiness" in blocked
    assert "API compatibility" in blocked
    assert "compiler correctness" in blocked
    assert "runtime performance" in blocked
    assert "broad EML advantage" in blocked
    for key in [
        "sdk_stability_claim",
        "sdk_public_ready",
        "public_readiness_claim",
        "public_package_release_claim",
        "api_compatibility_claim",
        "semantic_versioning_commitment",
        "compiler_correctness_claim",
        "semantic_preservation_claim",
        "runtime_performance_claim",
        "training_savings_claim",
        "hardware_readiness_claim",
        "silicon_readiness_claim",
        "broad_eml_advantage_claim",
    ]:
        assert payload["claimFlags"][key] is False


def test_sdk_a1_preserves_d109_hold_and_no_repo_touch_or_implementation_change():
    payload = build_payload()
    assert payload["summary"]["d109HoldRespected"] is True
    assert payload["summary"]["d110Started"] is False
    assert payload["summary"]["reviewerResponseConsumed"] is False
    assert payload["summary"]["sdkImplementationChanged"] is False
    assert payload["claimFlags"]["electronics_repo_touched"] is False
    assert payload["claimFlags"]["laptop_owned_repo_touched"] is False
    assert payload["claimFlags"]["sdk_implementation_changed"] is False


def test_sdk_a1_selects_import_and_cli_smoke_contract_next():
    payload = build_payload()
    assert payload["summary"]["nextRecommendedArtifact"] == "SDK-A2 private SDK import and CLI smoke contract"


def test_sdk_a1_claim_flags_are_inventory_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_sdk_a1_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# SDK-A1")


def test_sdk_a1_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/sdk_a1_private_sdk_surface_inventory.py",
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
    assert "SDK_A1_PRIVATE_SDK_SURFACE_INVENTORY_OK" in proc.stdout
