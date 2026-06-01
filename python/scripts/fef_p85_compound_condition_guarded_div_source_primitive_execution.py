#!/usr/bin/env python3
"""FEF-P85 guarded-div source primitive execution for the compound condition."""

from __future__ import annotations

import argparse
import copy
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import fef_p84_compound_condition_row_filtered_parsed_eml_execution as p84  # noqa: E402

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p85_compound_condition_guarded_div_source_primitive_execution.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P85_COMPOUND_CONDITION_GUARDED_DIV_SOURCE_PRIMITIVE_EXECUTION_PASS"

P84_PACKET = ROOT / "reports/evidence_packets/fef_p84_compound_condition_row_filtered_parsed_eml_execution.json"
P84_RESULT = ROOT / "python/results/fef_p84_compound_condition_row_filtered_parsed_eml_execution/fef_p84_compound_condition_row_filtered_parsed_eml_execution_2026_05_31.json"

CLAIM_FLAGS = {
    "compound_condition_guarded_div_source_primitive_execution_claim": False,
    "compound_condition_full_p77_guarded_primitive_comparison_claim": False,
    "compound_condition_reingest_execution_claim": False,
    "compound_condition_reingest_supported": False,
    "compound_condition_lowering_implemented": False,
    "compound_condition_support_claim": False,
    "short_circuit_semantics_implemented": False,
    "guarded_division_runtime_helper_installed": False,
    "nonzero_predicate_runtime_helper_installed": False,
    "selected_source_primitive_installed": False,
    "selected_codegen_fixture_installed_in_forge": False,
    "assignment_phi_support_claim": False,
    "nested_branch_support_claim": False,
    "control_flow_ir_implemented": False,
    "frontend_lowering_changed": False,
    "unsupported_constructs_supported": False,
    "general_branch_control_flow_claim": False,
    "branch_control_flow_reingest_claim": False,
    "full_non_generated_source_roundtrip_claim": False,
    "full_c_rust_roundtrip_claim": False,
    "arbitrary_source_family_claim": False,
    "private_reviewer_decision_recorded": False,
    "public_preview_release_claim": False,
    "package_published": False,
    "checkout_enabled": False,
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "runtime_performance_claim": False,
    "production_ready": False,
}

