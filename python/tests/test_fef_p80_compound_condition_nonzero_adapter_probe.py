"""Tests for FEF-P80 compound-condition nonzero adapter probe."""

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

from scripts.fef_p80_compound_condition_nonzero_adapter_probe import (
    CLAIM_FLAGS,
    P79_RESULT,
    adapt_selected_nonzero_predicates,
    build_outputs,
    build_payload,
    classify_failure,
    run_adapted_probe,
    validate_payload,
)


def test_fef_p80_clears_nonzero_predicate_blocker_and_records_next_blocker():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P80_COMPOUND_CONDITION_NONZERO_ADAPTER_PROBE_PASS"
    assert payload["decision"] == "selected_nonzero_predicate_adapter_clears_first_blocker_next_surface_blocked"
    assert summary["selectedFixtureId"] == "c_and_short_circuit_guard_v0"
    assert summary["previousBlockerCleared"] is True
    assert summary["nextBlockerDetected"] is True
    assert summary["reingestExecuted"] is False


def test_fef_p80_adapter_rewrites_only_selected_nonzero_surfaces():
    payload = build_payload()
    source = payload["adapterProbe"]
    replacements = source["replacements"]
    assert [item["replacementId"] for item in replacements] == [
        "nonzero01_helper_condition",
        "guarded_div_helper_condition",
    ]
    assert all(item["applied"] is True for item in replacements)


def test_fef_p80_adapter_function_changes_source():
    payload = build_payload()
    original = payload["reingestProbe"]["failure"]["message"]
    assert "call to non-math function" in original
    adapted = adapt_selected_nonzero_predicates(
        "return value != 0.0 ? 1.0 : 0.0;\nreturn guard != 0.0 ? numerator / denominator : default_value;"
    )
    assert adapted["sourceChanged"] is True
    assert "value != 0.0" not in adapted["adaptedSource"]
    assert "guard != 0.0" not in adapted["adaptedSource"]


def test_fef_p80_adapted_probe_is_actual_invocation():
    payload = build_payload()
    from scripts.fef_p79_compound_condition_reingest_execution_probe import read_json

    p79_payload = read_json(P79_RESULT)
    adapted = adapt_selected_nonzero_predicates(p79_payload["selectedCodegenFixture"]["source"])
    probe = run_adapted_probe(adapted["adaptedSource"])
    assert probe["invocationPerformed"] is True
    assert probe["status"] == "blocked_expected_next_surface"
    assert "selected_guard_helper_call_unsupported" in probe["failure"]["detectedBlockers"]


def test_fef_p80_failure_classifier_keeps_known_names():
    helper = classify_failure("call to non-math function `mg_step01` unsupported in E2")
    assert helper["detectedBlockers"] == ["selected_guard_helper_call_unsupported"]
    nonzero = classify_failure("BinaryOp unsupported as C branch condition")
    assert nonzero["detectedBlockers"] == ["nonzero_comparison_condition_unsupported"]


def test_fef_p80_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_nonzero_predicate_adapter_probe"] == "recorded"
    assert gates["selected_reingest_execution"] == "blocked_not_executed"
    assert gates["selected_guard_helper_call_surface"] == "blocked"
    assert "Compound-condition re-ingest is supported." in payload["blockedStatements"]
    assert summary["compoundConditionReingestSupported"] is False
    assert summary["compoundConditionLoweringImplemented"] is False
    assert summary["compoundConditionSupportClaim"] is False
    assert summary["helperRuntimeInstalled"] is False
    assert summary["controlFlowIrImplemented"] is False
    assert summary["frontendLoweringChanged"] is False
    assert summary["generalBranchControlFlowClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p80_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P80")


def test_fef_p80_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p80_compound_condition_nonzero_adapter_probe.py",
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
    assert "FEF_P80_COMPOUND_CONDITION_NONZERO_ADAPTER_PROBE_OK" in proc.stdout
