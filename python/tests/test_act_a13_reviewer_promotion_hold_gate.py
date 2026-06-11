"""Tests for ACT-A13 reviewer promotion hold gate."""

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

from scripts.act_a13_reviewer_promotion_hold_gate import (
    BLOCKED_STATEMENTS,
    CLAIM_FLAGS,
    REQUIRED_HELD_GATES,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_act_a13_consumes_act_a12_and_records_hold_gate():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "ACT_A13_REVIEWER_PROMOTION_HOLD_GATE_PASS"
    assert payload["sourceReviewerIntakeFeedGuard"] == "act-a12-reviewer-intake-feed-guard"
    assert payload["sourceFeed"]["feedId"] == "act_a12_reviewer_intake_feed_guard_feed"
    assert summary["reviewerPromotionHoldGateRecorded"] is True
    assert summary["actA12ReviewerIntakeFeedGuardConsumed"] is True
    assert summary["promotionAllowed"] is False


def test_act_a13_promotion_gates_are_held():
    payload = build_payload(ATLAS_GATE)
    gates = {gate["gateId"]: gate for gate in payload["promotionHoldGates"]}
    assert set(REQUIRED_HELD_GATES).issubset(gates)
    assert gates["source_next_action_private"]["observed"] is True
    assert gates["source_next_action_private"]["expected"] is True
    assert payload["summary"]["promotionHoldGateCount"] == 9
    for gate in gates.values():
        assert gate["promotionAllowed"] is False


def test_act_a13_promotion_hold_checks_pass_exactly():
    payload = build_payload(ATLAS_GATE)
    checks = {check["checkId"]: check for check in payload["promotionHoldChecks"]}
    assert payload["summary"]["promotionHoldCheckCount"] == 9
    assert payload["summary"]["promotionHoldPassCount"] == 9
    assert len(checks) == 9
    for check in checks.values():
        assert check["status"] == "pass"
        assert check["observed"] == check["expected"]


def test_act_a13_blocks_promotion_statements_and_claims():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert payload["blockedStatements"] == BLOCKED_STATEMENTS
    assert summary["blockedStatementCount"] == len(BLOCKED_STATEMENTS)
    assert "ACT artifacts are public-ready." in payload["blockedStatements"]
    assert summary["reviewerDecisionRecorded"] is False
    assert summary["concreteArtifactAccepted"] is False
    assert summary["productionValidatorImplemented"] is False
    assert summary["validatorSoundnessProved"] is False
    assert summary["soundnessProved"] is False
    assert summary["fullGaloisConnectionClaim"] is False
    assert summary["abstractInterpretationSoundnessProved"] is False
    assert summary["publicCopyApproved"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["laptopArtifactConsumed"] is False
    assert summary["publicReady"] is False


def test_act_a13_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    true_keys = {
        "reviewer_promotion_hold_gate_recorded",
        "act_a12_reviewer_intake_feed_guard_consumed",
        "source_feed_rebuilt",
        "promotion_hold_gates_recorded",
        "promotion_hold_checks_recorded",
        "promotion_hold_checks_passed",
    }
    for key in true_keys:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in true_keys:
            assert value is False


def test_act_a13_next_action_stays_private():
    payload = build_payload(ATLAS_GATE)
    assert "without public promotion" in payload["summary"]["nextAction"]
    assert "without public promotion" in payload["sourceFeed"]["nextAction"]
    assert payload["summary"]["publicReady"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False


def test_act_a13_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# ACT-A13")


def test_act_a13_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/act_a13_reviewer_promotion_hold_gate.py",
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
    assert "ACT_A13_REVIEWER_PROMOTION_HOLD_GATE_OK" in proc.stdout
