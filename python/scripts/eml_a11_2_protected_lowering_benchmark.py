#!/usr/bin/env python3
"""EML-A11.2 protected-lowering fixture benchmark.

Compares naive and protected numeric forms for guard-recommended lowerings.
This records deterministic stability evidence only; it is not a speed claim,
compiler implementation, or compiler-correctness proof.
"""

from __future__ import annotations

import argparse
from decimal import Decimal, getcontext
import json
import math
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_a11_1_mock_compiler_holdouts import CLAIM_FLAGS as A11_1_CLAIM_FLAGS  # noqa: E402
from scripts.eml_language_kernel import DATE  # noqa: E402

SCHEMA_VERSION = "monogate.eml_a11_2_protected_lowering_benchmark.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_protected_lowering_benchmark_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_A11_2_PROTECTED_LOWERING_BENCHMARK_PASS"

CLAIM_FLAGS = {
    **dict(A11_1_CLAIM_FLAGS),
    "protected_lowering_runtime_performance_claim": False,
    "protected_lowering_compiler_implementation_claim": False,
    "protected_lowering_compiler_correctness_claim": False,
}

NON_CLAIMS = [
    "A11.2 compares naive and protected numeric forms on deterministic edge grids.",
    "A11.2 does not measure speed, latency, energy, throughput, or production runtime performance.",
    "A11.2 does not implement or verify a real compiler lowering.",
    "A11.2 does not claim compiler correctness, production readiness, public Atlas promotion, or EML advantage.",
]

getcontext().prec = 80


def decimal_exp_minus_one(x: float) -> Decimal:
    return Decimal(str(x)).exp() - Decimal(1)


def decimal_logsumexp(values: list[float]) -> Decimal:
    decimals = [Decimal(str(value)) for value in values]
    max_value = max(decimals)
    total = sum((value - max_value).exp() for value in decimals)
    return max_value + total.ln()


def abs_error(value: float, reference: Decimal) -> float:
    if not math.isfinite(value):
        return float("inf")
    return float(abs(Decimal(str(value)) - reference))


def expm1_case() -> dict[str, Any]:
    samples = [-1e-12, -1e-10, -1e-8, -1e-6, -1e-4, 0.0, 1e-12, 1e-10, 1e-8, 1e-6, 1e-4]
    rows = []
    for x in samples:
        reference = decimal_exp_minus_one(x)
        naive = math.exp(x) - 1.0
        protected = math.expm1(x)
        naive_error = abs_error(naive, reference)
        protected_error = abs_error(protected, reference)
        rows.append({
            "sample": {"x": x},
            "reference": str(reference),
            "naiveValue": naive,
            "protectedValue": protected,
            "naiveAbsError": naive_error,
            "protectedAbsError": protected_error,
            "protectedNoWorse": protected_error <= naive_error,
        })
    return summarize_case("expm1_near_zero", "eml(x,e)", "expm1-style protected lowering", rows)


def logaddexp_value(values: list[float]) -> float:
    max_value = max(values)
    return max_value + math.log(sum(math.exp(value - max_value) for value in values))


def naive_logsumexp(values: list[float]) -> float:
    try:
        return math.log(sum(math.exp(value) for value in values))
    except (OverflowError, ValueError):
        return float("inf")


def logsumexp_case() -> dict[str, Any]:
    samples = [
        [-1000.0, -1001.0],
        [-745.0, -746.0],
        [-50.0, -51.0],
        [0.0, 0.0],
        [50.0, 49.0],
        [700.0, 699.0],
        [1000.0, 999.0],
        [-1000.0, -1001.0, -1002.0],
        [1000.0, 999.0, 998.0],
    ]
    rows = []
    for values in samples:
        reference = decimal_logsumexp(values)
        naive = naive_logsumexp(values)
        protected = logaddexp_value(values)
        naive_error = abs_error(naive, reference)
        protected_error = abs_error(protected, reference)
        rows.append({
            "sample": {"values": values},
            "reference": str(reference),
            "naiveValue": "inf" if math.isinf(naive) else naive,
            "protectedValue": protected,
            "naiveAbsError": "inf" if math.isinf(naive_error) else naive_error,
            "protectedAbsError": protected_error,
            "protectedNoWorse": protected_error <= naive_error,
        })
    return summarize_case("logsumexp_edge_grid", "ln(sum(exp(x_i)))", "logaddexp-style protected lowering", rows)


