"""Tests for FEF-P121 source-preserving roundtrip fixture gate."""

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

from scripts.fef_p121_source_preserving_roundtrip_fixture_gate import (
    CLAIM_FLAGS,
    FIXTURES,
    build_outputs,
    build_payload,
    fixture_fragment,
    matrix_rows,
    validate_payload,
)


def test_fef_p121_records_source_preserving_fixture_gate():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P121_SOURCE_PRESERVING_ROUNDTRIP_FIXTURE_GATE_PASS"
    assert payload["decision"] == "source_preserving_roundtrip_fixture_gate_recorded_support_blocked_review_hold_preserved"
    assert summary["fixtureCount"] == 4
    assert summary["cFixtureCount"] == 2
    assert summary["rustFixtureCount"] == 2
    assert summary["allFixturesBlocked"] is True


def test_fef_p121_fixture_matrix_focuses_source_fidelity_surfaces():
    rows = matrix_rows()
    assert [row["id"] for row in rows] == [fixture["id"] for fixture in FIXTURES]
    assert all(row["constructId"] == "source_preserving_roundtrip" for row in rows)
    assert all(row["formatSensitive"] is True for row in rows)
    assert sum(row["commentCount"] for row in rows) == 2
    assert sum(row["branchConstructCount"] for row in rows) == 5


def test_fef_p121_schema_fragments_are_fail_closed():
    for fixture in FIXTURES:
        fragment = fixture_fragment(fixture)
        statement = fragment["blocks"][0]["statements"][0]
        assert statement["kind"] == "unsupported_construct"
        assert statement["constructId"] == "source_preserving_roundtrip"
        assert statement["blockedBy"] == "non_generated_branch_roundtrip_gate"
        assert fragment["blocks"][0]["terminator"]["kind"] == "unreachable"


def test_fef_p121_preserves_p120_reviewer_hold():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["p120ValidationPass"] is True
    assert summary["p120ReviewerDecisionRecorded"] is False
    assert summary["p120ImplementationHeldPendingReview"] is True


def test_fef_p121_blocks_parse_reemission_fidelity_and_support():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["allSourceParseNotPerformed"] is True
    assert summary["allSourceReemissionNotPerformed"] is True
    assert summary["allRuntimeExecutionNotPerformed"] is True
    assert summary["sourcePreservingRoundtripSupportClaim"] is False
    assert summary["sourceParseExecutionClaim"] is False
    assert summary["sourceReemissionClaim"] is False
    assert summary["sourceFidelityClaim"] is False
    assert summary["fullNonGeneratedSourceRoundtripClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p121_release_gates_remain_blocked():
    payload = build_payload()
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["source_preserving_roundtrip_fixture_gate"] == "recorded"
    assert gates["source_preserving_roundtrip_support"] == "blocked"
    assert gates["source_parse_execution"] == "not_performed"
    assert gates["source_reemission"] == "not_performed"
    assert gates["source_fidelity_claim"] == "blocked"
    assert "Non-generated source was re-emitted." in payload["blockedStatements"]


def test_fef_p121_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P121")


def test_fef_p121_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p121_source_preserving_roundtrip_fixture_gate.py",
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
    assert "FEF_P121_SOURCE_PRESERVING_ROUNDTRIP_FIXTURE_GATE_OK" in proc.stdout
