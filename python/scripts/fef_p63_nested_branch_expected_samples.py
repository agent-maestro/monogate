#!/usr/bin/env python3
"""FEF-P63 expected samples for one nested-branch fixture."""

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

from scripts import fef_p62_nested_branch_fixture_matrix as p62

DATE = "2026-05-31"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p63_nested_branch_expected_samples.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P63_NESTED_BRANCH_EXPECTED_SAMPLES_PASS"

P62_PACKET = ROOT / "reports/evidence_packets/fef_p62_nested_branch_fixture_matrix.json"
P62_RESULT = ROOT / "python/results/fef_p62_nested_branch_fixture_matrix/fef_p62_nested_branch_fixture_matrix_2026_05_31.json"
SELECTED_FIXTURE_ID = "c_nested_if_return_v0"

CLAIM_FLAGS = {
    "nested_branch_expected_samples_claim": False,
    "nested_branch_runtime_execution_claim": False,
    "nested_branch_lowering_claim": False,
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
    "FEF-P63 records deterministic expected samples for one nested-branch fixture only.",
    "FEF-P63 does not execute source, generated, or re-ingested nested branch code.",
    "FEF-P63 does not implement nested branch lowering.",
    "FEF-P63 does not widen Forge or eFrog frontend lowering.",
    "FEF-P63 does not claim nested branch support.",
    "FEF-P63 does not claim general branch/control-flow support.",
    "FEF-P63 does not claim branch/control-flow re-ingest support.",
    "FEF-P63 does not claim full non-generated source roundtrip.",
    "FEF-P63 does not claim arbitrary C/Rust source-family support.",
    "FEF-P63 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P63 does not claim runtime performance.",
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


def expected_value(x: float, y: float) -> float:
    if x > 0.0:
        if y > 0.0:
            return x + y
    return 0.0


def expected_samples() -> list[dict[str, Any]]:
    samples = []
    for index, inputs in enumerate(SAMPLE_INPUTS):
        x = inputs["x"]
        y = inputs["y"]
        samples.append(
            {
                "sampleId": f"sample_{index:02d}",
                "inputs": dict(inputs),
                "path": "outer_true_inner_true_return_sum" if x > 0.0 and y > 0.0 else "fallthrough_return_zero",
                "expected": expected_value(x, y),
                "sourceSemanticsOnly": True,
            }
        )
    return samples


def selected_fixture(p62_result: dict[str, Any]) -> dict[str, Any]:
    for row in p62_result["nestedBranchFixtures"]:
        if row["id"] == SELECTED_FIXTURE_ID:
            return copy.deepcopy(row)
    raise ValueError(f"missing selected fixture: {SELECTED_FIXTURE_ID}")


def build_summary(p62_packet: dict[str, Any], fixture: dict[str, Any], samples: list[dict[str, Any]]) -> dict[str, Any]:
    nonzero_count = sum(1 for sample in samples if sample["expected"] != 0.0)
    return {
        "sourcePacketCount": 1,
        "p62ValidationPass": p62_packet["validationStatus"] == "pass",
        "p62ClaimFlagsAllFalse": all(value is False for value in p62_packet["claimFlags"].values()),
        "selectedFixtureId": fixture["id"],
        "selectedFixtureStatus": fixture["status"],
        "selectedFixtureStillBlocked": fixture["status"] == "blocked_fixture_defined",
        "sampleCount": len(samples),
        "nonzeroExpectedCount": nonzero_count,
        "zeroExpectedCount": len(samples) - nonzero_count,
        "allSamplesSourceSemanticsOnly": all(sample["sourceSemanticsOnly"] is True for sample in samples),
        "nestedBranchRuntimeExecutionClaim": False,
        "nestedBranchLoweringClaim": False,
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
    p62_packet = read_json(P62_PACKET)
    p62_result = read_json(P62_RESULT)
    fixture = selected_fixture(p62_result)
    samples = expected_samples()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p63-nested-branch-expected-samples",
        "decision": "nested_branch_expected_samples_recorded_support_blocked",
        "sourcePacket": {
            "phase": "P62",
            "packetPath": str(P62_PACKET.relative_to(ROOT)),
            "resultPath": str(P62_RESULT.relative_to(ROOT)),
            "reviewDecision": p62_packet["reviewDecision"],
            "validationStatus": p62_packet["validationStatus"],
        },
        "selectedFixture": fixture,
        "expectedSamples": samples,
        "summary": build_summary(p62_packet, fixture, samples),
        "releaseGates": [
            {"id": "nested_branch_expected_samples", "status": "recorded"},
            {"id": "nested_branch_runtime_execution", "status": "not_performed"},
            {"id": "nested_branch_lowering", "status": "blocked"},
            {"id": "nested_branch_support", "status": "blocked"},
            {"id": "frontend_lowering_change", "status": "not_performed"},
            {"id": "general_branch_control_flow_support", "status": "blocked"},
            {"id": "compiler_correctness", "status": "blocked"},
        ],
        "allowedPrivateReviewerStatements": [
            "P63 records deterministic expected samples for one blocked nested-branch fixture.",
            "The selected nested branch fixture remains blocked pending runtime/lowering/re-ingest validators.",
            "P63 helps define the next validation surface without implementing support.",
        ],
        "blockedStatements": [
            "Nested branch code was executed.",
            "Nested branch lowering is implemented.",
            "Nested branches are supported.",
            "Frontend branch lowering was widened.",
            "General C/Rust branch/control-flow support is established.",
            "Branch/control-flow re-ingest is generally supported.",
            "Full non-generated C/Rust source roundtrip is supported.",
            "Compiler correctness has been proved.",
            "Formal semantic equivalence has been proved.",
            "Runtime performance has been established.",
        ],
        "nextMilestones": [
            "Turn the selected expected-sample fixture into a runtime comparison gate.",
            "Build an assignment/phi fixture gate for dominance and merge semantics.",
            "Keep nested branch support blocked until lowering and re-ingest evidence exists.",
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
        "title": "FEF-P63 Nested Branch Expected Samples",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "nested_branch_expected_samples_recorded_support_blocked",
        "semanticReview": payload["summary"],
        "claimBoundary": "Expected-sample fixture only; no nested branch execution, lowering, support, frontend widening, branch re-ingest, full source roundtrip, arbitrary source-family, public readiness, compiler correctness, formal equivalence, or runtime performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "P63 records deterministic expected samples for c_nested_if_return_v0.",
            "The fixture remains blocked and source-semantics-only.",
            "Nested branch support and general branch/control-flow claims remain blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p63_nested_branch_expected_samples.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p63_nested_branch_expected_samples.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p63_nested_branch_expected_samples.v0",
        "date": DATE,
        "title": "FEF-P63 Nested Branch Expected Samples",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Turn the selected expected-sample fixture into a runtime comparison gate.",
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
            "# FEF-P63 Nested Branch Expected Samples",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            "FEF-P63 attaches deterministic expected samples to one blocked nested-branch fixture.",
            "",
            "## Summary",
            "",
            f"- Selected fixture: `{summary['selectedFixtureId']}`",
            f"- Selected fixture still blocked: `{summary['selectedFixtureStillBlocked']}`",
            f"- Samples: `{summary['sampleCount']}`",
            f"- Nonzero expected samples: `{summary['nonzeroExpectedCount']}`",
            f"- Zero expected samples: `{summary['zeroExpectedCount']}`",
            f"- Source semantics only: `{summary['allSamplesSourceSemanticsOnly']}`",
            f"- Nested branch runtime execution claim: `{summary['nestedBranchRuntimeExecutionClaim']}`",
            f"- Nested branch lowering claim: `{summary['nestedBranchLoweringClaim']}`",
            f"- Nested branch support claim: `{summary['nestedBranchSupportClaim']}`",
            "",
            "## Samples",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Expected samples only; no nested branch execution.",
            "- No nested branch lowering or support claim.",
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
    if sample["sourceSemanticsOnly"] is not True:
        raise ValueError("sample must remain source-semantics-only")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P63 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid FEF-P63 status")
    if payload["selectedFixture"]["id"] != SELECTED_FIXTURE_ID:
        raise ValueError("unexpected selected fixture")
    p62.validate_fixture(payload["selectedFixture"])
    for sample in payload["expectedSamples"]:
        validate_sample(sample)
    summary = payload["summary"]
    for key in ["p62ValidationPass", "p62ClaimFlagsAllFalse", "selectedFixtureStillBlocked", "allSamplesSourceSemanticsOnly", "claimFlagsAllFalse"]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["sampleCount"] != 7:
        raise ValueError("expected seven samples")
    if summary["nonzeroExpectedCount"] != 2 or summary["zeroExpectedCount"] != 5:
        raise ValueError("unexpected expected-value distribution")
    for key in [
        "nestedBranchRuntimeExecutionClaim",
        "nestedBranchLoweringClaim",
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
    result_path = out_dir / f"fef_p63_nested_branch_expected_samples_{STAMP}.json"
    report_path = report_dir / f"fef_p63_nested_branch_expected_samples_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p63_nested_branch_expected_samples.json"
    feed_path = command_feed_dir / f"fef_p63_nested_branch_expected_samples_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p63_nested_branch_expected_samples")
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
    print("FEF_P63_NESTED_BRANCH_EXPECTED_SAMPLES_OK")
    print(f"samples={built['payload']['summary']['sampleCount']}")
    print(f"selected_fixture={built['payload']['summary']['selectedFixtureId']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
