#!/usr/bin/env python3
"""FEF-P91 expected samples for one loop/back-edge fixture."""

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

from scripts import fef_p90_loop_backedge_fixture_gate as p90  # noqa: E402

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p91_loop_backedge_expected_samples.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P91_LOOP_BACKEDGE_EXPECTED_SAMPLES_PASS"

P90_PACKET = ROOT / "reports/evidence_packets/fef_p90_loop_backedge_fixture_gate.json"
P90_RESULT = ROOT / "python/results/fef_p90_loop_backedge_fixture_gate/fef_p90_loop_backedge_fixture_gate_2026_05_31.json"
SELECTED_FIXTURE_ID = "c_while_accumulate_v0"

CLAIM_FLAGS = {
    "loop_backedge_expected_samples_claim": False,
    "loop_runtime_execution_claim": False,
    "loop_lowering_claim": False,
    "loop_backedge_support_claim": False,
    "loop_boundedness_policy_claim": False,
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
    "FEF-P91 records deterministic expected samples for one loop/back-edge fixture only.",
    "FEF-P91 does not execute source, generated, or re-ingested loop code.",
    "FEF-P91 does not implement loop headers, latches, variants, or boundedness policy.",
    "FEF-P91 does not implement loop lowering.",
    "FEF-P91 does not widen Forge or eFrog frontend lowering.",
    "FEF-P91 does not claim loop/back-edge support.",
    "FEF-P91 does not claim assignment/phi, compound-condition, or nested-branch support.",
    "FEF-P91 does not record reviewer approval or rejection.",
    "FEF-P91 does not approve or apply the P88 implementation proposal.",
    "FEF-P91 does not claim general branch/control-flow support.",
    "FEF-P91 does not claim branch/control-flow re-ingest support.",
    "FEF-P91 does not claim full non-generated source roundtrip.",
    "FEF-P91 does not claim arbitrary C/Rust source-family support.",
    "FEF-P91 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P91 does not claim runtime performance, public readiness, package publication, checkout, or production readiness.",
]

