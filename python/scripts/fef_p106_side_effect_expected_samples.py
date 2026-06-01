#!/usr/bin/env python3
"""FEF-P106 expected samples for one side-effect/call/memory fixture."""

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

from scripts import fef_p105_side_effect_memory_fixture_gate as p105  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p106_side_effect_expected_samples.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P106_SIDE_EFFECT_EXPECTED_SAMPLES_PASS"

P105_PACKET = ROOT / "reports/evidence_packets/fef_p105_side_effect_memory_fixture_gate.json"
P105_RESULT = ROOT / "python/results/fef_p105_side_effect_memory_fixture_gate/fef_p105_side_effect_memory_fixture_gate_2026_06_01.json"
SELECTED_FIXTURE_ID = "c_global_state_update_v0"

CLAIM_FLAGS = {
    "side_effect_expected_samples_claim": False,
    "side_effect_runtime_execution_claim": False,
    "side_effect_lowering_implemented": False,
    "effect_order_policy_implemented": False,
    "external_call_policy_implemented": False,
    "memory_alias_policy_implemented": False,
    "side_effect_memory_support_claim": False,
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
    "FEF-P106 records deterministic expected samples for one side-effect/call/memory fixture only.",
    "FEF-P106 does not execute source, generated, or re-ingested side-effect code.",
    "FEF-P106 does not perform an external call.",
    "FEF-P106 does not write memory or mutate runtime state.",
    "FEF-P106 does not implement effect ordering, external-call, aliasing, or memory-state policy.",
    "FEF-P106 does not implement side-effect/call/memory lowering.",
    "FEF-P106 does not widen Forge or eFrog frontend lowering.",
    "FEF-P106 does not claim side-effect/call/memory support.",
    "FEF-P106 does not claim loop/back-edge, assignment/phi, compound-condition, or nested-branch support.",
    "FEF-P106 does not record reviewer approval or rejection.",
    "FEF-P106 does not claim general branch/control-flow support.",
    "FEF-P106 does not claim branch/control-flow re-ingest support.",
    "FEF-P106 does not claim full non-generated source roundtrip.",
    "FEF-P106 does not claim arbitrary C/Rust source-family support.",
    "FEF-P106 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P106 does not claim runtime performance, public readiness, package publication, checkout, or production readiness.",
]

