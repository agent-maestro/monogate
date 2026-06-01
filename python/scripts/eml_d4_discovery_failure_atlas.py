#!/usr/bin/env python3
"""EML-D4 discovery failure atlas.

Consolidates cases where EML should lose, remain blocked, or defer to
protected standard runtime forms before discovery claims are allowed to grow.
"""

from __future__ import annotations

import argparse
from decimal import Decimal, getcontext
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import eml_d1_discovery_frontier_queue as d1  # noqa: E402
from scripts.eml_r10_cost_stability_lab import eml  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_discovery_failure_atlas.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D4_DISCOVERY_FAILURE_ATLAS_PASS"

CLAIM_FLAGS = {
    "candidate_test_performed": False,
    "candidate_proved": False,
    "eml_advantage_proved": False,
    "general_eml_superiority_claim": False,
    "theorem_discovery_claim": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "public_atlas_promotion": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "EML-D4 records failure-atlas controls for discovery discipline.",
    "EML-D4 does not prove a universal negative theorem about EML.",
    "EML-D4 does not prove EML advantage, theorem discovery, compiler correctness, runtime performance, formal equivalence, public Atlas promotion, RH proof, or zeta-zero discovery.",
    "Protected standard runtime wins are guardrail evidence, not speed or production claims.",
]

getcontext().prec = 80


