#!/usr/bin/env python3
"""FEF-P115 policy gate for one compound-condition fixture."""

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

from scripts import fef_p114_compound_condition_expected_samples as p114  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p115_compound_condition_policy_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P115_COMPOUND_CONDITION_POLICY_GATE_PASS"

P114_PACKET = ROOT / "reports/evidence_packets/fef_p114_compound_condition_expected_samples.json"
P114_RESULT = ROOT / "python/results/fef_p114_compound_condition_expected_samples/fef_p114_compound_condition_expected_samples_2026_06_01.json"
SELECTED_FIXTURE_ID = "c_and_guard_return_v0"

CLAIM_FLAGS = {
    "compound_condition_policy_gate_claim": False,
    "compound_condition_runtime_execution_claim": False,
    "compound_condition_lowering_implemented": False,
    "short_circuit_policy_implemented": False,
    "boolean_normalization_policy_implemented": False,
    "predicate_order_policy_implemented": False,
    "compound_condition_support_claim": False,
    "reference_runtime_comparison_claim": False,
    "loop_backedge_support_claim": False,
    "assignment_phi_support_claim": False,
    "side_effect_memory_support_claim": False,
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
    "FEF-P115 records a policy gate for one selected compound-condition fixture only.",
    "FEF-P115 does not execute source, generated, or re-ingested compound-condition code.",
    "FEF-P115 does not implement short-circuit, predicate-order, or boolean-normalization policy.",
    "FEF-P115 does not run a reference runtime comparison.",
    "FEF-P115 does not implement compound-condition lowering.",
    "FEF-P115 does not widen Forge or eFrog frontend lowering.",
    "FEF-P115 does not claim compound-condition support.",
    "FEF-P115 does not record reviewer approval or rejection.",
    "FEF-P115 does not claim general branch/control-flow support.",
    "FEF-P115 does not claim branch/control-flow re-ingest support.",
    "FEF-P115 does not claim full non-generated source roundtrip.",
    "FEF-P115 does not claim arbitrary C/Rust source-family support.",
    "FEF-P115 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P115 does not claim runtime performance, public readiness, package publication, checkout, or production readiness.",
]

POLICY_RULES = [
    {
        "id": "and_left_to_right_short_circuit_v0",
        "policyFamily": "short_circuit",
        "selectedFixture": SELECTED_FIXTURE_ID,
        "operator": "and",
        "requiredOrder": ["evaluate_left_predicate", "evaluate_right_predicate_only_if_left_true", "select_return_path"],
        "appliesToPaths": [
            "left_true_right_true_return_sum",
            "left_true_right_false_return_zero",
            "left_false_short_circuit_return_zero",
        ],
        "status": "specified_not_applied",
        "implementationApplied": False,
    },
    {
        "id": "predicate_truth_table_for_selected_and_v0",
        "policyFamily": "predicate_truth_table",
        "selectedFixture": SELECTED_FIXTURE_ID,
        "leftPredicate": "x > 0.0",
        "rightPredicate": "y > 0.0",
        "truePath": "left_true_right_true_return_sum",
        "falsePaths": ["left_true_right_false_return_zero", "left_false_short_circuit_return_zero"],
        "status": "specified_not_applied",
        "implementationApplied": False,
    },
    {
        "id": "boolean_normalization_preserve_source_order_v0",
        "policyFamily": "boolean_normalization",
        "selectedFixture": SELECTED_FIXTURE_ID,
        "allowedNormalization": "preserve_source_order_and_short_circuit_boundary",
        "disallowedNormalization": "commute_or_eagerly_evaluate_predicates",
        "status": "specified_not_applied",
        "implementationApplied": False,
    },
    {
        "id": "branch_path_return_mapping_v0",
        "policyFamily": "return_path",
        "selectedFixture": SELECTED_FIXTURE_ID,
        "returnMapping": {
            "left_true_right_true_return_sum": "x + y",
            "left_true_right_false_return_zero": "0.0",
            "left_false_short_circuit_return_zero": "0.0",
        },
        "status": "specified_not_applied",
        "implementationApplied": False,
    },
]

