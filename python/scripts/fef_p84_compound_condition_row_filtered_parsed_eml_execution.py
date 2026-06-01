#!/usr/bin/env python3
"""FEF-P84 row-filtered parsed-EML execution harness for the compound condition."""

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

from scripts import fef_p83_compound_condition_short_circuit_execution_policy as p83  # noqa: E402

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p84_compound_condition_row_filtered_parsed_eml_execution.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P84_COMPOUND_CONDITION_ROW_FILTERED_PARSED_EML_EXECUTION_PASS"

P83_PACKET = ROOT / "reports/evidence_packets/fef_p83_compound_condition_short_circuit_execution_policy.json"
P83_RESULT = ROOT / "python/results/fef_p83_compound_condition_short_circuit_execution_policy/fef_p83_compound_condition_short_circuit_execution_policy_2026_05_31.json"

CLAIM_FLAGS = {
    "compound_condition_row_filtered_execution_claim": False,
    "compound_condition_reingest_execution_claim": False,
    "compound_condition_reingest_supported": False,
    "compound_condition_lowering_implemented": False,
    "compound_condition_support_claim": False,
    "short_circuit_semantics_implemented": False,
    "guarded_division_runtime_helper_installed": False,
    "nonzero_predicate_runtime_helper_installed": False,
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
    "FEF-P84 executes only the P83 eligible parsed-EML rows.",
    "FEF-P84 keeps zero-denominator short-circuit rows blocked.",
    "FEF-P84 does not claim full parsed-EML execution over all P77 rows.",
    "FEF-P84 does not change eFrog or Forge source code.",
    "FEF-P84 does not claim supported compound-condition re-ingest.",
    "FEF-P84 does not claim the normalized eager-division shape preserves all C short-circuit semantics.",
    "FEF-P84 does not install helper functions in Forge or eFrog.",
    "FEF-P84 does not claim compound-condition support.",
    "FEF-P84 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P84 does not claim runtime performance.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def step01(value: float) -> float:
    return max(0.0, min(1.0, value * 1.0e30))


def evaluate_p82_parsed_shape(x: float, y: float) -> dict[str, float]:
    lhs = step01(x)
    rhs_candidate = step01(y * y)
    rhs = lhs * rhs_candidate
    selected_candidate = (x / y) * step01(rhs_candidate * rhs_candidate)
    selected = lhs * selected_candidate
    observed = lhs * rhs * selected
    return {
        "lhs": lhs,
        "rhsCandidate": rhs_candidate,
        "rhs": rhs,
        "selectedCandidate": selected_candidate,
        "selected": selected,
        "observed": observed,
    }


def build_execution_rows(policy: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in policy["executionPolicyRows"]:
        if row["futureComparisonAllowed"]:
            values = evaluate_p82_parsed_shape(float(row["inputs"]["x"]), float(row["inputs"]["y"]))
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
                    "executionStatus": "executed_row_filtered_parsed_eml",
                    "p83PolicyStatus": row["policyStatus"],
                    "intermediates": values,
                }
            )
        else:
            rows.append(
                {
                    "sampleId": row["sampleId"],
                    "path": row["path"],
                    "inputs": dict(row["inputs"]),
                    "expected": row["expected"],
                    "observed": None,
                    "absError": None,
                    "pass": None,
                    "executionStatus": "blocked_by_p83_policy",
                    "p83PolicyStatus": row["policyStatus"],
                    "blockReason": row["reason"],
                }
            )
    return rows


