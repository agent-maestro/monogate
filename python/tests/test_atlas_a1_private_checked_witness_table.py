"""Tests for ATLAS-A1 private checked-witness table."""

from __future__ import annotations

import pytest

# Blanket-marked heavy: CLI-contract test (subprocess.run of a
# script that loads large JSON evidence). Skipped from the fast
# dev loop via `pytest -m "not heavy"`; runs in CI by default.
# A follow-up measurement pass will UN-mark individual fast files.
pytestmark = pytest.mark.heavy

import json
from pathlib import Path
import subprocess
import sys

from scripts.atlas_a1_private_checked_witness_table import (
    CLAIM_FLAGS,
    EXPECTED_WITNESS_IDS,
    ROOT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_atlas_a1_consumes_d100_and_creates_private_table():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ATLAS_A1_PRIVATE_CHECKED_WITNESS_TABLE_PASS"
    assert payload["sourceArtifact"] == "eml-d100-bounded-artifact-target-set-consolidation-review"
    assert summary["sourceStatus"] == "EML_D100_BOUNDED_ARTIFACT_TARGET_SET_CONSOLIDATION_REVIEW_PASS"
    assert summary["privateAtlasTableCreated"] is True
    assert summary["privateReviewOnly"] is True


def test_atlas_a1_records_expected_checked_witness_rows_private_only():
    payload = build_payload(ATLAS_GATE)
    rows = payload["atlasRows"]
    assert len(rows) == 13
    assert payload["summary"]["atlasRowCount"] == 13
    assert {row["witnessId"] for row in rows} == EXPECTED_WITNESS_IDS
    assert all(row["atlasVisibility"] == "private_only" for row in rows)
    assert all(row["reviewRole"] == "checked_witness_core" for row in rows)
    assert all(row["publicPromotionAllowed"] is False for row in rows)
    assert payload["summary"]["allRowsPrivateOnly"] is True
    assert payload["summary"]["allRowsBlockPublicPromotion"] is True


def test_atlas_a1_records_family_counts():
    payload = build_payload(ATLAS_GATE)
    counts = payload["familyCounts"]
    assert sum(counts.values()) == len(payload["atlasRows"])
    assert payload["summary"]["familyCount"] == len(counts)
    assert counts["nested_subtraction_boundary"] == 3
    assert counts["expm1_boundary"] == 1
    assert counts["positive_log_exp"] == 1
    assert counts["log1p_affine_scaled_boundary"] == 1


def test_atlas_a1_preserves_d100_target_status():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["sourceCheckedWitnessCoreCount"] == 13
    assert summary["targetMin"] == 15
    assert summary["targetMax"] == 25
    assert summary["targetLowerBoundReached"] is False
    assert summary["targetUpperBoundExceeded"] is False
    assert summary["additionalArtifactsNeededForLowerBound"] == 2
    assert summary["remainingSlotsBeforeUpperBound"] == 12
    assert summary["selectorOnlyPacketsCountedAsFinalArtifacts"] is False
    assert summary["nextRecommendedArtifact"] == "ATLAS-A2 private Atlas gap review or pause selector"


def test_atlas_a1_blocks_public_d110_product_proof_and_runtime_claims():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["publicPromotionAllowed"] is False
    assert summary["publicCopyApproved"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["catalogCompletenessClaim"] is False
    assert summary["d109HoldRespected"] is True
    assert summary["d110Started"] is False
    assert summary["reviewerResponseConsumed"] is False
    for key, value in payload["claimFlags"].items():
        if key in TRUE_CLAIM_FLAGS:
            assert value is True
        else:
            assert value is False
    for blocked in [
        "public_atlas_promotion",
        "public_copy_approved",
        "public_surface_updated",
        "sdk_compiler_docs_created",
        "course_material_created",
        "new_identity_candidate_selected",
        "proof_attempt_started",
        "machlib_file_changed",
        "lean_typecheck_performed",
        "runtime_lowering_changed",
        "renderer_implemented",
        "product_implementation_started",
        "electronics_repo_touched",
        "laptop_owned_repo_touched",
        "d110_started",
        "reviewer_response_consumed",
        "catalog_completeness_claim",
        "broad_eml_advantage_claim",
        "runtime_performance_claim",
        "compiler_correctness_claim",
        "public_ready",
    ]:
        assert CLAIM_FLAGS[blocked] is False


def test_atlas_a1_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# ATLAS-A1 Private Checked Witness Table")
    assert "## Private Atlas Rows" in report


def test_atlas_a1_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/atlas_a1_private_checked_witness_table.py",
            "--build",
            "--atlas-gate-path",
            str(ATLAS_GATE),
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
    assert "ATLAS_A1_PRIVATE_CHECKED_WITNESS_TABLE_OK" in proc.stdout
