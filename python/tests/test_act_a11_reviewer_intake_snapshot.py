"""Tests for ACT-A11 reviewer intake snapshot."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.act_a11_reviewer_intake_snapshot import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_act_a11_consumes_act_a10_and_records_snapshots():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "ACT_A11_REVIEWER_INTAKE_SNAPSHOT_PASS"
    assert payload["sourceReviewerIntakeGuard"] == "act-a10-reviewer-intake-guard"
    assert payload["summary"]["sourceFeedGuardRowCount"] == 6
    assert payload["summary"]["intakeGuardRowCount"] == 7


def test_act_a11_snapshot_counts_preserve_intake_guard():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["sourceFeedGuardPassCount"] == 6
    assert payload["summary"]["sourceClaimFlagCount"] == 30
    assert payload["summary"]["blockedSourceClaimFlagCount"] == 16
    assert payload["summary"]["intakeGuardPassCount"] == 7
    for snapshot in [payload["baselineSnapshot"], payload["observedSnapshot"]]:
        assert snapshot["sourceFeedGuardRowCount"] == 6
        assert snapshot["sourceFeedGuardPassCount"] == 6
        assert snapshot["sourceClaimFlagCount"] == 30
        assert snapshot["blockedSourceClaimFlagCount"] == 16
        assert snapshot["intakeGuardRowCount"] == 7
        assert snapshot["intakeGuardPassCount"] == 7


def test_act_a11_snapshot_digests_are_stable():
    payload = build_payload(ATLAS_GATE)
    baseline = payload["baselineSnapshot"]
    observed = payload["observedSnapshot"]
    for key in [
        "sourceFeedGuardRowDigest",
        "intakeGuardRowDigest",
        "summaryDigest",
        "nonClaimDigest",
        "claimFlagDigest",
    ]:
        assert baseline[key] == observed[key]
        assert len(baseline[key]) == 64


def test_act_a11_snapshot_checks_pass_exactly():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["snapshotCheckCount"] == 5
    assert payload["summary"]["snapshotCheckPassCount"] == 5
    checks = {check["checkId"]: check for check in payload["snapshotChecks"]}
    assert set(checks) == {
        "sourceFeedGuardRowDigest_matches",
        "intakeGuardRowDigest_matches",
        "summaryDigest_matches",
        "nonClaimDigest_matches",
        "claimFlagDigest_matches",
    }
    for check in checks.values():
        assert check["status"] == "pass"
        assert check["baseline"] == check["observed"]


def test_act_a11_records_no_production_validator_or_soundness_claim():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["reviewerIntakeSnapshotRecorded"] is True
    assert payload["summary"]["actA10ReviewerIntakeGuardConsumed"] is True
    assert payload["summary"]["baselineSnapshotRecorded"] is True
    assert payload["summary"]["observedSnapshotRecorded"] is True
    assert payload["summary"]["snapshotChecksRecorded"] is True
    assert payload["summary"]["snapshotChecksPassed"] is True
    assert payload["summary"]["productionValidatorImplemented"] is False
    assert payload["summary"]["validatorSoundnessProved"] is False
    assert payload["summary"]["soundnessProved"] is False
    assert payload["summary"]["fullGaloisConnectionClaim"] is False
    assert payload["summary"]["abstractInterpretationSoundnessProved"] is False
    assert payload["summary"]["visualizationStarted"] is False
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["proofAttemptStarted"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["rendererImplemented"] is False
    assert payload["summary"]["rendererExecuted"] is False
    assert payload["summary"]["publicReady"] is False


def test_act_a11_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    true_keys = {
        "reviewer_intake_snapshot_recorded",
        "act_a10_reviewer_intake_guard_consumed",
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


def test_act_a11_next_action_stays_private():
    payload = build_payload(ATLAS_GATE)
    assert "without public promotion" in payload["summary"]["nextAction"]
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_act_a11_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# ACT-A11")


def test_act_a11_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/act_a11_reviewer_intake_snapshot.py",
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
    assert "ACT_A11_REVIEWER_INTAKE_SNAPSHOT_OK" in proc.stdout