SAMPLE_INPUTS = [
    {"x": -2.0, "initialState": 5.0, "externalCallReturn": None},
    {"x": 0.0, "initialState": -1.0, "externalCallReturn": None},
    {"x": 0.25, "initialState": 3.0, "externalCallReturn": 1.5},
    {"x": 1.0, "initialState": 0.0, "externalCallReturn": 4.0},
    {"x": 2.5, "initialState": -4.0, "externalCallReturn": 8.0},
    {"x": -0.5, "initialState": 9.0, "externalCallReturn": None},
    {"x": 10.0, "initialState": 1.0, "externalCallReturn": 21.0},
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def call_would_execute(x: float) -> bool:
    return x > 0.0


def expected_state_after_sample(sample: dict[str, Any]) -> float:
    if call_would_execute(float(sample["x"])):
        return float(sample["externalCallReturn"])
    return float(sample["initialState"])


def path_for_sample(sample: dict[str, Any]) -> str:
    return "call_and_state_write" if call_would_execute(float(sample["x"])) else "guard_false_no_call"


def expected_samples() -> list[dict[str, Any]]:
    samples = []
    for index, inputs in enumerate(SAMPLE_INPUTS):
        call_expected = call_would_execute(float(inputs["x"]))
        expected_state = expected_state_after_sample(inputs)
        samples.append(
            {
                "sampleId": f"sample_{index:02d}",
                "inputs": dict(inputs),
                "path": path_for_sample(inputs),
                "callExpected": call_expected,
                "stateWriteExpected": call_expected,
                "expectedFinalState": expected_state,
                "expectedReturn": expected_state,
                "sourceSemanticsOnly": True,
                "runtimeExecutionPerformed": False,
                "externalCallPerformed": False,
                "memoryWritePerformed": False,
                "effectOrderPolicyApplied": False,
                "externalCallPolicyApplied": False,
                "memoryAliasPolicyApplied": False,
            }
        )
    return samples


def selected_fixture(p105_result: dict[str, Any]) -> dict[str, Any]:
    for row in p105_result["sideEffectMemoryFixtures"]:
        if row["id"] == SELECTED_FIXTURE_ID:
            return copy.deepcopy(row)
    raise ValueError(f"missing selected fixture: {SELECTED_FIXTURE_ID}")


def build_summary(p105_packet: dict[str, Any], fixture: dict[str, Any], samples: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p105ValidationPass": p105_packet["validationStatus"] == "pass",
        "p105ClaimFlagsAllFalse": all(value is False for value in p105_packet["claimFlags"].values()),
        "selectedFixtureId": fixture["id"],
        "selectedFixtureStatus": fixture["status"],
        "selectedFixtureStillBlocked": fixture["status"] == "blocked_fixture_defined",
        "sampleCount": len(samples),
        "callExpectedCount": sum(1 for sample in samples if sample["callExpected"]),
        "guardFalseNoCallCount": sum(1 for sample in samples if not sample["callExpected"]),
        "stateWriteExpectedCount": sum(1 for sample in samples if sample["stateWriteExpected"]),
        "effectBoundaryExpectedCount": sum(
            (1 if sample["callExpected"] else 0) + (1 if sample["stateWriteExpected"] else 0)
            for sample in samples
        ),
        "allSamplesSourceSemanticsOnly": all(sample["sourceSemanticsOnly"] is True for sample in samples),
        "allRuntimeExecutionNotPerformed": all(sample["runtimeExecutionPerformed"] is False for sample in samples),
        "allExternalCallsNotPerformed": all(sample["externalCallPerformed"] is False for sample in samples),
        "allMemoryWritesNotPerformed": all(sample["memoryWritePerformed"] is False for sample in samples),
        "allEffectPoliciesNotApplied": all(
            sample["effectOrderPolicyApplied"] is False
            and sample["externalCallPolicyApplied"] is False
            and sample["memoryAliasPolicyApplied"] is False
            for sample in samples
        ),
        "sideEffectRuntimeExecutionClaim": False,
        "sideEffectLoweringImplemented": False,
        "effectOrderPolicyImplemented": False,
        "externalCallPolicyImplemented": False,
        "memoryAliasPolicyImplemented": False,
        "sideEffectMemorySupportClaim": False,
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
    p105_packet = read_json(P105_PACKET)
    p105_result = read_json(P105_RESULT)
    p105.validate_payload(p105_result)
    fixture = selected_fixture(p105_result)
    samples = expected_samples()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p106-side-effect-expected-samples",
        "decision": "side_effect_expected_samples_recorded_support_blocked",
        "sourcePacket": {
            "phase": "P105",
            "packetPath": str(P105_PACKET.relative_to(ROOT)),
            "resultPath": str(P105_RESULT.relative_to(ROOT)),
            "reviewDecision": p105_packet["reviewDecision"],
            "validationStatus": p105_packet["validationStatus"],
        },
        "selectedFixture": fixture,
        "expectedSamples": samples,
        "summary": build_summary(p105_packet, fixture, samples),
        "releaseGates": [
            {"id": "side_effect_expected_samples", "status": "recorded"},
            {"id": "side_effect_runtime_execution", "status": "not_performed"},
            {"id": "external_call_execution", "status": "not_performed"},
            {"id": "memory_write_execution", "status": "not_performed"},
            {"id": "side_effect_lowering", "status": "blocked"},
            {"id": "effect_order_policy", "status": "not_applied"},
            {"id": "external_call_policy", "status": "not_applied"},
            {"id": "memory_alias_policy", "status": "not_applied"},
            {"id": "side_effect_memory_support", "status": "blocked"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P106 records deterministic expected samples for one blocked side-effect/call/memory fixture.",
            "The selected fixture remains blocked pending effect-order, external-call, memory-alias, runtime, lowering, and re-ingest validators.",
            "P106 defines expected source semantics without executing an external call or mutating runtime state.",
        ],
        "blockedStatements": [
            "Side-effect/call/memory fixtures were executed.",
            "An external call was performed.",
            "Runtime memory or state was mutated.",
            "Effect-order, external-call, or memory-alias policy was applied.",
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
            "Define an effect-order and external-call policy before executing side-effect samples.",
            "Turn the selected expected-sample fixture into a reference runtime comparison gate only after policy exists.",
            "Keep side-effect/call/memory support blocked until lowering and re-ingest evidence exists.",
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
        "title": "FEF-P106 Side-Effect Expected Samples",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "side_effect_expected_samples_recorded_support_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Expected-sample fixture only; no side-effect execution, external call, memory write, lowering, effect policy, support, frontend widening, branch re-ingest, full source roundtrip, arbitrary source-family, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P106 records deterministic expected samples for c_global_state_update_v0.",
            "Samples define call/write expectations without executing calls or mutating state.",
            "Side-effect/call/memory support remains blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p106_side_effect_expected_samples.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p106_side_effect_expected_samples.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p106_side_effect_expected_samples.v0",
        "date": DATE,
        "title": "FEF-P106 Side-Effect Expected Samples",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Define an effect-order/external-call policy before executing side-effect samples.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Sample | x | initial state | call expected | expected return |", "|---|---:|---:|---|---:|"]
    for sample in payload["expectedSamples"]:
        rows.append(
            f"| `{sample['sampleId']}` | `{sample['inputs']['x']}` | `{sample['inputs']['initialState']}` | "
            f"`{sample['callExpected']}` | `{sample['expectedReturn']}` |"
        )
    return "\n".join(
        [
            "# FEF-P106 Side-Effect Expected Samples",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P106 records source-semantics-only expected samples for one side-effect fixture.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Sample count: `{summary['sampleCount']}`",
            f"- Call expected count: `{summary['callExpectedCount']}`",
            f"- Guard-false no-call count: `{summary['guardFalseNoCallCount']}`",
            f"- State write expected count: `{summary['stateWriteExpectedCount']}`",
            f"- Effect boundary expected count: `{summary['effectBoundaryExpectedCount']}`",
            f"- Runtime execution performed: `{summary['sideEffectRuntimeExecutionClaim']}`",
            f"- External calls performed: `{summary['allExternalCallsNotPerformed'] is False}`",
            f"- Memory writes performed: `{summary['allMemoryWritesNotPerformed'] is False}`",
            f"- Effect policies applied: `{summary['allEffectPoliciesNotApplied'] is False}`",
            "",
            "## Samples",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Expected samples only.",
            "- No external calls performed.",
            "- No runtime memory writes or state mutation.",
            "- No effect-order, external-call, or memory-alias policy.",
            "- No side-effect/call/memory support claim.",
            "- No compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P106 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P106 status")
    p105.validate_payload(read_json(P105_RESULT))
    summary = payload["summary"]
    for key in [
        "p105ValidationPass",
        "p105ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "allSamplesSourceSemanticsOnly",
        "allRuntimeExecutionNotPerformed",
        "allExternalCallsNotPerformed",
        "allMemoryWritesNotPerformed",
        "allEffectPoliciesNotApplied",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["sampleCount"] != 7:
        raise ValueError("expected seven samples")
    if summary["callExpectedCount"] != 4:
        raise ValueError("expected four call-expected samples")
    if summary["guardFalseNoCallCount"] != 3:
        raise ValueError("expected three guard-false no-call samples")
    if summary["stateWriteExpectedCount"] != 4:
        raise ValueError("expected four state-write expected samples")
    if summary["effectBoundaryExpectedCount"] != 8:
        raise ValueError("expected eight expected effect boundaries")
    for sample in payload["expectedSamples"]:
        if sample["runtimeExecutionPerformed"] is not False:
            raise ValueError("runtime execution must remain false")
        if sample["externalCallPerformed"] is not False:
            raise ValueError("external calls must not be performed")
        if sample["memoryWritePerformed"] is not False:
            raise ValueError("memory writes must not be performed")
    for key in [
        "sideEffectRuntimeExecutionClaim",
        "sideEffectLoweringImplemented",
        "effectOrderPolicyImplemented",
        "externalCallPolicyImplemented",
        "memoryAliasPolicyImplemented",
        "sideEffectMemorySupportClaim",
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
    result_path = out_dir / f"fef_p106_side_effect_expected_samples_{STAMP}.json"
    report_path = report_dir / f"fef_p106_side_effect_expected_samples_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p106_side_effect_expected_samples.json"
    feed_path = command_feed_dir / f"fef_p106_side_effect_expected_samples_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p106_side_effect_expected_samples")
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
    print("FEF_P106_SIDE_EFFECT_EXPECTED_SAMPLES_OK")
    print(f"samples={built['payload']['summary']['sampleCount']}")
    print(f"call_expected={built['payload']['summary']['callExpectedCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