def build_execution_result(policy: dict[str, Any]) -> dict[str, Any]:
    rows = build_execution_rows(policy)
    executed_rows = [row for row in rows if row["executionStatus"] == "executed_row_filtered_parsed_eml"]
    blocked_rows = [row for row in rows if row["executionStatus"] == "blocked_by_p83_policy"]
    return {
        "harnessId": "selected_row_filtered_parsed_eml_execution_harness_v0",
        "scope": "p83_allowed_rows_only",
        "executionPolicyId": policy["policyId"],
        "rowCount": len(rows),
        "executedRowCount": len(executed_rows),
        "blockedRowCount": len(blocked_rows),
        "passCount": sum(1 for row in executed_rows if row["pass"] is True),
        "failCount": sum(1 for row in executed_rows if row["pass"] is False),
        "maxAbsError": max((row["absError"] for row in executed_rows), default=0.0),
        "blockedSampleIds": [row["sampleId"] for row in blocked_rows],
        "executedSampleIds": [row["sampleId"] for row in executed_rows],
        "allExecutedRowsFinite": all(math.isfinite(float(row["observed"])) for row in executed_rows),
        "allExecutedRowsPass": all(row["pass"] is True for row in executed_rows),
        "zeroDenominatorRowsExecuted": False,
        "fullP77RowComparisonPerformed": False,
        "rows": rows,
    }


