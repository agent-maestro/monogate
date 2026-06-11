"""Tests for ACT-A12 reviewer intake feed guard."""

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

from scripts.act_a12_reviewer_intake_feed_guard import (
    ALLOWED_TRUE_SOURCE_CLAIM_FLAGS,
    BLOCKED_SOURCE_CLAIM_FLAGS,
    CLAIM_FLAGS,
    EXPECTED_SOURCE_DECISION,
    EXPECTED_SOURCE_FEED_ID,
    EXPECTED_SOURCE_STATUS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_act_a12_consumes_act_a11_and_rebuilds_feed():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "ACT_A12_REVIEWER_INTAKE_FEED_GUARD_PASS"
    assert payload["sourceReviewerIntakeSnapshot"] == "act-a11-reviewer-intake-snapshot"
    assert payload["sourceFeed"]["feedId"] == EXPECTED_SOURCE_FEED_ID
    assert payload["sourceFeed"]["status"] == EXPECTED_SOURCE_STATUS
    assert payload["sourceFeed"]["decision"] == EXPECTED_SOURCE_DECISION


def test_act_a12_feed_guard_rows_pass_exactly():
    payload = build_payload(ATLAS_GATE)
    rows = {row["guardRowId"]: row for row in payload["feedGuardRows"]}
    assert set(rows) == {
        "act_a12_feed_guard:feed_id",
        "act_a12_feed_guard:status",
        "act_a12_feed_guard:decision",
        "act_a12_feed_guard:next_action_is_private",
        "act_a12_feed_guard:allowed_true_claim_flags",
        "act_a12_feed_guard:blocked_claim_flags_false",
    }
    assert payload["summary"]["feedGuardRowCount"] == 6
    assert payload["summary"]["feedGuardPassCount"] == 6
    for row in rows.values():
        assert row["status"] == "pass"
        assert row["observed"] == row["expected"]


def test_act_a12_source_claim_flags_are_guarded():
    payload = build_payload(ATLAS_GATE)
    source_flags = payload["sourceFeed"]["claimFlags"]
    true_flags = {key for key, value in source_flags.items() if value is True}
    assert true_flags == ALLOWED_TRUE_SOURCE_CLAIM_FLAGS
    assert payload["summary"]["allowedTrueSourceClaimFlagCount"] == 6
    assert payload["summary"]["blockedSourceClaimFlagCount"] == len(BLOCKED_SOURCE_CLAIM_FLAGS)
    for key in BLOCKED_SOURCE_CLAIM_FLAGS:
        assert source_flags[key] is False


def test_act_a12_records_no_production_validator_or_soundness_claim():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["reviewerIntakeFeedGuardRecorded"] is True
    assert payload["summary"]["actA11ReviewerIntakeSnapshotConsumed"] is True
    assert payload["summary"]["sourceFeedRebuilt"] is True
    assert payload["summary"]["feedGuardRowsRecorded"] is True
    assert payload["summary"]["feedGuardChecksRecorded"] is True
    assert payload["summary"]["feedGuardChecksPassed"] is True
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


def test_act_a12_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    true_keys = {
        "reviewer_intake_feed_guard_recorded",
        "act_a11_reviewer_intake_snapshot_consumed",
        "source_feed_rebuilt",
        "feed_guard_rows_recorded",
        "feed_guard_checks_recorded",
        "feed_guard_checks_passed",
    }
    for key in true_keys:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in true_keys:
            assert value is False


def test_act_a12_next_action_stays_private():
    payload = build_payload(ATLAS_GATE)
    assert "without public promotion" in payload["summary"]["nextAction"]
    assert "without public promotion" in payload["sourceFeed"]["nextAction"]
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_act_a12_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# ACT-A12")


def test_act_a12_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/act_a12_reviewer_intake_feed_guard.py",
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
    assert "ACT_A12_REVIEWER_INTAKE_FEED_GUARD_OK" in proc.stdout
