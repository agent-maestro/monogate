"""Tests for ACT-A4 dry-run validator fixture expansion."""

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

from scripts.act_a4_dry_run_validator_fixture_expansion import (
    CLAIM_FLAGS,
    OBLIGATION_IDS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_act_a4_consumes_act_a2_and_records_three_fixtures():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "ACT_A4_DRY_RUN_VALIDATOR_FIXTURE_EXPANSION_PASS"
    assert payload["sourceObligationsPacket"] == "act-a2-alpha-gamma-validator-obligations"
    assert payload["summary"]["fixtureCaseCount"] == 3
    assert {case["fixtureId"] for case in payload["fixtureCases"]} == {
        "eml_d45_positive_log_exp_branch_pause_freeze_packet",
        "eml_d53_constant_coordinate_branch_pause_freeze_packet",
        "eml_d62_expm1_boundary_branch_pause_freeze_packet",
    }


def test_act_a4_records_all_obligation_checks_for_each_fixture():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["sourceValidatorObligationCount"] == 6
    assert payload["summary"]["obligationCoveragePerFixture"] == 6
    assert payload["summary"]["fixtureCheckCount"] == 18
    assert payload["summary"]["fixtureCheckPassCount"] == 18
    assert payload["summary"]["fixtureRejectCount"] == 0
    for fixture in payload["fixtureCases"]:
        covered = {check["sourceObligation"] for check in payload["fixtureChecks"] if check["fixtureId"] == fixture["fixtureId"]}
        assert covered == set(OBLIGATION_IDS)


def test_act_a4_preserves_fixture_boundaries():
    payload = build_payload(ATLAS_GATE)
    by_fixture = {case["fixtureId"]: case for case in payload["fixtureCases"]}
    assert by_fixture["eml_d45_positive_log_exp_branch_pause_freeze_packet"]["checkedStatement"] == "0 < x -> exp (log x) = x"
    assert by_fixture["eml_d53_constant_coordinate_branch_pause_freeze_packet"]["checkedStatement"] == "eml 0 (exp (1 + 1)) = -1"
    assert by_fixture["eml_d62_expm1_boundary_branch_pause_freeze_packet"]["checkedStatement"] == "eml x (exp 1) = exp x - 1"
    for case in by_fixture.values():
        assert case["publicStatus"] == "held_private"
        assert case["claimFlags"]["public_ready"] is False
        assert case["claimFlags"]["runtime_lowering_changed"] is False
        assert case["claimFlags"]["electronics_repo_touched"] is False


def test_act_a4_records_fixture_expansion_without_production_validator_or_soundness_claim():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["dryRunFixtureExpansionRecorded"] is True
    assert payload["summary"]["actA2ObligationsConsumed"] is True
    assert payload["summary"]["fixtureCasesRecorded"] is True
    assert payload["summary"]["fixtureChecksDryRun"] is True
    assert payload["summary"]["fixtureChecksPassed"] is True
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


def test_act_a4_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    true_keys = {
        "dry_run_fixture_expansion_recorded",
        "act_a2_obligations_consumed",
        "fixture_cases_recorded",
        "fixture_checks_dry_run",
        "fixture_checks_passed",
    }
    for key in true_keys:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in true_keys:
            assert value is False


def test_act_a4_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# ACT-A4")


def test_act_a4_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/act_a4_dry_run_validator_fixture_expansion.py",
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
    assert "ACT_A4_DRY_RUN_VALIDATOR_FIXTURE_EXPANSION_OK" in proc.stdout
