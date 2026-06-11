"""Tests for FEF-P61 unsupported-construct blocker gate."""

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

from scripts.fef_p61_unsupported_construct_blocker_gate import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
    validate_probe,
)


def test_fef_p61_records_fail_closed_blocker_gate():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P61_UNSUPPORTED_CONSTRUCT_BLOCKER_GATE_PASS"
    assert payload["decision"] == "unsupported_construct_blocker_gate_recorded_support_blocked"
    assert summary["p60ValidationPass"] is True
    assert summary["p60ClaimFlagsAllFalse"] is True
    assert summary["unsupportedConstructProbeCount"] == 6
    assert summary["allUnsupportedProbesBlocked"] is True
    assert summary["unsupportedConstructsSupported"] is False


def test_fef_p61_covers_all_p59_p60_unsupported_forms():
    payload = build_payload()
    summary = payload["summary"]
    construct_ids = {probe["constructId"] for probe in payload["unsupportedConstructProbes"]}
    assert construct_ids == {
        "nested_statement_branches",
        "boolean_compound_conditions",
        "mutable_assignments_across_branches",
        "loops_and_back_edges",
        "side_effecting_calls_or_memory",
        "source_preserving_roundtrip",
    }
    assert summary["allP59UnsupportedFormsCovered"] is True
    assert summary["allP60SchemaUnsupportedFormsCovered"] is True


def test_fef_p61_probe_fragments_are_schema_shaped_and_blocked():
    payload = build_payload()
    for probe in payload["unsupportedConstructProbes"]:
        validate_probe(probe)
        fragment = probe["schemaFragment"]
        assert fragment["feature"] == probe["constructId"]
        assert fragment["unsupportedConstructs"][0]["id"] == probe["constructId"]
        assert fragment["blocks"][0]["statements"][0]["kind"] == "unsupported_construct"
        assert fragment["blocks"][0]["terminator"]["kind"] == "unreachable"
        assert probe["status"] == "blocked_fail_closed"
        assert probe["supportClaimAllowed"] is False
        assert all(value is False for value in fragment["claimFlags"].values())


def test_fef_p61_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["unsupported_construct_blocker_gate"] == "recorded"
    assert gates["unsupported_construct_support"] == "blocked"
    assert gates["control_flow_ir_implementation"] == "blocked"
    assert "Unsupported constructs are implemented." in payload["blockedStatements"]
    assert summary["controlFlowIrImplemented"] is False
    assert summary["frontendLoweringChanged"] is False
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["branchControlFlowReingestClaim"] is False
    assert summary["fullNonGeneratedSourceRoundtripClaim"] is False
    assert summary["arbitrarySourceFamilyClaim"] is False
    assert summary["publicReady"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p61_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P61")


def test_fef_p61_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p61_unsupported_construct_blocker_gate.py",
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
    assert "FEF_P61_UNSUPPORTED_CONSTRUCT_BLOCKER_GATE_OK" in proc.stdout
