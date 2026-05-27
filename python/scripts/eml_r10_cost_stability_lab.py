#!/usr/bin/env python3
"""EML-R10 finite-precision cost and stability lab.

This lab turns the EML practicality critique into deterministic review
artifacts. It compares EML-shaped implementations against standard/protected
implementations for accuracy, finite-value behavior, simple latency, and static
operator count. It does not make public savings, proof, hardware, or discovery
claims.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
from pathlib import Path
import sys
import time
from typing import Any, Callable

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_language_kernel import DATE  # noqa: E402
from scripts.eml_packet_builder import DEFAULT_CLAIM_FLAGS  # noqa: E402

SCHEMA_VERSION = "monogate.eml_r10_cost_stability_lab.v0"
COST_PACKET_SCHEMA_VERSION = "monogate.eml_cost_packet.v0"
STATUS = "EML_R10_COST_STABILITY_LAB_PASS"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"


ArrayFn = Callable[[dict[str, np.ndarray]], np.ndarray]


@dataclass(frozen=True)
class CaseSpec:
    case_id: str
    family: str
    expression: str
    standard_expression: str
    ranges: dict[str, tuple[float, float]]
    eml_fn: ArrayFn
    standard_fn: ArrayFn
    reference_fn: ArrayFn
    sample_count: int = 2048


def eml(x: np.ndarray, y: np.ndarray | float) -> np.ndarray:
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        return np.exp(x) - np.log(y)


def protected_softplus(x: np.ndarray) -> np.ndarray:
    return np.logaddexp(x, 0.0)


def stable_sigmoid(x: np.ndarray) -> np.ndarray:
    positive = x >= 0
    out = np.empty_like(x, dtype=np.float64)
    out[positive] = 1.0 / (1.0 + np.exp(-x[positive]))
    ex = np.exp(x[~positive])
    out[~positive] = ex / (1.0 + ex)
    return out


def case_specs() -> list[CaseSpec]:
    return [
        CaseSpec(
            case_id="exp_from_eml_v0",
            family="atlas_exact_identity",
            expression="eml(x, 1)",
            standard_expression="exp(x)",
            ranges={"x": (-20.0, 20.0)},
            eml_fn=lambda v: eml(v["x"], 1.0),
            standard_fn=lambda v: np.exp(v["x"]),
            reference_fn=lambda v: np.exp(v["x"]),
        ),
        CaseSpec(
            case_id="subtraction_boundary_v0",
            family="atlas_exact_identity",
            expression="eml(ln(v), exp(u))",
            standard_expression="v - u",
            ranges={"v": (0.05, 50.0), "u": (-12.0, 12.0)},
            eml_fn=lambda v: eml(np.log(v["v"]), np.exp(v["u"])),
            standard_fn=lambda v: v["v"] - v["u"],
            reference_fn=lambda v: v["v"] - v["u"],
        ),
        CaseSpec(
            case_id="bose_boundary_expm1_v0",
            family="statistical_boundary",
            expression="eml(x, e)",
            standard_expression="expm1(x)",
            ranges={"x": (-1.0e-8, 1.0e-8)},
            eml_fn=lambda v: eml(v["x"], math.e),
            standard_fn=lambda v: np.expm1(v["x"]),
            reference_fn=lambda v: np.expm1(v["x"]),
        ),
        CaseSpec(
            case_id="ln_from_eml_v0",
            family="atlas_exact_identity",
            expression="eml(1, eml(eml(1, y), 1))",
            standard_expression="ln(y)",
            ranges={"y": (1.0e-9, 1.0e9)},
            eml_fn=lambda v: eml(np.ones_like(v["y"]), eml(eml(np.ones_like(v["y"]), v["y"]), 1.0)),
            standard_fn=lambda v: np.log(v["y"]),
            reference_fn=lambda v: np.log(v["y"]),
        ),
        CaseSpec(
            case_id="softplus_pair_v0",
            family="softplus_logsumexp",
            expression="ln(exp(a) + exp(b))",
            standard_expression="logaddexp(a, b)",
            ranges={"a": (-100.0, 100.0), "b": (-100.0, 100.0)},
            eml_fn=lambda v: np.log(np.exp(v["a"]) + np.exp(v["b"])),
            standard_fn=lambda v: np.logaddexp(v["a"], v["b"]),
            reference_fn=lambda v: np.logaddexp(v["a"], v["b"]),
        ),
        CaseSpec(
            case_id="sigmoid_derivative_v0",
            family="sigmoid_logistic",
            expression="(1 / (1 + exp(-x))) * (1 - (1 / (1 + exp(-x))))",
            standard_expression="stable_sigmoid(x) * (1 - stable_sigmoid(x))",
            ranges={"x": (-80.0, 80.0)},
            eml_fn=lambda v: (1.0 / (1.0 + np.exp(-v["x"]))) * (1.0 - (1.0 / (1.0 + np.exp(-v["x"])))),
            standard_fn=lambda v: stable_sigmoid(v["x"]) * (1.0 - stable_sigmoid(v["x"])),
            reference_fn=lambda v: stable_sigmoid(v["x"]) * (1.0 - stable_sigmoid(v["x"])),
        ),
        CaseSpec(
            case_id="gaussian_energy_v0",
            family="forge_efrog_fixture",
            expression="exp(-(x * x)) + exp(-(x * x))",
            standard_expression="2 * exp(-(x * x))",
            ranges={"x": (-30.0, 30.0)},
            eml_fn=lambda v: np.exp(-(v["x"] * v["x"])) + np.exp(-(v["x"] * v["x"])),
            standard_fn=lambda v: 2.0 * np.exp(-(v["x"] * v["x"])),
            reference_fn=lambda v: 2.0 * np.exp(-(v["x"] * v["x"])),
        ),
    ]


def deterministic_inputs(spec: CaseSpec) -> dict[str, np.ndarray]:
    values: dict[str, np.ndarray] = {}
    for index, (name, bounds) in enumerate(sorted(spec.ranges.items())):
        low, high = bounds
        base = np.linspace(low, high, spec.sample_count, dtype=np.float64)
        if index:
            base = np.roll(base, int(spec.sample_count / (index + 2)))
        values[name] = base
    return values


def operator_count(expression: str) -> int:
    tokens = ["eml(", "exp(", "expm1(", "ln(", "log", "logaddexp(", "stable_sigmoid(", "+", "-", "*", "/"]
    return sum(expression.count(token) for token in tokens)


def _run_timed(fn: ArrayFn, values: dict[str, np.ndarray], repeats: int = 9) -> tuple[np.ndarray, float]:
    best = float("inf")
    result = None
    for _ in range(repeats):
        start = time.perf_counter_ns()
        with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
            candidate = fn(values)
        elapsed = time.perf_counter_ns() - start
        best = min(best, elapsed / max(1, len(next(iter(values.values())))))
        result = candidate
    assert result is not None
    return np.asarray(result, dtype=np.float64), best


def _metrics(
    expression: str,
    observed: np.ndarray,
    reference: np.ndarray,
    latency_ns_per_sample: float,
) -> dict[str, Any]:
    finite = np.isfinite(observed)
    finite_reference = np.isfinite(reference)
    comparable = finite & finite_reference
    errors = np.abs(observed[comparable] - reference[comparable])
    denominators = np.maximum(np.abs(reference[comparable]), 1.0e-12)
    rel_errors = errors / denominators
    return {
        "sampleCount": int(observed.size),
        "finiteRatio": float(np.mean(finite)),
        "nanOrInfCount": int(observed.size - np.count_nonzero(finite)),
        "maxAbsError": float(np.max(errors)) if errors.size else float("inf"),
        "maxRelError": float(np.max(rel_errors)) if rel_errors.size else float("inf"),
        "latencyNsPerSample": float(latency_ns_per_sample),
        "operatorCount": operator_count(expression),
    }


def _stability_score(eml_metrics: dict[str, Any], standard_metrics: dict[str, Any]) -> float:
    finite_score = min(eml_metrics["finiteRatio"], standard_metrics["finiteRatio"])
    error_penalty = min(0.5, math.log10(1.0 + eml_metrics["maxAbsError"]) / 10.0)
    nan_penalty = 0.25 if eml_metrics["nanOrInfCount"] else 0.0
    return max(0.0, min(1.0, finite_score - error_penalty - nan_penalty))


def _recommendation(eml_metrics: dict[str, Any], standard_metrics: dict[str, Any]) -> str:
    if eml_metrics["finiteRatio"] < 0.995 or eml_metrics["maxRelError"] > 1.0e-5:
        return "research_only"
    if standard_metrics["maxRelError"] < eml_metrics["maxRelError"] * 0.1:
        return "use_standard"
    if standard_metrics["operatorCount"] < eml_metrics["operatorCount"] and standard_metrics["latencyNsPerSample"] <= eml_metrics["latencyNsPerSample"] * 1.5:
        return "use_standard"
    if eml_metrics["operatorCount"] < standard_metrics["operatorCount"] and eml_metrics["maxRelError"] <= standard_metrics["maxRelError"] * 10.0:
        return "use_eml"
    return "use_hybrid"


def _blocked_claims(recommendation: str, eml_metrics: dict[str, Any], standard_metrics: dict[str, Any]) -> list[str]:
    claims = [
        "No public performance or energy savings claim.",
        "No formal verification or theorem claim.",
        "No hardware, GPU, FPGA, analog, or embedded measurement claim.",
    ]
    if recommendation != "use_eml":
        claims.append("No claim that EML is preferable for this case.")
    if eml_metrics["finiteRatio"] < 1.0 or eml_metrics["maxRelError"] > standard_metrics["maxRelError"]:
        claims.append("No claim that the EML form is numerically superior.")
    return claims


def analyze_case(spec: CaseSpec) -> dict[str, Any]:
    values = deterministic_inputs(spec)
    reference = spec.reference_fn(values).astype(np.float64)
    eml_observed, eml_latency = _run_timed(spec.eml_fn, values)
    standard_observed, standard_latency = _run_timed(spec.standard_fn, values)
    eml_metrics = _metrics(spec.expression, eml_observed, reference, eml_latency)
    standard_metrics = _metrics(spec.standard_expression, standard_observed, reference, standard_latency)
    recommendation = _recommendation(eml_metrics, standard_metrics)
    stability_score = _stability_score(eml_metrics, standard_metrics)
    return {
        "schemaVersion": COST_PACKET_SCHEMA_VERSION,
        "packetType": "eml_cost_packet_v0",
        "date": DATE,
        "caseId": spec.case_id,
        "family": spec.family,
        "expression": spec.expression,
        "standardExpression": spec.standard_expression,
        "ranges": {key: {"min": value[0], "max": value[1]} for key, value in spec.ranges.items()},
        "comparison": {
            "eml": eml_metrics,
            "standard": standard_metrics,
        },
        "stabilityScore": stability_score,
        "recommendation": recommendation,
        "blockedClaims": _blocked_claims(recommendation, eml_metrics, standard_metrics),
        "claimFlags": dict(DEFAULT_CLAIM_FLAGS),
        "nonClaims": [
            "This packet records deterministic finite-precision measurements only.",
            "This packet does not claim public savings, proof correctness, or hardware performance.",
            "Recommendation is local to this fixture and sample grid.",
        ],
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-R10 Cost and Stability Lab",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This lab compares EML-shaped implementations against standard or protected",
        "implementations under deterministic finite-precision sampling. It is a",
        "research filter, not a public savings or proof claim.",
        "",
        "| Case | EML finite | EML max rel err | Std max rel err | EML ns/sample | Std ns/sample | Recommendation |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for packet in payload["costPackets"]:
        eml_metrics = packet["comparison"]["eml"]
        std_metrics = packet["comparison"]["standard"]
        lines.append(
            f"| `{packet['caseId']}` | `{eml_metrics['finiteRatio']:.3f}` | "
            f"`{eml_metrics['maxRelError']:.3e}` | `{std_metrics['maxRelError']:.3e}` | "
            f"`{eml_metrics['latencyNsPerSample']:.1f}` | `{std_metrics['latencyNsPerSample']:.1f}` | "
            f"`{packet['recommendation']}` |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Cost packets: `{payload['summary']['packetCount']}`",
            f"- `use_eml`: `{payload['summary']['recommendations'].get('use_eml', 0)}`",
            f"- `use_standard`: `{payload['summary']['recommendations'].get('use_standard', 0)}`",
            f"- `use_hybrid`: `{payload['summary']['recommendations'].get('use_hybrid', 0)}`",
            f"- `research_only`: `{payload['summary']['recommendations'].get('research_only', 0)}`",
            "",
            "## Boundary",
            "",
            "- This does not benchmark CPU/GPU/embedded energy or cache behavior.",
            "- This does not prove semantic equivalence.",
            "- This does not change Forge/compiler behavior.",
            "- This intentionally blocks broad EML-superiority claims.",
            "",
        ]
    )
    return "\n".join(lines)


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-r10-cost-stability-lab",
        "title": "EML-R10 Cost and Stability Lab",
        "reviewDecision": "research_measurement_pass",
        "validationStatus": "pass",
        "replayStatus": "not_applicable",
        "semanticStrength": "finite_precision_measurement_no_public_savings_claim",
        "semanticReview": {
            "packet_count": payload["summary"]["packetCount"],
            "recommendations": payload["summary"]["recommendations"],
            "worst_eml_finite_ratio": payload["summary"]["worstEmlFiniteRatio"],
        },
        "claimBoundary": "Internal deterministic finite-precision lab; no public performance, proof, hardware, or superiority claim.",
        "claimFlags": {
            **dict(DEFAULT_CLAIM_FLAGS),
            "public_savings_claim": False,
            "formal_verification_claim": False,
            "hardware_observed": False,
            "deploy_performed": False,
        },
        "nonClaims": payload["nonClaims"],
        "reviewHighlights": [
            "Measures finite ratios, error, static operator count, and simple latency.",
            "Recommends use_eml/use_standard/use_hybrid/research_only per fixture.",
        ],
        "validationCommands": [
            "python python/scripts/eml_r10_cost_stability_lab.py --build --strict",
            "python -m pytest -q python/tests/test_eml_r10_cost_stability_lab.py",
        ],
    }


def build_lab(out_dir: Path, packet_dir: Path, report_dir: Path, evidence_dir: Path) -> dict[str, Any]:
    packets = [analyze_case(spec) for spec in case_specs()]
    recommendations: dict[str, int] = {}
    for packet in packets:
        recommendations[packet["recommendation"]] = recommendations.get(packet["recommendation"], 0) + 1
    summary = {
        "packetCount": len(packets),
        "recommendations": recommendations,
        "worstEmlFiniteRatio": min(packet["comparison"]["eml"]["finiteRatio"] for packet in packets),
        "maxEmlRelativeError": max(packet["comparison"]["eml"]["maxRelError"] for packet in packets),
        "publicCostClaimChanged": False,
    }
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "costPackets": packets,
        "summary": summary,
        "claimFlags": dict(DEFAULT_CLAIM_FLAGS),
        "nonClaims": [
            "This lab does not make public performance or energy savings claims.",
            "This lab does not claim EML is generally superior to standard math.",
            "This lab does not make hardware, GPU, FPGA, analog, or embedded measurements.",
            "This lab does not prove formal semantic equivalence.",
        ],
    }
    evidence = build_evidence_packet(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    packet_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    stamp = DATE.replace("-", "_")
    result_path = out_dir / f"eml_r10_cost_stability_lab_{stamp}.json"
    report_path = report_dir / f"eml_r10_cost_stability_lab_{stamp}.md"
    evidence_path = evidence_dir / "eml_r10_cost_stability_lab.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in packets:
        path = packet_dir / f"{packet['caseId']}_cost_packet_{stamp}.json"
        path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "evidence": evidence,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
    }


def validate_lab(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid R10 schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid R10 status")
    if payload["summary"]["packetCount"] < 7:
        raise ValueError("expected at least 7 cost packets")
    if payload["summary"]["publicCostClaimChanged"] is not False:
        raise ValueError("public cost claim must remain false")
    if "use_standard" not in payload["summary"]["recommendations"]:
        raise ValueError("expected at least one standard recommendation")
    for key, value in payload.get("claimFlags", {}).items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")
    for packet in payload["costPackets"]:
        if packet.get("schemaVersion") != COST_PACKET_SCHEMA_VERSION:
            raise ValueError(f"invalid packet schema: {packet.get('caseId')}")
        if packet["recommendation"] not in {"use_eml", "use_standard", "use_hybrid", "research_only"}:
            raise ValueError(f"invalid recommendation: {packet['caseId']}")
        for key, value in packet.get("claimFlags", {}).items():
            if value is not False:
                raise ValueError(f"claim flag must remain false for {packet['caseId']}: {key}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_r10_cost_stability_lab")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_cost_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_lab(args.out_dir, args.packet_dir, args.report_dir, args.evidence_dir)
    if args.strict:
        validate_lab(built["payload"])
    print("EML_R10_COST_STABILITY_LAB_OK")
    print(f"packets={built['payload']['summary']['packetCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
