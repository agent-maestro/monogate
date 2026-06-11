"""Tests for GB-VIS-A4 snapshot comparison fixture."""

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

from scripts.gb_vis_a4_snapshot_comparison_fixture import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_gb_vis_a4_consumes_gb_vis_a3_smoke_fixture():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "GB_VIS_A4_SNAPSHOT_COMPARISON_FIXTURE_PASS"
    assert payload["sourceSmokeFixture"] == "gb-vis-a3-renderer-smoke-fixture"


def test_gb_vis_a4_records_snapshot_counts():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["nodeCommandCount"] == 23
    assert payload["summary"]["edgeCommandCount"] == 16
    assert payload["summary"]["legendCommandCount"] == 5
    assert payload["summary"]["smokeCheckCount"] == 6
    assert payload["summary"]["comparisonCheckCount"] == 6
    assert payload["summary"]["comparisonPassCount"] == 6


def test_gb_vis_a4_preserves_source_boundaries():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["sourceCheckedStatement"] == "eml x (exp 1) = exp x - 1"
    assert payload["summary"]["sourceRuntimeControl"] == "protected_expm1_remains_runtime_control"
    assert payload["summary"]["sourcePublicStatus"] == "held_private"


def test_gb_vis_a4_compares_stable_snapshot_digests():
    payload = build_payload(ATLAS_GATE)
    baseline = payload["baselineSnapshot"]
    observed = payload["observedSnapshot"]
    for key in [
        "nodeDigest",
        "edgeDigest",
        "legendDigest",
        "smokeCheckDigest",
        "guardrailDigest",
        "viewportDigest",
    ]:
        assert baseline[key] == observed[key]
    assert len(baseline["nodeDigest"]) == 64


def test_gb_vis_a4_records_comparison_checks():
    payload = build_payload(ATLAS_GATE)
    checks = {item["checkId"]: item for item in payload["comparisonChecks"]}
    assert set(checks) == {
        "nodeDigest_matches",
        "edgeDigest_matches",
        "legendDigest_matches",
        "smokeCheckDigest_matches",
        "guardrailDigest_matches",
        "viewportDigest_matches",
    }
    for check in checks.values():
        assert check["status"] == "pass"
        assert check["baseline"] == check["observed"]


def test_gb_vis_a4_records_fixture_without_renderer_or_public_claim():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["snapshotComparisonFixtureRecorded"] is True
    assert payload["summary"]["gbVisA3SmokeFixtureConsumed"] is True
    assert payload["summary"]["baselineSnapshotRecorded"] is True
    assert payload["summary"]["observedSnapshotRecorded"] is True
    assert payload["summary"]["snapshotComparisonChecksRecorded"] is True
    assert payload["summary"]["snapshotComparisonChecksPassed"] is True
    assert payload["summary"]["pixelRendererImplemented"] is False
    assert payload["summary"]["rendererImplemented"] is False
    assert payload["summary"]["interactiveRendererImplemented"] is False
    assert payload["summary"]["rendererExecuted"] is False
    assert payload["summary"]["visualizationStarted"] is False
    assert payload["summary"]["visualizationRendered"] is False
    assert payload["summary"]["visualCorrectnessProved"] is False
    assert payload["summary"]["publicCopyApproved"] is False
    assert payload["summary"]["publicSurfaceUpdated"] is False
    assert payload["summary"]["runtimeLoweringChanged"] is False
    assert payload["summary"]["productionValidatorImplemented"] is False
    assert payload["summary"]["validatorSoundnessProved"] is False
    assert payload["summary"]["soundnessProved"] is False
    assert payload["summary"]["fullGaloisConnectionClaim"] is False
    assert payload["summary"]["abstractInterpretationSoundnessProved"] is False
    assert payload["summary"]["machlibFileChanged"] is False
    assert payload["summary"]["leanTypecheckPerformed"] is False
    assert payload["summary"]["proofAttemptStarted"] is False
    assert payload["summary"]["electronicsRepoTouched"] is False
    assert payload["summary"]["laptopArtifactConsumed"] is False
    assert payload["summary"]["publicReady"] is False


def test_gb_vis_a4_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    true_keys = {
        "snapshot_comparison_fixture_recorded",
        "gb_vis_a3_smoke_fixture_consumed",
        "baseline_snapshot_recorded",
        "observed_snapshot_recorded",
        "snapshot_comparison_checks_recorded",
        "snapshot_comparison_checks_passed",
    }
    for key in true_keys:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in true_keys:
            assert value is False


def test_gb_vis_a4_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# GB-VIS-A4")


def test_gb_vis_a4_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/gb_vis_a4_snapshot_comparison_fixture.py",
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
    assert "GB_VIS_A4_SNAPSHOT_COMPARISON_FIXTURE_OK" in proc.stdout
