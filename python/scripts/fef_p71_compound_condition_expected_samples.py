#!/usr/bin/env python3
"""FEF-P71 expected samples for one compound-condition fixture."""

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

from scripts import fef_p70_compound_condition_fixture_gate as p70

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p71_compound_condition_expected_samples.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P71_COMPOUND_CONDITION_EXPECTED_SAMPLES_PASS"

P70_PACKET = ROOT / "reports/evidence_packets/fef_p70_compound_condition_fixture_gate.json"
P70_RESULT = ROOT / "python/results/fef_p70_compound_condition_fixture_gate/fef_p70_compound_condition_fixture_gate_2026_05_31.json"
SELECTED_FIXTURE_ID = "c_and_short_circuit_guard_v0"

CLAIM_FLAGS = {
    "compound_condition_expected_samples_claim": False,
    "compound_condition_runtime_execution_claim": False,
    "compound_condition_lowering_claim": False,
    "compound_condition_support_claim": False,
    "short_circuit_semantics_implemented": False,
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
    "FEF-P71 records deterministic expected samples for one compound-condition fixture only.",
    "FEF-P71 does not execute source, generated, or re-ingested compound-condition code.",
    "FEF-P71 does not implement short-circuit condition semantics.",
    "FEF-P71 does not implement compound-condition lowering.",
    "FEF-P71 does not widen Forge or eFrog frontend lowering.",
    "FEF-P71 does not claim compound-condition support.",
    "FEF-P71 does not claim assignment/phi or nested branch support.",
    "FEF-P71 does not claim general branch/control-flow support.",
    "FEF-P71 does not claim branch/control-flow re-ingest support.",
    "FEF-P71 does not claim full non-generated source roundtrip.",
    "FEF-P71 does not claim arbitrary C/Rust source-family support.",
    "FEF-P71 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P71 does not claim runtime performance.",
]

