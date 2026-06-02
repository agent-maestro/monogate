"""Tests for EML-D46 post positive log-exp pause next selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d46_post_positive_log_exp_pause_next_selector import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def option_by_id(payload, option_id: str):
    return next(item for item in payload["selectorOptions"] if item["optionId"] == option_id)


def test_d46_consumes_d45_pause_freeze_packet():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D46_POST_POSITIVE_LOG_EXP_PAUSE_NEXT_SELECTOR_PASS"
    assert payload["sourceFreezePacket"] == "eml-d45-positive-log-exp-branch-pause-freeze-packet"
    assert payload["summary"]["branchPauseStarted"] is True
    assert payload["summary"]["checkedWitnessDeltaFrozen"] is True
    assert payload["summary"]["privateFreezePacket"] is True


def test_d46_preserves_frozen_positive_log_exp_delta():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["frozenWitnessName"] == "MachLib.Real.positive_log_exp_roundtrip_witness"
    assert payload["summary"]["frozenCheckedStatement"] == "0 < x -> exp (log x) = x"
    assert payload["summary"]["frozenGuardCount"] == 1
    assert payload["summary"]["frozenCaveatCount"] == 5
    assert payload["summary"]["frozenBlockedPhraseCount"] == 8
    assert payload["summary"]["positiveDomainGuardRequired"] is True
    assert payload["summary"]["publicHoldPreserved"] is True


def test_d46_selects_constant_coordinate_refresh():
    payload = build_payload(ATLAS_GATE)
    selected = option_by_id(payload, "constant_coordinate_refresh_selector")
    assert payload["decision"] == "select_constant_coordinate_refresh_selector"
    assert payload["summary"]["selectedOptionId"] == "constant_coordinate_refresh_selector"
    assert payload["summary"]["selectedNextArtifact"] == "EML-D47 constant-coordinate refresh feasibility selector"
    assert payload["summary"]["nextActionSelected"] is True
    assert payload["summary"]["constantCoordinateRefreshSelected"] is True
    assert selected["selectionStatus"] == "selected_next"
    assert selected["lane"] == "private_bounded_identity_lane"


def test_d46_parks_trig_and_public_copy_gate():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["optionCount"] == 3
    assert option_by_id(payload, "bounded_trig_identity_feasibility_selector")["selectionStatus"] == "candidate_later"
    assert option_by_id(payload, "human_approved_public_copy_gate")["selectionStatus"] == "candidate_later_requires_human_approval"
    assert payload["summary"]["boundedTrigFeasibilitySelected"] is False
    assert payload["summary"]["humanPublicCopyGateSelected"] is False
    assert payload["summary"]["humanApprovalRecorded"] is False


def test_d46_starts_no_public_copy_or_implementation():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["proofAttemptStarted"] is False


def test_d46_keeps_runtime_log_exp_and_laptop_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeBoundaryPreserved"] is True
    assert payload["summary"]["runtimeLoweringControl"] == "standard_log_exp_remains_runtime_control"
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d46_claim_flags_are_selector_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsSelectorOnly"] is True
    for key in ["next_action_selected", "constant_coordinate_refresh_selected"]:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in {"next_action_selected", "constant_coordinate_refresh_selected"}:
            assert value is False
    for option in payload["selectorOptions"]:
        assert option["claimFlags"]["next_action_selected"] is True
        assert option["claimFlags"]["constant_coordinate_refresh_selected"] is True
        for key, value in option["claimFlags"].items():
            if key not in {"next_action_selected", "constant_coordinate_refresh_selected"}:
                assert value is False


def test_d46_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D46")


def test_d46_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d46_post_positive_log_exp_pause_next_selector.py",
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
    assert "EML_D46_POST_POSITIVE_LOG_EXP_PAUSE_NEXT_SELECTOR_OK" in proc.stdout
