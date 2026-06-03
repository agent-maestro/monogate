"""Tests for ACT-A10 reviewer intake guard."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.act_a10_reviewer_intake_guard import (
    BLOCKED_SOURCE_CLAIM_FLAGS,
    CLAIM_FLAGS,
    EXPECTED_SOURCE_ARTIFACT,
    EXPECTED_SOURCE_FEED_ID,
    EXPECTED_SOURCE_STATUS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_act_a10_consumes_act_a9_reviewer_feed_guard():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "ACT_A10_REVIEWER_INTAKE_GUARD_PASS"
    assert payload["sourceReviewerFeedGuard"] == EXPECTED_SOURCE_ARTIFACT
    assert payload["summary"]["sourceFeedId"] == EXPECTED_SOURCE_FEED_ID
    assert payload["summary"]["sourceFeedGuardRowCount"] == 6
    assert payload["summary"]["sourceFeedGuardPassCount"] == 6


def test_act_a10_intake_guard_rows_pass_exactly():
    payload = build_payload(ATLAS_GATE)
    rows = {row["guardRowId"]: row for row in payload["intakeGuardRows"]}
    assert set(rows) == {
        "act_a10_intake_guard:source_artifact",
        "act_a10_intake_guard:source_status",
        "act_a10_intake_guard:source_feed_id",
        "act_a10_intake_guard:source_feed_guard_rows_passed",
        "act_a10_intake_guard:source_next_action_is_private",
        "act_a10_intake_guard:blocked_claim_flags_false",
        "act_a10_intake_guard:no_laptop_or_course_artifact_accepted",
    }
    assert rows["act_a10_intake_guard:source_artifact"]["expected"] == EXPECTED_SOURCE_ARTIFACT
    assert rows["act_a10_intake_guard:source_status"]["expected"] == EXPECTED_SOURCE_STATUS
    assert payload["summary"]["intakeGuardRowCount"] == 7
    assert payload["summary"]["intakeGuardPassCount"] == 7
    for row in rows.values():
        assert row["status"] == "pass"
        assert row["observed"] == row["expected"]


def test_act_a10_source_blocked_claim_flags_remain_false():
    payload = build_payload(ATLAS_GATE)
    blocked_row = next(
        row for row in payload["intakeGuardRows"] if row["guardRowId"] == "act_a10_intake_guard:blocked_claim_flags_false"
    )
    assert blocked_row["observed"] == sorted(BLOCKED_SOURCE_CLAIM_FLAGS)
    assert payload["summary"]["blockedSourceClaimFlagCount"] == len(BLOCKED_SOURCE_CLAIM_FLAGS)
    assert payload["summary"]["sourceClaimFlagCount"] == 30


def test_act_a10_records_no_validator_soundness_public_or_laptop_claim():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["reviewerIntakeGuardRecorded"] is True
    assert payload["summary"]["actA9ReviewerFeedGuardConsumed"] is True
    assert payload["summary"]["sourceFeedGuardRowsConsumed"] is True
    assert payload["summary"]["intakeGuardRowsRecorded"] is True
    assert payload["summary"]["intakeGuardChecksRecorded"] is True
    assert payload["summary"]["intakeGuardChecksPassed"] is True
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


def test_act_a10_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    true_keys = {
        "reviewer_intake_guard_recorded",
        "act_a9_reviewer_feed_guard_consumed",
        "source_feed_guard_rows_consumed",
        "intake_guard_rows_recorded",
        "intake_guard_checks_recorded",
        "intake_guard_checks_passed",
    }
    for key in true_keys:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in true_keys:
            assert value is False


def test_act_a10_next_action_stays_private_and_no_laptop_artifact_is_accepted():
    payload = build_payload(ATLAS_GATE)
    assert "without public promotion" in payload["summary"]["nextAction"]
    no_laptop_row = next(
        row
        for row in payload["intakeGuardRows"]
        if row["guardRowId"] == "act_a10_intake_guard:no_laptop_or_course_artifact_accepted"
    )
    assert no_laptop_row["observed"] == {"laptopArtifactConsumed": False, "publicReady": False}


def test_act_a10_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# ACT-A10")


def test_act_a10_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/act_a10_reviewer_intake_guard.py",
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
    assert "ACT_A10_REVIEWER_INTAKE_GUARD_OK" in proc.stdout
