#!/usr/bin/env python3
"""FEF-P96 selected loop lowering rule packet."""

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

from scripts import fef_p95_loop_generated_target_runtime_blocker as p95  # noqa: E402

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p96_loop_lowering_rule_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P96_LOOP_LOWERING_RULE_PACKET_PASS"

P95_PACKET = ROOT / "reports/evidence_packets/fef_p95_loop_generated_target_runtime_blocker.json"
P95_RESULT = ROOT / "python/results/fef_p95_loop_generated_target_runtime_blocker/fef_p95_loop_generated_target_runtime_blocker_2026_05_31.json"

CLAIM_FLAGS = {
    "loop_lowering_rule_packet_claim": False,
    "loop_lowering_implemented": False,
    "loop_generated_target_execution_claim": False,
    "loop_reingest_execution_claim": False,
    "loop_backedge_support_claim": False,
    "loop_backedge_semantics_implemented": False,
    "loop_boundedness_policy_general_claim": False,
    "assignment_phi_support_claim": False,
    "compound_condition_support_claim": False,
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
    "implementation_change_approved": False,
    "implementation_change_applied": False,
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
    "FEF-P96 records a selected loop lowering rule packet only.",
    "FEF-P96 does not change Forge or eFrog lowering behavior.",
    "FEF-P96 does not execute generated target code.",
    "FEF-P96 does not execute re-ingested code.",
    "FEF-P96 does not implement loop headers, latches, variants, or back-edge semantics in Forge or eFrog.",
    "FEF-P96 does not implement a general loop boundedness policy.",
    "FEF-P96 does not claim loop/back-edge support.",
    "FEF-P96 does not claim assignment/phi, compound-condition, or nested-branch support.",
    "FEF-P96 does not claim general branch/control-flow support.",
    "FEF-P96 does not claim branch/control-flow re-ingest support.",
    "FEF-P96 does not claim full non-generated source roundtrip.",
    "FEF-P96 does not claim arbitrary C/Rust source-family support.",
    "FEF-P96 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P96 does not claim runtime performance.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def lowering_rule() -> dict[str, Any]:
    return {
        "ruleId": "selected_c_while_accumulate_lowering_v0",
        "selectedFixtureId": "c_while_accumulate_v0",
        "sourcePattern": "double acc = 0.0; int i = 0; while (i < n) { acc = acc + x; i = i + 1; } return acc;",
        "status": "candidate_rule_recorded_runtime_blocked",
        "ruleScope": "selected_fixture_only_under_p92_policy",
        "loopShape": {
            "kind": "while",
            "init": ["acc = 0.0", "i = 0"],
            "condition": "i < n",
            "body": ["acc = acc + x", "i = i + 1"],
            "exit": "return acc",
        },
        "boundednessPrecondition": {
            "policyId": "selected_c_while_accumulate_boundedness_policy_v0",
            "effectiveIterationDefinition": "max(0, int(n))",
            "maxEffectiveIterationCount": 16,
            "requiresPolicyEligibleSample": True,
        },
        "candidateLowering": {
            "effectiveIterationBinding": "k = max(0, int(n))",
            "loweredValue": "x * k",
            "kind": "bounded_counted_accumulator_to_affine_multiply",
        },
        "semanticRequirements": [
            "loop bound n is integer-like for the selected fixture samples",
            "effective iteration count is max(0, int(n))",
            "effective iteration count is bounded by the P92 cap",
            "loop body has no side effects outside local acc/i mutation",
            "accumulator update is affine: acc_next = acc + x",
        ],
        "rejectedSurfaces": [
            "unknown_or_symbolic_loop_bound",
            "iteration_count_above_limit",
            "non_finite_numeric_input",
            "side_effecting_loop_body",
            "nested_or_unstructured_loop",
        ],
        "generatedTargetRuntimeStatusAfterRule": "blocked_until_codegen_fixture_exists",
        "compilerBehaviorChanged": False,
        "frontendLoweringChanged": False,
        "supportClaimAllowed": False,
    }


def evaluate_rule_for_sample(sample: dict[str, Any]) -> dict[str, Any]:
    x = float(sample["inputs"]["x"])
    n = int(sample["inputs"]["n"])
    effective_iterations = int(sample["policyEffectiveIterationCount"])
    lowered_value = x * effective_iterations
    expected = float(sample["expected"])
    return {
        "sampleId": sample["sampleId"],
        "inputs": copy.deepcopy(sample["inputs"]),
        "expected": expected,
        "loweredRuleValue": lowered_value,
        "absError": abs(lowered_value - expected),
        "pass": lowered_value == expected,
        "effectiveIterationCount": effective_iterations,
        "originalN": n,
        "path": sample["path"],
        "sourceSemanticsOnly": True,
        "generatedTargetExecuted": False,
        "reingestedTargetExecuted": False,
    }


def rule_validation_rows(p95_payload: dict[str, Any]) -> list[dict[str, Any]]:
    p94_result = read_json(ROOT / p95_payload["sourcePacket"]["resultPath"])
    return [evaluate_rule_for_sample(row) for row in p94_result["runtimeComparison"]["rows"]]


def build_summary(p95_packet: dict[str, Any], p95_payload: dict[str, Any], rule: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p95ValidationPass": p95_packet["validationStatus"] == "pass",
        "p95ClaimFlagsAllFalse": all(value is False for value in p95_packet["claimFlags"].values()),
        "selectedFixtureId": p95_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p95_payload["summary"]["selectedFixtureStillBlocked"],
        "loweringRuleStatus": rule["status"],
        "loweringRuleScope": rule["ruleScope"],
        "semanticRequirementCount": len(rule["semanticRequirements"]),
        "rejectedSurfaceCount": len(rule["rejectedSurfaces"]),
        "ruleValidationSampleCount": len(rows),
        "ruleValidationPassCount": sum(1 for row in rows if row["pass"]),
        "ruleValidationFailCount": sum(1 for row in rows if not row["pass"]),
        "ruleValidationMaxAbsError": max(row["absError"] for row in rows),
        "zeroIterationCount": sum(1 for row in rows if row["effectiveIterationCount"] == 0),
        "singleIterationCount": sum(1 for row in rows if row["effectiveIterationCount"] == 1),
        "multiIterationCount": sum(1 for row in rows if row["effectiveIterationCount"] > 1),
        "maxEffectiveIterationCount": max(row["effectiveIterationCount"] for row in rows),
        "generatedTargetRuntimeStatusAfterRule": rule["generatedTargetRuntimeStatusAfterRule"],
        "compilerBehaviorChanged": False,
        "frontendLoweringChanged": False,
        "loopLoweringImplemented": False,
        "loopGeneratedTargetExecuted": False,
        "loopReingestExecuted": False,
        "loopBackedgeSupportClaim": False,
        "loopBackedgeSemanticsImplemented": False,
        "loopBoundednessPolicyGeneralClaim": False,
        "assignmentPhiSupportClaim": False,
        "compoundConditionSupportClaim": False,
        "nestedBranchSupportClaim": False,
        "controlFlowIrImplemented": False,
        "unsupportedConstructsSupported": False,
        "generalBranchControlFlowClaim": False,
        "branchControlFlowReingestClaim": False,
        "fullNonGeneratedSourceRoundtripClaim": False,
        "fullCRustRoundtripClaim": False,
        "arbitrarySourceFamilyClaim": False,
        "reviewerDecisionRecorded": False,
        "implementationChangeApproved": False,
        "implementationChangeApplied": False,
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
    p95_packet = read_json(P95_PACKET)
    p95_payload = read_json(P95_RESULT)
    p95.validate_payload(p95_payload)
    rule = lowering_rule()
    rows = rule_validation_rows(p95_payload)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p96-loop-lowering-rule-packet",
        "decision": "selected_loop_lowering_rule_recorded_runtime_blocked",
        "sourcePacket": {
            "phase": "P95",
            "packetPath": str(P95_PACKET.relative_to(ROOT)),
            "resultPath": str(P95_RESULT.relative_to(ROOT)),
            "reviewDecision": p95_packet["reviewDecision"],
            "validationStatus": p95_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p95_payload["selectedFixture"]),
        "loweringRule": rule,
        "ruleValidationRows": rows,
        "summary": build_summary(p95_packet, p95_payload, rule, rows),
        "releaseGates": [
            {"id": "selected_loop_lowering_rule", "status": "recorded_runtime_blocked"},
            {"id": "generated_target_runtime_execution", "status": "blocked_not_run"},
            {"id": "loop_reingest_execution", "status": "not_performed"},
            {"id": "loop_backedge_support", "status": "blocked"},
            {"id": "loop_backedge_semantics_implementation", "status": "not_performed"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P96 records a selected loop lowering rule shape for review.",
            "The rule validates against the existing seven selected loop samples.",
            "P96 does not change Forge/eFrog behavior and generated-target runtime remains blocked.",
        ],
        "blockedStatements": [
            "Loop lowering is implemented in Forge or eFrog.",
            "Generated loop target code was executed.",
            "Re-ingested loop code was executed.",
            "Loop header, latch, variant, or back-edge semantics are implemented in Forge or eFrog.",
            "Loop/back-edge constructs are supported.",
            "The P92 boundedness policy is a general loop policy.",
            "Frontend branch lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Record a selected loop codegen fixture before generated-target runtime execution.",
            "Record private reviewer response to the P47-P96 branch/control-flow bundle.",
            "Keep loop/back-edge support blocked until generated-target and re-ingest evidence exist.",
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
        "title": "FEF-P96 Loop Lowering Rule Packet",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_loop_lowering_rule_recorded_runtime_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Selected loop lowering-rule packet only; no Forge/eFrog behavior change, generated target execution, re-ingest execution, loop/back-edge support, frontend widening, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P96 records a selected bounded accumulator loop lowering rule shape.",
            "The rule validates against seven existing selected loop samples.",
            "Generated-target runtime remains blocked until a codegen fixture exists.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p96_loop_lowering_rule_packet.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p96_loop_lowering_rule_packet.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p96_loop_lowering_rule_packet.v0",
        "date": DATE,
        "title": "FEF-P96 Loop Lowering Rule Packet",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Record a selected loop codegen fixture before generated-target runtime execution.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Sample | Path | Effective Iterations | Expected | Rule Value | Abs Error | Pass |", "|---|---|---:|---:|---:|---:|---|"]
    for row in payload["ruleValidationRows"]:
        rows.append(
            f"| `{row['sampleId']}` | `{row['path']}` | {row['effectiveIterationCount']} | {row['expected']} | {row['loweredRuleValue']} | {row['absError']} | `{row['pass']}` |"
        )
    requirements = [f"- {item}" for item in payload["loweringRule"]["semanticRequirements"]]
    rejected = [f"- `{item}`" for item in payload["loweringRule"]["rejectedSurfaces"]]
    return "\n".join(
        [
            "# FEF-P96 Loop Lowering Rule Packet",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P96 records a selected loop lowering rule shape without changing compiler behavior.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Lowering rule status: `{summary['loweringRuleStatus']}`",
            f"- Lowering rule scope: `{summary['loweringRuleScope']}`",
            f"- Semantic requirements: `{summary['semanticRequirementCount']}`",
            f"- Rejected surfaces: `{summary['rejectedSurfaceCount']}`",
            f"- Rule validation samples: `{summary['ruleValidationSampleCount']}`",
            f"- Rule validation pass count: `{summary['ruleValidationPassCount']}`",
            f"- Rule validation fail count: `{summary['ruleValidationFailCount']}`",
            f"- Rule validation max absolute error: `{summary['ruleValidationMaxAbsError']}`",
            f"- Max effective iteration count: `{summary['maxEffectiveIterationCount']}`",
            f"- Compiler behavior changed: `{summary['compilerBehaviorChanged']}`",
            f"- Frontend lowering changed: `{summary['frontendLoweringChanged']}`",
            f"- Loop lowering implemented: `{summary['loopLoweringImplemented']}`",
            f"- Generated target executed: `{summary['loopGeneratedTargetExecuted']}`",
            "",
            "## Semantic Requirements",
            "",
            *requirements,
            "",
            "## Rejected Surfaces",
            "",
            *rejected,
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
            "- No loop/back-edge support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_rule(rule: dict[str, Any]) -> None:
    if rule["status"] != "candidate_rule_recorded_runtime_blocked":
        raise ValueError("lowering rule must remain candidate/runtime-blocked")
    if rule["ruleScope"] != "selected_fixture_only_under_p92_policy":
        raise ValueError("lowering rule must stay selected-fixture scoped")
    if rule["candidateLowering"]["loweredValue"] != "x * k":
        raise ValueError("unexpected selected lowered value")
    if rule["boundednessPrecondition"]["maxEffectiveIterationCount"] != 16:
        raise ValueError("unexpected boundedness cap")
    if rule["compilerBehaviorChanged"] is not False or rule["frontendLoweringChanged"] is not False:
        raise ValueError("compiler/frontend behavior must remain unchanged")
    if rule["supportClaimAllowed"] is not False:
        raise ValueError("support claim must remain false")


def validate_row(row: dict[str, Any]) -> None:
    if row["loweredRuleValue"] != row["expected"]:
        raise ValueError("lowered rule value must match expected")
    if row["absError"] != abs(row["loweredRuleValue"] - row["expected"]):
        raise ValueError("absolute error mismatch")
    if row["absError"] != 0.0 or row["pass"] is not True:
        raise ValueError("selected rows must pass with zero error")
    if row["effectiveIterationCount"] != max(0, int(row["inputs"]["n"])):
        raise ValueError("effective iteration count mismatch")
    if row["generatedTargetExecuted"] is not False or row["reingestedTargetExecuted"] is not False:
        raise ValueError("generated and re-ingested execution must remain false")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P96 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P96 status")
    p95.validate_payload(read_json(P95_RESULT))
    validate_rule(payload["loweringRule"])
    for row in payload["ruleValidationRows"]:
        validate_row(row)
    summary = payload["summary"]
    for key in [
        "p95ValidationPass",
        "p95ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["selectedFixtureId"] != "c_while_accumulate_v0":
        raise ValueError("unexpected selected fixture")
    if summary["ruleValidationSampleCount"] != 7 or summary["ruleValidationPassCount"] != 7:
        raise ValueError("expected seven passing rule validation samples")
    if summary["ruleValidationFailCount"] != 0 or summary["ruleValidationMaxAbsError"] != 0.0:
        raise ValueError("expected zero rule validation error")
    if summary["zeroIterationCount"] != 2 or summary["singleIterationCount"] != 1 or summary["multiIterationCount"] != 4:
        raise ValueError("unexpected iteration distribution")
    if summary["maxEffectiveIterationCount"] != 8:
        raise ValueError("unexpected max effective iteration count")
    for key in [
        "compilerBehaviorChanged",
        "frontendLoweringChanged",
        "loopLoweringImplemented",
        "loopGeneratedTargetExecuted",
        "loopReingestExecuted",
        "loopBackedgeSupportClaim",
        "loopBackedgeSemanticsImplemented",
        "loopBoundednessPolicyGeneralClaim",
        "assignmentPhiSupportClaim",
        "compoundConditionSupportClaim",
        "nestedBranchSupportClaim",
        "controlFlowIrImplemented",
        "unsupportedConstructsSupported",
        "generalBranchControlFlowClaim",
        "branchControlFlowReingestClaim",
        "fullNonGeneratedSourceRoundtripClaim",
        "fullCRustRoundtripClaim",
        "arbitrarySourceFamilyClaim",
        "reviewerDecisionRecorded",
        "implementationChangeApproved",
        "implementationChangeApplied",
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
    result_path = out_dir / f"fef_p96_loop_lowering_rule_packet_{STAMP}.json"
    report_path = report_dir / f"fef_p96_loop_lowering_rule_packet_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p96_loop_lowering_rule_packet.json"
    feed_path = command_feed_dir / f"fef_p96_loop_lowering_rule_packet_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p96_loop_lowering_rule_packet")
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
    print("FEF_P96_LOOP_LOWERING_RULE_PACKET_OK")
    print(f"pass_count={built['payload']['summary']['ruleValidationPassCount']}")
    print(f"max_abs_error={built['payload']['summary']['ruleValidationMaxAbsError']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
