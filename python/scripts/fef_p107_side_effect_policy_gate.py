#!/usr/bin/env python3
"""FEF-P107 policy gate for one side-effect/call/memory fixture."""

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

from scripts import fef_p106_side_effect_expected_samples as p106  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p107_side_effect_policy_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P107_SIDE_EFFECT_POLICY_GATE_PASS"

P106_PACKET = ROOT / "reports/evidence_packets/fef_p106_side_effect_expected_samples.json"
P106_RESULT = ROOT / "python/results/fef_p106_side_effect_expected_samples/fef_p106_side_effect_expected_samples_2026_06_01.json"
SELECTED_FIXTURE_ID = "c_global_state_update_v0"

CLAIM_FLAGS = {
    "side_effect_policy_gate_claim": False,
    "side_effect_runtime_execution_claim": False,
    "side_effect_lowering_implemented": False,
    "effect_order_policy_implemented": False,
    "external_call_policy_implemented": False,
    "memory_alias_policy_implemented": False,
    "side_effect_memory_support_claim": False,
    "reference_runtime_comparison_claim": False,
    "loop_backedge_support_claim": False,
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
    "FEF-P107 records a policy gate for one selected side-effect/call/memory fixture only.",
    "FEF-P107 does not execute source, generated, or re-ingested side-effect code.",
    "FEF-P107 does not perform an external call.",
    "FEF-P107 does not write memory or mutate runtime state.",
    "FEF-P107 does not implement effect ordering, external-call, aliasing, or memory-state policy.",
    "FEF-P107 does not run a reference runtime comparison.",
    "FEF-P107 does not implement side-effect/call/memory lowering.",
    "FEF-P107 does not widen Forge or eFrog frontend lowering.",
    "FEF-P107 does not claim side-effect/call/memory support.",
    "FEF-P107 does not claim loop/back-edge, assignment/phi, compound-condition, or nested-branch support.",
    "FEF-P107 does not record reviewer approval or rejection.",
    "FEF-P107 does not claim general branch/control-flow support.",
    "FEF-P107 does not claim branch/control-flow re-ingest support.",
    "FEF-P107 does not claim full non-generated source roundtrip.",
    "FEF-P107 does not claim arbitrary C/Rust source-family support.",
    "FEF-P107 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P107 does not claim runtime performance, public readiness, package publication, checkout, or production readiness.",
]

POLICY_RULES = [
    {
        "id": "effect_order_call_before_write_before_return_v0",
        "policyFamily": "effect_order",
        "selectedFixture": SELECTED_FIXTURE_ID,
        "requiredOrder": ["evaluate_guard", "perform_modeled_call_if_guard_true", "write_modeled_state_if_call_occurs", "return_final_state"],
        "appliesToPaths": ["call_and_state_write", "guard_false_no_call"],
        "status": "specified_not_applied",
        "implementationApplied": False,
    },
    {
        "id": "external_call_return_injection_v0",
        "policyFamily": "external_call",
        "selectedFixture": SELECTED_FIXTURE_ID,
        "allowedExternalSurface": "deterministic_fixture_supplied_return_value_only",
        "disallowedExternalSurface": "live_callback_io_network_time_randomness_or_hidden_state",
        "appliesToPaths": ["call_and_state_write"],
        "status": "specified_not_applied",
        "implementationApplied": False,
    },
    {
        "id": "single_state_cell_no_alias_escape_v0",
        "policyFamily": "memory_alias",
        "selectedFixture": SELECTED_FIXTURE_ID,
        "modeledStateCells": ["state"],
        "aliasAssumption": "the selected fixture models one explicit state cell with no pointer alias escape",
        "appliesToPaths": ["call_and_state_write", "guard_false_no_call"],
        "status": "specified_not_applied",
        "implementationApplied": False,
    },
    {
        "id": "guard_false_no_effect_boundary_v0",
        "policyFamily": "no_effect_path",
        "selectedFixture": SELECTED_FIXTURE_ID,
        "requiredBehavior": "when x <= 0.0, no external call and no state write may be modeled",
        "appliesToPaths": ["guard_false_no_call"],
        "status": "specified_not_applied",
        "implementationApplied": False,
    },
]

