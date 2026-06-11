"""Tests for GB-VIS-A8 private adapter snapshot comparison."""

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

from scripts.gb_vis_a8_private_adapter_snapshot_comparison import (
    CLAIM_FLAGS,
    ROOT,
    build_outputs,
    build_payload,
    validate_payload,
)

ATLAS_GATE = ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json"


def test_gb_vis_a8_consumes_gb_vis_a7_and_records_snapshots():
    payload = build_payload(ATLAS_GATE)
    validate_payload(payload)
    assert payload["status"] == "GB_VIS_A8_PRIVATE_ADAPTER_SNAPSHOT_COMPARISON_PASS"
    assert payload["sourceAdapterSmokeFixture"] == "gb-vis-a7-private-adapter-smoke-fixture"
    assert payload["summary"]["adapterSmokeRowCount"] == 6


def test_gb_vis_a8_snapshot_counts_preserve_adapter_smoke_fixture():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["structureSmokeRowCount"] == 1
    assert payload["summary"]["guardOverlaySmokeRowCount"] == 5
    assert payload["summary"]["adapterSmokeCheckCount"] == 7
    assert payload["summary"]["adapterSmokeCheckPassCount"] == 7
    for snapshot in [payload["baselineSnapshot"], payload["observedSnapshot"]]:
        assert snapshot["adapterSmokeRowCount"] == 6
        assert snapshot["structureSmokeRowCount"] == 1
        assert snapshot["guardOverlaySmokeRowCount"] == 5
        assert snapshot["adapterSmokeCheckCount"] == 7
        assert snapshot["adapterSmokeCheckPassCount"] == 7


def test_gb_vis_a8_snapshot_digests_are_stable():
    payload = build_payload(ATLAS_GATE)
    baseline = payload["baselineSnapshot"]
    observed = payload["observedSnapshot"]
    for key in ["rowDigest", "checkDigest", "nonClaimDigest", "claimFlagDigest"]:
        assert baseline[key] == observed[key]
        assert len(baseline[key]) == 64


def test_gb_vis_a8_snapshot_comparison_checks_pass_exactly():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["snapshotComparisonCheckCount"] == 4
    assert payload["summary"]["snapshotComparisonPassCount"] == 4
    checks = {check["checkId"]: check for check in payload["snapshotComparisonChecks"]}
    assert set(checks) == {
        "rowDigest_matches",
        "checkDigest_matches",
        "nonClaimDigest_matches",
        "claimFlagDigest_matches",
    }
    for check in checks.values():
        assert check["status"] == "pass"
        assert check["baseline"] == check["observed"]


def test_gb_vis_a8_records_no_renderer_public_or_soundness_claim():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["privateAdapterSnapshotComparisonRecorded"] is True
    assert payload["summary"]["gbVisA7AdapterSmokeConsumed"] is True
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


def test_gb_vis_a8_claim_flags_are_bounded():
    payload = build_payload(ATLAS_GATE)
    assert payload["summary"]["claimFlagsBounded"] is True
    true_keys = {
        "private_adapter_snapshot_comparison_recorded",
        "gb_vis_a7_adapter_smoke_consumed",
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


def test_gb_vis_a8_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        ATLAS_GATE,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# GB-VIS-A8")


def test_gb_vis_a8_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/gb_vis_a8_private_adapter_snapshot_comparison.py",
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
    assert "GB_VIS_A8_PRIVATE_ADAPTER_SNAPSHOT_COMPARISON_OK" in proc.stdout