SAMPLE_INPUTS = [
    {"x": 2.0, "n": 0},
    {"x": 2.0, "n": 1},
    {"x": 2.0, "n": 3},
    {"x": -1.5, "n": 4},
    {"x": 0.0, "n": 5},
    {"x": 3.0, "n": -2},
    {"x": 0.25, "n": 8},
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def iteration_count(n: int) -> int:
    return max(0, int(n))


def expected_value(x: float, n: int) -> float:
    acc = 0.0
    i = 0
    while i < n:
        acc = acc + x
        i = i + 1
    return acc


def path_for_iterations(count: int) -> str:
    if count == 0:
        return "zero_iterations"
    if count == 1:
        return "single_iteration"
    return "multi_iteration"


def expected_samples() -> list[dict[str, Any]]:
    samples = []
    for index, inputs in enumerate(SAMPLE_INPUTS):
        x = inputs["x"]
        n = int(inputs["n"])
        count = iteration_count(n)
        samples.append(
            {
                "sampleId": f"sample_{index:02d}",
                "inputs": dict(inputs),
                "path": path_for_iterations(count),
                "loopConditionInitiallyTrue": n > 0,
                "iterationCount": count,
                "backEdgeTakenCount": count,
                "expected": expected_value(x, n),
                "sourceSemanticsOnly": True,
                "boundednessPolicyApplied": False,
                "runtimeExecutionPerformed": False,
            }
        )
    return samples


def selected_fixture(p90_result: dict[str, Any]) -> dict[str, Any]:
    for row in p90_result["loopBackedgeFixtures"]:
        if row["id"] == SELECTED_FIXTURE_ID:
            return copy.deepcopy(row)
    raise ValueError(f"missing selected fixture: {SELECTED_FIXTURE_ID}")


def build_summary(p90_packet: dict[str, Any], fixture: dict[str, Any], samples: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p90ValidationPass": p90_packet["validationStatus"] == "pass",
        "p90ClaimFlagsAllFalse": all(value is False for value in p90_packet["claimFlags"].values()),
        "selectedFixtureId": fixture["id"],
        "selectedFixtureStatus": fixture["status"],
        "selectedFixtureStillBlocked": fixture["status"] == "blocked_fixture_defined",
        "sampleCount": len(samples),
        "zeroIterationCount": sum(1 for sample in samples if sample["iterationCount"] == 0),
        "singleIterationCount": sum(1 for sample in samples if sample["iterationCount"] == 1),
        "multiIterationCount": sum(1 for sample in samples if sample["iterationCount"] > 1),
        "maxIterationCount": max(sample["iterationCount"] for sample in samples),
        "totalBackEdgeTakenCount": sum(sample["backEdgeTakenCount"] for sample in samples),
        "allSamplesSourceSemanticsOnly": all(sample["sourceSemanticsOnly"] is True for sample in samples),
        "allRuntimeExecutionNotPerformed": all(sample["runtimeExecutionPerformed"] is False for sample in samples),
        "allBoundednessPolicyNotApplied": all(sample["boundednessPolicyApplied"] is False for sample in samples),
        "loopRuntimeExecutionClaim": False,
        "loopLoweringClaim": False,
        "loopBackedgeSupportClaim": False,
        "loopBoundednessPolicyClaim": False,
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
    p90_packet = read_json(P90_PACKET)
    p90_result = read_json(P90_RESULT)
    p90.validate_payload(p90_result)
    fixture = selected_fixture(p90_result)
    samples = expected_samples()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p91-loop-backedge-expected-samples",
        "decision": "loop_backedge_expected_samples_recorded_support_blocked",
        "sourcePacket": {
            "phase": "P90",
            "packetPath": str(P90_PACKET.relative_to(ROOT)),
            "resultPath": str(P90_RESULT.relative_to(ROOT)),
            "reviewDecision": p90_packet["reviewDecision"],
            "validationStatus": p90_packet["validationStatus"],
        },
        "selectedFixture": fixture,
        "expectedSamples": samples,
        "summary": build_summary(p90_packet, fixture, samples),
        "releaseGates": [
            {"id": "loop_backedge_expected_samples", "status": "recorded"},
            {"id": "loop_runtime_execution", "status": "not_performed"},
            {"id": "loop_lowering", "status": "blocked"},
            {"id": "loop_boundedness_policy", "status": "not_applied"},
            {"id": "loop_backedge_support", "status": "blocked"},
            {"id": "p89_private_reviewer_hold", "status": "preserved"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P91 records deterministic expected samples for one blocked loop/back-edge fixture.",
            "The selected loop fixture remains blocked pending boundedness, runtime, lowering, and re-ingest validators.",
            "P91 helps define the next validation surface without implementing loop support.",
        ],
        "blockedStatements": [
            "Loop fixtures were executed.",
            "Loop lowering is implemented.",
            "Loop headers, latches, variants, or back-edge semantics are supported.",
            "A loop boundedness policy was applied.",
            "The P89 reviewer hold has been lifted.",
            "The P88 implementation proposal has been approved or applied.",
            "Frontend branch lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Define a boundedness and iteration-limit policy before executing loop samples.",
            "Turn the selected loop expected-sample fixture into a reference runtime comparison gate only after policy exists.",
            "Keep loop/back-edge support blocked until lowering and re-ingest evidence exists.",
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
        "title": "FEF-P91 Loop/Back-Edge Expected Samples",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "loop_backedge_expected_samples_recorded_support_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Expected-sample fixture only; no loop execution, lowering, boundedness policy, support, frontend widening, branch re-ingest, full source roundtrip, arbitrary source-family, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P91 records deterministic expected samples for c_while_accumulate_v0.",
            "The fixture remains blocked and source-semantics-only.",
            "Loop/back-edge support and general branch/control-flow claims remain blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p91_loop_backedge_expected_samples.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p91_loop_backedge_expected_samples.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p91_loop_backedge_expected_samples.v0",
        "date": DATE,
        "title": "FEF-P91 Loop/Back-Edge Expected Samples",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Define a boundedness and iteration-limit policy before executing loop samples.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Sample | x | n | Path | Iterations | Expected |", "|---|---:|---:|---|---:|---:|"]
    for sample in payload["expectedSamples"]:
        rows.append(
            f"| `{sample['sampleId']}` | {sample['inputs']['x']} | {sample['inputs']['n']} | `{sample['path']}` | {sample['iterationCount']} | {sample['expected']} |"
        )
    return "\n".join(
        [
            "# FEF-P91 Loop/Back-Edge Expected Samples",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P91 records deterministic expected samples for one blocked loop/back-edge fixture.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Sample count: `{summary['sampleCount']}`",
            f"- Zero-iteration samples: `{summary['zeroIterationCount']}`",
            f"- Single-iteration samples: `{summary['singleIterationCount']}`",
            f"- Multi-iteration samples: `{summary['multiIterationCount']}`",
            f"- Max iteration count: `{summary['maxIterationCount']}`",
            f"- Total back-edge taken count: `{summary['totalBackEdgeTakenCount']}`",
            f"- Source semantics only: `{summary['allSamplesSourceSemanticsOnly']}`",
            f"- Loop runtime execution claim: `{summary['loopRuntimeExecutionClaim']}`",
            f"- Loop boundedness policy claim: `{summary['loopBoundednessPolicyClaim']}`",
            f"- Loop/back-edge support claim: `{summary['loopBackedgeSupportClaim']}`",
            "",
            "## Samples",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Expected samples only; no loop execution.",
            "- No loop boundedness policy, lowering, or support claim.",
            "- No frontend lowering change.",
            "- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_sample(sample: dict[str, Any]) -> None:
    x = sample["inputs"]["x"]
    n = int(sample["inputs"]["n"])
    count = iteration_count(n)
    if sample["expected"] != expected_value(x, n):
        raise ValueError("sample expected value does not match source semantics")
    if sample["iterationCount"] != count:
        raise ValueError("iteration count does not match source semantics")
    if sample["backEdgeTakenCount"] != count:
        raise ValueError("back-edge count does not match source semantics")
    if sample["loopConditionInitiallyTrue"] != (n > 0):
        raise ValueError("initial loop condition does not match source semantics")
    if sample["path"] != path_for_iterations(count):
        raise ValueError("path does not match iteration count")
    if sample["sourceSemanticsOnly"] is not True:
        raise ValueError("sample must remain source-semantics-only")
    if sample["boundednessPolicyApplied"] is not False:
        raise ValueError("boundedness policy must not be applied")
    if sample["runtimeExecutionPerformed"] is not False:
        raise ValueError("runtime execution must not be performed")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P91 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P91 status")
    if payload["selectedFixture"]["id"] != SELECTED_FIXTURE_ID:
        raise ValueError("unexpected selected fixture")
    if payload["selectedFixture"]["status"] != "blocked_fixture_defined":
        raise ValueError("selected fixture must remain blocked")
    for sample in payload["expectedSamples"]:
        validate_sample(sample)
    summary = payload["summary"]
    for key in [
        "p90ValidationPass",
        "p90ClaimFlagsAllFalse",
        "selectedFixtureStillBlocked",
        "allSamplesSourceSemanticsOnly",
        "allRuntimeExecutionNotPerformed",
        "allBoundednessPolicyNotApplied",
        "claimFlagsAllFalse",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["sampleCount"] != 7:
        raise ValueError("expected seven samples")
    if summary["zeroIterationCount"] != 2:
        raise ValueError("expected two zero-iteration samples")
    if summary["singleIterationCount"] != 1:
        raise ValueError("expected one single-iteration sample")
    if summary["multiIterationCount"] != 4:
        raise ValueError("expected four multi-iteration samples")
    if summary["maxIterationCount"] != 8:
        raise ValueError("expected max iteration count of eight")
    if summary["totalBackEdgeTakenCount"] != 21:
        raise ValueError("unexpected total back-edge count")
    for key in [
        "loopRuntimeExecutionClaim",
        "loopLoweringClaim",
        "loopBackedgeSupportClaim",
        "loopBoundednessPolicyClaim",
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
    result_path = out_dir / f"fef_p91_loop_backedge_expected_samples_{STAMP}.json"
    report_path = report_dir / f"fef_p91_loop_backedge_expected_samples_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p91_loop_backedge_expected_samples.json"
    feed_path = command_feed_dir / f"fef_p91_loop_backedge_expected_samples_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p91_loop_backedge_expected_samples")
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
    print("FEF_P91_LOOP_BACKEDGE_EXPECTED_SAMPLES_OK")
    print(f"sample_count={built['payload']['summary']['sampleCount']}")
    print(f"max_iteration_count={built['payload']['summary']['maxIterationCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
