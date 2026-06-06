"""Tests for PROD-A1 private product evidence surface seed."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.prod_a1_private_product_evidence_surface_seed import (
    CLAIM_FLAGS,
    LANE_IDS,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def lane_by_id(payload, lane_id: str):
    return next(item for item in payload["productLanes"] if item["laneId"] == lane_id)


def test_prod_a1_maps_six_requested_product_lanes():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "PROD_A1_PRIVATE_PRODUCT_EVIDENCE_SURFACE_SEED_PASS"
    assert payload["summary"]["laneCount"] == 6
    assert set(payload["summary"]["laneIds"]) == LANE_IDS
    for lane_id in LANE_IDS:
        lane = lane_by_id(payload, lane_id)
        assert lane["nextPrivateArtifact"]
        assert lane["reviewerQuestion"]
        assert lane["ownerBoundary"]


def test_prod_a1_prioritizes_training_cost_estimator_as_next_private_artifact():
    payload = build_payload()
    assert payload["summary"]["nextRecommendedArtifact"] == "PROD-A2 training cost estimator private spec"
    estimator = lane_by_id(payload, "training_cost_estimator")
    assert estimator["currentPosture"] == "strongest_near_term_private_spec_candidate"
    assert "Private estimator spec" in estimator["nextPrivateArtifact"]
    assert "guaranteed training cost savings" in estimator["blockedPublicClaims"]


def test_prod_a1_keeps_compiler_hardware_and_public_claims_blocked():
    payload = build_payload()
    summary = payload["summary"]
    for key in [
        "publicProductReady",
        "publicLaunchCopyApproved",
        "compilerCorrectnessClaim",
        "runtimePerformanceClaim",
        "hardwareReadinessClaim",
        "siliconReadinessClaim",
        "trainingSavingsClaim",
        "broadEmlAdvantageClaim",
    ]:
        assert summary[key] is False
    compiler = lane_by_id(payload, "eml_compiler_plugin")
    assert "compiler correctness" in compiler["blockedPublicClaims"]
    accelerator = lane_by_id(payload, "eml_accelerator_card")
    assert "accelerator card readiness" in accelerator["blockedPublicClaims"]


def test_prod_a1_respects_d109_hold_and_does_not_consume_review():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["d109HoldRespected"] is True
    assert summary["d110Started"] is False
    assert summary["reviewerResponseConsumed"] is False
    assert payload["claimFlags"]["d109_hold_respected"] is True
    assert payload["claimFlags"]["d110_started"] is False
    assert payload["claimFlags"]["reviewer_response_consumed"] is False


def test_prod_a1_claim_flags_are_private_seed_only():
    payload = build_payload()
    assert payload["summary"]["claimFlagsBounded"] is True
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_prod_a1_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# PROD-A1")


def test_prod_a1_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/prod_a1_private_product_evidence_surface_seed.py",
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
    assert "PROD_A1_PRIVATE_PRODUCT_EVIDENCE_SURFACE_SEED_OK" in proc.stdout
