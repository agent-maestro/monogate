"""Tests for FEF-P33 selected-fixture free-target matrix."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p33_free_target_fixture_matrix import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p33_matrix_covers_two_fixtures_and_all_free_targets():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P33_FREE_TARGET_FIXTURE_MATRIX_PASS"
    assert [fixture["id"] for fixture in payload["fixtureRows"]] == [
        "verified_add",
        "runtime_helper_mix",
    ]
    assert summary["fixtureCount"] == 2
    assert summary["freeTargetCount"] == 13
    assert summary["matrixCellCount"] == 26
    assert summary["emissionPassCount"] == 26
    assert summary["validationPassCount"] == 26
    assert summary["allMatrixEmissionPass"] is True
    assert summary["allMatrixValidationPass"] is True


def test_fef_p33_expected_free_target_order():
    payload = build_payload()
    assert payload["targetOrder"] == [
        "c",
        "cpp",
        "rust",
        "python",
        "go",
        "java",
        "kotlin",
        "csharp",
        "javascript",
        "wasm",
        "matlab",
        "lean",
        "zkproof",
    ]


def test_fef_p33_every_target_has_two_passing_fixture_cells():
    payload = build_payload()
    for target_row in payload["summary"]["byTarget"]:
        assert target_row["fixtureCount"] == 2
        assert target_row["emissionPassCount"] == 2
        assert target_row["validationPassCount"] == 2
    by_fixture = {}
    for row in payload["matrixRows"]:
        by_fixture.setdefault(row["fixtureId"], []).append(row)
        assert row["emissionStatus"] == "pass"
        assert row["validationStatus"] == "pass"
    assert set(by_fixture) == {"verified_add", "runtime_helper_mix"}
    assert all(len(rows) == 13 for rows in by_fixture.values())


def test_fef_p33_keeps_broad_claims_false():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["allFreeTargetsPublicReadyClaim"] is False
    assert summary["targetAllReadyClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p33_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P33")


def test_fef_p33_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p33_free_target_fixture_matrix.py",
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
    assert "FEF_P33_FREE_TARGET_FIXTURE_MATRIX_OK" in proc.stdout
