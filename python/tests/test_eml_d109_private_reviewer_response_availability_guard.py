"""Tests for EML-D109 private reviewer response availability guard."""

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

from scripts.eml_d109_private_reviewer_response_availability_guard import (
    CLAIM_FLAGS,
    ROOT,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def check_by_id(payload, check_id: str):
    return next(item for item in payload["responseAvailabilityChecks"] if item["checkId"] == check_id)


def action_by_id(payload, action_id: str):
    return next(item for item in payload["holdActions"] if item["actionId"] == action_id)


def test_d109_consumes_d108_and_preserves_boundary():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "EML_D109_PRIVATE_REVIEWER_RESPONSE_AVAILABILITY_GUARD_PASS"
    assert payload["sourceSelector"] == "eml-d108-post-static-topology-summary-next-selector"
    assert summary["d108SelectedOptionId"] == "private_reviewer_response_intake"
    assert summary["d108SelectedNextArtifact"] == "EML-D109 private reviewer response intake packet"
    assert summary["selectedWitnessName"] == "MachLib.Real.expm1_boundary_identity_witness"
    assert summary["checkedStatement"] == "eml x (exp 1) = exp x - 1"
    assert summary["guardSummary"] == "no extra real-domain guard recorded"
    assert summary["runtimeControl"] == "protected_expm1_remains_runtime_control"


def test_d109_records_missing_response_checks_and_hold_actions():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    assert summary["availabilityCheckCount"] == 3
    assert summary["missingResponseCheckCount"] == 2
    assert summary["holdActionCount"] == 3
    assert summary["reviewerResponseAvailabilityChecked"] is True
    assert summary["d108SelectorConsumed"] is True
    assert summary["noResponseHoldRecorded"] is True
    assert summary["d110BlockedUntilResponseExists"] is True
    assert check_by_id(payload, "response_text_supplied")["status"] == "missing"
    assert check_by_id(payload, "response_source_artifact_supplied")["status"] == "missing"
    assert check_by_id(payload, "response_decision_explicit")["status"] == "unavailable"
    assert action_by_id(payload, "wait_for_actual_private_reviewer_response")["status"] == "selected_hold"


def test_d109_does_not_consume_or_invent_reviewer_decision():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    for key in [
        "reviewerResponseSupplied",
        "reviewerResponseConsumed",
        "reviewerDecisionRecorded",
        "reviewerApprovalRecorded",
        "reviewerRejectionRecorded",
        "reviewerHoldRecorded",
        "humanApprovalRecorded",
        "implementationApproved",
    ]:
        assert summary[key] is False


def test_d109_blocks_renderer_public_runtime_proof_and_laptop_claims():
    payload = build_payload(ATLAS_GATE)
    summary = payload["summary"]
    for key in [
        "privateSummaryImplementationSelected",
        "claimTopologySurfaceCreated",
        "interactiveRendererImplemented",
        "rendererImplemented",
        "rendererExecuted",
        "visualizationRendered",
        "visualizationQualityClaim",
        "rendererCorrectnessClaim",
        "rendererSoundnessProved",
        "publicSurfaceUpdated",
        "publicPageCreated",
        "publicCopyApproved",
        "publicReady",
        "sdkCompilerDocsCreated",
        "courseMaterialCreated",
        "newIdentityCandidateSelected",
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "runtimeLoweringChanged",
        "runtimePerformanceClaim",
        "protectedExpm1ReplacementClaim",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
        "fullEmlSemanticsClaim",
        "catalogCompletenessClaim",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
    ]:
        assert summary[key] is False


def test_d109_claim_flags_are_hold_guard_only():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_d109_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D109")


def test_d109_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d109_private_reviewer_response_availability_guard.py",
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
    assert "EML_D109_PRIVATE_REVIEWER_RESPONSE_AVAILABILITY_GUARD_OK" in proc.stdout
