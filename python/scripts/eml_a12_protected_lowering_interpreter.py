#!/usr/bin/env python3
"""EML-A12 tiny protected-lowering interpreter.

Runs a bounded interpreter over guard-approved protected lowering cases. This
is executable fixture evidence only: no compiler implementation, no compiler
correctness proof, and no runtime performance claim.
"""

from __future__ import annotations

import argparse
from decimal import Decimal, getcontext
import json
import math
from pathlib import Path
import sys
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_language_kernel import DATE  # noqa: E402

SCHEMA_VERSION = "monogate.eml_a12_protected_lowering_interpreter.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_protected_lowering_interpreter_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_A12_PROTECTED_LOWERING_INTERPRETER_PASS"

CLAIM_FLAGS = {
    "public_ready": False,
    "real_compiler_behavior_changed": False,
    "compiler_implementation_claim": False,
    "compiler_correctness_claim": False,
    "formal_semantic_equivalence_claim": False,
    "runtime_performance_claim": False,
    "production_lowering_claim": False,
    "hardware_measurement_claim": False,
    "general_eml_advantage_claim": False,
    "deploy_performed": False,
    "package_published": False,
}

NON_CLAIMS = [
    "A12 is a tiny fixture interpreter over selected protected lowering cases.",
    "A12 does not implement a production compiler or change Forge/compiler behavior.",
    "A12 does not prove compiler correctness or formal semantic equivalence.",
    "A12 does not claim runtime performance, hardware measurement, production readiness, or general EML advantage.",
]

getcontext().prec = 90


def dec(x: float) -> Decimal:
    return Decimal(str(x))


def reference_expm1(sample: dict[str, Any]) -> Decimal:
    return dec(sample["x"]).exp() - Decimal(1)


def naive_expm1(sample: dict[str, Any]) -> float:
    return math.exp(float(sample["x"])) - 1.0


def protected_expm1(sample: dict[str, Any]) -> float:
    return math.expm1(float(sample["x"]))


def reference_logsumexp(sample: dict[str, Any]) -> Decimal:
    values = [dec(float(value)) for value in sample["values"]]
    max_value = max(values)
    total = sum((value - max_value).exp() for value in values)
    return max_value + total.ln()


def naive_logsumexp(sample: dict[str, Any]) -> float:
    try:
        return math.log(sum(math.exp(float(value)) for value in sample["values"]))
    except (OverflowError, ValueError):
        return float("inf")


def protected_logsumexp(sample: dict[str, Any]) -> float:
    values = [float(value) for value in sample["values"]]
    max_value = max(values)
    return max_value + math.log(sum(math.exp(value - max_value) for value in values))


def finite_float(value: float) -> bool:
    return math.isfinite(float(value))


def abs_error(value: float, reference: Decimal) -> float | str:
    if not finite_float(value):
        return "inf"
    return float(abs(Decimal(str(value)) - reference))


def protected_no_worse(naive_error: float | str, protected_error: float | str) -> bool:
    if protected_error == "inf":
        return False
    if naive_error == "inf":
        return True
    return float(protected_error) <= float(naive_error)


CaseFns = tuple[Callable[[dict[str, Any]], Decimal], Callable[[dict[str, Any]], float], Callable[[dict[str, Any]], float]]

CASES: list[dict[str, Any]] = [
    {
        "caseId": "expm1_near_zero_interpreter_v0",
        "sourceShape": "eml(x,e)",
        "guardDecision": "recommend_protected_lowering",
        "mockCompilerDecision": "protected_runtime_lowering",
        "recommendedLowering": "expm1",
        "matchedRules": ["lower_expm1_near_zero_v0"],
        "requiredGuards": ["finite x", "near-zero cancellation risk acknowledged"],
        "samples": [{"x": x} for x in [-1e-12, -1e-10, -1e-8, -1e-6, 0.0, 1e-12, 1e-10, 1e-8, 1e-6]],
    },
    {
        "caseId": "logsumexp_edge_grid_interpreter_v0",
        "sourceShape": "ln(sum(exp(x_i)))",
        "guardDecision": "recommend_protected_lowering",
        "mockCompilerDecision": "protected_runtime_lowering",
        "recommendedLowering": "max_shifted_logsumexp",
        "matchedRules": ["lower_logaddexp_softplus_v0"],
        "requiredGuards": ["finite inputs", "non-empty input vector"],
        "samples": [
            {"values": [-1000.0, -1001.0]},
            {"values": [-745.0, -746.0]},
            {"values": [0.0, 0.0]},
            {"values": [50.0, 49.0]},
            {"values": [700.0, 699.0]},
            {"values": [1000.0, 999.0]},
            {"values": [1000.0, 999.0, 998.0]},
        ],
    },
]


