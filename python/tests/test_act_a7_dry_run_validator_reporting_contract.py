"""Tests for ACT-A7 dry-run validator reporting contract."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.act_a7_dry_run_validator_reporting_contract import (
    CLAIM_FLAGS,
    REPORT_SECTIONS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_act_a7_consumes_act_a6_and_records_report_rows():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "ACT_A7_DRY_RUN_VALIDATOR_REPORTING_CONTRACT_PASS"
    assert payload["sourceHardeningPacket"] == "act-a6-rejection-fixture-hardening"
    assert payload["summary"]["sourceHardeningRowCount"] == 5
    assert payload["summary"]["reportRowCount"] == 5


def test_act_a7_report_sections_are_recorded():
    payload = build_payload(ATLAS_GATE)
    assert payload["reportSections"] == REPORT_SECTIONS
    assert payload["summary"]["reportSectionCount"] == 6
    assert set(payload["reportSections"]) == {
        "source_packet",
        "accepted_fixture_context",
        "negative_rejection_coverage",
        "hardening_obligations",
        "non_claims",
        "next_action",
    }


def test_act_a7_report_rows_cover_rejection_modes():
    payload = build_payload(ATLAS_GATE)
    assert {row["failureMode"] for row in payload["reportRows"]} == {
        "claim_escalation",
        "trace_gap",
        "public_gate_bypass",
        "runtime_drift",
        "lane_owner_drift",
    }
    for row in payload["reportRows"]:
        assert row["reportDisposition"] == "include_private_reviewer_report"
        assert row["coverageStatus"] == "covered"
        assert row["expectedStatus"] == "reject"
        assert row["missingMutationPathCount"] == 0


def test_act_a7_reporting_checks_pass_exactly():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["reportingCheckCount"] == 7
    assert payload["summary"]["reportingCheckPassCount"] == 7
    checks = {check["checkId"]: check for check in payload["reportingChecks"]}
    assert set(checks) == {
        "source_hardening_packet_is_act_a6",
        "report_rows_match_hardening_rows",
        "report_sections_are_complete",
        "all_report_rows_are_private_reviewer_rows",
        "all_report_rows_are_covered",
        "no_missing_mutation_paths_reported",
        "production_validator_claims_remain_false",
    }
    for check in checks.values():
        assert check["status"] == "pass"
        assert check["observed"] == check["expected"]


def test_act_a7_records_no_production_validator_or_soundness_claim():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["dryRunValidatorReportingContractRecorded"] is True
    assert payload["summary"]["actA6HardeningConsumed"] is True
    assert payload["summary"]["reportRowsRecorded"] is True
    assert payload["summary"]["reportSectionsRecorded"] is True
    assert payload["summary"]["reportingChecksRecorded"] is True
    assert payload["summary"]["reportingChecksPassed"] is True
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
    assert payload["summary"]["rendererImplemented"] is False
    assert payload["summary"]["rendererExecuted"] is False
    assert payload["summary"]["publicReady"] is False


def test_act_a7_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    true_keys = {
        "dry_run_validator_reporting_contract_recorded",
        "act_a6_hardening_consumed",
        "report_rows_recorded",
        "report_sections_recorded",
        "reporting_checks_recorded",
        "reporting_checks_passed",
    }
    for key in true_keys:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in true_keys:
            assert value is False


def test_act_a7_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# ACT-A7")


def test_act_a7_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/act_a7_dry_run_validator_reporting_contract.py",
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
    assert "ACT_A7_DRY_RUN_VALIDATOR_REPORTING_CONTRACT_OK" in proc.stdout
