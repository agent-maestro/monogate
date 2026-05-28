#!/usr/bin/env python3
"""EML-R10B runtime bakeoff.

Consumes R12 generated lowering stubs and validates them on broader deterministic
float64/float32 grids. This is local runtime evidence only: no compiler
correctness, formal semantic equivalence, public performance, deployment, or
hardware claim.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
from typing import Any, Callable

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_language_kernel import DATE  # noqa: E402
from scripts.eml_r10_cost_stability_lab import case_specs, deterministic_inputs  # noqa: E402
from scripts.eml_r12_generated_lowering_stubs import ARGUMENTS, compile_stub  # noqa: E402

SCHEMA_VERSION = "monogate.eml_r10b_runtime_bakeoff.v0"
BAKEOFF_PACKET_SCHEMA_VERSION = "monogate.eml_runtime_bakeoff_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_R10B_RUNTIME_BAKEOFF_PASS"

CLAIM_FLAGS = {
    "public_ready": False,
    "public_performance_claim": False,
    "public_savings_claim": False,
    "compiler_correctness_claim": False,
    "semantic_equivalence_claim": False,
    "formal_verification_claim": False,
    "production_lowering_claim": False,
    "deploy_performed": False,
    "hardware_observed": False,
    "gpu_measurement_claim": False,
    "embedded_measurement_claim": False,
}

NON_CLAIMS = [
    "R10B records local runtime bakeoff evidence only.",
    "R10B does not claim compiler correctness or formal semantic equivalence.",
    "R10B does not make public performance, savings, hardware, GPU, or embedded claims.",
    "R10B does not change Forge/compiler behavior or deploy generated code.",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def case_spec_by_id() -> dict[str, Any]:
    return {spec.case_id: spec for spec in case_specs()}


def broader_inputs(case_id: str, dtype: np.dtype[Any]) -> dict[str, np.ndarray]:
    spec = case_spec_by_id()[case_id]
    base_values = deterministic_inputs(spec)
    values: dict[str, np.ndarray] = {}
    for name, base in base_values.items():
        low, high = spec.ranges[name]
        edges = np.array([low, high, (low + high) / 2.0], dtype=np.float64)
        if low > 0:
            geometric = np.geomspace(low, high, num=257, dtype=np.float64)
            dense = np.concatenate([base, geometric, edges])
        else:
            dense = np.concatenate([base, np.linspace(low, high, 257, dtype=np.float64), edges])
        values[name] = dense.astype(dtype)
    return values


def timed_call(fn: Callable[..., Any], args: list[np.ndarray], repeats: int = 7) -> tuple[np.ndarray, float]:
    best = float("inf")
    observed = None
    for _ in range(repeats):
        start = time.perf_counter_ns()
        with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
            candidate = fn(*args)
        elapsed = time.perf_counter_ns() - start
        best = min(best, elapsed / max(1, args[0].size))
        observed = candidate
    assert observed is not None
    return np.asarray(observed), float(best)


def reference_for(case_id: str, values: dict[str, np.ndarray]) -> np.ndarray:
    spec = case_spec_by_id()[case_id]
    reference_values = {key: np.asarray(value, dtype=np.float64) for key, value in values.items()}
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        return np.asarray(spec.reference_fn(reference_values), dtype=np.float64)


def dtype_result(case_id: str, fn: Callable[..., Any], dtype_name: str) -> dict[str, Any]:
    dtype = np.float64 if dtype_name == "float64" else np.float32
    values = broader_inputs(case_id, np.dtype(dtype))
    args = [values[name] for name in ARGUMENTS[case_id]]
    observed, ns_per_sample = timed_call(fn, args)
    reference = reference_for(case_id, values)
    observed64 = np.asarray(observed, dtype=np.float64)
    finite = np.isfinite(observed64)
    comparable = finite & np.isfinite(reference)
    errors = np.abs(observed64[comparable] - reference[comparable])
    denominators = np.maximum(np.abs(reference[comparable]), 1.0e-12)
    rel_errors = errors / denominators
    max_abs = float(np.max(errors)) if errors.size else float("inf")
    max_rel = float(np.max(rel_errors)) if rel_errors.size else float("inf")
    tolerances = {
        "maxAbsError": 1.0e-9 if dtype_name == "float64" else 1.0e-4,
        "maxRelError": 1.0e-9 if dtype_name == "float64" else 1.0e-4,
    }
    # Float32 can have large absolute error on large-magnitude outputs and
    # large relative error near zero. Passing either tolerance is the intended
    # local-runtime criterion for this bakeoff.
    status = (
        "pass"
        if bool(np.all(finite))
        and (max_abs <= tolerances["maxAbsError"] or max_rel <= tolerances["maxRelError"])
        else "fail"
    )
    return {
        "dtype": dtype_name,
        "status": status,
        "sampleCount": int(observed64.size),
        "finiteRatio": float(np.mean(finite)),
        "nanOrInfCount": int(observed64.size - np.count_nonzero(finite)),
        "maxAbsError": max_abs,
        "maxRelError": max_rel,
        "latencyNsPerSample": ns_per_sample,
        "tolerances": tolerances,
    }


def packet_from_stub(stub_packet: dict[str, Any]) -> dict[str, Any]:
    case_id = stub_packet["caseId"]
    fn = compile_stub(case_id, stub_packet["pythonSource"])
    dtype_results = [dtype_result(case_id, fn, "float64"), dtype_result(case_id, fn, "float32")]
    status = "pass" if all(item["status"] == "pass" for item in dtype_results) else "fail"
    return {
        "schemaVersion": BAKEOFF_PACKET_SCHEMA_VERSION,
        "packetType": "eml_runtime_bakeoff_packet_v0",
        "date": DATE,
        "caseId": case_id,
        "sourceStubFunction": stub_packet["pythonFunctionName"],
        "loweredExpression": stub_packet["loweredExpression"],
        "runtimeStatus": status,
        "dtypeResults": dtype_results,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def summarize(packets: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "bakeoffPacketCount": len(packets),
        "passCount": sum(1 for packet in packets if packet["runtimeStatus"] == "pass"),
        "failCount": sum(1 for packet in packets if packet["runtimeStatus"] == "fail"),
        "dtypeRunCount": sum(len(packet["dtypeResults"]) for packet in packets),
        "worstFiniteRatio": min(item["finiteRatio"] for packet in packets for item in packet["dtypeResults"]),
        "maxAbsError": max(item["maxAbsError"] for packet in packets for item in packet["dtypeResults"]),
        "maxRelError": max(item["maxRelError"] for packet in packets for item in packet["dtypeResults"]),
        "runtimeBakeoffPerformed": True,
        "compilerBehaviorChanged": False,
        "semanticEquivalenceClaim": False,
        "compilerCorrectnessClaim": False,
        "publicPerformanceClaim": False,
        "hardwareMeasurementClaim": False,
        "claimFlagsAllFalse": all(all(value is False for value in packet["claimFlags"].values()) for packet in packets),
    }


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-r10b-runtime-bakeoff",
        "title": "EML-R10B Runtime Bakeoff",
        "reviewDecision": "local_runtime_bakeoff_recorded",
        "validationStatus": "pass",
        "replayStatus": "not_applicable",
        "semanticStrength": "local_runtime_bakeoff_no_compiler_correctness_claim",
        "semanticReview": {
            "bakeoffPacketCount": payload["summary"]["bakeoffPacketCount"],
            "passCount": payload["summary"]["passCount"],
            "failCount": payload["summary"]["failCount"],
            "dtypeRunCount": payload["summary"]["dtypeRunCount"],
            "compilerBehaviorChanged": False,
            "semanticEquivalenceClaim": False,
            "publicPerformanceClaim": False,
        },
        "claimBoundary": "Local runtime bakeoff of generated Python stubs only; no compiler correctness, semantic equivalence, public performance, deployment, or hardware claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Consumes R12 generated lowering stub packets.",
            "Runs broader deterministic float64 and float32 grids.",
            "Records finite ratio, error, and simple local latency per case.",
            "Advances compiler claims only to scoped semantic proof review.",
        ],
        "validationCommands": [
            "python python/scripts/eml_r10b_runtime_bakeoff.py --build --strict",
            "python -m pytest -q python/tests/test_eml_r10b_runtime_bakeoff.py",
        ],
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_r10b.v0",
        "date": DATE,
        "title": "EML-R10B Runtime Bakeoff",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "R10C scoped semantic proof",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-R10B Runtime Bakeoff",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "R10B validates R12 generated Python stubs on broader deterministic",
        "float64 and float32 grids. It is local runtime evidence, not compiler",
        "correctness or formal semantic equivalence.",
        "",
        "| Case | Runtime | Float64 max rel | Float32 max rel | Float64 ns/sample | Float32 ns/sample |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for packet in payload["bakeoffPackets"]:
        by_dtype = {item["dtype"]: item for item in packet["dtypeResults"]}
        lines.append(
            f"| `{packet['caseId']}` | `{packet['runtimeStatus']}` | "
            f"{by_dtype['float64']['maxRelError']:.3e} | {by_dtype['float32']['maxRelError']:.3e} | "
            f"{by_dtype['float64']['latencyNsPerSample']:.1f} | {by_dtype['float32']['latencyNsPerSample']:.1f} |"
        )
    summary = payload["summary"]
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Bakeoff packets: `{summary['bakeoffPacketCount']}`",
            f"- Pass: `{summary['passCount']}`",
            f"- Fail: `{summary['failCount']}`",
            f"- Dtype runs: `{summary['dtypeRunCount']}`",
            f"- Compiler behavior changed: `{summary['compilerBehaviorChanged']}`",
            f"- Compiler correctness claim: `{summary['compilerCorrectnessClaim']}`",
            "",
            "## Boundary",
            "",
            "- Local generated Python stub bakeoff only.",
            "- No compiler correctness claim.",
            "- No formal semantic equivalence claim.",
            "- No public performance, hardware, deployment, or production lowering claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid R10B schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid R10B status")
    summary = payload["summary"]
    if summary["bakeoffPacketCount"] < 7:
        raise ValueError("expected at least 7 bakeoff packets")
    if summary["failCount"] != 0:
        raise ValueError("all R10B bakeoff packets must pass")
    for key in [
        "compilerBehaviorChanged",
        "semanticEquivalenceClaim",
        "compilerCorrectnessClaim",
        "publicPerformanceClaim",
        "hardwareMeasurementClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["runtimeBakeoffPerformed"] is not True:
        raise ValueError("runtime bakeoff should be marked performed")
    for key, value in payload.get("claimFlags", {}).items():
        if value is not False:
            raise ValueError(f"payload claim flag must remain false: {key}")
    for packet in payload["bakeoffPackets"]:
        if packet.get("schemaVersion") != BAKEOFF_PACKET_SCHEMA_VERSION:
            raise ValueError(f"invalid bakeoff packet schema: {packet.get('caseId')}")
        if packet["runtimeStatus"] != "pass":
            raise ValueError(f"bakeoff failed: {packet['caseId']}")
        for item in packet["dtypeResults"]:
            if item["status"] != "pass":
                raise ValueError(f"dtype bakeoff failed: {packet['caseId']} {item['dtype']}")
        for key, value in packet.get("claimFlags", {}).items():
            if value is not False:
                raise ValueError(f"packet claim flag must remain false for {packet['caseId']}: {key}")


def build_bakeoff(
    r12_path: Path,
    out_dir: Path,
    packet_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
) -> dict[str, Any]:
    r12 = load_json(r12_path)
    packets = [packet_from_stub(packet) for packet in r12["stubPackets"]]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "sourceR12Path": str(r12_path),
        "bakeoffPackets": packets,
        "summary": summarize(packets),
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
    result_path = out_dir / f"eml_r10b_runtime_bakeoff_{stamp}.json"
    report_path = report_dir / f"eml_r10b_runtime_bakeoff_{stamp}.md"
    evidence_path = evidence_dir / "eml_r10b_runtime_bakeoff.json"
    feed_path = command_feed_dir / f"eml_r10b_runtime_bakeoff_feed_{stamp}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in packets:
        path = packet_dir / f"{packet['caseId']}_runtime_bakeoff_packet_{stamp}.json"
        path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
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
    parser.add_argument(
        "--r12-path",
        type=Path,
        default=ROOT / f"python/results/eml_r12_generated_lowering_stubs/eml_r12_generated_lowering_stubs_{DATE.replace('-', '_')}.json",
    )
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_r10b_runtime_bakeoff")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_runtime_bakeoff_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_bakeoff(args.r12_path, args.out_dir, args.packet_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("EML_R10B_RUNTIME_BAKEOFF_OK")
    print(f"bakeoff_packets={built['payload']['summary']['bakeoffPacketCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
