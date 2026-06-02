"""Tests for EML-D43 positive log-exp delta copy review packet."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d43_positive_log_exp_delta_copy_review_packet import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def row_by_id(payload, witness_id: str):
    return next(item for item in payload["witnessCopyRows"] if item["witnessId"] == witness_id)


def test_d43_consumes_d42_and_starts_private_delta_copy_review():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D43_POSITIVE_LOG_EXP_DELTA_COPY_REVIEW_PACKET_PASS"
    assert payload["sourceSelector"] == "eml-d42-positive-log-exp-next-action-selector"
    assert payload["summary"]["selectedOptionId"] == "positive_log_exp_delta_copy_review_packet"
    assert payload["summary"]["copyReviewStarted"] is True
    assert payload["summary"]["privateCopyReviewOnly"] is True
    assert payload["summary"]["deltaCopyReviewOnly"] is True


def test_d43_records_one_positive_log_exp_delta_row():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["witnessRowCount"] == 1
    row = row_by_id(payload, "positive_log_exp_roundtrip")
    assert row["machlibName"] == "MachLib.Real.positive_log_exp_roundtrip_witness"
    assert row["copyStatus"] == "private_delta_copy_reviewable"
    assert row["publicPromotionAllowed"] is False


def test_d43_requires_guard_and_runtime_caveats():
    payload = build_payload(ATLAS_GATE)
    row = row_by_id(payload, "positive_log_exp_roundtrip")
    assert payload["summary"]["positiveDomainGuardRequired"] is True
    assert payload["summary"]["guardCount"] == 1
    assert "Always name the 0 < x guard." in row["requiredCaveats"]
    assert "Keep standard log/exp as the semantic and runtime controls." in row["requiredCaveats"]
    assert row["runtimeControl"] == "standard log/exp remain runtime controls"


def test_d43_blocks_risky_public_runtime_or_broad_phrases():
    payload = build_payload(ATLAS_GATE)
    row = row_by_id(payload, "positive_log_exp_roundtrip")
    assert "theorem discovery" in payload["blockedGlobalPhrases"]
    assert "log/exp replacement" in payload["blockedGlobalPhrases"]
    assert "runtime advantage" in payload["blockedGlobalPhrases"]
    assert "EML replaces log" in row["blockedPhrases"]
    assert "EML replaces exp" in row["blockedPhrases"]
    assert "unguarded log theorem" in row["blockedPhrases"]


def test_d43_keeps_public_surfaces_and_advantage_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["publicHoldPreserved"] is True
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False
    assert payload["summary"]["publicReady"] is False
    assert payload["summary"]["claimFlagsPublicFalse"] is True


def test_d43_keeps_runtime_implementation_and_laptop_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeBoundaryPreserved"] is True
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProvedThisPhase"] is False
    assert payload["summary"]["proofAttemptStarted"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False


def test_d43_preserves_parked_options():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["parkedConstantCoordinateRefresh"] is True
    assert payload["summary"]["parkedBoundedTrigFeasibility"] is True
    assert payload["summary"]["parkedPositiveLogExpBranchPause"] is True


def test_d43_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsAllBounded"] is True
    for key in ["copy_review_started", "private_copy_review_only", "delta_copy_review_only"]:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in {"copy_review_started", "private_copy_review_only", "delta_copy_review_only"}:
            assert value is False
    assert all(row["publicPromotionAllowed"] is False for row in payload["witnessCopyRows"])


def test_d43_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D43")


def test_d43_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d43_positive_log_exp_delta_copy_review_packet.py",
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
    assert "EML_D43_POSITIVE_LOG_EXP_DELTA_COPY_REVIEW_PACKET_OK" in proc.stdout
