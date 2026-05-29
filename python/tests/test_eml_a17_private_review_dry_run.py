"""Tests for EML-A17 private review dry run."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_a17_private_review_dry_run import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_a17_builds_one_gaussian_stable_dry_run():
    payload, candidate = build_payload()
    validate_payload(payload, candidate)
    assert payload["status"] == "EML_A17_PRIVATE_REVIEW_DRY_RUN_PASS"
    assert payload["summary"]["dryRunCount"] == 1
    assert payload["summary"]["selectedFunction"] == "gaussian_stable"
    assert candidate["semanticReview"]["function_name"] == "gaussian_stable"


def test_a17_candidate_links_a14_export_to_a15_mount_card():
    payload, candidate = build_payload()
    review = candidate["semanticReview"]
    assert payload["summary"]["roundtripLinked"] is True
    assert payload["summary"]["mountCardLinked"] is True
    assert review["source_artifact_id"] == "eml-a14-forge-efrog-export-ux"
    assert review["glassbox_mount_card_id"] == "gaussian_stable_holdout_semantic_compare_v0_glassbox_mount_card_v0"
    assert review["roundtrip_link_status"] == "linked_by_canonical_eml_hash"


def test_a17_candidate_remains_candidate_only():
    payload, candidate = build_payload()
    assert candidate["reviewDecision"] == "candidate_only"
    assert payload["summary"]["automaticApproval"] is False
    assert payload["summary"]["publicReady"] is False
    assert payload["summary"]["deploymentPerformed"] is False
    assert payload["summary"]["engineFilesModified"] is False


def test_a17_claim_flags_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload, candidate = build_payload()
    assert all(value is False for value in payload["claimFlags"].values())
    assert all(value is False for value in candidate["claimFlags"].values())


def test_a17_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "candidates",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "candidate_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-A17")


def test_a17_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_a17_private_review_dry_run.py",
            "--build",
            "--out-dir",
            str(tmp_path / "results"),
            "--candidate-dir",
            str(tmp_path / "candidates"),
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
    assert "EML_A17_PRIVATE_REVIEW_DRY_RUN_OK" in proc.stdout
