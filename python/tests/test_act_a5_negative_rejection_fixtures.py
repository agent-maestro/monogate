"""Tests for ACT-A5 negative rejection fixtures."""

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

from scripts.act_a5_negative_rejection_fixtures import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_act_a5_consumes_act_a4_and_records_negative_fixtures():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "ACT_A5_NEGATIVE_REJECTION_FIXTURES_PASS"
    assert payload["sourceFixtureExpansionPacket"] == "act-a4-dry-run-validator-fixture-expansion"
    assert payload["summary"]["sourceAcceptedFixtureCount"] == 3
    assert payload["summary"]["negativeFixtureCount"] == 5


def test_act_a5_covers_expected_failure_modes():
    payload = build_payload(ATLAS_GATE)
    assert set(payload["summary"]["failureModesCovered"]) == {
        "claim_escalation",
        "trace_gap",
        "public_gate_bypass",
        "runtime_drift",
        "lane_owner_drift",
    }
    assert payload["summary"]["claimEscalationFixtureIncluded"] is True
    assert payload["summary"]["traceGapFixtureIncluded"] is True
    assert payload["summary"]["publicGateBypassFixtureIncluded"] is True
    assert payload["summary"]["runtimeDriftFixtureIncluded"] is True
    assert payload["summary"]["laneOwnerDriftFixtureIncluded"] is True


def test_act_a5_records_expected_rejections_without_unexpected_accepts():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["rejectionCheckCount"] == 5
    assert payload["summary"]["expectedRejectCount"] == 5
    assert payload["summary"]["unexpectedAcceptCount"] == 0
    for fixture in payload["negativeFixtures"]:
        assert fixture["expectedStatus"] == "reject"
        assert fixture["expectedRejectReason"]
    for check in payload["rejectionChecks"]:
        assert check["status"] == "expected_reject"
        assert check["productionValidatorUsed"] is False


def test_act_a5_negative_mutations_are_visible_and_bounded():
    payload = build_payload(ATLAS_GATE)
    by_mode = {fixture["failureMode"]: fixture for fixture in payload["negativeFixtures"]}
    assert by_mode["claim_escalation"]["mutatedFixture"]["claimFlags"]["soundness_proved"] is True
    assert by_mode["trace_gap"]["mutatedFixture"]["checkedStatement"] == ""
    assert by_mode["public_gate_bypass"]["mutatedFixture"]["publicStatus"] == "public_ready"
    assert by_mode["runtime_drift"]["mutatedFixture"]["runtimeControl"] == "runtime_lowering_changed"
    assert by_mode["lane_owner_drift"]["mutatedFixture"]["claimFlags"]["electronics_repo_touched"] is True
    assert by_mode["lane_owner_drift"]["mutatedFixture"]["claimFlags"]["laptop_artifact_consumed"] is True


def test_act_a5_records_no_production_validator_or_soundness_claim():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["negativeRejectionFixturesRecorded"] is True
    assert payload["summary"]["actA4FixtureExpansionConsumed"] is True
    assert payload["summary"]["expectedRejectionsRecorded"] is True
    assert payload["summary"]["dryRunRejectionGateRecorded"] is True
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
    assert payload["summary"]["publicReady"] is False


def test_act_a5_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    true_keys = {
        "negative_rejection_fixtures_recorded",
        "act_a4_fixture_expansion_consumed",
        "expected_rejections_recorded",
        "rejection_failure_modes_recorded",
        "dry_run_rejection_gate_recorded",
    }
    for key in true_keys:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in true_keys:
            assert value is False


def test_act_a5_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# ACT-A5")


def test_act_a5_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/act_a5_negative_rejection_fixtures.py",
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
    assert "ACT_A5_NEGATIVE_REJECTION_FIXTURES_OK" in proc.stdout
