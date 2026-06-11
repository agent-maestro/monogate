"""Tests for EML-D54 post constant-coordinate pause next selector."""

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

from scripts.eml_d54_post_constant_coordinate_pause_next_selector import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def option_by_id(payload, option_id: str):
    return next(item for item in payload["selectorOptions"] if item["optionId"] == option_id)


def test_d54_consumes_d53_pause_freeze_packet():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D54_POST_CONSTANT_COORDINATE_PAUSE_NEXT_SELECTOR_PASS"
    assert payload["sourceFreezePacket"] == "eml-d53-constant-coordinate-branch-pause-freeze-packet"
    assert payload["summary"]["branchPauseStarted"] is True
    assert payload["summary"]["checkedWitnessDeltaFrozen"] is True
    assert payload["summary"]["privateFreezePacket"] is True


def test_d54_preserves_frozen_constant_coordinate_delta():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["frozenWitnessName"] == "MachLib.Real.constant_coordinate_zero_exp_two_witness"
    assert payload["summary"]["frozenSourceStatement"] == "eml 0 (exp 2) = -1"
    assert payload["summary"]["frozenCheckedStatement"] == "eml 0 (exp (1 + 1)) = -1"
    assert payload["summary"]["frozenGuardCount"] == 0
    assert payload["summary"]["frozenCaveatCount"] == 8
    assert payload["summary"]["frozenBlockedPhraseCount"] == 10
    assert payload["summary"]["localSpellingUsesOnePlusOne"] is True
    assert payload["summary"]["publicHoldPreserved"] is True


def test_d54_preserves_non_duplicate_boundary():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["existingConstantWitnessName"] == "MachLib.Real.constants_zero_one_e_boundary_witness"
    assert payload["summary"]["duplicatesExistingConstantWitness"] is False


def test_d54_selects_next_bounded_identity_branch():
    payload = build_payload(ATLAS_GATE)
    selected = option_by_id(payload, "next_bounded_identity_branch_selector")
    assert payload["decision"] == "select_next_bounded_identity_branch_selector"
    assert payload["summary"]["selectedOptionId"] == "next_bounded_identity_branch_selector"
    assert payload["summary"]["selectedNextArtifact"] == "EML-D55 bounded identity branch candidate selector"
    assert payload["summary"]["nextActionSelected"] is True
    assert payload["summary"]["nextBoundedIdentityBranchSelected"] is True
    assert selected["selectionStatus"] == "selected_next"
    assert selected["lane"] == "private_bounded_identity_lane"


def test_d54_parks_trig_and_public_copy_gate():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["optionCount"] == 3
    assert option_by_id(payload, "bounded_trig_identity_feasibility_selector")["selectionStatus"] == "candidate_later"
    assert option_by_id(payload, "human_approved_public_copy_gate")["selectionStatus"] == "candidate_later_requires_human_approval"
    assert payload["summary"]["boundedTrigFeasibilitySelected"] is False
    assert payload["summary"]["humanPublicCopyGateSelected"] is False
    assert payload["summary"]["humanApprovalRecorded"] is False


def test_d54_starts_no_public_copy_or_implementation():
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


def test_d54_keeps_runtime_log_exp_and_laptop_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeBoundaryPreserved"] is True
    assert payload["summary"]["runtimeLoweringControl"] == "standard_log_exp_and_arithmetic_remain_runtime_controls"
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d54_claim_flags_are_selector_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsSelectorOnly"] is True
    for key in ["next_action_selected", "next_bounded_identity_branch_selected"]:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in {"next_action_selected", "next_bounded_identity_branch_selected"}:
            assert value is False
    for option in payload["selectorOptions"]:
        assert option["claimFlags"]["next_action_selected"] is True
        assert option["claimFlags"]["next_bounded_identity_branch_selected"] is True
        for key, value in option["claimFlags"].items():
            if key not in {"next_action_selected", "next_bounded_identity_branch_selected"}:
                assert value is False


def test_d54_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D54")


def test_d54_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d54_post_constant_coordinate_pause_next_selector.py",
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
    assert "EML_D54_POST_CONSTANT_COORDINATE_PAUSE_NEXT_SELECTOR_OK" in proc.stdout
