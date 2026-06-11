"""Tests for EML-D69 probability logit checked-witness copy review packet."""

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

from scripts.eml_d69_probability_logit_checked_witness_copy_review_packet import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_d69_consumes_d68_selector():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D69_PROBABILITY_LOGIT_CHECKED_WITNESS_COPY_REVIEW_PACKET_PASS"
    assert payload["sourceSelector"] == "eml-d68-probability-logit-surface-next-selector"
    assert payload["summary"]["selectedOptionId"] == "probability_logit_checked_witness_copy_review_packet"


def test_d69_preserves_checked_witness_and_guards():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["selectedWitnessName"] == "MachLib.Real.probability_logit_boundary_coordinate_witness"
    assert payload["summary"]["checkedStatement"] == (
        "0 < p -> p < 1 -> eml (log p) (exp (log (1 - p))) = p - log (1 - p)"
    )
    assert payload["summary"]["machlibFile"] == "foundations/MachLib/EMLAtlasWitness.lean"
    assert payload["summary"]["guardCount"] == 2
    assert payload["summary"]["sourceNegativeControlCount"] == 4
    assert payload["summary"]["sourceBlockerCount"] == 4


def test_d69_records_private_copy_review_boundaries():
    payload = build_payload(ATLAS_GATE)
    row = payload["witnessCopyRows"][0]
    assert payload["summary"]["copyReviewStarted"] is True
    assert payload["summary"]["privateCopyReviewOnly"] is True
    assert payload["summary"]["checkedWitnessCopyReviewOnly"] is True
    assert payload["summary"]["witnessRowCount"] == 1
    assert payload["summary"]["requiredCaveatCount"] == 9
    assert payload["summary"]["blockedGlobalPhraseCount"] == 12
    assert payload["summary"]["rowRequiredCaveatCount"] == 6
    assert payload["summary"]["rowBlockedPhraseCount"] == 10
    assert row["copyStatus"] == "private_checked_witness_copy_reviewable"
    assert row["publicPromotionAllowed"] is False


def test_d69_freezes_guard_and_runtime_copy_language():
    payload = build_payload(ATLAS_GATE)
    row = payload["witnessCopyRows"][0]
    assert "Both probability interval guards" in " ".join(payload["requiredCaveats"])
    assert "Protected log and log1p remain" in " ".join(payload["requiredCaveats"])
    assert "unguarded statements remain blocked" in " ".join(row["requiredCaveats"])
    assert payload["summary"]["runtimeLoweringControl"] == "protected_log_and_log1p_remain_runtime_controls"
    assert payload["summary"]["runtimeGuardrailStatus"] == "protected_log_and_log1p_runtime_controls_required"
    assert payload["summary"]["publicAtlasStatus"] == "held_private"


def test_d69_blocks_public_runtime_and_broad_claims():
    payload = build_payload(ATLAS_GATE)
    assert "log replacement" in payload["blockedGlobalPhrases"]
    assert "log1p replacement" in payload["blockedGlobalPhrases"]
    assert "logit replacement" in payload["blockedGlobalPhrases"]
    assert "broad EML advantage" in payload["blockedGlobalPhrases"]
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["protectedLogReplacementClaim"] is False
    assert payload["summary"]["protectedLog1pReplacementClaim"] is False
    assert payload["summary"]["publicReady"] is False


def test_d69_starts_no_machlib_or_proof_work():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["proofAttemptStarted"] is False
    assert payload["summary"]["newBoundedBranchSelected"] is False
    assert payload["summary"]["humanPublicCopyGateSelected"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False


def test_d69_claim_flags_are_copy_review_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsAllBounded"] is True
    for key in ["copy_review_started", "private_copy_review_only", "checked_witness_copy_review_only"]:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in {"copy_review_started", "private_copy_review_only", "checked_witness_copy_review_only"}:
            assert value is False


def test_d69_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D69")


def test_d69_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d69_probability_logit_checked_witness_copy_review_packet.py",
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
    assert "EML_D69_PROBABILITY_LOGIT_CHECKED_WITNESS_COPY_REVIEW_PACKET_OK" in proc.stdout
