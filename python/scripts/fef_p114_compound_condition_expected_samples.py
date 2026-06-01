#!/usr/bin/env python3
"""FEF-P114 expected samples for one compound-condition fixture."""

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

from scripts import fef_p113_compound_condition_fixture_gate as p113  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p114_compound_condition_expected_samples.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P114_COMPOUND_CONDITION_EXPECTED_SAMPLES_PASS"

P113_PACKET = ROOT / "reports/evidence_packets/fef_p113_compound_condition_fixture_gate.json"
P113_RESULT = ROOT / "python/results/fef_p113_compound_condition_fixture_gate/fef_p113_compound_condition_fixture_gate_2026_06_01.json"
SELECTED_FIXTURE_ID = "c_and_guard_return_v0"

CLAIM_FLAGS = {
    "compound_condition_expected_samples_claim": False,
    "compound_condition_runtime_execution_claim": False,
    "compound_condition_lowering_implemented": False,
    "short_circuit_policy_implemented": False,
    "boolean_normalization_policy_implemented": False,
    "compound_condition_support_claim": False,
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
    "FEF-P114 records deterministic expected samples for one compound-condition fixture only.",
    "FEF-P114 does not execute source, generated, or re-ingested compound-condition code.",
    "FEF-P114 does not implement short-circuit or boolean-normalization policy.",
    "FEF-P114 does not implement compound-condition lowering.",
    "FEF-P114 does not widen Forge or eFrog frontend lowering.",
    "FEF-P114 does not claim compound-condition support.",
    "FEF-P114 does not record reviewer approval or rejection.",
    "FEF-P114 does not claim general branch/control-flow support.",
    "FEF-P114 does not claim branch/control-flow re-ingest support.",
    "FEF-P114 does not claim full non-generated source roundtrip.",
    "FEF-P114 does not claim arbitrary C/Rust source-family support.",
    "FEF-P114 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P114 does not claim runtime performance, public readiness, package publication, checkout, or production readiness.",
]

