"""Tests for ACT-A14 reviewer promotion hold snapshot."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.act_a14_reviewer_promotion_hold_snapshot import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_act_a14_consumes_act_a13_and_records_snapshots():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "ACT_A14_REVIEWER_PROMOTION_HOLD_SNAPSHOT_PASS"
    assert payload["sourceReviewerPromotionHoldGate"] == "act-a13-reviewer-promotion-hold-gate"
    assert payload["summary"]["sourceFeedId"] == "act_a12_reviewer_intake_feed_guard_feed"
    assert payload["summary"]["reviewerPromotionHoldSnapshotRecorded"] is True
    assert payload["summary"]["actA13ReviewerPromotionHoldGateConsumed"] is True


def test_act_a14_snapshot_counts_preserve_promotion_hold_gate():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["promotionHoldGateCount"] == 9
    assert payload["summary"]["promotionHoldCheckCount"] == 9
    assert payload["summary"]["promotionHoldPassCount"] == 9
    assert payload["summary"]["blockedStatementCount"] == 6
    assert payload["summary"]["promotionAllowed"] is False
    for snapshot in [payload["baselineSnapshot"], payload["observedSnapshot"]]:
        assert snapshot["promotionHoldGateCount"] == 9
        assert snapshot["promotionHoldCheckCount"] == 9
        assert snapshot["promotionHoldPassCount"] == 9
        assert snapshot["blockedStatementCount"] == 6
        assert snapshot["promotionAllowed"] is False


def test_act_a14_snapshot_digests_are_stable():
    payload = build_payload(ATLAS_GATE)
    baseline = payload["baselineSnapshot"]
    observed = payload["observedSnapshot"]
    for key in [
        "sourceFeedDigest",
        "promotionHoldGateDigest",
        "promotionHoldCheckDigest",
        "blockedStatementDigest",
        "summaryDigest",
        "nonClaimDigest",
        "claimFlagDigest",
    ]:
        assert baseline[key] == observed[key]
        assert len(baseline[key]) == 64


def test_act_a14_snapshot_checks_pass_exactly():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["snapshotCheckCount"] == 7
    assert payload["summary"]["snapshotCheckPassCount"] == 7
    checks = {check["checkId"]: check for check in payload["snapshotChecks"]}
    assert set(checks) == {
        "sourceFeedDigest_matches",
        "promotionHoldGateDigest_matches",
        "promotionHoldCheckDigest_matches",
        "blockedStatementDigest_matches",
        "summaryDigest_matches",
        "nonClaimDigest_matches",
        "claimFlagDigest_matches",
    }
    for check in checks.values():
        assert check["status"] == "pass"
        assert check["baseline"] == check["observed"]


def test_act_a14_records_no_acceptance_or_public_promotion_claim():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["baselineSnapshotRecorded"] is True
    assert summary["observedSnapshotRecorded"] is True
    assert summary["snapshotChecksRecorded"] is True
    assert summary["snapshotChecksPassed"] is True
    assert summary["reviewerDecisionRecorded"] is False
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
    assert summary["rendererImplemented"] is False
    assert summary["rendererExecuted"] is False
    assert summary["publicReady"] is False


def test_act_a14_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    true_keys = {
        "reviewer_promotion_hold_snapshot_recorded",
        "act_a13_reviewer_promotion_hold_gate_consumed",
        "baseline_snapshot_recorded",
        "observed_snapshot_recorded",
        "snapshot_checks_recorded",
        "snapshot_checks_passed",
    }
    for key in true_keys:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in true_keys:
            assert value is False


def test_act_a14_next_action_stays_private():
    payload = build_payload(ATLAS_GATE)
    assert "without public promotion" in payload["summary"]["nextAction"]
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_act_a14_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# ACT-A14")


def test_act_a14_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/act_a14_reviewer_promotion_hold_snapshot.py",
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
    assert "ACT_A14_REVIEWER_PROMOTION_HOLD_SNAPSHOT_OK" in proc.stdout