def candidate_by_id(queue: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    return next(item for item in queue["frontierCandidates"] if item["candidateId"] == candidate_id)


def finite_metric(values: np.ndarray) -> dict[str, Any]:
    finite = np.isfinite(values)
    return {
        "sampleCount": int(values.size),
        "finiteRatio": float(np.mean(finite)),
        "nanOrInfCount": int(values.size - np.count_nonzero(finite)),
    }


def abs_error(value: float, reference: Decimal) -> float:
    if not math.isfinite(value):
        return float("inf")
    return float(abs(Decimal(str(value)) - reference))


def failure_packet(candidate: dict[str, Any], failure_id: str, failure_class: str, result: dict[str, Any], interpretation: str) -> dict[str, Any]:
    return {
        "candidateId": candidate["candidateId"],
        "failureId": failure_id,
        "door": candidate["door"],
        "family": candidate["family"],
        "failureClass": failure_class,
        "emlForm": candidate["emlForm"],
        "standardForm": candidate["standardForm"],
        "result": result,
        "interpretation": interpretation,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def ordinary_polynomial_failure(candidate: dict[str, Any]) -> dict[str, Any]:
    x = np.linspace(-4.0, 4.0, 4096)
    standard = ((2.0 * x - 3.0) * x + 0.5) * x + 7.0
    profile = {
        "profile": "cubic_horner_failure_atlas",
        "sampleCount": int(x.size),
        "standardFiniteRatio": float(np.mean(np.isfinite(standard))),
        "standardOperatorCount": 6,
        "emlEncodedLowerBoundNodes": 18,
        "standardSimpler": True,
        "linkedD2Trial": "ordinary_polynomial_failure_trial_v0",
    }
    result = {
        "profiles": [profile],
        "recommendedDisposition": "standard_representation_wins",
        "blocksClaimTypes": ["surface_compression", "runtime_advantage", "compiler_lowering_preference"],
    }
    return failure_packet(
        candidate,
        "ordinary_polynomial_failure_atlas_v0",
        "standard_representation_wins",
        result,
        "Ordinary polynomial structure remains clearer as Horner form; EML encoding would hide complexity.",
    )


def deep_tree_values(x: np.ndarray, depth: int) -> np.ndarray:
    y = np.asarray(x, dtype=np.float64)
    with np.errstate(over="ignore", invalid="ignore"):
        for _ in range(depth):
            y = eml(y, math.e)
    return y


def deep_tree_failure(candidate: dict[str, Any]) -> dict[str, Any]:
    x = np.linspace(2.0, 8.0, 4096)
    values = deep_tree_values(x, 12)
    metric = finite_metric(values)
    result = {
        "profiles": [
            {
                "profile": "depth_12_expm1_fold_stress",
                "treeDepth": 12,
                **metric,
                "guardDecision": "block_unstable_deep_tree",
                "linkedA8_5Evidence": "unstable_deep_tree_negative_control_v0",
            }
        ],
        "recommendedDisposition": "blocked_until_guarded_or_lowered",
        "blocksClaimTypes": ["deep_tree_stability", "runtime_advantage", "unguarded_lowering"],
    }
    return failure_packet(
        candidate,
        "deep_tree_stability_failure_atlas_v1",
        "blocked_unstable_deep_tree",
        result,
        "The depth-12 EML fold is a runtime guardrail case: it should be blocked unless a protected lowering or explicit guard is attached.",
    )


def expm1_failure(candidate: dict[str, Any]) -> dict[str, Any]:
    samples = [-1e-12, -1e-10, -1e-8, -1e-6, -1e-4, 0.0, 1e-12, 1e-10, 1e-8, 1e-6, 1e-4]
    rows = []
    protected_better = 0
    protected_no_worse = 0
    for x in samples:
        reference = Decimal(str(x)).exp() - Decimal(1)
        naive = math.exp(x) - 1.0
        protected = math.expm1(x)
        naive_error = abs_error(naive, reference)
        protected_error = abs_error(protected, reference)
        if protected_error < naive_error:
            protected_better += 1
        if protected_error <= naive_error:
            protected_no_worse += 1
        rows.append(
            {
                "x": x,
                "naiveAbsError": naive_error,
                "protectedAbsError": protected_error,
                "protectedNoWorse": protected_error <= naive_error,
            }
        )
    result = {
        "profiles": [
            {
                "profile": "near_zero_expm1_failure_boundary",
                "sampleCount": len(samples),
                "protectedBetterCount": protected_better,
                "protectedNoWorseCount": protected_no_worse,
                "rows": rows,
            }
        ],
        "recommendedDisposition": "protected_expm1_runtime_control",
        "blocksClaimTypes": ["raw_eml_runtime_preference", "runtime_advantage", "compiler_lowering_to_raw_exp_minus_one"],
    }
    return failure_packet(
        candidate,
        "expm1_failure_boundary_atlas_v1",
        "protected_standard_runtime_wins",
        result,
        "Near zero, protected `expm1` is no worse than raw `exp(x)-1`; raw EML-shaped runtime should not be preferred.",
    )


def decimal_logsumexp(values: list[float]) -> Decimal:
    decimals = [Decimal(str(value)) for value in values]
    max_value = max(decimals)
    total = sum((value - max_value).exp() for value in decimals)
    return max_value + total.ln()


def protected_logsumexp(values: list[float]) -> float:
    max_value = max(values)
    return max_value + math.log(sum(math.exp(value - max_value) for value in values))


def naive_logsumexp(values: list[float]) -> float:
    try:
        return math.log(sum(math.exp(value) for value in values))
    except (OverflowError, ValueError):
        return float("inf")


def logaddexp_failure(candidate: dict[str, Any]) -> dict[str, Any]:
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
    protected_no_worse = 0
    naive_nonfinite = 0
    protected_nonfinite = 0
    for values in samples:
        reference = decimal_logsumexp(values)
        naive = naive_logsumexp(values)
        protected = protected_logsumexp(values)
        naive_error = abs_error(naive, reference)
        protected_error = abs_error(protected, reference)
        if not math.isfinite(naive):
            naive_nonfinite += 1
        if not math.isfinite(protected):
            protected_nonfinite += 1
        if protected_error <= naive_error:
            protected_no_worse += 1
        rows.append(
            {
                "values": values,
                "naiveValue": "inf" if math.isinf(naive) else naive,
                "protectedValue": protected,
                "naiveAbsError": "inf" if math.isinf(naive_error) else naive_error,
                "protectedAbsError": protected_error,
                "protectedNoWorse": protected_error <= naive_error,
            }
        )
    result = {
        "profiles": [
            {
                "profile": "logaddexp_edge_failure_boundary",
                "sampleCount": len(samples),
                "protectedNoWorseCount": protected_no_worse,
                "naiveNonFiniteCount": naive_nonfinite,
                "protectedNonFiniteCount": protected_nonfinite,
                "rows": rows,
            }
        ],
        "recommendedDisposition": "protected_logaddexp_runtime_control",
        "blocksClaimTypes": ["naive_logsumexp_runtime_preference", "runtime_advantage", "compiler_lowering_to_naive_exp_sum_log"],
    }
    return failure_packet(
        candidate,
        "logaddexp_failure_boundary_atlas_v1",
        "protected_standard_runtime_wins",
        result,
        "On edge log-sum-exp samples, protected logaddexp-style runtime is the control and naive EML-shaped runtime can overflow.",
    )


def build_payload() -> dict[str, Any]:
    queue = d1.build_payload()
    selected_ids = [
        "ordinary_polynomial_failure_v0",
        "deep_tree_stability_failure_v1",
        "expm1_failure_boundary_v1",
        "logaddexp_failure_boundary_v1",
    ]
    packets = [
        ordinary_polynomial_failure(candidate_by_id(queue, selected_ids[0])),
        deep_tree_failure(candidate_by_id(queue, selected_ids[1])),
        expm1_failure(candidate_by_id(queue, selected_ids[2])),
        logaddexp_failure(candidate_by_id(queue, selected_ids[3])),
    ]
    by_class: dict[str, int] = {}
    dispositions: dict[str, int] = {}
    for packet in packets:
        by_class[packet["failureClass"]] = by_class.get(packet["failureClass"], 0) + 1
        disposition = packet["result"]["recommendedDisposition"]
        dispositions[disposition] = dispositions.get(disposition, 0) + 1
    summary = {
        "failurePacketCount": len(packets),
        "selectedCandidateIds": selected_ids,
        "byFailureClass": by_class,
        "byRecommendedDisposition": dispositions,
        "standardRepresentationWinCount": by_class.get("standard_representation_wins", 0),
        "blockedUnstableDeepTreeCount": by_class.get("blocked_unstable_deep_tree", 0),
        "protectedStandardRuntimeWinCount": by_class.get("protected_standard_runtime_wins", 0),
        "candidateTestPerformed": True,
        "candidateProved": False,
        "emlAdvantageProved": False,
        "runtimePerformanceClaim": False,
        "failureAtlasExhaustive": False,
        "claimFlagsAllFalse": all(all(value is False for value in packet["claimFlags"].values()) for packet in packets),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "atlasType": "eml_discovery_failure_atlas_v0",
        "artifactId": "eml-d4-discovery-failure-atlas",
        "status": STATUS,
        "decision": "eml_discovery_failure_atlas_recorded_no_public_claims",
        "date": DATE,
        "sourceQueue": queue["artifactId"],
        "failurePackets": packets,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if summary["failurePacketCount"] != 4:
        raise ValueError("expected 4 failure atlas packets")
    if summary["standardRepresentationWinCount"] != 1:
        raise ValueError("expected one standard representation win")
    if summary["blockedUnstableDeepTreeCount"] != 1:
        raise ValueError("expected one blocked unstable deep tree")
    if summary["protectedStandardRuntimeWinCount"] != 2:
        raise ValueError("expected two protected standard runtime wins")
    for key in ["candidateProved", "emlAdvantageProved", "runtimePerformanceClaim", "failureAtlasExhaustive"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if not all(value is False for value in payload["claimFlags"].values()):
        raise ValueError("claim flag drift")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("packet claim flags must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_discovery_failure_atlas",
        "validationStatus": "pass",
        "semanticStrength": "bounded_failure_atlas_no_advantage_claim",
        "source": f"python/results/eml_d4_discovery_failure_atlas/eml_d4_discovery_failure_atlas_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d4_discovery_failure_atlas_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedCandidateIds": payload["summary"]["selectedCandidateIds"],
        "nextAction": "Use D4 as the negative-control gate before D5 preregistered symbolic-search refinement.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D4 Discovery Failure Atlas",
        "",
        f"Status: `{payload['status']}`",
        "",
        "EML-D4 records the discovery-lane controls where EML should lose, remain blocked, or defer to protected standard runtime forms.",
        "",
        "| Candidate | Failure class | Disposition | Interpretation |",
        "|---|---|---|---|",
    ]
    for packet in payload["failurePackets"]:
        lines.append(
            f"| `{packet['candidateId']}` | `{packet['failureClass']}` | `{packet['result']['recommendedDisposition']}` | {packet['interpretation']} |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- failure packets: {payload['summary']['failurePacketCount']}",
            f"- standard representation wins: {payload['summary']['standardRepresentationWinCount']}",
            f"- blocked unstable deep trees: {payload['summary']['blockedUnstableDeepTreeCount']}",
            f"- protected standard runtime wins: {payload['summary']['protectedStandardRuntimeWinCount']}",
            f"- failure atlas exhaustive: `{payload['summary']['failureAtlasExhaustive']}`",
            f"- EML advantage proved: `{payload['summary']['emlAdvantageProved']}`",
            "",
            "## Non-Claims",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["nonClaims"])
    return "\n".join(lines) + "\n"


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"eml_d4_discovery_failure_atlas_{STAMP}.json"
    report_path = report_dir / f"eml_d4_discovery_failure_atlas_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d4_discovery_failure_atlas.json"
    feed_path = command_feed_dir / f"eml_d4_discovery_failure_atlas_feed_{STAMP}.json"
    write_json(result_path, payload)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(payload), encoding="utf-8")
    write_json(evidence_path, evidence)
    write_json(feed_path, feed)
    return {
        "payload": payload,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d4_discovery_failure_atlas")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    validate_payload(payload)
    if args.build:
        build_outputs(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    print("EML_D4_DISCOVERY_FAILURE_ATLAS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
