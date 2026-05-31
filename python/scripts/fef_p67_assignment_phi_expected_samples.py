#!/usr/bin/env python3
"""FEF-P67 expected samples for one assignment/phi fixture."""

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

from scripts import fef_p66_assignment_phi_fixture_gate as p66

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p67_assignment_phi_expected_samples.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P67_ASSIGNMENT_PHI_EXPECTED_SAMPLES_PASS"

P66_PACKET = ROOT / "reports/evidence_packets/fef_p66_assignment_phi_fixture_gate.json"
P66_RESULT = ROOT / "python/results/fef_p66_assignment_phi_fixture_gate/fef_p66_assignment_phi_fixture_gate_2026_05_31.json"
SELECTED_FIXTURE_ID = "c_branch_assignment_merge_v0"

CLAIM_FLAGS = {
    "assignment_phi_expected_samples_claim": False,
    "assignment_phi_runtime_execution_claim": False,
    "assignment_phi_lowering_claim": False,
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
    "FEF-P67 records deterministic expected samples for one assignment/phi fixture only.",
    "FEF-P67 does not execute source, generated, or re-ingested assignment/phi code.",
    "FEF-P67 does not implement mutable assignment lowering.",
    "FEF-P67 does not implement phi/select lowering.",
    "FEF-P67 does not widen Forge or eFrog frontend lowering.",
    "FEF-P67 does not claim assignment/phi support.",
    "FEF-P67 does not claim nested branch support.",
    "FEF-P67 does not claim general branch/control-flow support.",
    "FEF-P67 does not claim branch/control-flow re-ingest support.",
    "FEF-P67 does not claim full non-generated source roundtrip.",
    "FEF-P67 does not claim arbitrary C/Rust source-family support.",
    "FEF-P67 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P67 does not claim runtime performance.",
]

