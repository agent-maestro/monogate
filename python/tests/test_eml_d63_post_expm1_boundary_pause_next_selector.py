"""Tests for EML-D63 post expm1-boundary pause next selector."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d63_post_expm1_boundary_pause_next_selector import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_d63_consumes_d62_and_selects_next_bounded_identity_branch():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "EML_D63_POST_EXPM1_BOUNDARY_PAUSE_NEXT_SELECTOR_PASS"
    assert payload["sourceFreezePacket"] == "eml-d62-expm1-boundary-branch-pause-freeze-packet"
    assert summary["selectedOptionId"] == "next_bounded_identity_branch_selector"
    assert summary["selectedNextArtifact"] == "EML-D64 bounded identity branch candidate selector"
    assert summary["nextActionSelected"] is True
    assert summary["nextBoundedIdentityBranchSelected"] is True


def test_d63_preserves_d62_expm1_freeze_boundary():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["branchPauseStarted"] is True
    assert summary["checkedWitnessCopyFrozen"] is True
    assert summary["privateFreezePacket"] is True
    assert summary["frozenWitnessName"] == "MachLib.Real.expm1_boundary_identity_witness"
    assert summary["frozenCheckedStatement"] == "eml x (exp 1) = exp x - 1"
    assert summary["frozenGuardCount"] == 0
    assert summary["frozenCaveatCount"] == 8
    assert summary["frozenBlockedPhraseCount"] == 10
    assert summary["nonDuplicateWitnessName"] == "MachLib.Real.atlas_exp_from_eml_witness"
    assert summary["duplicatesExistingExpBranchWitness"] is False


def test_d63_options_keep_later_paths_parked():
    payload = build_payload(ATLAS_GATE)
    options = {option["optionId"]: option for option in payload["selectorOptions"]}
    assert payload["summary"]["optionCount"] == 3
    assert options["next_bounded_identity_branch_selector"]["selectionStatus"] == "selected_next"
    assert options["bounded_trig_identity_feasibility_selector"]["selectionStatus"] == "candidate_later"
    assert options["human_approved_public_copy_gate"]["selectionStatus"] == "candidate_later_requires_human_approval"
    assert payload["selectedOption"]["optionId"] == "next_bounded_identity_branch_selector"


def test_d63_keeps_public_proof_runtime_and_laptop_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["boundedTrigFeasibilitySelected"] is False
    assert summary["humanPublicCopyGateSelected"] is False
    assert summary["humanApprovalRecorded"] is False
    assert summary["publicCopyApproved"] is False
    assert summary["publicPromotionPerformed"] is False
    assert summary["publicEducationPromotionPerformed"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["advantageLabCaseAdded"] is False
    assert summary["implementationStarted"] is False
    assert summary["machlibFileChanged"] is False
    assert summary["leanTypecheckPerformed"] is False
    assert summary["candidateProved"] is False
    assert summary["proofAttemptStarted"] is False
    assert summary["runtimeLoweringChanged"] is False
    assert summary["protectedExpm1ReplacementClaim"] is False
    assert summary["electronicsRepoTouched"] is False
    assert summary["laptopArtifactConsumed"] is False
    assert summary["publicReady"] is False


def test_d63_runtime_control_and_public_hold_preserved():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["runtimeLoweringControl"] == "protected_expm1_remains_runtime_control"
    assert summary["runtimeGuardrailStatus"] == "protected_expm1_runtime_control_required"
    assert summary["publicAtlasStatus"] == "held_private"


def test_d63_claim_flags_are_selector_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsSelectorOnly"] is True
    for key in ["next_action_selected", "next_bounded_identity_branch_selected"]:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in {"next_action_selected", "next_bounded_identity_branch_selected"}:
            assert value is False


def test_d63_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D63")


def test_d63_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d63_post_expm1_boundary_pause_next_selector.py",
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
    assert "EML_D63_POST_EXPM1_BOUNDARY_PAUSE_NEXT_SELECTOR_OK" in proc.stdout
