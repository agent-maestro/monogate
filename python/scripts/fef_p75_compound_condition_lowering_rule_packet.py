#!/usr/bin/env python3
"""FEF-P75 selected compound-condition lowering rule packet."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import fef_p74_compound_condition_generated_target_runtime_blocker as p74

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p75_compound_condition_lowering_rule_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P75_COMPOUND_CONDITION_LOWERING_RULE_PACKET_PASS"

P74_PACKET = ROOT / "reports/evidence_packets/fef_p74_compound_condition_generated_target_runtime_blocker.json"
P74_RESULT = ROOT / "python/results/fef_p74_compound_condition_generated_target_runtime_blocker/fef_p74_compound_condition_generated_target_runtime_blocker_2026_05_31.json"

CLAIM_FLAGS = {
    "compound_condition_lowering_rule_packet_claim": False,
    "compound_condition_lowering_implemented": False,
    "compound_condition_generated_target_execution_claim": False,
    "compound_condition_reingest_execution_claim": False,
    "compound_condition_support_claim": False,
    "short_circuit_semantics_implemented": False,
    "guarded_division_runtime_helper_implemented": False,
    "nonzero_predicate_runtime_helper_implemented": False,
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
    "FEF-P75 records a selected compound-condition lowering rule packet only.",
    "FEF-P75 does not change Forge or eFrog lowering behavior.",
    "FEF-P75 does not execute generated target code.",
    "FEF-P75 does not execute re-ingested code.",
    "FEF-P75 does not implement short-circuit condition semantics in Forge or eFrog.",
    "FEF-P75 does not implement guarded division or nonzero predicate helpers.",
    "FEF-P75 does not claim compound-condition support.",
    "FEF-P75 does not claim assignment/phi or nested branch support.",
    "FEF-P75 does not claim general branch/control-flow support.",
    "FEF-P75 does not claim branch/control-flow re-ingest support.",
    "FEF-P75 does not claim full non-generated source roundtrip.",
    "FEF-P75 does not claim arbitrary C/Rust source-family support.",
    "FEF-P75 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P75 does not claim runtime performance.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def lowering_rule() -> dict[str, Any]:
    return {
        "ruleId": "selected_c_and_short_circuit_guard_lowering_v0",
        "selectedFixtureId": "c_and_short_circuit_guard_v0",
        "sourcePattern": "if (x > 0.0 && y != 0.0) { return x / y; } return 0.0;",
        "status": "candidate_rule_recorded_runtime_blocked",
        "ruleScope": "selected_fixture_only",
        "conditionLowering": [
            {"id": "lhs_x_gt_zero", "surface": "x > 0.0", "lowering": "step01(x)", "requiresHelper": "step01"},
            {"id": "rhs_y_nonzero", "surface": "y != 0.0", "lowering": "nonzero01(y)", "requiresHelper": "nonzero01"},
            {"id": "and_guard", "surface": "lhs && rhs", "lowering": "lhs_x_gt_zero * rhs_y_nonzero", "requiresShortCircuitOrder": True},
        ],
        "valueLowering": {
            "selectedValue": "guarded_div(x, y, default=0.0, guard=rhs_y_nonzero)",
            "mergedReturn": "and_guard * selectedValue",
            "requiresHelper": "guarded_div",
        },
        "requiredHelpers": ["step01", "nonzero01", "guarded_div"],
        "semanticRequirements": [
            "left condition evaluated before right condition",
            "right condition skipped when left condition is false",
            "division is not evaluated unless y != 0.0",
            "merged return defaults to 0.0 when guard is false",
        ],
        "generatedTargetRuntimeStatusAfterRule": "blocked_until_helpers_and_codegen_exist",
        "compilerBehaviorChanged": False,
        "frontendLoweringChanged": False,
        "supportClaimAllowed": False,
    }


def evaluate_rule_for_sample(sample: dict[str, Any]) -> dict[str, Any]:
    x = float(sample["inputs"]["x"])
    y = float(sample["inputs"]["y"])
    lhs = 1.0 if x > 0.0 else 0.0
    rhs_evaluated = lhs == 1.0
    rhs = 1.0 if rhs_evaluated and y != 0.0 else 0.0
    and_guard = lhs * rhs
    selected_value = x / y if rhs == 1.0 else 0.0
    lowered_value = and_guard * selected_value
    expected = float(sample["expected"])
    return {
        "sampleId": sample["sampleId"],
        "inputs": copy.deepcopy(sample["inputs"]),
        "expected": expected,
        "loweredRuleValue": lowered_value,
        "absError": abs(lowered_value - expected),
        "pass": lowered_value == expected,
        "lhsValue": lhs,
        "rhsEvaluated": rhs_evaluated,
        "rhsValue": rhs,
        "andGuard": and_guard,
        "divisionProtected": rhs != 1.0,
        "path": sample["path"],
        "sourceSemanticsOnly": True,
    }


def rule_validation_rows(p74_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    p73_result = read_json(ROOT / p74_payload["sourcePacket"]["resultPath"])
    for row in p73_result["runtimeComparison"]["rows"]:
        rows.append(evaluate_rule_for_sample(row))
    return rows


def build_summary(p74_packet: dict[str, Any], p74_payload: dict[str, Any], rule: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p74ValidationPass": p74_packet["validationStatus"] == "pass",
        "p74ClaimFlagsAllFalse": all(value is False for value in p74_packet["claimFlags"].values()),
        "selectedFixtureId": p74_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p74_payload["summary"]["selectedFixtureStillBlocked"],
        "loweringRuleStatus": rule["status"],
        "loweringRuleScope": rule["ruleScope"],
        "requiredHelperCount": len(rule["requiredHelpers"]),
        "semanticRequirementCount": len(rule["semanticRequirements"]),
        "ruleValidationSampleCount": len(rows),
        "ruleValidationPassCount": sum(1 for row in rows if row["pass"]),
        "ruleValidationFailCount": sum(1 for row in rows if not row["pass"]),
        "ruleValidationMaxAbsError": max(row["absError"] for row in rows),
        "generatedTargetRuntimeStatusAfterRule": rule["generatedTargetRuntimeStatusAfterRule"],
        "compilerBehaviorChanged": False,
        "frontendLoweringChanged": False,
        "compoundConditionLoweringImplemented": False,
        "compoundConditionGeneratedTargetExecuted": False,
        "compoundConditionReingestExecuted": False,
        "compoundConditionSupportClaim": False,
        "shortCircuitSemanticsImplemented": False,
        "guardedDivisionRuntimeHelperImplemented": False,
        "nonzeroPredicateRuntimeHelperImplemented": False,
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
    p74_packet = read_json(P74_PACKET)
    p74_payload = read_json(P74_RESULT)
    p74.validate_payload(p74_payload)
    rule = lowering_rule()
    rows = rule_validation_rows(p74_payload)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p75-compound-condition-lowering-rule-packet",
        "decision": "selected_compound_condition_lowering_rule_recorded_runtime_blocked",
        "sourcePacket": {
            "phase": "P74",
            "packetPath": str(P74_PACKET.relative_to(ROOT)),
            "resultPath": str(P74_RESULT.relative_to(ROOT)),
            "reviewDecision": p74_packet["reviewDecision"],
            "validationStatus": p74_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p74_payload["selectedFixture"]),
        "loweringRule": rule,
        "ruleValidationRows": rows,
        "summary": build_summary(p74_packet, p74_payload, rule, rows),
        "releaseGates": [
            {"id": "selected_compound_condition_lowering_rule", "status": "recorded_runtime_blocked"},
            {"id": "generated_target_runtime_execution", "status": "blocked_not_run"},
            {"id": "compound_condition_reingest_execution", "status": "not_performed"},
            {"id": "compound_condition_support", "status": "blocked"},
            {"id": "short_circuit_semantics_implementation", "status": "not_performed"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P75 records a selected compound-condition lowering rule shape for review.",
            "The rule validates against the existing seven-sample semantics table.",
            "P75 does not change Forge/eFrog behavior and generated-target runtime remains blocked.",
        ],
        "blockedStatements": [
            "Compound-condition lowering is implemented in Forge or eFrog.",
            "Generated compound-condition target code was executed.",
            "Re-ingested compound-condition code was executed.",
            "Short-circuit condition semantics are implemented in Forge or eFrog.",
            "Short-circuit boolean conditions are supported.",
            "Frontend branch lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Implement guarded helpers and selected codegen before generated-target runtime execution.",
            "Record private reviewer response to the P47-P75 branch/control-flow bundle.",
            "Move to another unsupported P59/P60 form with the same fixture/sample/reference/original-source ladder.",
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
        "title": "FEF-P75 Compound-Condition Lowering Rule Packet",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_lowering_rule_recorded_runtime_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected lowering-rule packet only; no Forge/eFrog behavior change, generated target execution, re-ingest execution, compound-condition support, frontend widening, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P75 records a selected compound-condition lowering rule shape.",
            "The rule validates against seven existing semantic samples.",
            "Generated-target runtime remains blocked until helpers and codegen exist.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p75_compound_condition_lowering_rule_packet.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p75_compound_condition_lowering_rule_packet.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p75_compound_condition_lowering_rule_packet.v0",
        "date": DATE,
        "title": "FEF-P75 Compound-Condition Lowering Rule Packet",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Implement guarded helpers and selected codegen before generated-target runtime execution.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Sample | Path | Expected | Rule Value | Abs Error | Pass |", "|---|---|---:|---:|---:|---|"]
    for row in payload["ruleValidationRows"]:
        rows.append(
            f"| `{row['sampleId']}` | `{row['path']}` | {row['expected']} | {row['loweredRuleValue']} | {row['absError']} | `{row['pass']}` |"
        )
    helpers = [f"- `{item}`" for item in payload["loweringRule"]["requiredHelpers"]]
    requirements = [f"- {item}" for item in payload["loweringRule"]["semanticRequirements"]]
    return "\n".join(
        [
            "# FEF-P75 Compound-Condition Lowering Rule Packet",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P75 records a selected compound-condition lowering rule shape without changing compiler behavior.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Lowering rule status: `{summary['loweringRuleStatus']}`",
            f"- Lowering rule scope: `{summary['loweringRuleScope']}`",
            f"- Required helpers: `{summary['requiredHelperCount']}`",
            f"- Semantic requirements: `{summary['semanticRequirementCount']}`",
            f"- Rule validation samples: `{summary['ruleValidationSampleCount']}`",
            f"- Rule validation pass count: `{summary['ruleValidationPassCount']}`",
            f"- Rule validation fail count: `{summary['ruleValidationFailCount']}`",
            f"- Rule validation max absolute error: `{summary['ruleValidationMaxAbsError']}`",
            f"- Compiler behavior changed: `{summary['compilerBehaviorChanged']}`",
            f"- Frontend lowering changed: `{summary['frontendLoweringChanged']}`",
            f"- Compound-condition lowering implemented: `{summary['compoundConditionLoweringImplemented']}`",
            f"- Generated target executed: `{summary['compoundConditionGeneratedTargetExecuted']}`",
            "",
            "## Required Helpers",
            "",
            *helpers,
            "",
            "## Semantic Requirements",
            "",
            *requirements,
            "",
            "## Rule Validation",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Selected lowering-rule packet only.",
            "- No Forge/eFrog behavior change.",
            "- No generated target or re-ingested target execution.",
            "- No compound-condition support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_rule(rule: dict[str, Any]) -> None:
    if rule["status"] != "candidate_rule_recorded_runtime_blocked":
        raise ValueError("lowering rule must remain candidate/runtime-blocked")
    if rule["ruleScope"] != "selected_fixture_only":
        raise ValueError("lowering rule must stay selected-fixture-only")
    if rule["requiredHelpers"] != ["step01", "nonzero01", "guarded_div"]:
        raise ValueError("unexpected helper set")
    if rule["compilerBehaviorChanged"] is not False or rule["frontendLoweringChanged"] is not False:
        raise ValueError("rule packet must not change compiler/frontend behavior")
    if rule["supportClaimAllowed"] is not False:
        raise ValueError("support claim must remain false")


def validate_row(row: dict[str, Any]) -> None:
    if row["loweredRuleValue"] != row["expected"]:
        raise ValueError("lowering rule value must match expected sample")
    if row["absError"] != 0.0 or row["pass"] is not True:
        raise ValueError("lowering rule validation row must pass exactly")
    if row["sourceSemanticsOnly"] is not True:
        raise ValueError("rule validation must remain source-semantics-only")
    if row["path"] == "left_false_short_circuit" and row["rhsEvaluated"] is not False:
        raise ValueError("left-false short circuit must skip rhs")
    if row["path"] == "right_false_zero_denominator_guard" and row["divisionProtected"] is not True:
        raise ValueError("zero-denominator guard must protect division")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P75 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P75 status")
    p74.validate_payload(read_json(P74_RESULT))
    validate_rule(payload["loweringRule"])
    for row in payload["ruleValidationRows"]:
        validate_row(row)
    summary = payload["summary"]
    for key in [
        "p74ValidationPass",
        "p74ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["selectedFixtureId"] != "c_and_short_circuit_guard_v0":
        raise ValueError("unexpected selected fixture")
    if summary["ruleValidationSampleCount"] != 7 or summary["ruleValidationPassCount"] != 7 or summary["ruleValidationFailCount"] != 0:
        raise ValueError("unexpected rule validation counts")
    if summary["ruleValidationMaxAbsError"] != 0.0:
        raise ValueError("unexpected rule validation max error")
    for key in [
        "compilerBehaviorChanged",
        "frontendLoweringChanged",
        "compoundConditionLoweringImplemented",
        "compoundConditionGeneratedTargetExecuted",
        "compoundConditionReingestExecuted",
        "compoundConditionSupportClaim",
        "shortCircuitSemanticsImplemented",
        "guardedDivisionRuntimeHelperImplemented",
        "nonzeroPredicateRuntimeHelperImplemented",
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
    result_path = out_dir / f"fef_p75_compound_condition_lowering_rule_packet_{STAMP}.json"
    report_path = report_dir / f"fef_p75_compound_condition_lowering_rule_packet_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p75_compound_condition_lowering_rule_packet.json"
    feed_path = command_feed_dir / f"fef_p75_compound_condition_lowering_rule_packet_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p75_compound_condition_lowering_rule_packet")
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
    print("FEF_P75_COMPOUND_CONDITION_LOWERING_RULE_PACKET_OK")
    print(f"rule_status={built['payload']['summary']['loweringRuleStatus']}")
    print(f"validation_pass_count={built['payload']['summary']['ruleValidationPassCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