NON_CLAIMS = [
    "FEF-P85 records a selected guarded-div source primitive execution artifact only.",
    "FEF-P85 does not install guarded_div, nonzero01, or step01 in eFrog or Forge.",
    "FEF-P85 does not change eFrog or Forge source code.",
    "FEF-P85 does not execute re-ingested code.",
    "FEF-P85 does not claim supported compound-condition re-ingest.",
    "FEF-P85 does not claim compiler-wide short-circuit semantics.",
    "FEF-P85 does not claim compound-condition support.",
    "FEF-P85 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P85 does not claim runtime performance.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def step01(value: float) -> float:
    return 1.0 if value > 0.0 else 0.0


def nonzero01(value: float) -> float:
    return 1.0 if value != 0.0 else 0.0


def guarded_div(numerator: float, denominator: float, default: float, guard: float) -> dict[str, Any]:
    if guard != 0.0:
        return {"value": numerator / denominator, "divisionEvaluated": True, "defaultUsed": False}
    return {"value": default, "divisionEvaluated": False, "defaultUsed": True}


def evaluate_guarded_div_source_primitive(x: float, y: float) -> dict[str, Any]:
    lhs = step01(x)
    rhs_evaluated = lhs != 0.0
    rhs = nonzero01(y) if rhs_evaluated else 0.0
    div = guarded_div(x, y, 0.0, rhs)
    and_guard = lhs * rhs
    observed = and_guard * float(div["value"])
    return {
        "lhs": lhs,
        "rhsEvaluated": rhs_evaluated,
        "rhs": rhs,
        "andGuard": and_guard,
        "guardedDivValue": float(div["value"]),
        "divisionEvaluated": div["divisionEvaluated"],
        "defaultUsed": div["defaultUsed"],
        "observed": observed,
    }


def build_execution_rows(p84_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in p84_payload["executionResult"]["rows"]:
        values = evaluate_guarded_div_source_primitive(float(row["inputs"]["x"]), float(row["inputs"]["y"]))
        observed = values["observed"]
        expected = float(row["expected"])
        abs_error = abs(observed - expected)
        rows.append(
            {
                "sampleId": row["sampleId"],
                "path": row["path"],
                "inputs": dict(row["inputs"]),
                "expected": expected,
                "observed": observed,
                "absError": abs_error,
                "pass": math.isfinite(observed) and abs_error <= 1.0e-12,
                "executionStatus": "executed_guarded_div_source_primitive",
                "p84ExecutionStatus": row["executionStatus"],
                "wasBlockedInP84": row["executionStatus"] == "blocked_by_p83_policy",
                "zeroDenominator": float(row["inputs"]["y"]) == 0.0,
                "intermediates": values,
            }
        )
    return rows


def build_execution_result(p84_payload: dict[str, Any]) -> dict[str, Any]:
    rows = build_execution_rows(p84_payload)
    zero_denominator_rows = [row for row in rows if row["zeroDenominator"]]
    return {
        "harnessId": "selected_guarded_div_source_primitive_execution_harness_v0",
        "sourcePrimitiveId": "selected_guarded_div_non_evaluation_source_primitive_v0",
        "scope": "selected_p77_rows_guarded_div_source_primitive_only",
        "rowCount": len(rows),
        "executedRowCount": len(rows),
        "p84PreviouslyBlockedRowCount": sum(1 for row in rows if row["wasBlockedInP84"]),
        "zeroDenominatorRowCount": len(zero_denominator_rows),
        "zeroDenominatorRowsWithDivisionSkipped": sum(
            1 for row in zero_denominator_rows if row["intermediates"]["divisionEvaluated"] is False
        ),
        "passCount": sum(1 for row in rows if row["pass"] is True),
        "failCount": sum(1 for row in rows if row["pass"] is False),
        "maxAbsError": max((row["absError"] for row in rows), default=0.0),
        "executedSampleIds": [row["sampleId"] for row in rows],
        "previouslyBlockedSampleIds": [row["sampleId"] for row in rows if row["wasBlockedInP84"]],
        "allRowsFinite": all(math.isfinite(float(row["observed"])) for row in rows),
        "allRowsPass": all(row["pass"] is True for row in rows),
        "fullP77GuardedPrimitiveComparisonPerformed": True,
        "zeroDenominatorRowsRepresentedByGuardedPrimitive": True,
        "zeroDenominatorDivisionEvaluated": any(
            row["intermediates"]["divisionEvaluated"] is True for row in zero_denominator_rows
        ),
        "rows": rows,
    }


def build_summary(p84_packet: dict[str, Any], p84_payload: dict[str, Any], execution: dict[str, Any]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p84ValidationPass": p84_packet["validationStatus"] == "pass",
        "p84ClaimFlagsAllFalse": all(value is False for value in p84_packet["claimFlags"].values()),
        "selectedFixtureId": p84_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p84_payload["summary"]["selectedFixtureStillBlocked"],
        "harnessId": execution["harnessId"],
        "sourcePrimitiveId": execution["sourcePrimitiveId"],
        "rowCount": execution["rowCount"],
        "executedRowCount": execution["executedRowCount"],
        "p84PreviouslyBlockedRowCount": execution["p84PreviouslyBlockedRowCount"],
        "zeroDenominatorRowCount": execution["zeroDenominatorRowCount"],
        "zeroDenominatorRowsWithDivisionSkipped": execution["zeroDenominatorRowsWithDivisionSkipped"],
        "passCount": execution["passCount"],
        "failCount": execution["failCount"],
        "maxAbsError": execution["maxAbsError"],
        "allRowsFinite": execution["allRowsFinite"],
        "allRowsPass": execution["allRowsPass"],
        "fullP77GuardedPrimitiveComparisonPerformed": execution["fullP77GuardedPrimitiveComparisonPerformed"],
        "zeroDenominatorRowsRepresentedByGuardedPrimitive": execution["zeroDenominatorRowsRepresentedByGuardedPrimitive"],
        "zeroDenominatorDivisionEvaluated": execution["zeroDenominatorDivisionEvaluated"],
        "sourcePrimitiveExecutionPerformed": True,
        "runtimeComparisonPerformed": True,
        "compoundConditionReingestSupported": False,
        "helperRuntimeInstalled": False,
        "sourcePrimitiveInstalled": False,
        "codegenFixtureInstalledInForge": False,
        "compilerBehaviorChanged": False,
        "frontendLoweringChanged": False,
        "compoundConditionLoweringImplemented": False,
        "compoundConditionSupportClaim": False,
        "shortCircuitSemanticsImplemented": False,
        "guardedDivisionRuntimeHelperInstalled": False,
        "nonzeroPredicateRuntimeHelperInstalled": False,
        "assignmentPhiSupportClaim": False,
        "nestedBranchSupportClaim": False,
        "controlFlowIrImplemented": False,
        "unsupportedConstructsSupported": False,
        "generalBranchControlFlowClaim": False,
        "branchControlFlowReingestClaim": False,
        "fullNonGeneratedSourceRoundtripClaim": False,
        "fullCRustRoundtripClaim": False,
        "arbitrarySourceFamilyClaim": False,
        "reviewerDecisionRecorded": False,
        "packagePublished": False,
        "checkoutEnabled": False,
        "publicReady": False,
        "safeToPublishPublicly": False,
        "compilerCorrectnessClaim": False,
        "formalEquivalenceClaim": False,
        "runtimePerformanceClaim": False,
        "productionReady": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }


def build_payload() -> dict[str, Any]:
    p84_packet = read_json(P84_PACKET)
    p84_payload = read_json(P84_RESULT)
    p84.validate_payload(p84_payload)
    execution = build_execution_result(p84_payload)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p85-compound-condition-guarded-div-source-primitive-execution",
        "decision": "selected_guarded_div_source_primitive_executes_all_rows_installation_blocked",
        "sourcePacket": {
            "phase": "P84",
            "packetPath": str(P84_PACKET.relative_to(ROOT)),
            "resultPath": str(P84_RESULT.relative_to(ROOT)),
            "reviewDecision": p84_packet["reviewDecision"],
            "validationStatus": p84_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p84_payload["selectedFixture"]),
        "sourcePrimitive": {
            "primitiveId": execution["sourcePrimitiveId"],
            "status": "selected_source_primitive_executed_not_installed",
            "surface": "guarded_div(x, y, default=0.0, guard=nonzero01(y))",
            "nonEvaluationBoundary": "division is evaluated only when guard is nonzero",
            "installedInEfrog": False,
            "installedInForge": False,
            "compilerBehaviorChanged": False,
        },
        "executionResult": execution,
        "summary": build_summary(p84_packet, p84_payload, execution),
        "releaseGates": [
            {"id": "selected_guarded_div_source_primitive_execution", "status": "executed_all_selected_rows"},
            {"id": "zero_denominator_non_evaluation_boundary", "status": "preserved_by_source_primitive"},
            {"id": "source_primitive_installation", "status": "not_performed"},
            {"id": "compound_condition_reingest_execution", "status": "blocked_not_performed"},
            {"id": "compound_condition_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P85 executes a selected guarded-div source primitive over all seven P77 rows.",
            "All seven guarded-primitive rows match the P77 expected values with max absolute error 0.0.",
            "The two zero-denominator rows are represented by guard-skipped division, not eager division.",
            "P85 does not install this primitive in eFrog or Forge.",
        ],
        "blockedStatements": [
            "Compound-condition re-ingest is supported.",
            "The selected guarded-div source primitive is installed in eFrog or Forge.",
            "The selected primitive proves compiler-wide short-circuit semantics.",
            "Compound-condition lowering is implemented.",
            "Short-circuit boolean conditions are supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Decide whether to install a selected guarded-div source primitive in the local adapter pipeline.",
            "If installed, add a fail-closed re-ingest probe that checks the same non-evaluation boundary.",
            "Record private reviewer response to the P47-P85 branch/control-flow bundle.",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    return copy.deepcopy(payload)


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "title": "FEF-P85 Compound-Condition Guarded-Div Source Primitive Execution",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_guarded_div_source_primitive_executes_all_rows_installation_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected source-primitive execution only; no installed eFrog/Forge behavior change, compound-condition support, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P85 executes all seven P77 rows through a guarded-div source primitive.",
            "The two zero-denominator rows skip division through the guard.",
            "The primitive remains selected evidence only and is not installed.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p85_compound_condition_guarded_div_source_primitive_execution.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p85_compound_condition_guarded_div_source_primitive_execution.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p85_compound_condition_guarded_div_source_primitive_execution.v0",
        "date": DATE,
        "title": "FEF-P85 Compound-Condition Guarded-Div Source Primitive Execution",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Decide whether to install the selected guarded-div primitive in the local adapter pipeline.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = [
        f"- `{row['sampleId']}` `{row['executionStatus']}` observed `{row['observed']}` pass `{row['pass']}` div-eval `{row['intermediates']['divisionEvaluated']}`"
        for row in payload["executionResult"]["rows"]
    ]
    return "\n".join(
        [
            "# FEF-P85 Compound-Condition Guarded-Div Source Primitive Execution",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P85 executes a selected guarded-div source primitive over all P77 rows without installing it.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Harness: `{summary['harnessId']}`",
            f"- Source primitive: `{summary['sourcePrimitiveId']}`",
            f"- Executed rows: `{summary['executedRowCount']}`",
            f"- Previously blocked P84 rows: `{summary['p84PreviouslyBlockedRowCount']}`",
            f"- Zero-denominator rows with division skipped: `{summary['zeroDenominatorRowsWithDivisionSkipped']}`",
            f"- Pass count: `{summary['passCount']}`",
            f"- Fail count: `{summary['failCount']}`",
            f"- Max absolute error: `{summary['maxAbsError']}`",
            f"- Source primitive installed: `{summary['sourcePrimitiveInstalled']}`",
            f"- Compiler behavior changed: `{summary['compilerBehaviorChanged']}`",
            "",
            "## Rows",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Selected source-primitive execution only.",
            "- No installed eFrog or Forge behavior change.",
            "- No compound-condition support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P85 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P85 status")
    p84.validate_payload(read_json(P84_RESULT))
    summary = payload["summary"]
    for key in [
        "p84ValidationPass",
        "p84ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "allRowsFinite",
        "allRowsPass",
        "fullP77GuardedPrimitiveComparisonPerformed",
        "zeroDenominatorRowsRepresentedByGuardedPrimitive",
        "sourcePrimitiveExecutionPerformed",
        "runtimeComparisonPerformed",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["rowCount"] != 7 or summary["executedRowCount"] != 7:
        raise ValueError("expected seven executed rows")
    if summary["p84PreviouslyBlockedRowCount"] != 2:
        raise ValueError("expected two P84 blocked rows to be represented")
    if summary["zeroDenominatorRowCount"] != 2 or summary["zeroDenominatorRowsWithDivisionSkipped"] != 2:
        raise ValueError("expected zero-denominator rows to skip division")
    if summary["passCount"] != 7 or summary["failCount"] != 0:
        raise ValueError("expected all rows to pass")
    if summary["maxAbsError"] != 0.0:
        raise ValueError("expected exact selected guarded-primitive agreement")
    if payload["executionResult"]["previouslyBlockedSampleIds"] != ["sample_01", "sample_03"]:
        raise ValueError("expected P84 blocked rows to be represented")
    for key in [
        "zeroDenominatorDivisionEvaluated",
        "compoundConditionReingestSupported",
        "helperRuntimeInstalled",
        "sourcePrimitiveInstalled",
        "codegenFixtureInstalledInForge",
        "compilerBehaviorChanged",
        "frontendLoweringChanged",
        "compoundConditionLoweringImplemented",
        "compoundConditionSupportClaim",
        "shortCircuitSemanticsImplemented",
        "guardedDivisionRuntimeHelperInstalled",
        "nonzeroPredicateRuntimeHelperInstalled",
        "assignmentPhiSupportClaim",
        "nestedBranchSupportClaim",
        "controlFlowIrImplemented",
        "unsupportedConstructsSupported",
        "generalBranchControlFlowClaim",
        "branchControlFlowReingestClaim",
        "fullNonGeneratedSourceRoundtripClaim",
        "fullCRustRoundtripClaim",
        "arbitrarySourceFamilyClaim",
        "reviewerDecisionRecorded",
        "packagePublished",
        "checkoutEnabled",
        "publicReady",
        "safeToPublishPublicly",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
        "runtimePerformanceClaim",
        "productionReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if not all(value is False for value in payload["claimFlags"].values()):
        raise ValueError("claim flags must remain false")


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    evidence = build_evidence_packet(payload)
    feed = build_command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"fef_p85_compound_condition_guarded_div_source_primitive_execution_{STAMP}.json"
    report_path = report_dir / f"fef_p85_compound_condition_guarded_div_source_primitive_execution_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p85_compound_condition_guarded_div_source_primitive_execution.json"
    feed_path = command_feed_dir / f"fef_p85_compound_condition_guarded_div_source_primitive_execution_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p85_compound_condition_guarded_div_source_primitive_execution")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_outputs(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("FEF_P85_COMPOUND_CONDITION_GUARDED_DIV_SOURCE_PRIMITIVE_EXECUTION_OK")
    print(f"executed_rows={built['payload']['summary']['executedRowCount']}")
    print(f"previously_blocked_rows={built['payload']['summary']['p84PreviouslyBlockedRowCount']}")
    print(f"max_abs_error={built['payload']['summary']['maxAbsError']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