RUNTIME_ELIGIBILITY_CHECKS = [
    {"id": "expected_samples_exist", "status": "satisfied_by_p114", "source": "FEF-P114"},
    {"id": "short_circuit_policy_specified", "status": "specified_not_applied", "source": "FEF-P115"},
    {"id": "predicate_truth_policy_specified", "status": "specified_not_applied", "source": "FEF-P115"},
    {"id": "boolean_normalization_policy_specified", "status": "specified_not_applied", "source": "FEF-P115"},
    {"id": "reference_runtime_may_be_next", "status": "eligible_next_gate_only", "source": "FEF-P115"},
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def policy_rows() -> list[dict[str, Any]]:
    return copy.deepcopy(POLICY_RULES)


def runtime_eligibility_checks() -> list[dict[str, Any]]:
    return copy.deepcopy(RUNTIME_ELIGIBILITY_CHECKS)


def build_summary(p114_packet: dict[str, Any], p114_payload: dict[str, Any], rules: list[dict[str, Any]], checks: list[dict[str, Any]]) -> dict[str, Any]:
    samples = p114_payload["expectedSamples"]
    families = {rule["policyFamily"] for rule in rules}
    return {
        "sourcePacketCount": 1,
        "p114ValidationPass": p114_packet["validationStatus"] == "pass",
        "p114ClaimFlagsAllFalse": all(value is False for value in p114_packet["claimFlags"].values()),
        "selectedFixtureId": p114_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p114_payload["summary"]["selectedFixtureStillBlocked"],
        "p114SampleCount": p114_payload["summary"]["sampleCount"],
        "p114RightPredicateEvaluatedCount": p114_payload["summary"]["rightPredicateEvaluatedCount"],
        "p114ShortCircuitExpectedCount": p114_payload["summary"]["shortCircuitExpectedCount"],
        "policyRuleCount": len(rules),
        "policyFamilyCount": len(families),
        "shortCircuitRuleCount": sum(1 for rule in rules if rule["policyFamily"] == "short_circuit"),
        "predicateTruthRuleCount": sum(1 for rule in rules if rule["policyFamily"] == "predicate_truth_table"),
        "booleanNormalizationRuleCount": sum(1 for rule in rules if rule["policyFamily"] == "boolean_normalization"),
        "returnPathRuleCount": sum(1 for rule in rules if rule["policyFamily"] == "return_path"),
        "runtimeEligibilityCheckCount": len(checks),
        "eligibleForReferenceRuntimeNextGate": any(check["id"] == "reference_runtime_may_be_next" and check["status"] == "eligible_next_gate_only" for check in checks),
        "allPoliciesSpecifiedNotApplied": all(rule["status"] == "specified_not_applied" for rule in rules),
        "allPolicyImplementationsNotApplied": all(rule["implementationApplied"] is False for rule in rules),
        "allP114SamplesStillNotExecuted": all(sample["runtimeExecutionPerformed"] is False for sample in samples),
        "allP114SamplesStillNotLowered": all(sample["loweringPerformed"] is False for sample in samples),
        "allP114PoliciesStillNotApplied": all(
            sample["shortCircuitPolicyApplied"] is False
            and sample["booleanNormalizationPolicyApplied"] is False
            for sample in samples
        ),
        "compoundConditionRuntimeExecutionClaim": False,
        "compoundConditionLoweringImplemented": False,
        "shortCircuitPolicyImplemented": False,
        "booleanNormalizationPolicyImplemented": False,
        "predicateOrderPolicyImplemented": False,
        "compoundConditionSupportClaim": False,
        "referenceRuntimeComparisonClaim": False,
        "loopBackedgeSupportClaim": False,
        "assignmentPhiSupportClaim": False,
        "sideEffectMemorySupportClaim": False,
        "nestedBranchSupportClaim": False,
        "controlFlowIrImplemented": False,
        "frontendLoweringChanged": False,
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
    p114_packet = read_json(P114_PACKET)
    p114_payload = read_json(P114_RESULT)
    p114.validate_payload(p114_payload)
    rules = policy_rows()
    checks = runtime_eligibility_checks()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p115-compound-condition-policy-gate",
        "decision": "compound_condition_policy_specified_not_applied_reference_runtime_eligible_next",
        "sourcePacket": {
            "phase": "P114",
            "packetPath": str(P114_PACKET.relative_to(ROOT)),
            "resultPath": str(P114_RESULT.relative_to(ROOT)),
            "reviewDecision": p114_packet["reviewDecision"],
            "validationStatus": p114_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p114_payload["selectedFixture"]),
        "policyRules": rules,
        "runtimeEligibilityChecks": checks,
        "summary": build_summary(p114_packet, p114_payload, rules, checks),
        "releaseGates": [
            {"id": "compound_condition_policy_gate", "status": "recorded"},
            {"id": "short_circuit_policy", "status": "specified_not_applied"},
            {"id": "predicate_truth_policy", "status": "specified_not_applied"},
            {"id": "boolean_normalization_policy", "status": "specified_not_applied"},
            {"id": "reference_runtime_comparison", "status": "eligible_next_gate_only"},
            {"id": "compound_condition_runtime_execution", "status": "not_performed"},
            {"id": "compound_condition_lowering", "status": "blocked"},
            {"id": "compound_condition_support", "status": "blocked"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P115 specifies selected-fixture short-circuit, predicate truth, boolean-normalization, and return-path policies.",
            "The selected compound-condition fixture may move to a reference-runtime comparison gate next, but P115 does not run it.",
            "All compound-condition support, lowering, generated execution, and re-ingest claims remain blocked.",
        ],
        "blockedStatements": [
            "Compound-condition code was executed.",
            "Compound-condition lowering is implemented.",
            "Short-circuit, predicate-order, or boolean-normalization policy was implemented.",
            "A reference runtime comparison was executed.",
            "Compound-condition constructs are supported.",
            "Frontend branch/control-flow lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Run a local reference evaluator for P114 samples under the P115 policy without executing C or generated targets.",
            "Keep generated target execution and re-ingest blocked until compound-condition lowering policy exists.",
            "Record a real private reviewer response if one exists before installing any lowering.",
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
        "title": "FEF-P115 Compound-Condition Policy Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "compound_condition_policy_specified_not_applied",
        "semanticReview": payload["summary"],
        "claimBoundary": "Policy gate only; no compound-condition execution, lowering, implemented short-circuit policy, implemented boolean-normalization policy, support, frontend widening, branch re-ingest, full source roundtrip, arbitrary source-family, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P115 specifies four selected policy rows for c_and_guard_return_v0.",
            "The next eligible gate is a local reference evaluator under specified short-circuit rules.",
            "Policies are specified but not implemented or applied.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p115_compound_condition_policy_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p115_compound_condition_policy_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p115_compound_condition_policy_gate.v0",
        "date": DATE,
        "title": "FEF-P115 Compound-Condition Policy Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Run a local reference evaluator for P114 samples under the specified P115 policy without executing C or generated targets.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Policy | Family | Status | Applied |", "|---|---|---|---|"]
    for rule in payload["policyRules"]:
        rows.append(f"| `{rule['id']}` | `{rule['policyFamily']}` | `{rule['status']}` | `{rule['implementationApplied']}` |")
    return "\n".join(
        [
            "# FEF-P115 Compound-Condition Policy Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P115 specifies selected compound-condition policy while keeping implementation blocked.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- P114 samples: `{summary['p114SampleCount']}`",
            f"- P114 short-circuit expected rows: `{summary['p114ShortCircuitExpectedCount']}`",
            f"- Policy rules: `{summary['policyRuleCount']}`",
            f"- Policy families: `{summary['policyFamilyCount']}`",
            f"- Reference runtime eligible next gate: `{summary['eligibleForReferenceRuntimeNextGate']}`",
            f"- Policies specified not applied: `{summary['allPoliciesSpecifiedNotApplied']}`",
            f"- Policy implementations not applied: `{summary['allPolicyImplementationsNotApplied']}`",
            f"- Compound-condition runtime execution claim: `{summary['compoundConditionRuntimeExecutionClaim']}`",
            f"- Reference runtime comparison claim: `{summary['referenceRuntimeComparisonClaim']}`",
            f"- Compound-condition support claim: `{summary['compoundConditionSupportClaim']}`",
            "",
            "## Policy Rules",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Policy gate only.",
            "- No runtime execution or reference runtime comparison.",
            "- No applied short-circuit, predicate-order, or boolean-normalization policy.",
            "- No compound-condition lowering or support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P115 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P115 status")
    p114.validate_payload(read_json(P114_RESULT))
    summary = payload["summary"]
    for key in [
        "p114ValidationPass",
        "p114ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "eligibleForReferenceRuntimeNextGate",
        "allPoliciesSpecifiedNotApplied",
        "allPolicyImplementationsNotApplied",
        "allP114SamplesStillNotExecuted",
        "allP114SamplesStillNotLowered",
        "allP114PoliciesStillNotApplied",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["selectedFixtureId"] != SELECTED_FIXTURE_ID:
        raise ValueError("unexpected selected fixture")
    if summary["p114SampleCount"] != 7:
        raise ValueError("expected seven P114 samples")
    if summary["p114RightPredicateEvaluatedCount"] != 4 or summary["p114ShortCircuitExpectedCount"] != 3:
        raise ValueError("unexpected P114 short-circuit distribution")
    if summary["policyRuleCount"] != 4 or summary["policyFamilyCount"] != 4:
        raise ValueError("expected four policy rows/families")
    if summary["runtimeEligibilityCheckCount"] != 5:
        raise ValueError("expected five runtime eligibility checks")
    for rule in payload["policyRules"]:
        if rule["status"] != "specified_not_applied":
            raise ValueError("policy rules must remain specified not applied")
        if rule["implementationApplied"] is not False:
            raise ValueError("policy implementation must remain unapplied")
    for key in [
        "compoundConditionRuntimeExecutionClaim",
        "compoundConditionLoweringImplemented",
        "shortCircuitPolicyImplemented",
        "booleanNormalizationPolicyImplemented",
        "predicateOrderPolicyImplemented",
        "compoundConditionSupportClaim",
        "referenceRuntimeComparisonClaim",
        "loopBackedgeSupportClaim",
        "assignmentPhiSupportClaim",
        "sideEffectMemorySupportClaim",
        "nestedBranchSupportClaim",
        "controlFlowIrImplemented",
        "frontendLoweringChanged",
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
    result_path = out_dir / f"fef_p115_compound_condition_policy_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p115_compound_condition_policy_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p115_compound_condition_policy_gate.json"
    feed_path = command_feed_dir / f"fef_p115_compound_condition_policy_gate_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p115_compound_condition_policy_gate")
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
    print("FEF_P115_COMPOUND_CONDITION_POLICY_GATE_OK")
    print(f"rules={built['payload']['summary']['policyRuleCount']}")
    print(f"reference_next={built['payload']['summary']['eligibleForReferenceRuntimeNextGate']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
