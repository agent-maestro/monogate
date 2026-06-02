"""Tests for ACT-A3 alpha/gamma dry-run validator skeleton."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.act_a3_alpha_gamma_dry_run_validator_skeleton import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def check_by_id(payload, check_id: str):
    return next(item for item in payload["dryRunChecks"] if item["checkId"] == check_id)


def test_act_a3_consumes_act_a2_and_retains_act_a1_contract():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "ACT_A3_ALPHA_GAMMA_DRY_RUN_VALIDATOR_SKELETON_PASS"
    assert payload["sourceContract"] == "act-a1-abstract-concrete-trace-contract"
    assert payload["sourceObligationsPacket"] == "act-a2-alpha-gamma-validator-obligations"
    assert payload["summary"]["sourceValidatorObligationCount"] == 6
    assert payload["summary"]["sourceFailureModeCount"] == 5


def test_act_a3_records_one_dry_run_check_per_a2_obligation():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["dryRunCheckCount"] == 6
    assert payload["summary"]["dryRunPassCount"] == 6
    assert payload["summary"]["dryRunRejectCount"] == 0
    assert payload["summary"]["alphaDryRunCheckCount"] == 3
    assert payload["summary"]["gammaDryRunCheckCount"] == 2
    assert payload["summary"]["roundtripDryRunCheckCount"] == 1
    obligations = {check["sourceObligation"] for check in payload["dryRunChecks"]}
    assert obligations == {
        "alpha_source_identity_required",
        "alpha_claim_strength_bounded",
        "alpha_traceability_complete",
        "gamma_admissible_artifact_class",
        "gamma_boundary_preservation",
        "roundtrip_no_claim_escalation",
    }


def test_act_a3_alpha_checks_preserve_trace_and_claim_bounds():
    payload = build_payload(ATLAS_GATE)
    source_identity = check_by_id(payload, "alpha_source_identity_required_dry_run")
    claim_bounds = check_by_id(payload, "alpha_claim_strength_bounded_dry_run")
    traceability = check_by_id(payload, "alpha_traceability_complete_dry_run")
    assert source_identity["status"] == "pass"
    assert "act-a2-alpha-gamma-validator-obligations" in source_identity["evidence"]
    assert set(claim_bounds["evidence"]) == {
        "validator_obligations_recorded",
        "alpha_validator_requirements_defined",
        "gamma_validator_requirements_defined",
        "failure_modes_defined",
    }
    assert "eml x (exp 1) = exp x - 1" in traceability["evidence"]
    assert "held_private" in traceability["evidence"]


def test_act_a3_gamma_checks_preserve_classes_and_boundaries():
    payload = build_payload(ATLAS_GATE)
    artifact_classes = check_by_id(payload, "gamma_admissible_artifact_class_dry_run")
    boundaries = check_by_id(payload, "gamma_boundary_preservation_dry_run")
    assert set(artifact_classes["evidence"]) == {
        "lean_checked_witness",
        "evidence_packet",
        "runtime_trace",
        "lesson_or_hardware_artifact",
    }
    assert boundaries["evidence"].count("protected_expm1_remains_runtime_control") == 2
    assert boundaries["evidence"].count("held_private") == 2


def test_act_a3_roundtrip_check_has_no_claim_escalation():
    payload = build_payload(ATLAS_GATE)
    roundtrip = check_by_id(payload, "roundtrip_no_claim_escalation_dry_run")
    assert roundtrip["operator"] == "alpha_gamma_roundtrip"
    assert roundtrip["rejectedFailureModes"] == []
    assert "publicReady=false" in roundtrip["evidence"]
    assert "runtimeLoweringChanged=false" in roundtrip["evidence"]
    assert "soundnessProved=false" in roundtrip["evidence"]


def test_act_a3_records_skeleton_without_production_validator_or_soundness_claim():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["dryRunValidatorSkeletonRecorded"] is True
    assert payload["summary"]["actA2ObligationsConsumed"] is True
    assert payload["summary"]["alphaChecksDryRun"] is True
    assert payload["summary"]["gammaChecksDryRun"] is True
    assert payload["summary"]["roundtripChecksDryRun"] is True
    assert payload["summary"]["validatorSkeletonImplemented"] is True
    assert payload["summary"]["dryRunExecuted"] is True
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


def test_act_a3_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    true_keys = {
        "dry_run_validator_skeleton_recorded",
        "act_a2_obligations_consumed",
        "alpha_checks_dry_run",
        "gamma_checks_dry_run",
        "roundtrip_checks_dry_run",
        "validator_skeleton_implemented",
        "dry_run_executed",
    }
    for key in true_keys:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in true_keys:
            assert value is False


def test_act_a3_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# ACT-A3")


def test_act_a3_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/act_a3_alpha_gamma_dry_run_validator_skeleton.py",
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
    assert "ACT_A3_ALPHA_GAMMA_DRY_RUN_VALIDATOR_SKELETON_OK" in proc.stdout
