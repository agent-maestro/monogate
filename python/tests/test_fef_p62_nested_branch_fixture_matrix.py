"""Tests for FEF-P62 nested branch fixture matrix."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p62_nested_branch_fixture_matrix import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_fixture,
    validate_payload,
)


def test_fef_p62_records_nested_matrix_without_support_claim():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P62_NESTED_BRANCH_FIXTURE_MATRIX_PASS"
    assert payload["decision"] == "nested_branch_fixture_matrix_recorded_support_blocked"
    assert summary["p61ValidationPass"] is True
    assert summary["fixtureCount"] == 4
    assert summary["allFixturesBlocked"] is True
    assert summary["nestedBranchSupportClaim"] is False


def test_fef_p62_matrix_covers_c_and_rust_nested_shapes():
    payload = build_payload()
    rows = {row["id"]: row for row in payload["nestedBranchFixtures"]}
    assert set(rows) == {
        "c_nested_if_return_v0",
        "c_nested_if_else_value_v0",
        "rust_nested_if_expr_v0",
        "rust_nested_if_return_v0",
    }
    assert payload["summary"]["cFixtureCount"] == 2
    assert payload["summary"]["rustFixtureCount"] == 2
    assert payload["summary"]["maxBranchDepth"] == 2
    assert all(row["branchDepth"] == 2 for row in rows.values())


def test_fef_p62_fixture_fragments_are_schema_shaped_and_blocked():
    payload = build_payload()
    for row in payload["nestedBranchFixtures"]:
        validate_fixture(row)
        fragment = row["schemaFragment"]
        assert fragment["feature"] == row["shape"]
        assert fragment["blocks"][0]["statements"][0]["constructId"] == "nested_statement_branches"
        assert fragment["blocks"][0]["terminator"]["kind"] == "unreachable"
        assert row["status"] == "blocked_fixture_defined"
        assert row["supportClaimAllowed"] is False
        assert all(value is False for value in fragment["claimFlags"].values())


def test_fef_p62_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["nested_branch_fixture_matrix"] == "recorded"
    assert gates["nested_branch_support"] == "blocked"
    assert "Nested branch lowering is implemented." in payload["blockedStatements"]
    assert summary["controlFlowIrImplemented"] is False
    assert summary["frontendLoweringChanged"] is False
    assert summary["unsupportedConstructsSupported"] is False
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["branchControlFlowReingestClaim"] is False
    assert summary["fullNonGeneratedSourceRoundtripClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p62_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P62")


def test_fef_p62_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p62_nested_branch_fixture_matrix.py",
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
    assert "FEF_P62_NESTED_BRANCH_FIXTURE_MATRIX_OK" in proc.stdout