def summarize_case(case_id: str, expression_shape: str, lowering: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    protected_better = 0
    protected_no_worse = 0
    naive_nonfinite = 0
    protected_nonfinite = 0
    max_naive_error = 0.0
    max_protected_error = 0.0
    for row in rows:
        naive_error = float("inf") if row["naiveAbsError"] == "inf" else float(row["naiveAbsError"])
        protected_error = float(row["protectedAbsError"])
        if naive_error == float("inf"):
            naive_nonfinite += 1
        if not math.isfinite(float(row["protectedValue"])):
            protected_nonfinite += 1
        if protected_error < naive_error:
            protected_better += 1
        if protected_error <= naive_error:
            protected_no_worse += 1
        if math.isfinite(naive_error):
            max_naive_error = max(max_naive_error, naive_error)
        else:
            max_naive_error = float("inf")
        max_protected_error = max(max_protected_error, protected_error)
    return {
        "caseId": case_id,
        "expressionShape": expression_shape,
        "recommendedLowering": lowering,
        "sampleCount": len(rows),
        "protectedBetterCount": protected_better,
        "protectedNoWorseCount": protected_no_worse,
        "naiveNonFiniteCount": naive_nonfinite,
        "protectedNonFiniteCount": protected_nonfinite,
        "maxNaiveAbsError": "inf" if math.isinf(max_naive_error) else max_naive_error,
        "maxProtectedAbsError": max_protected_error,
        "rows": rows,
        "interpretation": "Protected numeric form is stability-preferred on this deterministic edge grid.",
        "blockedClaims": ["runtime performance", "compiler correctness", "production readiness", "general EML superiority"],
    }


def summarize(cases: list[dict[str, Any]]) -> dict[str, Any]:
    sample_count = sum(case["sampleCount"] for case in cases)
    protected_better = sum(case["protectedBetterCount"] for case in cases)
    protected_no_worse = sum(case["protectedNoWorseCount"] for case in cases)
    naive_nonfinite = sum(case["naiveNonFiniteCount"] for case in cases)
    protected_nonfinite = sum(case["protectedNonFiniteCount"] for case in cases)
    return {
        "caseCount": len(cases),
        "sampleCount": sample_count,
        "protectedBetterCount": protected_better,
        "protectedNoWorseCount": protected_no_worse,
        "naiveNonFiniteCount": naive_nonfinite,
        "protectedNonFiniteCount": protected_nonfinite,
        "numericStabilityEvidenceRecorded": True,
        "runtimePerformanceClaim": False,
        "compilerImplementationClaim": False,
        "compilerCorrectnessClaim": False,
        "productionReady": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }


def build_benchmark(out_dir: Path, packet_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    cases = [expm1_case(), logsumexp_case()]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "eml_protected_lowering_benchmark_packet_v0",
        "date": DATE,
        "status": STATUS,
        "benchmarkId": "eml_a11_2_protected_lowering_benchmark",
        "cases": cases,
        "summary": summarize(cases),
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
    result_path = out_dir / f"eml_a11_2_protected_lowering_benchmark_{stamp}.json"
    packet_path = packet_dir / f"eml_a11_2_protected_lowering_benchmark_{stamp}.json"
    report_path = report_dir / f"eml_a11_2_protected_lowering_benchmark_{stamp}.md"
    evidence_path = evidence_dir / "eml_a11_2_protected_lowering_benchmark.json"
    feed_path = command_feed_dir / f"eml_a11_2_protected_lowering_benchmark_feed_{stamp}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    packet_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"payload": payload, "evidence": evidence, "feed": feed, "result_path": str(result_path), "packet_path": str(packet_path), "report_path": str(report_path), "evidence_path": str(evidence_path), "feed_path": str(feed_path)}


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-a11-2-protected-lowering-benchmark",
        "title": "EML-A11.2 Protected Lowering Benchmark",
        "reviewDecision": "protected_lowering_stability_evidence_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_numeric_grid",
        "semanticStrength": "stability_fixture_no_runtime_performance_claim",
        "semanticReview": payload["summary"],
        "claimBoundary": "Protected-lowering stability fixture only; no speed, compiler implementation, compiler correctness, production readiness, or EML advantage claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_a11_2.v0",
        "date": DATE,
        "title": "EML-A11.2 Protected Lowering Benchmark",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "A11.3 connect protected-lowering stability evidence back into the builder/export review flow",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-A11.2 Protected Lowering Benchmark",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "| Case | Samples | Protected better | Protected no worse | Naive non-finite | Protected non-finite |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for case in payload["cases"]:
        lines.append(
            f"| `{case['caseId']}` | {case['sampleCount']} | {case['protectedBetterCount']} | {case['protectedNoWorseCount']} | {case['naiveNonFiniteCount']} | {case['protectedNonFiniteCount']} |"
        )
    lines.extend([
        "",
        "## Boundary",
        "",
        "- Numeric stability fixture only.",
        "- No speed, latency, energy, throughput, compiler implementation, compiler correctness, production readiness, or EML advantage claim.",
        "",
    ])
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION or payload["status"] != STATUS:
        raise ValueError("invalid A11.2 payload")
    summary = payload["summary"]
    if summary["caseCount"] != 2:
        raise ValueError("expected exactly two protected lowering cases")
    if summary["sampleCount"] < 18:
        raise ValueError("expected edge-grid samples")
    if summary["protectedNoWorseCount"] != summary["sampleCount"]:
        raise ValueError("protected lowering should be no worse on all fixture samples")
    if summary["naiveNonFiniteCount"] < 1:
        raise ValueError("expected at least one naive non-finite edge case")
    if summary["protectedNonFiniteCount"] != 0:
        raise ValueError("protected lowering should remain finite on fixture samples")
    for key in ["runtimePerformanceClaim", "compilerImplementationClaim", "compilerCorrectnessClaim", "productionReady"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_a11_2_protected_lowering_benchmark")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_protected_lowering_benchmark_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_benchmark(args.out_dir, args.packet_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("EML_A11_2_PROTECTED_LOWERING_BENCHMARK_OK")
    print(f"cases={built['payload']['summary']['caseCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