SAMPLE_INPUTS = [
    {"x": 2.0, "y": 3.0},
    {"x": 2.0, "y": -1.0},
    {"x": -2.0, "y": 3.0},
    {"x": 0.0, "y": 3.0},
    {"x": 2.0, "y": 0.0},
    {"x": 1.25, "y": 0.75},
    {"x": -0.5, "y": -0.5},
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def left_predicate(x: float) -> bool:
    return x > 0.0


def right_predicate(y: float) -> bool:
    return y > 0.0


def right_predicate_evaluated(x: float) -> bool:
    return left_predicate(x)


def expected_value(x: float, y: float) -> float:
    if left_predicate(x) and right_predicate(y):
        return x + y
    return 0.0


def path_for_sample(x: float, y: float) -> str:
    if not left_predicate(x):
        return "left_false_short_circuit_return_zero"
    if not right_predicate(y):
        return "left_true_right_false_return_zero"
    return "left_true_right_true_return_sum"


def expected_samples() -> list[dict[str, Any]]:
    samples = []
    for index, inputs in enumerate(SAMPLE_INPUTS):
        x = float(inputs["x"])
        y = float(inputs["y"])
        left_value = left_predicate(x)
        right_evaluated = right_predicate_evaluated(x)
        right_value = right_predicate(y) if right_evaluated else None
        samples.append(
            {
                "sampleId": f"sample_{index:02d}",
                "inputs": dict(inputs),
                "path": path_for_sample(x, y),
                "leftPredicate": "x > 0.0",
                "rightPredicate": "y > 0.0",
                "leftPredicateValue": left_value,
                "rightPredicateEvaluated": right_evaluated,
                "rightPredicateValue": right_value,
                "expected": expected_value(x, y),
                "sourceSemanticsOnly": True,
                "runtimeExecutionPerformed": False,
                "loweringPerformed": False,
                "shortCircuitPolicyApplied": False,
                "booleanNormalizationPolicyApplied": False,
            }
        )
    return samples


def selected_fixture(p113_result: dict[str, Any]) -> dict[str, Any]:
    for row in p113_result["compoundConditionFixtures"]:
        if row["id"] == SELECTED_FIXTURE_ID:
            return copy.deepcopy(row)
    raise ValueError(f"missing selected fixture: {SELECTED_FIXTURE_ID}")


def build_summary(p113_packet: dict[str, Any], fixture: dict[str, Any], samples: list[dict[str, Any]]) -> dict[str, Any]:
    nonzero_count = sum(1 for sample in samples if sample["expected"] != 0.0)
    right_eval_count = sum(1 for sample in samples if sample["rightPredicateEvaluated"])
    short_circuit_count = sum(1 for sample in samples if not sample["rightPredicateEvaluated"])
    return {
        "sourcePacketCount": 1,
        "p113ValidationPass": p113_packet["validationStatus"] == "pass",
        "p113ClaimFlagsAllFalse": all(value is False for value in p113_packet["claimFlags"].values()),
        "selectedFixtureId": fixture["id"],
        "selectedFixtureStatus": fixture["status"],
        "selectedFixtureStillBlocked": fixture["status"] == "blocked_fixture_defined",
        "sampleCount": len(samples),
        "nonzeroExpectedCount": nonzero_count,
        "zeroExpectedCount": len(samples) - nonzero_count,
        "rightPredicateEvaluatedCount": right_eval_count,
        "shortCircuitExpectedCount": short_circuit_count,
        "allSamplesSourceSemanticsOnly": all(sample["sourceSemanticsOnly"] is True for sample in samples),
        "allRuntimeExecutionNotPerformed": all(sample["runtimeExecutionPerformed"] is False for sample in samples),
        "allLoweringNotPerformed": all(sample["loweringPerformed"] is False for sample in samples),
        "allPoliciesNotApplied": all(
            sample["shortCircuitPolicyApplied"] is False
            and sample["booleanNormalizationPolicyApplied"] is False
            for sample in samples
        ),
        "compoundConditionRuntimeExecutionClaim": False,
        "compoundConditionLoweringImplemented": False,
        "shortCircuitPolicyImplemented": False,
        "booleanNormalizationPolicyImplemented": False,
        "compoundConditionSupportClaim": False,
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
    p113_packet = read_json(P113_PACKET)
    p113_result = read_json(P113_RESULT)
    p113.validate_payload(p113_result)
    fixture = selected_fixture(p113_result)
    samples = expected_samples()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p114-compound-condition-expected-samples",
        "decision": "compound_condition_expected_samples_recorded_support_blocked",
        "sourcePacket": {
            "phase": "P113",
            "packetPath": str(P113_PACKET.relative_to(ROOT)),
            "resultPath": str(P113_RESULT.relative_to(ROOT)),
            "reviewDecision": p113_packet["reviewDecision"],
            "validationStatus": p113_packet["validationStatus"],
        },
        "selectedFixture": fixture,
        "expectedSamples": samples,
        "summary": build_summary(p113_packet, fixture, samples),
        "releaseGates": [
            {"id": "compound_condition_expected_samples", "status": "recorded"},
            {"id": "compound_condition_runtime_execution", "status": "not_performed"},
            {"id": "compound_condition_lowering", "status": "blocked"},
            {"id": "short_circuit_policy", "status": "not_applied"},
            {"id": "boolean_normalization_policy", "status": "not_applied"},
            {"id": "compound_condition_support", "status": "blocked"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P114 records deterministic expected samples for one blocked compound-condition fixture.",
            "The selected fixture remains blocked pending short-circuit, boolean-normalization, runtime, lowering, and re-ingest validators.",
            "P114 defines expected source semantics without executing source or generated code.",
        ],
        "blockedStatements": [
            "Compound-condition code was executed.",
            "Compound-condition lowering is implemented.",
            "Short-circuit or boolean-normalization policy was applied.",
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
            "Define short-circuit and boolean-normalization policy before executing compound-condition samples.",
            "Turn the selected expected-sample fixture into a reference runtime comparison gate only after policy exists.",
            "Keep compound-condition support blocked until lowering and re-ingest evidence exists.",
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
        "title": "FEF-P114 Compound-Condition Expected Samples",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "compound_condition_expected_samples_recorded_support_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Expected-sample fixture only; no compound-condition execution, lowering, short-circuit policy, boolean-normalization policy, support, frontend widening, branch re-ingest, full source roundtrip, arbitrary source-family, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P114 records deterministic expected samples for c_and_guard_return_v0.",
            "Samples define expected short-circuit paths without executing code.",
            "Compound-condition support remains blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p114_compound_condition_expected_samples.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p114_compound_condition_expected_samples.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p114_compound_condition_expected_samples.v0",
        "date": DATE,
        "title": "FEF-P114 Compound-Condition Expected Samples",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Define short-circuit/boolean-normalization policy before executing compound-condition samples.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Sample | x | y | Path | Right evaluated | Expected |", "|---|---:|---:|---|---|---:|"]
    for sample in payload["expectedSamples"]:
        rows.append(
            f"| `{sample['sampleId']}` | `{sample['inputs']['x']}` | `{sample['inputs']['y']}` | "
            f"`{sample['path']}` | `{sample['rightPredicateEvaluated']}` | `{sample['expected']}` |"
        )
    return "\n".join(
        [
            "# FEF-P114 Compound-Condition Expected Samples",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P114 attaches deterministic expected samples to one blocked compound-condition fixture.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Selected fixture still blocked: `{summary['selectedFixtureStillBlocked']}`",
            f"- Samples: `{summary['sampleCount']}`",
            f"- Nonzero expected samples: `{summary['nonzeroExpectedCount']}`",
            f"- Zero expected samples: `{summary['zeroExpectedCount']}`",
            f"- Right predicate evaluated samples: `{summary['rightPredicateEvaluatedCount']}`",
            f"- Short-circuit expected samples: `{summary['shortCircuitExpectedCount']}`",
            f"- Source semantics only: `{summary['allSamplesSourceSemanticsOnly']}`",
            f"- Compound-condition runtime execution claim: `{summary['compoundConditionRuntimeExecutionClaim']}`",
            f"- Compound-condition lowering implemented: `{summary['compoundConditionLoweringImplemented']}`",
            f"- Compound-condition support claim: `{summary['compoundConditionSupportClaim']}`",
            "",
            "## Samples",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Expected samples only; no compound-condition execution.",
            "- No short-circuit or boolean-normalization policy is applied.",
            "- No compound-condition lowering or support claim.",
            "- No frontend lowering change.",
            "- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_sample(sample: dict[str, Any]) -> None:
    x = float(sample["inputs"]["x"])
    y = float(sample["inputs"]["y"])
    if sample["leftPredicateValue"] != left_predicate(x):
        raise ValueError("left predicate value does not match source semantics")
    if sample["rightPredicateEvaluated"] != right_predicate_evaluated(x):
        raise ValueError("right predicate evaluation does not match source semantics")
    expected_right = right_predicate(y) if right_predicate_evaluated(x) else None
    if sample["rightPredicateValue"] != expected_right:
        raise ValueError("right predicate value does not match source semantics")
    if sample["expected"] != expected_value(x, y):
        raise ValueError("sample expected value does not match source semantics")
    if sample["path"] != path_for_sample(x, y):
        raise ValueError("sample path does not match source semantics")
    for key in [
        "sourceSemanticsOnly",
    ]:
        if sample[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "runtimeExecutionPerformed",
        "loweringPerformed",
        "shortCircuitPolicyApplied",
        "booleanNormalizationPolicyApplied",
    ]:
        if sample[key] is not False:
            raise ValueError(f"{key} must be false")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P114 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P114 status")
    p113.validate_payload(read_json(P113_RESULT))
    summary = payload["summary"]
    for key in [
        "p113ValidationPass",
        "p113ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "allSamplesSourceSemanticsOnly",
        "allRuntimeExecutionNotPerformed",
        "allLoweringNotPerformed",
        "allPoliciesNotApplied",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["selectedFixtureId"] != SELECTED_FIXTURE_ID:
        raise ValueError("unexpected selected fixture")
    if summary["sampleCount"] != 7:
        raise ValueError("expected seven samples")
    if summary["nonzeroExpectedCount"] != 2 or summary["zeroExpectedCount"] != 5:
        raise ValueError("unexpected expected-value distribution")
    if summary["rightPredicateEvaluatedCount"] != 4 or summary["shortCircuitExpectedCount"] != 3:
        raise ValueError("unexpected short-circuit distribution")
    for sample in payload["expectedSamples"]:
        validate_sample(sample)
    for key in [
        "compoundConditionRuntimeExecutionClaim",
        "compoundConditionLoweringImplemented",
        "shortCircuitPolicyImplemented",
        "booleanNormalizationPolicyImplemented",
        "compoundConditionSupportClaim",
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
    result_path = out_dir / f"fef_p114_compound_condition_expected_samples_{STAMP}.json"
    report_path = report_dir / f"fef_p114_compound_condition_expected_samples_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p114_compound_condition_expected_samples.json"
    feed_path = command_feed_dir / f"fef_p114_compound_condition_expected_samples_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p114_compound_condition_expected_samples")
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
    print("FEF_P114_COMPOUND_CONDITION_EXPECTED_SAMPLES_OK")
    print(f"samples={built['payload']['summary']['sampleCount']}")
    print(f"short_circuit={built['payload']['summary']['shortCircuitExpectedCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