SAMPLE_INPUTS = [
    {"x": 2.0, "y": 4.0},
    {"x": -2.0, "y": 0.0},
    {"x": 0.0, "y": 5.0},
    {"x": 3.0, "y": 0.0},
    {"x": 1.5, "y": -0.5},
    {"x": -1.0, "y": -2.0},
    {"x": 5.0, "y": 2.0},
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def expected_value(x: float, y: float) -> float:
    if x > 0.0 and y != 0.0:
        return x / y
    return 0.0


def expected_samples() -> list[dict[str, Any]]:
    samples = []
    for index, inputs in enumerate(SAMPLE_INPUTS):
        x = inputs["x"]
        y = inputs["y"]
        left_condition = x > 0.0
        right_condition_evaluated = left_condition
        right_condition = y != 0.0 if right_condition_evaluated else None
        division_performed = bool(left_condition and right_condition)
        if division_performed:
            path = "and_true_division"
        elif not left_condition:
            path = "left_false_short_circuit"
        else:
            path = "right_false_zero_denominator_guard"
        samples.append(
            {
                "sampleId": f"sample_{index:02d}",
                "inputs": dict(inputs),
                "path": path,
                "leftCondition": left_condition,
                "rightConditionEvaluated": right_condition_evaluated,
                "rightCondition": right_condition,
                "divisionPerformed": division_performed,
                "expected": expected_value(x, y),
                "sourceSemanticsOnly": True,
            }
        )
    return samples


def selected_fixture(p70_result: dict[str, Any]) -> dict[str, Any]:
    for row in p70_result["compoundConditionFixtures"]:
        if row["id"] == SELECTED_FIXTURE_ID:
            return copy.deepcopy(row)
    raise ValueError(f"missing selected fixture: {SELECTED_FIXTURE_ID}")


def build_summary(p70_packet: dict[str, Any], fixture: dict[str, Any], samples: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p70ValidationPass": p70_packet["validationStatus"] == "pass",
        "p70ClaimFlagsAllFalse": all(value is False for value in p70_packet["claimFlags"].values()),
        "selectedFixtureId": fixture["id"],
        "selectedFixtureStatus": fixture["status"],
        "selectedFixtureStillBlocked": fixture["status"] == "blocked_fixture_defined",
        "sampleCount": len(samples),
        "andTrueDivisionCount": sum(1 for sample in samples if sample["path"] == "and_true_division"),
        "leftFalseShortCircuitCount": sum(1 for sample in samples if sample["path"] == "left_false_short_circuit"),
        "rightFalseGuardCount": sum(1 for sample in samples if sample["path"] == "right_false_zero_denominator_guard"),
        "rightConditionEvaluationCount": sum(1 for sample in samples if sample["rightConditionEvaluated"] is True),
        "divisionPerformedCount": sum(1 for sample in samples if sample["divisionPerformed"] is True),
        "allSamplesSourceSemanticsOnly": all(sample["sourceSemanticsOnly"] is True for sample in samples),
        "compoundConditionRuntimeExecutionClaim": False,
        "compoundConditionLoweringClaim": False,
        "compoundConditionSupportClaim": False,
        "shortCircuitSemanticsImplemented": False,
        "assignmentPhiSupportClaim": False,
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
    p70_packet = read_json(P70_PACKET)
    p70_result = read_json(P70_RESULT)
    p70.validate_payload(p70_result)
    fixture = selected_fixture(p70_result)
    samples = expected_samples()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p71-compound-condition-expected-samples",
        "decision": "compound_condition_expected_samples_recorded_support_blocked",
        "sourcePacket": {
            "phase": "P70",
            "packetPath": str(P70_PACKET.relative_to(ROOT)),
            "resultPath": str(P70_RESULT.relative_to(ROOT)),
            "reviewDecision": p70_packet["reviewDecision"],
            "validationStatus": p70_packet["validationStatus"],
        },
        "selectedFixture": fixture,
        "expectedSamples": samples,
        "summary": build_summary(p70_packet, fixture, samples),
        "releaseGates": [
            {"id": "compound_condition_expected_samples", "status": "recorded"},
            {"id": "compound_condition_runtime_execution", "status": "not_performed"},
            {"id": "compound_condition_lowering", "status": "blocked"},
            {"id": "compound_condition_support", "status": "blocked"},
            {"id": "short_circuit_semantics_implementation", "status": "not_performed"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P71 records deterministic expected samples for one blocked compound-condition fixture.",
            "The selected fixture remains blocked pending runtime, lowering, and re-ingest validators.",
            "P71 helps define the next validation surface without implementing short-circuit support.",
        ],
        "blockedStatements": [
            "Compound-condition fixtures were executed.",
            "Short-circuit condition semantics are implemented.",
            "Compound-condition lowering is implemented.",
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
            "Turn the selected compound-condition expected-sample fixture into a reference runtime comparison gate.",
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
        "title": "FEF-P71 Compound-Condition Expected Samples",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "compound_condition_expected_samples_recorded_support_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Expected-sample fixture only; no compound-condition execution, lowering, support, frontend widening, branch re-ingest, full source roundtrip, arbitrary source-family, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P71 records deterministic expected samples for c_and_short_circuit_guard_v0.",
            "The fixture remains blocked and source-semantics-only.",
            "Compound-condition support and general branch/control-flow claims remain blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p71_compound_condition_expected_samples.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p71_compound_condition_expected_samples.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p71_compound_condition_expected_samples.v0",
        "date": DATE,
        "title": "FEF-P71 Compound-Condition Expected Samples",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Turn the selected compound-condition expected-sample fixture into a reference runtime comparison gate.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Sample | x | y | Path | Right eval | Division | Expected |", "|---|---:|---:|---|---|---|---:|"]
    for sample in payload["expectedSamples"]:
        rows.append(
            f"| `{sample['sampleId']}` | {sample['inputs']['x']} | {sample['inputs']['y']} | `{sample['path']}` | `{sample['rightConditionEvaluated']}` | `{sample['divisionPerformed']}` | {sample['expected']} |"
        )
    return "\n".join(
        [
            "# FEF-P71 Compound-Condition Expected Samples",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P71 attaches deterministic expected samples to one blocked compound-condition fixture.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Selected fixture still blocked: `{summary['selectedFixtureStillBlocked']}`",
            f"- Samples: `{summary['sampleCount']}`",
            f"- True-division samples: `{summary['andTrueDivisionCount']}`",
            f"- Left-false short-circuit samples: `{summary['leftFalseShortCircuitCount']}`",
            f"- Right-false guard samples: `{summary['rightFalseGuardCount']}`",
            f"- Right condition evaluations: `{summary['rightConditionEvaluationCount']}`",
            f"- Division performed samples: `{summary['divisionPerformedCount']}`",
            f"- Source semantics only: `{summary['allSamplesSourceSemanticsOnly']}`",
            f"- Compound-condition runtime execution claim: `{summary['compoundConditionRuntimeExecutionClaim']}`",
            f"- Compound-condition lowering claim: `{summary['compoundConditionLoweringClaim']}`",
            f"- Compound-condition support claim: `{summary['compoundConditionSupportClaim']}`",
            "",
            "## Samples",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Expected samples only; no compound-condition execution.",
            "- No short-circuit implementation, lowering, or support claim.",
            "- No frontend lowering change.",
            "- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_sample(sample: dict[str, Any]) -> None:
    x = sample["inputs"]["x"]
    y = sample["inputs"]["y"]
    left_condition = x > 0.0
    right_evaluated = left_condition
    right_condition = y != 0.0 if right_evaluated else None
    division_performed = bool(left_condition and right_condition)
    if sample["expected"] != expected_value(x, y):
        raise ValueError("sample expected value does not match source semantics")
    if sample["leftCondition"] != left_condition:
        raise ValueError("left condition does not match source semantics")
    if sample["rightConditionEvaluated"] != right_evaluated:
        raise ValueError("right condition evaluation does not match short-circuit semantics")
    if sample["rightCondition"] != right_condition:
        raise ValueError("right condition value does not match source semantics")
    if sample["divisionPerformed"] != division_performed:
        raise ValueError("division path does not match source semantics")
    if sample["sourceSemanticsOnly"] is not True:
        raise ValueError("sample must remain source-semantics-only")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P71 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P71 status")
    if payload["selectedFixture"]["id"] != SELECTED_FIXTURE_ID:
        raise ValueError("unexpected selected fixture")
    p70.validate_fixture(payload["selectedFixture"])
    for sample in payload["expectedSamples"]:
        validate_sample(sample)
    summary = payload["summary"]
    for key in ["p70ValidationPass", "p70ClaimFlagsAllFalse", "selectedFixtureStillBlocked", "allSamplesSourceSemanticsOnly", "claimFlagsAllFalse"]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["sampleCount"] != 7:
        raise ValueError("expected seven samples")
    if summary["andTrueDivisionCount"] != 3:
        raise ValueError("expected three true-division samples")
    if summary["leftFalseShortCircuitCount"] != 3:
        raise ValueError("expected three left-false short-circuit samples")
    if summary["rightFalseGuardCount"] != 1:
        raise ValueError("expected one right-false guard sample")
    if summary["rightConditionEvaluationCount"] != 4 or summary["divisionPerformedCount"] != 3:
        raise ValueError("unexpected right-evaluation/division distribution")
    for key in [
        "compoundConditionRuntimeExecutionClaim",
        "compoundConditionLoweringClaim",
        "compoundConditionSupportClaim",
        "shortCircuitSemanticsImplemented",
        "assignmentPhiSupportClaim",
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
    result_path = out_dir / f"fef_p71_compound_condition_expected_samples_{STAMP}.json"
    report_path = report_dir / f"fef_p71_compound_condition_expected_samples_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p71_compound_condition_expected_samples.json"
    feed_path = command_feed_dir / f"fef_p71_compound_condition_expected_samples_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p71_compound_condition_expected_samples")
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
    print("FEF_P71_COMPOUND_CONDITION_EXPECTED_SAMPLES_OK")
    print(f"samples={built['payload']['summary']['sampleCount']}")
    print(f"selected_fixture={built['payload']['summary']['selectedFixtureId']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
