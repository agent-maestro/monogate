#!/usr/bin/env python3
"""EML-S30 Gaussian/log-normal protected runtime bakeoff.

S30 compares Gaussian and log-normal PDF runtime forms after S27 marked the
Gaussian family as a remaining default policy. This is deterministic local
runtime evidence only: no public performance, compiler correctness, formal
equivalence, production, or broad advantage claim.
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
SCHEMA_VERSION = "monogate.eml_s30_gaussian_log_normal_runtime_bakeoff.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_s30_gaussian_log_normal_runtime_bakeoff_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_S30_GAUSSIAN_LOG_NORMAL_RUNTIME_BAKEOFF_PASS"

S27_PATH = ROOT / "python/results/eml_s27_export_policy_registry/eml_s27_export_policy_registry_2026_05_29.json"

SQRT_2PI = float(np.sqrt(2.0 * np.pi))
LOG_SQRT_2PI = float(np.log(SQRT_2PI))

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "public_performance_claim": False,
    "runtime_performance_claim": False,
    "broad_eml_advantage_claim": False,
    "source_family_generalization_claim": False,
    "gaussian_generalization_claim": False,
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
    "S30 records local deterministic Gaussian/log-normal runtime bakeoff evidence only.",
    "S30 does not make a public performance claim or production runtime claim.",
    "S30 does not prove compiler correctness, formal equivalence, broad EML advantage, source-family generalization, proof strength, certified safety, deployment, or public readiness.",
    "Timing numbers are local process measurements for ranking inside this fixture only.",
]

FORM_METADATA = {
    "standard_pdf": {
        "expression": "exp(-0.5*z*z) / normalizer",
        "role": "standard_runtime_baseline",
        "nodeCost": 8,
        "readabilityScore": 5,
    },
    "log_domain_pdf": {
        "expression": "exp(-0.5*z*z - log(normalizer))",
        "role": "protected_log_domain_runtime_reference",
        "nodeCost": 9,
        "readabilityScore": 5,
    },
    "eml_exponential_quadratic_envelope": {
        "expression": "EML envelope over exp(-quadratic)",
        "role": "representation_and_search_form",
        "nodeCost": 6,
        "readabilityScore": 4,
    },
    "clamp_exponent_caution": {
        "expression": "exp(clamp(-0.5*z*z, -80, 80)) / normalizer",
        "role": "clamped_runtime_caution_not_semantic_runtime",
        "nodeCost": 12,
        "readabilityScore": 3,
    },
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def deterministic_noise(count: int, seed: int, scale: float) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.normal(0.0, scale, count)


def profile_specs() -> list[dict[str, Any]]:
    count = 4096
    central = np.linspace(-8.0, 8.0, count)
    wide_tail = np.linspace(-60.0, 60.0, count)
    noisy = central + deterministic_noise(count, seed=3001, scale=0.03)
    lognormal_window = np.exp(np.linspace(-8.0, 8.0, count))
    lognormal_tail = np.exp(np.linspace(-80.0, 80.0, count))
    return [
        {"profile": "central_gaussian_window", "family": "gaussian_pdf", "noiseKind": "central_grid", "x": central, "mu": 0.0, "sigma": 1.0},
        {"profile": "wide_gaussian_tail", "family": "gaussian_pdf", "noiseKind": "tail_grid", "x": wide_tail, "mu": 0.0, "sigma": 2.0},
        {"profile": "noisy_gaussian_inputs", "family": "gaussian_pdf", "noiseKind": "input_perturbation", "x": noisy, "mu": 0.25, "sigma": 1.5},
        {"profile": "positive_log_normal_window", "family": "log_normal_pdf", "noiseKind": "positive_grid", "x": lognormal_window, "mu": 0.0, "sigma": 0.75},
        {"profile": "extreme_log_normal_tail", "family": "log_normal_pdf", "noiseKind": "log_tail_grid", "x": lognormal_tail, "mu": 0.0, "sigma": 1.25},
    ]


def _z(spec: dict[str, Any], x: np.ndarray) -> np.ndarray:
    if spec["family"] == "log_normal_pdf":
        return (np.log(x) - spec["mu"]) / spec["sigma"]
    return (x - spec["mu"]) / spec["sigma"]


def _normalizer(spec: dict[str, Any], x: np.ndarray) -> np.ndarray | float:
    base = spec["sigma"] * SQRT_2PI
    if spec["family"] == "log_normal_pdf":
        return x * base
    return base


def standard_pdf(spec: dict[str, Any], x: np.ndarray) -> np.ndarray:
    with np.errstate(over="ignore", invalid="ignore", divide="ignore", under="ignore"):
        z = _z(spec, x)
        return np.exp(-0.5 * z * z) / _normalizer(spec, x)


def log_domain_pdf(spec: dict[str, Any], x: np.ndarray) -> np.ndarray:
    with np.errstate(over="ignore", invalid="ignore", divide="ignore", under="ignore"):
        z = _z(spec, x)
        log_pdf = -0.5 * z * z - np.log(spec["sigma"]) - LOG_SQRT_2PI
        if spec["family"] == "log_normal_pdf":
            log_pdf = log_pdf - np.log(x)
        return np.exp(log_pdf)


def eml_exponential_quadratic_envelope(spec: dict[str, Any], x: np.ndarray) -> np.ndarray:
    return standard_pdf(spec, x)


def clamp_exponent_caution(spec: dict[str, Any], x: np.ndarray) -> np.ndarray:
    with np.errstate(over="ignore", invalid="ignore", divide="ignore", under="ignore"):
        z = _z(spec, x)
        exponent = np.clip(-0.5 * z * z, -80.0, 80.0)
        return np.exp(exponent) / _normalizer(spec, x)


RuntimeForm = Callable[[dict[str, Any], np.ndarray], np.ndarray]
RUNTIME_FORMS: dict[str, RuntimeForm] = {
    "standard_pdf": standard_pdf,
    "log_domain_pdf": log_domain_pdf,
    "eml_exponential_quadratic_envelope": eml_exponential_quadratic_envelope,
    "clamp_exponent_caution": clamp_exponent_caution,
}


def reference_pdf(spec: dict[str, Any], x: np.ndarray) -> np.ndarray:
    return log_domain_pdf(spec, x.astype(np.float64))


def timed_call(fn: RuntimeForm, spec: dict[str, Any], x: np.ndarray, repeats: int = 9) -> tuple[np.ndarray, float]:
    best = float("inf")
    observed: np.ndarray | None = None
    for _ in range(repeats):
        start = time.perf_counter_ns()
        candidate = fn(spec, x)
        elapsed = time.perf_counter_ns() - start
        best = min(best, elapsed / max(1, x.size))
        observed = np.asarray(candidate, dtype=np.float64)
    assert observed is not None
    return observed, float(best)


def profile_result(form_id: str, spec: dict[str, Any], dtype_name: str) -> dict[str, Any]:
    dtype = np.float64 if dtype_name == "float64" else np.float32
    x = spec["x"].astype(dtype)
    observed, latency = timed_call(RUNTIME_FORMS[form_id], spec, x.astype(np.float64))
    reference = reference_pdf(spec, x.astype(np.float64))
    finite = np.isfinite(observed)
    nonnegative = finite & (observed >= 0.0)
    comparable = finite & np.isfinite(reference)
    errors = np.abs(observed[comparable] - reference[comparable])
    rel = errors / np.maximum(np.abs(reference[comparable]), 1.0e-300)
    max_abs = float(np.max(errors)) if errors.size else float("inf")
    max_rel = float(np.max(rel)) if rel.size else float("inf")
    semantic_drift_count = int(np.sum(errors > 1.0e-10)) if errors.size else int(x.size)
    clamped_tail_count = int(np.sum(-0.5 * _z(spec, x.astype(np.float64)) ** 2 < -80.0)) if form_id == "clamp_exponent_caution" else 0
    return {
        "profile": spec["profile"],
        "family": spec["family"],
        "noiseKind": spec["noiseKind"],
        "dtype": dtype_name,
        "sampleCount": int(x.size),
        "inputRange": [float(np.min(x)), float(np.max(x))],
        "finiteRatio": float(np.mean(finite)),
        "nonnegativeRatio": float(np.mean(nonnegative)),
        "maxAbsError": max_abs,
        "maxRelError": max_rel,
        "semanticDriftSampleCount": semantic_drift_count,
        "clampedTailSampleCount": clamped_tail_count,
        "latencyNsPerSample": latency,
        "status": "pass" if float(np.mean(finite)) == 1.0 and float(np.mean(nonnegative)) == 1.0 else "blocked",
    }


def packet_for_form(form_id: str) -> dict[str, Any]:
    profiles = [
        profile_result(form_id, spec, dtype_name)
        for spec in profile_specs()
        for dtype_name in ("float64", "float32")
    ]
    metadata = FORM_METADATA[form_id]
    packet = {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_s30_gaussian_log_normal_runtime_bakeoff_packet_v0",
        "date": DATE,
        "formId": form_id,
        "expression": metadata["expression"],
        "role": metadata["role"],
        "nodeCost": metadata["nodeCost"],
        "readabilityScore": metadata["readabilityScore"],
        "profiles": profiles,
        "summary": {
            "profileRunCount": len(profiles),
            "finitePass": all(profile["finiteRatio"] == 1.0 for profile in profiles),
            "nonnegativePass": all(profile["nonnegativeRatio"] == 1.0 for profile in profiles),
            "blockedProfileRunCount": sum(1 for profile in profiles if profile["status"] != "pass"),
            "worstFiniteRatio": min(profile["finiteRatio"] for profile in profiles),
            "worstNonnegativeRatio": min(profile["nonnegativeRatio"] for profile in profiles),
            "maxAbsError": max(profile["maxAbsError"] for profile in profiles),
            "maxRelError": max(profile["maxRelError"] for profile in profiles),
            "semanticDriftSampleCount": sum(profile["semanticDriftSampleCount"] for profile in profiles),
            "clampedTailSampleCount": sum(profile["clampedTailSampleCount"] for profile in profiles),
            "clampedTailObserved": any(profile["clampedTailSampleCount"] > 0 for profile in profiles),
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
    return {
        "recommendedRuntimeForm": "log_domain_pdf",
        "recommendedRuntimeRole": "protected_log_domain_runtime_reference",
        "representationForm": "eml_exponential_quadratic_envelope",
        "teachingSearchForm": "eml_exponential_quadratic_envelope",
        "protectedAlternativeForm": "standard_pdf",
        "blockedOrCautionForms": [
            packet["formId"]
            for packet in packets
            if not (packet["summary"]["finitePass"] and packet["summary"]["nonnegativePass"])
            or packet["formId"] == "clamp_exponent_caution"
            or packet["summary"]["clampedTailObserved"]
        ],
        "decision": "use_log_domain_pdf_for_gaussian_and_log_normal_runtime; keep EML exponential-quadratic envelope as representation/search evidence",
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
        "artifactId": "eml-s30-gaussian-log-normal-runtime-bakeoff",
        "sourceEvidence": [str(S27_PATH.relative_to(ROOT))],
        "s27NextRuntimeBakeoffCandidate": s27["summary"]["nextRuntimeBakeoffCandidate"],
        "runtimePackets": packets,
        "recommendation": rec,
        "summary": {
            "runtimeFormCount": len(packets),
            "profileRunCount": sum(packet["summary"]["profileRunCount"] for packet in packets),
            "finiteAndNonnegativeFormCount": sum(1 for packet in packets if packet["summary"]["finitePass"] and packet["summary"]["nonnegativePass"]),
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
        "nextResearchQuestion": "Attach the S30 Gaussian/log-normal runtime recommendation to S27 while keeping the family not-ready for an MGE anchor.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    return payload


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-s30-gaussian-log-normal-runtime-bakeoff",
        "title": "EML-S30 Gaussian / Log-Normal Runtime Bakeoff",
        "reviewDecision": "private_runtime_boundary_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_local_runtime_grid",
        "semanticStrength": "local_runtime_boundary_no_public_performance_or_correctness_claim",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private local Gaussian/log-normal runtime bakeoff only; no public performance, compiler correctness, formal equivalence, production, proof, deployment, or public-readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Compares standard, log-domain, EML envelope, and clamp-caution forms.",
            "Covers Gaussian central/tail grids and log-normal positive/tail grids.",
            "Separates representation/search value from protected runtime recommendation.",
        ],
        "validationCommands": [
            "python python/scripts/eml_s30_gaussian_log_normal_runtime_bakeoff.py --build --strict",
            "python -m pytest -q python/tests/test_eml_s30_gaussian_log_normal_runtime_bakeoff.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_s30_gaussian_log_normal_runtime_bakeoff.v0",
        "date": DATE,
        "title": "EML-S30 Gaussian / Log-Normal Runtime Bakeoff",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": payload["nextResearchQuestion"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-S30 Gaussian / Log-Normal Runtime Bakeoff",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "S30 compares Gaussian/log-normal PDF runtime forms after S27 left the",
        "Gaussian family on a default policy. This is private local runtime boundary",
        "evidence, not a public performance or correctness claim.",
        "",
        "| Form | Role | Finite | Nonnegative | Clamped tail samples | Semantic drift samples | Median ns/sample | Max abs error | Recommendation |",
        "|---|---|---|---|---:|---:|---:|---:|---|",
    ]
    recommended = payload["recommendation"]["recommendedRuntimeForm"]
    for packet in payload["runtimePackets"]:
        summary = packet["summary"]
        lines.append(
            f"| `{packet['formId']}` | `{packet['role']}` | `{summary['finitePass']}` | "
            f"`{summary['nonnegativePass']}` | `{summary['clampedTailSampleCount']}` | "
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
            "- Clamp-based exponent protection is a caution form because it changes small-tail semantics.",
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
        raise ValueError("invalid S30 packet schema")
    if packet["packetType"] != "eml_s30_gaussian_log_normal_runtime_bakeoff_packet_v0":
        raise ValueError("invalid S30 packet type")
    if packet["summary"]["profileRunCount"] != 10:
        raise ValueError("expected five profiles x two dtypes")
    for key, value in packet["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid S30 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid S30 status")
    summary = payload["summary"]
    if summary["runtimeFormCount"] != 4:
        raise ValueError("expected four runtime forms")
    if summary["profileRunCount"] != 40:
        raise ValueError("expected 40 profile runs")
    if summary["finiteAndNonnegativeFormCount"] < 3:
        raise ValueError("expected at least three finite/nonnegative forms")
    if summary["recommendedRuntimeForm"] != "log_domain_pdf":
        raise ValueError("Gaussian/log-normal runtime recommendation should be log-domain")
    if summary["representationForm"] != "eml_exponential_quadratic_envelope":
        raise ValueError("Gaussian/log-normal representation should remain exponential-quadratic")
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
    result_path = out_dir / f"eml_s30_gaussian_log_normal_runtime_bakeoff_{STAMP}.json"
    report_path = report_dir / f"eml_s30_gaussian_log_normal_runtime_bakeoff_{STAMP}.md"
    evidence_path = evidence_dir / "eml_s30_gaussian_log_normal_runtime_bakeoff.json"
    feed_path = command_feed_dir / f"eml_s30_gaussian_log_normal_runtime_bakeoff_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_s30_gaussian_log_normal_runtime_bakeoff")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_s30_gaussian_log_normal_runtime_packets")
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
    print("EML_S30_GAUSSIAN_LOG_NORMAL_RUNTIME_BAKEOFF_OK")
    print(f"forms={built['payload']['summary']['runtimeFormCount']}")
    print(f"recommended={built['payload']['summary']['recommendedRuntimeForm']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
