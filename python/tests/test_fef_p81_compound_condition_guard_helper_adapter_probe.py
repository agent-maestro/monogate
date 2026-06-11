"""Tests for FEF-P81 compound-condition guard-helper adapter probe."""

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

from scripts.fef_p81_compound_condition_guard_helper_adapter_probe import (
    CLAIM_FLAGS,
    P80_RESULT,
    adapt_selected_guard_helper_calls,
    build_outputs,
    build_payload,
    classify_failure,
    run_adapted_probe,
    validate_payload,
)


def test_fef_p81_clears_guard_helper_blocker_and_records_next_blocker():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P81_COMPOUND_CONDITION_GUARD_HELPER_ADAPTER_PROBE_PASS"
    assert payload["decision"] == "selected_guard_helper_adapter_clears_second_blocker_next_surface_blocked"
    assert summary["selectedFixtureId"] == "c_and_short_circuit_guard_v0"
    assert summary["previousBlockerCleared"] is True
    assert summary["nonzeroComparisonBlockerStillCleared"] is True
    assert summary["nextBlockerDetected"] is True
    assert summary["reingestExecuted"] is False


def test_fef_p81_adapter_rewrites_selected_guard_helper_surfaces():
    payload = build_payload()
    replacements = payload["adapterProbe"]["replacements"]
    assert [item["replacementId"] for item in replacements] == [
        "mg_step01_call_to_step01",
        "mg_nonzero01_call_to_branch_free_step01",
        "mg_guarded_div_call_to_selected_affine_guard",
        "step01_lhs_nonzero_guard_to_positive_guard",
    ]
    assert all(item["applied"] is True for item in replacements)


def test_fef_p81_adapter_composes_p80_nonzero_adapter():
    payload = build_payload()
    adapter = payload["adapterProbe"]
    assert adapter["composesPriorAdapter"] == "selected_nonzero_predicate_branch_free_adapter_v0"
    assert adapter["priorReplacementAppliedCount"] == 2
    assert adapter["sourceChanged"] is True


def test_fef_p81_adapter_function_changes_helper_calls_and_main_guard():
    adapted = adapt_selected_guard_helper_calls(
        "\n".join(
            [
                "static double mg_step01(double value) { return value > 0.0 ? 1.0 : 0.0; }",
                "static double mg_nonzero01(double value) { return value != 0.0 ? 1.0 : 0.0; }",
                "static double mg_guarded_div(double numerator, double denominator, double default_value, double guard) {",
                "  return guard != 0.0 ? numerator / denominator : default_value;",
                "}",
                "double f(double x, double y) {",
                "  double lhs = mg_step01(x);",
                "  double rhs = 0.0;",
                "  double selected = 0.0;",
                "  if (lhs != 0.0) {",
                "    rhs = mg_nonzero01(y);",
                "    selected = mg_guarded_div(x, y, 0.0, rhs);",
                "  }",
                "  return lhs * rhs * selected;",
                "}",
            ]
        )
    )
    source = adapted["adaptedSource"]
    assert "double lhs = step01(x);" in source
    assert "rhs = step01(y * y);" in source
    assert "selected = 0.0 + (x / y - (0.0)) * step01(rhs * rhs);" in source
    assert "if (lhs > 0.0) {" in source


def test_fef_p81_adapted_probe_is_actual_invocation():
    payload = build_payload()
    from scripts.fef_p80_compound_condition_nonzero_adapter_probe import read_json

    p80_payload = read_json(P80_RESULT)
    p79_payload = read_json(Path("python/results/fef_p79_compound_condition_reingest_execution_probe/fef_p79_compound_condition_reingest_execution_probe_2026_05_31.json"))
    assert p80_payload["summary"]["selectedFixtureId"] == "c_and_short_circuit_guard_v0"
    adapted = adapt_selected_guard_helper_calls(p79_payload["selectedCodegenFixture"]["source"])
    probe = run_adapted_probe(adapted["adaptedSource"])
    assert probe["invocationPerformed"] is True
    assert probe["status"] == "blocked_expected_next_surface"
    assert probe["failure"]["detectedBlockers"] == ["statement_level_if_assignment_shape_unsupported"]


def test_fef_p81_failure_classifier_keeps_known_names():
    if_shape = classify_failure("C if statement form not supported in E2")
    assert if_shape["detectedBlockers"] == ["statement_level_if_assignment_shape_unsupported"]
    helper = classify_failure("call to non-math function `mg_step01` unsupported in E2")
    assert helper["detectedBlockers"] == ["selected_guard_helper_call_unsupported"]
    nonzero = classify_failure("BinaryOp unsupported as C branch condition")
    assert nonzero["detectedBlockers"] == ["nonzero_comparison_condition_unsupported"]


def test_fef_p81_boundaries_and_claim_flags_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    gates = {gate["id"]: gate["status"] for gate in payload["releaseGates"]}
    assert gates["selected_guard_helper_call_adapter_probe"] == "recorded"
    assert gates["selected_reingest_execution"] == "blocked_not_executed"
    assert gates["statement_level_if_assignment_surface"] == "blocked"
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


def test_fef_p81_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P81")


def test_fef_p81_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p81_compound_condition_guard_helper_adapter_probe.py",
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
    assert "FEF_P81_COMPOUND_CONDITION_GUARD_HELPER_ADAPTER_PROBE_OK" in proc.stdout
