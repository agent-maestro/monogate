"""Tests for ACT-A1 abstract/concrete trace contract."""

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

from scripts.act_a1_abstract_concrete_trace_contract import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def operator_by_id(payload, operator_id: str):
    return next(item for item in payload["operators"] if item["operator"] == operator_id)


def obligation_by_id(payload, obligation_id: str):
    return next(item for item in payload["preservationObligations"] if item["obligationId"] == obligation_id)


def test_act_a1_consumes_d62_freeze_packet():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "ACT_A1_ABSTRACT_CONCRETE_TRACE_CONTRACT_PASS"
    assert payload["sourceFreezePacket"] == "eml-d62-expm1-boundary-branch-pause-freeze-packet"
    assert payload["summary"]["sourceCheckedStatement"] == "eml x (exp 1) = exp x - 1"


def test_act_a1_defines_alpha_and_gamma_roles():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["operatorCount"] == 2
    alpha = operator_by_id(payload, "alpha")
    gamma = operator_by_id(payload, "gamma")
    assert alpha["role"] == "abstraction"
    assert gamma["role"] == "concretion"
    assert "ConcreteArtifact" in alpha["spelling"]
    assert "AdmissibleConcreteArtifacts" in gamma["spelling"]


def test_act_a1_records_artifact_classes_and_obligations():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["artifactClassCount"] == 4
    assert payload["summary"]["preservationObligationCount"] == 5
    classes = {item["classId"] for item in payload["artifactClasses"]}
    assert "lean_checked_witness" in classes
    assert "evidence_packet" in classes
    assert obligation_by_id(payload, "soundness_of_claim_strength")["rule"].startswith("alpha(c)")
    assert "public_ready true" in obligation_by_id(payload, "public_copy_gate")["blockedIf"]


def test_act_a1_binds_d62_as_worked_private_example():
    payload = build_payload(ATLAS_GATE)
    example = payload["workedExamples"][0]
    assert payload["summary"]["workedExampleCount"] == 1
    assert example["sourceFreezePacket"] == "eml-d62-expm1-boundary-branch-pause-freeze-packet"
    assert example["alphaResult"]["abstractClaimObjectId"] == "expm1_boundary_checked_witness_private_claim"
    assert example["alphaResult"]["runtimeControl"] == "protected_expm1_remains_runtime_control"
    assert example["alphaResult"]["publicStatus"] == "held_private"
    assert "MachLib.Real.expm1_boundary_identity_witness" in example["concreteArtifacts"]


def test_act_a1_keeps_soundness_and_public_claims_unproved():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["contractSeedRecorded"] is True
    assert payload["summary"]["alphaOperatorDefined"] is True
    assert payload["summary"]["gammaOperatorDefined"] is True
    assert payload["summary"]["d62ExampleBound"] is True
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


def test_act_a1_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    for key in ["contract_seed_recorded", "alpha_operator_defined", "gamma_operator_defined", "d62_example_bound"]:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in {"contract_seed_recorded", "alpha_operator_defined", "gamma_operator_defined", "d62_example_bound"}:
            assert value is False


def test_act_a1_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# ACT-A1")


def test_act_a1_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/act_a1_abstract_concrete_trace_contract.py",
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
    assert "ACT_A1_ABSTRACT_CONCRETE_TRACE_CONTRACT_OK" in proc.stdout