RUNTIME_ELIGIBILITY_CHECKS = [
    {
        "id": "expected_samples_exist",
        "status": "satisfied_by_p106",
        "source": "FEF-P106",
    },
    {
        "id": "effect_order_policy_specified",
        "status": "specified_not_applied",
        "source": "FEF-P107",
    },
    {
        "id": "external_call_policy_specified",
        "status": "specified_not_applied",
        "source": "FEF-P107",
    },
    {
        "id": "memory_alias_policy_specified",
        "status": "specified_not_applied",
        "source": "FEF-P107",
    },
    {
        "id": "reference_runtime_may_be_next",
        "status": "eligible_next_gate_only",
        "source": "FEF-P107",
    },
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def policy_rows() -> list[dict[str, Any]]:
    return copy.deepcopy(POLICY_RULES)


def runtime_eligibility_checks() -> list[dict[str, Any]]:
    return copy.deepcopy(RUNTIME_ELIGIBILITY_CHECKS)


def build_summary(p106_packet: dict[str, Any], p106_payload: dict[str, Any], rules: list[dict[str, Any]], checks: list[dict[str, Any]]) -> dict[str, Any]:
    samples = p106_payload["expectedSamples"]
    families = {rule["policyFamily"] for rule in rules}
    return {
        "sourcePacketCount": 1,
        "p106ValidationPass": p106_packet["validationStatus"] == "pass",
        "p106ClaimFlagsAllFalse": all(value is False for value in p106_packet["claimFlags"].values()),
        "selectedFixtureId": p106_payload["summary"]["selectedFixtureId"],
        "selectedFixtureStillBlocked": p106_payload["summary"]["selectedFixtureStillBlocked"],
        "p106SampleCount": p106_payload["summary"]["sampleCount"],
        "p106CallExpectedCount": p106_payload["summary"]["callExpectedCount"],
        "p106GuardFalseNoCallCount": p106_payload["summary"]["guardFalseNoCallCount"],
        "policyRuleCount": len(rules),
        "policyFamilyCount": len(families),
        "effectOrderRuleCount": sum(1 for rule in rules if rule["policyFamily"] == "effect_order"),
        "externalCallRuleCount": sum(1 for rule in rules if rule["policyFamily"] == "external_call"),
        "memoryAliasRuleCount": sum(1 for rule in rules if rule["policyFamily"] == "memory_alias"),
        "noEffectPathRuleCount": sum(1 for rule in rules if rule["policyFamily"] == "no_effect_path"),
        "runtimeEligibilityCheckCount": len(checks),
        "eligibleForReferenceRuntimeNextGate": any(check["id"] == "reference_runtime_may_be_next" and check["status"] == "eligible_next_gate_only" for check in checks),
        "allPoliciesSpecifiedNotApplied": all(rule["status"] == "specified_not_applied" for rule in rules),
        "allPolicyImplementationsNotApplied": all(rule["implementationApplied"] is False for rule in rules),
        "allP106SamplesStillNotExecuted": all(sample["runtimeExecutionPerformed"] is False for sample in samples),
        "allExternalCallsStillNotPerformed": all(sample["externalCallPerformed"] is False for sample in samples),
        "allMemoryWritesStillNotPerformed": all(sample["memoryWritePerformed"] is False for sample in samples),
        "sideEffectRuntimeExecutionClaim": False,
        "sideEffectLoweringImplemented": False,
        "effectOrderPolicyImplemented": False,
        "externalCallPolicyImplemented": False,
        "memoryAliasPolicyImplemented": False,
        "sideEffectMemorySupportClaim": False,
        "referenceRuntimeComparisonClaim": False,
        "loopBackedgeSupportClaim": False,
        "assignmentPhiSupportClaim": False,
        "compoundConditionSupportClaim": False,
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
    p106_packet = read_json(P106_PACKET)
    p106_payload = read_json(P106_RESULT)
    p106.validate_payload(p106_payload)
    rules = policy_rows()
    checks = runtime_eligibility_checks()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p107-side-effect-policy-gate",
        "decision": "side_effect_policy_specified_not_applied_reference_runtime_eligible_next",
        "sourcePacket": {
            "phase": "P106",
            "packetPath": str(P106_PACKET.relative_to(ROOT)),
            "resultPath": str(P106_RESULT.relative_to(ROOT)),
            "reviewDecision": p106_packet["reviewDecision"],
            "validationStatus": p106_packet["validationStatus"],
        },
        "selectedFixture": copy.deepcopy(p106_payload["selectedFixture"]),
        "policyRules": rules,
        "runtimeEligibilityChecks": checks,
        "summary": build_summary(p106_packet, p106_payload, rules, checks),
        "releaseGates": [
            {"id": "side_effect_policy_gate", "status": "recorded"},
            {"id": "effect_order_policy", "status": "specified_not_applied"},
            {"id": "external_call_policy", "status": "specified_not_applied"},
            {"id": "memory_alias_policy", "status": "specified_not_applied"},
            {"id": "reference_runtime_comparison", "status": "eligible_next_gate_only"},
            {"id": "side_effect_runtime_execution", "status": "not_performed"},
            {"id": "external_call_execution", "status": "not_performed"},
            {"id": "memory_write_execution", "status": "not_performed"},
            {"id": "side_effect_lowering", "status": "blocked"},
            {"id": "side_effect_memory_support", "status": "blocked"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P107 specifies selected-fixture effect-order, external-call, memory-alias, and no-effect-path policies.",
            "The selected side-effect fixture may move to a reference-runtime comparison gate next, but P107 does not run it.",
            "All side-effect/call/memory support, lowering, generated execution, and re-ingest claims remain blocked.",
        ],
        "blockedStatements": [
            "Side-effect/call/memory fixtures were executed.",
            "An external call was performed.",
            "Runtime memory or state was mutated.",
            "Effect-order, external-call, or memory-alias policy was implemented.",
            "A reference runtime comparison was executed.",
            "Side-effect/call/memory lowering is implemented.",
            "Side-effecting calls or memory operations are supported.",
            "Frontend branch/control-flow lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Run a local reference evaluator for P106 samples under the P107 policy without live external calls.",
            "Keep generated target execution and re-ingest blocked until side-effect lowering policy exists.",
            "Record a real private reviewer response if one exists before installing any adapter or lowering.",
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
        "title": "FEF-P107 Side-Effect Policy Gate",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "side_effect_policy_specified_not_applied",
        "semanticReview": payload["summary"],
        "claimBoundary": "Policy gate only; no side-effect execution, external call, memory write, lowering, implemented effect policy, support, frontend widening, branch re-ingest, full source roundtrip, arbitrary source-family, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P107 specifies four selected policy rows for c_global_state_update_v0.",
            "The next eligible gate is a local reference evaluator under deterministic injected call returns.",
            "Policies are specified but not implemented or applied.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p107_side_effect_policy_gate.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p107_side_effect_policy_gate.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p107_side_effect_policy_gate.v0",
        "date": DATE,
        "title": "FEF-P107 Side-Effect Policy Gate",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Run a local reference evaluator for P106 samples under the specified P107 policy without live external calls.",
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
            "# FEF-P107 Side-Effect Policy Gate",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P107 specifies selected-fixture side-effect policy without applying it.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- P106 sample count: `{summary['p106SampleCount']}`",
            f"- Policy rule count: `{summary['policyRuleCount']}`",
            f"- Policy family count: `{summary['policyFamilyCount']}`",
            f"- Runtime eligibility checks: `{summary['runtimeEligibilityCheckCount']}`",
            f"- Eligible for reference runtime next gate: `{summary['eligibleForReferenceRuntimeNextGate']}`",
            f"- Policies specified not applied: `{summary['allPoliciesSpecifiedNotApplied']}`",
            f"- Runtime execution performed: `{summary['sideEffectRuntimeExecutionClaim']}`",
            f"- Reference runtime comparison performed: `{summary['referenceRuntimeComparisonClaim']}`",
            "",
            "## Policy Rows",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Policy gate only.",
            "- No external calls performed.",
            "- No runtime memory writes or state mutation.",
            "- No effect-order, external-call, or memory-alias implementation.",
            "- No reference runtime comparison.",
            "- No side-effect/call/memory support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P107 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P107 status")
    p106.validate_payload(read_json(P106_RESULT))
    summary = payload["summary"]
    for key in [
        "p106ValidationPass",
        "p106ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "allPoliciesSpecifiedNotApplied",
        "allPolicyImplementationsNotApplied",
        "allP106SamplesStillNotExecuted",
        "allExternalCallsStillNotPerformed",
        "allMemoryWritesStillNotPerformed",
        "eligibleForReferenceRuntimeNextGate",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["selectedFixtureId"] != SELECTED_FIXTURE_ID:
        raise ValueError("unexpected selected fixture")
    if summary["policyRuleCount"] != 4:
        raise ValueError("expected four policy rows")
    if summary["policyFamilyCount"] != 4:
        raise ValueError("expected four policy families")
    if summary["runtimeEligibilityCheckCount"] != 5:
        raise ValueError("expected five runtime eligibility checks")
    for key in [
        "sideEffectRuntimeExecutionClaim",
        "sideEffectLoweringImplemented",
        "effectOrderPolicyImplemented",
        "externalCallPolicyImplemented",
        "memoryAliasPolicyImplemented",
        "sideEffectMemorySupportClaim",
        "referenceRuntimeComparisonClaim",
        "loopBackedgeSupportClaim",
        "assignmentPhiSupportClaim",
        "compoundConditionSupportClaim",
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
    result_path = out_dir / f"fef_p107_side_effect_policy_gate_{STAMP}.json"
    report_path = report_dir / f"fef_p107_side_effect_policy_gate_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p107_side_effect_policy_gate.json"
    feed_path = command_feed_dir / f"fef_p107_side_effect_policy_gate_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p107_side_effect_policy_gate")
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
    print("FEF_P107_SIDE_EFFECT_POLICY_GATE_OK")
    print(f"policy_rules={built['payload']['summary']['policyRuleCount']}")
    print(f"eligible_next={built['payload']['summary']['eligibleForReferenceRuntimeNextGate']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
