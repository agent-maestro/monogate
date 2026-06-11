"""Tests for EML-D62 expm1 boundary branch pause freeze packet."""

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

from scripts.eml_d62_expm1_boundary_branch_pause_freeze_packet import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def parked_by_id(payload, option_id: str):
    return next(item for item in payload["parkedOptions"] if item["optionId"] == option_id)


def test_d62_consumes_d61_selected_pause_freeze_option():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D62_EXPM1_BOUNDARY_BRANCH_PAUSE_FREEZE_PACKET_PASS"
    assert payload["sourceSelector"] == "eml-d61-expm1-boundary-copy-review-next-selector"
    assert payload["summary"]["selectedOptionId"] == "expm1_boundary_pause_freeze_packet"


def test_d62_freezes_expm1_checked_witness_copy():
    payload = build_payload(ATLAS_GATE)
    row = payload["freezeRows"][0]
    assert payload["summary"]["branchPauseStarted"] is True
    assert payload["summary"]["checkedWitnessCopyFrozen"] is True
    assert payload["summary"]["privateFreezePacket"] is True
    assert row["freezeStatus"] == "private_checked_witness_copy_frozen"
    assert row["machlibName"] == "MachLib.Real.expm1_boundary_identity_witness"
    assert row["checkedStatement"] == "eml x (exp 1) = exp x - 1"
    assert row["guards"] == []


def test_d62_preserves_non_duplicate_exp_branch_boundary():
    payload = build_payload(ATLAS_GATE)
    row = payload["freezeRows"][0]
    assert row["nonDuplicateWitnessName"] == "MachLib.Real.atlas_exp_from_eml_witness"
    assert row["duplicatesExistingExpBranchWitness"] is False
    assert payload["summary"]["sourceSelectedCandidateId"] == "expm1_boundary_identity"
    assert payload["summary"]["sourceSelectedFamily"] == "protected_runtime_boundary_identity"


def test_d62_preserves_d60_caveats_blockers_and_runtime_control():
    payload = build_payload(ATLAS_GATE)
    row = payload["freezeRows"][0]
    assert payload["summary"]["guardCount"] == 0
    assert payload["summary"]["frozenCaveatCount"] == 8
    assert payload["summary"]["frozenBlockedPhraseCount"] == 10
    assert payload["summary"]["sourceD60RequiredCaveatCount"] == 8
    assert payload["summary"]["sourceD60BlockedGlobalPhraseCount"] == 10
    assert payload["summary"]["runtimeGuardrailStatus"] == "protected_expm1_runtime_control_required"
    assert payload["summary"]["publicAtlasStatus"] == "held_private"
    assert payload["summary"]["runtimeLoweringControl"] == "protected_expm1_remains_runtime_control"
    assert row["runtimeControl"] == "protected_expm1_remains_runtime_control"
    assert "The checked statement is eml x (exp 1) = exp x - 1." in row["frozenCaveats"]
    assert "protected expm1 replacement" in row["frozenBlockedPhrases"]


def test_d62_parks_future_branches_and_public_gate():
    payload = build_payload(ATLAS_GATE)
    assert parked_by_id(payload, "next_bounded_identity_branch_selector")["status"] == "parked_after_expm1_boundary_pause"
    assert parked_by_id(payload, "bounded_trig_identity_feasibility_selector")["status"] == "parked_after_expm1_boundary_pause"
    assert parked_by_id(payload, "human_approved_public_copy_gate")["status"] == "parked_requires_explicit_human_approval"
    assert payload["summary"]["parkedNextBoundedIdentityBranchSelector"] is True
    assert payload["summary"]["parkedBoundedTrigFeasibility"] is True
    assert payload["summary"]["parkedHumanApprovedPublicCopyGate"] is True
    assert payload["summary"]["newBoundedBranchSelected"] is False
    assert payload["summary"]["boundedTrigFeasibilitySelected"] is False
    assert payload["summary"]["humanApprovedPublicCopyGateSelected"] is False
    assert payload["summary"]["humanApprovalRecorded"] is False


def test_d62_starts_no_public_copy_or_implementation():
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
    assert payload["summary"]["candidateProvedThisPhase"] is False
    assert payload["summary"]["proofAttemptStarted"] is False
    assert payload["freezeRows"][0]["publicPromotionAllowed"] is False


def test_d62_keeps_runtime_expm1_and_laptop_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["protectedExpm1ReplacementClaim"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d62_claim_flags_are_freeze_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsFrozenOnly"] is True
    for key in ["branch_pause_started", "checked_witness_copy_frozen", "private_freeze_packet"]:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in {"branch_pause_started", "checked_witness_copy_frozen", "private_freeze_packet"}:
            assert value is False
    for row in payload["freezeRows"]:
        for key, value in row["claimFlags"].items():
            if key not in {"branch_pause_started", "checked_witness_copy_frozen", "private_freeze_packet"}:
                assert value is False


def test_d62_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D62")


def test_d62_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d62_expm1_boundary_branch_pause_freeze_packet.py",
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
    assert "EML_D62_EXPM1_BOUNDARY_BRANCH_PAUSE_FREEZE_PACKET_OK" in proc.stdout
