"""Tests for EML-D71 probability logit branch pause freeze packet."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d71_probability_logit_branch_pause_freeze_packet import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def parked_by_id(payload, option_id: str):
    return next(item for item in payload["parkedOptions"] if item["optionId"] == option_id)


def test_d71_consumes_d70_selected_pause_freeze_option():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D71_PROBABILITY_LOGIT_BRANCH_PAUSE_FREEZE_PACKET_PASS"
    assert payload["sourceSelector"] == "eml-d70-probability-logit-branch-pause-next-selector"
    assert payload["summary"]["selectedOptionId"] == "probability_logit_branch_pause_freeze_packet"


def test_d71_freezes_probability_logit_checked_witness_copy():
    payload = build_payload(ATLAS_GATE)
    row = payload["freezeRows"][0]
    assert payload["summary"]["branchPauseStarted"] is True
    assert payload["summary"]["checkedWitnessCopyFrozen"] is True
    assert payload["summary"]["privateFreezePacket"] is True
    assert row["freezeStatus"] == "private_checked_witness_copy_frozen"
    assert row["machlibName"] == "MachLib.Real.probability_logit_boundary_coordinate_witness"
    assert row["checkedStatement"] == (
        "0 < p -> p < 1 -> eml (log p) (exp (log (1 - p))) = p - log (1 - p)"
    )
    assert row["guards"] == ["0 < p", "p < 1"]


def test_d71_preserves_probability_logit_guard_and_boundary_counts():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["sourceSelectedCandidateId"] == "probability_logit_boundary_coordinate"
    assert payload["summary"]["sourceSelectedFamily"] == "guarded_probability_log_coordinate"
    assert payload["summary"]["guardCount"] == 2
    assert payload["summary"]["sourceDerivedDomainObligationCount"] == 2
    assert payload["summary"]["sourceNegativeControlCount"] == 4
    assert payload["summary"]["sourceBlockerCount"] == 4
    assert payload["summary"]["d67SurfaceRowCount"] == 5
    assert payload["summary"]["guardBoundaryStatus"] == "guarded_domain_boundary_required"


def test_d71_preserves_d69_caveats_blockers_and_runtime_control():
    payload = build_payload(ATLAS_GATE)
    row = payload["freezeRows"][0]
    assert payload["summary"]["frozenCaveatCount"] == 9
    assert payload["summary"]["frozenBlockedPhraseCount"] == 12
    assert payload["summary"]["sourceD69RequiredCaveatCount"] == 9
    assert payload["summary"]["sourceD69BlockedGlobalPhraseCount"] == 12
    assert payload["summary"]["sourceD69RowRequiredCaveatCount"] == 6
    assert payload["summary"]["sourceD69RowBlockedPhraseCount"] == 10
    assert payload["summary"]["runtimeGuardrailStatus"] == "protected_log_and_log1p_runtime_controls_required"
    assert payload["summary"]["publicAtlasStatus"] == "held_private"
    assert payload["summary"]["runtimeLoweringControl"] == "protected_log_and_log1p_remain_runtime_controls"
    assert row["runtimeControl"] == "protected_log_and_log1p_remain_runtime_controls"
    assert "Both probability interval guards" in " ".join(row["frozenCaveats"])
    assert "logit replacement" in row["frozenBlockedPhrases"]


def test_d71_parks_future_branches_and_public_gate():
    payload = build_payload(ATLAS_GATE)
    assert parked_by_id(payload, "next_bounded_identity_branch_selector")["status"] == "parked_after_probability_logit_pause"
    assert parked_by_id(payload, "bounded_trig_identity_feasibility_selector")["status"] == "parked_after_probability_logit_pause"
    assert parked_by_id(payload, "human_approved_public_copy_gate")["status"] == "parked_requires_explicit_human_approval"
    assert payload["summary"]["parkedNextBoundedIdentityBranchSelector"] is True
    assert payload["summary"]["parkedBoundedTrigFeasibility"] is True
    assert payload["summary"]["parkedHumanApprovedPublicCopyGate"] is True
    assert payload["summary"]["newBoundedBranchSelected"] is False
    assert payload["summary"]["boundedTrigFeasibilitySelected"] is False
    assert payload["summary"]["humanApprovedPublicCopyGateSelected"] is False
    assert payload["summary"]["humanApprovalRecorded"] is False


def test_d71_starts_no_public_copy_or_implementation():
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


def test_d71_keeps_runtime_log_and_laptop_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["protectedLogReplacementClaim"] is False
    assert payload["summary"]["protectedLog1pReplacementClaim"] is False
    assert payload["summary"]["protectedExpm1ReplacementClaim"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d71_claim_flags_are_freeze_only():
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


def test_d71_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D71")


def test_d71_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d71_probability_logit_branch_pause_freeze_packet.py",
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
    assert "EML_D71_PROBABILITY_LOGIT_BRANCH_PAUSE_FREEZE_PACKET_OK" in proc.stdout
