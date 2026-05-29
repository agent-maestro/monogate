"""Tests for PCC-M3 proof-carrying artifact contract validator."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys

from scripts.proof_carrying_artifact_contract_validator import (
    DEFAULT_CONTRACT,
    DEFAULT_CONTRACTS_DIR,
    build_batch_validator,
    build_validator,
    is_external_workspace_ref,
    read_json,
    validate_contract,
)

RESCUE_CONTRACT = Path("reports/proof_carrying_artifacts/forge_rescue_contract_2026_05_29.json")
EML_ADVANTAGE_CONTRACT = Path("reports/proof_carrying_artifacts/eml_advantage_lab_contract_2026_05_29.json")


def build_tmp(tmp_path):
    return build_validator(
        DEFAULT_CONTRACT,
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )


def test_a13_contract_validates(tmp_path):
    built = build_tmp(tmp_path)
    payload = built["payload"]
    assert payload["status"] == "PCC_M3_CONTRACT_VALIDATOR_PASS"
    assert payload["summary"]["valid"] is True
    assert payload["summary"]["obligationCount"] == 8
    assert payload["summary"]["dischargedObligations"] == 3
    assert payload["summary"]["partialObligations"] == 2
    assert payload["summary"]["blockedObligations"] == 1
    assert payload["summary"]["unresolvedObligations"] == 2


def test_validator_rejects_true_claim_flag():
    contract = read_json(DEFAULT_CONTRACT)
    contract["claimFlags"]["compiler_correctness_claim"] = True
    payload = validate_contract(contract)
    assert payload["summary"]["valid"] is False
    assert any("compiler_correctness_claim" in failure for failure in payload["failures"])


def test_validator_requires_non_claim_for_risky_flag():
    contract = read_json(DEFAULT_CONTRACT)
    contract["nonClaims"] = ["No overclaim."]
    payload = validate_contract(contract)
    assert payload["summary"]["valid"] is False
    assert any("compiler_correctness_claim needs" in failure for failure in payload["failures"])


def test_validator_rejects_duplicate_obligation_id():
    contract = read_json(DEFAULT_CONTRACT)
    contract["obligations"][1]["obligationId"] = contract["obligations"][0]["obligationId"]
    payload = validate_contract(contract)
    assert payload["summary"]["valid"] is False
    assert any("duplicate obligationId" in failure for failure in payload["failures"])


def test_validator_rejects_missing_discharge_for_partial():
    contract = read_json(DEFAULT_CONTRACT)
    contract["obligations"][2]["dischargeArtifact"] = ""
    payload = validate_contract(contract)
    assert payload["summary"]["valid"] is False
    assert any("partial obligation must name" in failure for failure in payload["failures"])


def test_validator_can_skip_path_checks_for_synthetic_contract():
    contract = read_json(DEFAULT_CONTRACT)
    synthetic = copy.deepcopy(contract)
    synthetic["payloadReference"] = "missing/path.md"
    payload = validate_contract(synthetic, check_paths=False)
    assert payload["summary"]["valid"] is True


def test_external_workspace_refs_are_warnings_not_failures():
    contract = read_json(DEFAULT_CONTRACT)
    contract["payloadReference"] = "../missing-sibling/reports/example.json"
    payload = validate_contract(contract)
    assert is_external_workspace_ref(contract["payloadReference"]) is True
    assert payload["summary"]["valid"] is True
    assert payload["summary"]["warningCount"] == 1


def test_generated_json_files_parse(tmp_path):
    built = build_tmp(tmp_path)
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))


def test_cli_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/proof_carrying_artifact_contract_validator.py",
            "--contract",
            str(DEFAULT_CONTRACT),
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
    assert "PCC_M3_CONTRACT_VALIDATOR_OK" in proc.stdout


def test_forge_rescue_contract_validates(tmp_path):
    built = build_validator(
        RESCUE_CONTRACT,
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        result_stem="pcc_m4_forge_rescue_contract_validator_2026_05_29",
        feed_stem="pcc_m4_forge_rescue_contract_validator_feed_2026_05_29",
        evidence_id="pcc-m4-forge-rescue-contract-validator",
        title="PCC-M4 Forge Rescue Contract Validator",
        next_step="PCC-M5: validate all proof-carrying artifact contracts as a batch.",
    )
    payload = built["payload"]
    assert payload["summary"]["valid"] is True
    assert payload["summary"]["obligationCount"] == 9
    assert payload["summary"]["dischargedObligations"] == 4
    assert payload["summary"]["partialObligations"] == 3
    assert payload["summary"]["blockedObligations"] == 2


def test_eml_advantage_lab_contract_validates(tmp_path):
    built = build_validator(
        EML_ADVANTAGE_CONTRACT,
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        result_stem="eml_advantage_lab_contract_validator_2026_05_29",
        feed_stem="eml_advantage_lab_contract_validator_feed_2026_05_29",
        evidence_id="eml-advantage-lab-contract-validator",
        title="EML Advantage Lab Contract Validator",
        next_step="EML-ADV-PCC4: add noisy-data perturbation around the real-source holdout or ingest a second eFrog source.",
    )
    payload = built["payload"]
    assert payload["summary"]["valid"] is True
    assert payload["summary"]["obligationCount"] == 12
    assert payload["summary"]["dischargedObligations"] == 5
    assert payload["summary"]["partialObligations"] == 4
    assert payload["summary"]["blockedObligations"] == 3


def test_batch_validator_validates_all_contracts(tmp_path):
    built = build_batch_validator(
        DEFAULT_CONTRACTS_DIR,
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    payload = built["payload"]
    assert payload["status"] == "PCC_M5_CONTRACT_BATCH_VALIDATOR_PASS"
    assert payload["summary"]["valid"] is True
    assert payload["summary"]["contractCount"] >= 3
    assert payload["summary"]["failedContractCount"] == 0
    assert payload["summary"]["obligationCount"] >= 29


def test_batch_cli_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/proof_carrying_artifact_contract_validator.py",
            "--contracts-dir",
            str(DEFAULT_CONTRACTS_DIR),
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
    assert "PCC_M5_CONTRACT_BATCH_VALIDATOR_OK" in proc.stdout
