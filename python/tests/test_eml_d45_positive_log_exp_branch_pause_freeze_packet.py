"""Tests for EML-D45 positive log-exp branch pause freeze packet."""

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

from scripts.eml_d45_positive_log_exp_branch_pause_freeze_packet import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def parked_by_id(payload, option_id: str):
    return next(item for item in payload["parkedOptions"] if item["optionId"] == option_id)


def test_d45_consumes_d44_selected_pause_freeze_option():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "EML_D45_POSITIVE_LOG_EXP_BRANCH_PAUSE_FREEZE_PACKET_PASS"
    assert payload["sourceSelector"] == "eml-d44-positive-log-exp-review-next-selector"
    assert payload["summary"]["selectedOptionId"] == "positive_log_exp_branch_pause_freeze_packet"


def test_d45_freezes_positive_log_exp_checked_delta():
    payload = build_payload(ATLAS_GATE)
    row = payload["freezeRows"][0]
    assert payload["summary"]["branchPauseStarted"] is True
    assert payload["summary"]["checkedWitnessDeltaFrozen"] is True
    assert payload["summary"]["privateFreezePacket"] is True
    assert row["freezeStatus"] == "private_checked_witness_delta_frozen"
    assert row["machlibName"] == "MachLib.Real.positive_log_exp_roundtrip_witness"
    assert row["checkedStatement"] == "0 < x -> exp (log x) = x"
    assert row["guards"] == ["0 < x"]


def test_d45_preserves_d43_caveats_blockers_and_runtime_control():
    payload = build_payload(ATLAS_GATE)
    row = payload["freezeRows"][0]
    assert payload["summary"]["guardCount"] == 1
    assert payload["summary"]["frozenCaveatCount"] == 5
    assert payload["summary"]["frozenBlockedPhraseCount"] == 8
    assert payload["summary"]["positiveDomainGuardRequired"] is True
    assert payload["summary"]["publicHoldPreserved"] is True
    assert payload["summary"]["runtimeBoundaryPreserved"] is True
    assert payload["summary"]["runtimeLoweringControl"] == "standard_log_exp_remains_runtime_control"
    assert row["runtimeControl"] == "standard_log_exp_remains_runtime_control"
    assert "Always name the 0 < x guard." in row["frozenCaveats"]
    assert "log/exp replacement" in row["frozenBlockedPhrases"]


def test_d45_parks_future_branches_and_public_gate():
    payload = build_payload(ATLAS_GATE)
    assert parked_by_id(payload, "constant_coordinate_refresh_selector")["status"] == "parked_after_positive_log_exp_pause"
    assert parked_by_id(payload, "bounded_trig_identity_feasibility_selector")["status"] == "parked_after_positive_log_exp_pause"
    assert parked_by_id(payload, "human_approved_public_copy_gate")["status"] == "parked_requires_explicit_human_approval"
    assert payload["summary"]["parkedConstantCoordinateRefresh"] is True
    assert payload["summary"]["parkedBoundedTrigFeasibility"] is True
    assert payload["summary"]["parkedHumanApprovedPublicCopyGate"] is True
    assert payload["summary"]["newBoundedBranchSelected"] is False
    assert payload["summary"]["humanApprovedPublicCopyGateSelected"] is False
    assert payload["summary"]["humanApprovalRecorded"] is False


def test_d45_starts_no_public_copy_or_implementation():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["publicPromotionPerformed"] is False
    assert payload["summary"]["publicEducationPromotionPerformed"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["advantageLabCaseAdded"] is False
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["candidateProvedThisPhase"] is False
    assert payload["summary"]["proofAttemptStarted"] is False
    assert payload["freezeRows"][0]["publicPromotionAllowed"] is False


def test_d45_keeps_runtime_log_exp_and_laptop_claims_blocked():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["logExpReplacementClaim"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_d45_claim_flags_are_freeze_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsFrozenOnly"] is True
    for key in ["branch_pause_started", "checked_witness_delta_frozen", "private_freeze_packet"]:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in {"branch_pause_started", "checked_witness_delta_frozen", "private_freeze_packet"}:
            assert value is False
    for row in payload["freezeRows"]:
        for key, value in row["claimFlags"].items():
            if key not in {"branch_pause_started", "checked_witness_delta_frozen", "private_freeze_packet"}:
                assert value is False


def test_d45_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D45")


def test_d45_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d45_positive_log_exp_branch_pause_freeze_packet.py",
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
    assert "EML_D45_POSITIVE_LOG_EXP_BRANCH_PAUSE_FREEZE_PACKET_OK" in proc.stdout
