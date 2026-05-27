"""Tests for EML-A9 Atlas safe education draft."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_atlas_annex import build_annex
from scripts.eml_atlas_promotion_gate import build_gate
from scripts.eml_atlas_safe_education_draft import build_draft, validate_draft


def built_gate_path(tmp_path: Path) -> str:
    annex = build_annex(tmp_path / "annex", tmp_path / "reports", tmp_path / "evidence")
    gate = build_gate(Path(annex["result_path"]), tmp_path / "gate", tmp_path / "reports", tmp_path / "evidence")
    return gate["result_path"]


def test_draft_contains_seven_safe_candidates(tmp_path):
    result = build_draft(Path(built_gate_path(tmp_path)), tmp_path / "draft", tmp_path / "reports", tmp_path / "evidence")["result"]
    assert result["draftCount"] == 7
    ids = {draft["id"] for draft in result["drafts"]}
    assert "exp_from_eml" in ids
    assert "subtraction_boundary" in ids
    assert all(draft["publicPromotionPerformed"] is False for draft in result["drafts"])
    validate_draft(result)


def test_draft_copy_has_non_claims_and_review_status(tmp_path):
    result = build_draft(Path(built_gate_path(tmp_path)), tmp_path / "draft", tmp_path / "reports", tmp_path / "evidence")["result"]
    assert result["policy"]["requiresMuseOrReviewerReview"] is True
    assert all(draft["reviewStatus"] == "draft_needs_human_review" for draft in result["drafts"])
    assert all(draft["nonClaims"] for draft in result["drafts"])
    assert result["claimFlags"]["public_atlas_promotion"] is False


def test_draft_writes_json_report_and_evidence(tmp_path):
    built = build_draft(Path(built_gate_path(tmp_path)), tmp_path / "draft", tmp_path / "reports", tmp_path / "evidence")
    result = json.loads(Path(built["result_path"]).read_text(encoding="utf-8"))
    evidence = json.loads(Path(built["evidence_path"]).read_text(encoding="utf-8"))
    assert result["status"] == "EML_ATLAS_SAFE_EDUCATION_DRAFT_PASS"
    assert evidence["reviewDecision"] == "draft_needs_human_review"
    assert evidence["claimFlags"]["deploy_performed"] is False
    validate_draft(result)


def test_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_atlas_safe_education_draft.py",
            "--build",
            "--gate-path",
            built_gate_path(tmp_path),
            "--out-dir",
            str(tmp_path / "draft"),
            "--report-dir",
            str(tmp_path / "reports"),
            "--evidence-dir",
            str(tmp_path / "evidence"),
            "--strict",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "EML_ATLAS_SAFE_EDUCATION_DRAFT_OK" in proc.stdout
