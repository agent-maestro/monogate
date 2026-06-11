"""Tests for FEF-P50 non-generated source-derived re-ingest gate."""

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

from scripts.fef_p50_non_generated_source_reingest_gate import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p50_records_selected_source_derived_reingest():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P50_NON_GENERATED_SOURCE_REINGEST_GATE_PASS"
    assert payload["decision"] == (
        "selected_non_generated_source_derived_reingest_passed_full_roundtrip_blocked"
    )
    assert summary["selectedNonGeneratedSourceDerivedReingest"] is True
    assert summary["p49SemanticEvidenceAttached"] is True
    assert summary["sourceCaseCount"] == 5
    assert summary["packetCount"] == 10
    assert summary["passCount"] == 10


def test_fef_p50_covers_expected_sources_targets_and_samples():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["sourceLanguages"] == ["c", "rust"]
    assert summary["generatedTargetLanguages"] == ["c", "rust"]
    assert summary["recompiledTargetLanguages"] == ["python"]
    assert summary["sourceSampleCount"] == 23
    assert summary["packetSampleCount"] == 46
    assert summary["maxAbsError"] <= 1e-9 or summary["maxRelError"] <= 1e-9


def test_fef_p50_packets_compare_generated_runtime_to_reingested_python():
    payload = build_payload()
    for packet in payload["reingestPackets"]:
        assert packet["sourceLanguage"] in {"c", "rust"}
        assert packet["generatedTargetLanguage"] in {"c", "rust"}
        assert packet["recompiledTargetLanguage"] == "python"
        assert packet["sourceFunctionCount"] == 1
        assert packet["reingestedFunctionCount"] == 1
        assert packet["reingestStatus"] == "pass"
        assert packet["maxAbsError"] <= 1e-9 or packet["maxRelError"] <= 1e-9
        assert set(packet["frames"][0]["values"]) == {
            "sourceDerivedGeneratedTargetRuntime",
            "reingestedRecompiledPython",
        }


def test_fef_p50_claim_boundaries_and_gates_remain_blocked():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_non_generated_source_derived_reingest"] == "pass"
    assert gates["full_non_generated_source_roundtrip_claim"] == "blocked"
    assert gates["full_c_rust_roundtrip_claim"] == "blocked"
    assert gates["arbitrary_source_family_claim"] == "blocked"
    assert gates["private_reviewer_decision"] == "not_recorded"
    assert summary["fullNonGeneratedSourceRoundtripClaim"] is False
    assert summary["fullCRustRoundtripClaim"] is False
    assert summary["arbitrarySourceFamilyClaim"] is False
    assert summary["reviewerDecisionRecorded"] is False
    assert summary["packagePublished"] is False
    assert summary["checkoutEnabled"] is False
    assert summary["publicReady"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert summary["allFreeTargetsRuntimeExecutionClaim"] is False
    assert summary["allFreeTargetsRoundtripClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p50_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    packets = sorted((tmp_path / "packets").glob("*.json"))
    assert len(packets) == 10
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P50")


def test_fef_p50_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p50_non_generated_source_reingest_gate.py",
            "--build",
            "--out-dir",
            str(tmp_path / "results"),
            "--packet-dir",
            str(tmp_path / "packets"),
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
    assert "FEF_P50_NON_GENERATED_SOURCE_REINGEST_GATE_OK" in proc.stdout
