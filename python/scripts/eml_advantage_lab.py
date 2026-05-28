#!/usr/bin/env python3
"""EML Advantage Lab v0.

Synthesizes existing EML evidence into per-case advantage packets. The lab asks
where EML is useful, mixed, or worse than standard forms. It does not claim
general EML superiority, compiler correctness, theorem discovery, or public
performance.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_language_kernel import DATE  # noqa: E402
from scripts.eml_packet_builder import DEFAULT_CLAIM_FLAGS  # noqa: E402
from scripts.eml_r10_cost_stability_lab import eml, operator_count  # noqa: E402

SCHEMA_VERSION = "monogate.eml_advantage_lab.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_advantage_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_ADVANTAGE_LAB_PASS"

CLAIM_FLAGS = {
    **dict(DEFAULT_CLAIM_FLAGS),
    "eml_general_superiority_claim": False,
    "public_performance_claim": False,
    "public_savings_claim": False,
    "compiler_correctness_claim": False,
    "formal_proof_claim": False,
    "theorem_discovery_claim": False,
    "rh_proof_claim": False,
    "zeta_zero_discovery_claim": False,
    "hardware_measurement_claim": False,
    "deploy_performed": False,
}

NON_CLAIMS = [
    "The EML Advantage Lab is a bounded comparison surface, not a proof system.",
    "It does not claim EML is generally superior to standard mathematics.",
    "It does not claim compiler correctness, theorem discovery, RH proof, zeta-zero discovery, hardware measurement, or public performance.",
    "Each advantage class is local to the listed evidence and fixture.",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def ratio_delta(numerator: float, denominator: float) -> float:
    if not math.isfinite(numerator) or not math.isfinite(denominator):
        return 0.0
    return numerator - denominator


def sign_label(value: float, positive_label: str, negative_label: str, neutral_label: str = "mixed") -> str:
    if value > 1.0e-12:
        return positive_label
    if value < -1.0e-12:
        return negative_label
    return neutral_label


def proof_case_index(r10c: dict[str, Any]) -> set[str]:
    return {packet["caseId"] for packet in r10c.get("proofPackets", []) if packet.get("proofStatus") == "scoped_proof_pass"}


def r10_case_packets(r10: dict[str, Any]) -> list[dict[str, Any]]:
    return list(r10.get("costPackets", []))


def runtime_index(r10b: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {packet["caseId"]: packet for packet in r10b.get("bakeoffPackets", [])}


def runtime_axis(case_id: str, r10_packet: dict[str, Any], r10b_packet: dict[str, Any] | None) -> dict[str, Any]:
    eml_latency = float(r10_packet["comparison"]["eml"]["latencyNsPerSample"])
    standard_latency = float(r10_packet["comparison"]["standard"]["latencyNsPerSample"])
    delta = standard_latency - eml_latency
    dtype_status = "not_run"
    if r10b_packet:
        dtype_status = r10b_packet["runtimeStatus"]
    return {
        "emlLatencyNsPerSample": eml_latency,
        "standardLatencyNsPerSample": standard_latency,
        "deltaStandardMinusEmlNs": delta,
        "label": sign_label(delta, "eml_faster_local", "standard_faster_local", "similar_local"),
        "runtimeBakeoffStatus": dtype_status,
    }


def stability_axis(r10_packet: dict[str, Any]) -> dict[str, Any]:
    eml_metrics = r10_packet["comparison"]["eml"]
    standard_metrics = r10_packet["comparison"]["standard"]
    finite_delta = float(eml_metrics["finiteRatio"]) - float(standard_metrics["finiteRatio"])
    rel_delta = float(standard_metrics["maxRelError"]) - float(eml_metrics["maxRelError"])
    if eml_metrics["finiteRatio"] < standard_metrics["finiteRatio"] or eml_metrics["maxRelError"] > standard_metrics["maxRelError"] * 10.0:
        label = "standard_more_stable"
    elif rel_delta > 0.0:
        label = "eml_more_stable_local"
    else:
        label = "similar_or_mixed"
    return {
        "emlFiniteRatio": float(eml_metrics["finiteRatio"]),
        "standardFiniteRatio": float(standard_metrics["finiteRatio"]),
        "finiteDeltaEmlMinusStandard": finite_delta,
        "emlMaxRelError": float(eml_metrics["maxRelError"]),
        "standardMaxRelError": float(standard_metrics["maxRelError"]),
        "relativeErrorDeltaStandardMinusEml": rel_delta,
        "label": label,
    }


def compression_axis(r10_packet: dict[str, Any]) -> dict[str, Any]:
    eml_count = int(r10_packet["comparison"]["eml"]["operatorCount"])
    standard_count = int(r10_packet["comparison"]["standard"]["operatorCount"])
    delta = standard_count - eml_count
    return {
        "emlOperatorCount": eml_count,
        "standardOperatorCount": standard_count,
        "deltaStandardMinusEml": delta,
        "label": sign_label(float(delta), "eml_smaller_surface", "standard_smaller_surface", "same_surface_count"),
    }


def lowering_axis(r10_packet: dict[str, Any]) -> dict[str, Any]:
    recommendation = r10_packet["recommendation"]
    return {
        "recommendation": recommendation,
        "label": {
            "use_eml": "lower_to_eml",
            "use_standard": "lower_to_standard",
            "use_hybrid": "lower_to_hybrid",
            "research_only": "research_only",
        }[recommendation],
    }


def proof_axis(case_id: str, scoped_cases: set[str], r10e: dict[str, Any]) -> dict[str, Any]:
    scoped = case_id in scoped_cases
    return {
        "scopedSemanticCertificate": scoped,
        "compilerSkeletonOpenObligations": int(r10e["summary"]["openObligationCount"]),
        "compilerCorrectnessProved": False,
        "label": "scoped_certificate_present" if scoped else "proof_obligations_open",
    }


def classify(axes: dict[str, Any]) -> str:
    lowering = axes["lowering"]["recommendation"]
    scoped = axes["proof"]["scopedSemanticCertificate"]
    stability = axes["stability"]["label"]
    compression = axes["compression"]["label"]
    runtime = axes["runtime"]["label"]
    teaching = axes["teaching"]["label"]
    if lowering == "research_only":
        return "research_only"
    if lowering == "use_standard" and stability == "standard_more_stable":
        return "standard_win"
    if scoped and teaching == "eml_generator_identity" and stability != "standard_more_stable":
        return "eml_win"
    if lowering == "use_eml" and scoped and compression == "eml_smaller_surface":
        return "eml_win"
    if runtime == "eml_faster_local" and scoped:
        return "mixed"
    return "mixed"


def packet_from_r10(
    r10_packet: dict[str, Any],
    r10b_by_case: dict[str, dict[str, Any]],
    scoped_cases: set[str],
    r10e: dict[str, Any],
) -> dict[str, Any]:
    case_id = r10_packet["caseId"]
    axes = {
        "compression": compression_axis(r10_packet),
        "runtime": runtime_axis(case_id, r10_packet, r10b_by_case.get(case_id)),
        "stability": stability_axis(r10_packet),
        "lowering": lowering_axis(r10_packet),
        "proof": proof_axis(case_id, scoped_cases, r10e),
        "search": {
            "included": False,
            "label": "not_a_search_fixture",
        },
        "teaching": teaching_axis(case_id, r10_packet),
    }
    advantage = classify(axes)
    return {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_advantage_packet_v0",
        "date": DATE,
        "caseId": case_id,
        "family": r10_packet["family"],
        "standardForm": r10_packet["standardExpression"],
        "emlForm": r10_packet["expression"],
        "advantageClass": advantage,
        "axes": axes,
        "evidencePaths": [
            "reports/eml_r10_cost_stability_lab_2026_05_27.md",
            "reports/eml_r10b_runtime_bakeoff_2026_05_27.md",
            "reports/eml_r10c_scoped_semantic_proof_2026_05_27.md",
            "reports/eml_r10e_formal_compiler_proof_skeleton_2026_05_27.md",
        ],
        "blockedClaims": blocked_claims_for(advantage),
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def prime_signature_packet(r10e: dict[str, Any]) -> dict[str, Any]:
    xs = np.geomspace(math.e + 1.0e-6, 10_000.0, 2048)
    sigma = np.log(np.log(xs))
    eml_observed = eml(sigma, 1.0)
    standard = np.log(xs)
    err = np.abs(eml_observed - standard)
    axes = {
        "compression": {
            "emlOperatorCount": operator_count("eml(sigma(x), 1)"),
            "standardOperatorCount": operator_count("ln(x)"),
            "deltaStandardMinusEml": operator_count("ln(x)") - operator_count("eml(sigma(x), 1)"),
            "label": "standard_smaller_surface",
        },
        "runtime": {
            "label": "not_benchmarked",
            "runtimeBakeoffStatus": "not_run",
        },
        "stability": {
            "emlFiniteRatio": float(np.mean(np.isfinite(eml_observed))),
            "standardFiniteRatio": float(np.mean(np.isfinite(standard))),
            "emlMaxRelError": float(np.max(err / np.maximum(np.abs(standard), 1.0e-12))),
            "standardMaxRelError": 0.0,
            "relativeErrorDeltaStandardMinusEml": float(-np.max(err / np.maximum(np.abs(standard), 1.0e-12))),
            "label": "identity_numeric_match_but_standard_simpler",
        },
        "lowering": {
            "recommendation": "use_standard",
            "label": "lower_to_standard",
        },
        "proof": {
            "scopedSemanticCertificate": False,
            "compilerSkeletonOpenObligations": int(r10e["summary"]["openObligationCount"]),
            "compilerCorrectnessProved": False,
            "label": "proof_obligations_open",
        },
        "search": {
            "included": False,
            "label": "not_a_search_fixture",
        },
        "teaching": {
            "label": "eml_signature_lens",
            "summary": "EML signature recovers ln(x), useful as a number-theory coordinate lens but not a better runtime form.",
        },
    }
    return {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_advantage_packet_v0",
        "date": DATE,
        "caseId": "prime_signature_log_recovery_v0",
        "family": "prime_signature_identity",
        "standardForm": "ln(x)",
        "emlForm": "eml(sigma(x), 1), sigma(x)=ln(ln(x))",
        "advantageClass": "mixed",
        "axes": axes,
        "evidencePaths": [
            "python/results/eml_prime_residual_benchmark/eml_prime_residual_benchmark_2026_05_27.json",
            "reports/eml_r10e_formal_compiler_proof_skeleton_2026_05_27.md",
        ],
        "blockedClaims": blocked_claims_for("mixed"),
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def psi_residual_packet(a5: dict[str, Any]) -> dict[str, Any]:
    eml_template = next(item for item in a5["templates"] if item["id"] == "eml_critical_one_node")
    standard_template = next(item for item in a5["templates"] if item["id"] == "standard_profiled_sqrt_cos_sin")
    axes = {
        "compression": {
            "emlOperatorCount": eml_template["grammarOperatorNodes"],
            "standardOperatorCount": standard_template["grammarOperatorNodes"],
            "deltaStandardMinusEml": standard_template["grammarOperatorNodes"] - eml_template["grammarOperatorNodes"],
            "label": "eml_smaller_template",
        },
        "runtime": {
            "label": "not_runtime_fixture",
            "runtimeBakeoffStatus": "not_run",
        },
        "stability": {
            "label": "not_finite_precision_fixture",
        },
        "lowering": {
            "recommendation": "research_only",
            "label": "research_only",
        },
        "proof": {
            "scopedSemanticCertificate": False,
            "compilerCorrectnessProved": False,
            "label": "not_a_proof_fixture",
        },
        "search": {
            "included": True,
            "emlBestMse": eml_template["bestMse"],
            "standardBestMse": standard_template["bestMse"],
            "emlGammaError": eml_template["errorFromFirstKnownZero"],
            "standardGammaError": standard_template["errorFromFirstKnownZero"],
            "label": "eml_compact_but_not_decisive",
        },
        "teaching": {
            "label": "eml_search_lens",
            "summary": "EML exposes a compact critical-line template for the residual, but current evidence remains research-only.",
        },
    }
    return {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_advantage_packet_v0",
        "date": DATE,
        "caseId": "psi_residual_template_v0",
        "family": "symbolic_regression_frontier",
        "standardForm": "sqrt(x) * (A cos(gamma log x) + B sin(gamma log x))",
        "emlForm": "-2 Re(x^(1/2+i gamma)/(1/2+i gamma))",
        "advantageClass": "research_only",
        "axes": axes,
        "evidencePaths": [
            "reports/eml_a5_symbolic_regression_template_search_2026_05_27.md",
            "reports/evidence_packets/eml_symbolic_regression_template_search.json",
        ],
        "blockedClaims": blocked_claims_for("research_only"),
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def blocked_claims_for(advantage_class: str) -> list[str]:
    claims = [
        "No general EML superiority claim.",
        "No public performance or savings claim.",
        "No compiler correctness claim.",
        "No theorem discovery claim.",
    ]
    if advantage_class != "eml_win":
        claims.append("No claim that EML wins on this case.")
    if advantage_class == "research_only":
        claims.append("No public product-readiness claim for this case.")
    return claims


def teaching_axis(case_id: str, r10_packet: dict[str, Any]) -> dict[str, Any]:
    if case_id == "exp_from_eml_v0":
        return {
            "label": "eml_generator_identity",
            "summary": "The EML primitive directly recovers exp(x) as eml(x, 1).",
        }
    if case_id in {"subtraction_boundary_v0", "ln_from_eml_v0", "bose_boundary_expm1_v0"}:
        return {
            "label": "eml_boundary_identity",
            "summary": "EML shows the expression as a boundary identity, while runtime lowering still favors standard or protected math.",
        }
    if r10_packet["recommendation"] == "use_standard":
        return {
            "label": "standard_runtime_clarity",
            "summary": "The standard form is clearer for implementation under the current evidence.",
        }
    return {
        "label": "mixed_research_clarity",
        "summary": "The EML form is useful for research framing but not yet a public runtime claim.",
    }


def summarize(packets: list[dict[str, Any]]) -> dict[str, Any]:
    by_class: dict[str, int] = {}
    for packet in packets:
        by_class[packet["advantageClass"]] = by_class.get(packet["advantageClass"], 0) + 1
    return {
        "packetCount": len(packets),
        "byAdvantageClass": by_class,
        "emlWinCount": by_class.get("eml_win", 0),
        "standardWinCount": by_class.get("standard_win", 0),
        "mixedCount": by_class.get("mixed", 0),
        "researchOnlyCount": by_class.get("research_only", 0),
        "generalEmlSuperiorityClaim": False,
        "publicPerformanceClaim": False,
        "compilerCorrectnessClaim": False,
        "theoremDiscoveryClaim": False,
        "hardwareMeasurementClaim": False,
        "claimFlagsAllFalse": all(all(value is False for value in packet["claimFlags"].values()) for packet in packets),
    }


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-advantage-lab",
        "title": "EML Advantage Lab",
        "reviewDecision": "bounded_advantage_comparison_recorded",
        "validationStatus": "pass",
        "replayStatus": "not_applicable",
        "semanticStrength": "local_advantage_classification_no_general_superiority_claim",
        "semanticReview": {
            "packetCount": payload["summary"]["packetCount"],
            "byAdvantageClass": payload["summary"]["byAdvantageClass"],
            "generalEmlSuperiorityClaim": False,
            "compilerCorrectnessClaim": False,
        },
        "claimBoundary": "Bounded EML-vs-standard comparison only; no general EML superiority, compiler correctness, theorem discovery, hardware, or public performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Synthesizes R10, R10B, R10C, R10E, and A5 evidence.",
            "Classifies each case as EML win, standard win, mixed, or research-only.",
            "Shows where EML is promising without hiding standard-math wins.",
        ],
        "validationCommands": [
            "python python/scripts/eml_advantage_lab.py --build --strict",
            "python -m pytest -q python/tests/test_eml_advantage_lab.py",
        ],
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_advantage_lab.v0",
        "date": DATE,
        "title": "EML Advantage Lab",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "EML-A8.1 holdout advantage benchmark",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML Advantage Lab",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "The Advantage Lab compares EML-native and standard representations across",
        "compression, runtime, stability, lowering, proof, and search evidence.",
        "It is a bounded research surface, not a general superiority claim.",
        "",
        "| Case | Class | Compression | Runtime | Stability | Lowering | Proof |",
        "|---|---|---|---|---|---|---|",
    ]
    for packet in payload["advantagePackets"]:
        axes = packet["axes"]
        lines.append(
            f"| `{packet['caseId']}` | `{packet['advantageClass']}` | "
            f"`{axes['compression']['label']}` | `{axes['runtime']['label']}` | "
            f"`{axes['stability']['label']}` | `{axes['lowering']['label']}` | "
            f"`{axes['proof']['label']}` |"
        )
    summary = payload["summary"]
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Packets: `{summary['packetCount']}`",
            f"- EML wins: `{summary['emlWinCount']}`",
            f"- Standard wins: `{summary['standardWinCount']}`",
            f"- Mixed: `{summary['mixedCount']}`",
            f"- Research-only: `{summary['researchOnlyCount']}`",
            f"- General EML superiority claim: `{summary['generalEmlSuperiorityClaim']}`",
            f"- Compiler correctness claim: `{summary['compilerCorrectnessClaim']}`",
            "",
            "## Boundary",
            "",
            "- No general EML superiority claim.",
            "- No public performance or savings claim.",
            "- No compiler correctness claim.",
            "- No theorem discovery, RH, zeta-zero, hardware, or deployment claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid Advantage Lab schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid Advantage Lab status")
    if payload["summary"]["packetCount"] < 9:
        raise ValueError("expected at least 9 advantage packets")
    if payload["summary"]["mixedCount"] < 1:
        raise ValueError("expected at least one mixed case")
    if payload["summary"]["standardWinCount"] < 1:
        raise ValueError("expected at least one standard win")
    if payload["summary"]["researchOnlyCount"] < 1:
        raise ValueError("expected at least one research-only case")
    for key in [
        "claimFlagsAllFalse",
    ]:
        if payload["summary"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "generalEmlSuperiorityClaim",
        "publicPerformanceClaim",
        "compilerCorrectnessClaim",
        "theoremDiscoveryClaim",
        "hardwareMeasurementClaim",
    ]:
        if payload["summary"][key] is not False:
            raise ValueError(f"{key} must be false")
    for packet in payload["advantagePackets"]:
        if packet.get("schemaVersion") != PACKET_SCHEMA_VERSION:
            raise ValueError(f"invalid packet schema: {packet.get('caseId')}")
        if packet["advantageClass"] not in {"eml_win", "standard_win", "mixed", "research_only", "blocked"}:
            raise ValueError(f"invalid advantage class: {packet['caseId']}")
        for key, value in packet.get("claimFlags", {}).items():
            if value is not False:
                raise ValueError(f"claim flag must remain false for {packet['caseId']}: {key}")


def build_lab(
    r10_path: Path,
    r10b_path: Path,
    r10c_path: Path,
    r10e_path: Path,
    a5_path: Path,
    out_dir: Path,
    packet_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
) -> dict[str, Any]:
    r10 = load_json(r10_path)
    r10b = load_json(r10b_path)
    r10c = load_json(r10c_path)
    r10e = load_json(r10e_path)
    a5 = load_json(a5_path)
    scoped_cases = proof_case_index(r10c)
    r10b_by_case = runtime_index(r10b)
    packets = [packet_from_r10(packet, r10b_by_case, scoped_cases, r10e) for packet in r10_case_packets(r10)]
    packets.append(prime_signature_packet(r10e))
    packets.append(psi_residual_packet(a5))
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "labId": "eml_advantage_lab_v0",
        "sourcePaths": {
            "r10": str(r10_path),
            "r10b": str(r10b_path),
            "r10c": str(r10c_path),
            "r10e": str(r10e_path),
            "a5": str(a5_path),
        },
        "advantagePackets": packets,
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
    result_path = out_dir / f"eml_advantage_lab_{stamp}.json"
    report_path = report_dir / f"eml_advantage_lab_{stamp}.md"
    evidence_path = evidence_dir / "eml_advantage_lab.json"
    feed_path = command_feed_dir / f"eml_advantage_lab_feed_{stamp}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in packets:
        packet_path = packet_dir / f"{packet['caseId']}_advantage_packet_{stamp}.json"
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
    stamp = DATE.replace("-", "_")
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--r10-path", type=Path, default=ROOT / f"python/results/eml_r10_cost_stability_lab/eml_r10_cost_stability_lab_{stamp}.json")
    parser.add_argument("--r10b-path", type=Path, default=ROOT / f"python/results/eml_r10b_runtime_bakeoff/eml_r10b_runtime_bakeoff_{stamp}.json")
    parser.add_argument("--r10c-path", type=Path, default=ROOT / f"python/results/eml_r10c_scoped_semantic_proof/eml_r10c_scoped_semantic_proof_{stamp}.json")
    parser.add_argument("--r10e-path", type=Path, default=ROOT / f"python/results/eml_r10e_formal_compiler_proof_skeleton/eml_r10e_formal_compiler_proof_skeleton_{stamp}.json")
    parser.add_argument("--a5-path", type=Path, default=ROOT / f"python/results/eml_symbolic_regression_template_search/eml_symbolic_regression_template_search_{stamp}.json")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_advantage_lab")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_advantage_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_lab(
        args.r10_path,
        args.r10b_path,
        args.r10c_path,
        args.r10e_path,
        args.a5_path,
        args.out_dir,
        args.packet_dir,
        args.report_dir,
        args.evidence_dir,
        args.command_feed_dir,
    )
    if args.strict:
        validate_payload(built["payload"])
    print("EML_ADVANTAGE_LAB_OK")
    print(f"packets={built['payload']['summary']['packetCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
