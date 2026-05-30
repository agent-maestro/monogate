"""Tests for FEF-P5 publication/copy review."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p5_publication_copy_review import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    scan_copy,
    validate_payload,
)


def test_fef_p5_records_copy_review_and_blocks_publication():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "FEF_P5_PUBLICATION_COPY_REVIEW_PASS"
    assert payload["decision"] == "copy_review_passed_publication_blocked"
    assert payload["summary"]["copyReviewPassed"] is True
    assert payload["summary"]["packagePublished"] is False
    assert payload["summary"]["publicReady"] is False
    assert payload["summary"]["checkoutEnabled"] is False


def test_fef_p5_copy_scan_requires_boundaries():
    payload = build_payload()
    assert payload["copyReview"]["forbiddenHits"] == []
    assert payload["copyReview"]["requiredBoundaryMissing"] == []
    bad = scan_copy("monogate-forge-preview is a public package available with 36 shipped targets")
    assert bad["status"] == "fail"
    assert "36 shipped targets" in bad["forbiddenHits"]


def test_fef_p5_evidence_inputs_and_release_gates_are_bounded():
    payload = build_payload()
    assert payload["summary"]["evidenceInputsValid"] is True
    assert payload["summary"]["evidenceClaimFlagsAllFalse"] is True
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["fef_p1_preview_shape_selected"] == "pass"
    assert gates["fef_p4_javascript_source_semantic_comparison_passed"] == "pass"
    assert gates["public_copy_boundary_review_passed"] == "pass"
    assert gates["package_published"] == "blocked"
    assert gates["checkout_remains_disabled"] == "required"


def test_fef_p5_claim_flags_remain_false():
    payload = build_payload()
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p5_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P5")


def test_fef_p5_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p5_publication_copy_review.py",
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
    assert "FEF_P5_PUBLICATION_COPY_REVIEW_OK" in proc.stdout