CASE_FNS: dict[str, CaseFns] = {
    "expm1_near_zero_interpreter_v0": (reference_expm1, naive_expm1, protected_expm1),
    "logsumexp_edge_grid_interpreter_v0": (reference_logsumexp, naive_logsumexp, protected_logsumexp),
}


def run_case(case: dict[str, Any]) -> dict[str, Any]:
    reference_fn, naive_fn, protected_fn = CASE_FNS[case["caseId"]]
    frames = []
    for index, sample in enumerate(case["samples"]):
        reference = reference_fn(sample)
        naive_value = naive_fn(sample)
        protected_value = protected_fn(sample)
        naive_error = abs_error(naive_value, reference)
        protected_error = abs_error(protected_value, reference)
        frames.append(
            {
                "frameIndex": index,
                "sample": sample,
                "reference": str(reference),
                "naiveValue": "inf" if math.isinf(naive_value) else naive_value,
                "protectedValue": "inf" if math.isinf(protected_value) else protected_value,
                "naiveAbsError": naive_error,
                "protectedAbsError": protected_error,
                "protectedNoWorse": protected_no_worse(naive_error, protected_error),
                "naiveFinite": finite_float(naive_value),
                "protectedFinite": finite_float(protected_value),
            }
        )
    protected_better = sum(
        1
        for frame in frames
        if frame["protectedAbsError"] != "inf"
        and (frame["naiveAbsError"] == "inf" or float(frame["protectedAbsError"]) < float(frame["naiveAbsError"]))
    )
    protected_no_worse_count = sum(1 for frame in frames if frame["protectedNoWorse"])
    naive_nonfinite = sum(1 for frame in frames if not frame["naiveFinite"])
    protected_nonfinite = sum(1 for frame in frames if not frame["protectedFinite"])
    packet = {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_protected_lowering_interpreter_packet_v0",
        "date": DATE,
        "caseId": case["caseId"],
        "sourceShape": case["sourceShape"],
        "guardDecision": case["guardDecision"],
        "mockCompilerDecision": case["mockCompilerDecision"],
        "recommendedLowering": case["recommendedLowering"],
        "matchedRules": case["matchedRules"],
        "requiredGuards": case["requiredGuards"],
        "frames": frames,
        "summary": {
            "frameCount": len(frames),
            "protectedBetterCount": protected_better,
            "protectedNoWorseCount": protected_no_worse_count,
            "naiveNonFiniteCount": naive_nonfinite,
            "protectedNonFiniteCount": protected_nonfinite,
            "allProtectedFinite": protected_nonfinite == 0,
            "allProtectedNoWorse": protected_no_worse_count == len(frames),
        },
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_case_packet(packet)
    return packet


def summarize(case_packets: list[dict[str, Any]]) -> dict[str, Any]:
    frame_count = sum(packet["summary"]["frameCount"] for packet in case_packets)
    protected_better = sum(packet["summary"]["protectedBetterCount"] for packet in case_packets)
    protected_no_worse = sum(packet["summary"]["protectedNoWorseCount"] for packet in case_packets)
    naive_nonfinite = sum(packet["summary"]["naiveNonFiniteCount"] for packet in case_packets)
    protected_nonfinite = sum(packet["summary"]["protectedNonFiniteCount"] for packet in case_packets)
    return {
        "caseCount": len(case_packets),
        "frameCount": frame_count,
        "protectedBetterCount": protected_better,
        "protectedNoWorseCount": protected_no_worse,
        "naiveNonFiniteCount": naive_nonfinite,
        "protectedNonFiniteCount": protected_nonfinite,
        "interpreterExecuted": True,
        "realCompilerBehaviorChanged": False,
        "compilerImplementationClaim": False,
        "compilerCorrectnessClaim": False,
        "formalSemanticEquivalenceClaim": False,
        "runtimePerformanceClaim": False,
        "productionLoweringClaim": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-a12-protected-lowering-interpreter",
        "title": "EML-A12 Protected Lowering Interpreter",
        "reviewDecision": "tiny_protected_lowering_interpreter_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_numeric_interpreter_frames",
        "semanticStrength": "executable_fixture_interpreter_no_compiler_correctness_claim",
        "semanticReview": payload["summary"],
        "claimBoundary": "Tiny protected-lowering interpreter only; no production compiler, formal semantic equivalence, runtime performance, hardware measurement, or compiler correctness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_a12.v0",
        "date": DATE,
        "title": "EML-A12 Protected Lowering Interpreter",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "R10F proof-assistant AST and guard model",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-A12 Protected Lowering Interpreter",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "A12 runs a tiny deterministic interpreter over protected-lowering",
        "cases selected by the guard/mock-compiler lane.",
        "",
        "| Case | Frames | Protected no-worse | Naive non-finite | Protected non-finite |",
        "|---|---:|---:|---:|---:|",
    ]
    for packet in payload["casePackets"]:
        summary = packet["summary"]
        lines.append(
            f"| `{packet['caseId']}` | {summary['frameCount']} | {summary['protectedNoWorseCount']} | {summary['naiveNonFiniteCount']} | {summary['protectedNonFiniteCount']} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Executable fixture interpreter only.",
            "- No compiler behavior change.",
            "- No compiler correctness or formal semantic equivalence claim.",
            "- No runtime performance, hardware measurement, production lowering, or general EML advantage claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_case_packet(packet: dict[str, Any]) -> None:
    if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid A12 case packet schema")
    if packet["summary"]["frameCount"] <= 0:
        raise ValueError("case packet must contain interpreter frames")
    if packet["summary"]["allProtectedFinite"] is not True:
        raise ValueError("protected path must remain finite in A12 fixtures")
    if packet["summary"]["allProtectedNoWorse"] is not True:
        raise ValueError("protected path must be no worse in A12 fixtures")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"case packet claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid A12 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid A12 status")
    summary = payload["summary"]
    if summary["caseCount"] < 2:
        raise ValueError("expected at least two protected-lowering cases")
    if summary["frameCount"] < 12:
        raise ValueError("expected at least 12 interpreter frames")
    if summary["protectedNonFiniteCount"] != 0:
        raise ValueError("protected path should remain finite")
    for key in [
        "realCompilerBehaviorChanged",
        "compilerImplementationClaim",
        "compilerCorrectnessClaim",
        "formalSemanticEquivalenceClaim",
        "runtimePerformanceClaim",
        "productionLoweringClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("A12 claim flags must remain false")
    for packet in payload["casePackets"]:
        validate_case_packet(packet)


def build_interpreter(
    out_dir: Path,
    packet_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
) -> dict[str, Any]:
    case_packets = [run_case(case) for case in CASES]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "interpreterId": "eml_a12_protected_lowering_interpreter",
        "casePackets": case_packets,
        "summary": summarize(case_packets),
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    evidence = build_evidence_packet(payload)
    feed = command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    packet_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    stamp = DATE.replace("-", "_")
    result_path = out_dir / f"eml_a12_protected_lowering_interpreter_{stamp}.json"
    report_path = report_dir / f"eml_a12_protected_lowering_interpreter_{stamp}.md"
    evidence_path = evidence_dir / "eml_a12_protected_lowering_interpreter.json"
    feed_path = command_feed_dir / f"eml_a12_protected_lowering_interpreter_feed_{stamp}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in case_packets:
        packet_path = packet_dir / f"{packet['caseId']}_{stamp}.json"
        packet_path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "evidence": evidence,
        "feed": feed,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_a12_protected_lowering_interpreter")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_protected_lowering_interpreter_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_interpreter(args.out_dir, args.packet_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("EML_A12_PROTECTED_LOWERING_INTERPRETER_OK")
    print(f"cases={built['payload']['summary']['caseCount']}")
    print(f"frames={built['payload']['summary']['frameCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
