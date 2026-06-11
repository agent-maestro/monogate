"""Tests for ACT-A16 reviewer promotion hold final handoff."""

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

from scripts.act_a16_reviewer_promotion_hold_final_handoff import (
    BLOCKED_STATEMENTS,
    CLAIM_FLAGS,
    ROOT,
    build_handoff_checklist,
    build_handoff_packet,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_act_a16_consumes_act_a15_and_records_private_handoff():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ACT_A16_REVIEWER_PROMOTION_HOLD_FINAL_HANDOFF_PASS"
    assert payload["sourceReviewerPromotionHoldFeedGuard"] == "act-a15-reviewer-promotion-hold-feed-guard"
    assert summary["sourceFeedId"] == "act_a15_reviewer_promotion_hold_feed_guard_feed"
    assert summary["reviewerPromotionHoldFinalHandoffRecorded"] is True
    assert summary["privateReviewerHandoffReady"] is True
    assert summary["promotionAllowed"] is False


def test_act_a16_chain_summary_covers_a13_through_a15():
    payload = build_payload(ATLAS_GATE)
    chain = payload["promotionHoldChain"]
    assert [item["phase"] for item in chain] == ["ACT-A13", "ACT-A14", "ACT-A15"]
    assert payload["summary"]["chainRange"] == "ACT-A13-A15"
    assert payload["summary"]["chainEntryCount"] == 3
    assert chain[0]["recordedCounts"]["promotionHoldGates"] == 9
    assert chain[0]["recordedCounts"]["promotionHoldChecks"] == 9
    assert chain[1]["recordedCounts"]["snapshotChecks"] == 7
    assert chain[2]["recordedCounts"]["feedGuardRows"] == 6
    assert chain[2]["recordedCounts"]["blockedFalseSourceClaimFlags"] == 26
    assert all(item["promotionAllowed"] is False for item in chain)


def test_act_a16_handoff_packet_defines_private_review_pivot():
    handoff = build_handoff_packet()
    checklist = build_handoff_checklist()
    assert handoff["handoffStatus"] == "ready_for_private_review"
    assert handoff["reviewerDecisionStatus"] == "not_recorded"
    assert handoff["implementationStatus"] == "held_pending_reviewer_response"
    assert handoff["chainRange"] == "ACT-A13-A15"
    assert len(handoff["allowedPrivateOutcomes"]) == 7
    assert len(handoff["reviewerMustInspect"]) == 5
    assert len(handoff["pivotCriteria"]) == 4
    assert len(checklist) == 6


def test_act_a16_preserves_source_feed_guard_boundary():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["sourceFeedGuardRowCount"] == 6
    assert summary["sourceFeedGuardPassCount"] == 6
    assert summary["sourceAllowedTrueClaimFlagCount"] == 6
    assert summary["sourceBlockedClaimFlagCount"] == 26
    assert "without public promotion" in summary["sourceFeedNextAction"]


def test_act_a16_blocks_acceptance_soundness_public_and_runtime_claims():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert payload["blockedStatements"] == BLOCKED_STATEMENTS
    assert summary["blockedStatementCount"] == len(BLOCKED_STATEMENTS)
    assert summary["reviewerDecisionRecorded"] is False
    assert summary["reviewerApprovalRecorded"] is False
    assert summary["reviewerRejectionRecorded"] is False
    assert summary["concreteArtifactAccepted"] is False
    assert summary["productionValidatorImplemented"] is False
    assert summary["validatorSoundnessProved"] is False
    assert summary["soundnessProved"] is False
    assert summary["fullGaloisConnectionClaim"] is False
    assert summary["abstractInterpretationSoundnessProved"] is False
    assert summary["publicCopyApproved"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["runtimeLoweringChanged"] is False
    assert summary["machlibFileChanged"] is False
    assert summary["leanTypecheckPerformed"] is False
    assert summary["proofAttemptStarted"] is False
    assert summary["electronicsRepoTouched"] is False
    assert summary["laptopArtifactConsumed"] is False
    assert summary["publicReady"] is False


def test_act_a16_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    true_keys = {
        "reviewer_promotion_hold_final_handoff_recorded",
        "act_a15_reviewer_promotion_hold_feed_guard_consumed",
        "source_feed_rebuilt",
        "promotion_hold_chain_summary_recorded",
        "private_handoff_checklist_recorded",
        "private_reviewer_handoff_ready",
    }
    for key in true_keys:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in true_keys:
            assert value is False


def test_act_a16_next_action_stays_private():
    payload = build_payload(ATLAS_GATE)
    assert "without public promotion" in payload["summary"]["nextAction"]
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_act_a16_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# ACT-A16")


def test_act_a16_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/act_a16_reviewer_promotion_hold_final_handoff.py",
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
    assert "ACT_A16_REVIEWER_PROMOTION_HOLD_FINAL_HANDOFF_OK" in proc.stdout
