#!/usr/bin/env python3
"""EML-S28 softplus/logaddexp protected runtime bakeoff.

S28 compares softplus/log-sum-exp runtime forms after S27 identified
`numpy_softplus` as the next family needing a runtime policy. This is local
deterministic runtime evidence only: no public performance, compiler
correctness, formal equivalence, production, or broad advantage claim.
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

from scripts.eml_advantage_lab import CLAIM_FLAGS as ADVANTAGE_CLAIM_FLAGS  # noqa: E402

DATE = "2026-05-29"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_s28_softplus_runtime_bakeoff.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_s28_softplus_runtime_bakeoff_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_S28_SOFTPLUS_RUNTIME_BAKEOFF_PASS"

S27_PATH = ROOT / "python/results/eml_s27_export_policy_registry/eml_s27_export_policy_registry_2026_05_29.json"

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "public_performance_claim": False,
    "runtime_performance_claim": False,
    "broad_eml_advantage_claim": False,
    "source_family_generalization_claim": False,
    "softplus_generalization_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "formal_proof_claim": False,
    "production_toolchain_claim": False,
    "certified_safety_claim": False,
    "hardware_measurement_claim": False,
    "gpu_measurement_claim": False,
    "deploy_performed": False,
    "package_published": False,
}

NON_CLAIMS = [
    "S28 records local deterministic softplus runtime bakeoff evidence only.",
    "S28 does not make a public performance claim or production runtime claim.",
    "S28 does not prove compiler correctness, formal equivalence, broad EML advantage, softplus generalization, proof strength, certified safety, deployment, or public readiness.",
    "Timing numbers are local process measurements for ranking inside this fixture only.",
]

FORM_METADATA = {
    "naive_softplus": {
        "expression": "ln(1 + exp(x))",
        "role": "teaching_and_search_baseline",
        "nodeCost": 4,
        "readabilityScore": 5,
    },
    "logaddexp_softplus": {
        "expression": "logaddexp(0, x)",
        "role": "protected_library_runtime_reference",
        "nodeCost": 2,
        "readabilityScore": 5,
    },
    "branch_stable_softplus": {
        "expression": "where(x > 0, x + log1p(exp(-x)), log1p(exp(x)))",
        "role": "protected_branch_runtime_alternative",
        "nodeCost": 10,
        "readabilityScore": 4,
    },
    "clamp60_softplus_caution": {
        "expression": "ln(1 + exp(clamp60(x)))",
        "role": "clamped_search_caution_not_semantic_runtime",
        "nodeCost": 10,
        "readabilityScore": 3,
    },
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def deterministic_noise(count: int, seed: int, scale: float) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.normal(0.0, scale, count)


def clamp60(x: np.ndarray) -> np.ndarray:
    return (np.abs(x + 60.0) - np.abs(x - 60.0)) / 2.0


def profile_specs() -> list[dict[str, Any]]:
    count = 4096
    transition = np.linspace(-12.0, 12.0, count)
    safe = np.linspace(-80.0, 80.0, count)
    noisy = transition + deterministic_noise(count, seed=2801, scale=0.05)
    extreme = np.concatenate(
        [
            np.linspace(-1200.0, -120.0, count // 2),
            np.linspace(120.0, 1200.0, count // 2),
        ]
    ).astype(np.float64)
    return [
        {"profile": "transition_window", "noiseKind": "transition", "x": transition},
        {"profile": "safe_float_range", "noiseKind": "safe_range", "x": safe},
        {"profile": "noisy_transition_inputs", "noiseKind": "input_perturbation", "x": noisy},
        {"profile": "extreme_overflow_boundary", "noiseKind": "overflow_boundary", "x": extreme},
    ]


def naive_softplus(x: np.ndarray) -> np.ndarray:
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        return np.log1p(np.exp(x))


def logaddexp_softplus(x: np.ndarray) -> np.ndarray:
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        return np.logaddexp(0.0, x)


def branch_stable_softplus(x: np.ndarray) -> np.ndarray:
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        return np.where(x > 0.0, x + np.log1p(np.exp(-x)), np.log1p(np.exp(x)))


def clamp60_softplus_caution(x: np.ndarray) -> np.ndarray:
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        return np.log1p(np.exp(clamp60(x)))


RUNTIME_FORMS: dict[str, Callable[[np.ndarray], np.ndarray]] = {
    "naive_softplus": naive_softplus,
    "logaddexp_softplus": logaddexp_softplus,
    "branch_stable_softplus": branch_stable_softplus,
    "clamp60_softplus_caution": clamp60_softplus_caution,
}


def reference_softplus(x: np.ndarray) -> np.ndarray:
    return logaddexp_softplus(x.astype(np.float64))


def timed_call(fn: Callable[[np.ndarray], np.ndarray], x: np.ndarray, repeats: int = 9) -> tuple[np.ndarray, float]:
    best = float("inf")
    observed: np.ndarray | None = None
    for _ in range(repeats):
        start = time.perf_counter_ns()
        candidate = fn(x)
        elapsed = time.perf_counter_ns() - start
        best = min(best, elapsed / max(1, x.size))
        observed = np.asarray(candidate, dtype=np.float64)
    assert observed is not None
    return observed, float(best)


def profile_result(form_id: str, spec: dict[str, Any], dtype_name: str) -> dict[str, Any]:
    dtype = np.float64 if dtype_name == "float64" else np.float32
    x = spec["x"].astype(dtype)
    observed, latency = timed_call(RUNTIME_FORMS[form_id], x.astype(np.float64))
    reference = reference_softplus(x.astype(np.float64))
    finite = np.isfinite(observed)
    nonnegative = finite & (observed >= 0.0)
    comparable = finite & np.isfinite(reference)
    errors = np.abs(observed[comparable] - reference[comparable])
    rel = errors / np.maximum(np.abs(reference[comparable]), 1.0e-300)
    max_abs = float(np.max(errors)) if errors.size else float("inf")
    max_rel = float(np.max(rel)) if rel.size else float("inf")
    dangerous_exponent_count = int(np.sum(x.astype(np.float64) > 700.0)) if form_id == "naive_softplus" else 0
    semantic_drift_count = int(np.sum(errors > 1.0e-6)) if errors.size else int(x.size)
    return {
        "profile": spec["profile"],
        "noiseKind": spec["noiseKind"],
        "dtype": dtype_name,
        "sampleCount": int(x.size),
        "inputRange": [float(np.min(x)), float(np.max(x))],
        "finiteRatio": float(np.mean(finite)),
        "nonnegativeRatio": float(np.mean(nonnegative)),
        "maxAbsError": max_abs,
        "maxRelError": max_rel,
        "semanticDriftSampleCount": semantic_drift_count,
        "dangerousExponentInputCount": dangerous_exponent_count,
        "latencyNsPerSample": latency,
        "status": "pass" if float(np.mean(finite)) == 1.0 and float(np.mean(nonnegative)) == 1.0 else "blocked",
    }


def packet_for_form(form_id: str) -> dict[str, Any]:
    profiles = [
        profile_result(form_id, spec, dtype_name)
        for spec in profile_specs()
        for dtype_name in ("float64", "float32")
    ]
    finite_pass = all(profile["finiteRatio"] == 1.0 for profile in profiles)
    nonnegative_pass = all(profile["nonnegativeRatio"] == 1.0 for profile in profiles)
    metadata = FORM_METADATA[form_id]
    packet = {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_s28_softplus_runtime_bakeoff_packet_v0",
        "date": DATE,
        "formId": form_id,
        "expression": metadata["expression"],
        "role": metadata["role"],
        "nodeCost": metadata["nodeCost"],
        "readabilityScore": metadata["readabilityScore"],
        "profiles": profiles,
        "summary": {
            "profileRunCount": len(profiles),
            "finitePass": finite_pass,
            "nonnegativePass": nonnegative_pass,
            "blockedProfileRunCount": sum(1 for profile in profiles if profile["status"] != "pass"),
            "worstFiniteRatio": min(profile["finiteRatio"] for profile in profiles),
            "worstNonnegativeRatio": min(profile["nonnegativeRatio"] for profile in profiles),
            "maxAbsError": max(profile["maxAbsError"] for profile in profiles),
            "maxRelError": max(profile["maxRelError"] for profile in profiles),
            "semanticDriftSampleCount": sum(profile["semanticDriftSampleCount"] for profile in profiles),
            "dangerousExponentInputCount": sum(profile["dangerousExponentInputCount"] for profile in profiles),
            "dangerousExponentInputObserved": any(profile["dangerousExponentInputCount"] > 0 for profile in profiles),
            "medianLatencyNsPerSample": float(np.median([profile["latencyNsPerSample"] for profile in profiles])),
            "localTimingOnly": True,
            "runtimePerformanceClaim": False,
        },
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_packet(packet)
    return packet


def recommendation(packets: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {packet["formId"]: packet for packet in packets}
    runtime_winner = by_id["logaddexp_softplus"]
    return {
        "recommendedRuntimeForm": runtime_winner["formId"],
        "recommendedRuntimeRole": runtime_winner["role"],
        "representationForm": "softplus_logsumexp",
        "teachingSearchForm": "naive_softplus",
        "protectedAlternativeForm": "branch_stable_softplus",
        "blockedOrCautionForms": [
            packet["formId"]
            for packet in packets
            if not (packet["summary"]["finitePass"] and packet["summary"]["nonnegativePass"])
            or packet["summary"]["dangerousExponentInputObserved"]
            or packet["formId"] == "clamp60_softplus_caution"
        ],
        "decision": "use_logaddexp_softplus_for_runtime; keep softplus/logsumexp as representation/search evidence",
        "publicPerformanceClaim": False,
        "runtimePerformanceClaim": False,
    }


def build_payload() -> dict[str, Any]:
    s27 = read_json(S27_PATH)
    packets = [packet_for_form(form_id) for form_id in RUNTIME_FORMS]
    rec = recommendation(packets)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "eml-s28-softplus-runtime-bakeoff",
        "sourceEvidence": [str(S27_PATH.relative_to(ROOT))],
        "s27NextRuntimeBakeoffCandidate": s27["summary"]["nextRuntimeBakeoffCandidate"],
        "runtimePackets": packets,
        "recommendation": rec,
        "summary": {
            "runtimeFormCount": len(packets),
            "profileRunCount": sum(packet["summary"]["profileRunCount"] for packet in packets),
            "finiteAndNonnegativeFormCount": sum(
                1 for packet in packets if packet["summary"]["finitePass"] and packet["summary"]["nonnegativePass"]
            ),
            "recommendedRuntimeForm": rec["recommendedRuntimeForm"],
            "representationForm": rec["representationForm"],
            "publicReady": False,
            "publicPerformanceClaim": False,
            "runtimePerformanceClaim": False,
            "broadEmlAdvantageClaim": False,
            "sourceFamilyGeneralizationClaim": False,
            "compilerCorrectnessClaim": False,
            "formalEquivalenceClaim": False,
            "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
        },
        "nextResearchQuestion": "Attach the S28 softplus runtime recommendation to the S27 export policy registry without changing compiler behavior.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    return payload


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-s28-softplus-runtime-bakeoff",
        "title": "EML-S28 Softplus Runtime Bakeoff",
        "reviewDecision": "private_runtime_boundary_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_local_runtime_grid",
        "semanticStrength": "local_runtime_boundary_no_public_performance_or_correctness_claim",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private local softplus runtime bakeoff only; no public performance, compiler correctness, formal equivalence, production, proof, deployment, or public-readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Compares naive, logaddexp, branch-stable, and clamp-caution softplus forms.",
            "Records finite ratio, nonnegative output, error versus logaddexp reference, and local timing.",
            "Separates representation/search value from protected runtime recommendation.",
        ],
        "validationCommands": [
            "python python/scripts/eml_s28_softplus_runtime_bakeoff.py --build --strict",
            "python -m pytest -q python/tests/test_eml_s28_softplus_runtime_bakeoff.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_s28_softplus_runtime_bakeoff.v0",
        "date": DATE,
        "title": "EML-S28 Softplus Runtime Bakeoff",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": payload["nextResearchQuestion"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-S28 Softplus Runtime Bakeoff",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "S28 compares softplus/logaddexp runtime forms after S27 marked softplus",
        "as the next family needing a protected runtime policy. This is private",
        "local runtime boundary evidence, not a public performance or correctness claim.",
        "",
        "| Form | Role | Finite | Nonnegative | Dangerous exponent input | Semantic drift samples | Median ns/sample | Max abs error | Recommendation |",
        "|---|---|---|---|---|---:|---:|---:|---|",
    ]
    recommended = payload["recommendation"]["recommendedRuntimeForm"]
    for packet in payload["runtimePackets"]:
        summary = packet["summary"]
        lines.append(
            f"| `{packet['formId']}` | `{packet['role']}` | `{summary['finitePass']}` | "
            f"`{summary['nonnegativePass']}` | `{summary['dangerousExponentInputObserved']}` | "
            f"`{summary['semanticDriftSampleCount']}` | `{summary['medianLatencyNsPerSample']:.1f}` | "
            f"`{summary['maxAbsError']:.3e}` | "
            f"{'runtime recommendation' if packet['formId'] == recommended else ''} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- Recommended runtime form: `{payload['recommendation']['recommendedRuntimeForm']}`",
            f"- Representation form: `{payload['recommendation']['representationForm']}`",
            f"- Teaching/search form: `{payload['recommendation']['teachingSearchForm']}`",
            f"- Protected alternative: `{payload['recommendation']['protectedAlternativeForm']}`",
            f"- Decision: {payload['recommendation']['decision']}",
            "- Naive softplus is kept as a caution/teaching form because exponent overflow can make it non-finite.",
            "- Clamp-based softplus is a caution form because it changes large-positive semantics.",
            "",
            "## Boundary",
            "",
            "- No public performance claim.",
            "- No runtime performance claim beyond local fixture ranking.",
            "- No broad EML advantage or source-family generalization claim.",
            "- No compiler correctness or formal equivalence claim.",
            "- No proof, deployment, package publish, hardware, GPU, certified-safety, or public-readiness claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_packet(packet: dict[str, Any]) -> None:
    if packet["schemaVersion"] != PACKET_SCHEMA_VERSION:
        raise ValueError("invalid S28 packet schema")
    if packet["packetType"] != "eml_s28_softplus_runtime_bakeoff_packet_v0":
        raise ValueError("invalid S28 packet type")
    if packet["summary"]["profileRunCount"] != 8:
        raise ValueError("expected four profiles x two dtypes")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid S28 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid S28 status")
    summary = payload["summary"]
    if summary["runtimeFormCount"] != 4:
        raise ValueError("expected four runtime forms")
    if summary["profileRunCount"] != 32:
        raise ValueError("expected 32 profile runs")
    if summary["finiteAndNonnegativeFormCount"] < 2:
        raise ValueError("expected at least two finite/nonnegative forms")
    if summary["recommendedRuntimeForm"] != "logaddexp_softplus":
        raise ValueError("softplus runtime recommendation should be logaddexp")
    if summary["representationForm"] != "softplus_logsumexp":
        raise ValueError("softplus representation should remain logsumexp-shaped")
    for key in [
        "publicReady",
        "publicPerformanceClaim",
        "runtimePerformanceClaim",
        "broadEmlAdvantageClaim",
        "sourceFamilyGeneralizationClaim",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    for packet in payload["runtimePackets"]:
        validate_packet(packet)
    for key, value in payload["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def build_outputs(
    out_dir: Path,
    packet_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
) -> dict[str, Any]:
    payload = build_payload()
    evidence = build_evidence_packet(payload)
    feed = build_command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    packet_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"eml_s28_softplus_runtime_bakeoff_{STAMP}.json"
    report_path = report_dir / f"eml_s28_softplus_runtime_bakeoff_{STAMP}.md"
    evidence_path = evidence_dir / "eml_s28_softplus_runtime_bakeoff.json"
    feed_path = command_feed_dir / f"eml_s28_softplus_runtime_bakeoff_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    for packet in payload["runtimePackets"]:
        packet_path = packet_dir / f"{packet['formId']}_runtime_bakeoff_packet_{STAMP}.json"
        packet_path.write_text(json.dumps(packet, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_s28_softplus_runtime_bakeoff")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_s28_softplus_runtime_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_outputs(args.out_dir, args.packet_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("EML_S28_SOFTPLUS_RUNTIME_BAKEOFF_OK")
    print(f"forms={built['payload']['summary']['runtimeFormCount']}")
    print(f"recommended={built['payload']['summary']['recommendedRuntimeForm']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
