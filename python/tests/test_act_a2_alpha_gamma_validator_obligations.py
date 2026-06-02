"""Tests for ACT-A2 alpha/gamma validator obligations."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.act_a2_alpha_gamma_validator_obligations import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def obligation_by_id(payload, obligation_id: str):
    return next(item for item in payload["validatorObligations"] if item["obligationId"] == obligation_id)


def failure_by_id(payload, failure_id: str):
    return next(item for item in payload["failureModes"] if item["failureModeId"] == failure_id)


def test_act_a2_consumes_act_a1_contract():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "ACT_A2_ALPHA_GAMMA_VALIDATOR_OBLIGATIONS_PASS"
    assert payload["sourceContract"] == "act-a1-abstract-concrete-trace-contract"
    assert payload["summary"]["sourceOperatorCount"] == 2
    assert payload["summary"]["sourceArtifactClassCount"] == 4
    assert payload["summary"]["sourcePreservationObligationCount"] == 5


def test_act_a2_records_validator_obligations():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["validatorObligationCount"] == 6
    assert payload["summary"]["alphaValidatorRequirementCount"] == 3
    assert payload["summary"]["gammaValidatorRequirementCount"] == 2
    assert payload["summary"]["roundtripRequirementCount"] == 1
    assert obligation_by_id(payload, "alpha_source_identity_required")["operator"] == "alpha"
    assert obligation_by_id(payload, "gamma_boundary_preservation")["operator"] == "gamma"
    assert obligation_by_id(payload, "roundtrip_no_claim_escalation")["operator"] == "alpha_gamma_roundtrip"


def test_act_a2_records_blocking_failure_modes():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["failureModeCount"] == 5
    assert failure_by_id(payload, "claim_flag_escalation")["severity"] == "block"
    assert failure_by_id(payload, "public_gate_bypass")["severity"] == "block"
    assert failure_by_id(payload, "runtime_control_drift")["severity"] == "block"
    assert "laptop-owned" in failure_by_id(payload, "lane_owner_drift")["description"]


def test_act_a2_preserves_source_example_boundaries():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["sourceCheckedStatement"] == "eml x (exp 1) = exp x - 1"
    assert payload["summary"]["sourceRuntimeControl"] == "protected_expm1_remains_runtime_control"
    assert payload["summary"]["sourcePublicStatus"] == "held_private"


def test_act_a2_records_requirements_without_implementation_or_soundness_claim():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["validatorObligationsRecorded"] is True
    assert payload["summary"]["alphaValidatorRequirementsDefined"] is True
    assert payload["summary"]["gammaValidatorRequirementsDefined"] is True
    assert payload["summary"]["failureModesDefined"] is True
    assert payload["summary"]["validatorImplemented"] is False
    assert payload["summary"]["validatorExecuted"] is False
    assert payload["summary"]["soundnessProved"] is False
    assert payload["summary"]["fullGaloisConnectionClaim"] is False
    assert payload["summary"]["abstractInterpretationSoundnessProved"] is False
    assert payload["summary"]["visualizationStarted"] is False
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["implementationStarted"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["proofAttemptStarted"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_act_a2_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    true_keys = {
        "validator_obligations_recorded",
        "alpha_validator_requirements_defined",
        "gamma_validator_requirements_defined",
        "failure_modes_defined",
    }
    for key in true_keys:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in true_keys:
            assert value is False


def test_act_a2_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# ACT-A2")


def test_act_a2_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/act_a2_alpha_gamma_validator_obligations.py",
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
    assert "ACT_A2_ALPHA_GAMMA_VALIDATOR_OBLIGATIONS_OK" in proc.stdout