def build_summary(p83_packet: dict[str, Any], p83_payload: dict[str, Any], execution: dict[str, Any]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p83ValidationPass": p83_packet["validationStatus"] == "pass",
        "p83ClaimFlagsAllFalse": all(value is False for value in p83_packet["claimFlags"].values()),
        "selectedFixtureId": p83_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p83_payload["summary"]["selectedFixtureStillBlocked"],
        "harnessId": execution["harnessId"],
        "executionPolicyId": execution["executionPolicyId"],
        "rowCount": execution["rowCount"],
        "executedRowCount": execution["executedRowCount"],
        "blockedRowCount": execution["blockedRowCount"],
        "passCount": execution["passCount"],
        "failCount": execution["failCount"],
        "maxAbsError": execution["maxAbsError"],
        "allExecutedRowsFinite": execution["allExecutedRowsFinite"],
        "allExecutedRowsPass": execution["allExecutedRowsPass"],
        "zeroDenominatorRowsExecuted": execution["zeroDenominatorRowsExecuted"],
        "fullP77RowComparisonPerformed": execution["fullP77RowComparisonPerformed"],
        "rowFilteredParsedEmlExecutionPerformed": True,
        "runtimeComparisonPerformed": True,
        "compoundConditionReingestSupported": False,
        "helperRuntimeInstalled": False,
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
    p83_packet = read_json(P83_PACKET)
    p83_payload = read_json(P83_RESULT)
    p83.validate_payload(p83_payload)
    execution = build_execution_result(p83_payload["executionPolicy"])
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p84-compound-condition-row-filtered-parsed-eml-execution",
        "decision": "selected_row_filtered_parsed_eml_execution_pass_blocked_rows_preserved",
        "sourcePacket": {
            "phase": "P83",
            "packetPath": str(P83_PACKET.relative_to(ROOT)),
            "resultPath": str(P83_RESULT.relative_to(ROOT)),
            "reviewDecision": p83_packet["reviewDecision"],
            "validationStatus": p83_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p83_payload["selectedFixture"]),
        "executionResult": execution,
        "summary": build_summary(p83_packet, p83_payload, execution),
        "releaseGates": [
            {"id": "selected_row_filtered_parsed_eml_execution", "status": "executed_p83_allowed_rows_only"},
            {"id": "blocked_zero_denominator_rows", "status": "preserved_blocked"},
            {"id": "full_p77_row_comparison", "status": "blocked_not_performed"},
            {"id": "helper_runtime_installation", "status": "not_performed"},
            {"id": "compound_condition_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P84 executes the parsed-EML-shaped evaluator only for the five P83 eligible rows.",
            "All five executed rows match the P77 expected values with max absolute error 0.0.",
            "The two zero-denominator short-circuit rows remain blocked.",
            "P84 does not perform a full P77 row comparison.",
        ],
        "blockedStatements": [
            "All P77 rows were executed through parsed EML.",
            "Zero-denominator short-circuit rows were safely executed through eager parsed EML.",
            "Compound-condition re-ingest is supported.",
            "The selected harness is installed in eFrog or Forge.",
            "The normalized branch-free source is semantically equivalent to the original C short-circuit source.",
            "Compound-condition lowering is implemented.",
            "Short-circuit boolean conditions are supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Add a selected guarded_div source primitive if zero-denominator rows should be compared.",
            "Keep zero-denominator short-circuit rows blocked unless non-evaluation is preserved.",
            "Record private reviewer response to the P47-P84 branch/control-flow bundle.",
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
        "title": "FEF-P84 Compound-Condition Row-Filtered Parsed-EML Execution",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_row_filtered_parsed_eml_execution_pass_blocked_rows_preserved",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected row-filtered execution only; zero-denominator rows remain blocked, with no installed eFrog/Forge behavior change, compound-condition support, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P84 executes only the five rows allowed by P83.",
            "All executed rows pass against P77 expected values.",
            "Two zero-denominator rows remain blocked to preserve the short-circuit boundary.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p84_compound_condition_row_filtered_parsed_eml_execution.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p84_compound_condition_row_filtered_parsed_eml_execution.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p84_compound_condition_row_filtered_parsed_eml_execution.v0",
        "date": DATE,
        "title": "FEF-P84 Compound-Condition Row-Filtered Parsed-EML Execution",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Add selected guarded_div source primitive or keep zero-denominator rows blocked.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = [
        f"- `{row['sampleId']}` `{row['executionStatus']}` observed `{row['observed']}` pass `{row['pass']}`"
        for row in payload["executionResult"]["rows"]
    ]
    return "\n".join(
        [
            "# FEF-P84 Compound-Condition Row-Filtered Parsed-EML Execution",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P84 executes only the P83-safe parsed-EML rows and preserves the zero-denominator blockers.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Harness: `{summary['harnessId']}`",
            f"- Executed rows: `{summary['executedRowCount']}`",
            f"- Blocked rows: `{summary['blockedRowCount']}`",
            f"- Pass count: `{summary['passCount']}`",
            f"- Fail count: `{summary['failCount']}`",
            f"- Max absolute error: `{summary['maxAbsError']}`",
            f"- Full P77 row comparison performed: `{summary['fullP77RowComparisonPerformed']}`",
            f"- Compiler behavior changed: `{summary['compilerBehaviorChanged']}`",
            "",
            "## Rows",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Selected row-filtered execution only.",
            "- Zero-denominator short-circuit rows remain blocked.",
            "- No installed eFrog or Forge behavior change.",
            "- No compound-condition support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P84 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P84 status")
    p83.validate_payload(read_json(P83_RESULT))
    summary = payload["summary"]
    for key in [
        "p83ValidationPass",
        "p83ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "allExecutedRowsFinite",
        "allExecutedRowsPass",
        "rowFilteredParsedEmlExecutionPerformed",
        "runtimeComparisonPerformed",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["rowCount"] != 7:
        raise ValueError("expected seven policy rows")
    if summary["executedRowCount"] != 5 or summary["blockedRowCount"] != 2:
        raise ValueError("expected five executed rows and two blocked rows")
    if summary["passCount"] != 5 or summary["failCount"] != 0:
        raise ValueError("expected all executed rows to pass")
    if summary["maxAbsError"] != 0.0:
        raise ValueError("expected exact selected row-filtered agreement")
    if payload["executionResult"]["blockedSampleIds"] != ["sample_01", "sample_03"]:
        raise ValueError("expected zero-denominator rows to remain blocked")
    for key in [
        "zeroDenominatorRowsExecuted",
        "fullP77RowComparisonPerformed",
        "compoundConditionReingestSupported",
        "helperRuntimeInstalled",
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
    result_path = out_dir / f"fef_p84_compound_condition_row_filtered_parsed_eml_execution_{STAMP}.json"
    report_path = report_dir / f"fef_p84_compound_condition_row_filtered_parsed_eml_execution_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p84_compound_condition_row_filtered_parsed_eml_execution.json"
    feed_path = command_feed_dir / f"fef_p84_compound_condition_row_filtered_parsed_eml_execution_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p84_compound_condition_row_filtered_parsed_eml_execution")
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
    print("FEF_P84_COMPOUND_CONDITION_ROW_FILTERED_PARSED_EML_EXECUTION_OK")
    print(f"executed_rows={built['payload']['summary']['executedRowCount']}")
    print(f"blocked_rows={built['payload']['summary']['blockedRowCount']}")
    print(f"max_abs_error={built['payload']['summary']['maxAbsError']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