SAMPLE_INPUTS = [
    {"x": 2.0, "y": 5.0},
    {"x": -2.0, "y": 5.0},
    {"x": 0.0, "y": 5.0},
    {"x": 1.25, "y": -3.5},
    {"x": -0.5, "y": -3.5},
    {"x": 4.0, "y": 0.0},
    {"x": -7.0, "y": 0.0},
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def expected_value(x: float, y: float) -> float:
    z = x
    if x > 0.0:
        z = y
    return z


def expected_samples() -> list[dict[str, Any]]:
    samples = []
    for index, inputs in enumerate(SAMPLE_INPUTS):
        x = inputs["x"]
        y = inputs["y"]
        assigned = x > 0.0
        samples.append(
            {
                "sampleId": f"sample_{index:02d}",
                "inputs": dict(inputs),
                "path": "branch_assignment_to_y" if assigned else "fallthrough_initial_x",
                "assignmentTaken": assigned,
                "expected": expected_value(x, y),
                "sourceSemanticsOnly": True,
            }
        )
    return samples


def selected_fixture(p66_result: dict[str, Any]) -> dict[str, Any]:
    for row in p66_result["assignmentPhiFixtures"]:
        if row["id"] == SELECTED_FIXTURE_ID:
            return copy.deepcopy(row)
    raise ValueError(f"missing selected fixture: {SELECTED_FIXTURE_ID}")


def build_summary(p66_packet: dict[str, Any], fixture: dict[str, Any], samples: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sourcePacketCount": 1,
        "p66ValidationPass": p66_packet["validationStatus"] == "pass",
        "p66ClaimFlagsAllFalse": all(value is False for value in p66_packet["claimFlags"].values()),
        "selectedFixtureId": fixture["id"],
        "selectedFixtureStatus": fixture["status"],
        "selectedFixtureStillBlocked": fixture["status"] == "blocked_fixture_defined",
        "sampleCount": len(samples),
        "assignmentTakenCount": sum(1 for sample in samples if sample["assignmentTaken"] is True),
        "fallthroughCount": sum(1 for sample in samples if sample["assignmentTaken"] is False),
        "allSamplesSourceSemanticsOnly": all(sample["sourceSemanticsOnly"] is True for sample in samples),
        "assignmentPhiRuntimeExecutionClaim": False,
        "assignmentPhiLoweringClaim": False,
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
    p66_packet = read_json(P66_PACKET)
    p66_result = read_json(P66_RESULT)
    p66.validate_payload(p66_result)
    fixture = selected_fixture(p66_result)
    samples = expected_samples()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p67-assignment-phi-expected-samples",
        "decision": "assignment_phi_expected_samples_recorded_support_blocked",
        "sourcePacket": {
            "phase": "P66",
            "packetPath": str(P66_PACKET.relative_to(ROOT)),
            "resultPath": str(P66_RESULT.relative_to(ROOT)),
            "reviewDecision": p66_packet["reviewDecision"],
            "validationStatus": p66_packet["validationStatus"],
        },
        "selectedFixture": fixture,
        "expectedSamples": samples,
        "summary": build_summary(p66_packet, fixture, samples),
        "releaseGates": [
            {"id": "assignment_phi_expected_samples", "status": "recorded"},
            {"id": "assignment_phi_runtime_execution", "status": "not_performed"},
            {"id": "assignment_phi_lowering", "status": "blocked"},
            {"id": "assignment_phi_support", "status": "blocked"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P67 records deterministic expected samples for one blocked assignment/phi fixture.",
            "The selected assignment/phi fixture remains blocked pending runtime/lowering/re-ingest validators.",
            "P67 helps define the next validation surface without implementing support.",
        ],
        "blockedStatements": [
            "Assignment/phi fixtures were executed.",
            "Assignment/phi lowering is implemented.",
            "Mutable assignments across branches are supported.",
            "Phi/select lowering is supported.",
            "Frontend branch lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Turn the selected assignment/phi expected-sample fixture into a runtime comparison gate.",
            "Build a compound-condition semantics gate for short-circuit shape.",
            "Keep assignment/phi support blocked until lowering and re-ingest evidence exists.",
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
        "title": "FEF-P67 Assignment/Phi Expected Samples",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "assignment_phi_expected_samples_recorded_support_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Expected-sample fixture only; no assignment/phi execution, lowering, support, frontend widening, branch re-ingest, full source roundtrip, arbitrary source-family, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P67 records deterministic expected samples for c_branch_assignment_merge_v0.",
            "The fixture remains blocked and source-semantics-only.",
            "Assignment/phi support and general branch/control-flow claims remain blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p67_assignment_phi_expected_samples.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p67_assignment_phi_expected_samples.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p67_assignment_phi_expected_samples.v0",
        "date": DATE,
        "title": "FEF-P67 Assignment/Phi Expected Samples",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Turn the selected assignment/phi expected-sample fixture into a runtime comparison gate.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = ["| Sample | x | y | Path | Expected |", "|---|---:|---:|---|---:|"]
    for sample in payload["expectedSamples"]:
        rows.append(
            f"| `{sample['sampleId']}` | {sample['inputs']['x']} | {sample['inputs']['y']} | `{sample['path']}` | {sample['expected']} |"
        )
    return "\n".join(
        [
            "# FEF-P67 Assignment/Phi Expected Samples",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P67 attaches deterministic expected samples to one blocked assignment/phi fixture.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Selected fixture still blocked: `{summary['selectedFixtureStillBlocked']}`",
            f"- Samples: `{summary['sampleCount']}`",
            f"- Assignment taken samples: `{summary['assignmentTakenCount']}`",
            f"- Fallthrough samples: `{summary['fallthroughCount']}`",
            f"- Source semantics only: `{summary['allSamplesSourceSemanticsOnly']}`",
            f"- Assignment/phi runtime execution claim: `{summary['assignmentPhiRuntimeExecutionClaim']}`",
            f"- Assignment/phi lowering claim: `{summary['assignmentPhiLoweringClaim']}`",
            f"- Assignment/phi support claim: `{summary['assignmentPhiSupportClaim']}`",
            "",
            "## Samples",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Expected samples only; no assignment/phi execution.",
            "- No assignment/phi lowering or support claim.",
            "- No frontend lowering change.",
            "- No branch re-ingest, full source roundtrip, arbitrary source-family, compiler-correctness, formal-equivalence, or runtime-performance claim.",
            "",
        ]
    )


def validate_sample(sample: dict[str, Any]) -> None:
    x = sample["inputs"]["x"]
    y = sample["inputs"]["y"]
    if sample["expected"] != expected_value(x, y):
        raise ValueError("sample expected value does not match source semantics")
    if sample["assignmentTaken"] != (x > 0.0):
        raise ValueError("sample assignment path does not match source semantics")
    if sample["sourceSemanticsOnly"] is not True:
        raise ValueError("sample must remain source-semantics-only")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P67 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P67 status")
    if payload["selectedFixture"]["id"] != SELECTED_FIXTURE_ID:
        raise ValueError("unexpected selected fixture")
    p66.validate_fixture(payload["selectedFixture"])
    for sample in payload["expectedSamples"]:
        validate_sample(sample)
    summary = payload["summary"]
    for key in ["p66ValidationPass", "p66ClaimFlagsAllFalse", "selectedFixtureStillBlocked", "allSamplesSourceSemanticsOnly", "claimFlagsAllFalse"]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["sampleCount"] != 7:
        raise ValueError("expected seven samples")
    if summary["assignmentTakenCount"] != 3 or summary["fallthroughCount"] != 4:
        raise ValueError("unexpected assignment/fallthrough distribution")
    for key in [
        "assignmentPhiRuntimeExecutionClaim",
        "assignmentPhiLoweringClaim",
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
    result_path = out_dir / f"fef_p67_assignment_phi_expected_samples_{STAMP}.json"
    report_path = report_dir / f"fef_p67_assignment_phi_expected_samples_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p67_assignment_phi_expected_samples.json"
    feed_path = command_feed_dir / f"fef_p67_assignment_phi_expected_samples_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p67_assignment_phi_expected_samples")
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
    print("FEF_P67_ASSIGNMENT_PHI_EXPECTED_SAMPLES_OK")
    print(f"samples={built['payload']['summary']['sampleCount']}")
    print(f"selected_fixture={built['payload']['summary']['selectedFixtureId']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
