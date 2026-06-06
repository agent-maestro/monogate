"""Tests for EA-A1 shared evidence artifact toolkit seed."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.ea_a1_shared_evidence_artifact_toolkit_seed import (
    CLAIM_FLAGS,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def helper_by_id(payload, helper_id: str):
    return next(item for item in payload["helperContracts"] if item["helperId"] == helper_id)


def test_ea_a1_consumes_prod_a6_and_records_three_helpers():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EA_A1_SHARED_EVIDENCE_ARTIFACT_TOOLKIT_SEED_PASS"
    assert payload["sourceArtifact"] == "prod-a6-training-cost-estimator-fixture-packet"
    assert payload["summary"]["helperCount"] == 3
    assert helper_by_id(payload, "claim_flagged_json_packet_builder")["moduleFunction"] == "build_claim_flagged_packet"
    assert helper_by_id(payload, "markdown_report_builder")["moduleFunction"] == "render_markdown_report"
    assert helper_by_id(payload, "command_feed_builder")["moduleFunction"] == "build_command_feed"


def test_ea_a1_is_not_broad_framework_or_rewrite():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["oldArtifactsRewritten"] is False
    assert summary["broadFrameworkCreated"] is False
    assert payload["claimFlags"]["broad_framework_created"] is False
    assert payload["claimFlags"]["old_artifacts_rewritten"] is False


def test_ea_a1_blocks_product_runtime_d110_and_advantage_claims():
    payload = build_payload()
    for key in [
        "schema_validator_implemented",
        "estimator_implemented",
        "public_product_ready",
        "training_savings_claim",
        "runtime_performance_claim",
        "compiler_correctness_claim",
        "hardware_readiness_claim",
        "d110_started",
        "reviewer_response_consumed",
        "broad_eml_advantage_claim",
    ]:
        assert payload["claimFlags"][key] is False


def test_ea_a1_claim_flags_are_seed_only():
    payload = build_payload()
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_ea_a1_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EA-A1")


def test_ea_a1_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/ea_a1_shared_evidence_artifact_toolkit_seed.py",
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
    assert "EA_A1_SHARED_EVIDENCE_ARTIFACT_TOOLKIT_SEED_OK" in proc.stdout
