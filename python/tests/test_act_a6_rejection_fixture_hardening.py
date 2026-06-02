"""Tests for ACT-A6 rejection fixture hardening."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.act_a6_rejection_fixture_hardening import (
    CLAIM_FLAGS,
    EXPECTED_HARDENING,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_act_a6_consumes_act_a5_and_records_hardening_rows():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "ACT_A6_REJECTION_FIXTURE_HARDENING_PASS"
    assert payload["sourceRejectionPacket"] == "act-a5-negative-rejection-fixtures"
    assert payload["summary"]["sourceNegativeFixtureCount"] == 5
    assert payload["summary"]["hardeningRowCount"] == 5


def test_act_a6_hardening_rows_cover_expected_modes_and_families():
    payload = build_payload(ATLAS_GATE)
    by_mode = {row["failureMode"]: row for row in payload["hardeningRows"]}
    assert set(by_mode) == set(EXPECTED_HARDENING)
    assert {row["boundaryFamily"] for row in payload["hardeningRows"]} == {
        "claim_strength",
        "traceability",
        "public_boundary",
        "runtime_boundary",
        "lane_ownership",
    }
    for mode, expected in EXPECTED_HARDENING.items():
        assert by_mode[mode]["boundaryFamily"] == expected["boundaryFamily"]
        assert by_mode[mode]["reviewerCue"] == expected["reviewerCue"]


def test_act_a6_required_mutation_paths_are_present():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["coverageObligationCount"] == 9
    assert payload["summary"]["missingMutationPathCount"] == 0
    for row in payload["hardeningRows"]:
        assert row["coverageStatus"] == "covered"
        assert row["expectedStatus"] == "reject"
        assert row["missingRequiredMutationPaths"] == []
        assert set(row["requiredMutationPaths"]).issubset(set(row["mutationPaths"]))


def test_act_a6_hardening_checks_pass_exactly():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["hardeningCheckCount"] == 7
    assert payload["summary"]["hardeningCheckPassCount"] == 7
    checks = {check["checkId"]: check for check in payload["hardeningChecks"]}
    assert set(checks) == {
        "act_a5_source_consumed",
        "all_rejection_modes_have_hardening_rows",
        "boundary_families_are_complete",
        "required_mutation_paths_are_present",
        "all_rows_remain_expected_reject",
        "reviewer_cues_are_unique",
        "coverage_statuses_are_covered",
    }
    for check in checks.values():
        assert check["status"] == "pass"
        assert check["observed"] == check["expected"]


def test_act_a6_records_no_production_validator_renderer_or_soundness_claim():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["rejectionFixtureHardeningRecorded"] is True
    assert payload["summary"]["actA5RejectionFixturesConsumed"] is True
    assert payload["summary"]["hardeningRowsRecorded"] is True
    assert payload["summary"]["coverageObligationsRecorded"] is True
    assert payload["summary"]["hardeningChecksRecorded"] is True
    assert payload["summary"]["hardeningChecksPassed"] is True
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


def test_act_a6_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    true_keys = {
        "rejection_fixture_hardening_recorded",
        "act_a5_rejection_fixtures_consumed",
        "hardening_rows_recorded",
        "coverage_obligations_recorded",
        "hardening_checks_recorded",
        "hardening_checks_passed",
    }
    for key in true_keys:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in true_keys:
            assert value is False


def test_act_a6_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# ACT-A6")


def test_act_a6_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/act_a6_rejection_fixture_hardening.py",
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
    assert "ACT_A6_REJECTION_FIXTURE_HARDENING_OK" in proc.stdout
