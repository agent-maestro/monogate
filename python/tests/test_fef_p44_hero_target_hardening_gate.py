"""Tests for FEF-P44 Rust/C/Python hero-target hardening gate."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p44_hero_target_hardening_gate import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p44_consolidates_hero_runtime_lane():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P44_HERO_TARGET_HARDENING_GATE_PASS"
    assert payload["decision"] == "rust_c_python_hero_lane_hardened_publication_blocked"
    assert summary["heroTargets"] == ["rust", "c", "python"]
    assert summary["fixtureCount"] == 4
    assert summary["heroRuntimeCellCount"] == 12
    assert summary["heroRuntimePassCount"] == 12
    assert summary["heroRuntimeSampleExecutions"] == 72
    assert summary["heroRuntimeMaxAbsError"] <= 1.0e-12


def test_fef_p44_rows_cover_all_hero_fixtures_by_target():
    payload = build_payload()
    by_target = {}
    for row in payload["heroFixtureRows"]:
        by_target.setdefault(row["target"], []).append(row)
        assert row["emissionStatus"] == "pass"
        assert row["validationStatus"] == "pass"
        assert row["runtimeStatus"] == "pass"
        assert row["runtimeSampleCount"] > 0
    assert set(by_target) == {"rust", "c", "python"}
    for rows in by_target.values():
        assert {row["fixtureId"] for row in rows} == {
            "verified_add",
            "runtime_helper_mix",
            "clamp_guard_mix",
            "affine_poly_mix",
        }


def test_fef_p44_keeps_roundtrip_and_public_claim_boundaries_explicit():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["pythonRoundtripEvidenceAttached"] is True
    assert summary["rustRoundtripEvidenceAttached"] is False
    assert summary["cRoundtripEvidenceAttached"] is False
    assert any(gate["id"] == "rust_roundtrip_attached" and gate["status"] == "blocked" for gate in payload["releaseGates"])
    assert any(gate["id"] == "c_roundtrip_attached" and gate["status"] == "blocked" for gate in payload["releaseGates"])
    assert summary["packagePublished"] is False
    assert summary["publicReady"] is False
    assert summary["allFreeTargetsRuntimeExecutionClaim"] is False
    assert summary["allFreeTargetsRoundtripClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p44_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P44")


def test_fef_p44_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p44_hero_target_hardening_gate.py",
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
    assert "FEF_P44_HERO_TARGET_HARDENING_GATE_OK" in proc.stdout
