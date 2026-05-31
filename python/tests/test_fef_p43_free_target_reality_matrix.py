"""Tests for FEF-P43 free-target reality matrix."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p43_free_target_reality_matrix import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p43_records_target_level_reality_matrix():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P43_FREE_TARGET_REALITY_MATRIX_PASS"
    assert payload["decision"] == "free_target_reality_matrix_recorded_publication_blocked"
    assert summary["freeTargetCount"] == 13
    assert summary["fixtureCount"] == 4
    assert summary["matrixCellCount"] == 52
    assert summary["emissionPassTargetCount"] == 13
    assert summary["validationPassTargetCount"] == 13


def test_fef_p43_marks_selected_runtime_and_roundtrip_targets():
    payload = build_payload()
    rows = {row["target"]: row for row in payload["targetRows"]}
    for target in ["c", "cpp", "rust", "python", "java", "javascript"]:
        assert rows[target]["runtimeCheckStatus"] == "pass_selected_fixture_runtime"
        assert rows[target]["runtimePassCount"] == 4
        assert rows[target]["runtimeSampleExecutions"] > 0
    for target in ["go", "kotlin", "csharp", "wasm", "matlab", "lean", "zkproof"]:
        assert rows[target]["runtimeCheckStatus"] != "pass_selected_fixture_runtime"
        assert rows[target]["runtimePassCount"] == 0
        assert rows[target]["runtimeSampleExecutions"] == 0
    assert rows["python"]["roundtripStatus"] == "pass_selected_roundtrip_evidence"
    assert rows["javascript"]["roundtripStatus"] == "pass_selected_roundtrip_evidence"
    assert rows["rust"]["roundtripStatus"] == "not_attempted"


def test_fef_p43_names_hero_lane_without_public_claims():
    payload = build_payload()
    rows = {row["target"]: row for row in payload["targetRows"]}
    assert payload["summary"]["heroTargets"] == ["rust", "c", "python"]
    assert rows["rust"]["priorityClass"] == "hero_runtime_lane"
    assert rows["c"]["priorityClass"] == "hero_runtime_lane"
    assert rows["python"]["priorityClass"] == "hero_runtime_lane"
    assert payload["summary"]["packagePublished"] is False
    assert payload["summary"]["publicReady"] is False
    assert payload["summary"]["allFreeTargetsRuntimeExecutionClaim"] is False
    assert payload["summary"]["allFreeTargetsRoundtripClaim"] is False
    assert payload["summary"]["compilerCorrectnessClaim"] is False
    assert payload["summary"]["formalEquivalenceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p43_rows_include_target_specific_claim_boundaries():
    payload = build_payload()
    for row in payload["targetRows"]:
        assert row["allowedClaim"].startswith(f"{row['target']}: selected emission and validation pass")
        assert "public readiness" in row["blockedClaims"]
        assert "general compiler correctness" in row["blockedClaims"]
        assert row["runtimeToolchain"]["target"] == row["target"]
        assert isinstance(row["runtimeToolchain"]["detectedCommands"], list)


def test_fef_p43_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P43")


def test_fef_p43_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p43_free_target_reality_matrix.py",
            "--build",
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
    assert "FEF_P43_FREE_TARGET_REALITY_MATRIX_OK" in proc.stdout
