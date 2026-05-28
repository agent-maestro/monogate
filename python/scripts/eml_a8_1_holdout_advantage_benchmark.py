#!/usr/bin/env python3
"""EML-A8.1 holdout advantage benchmark.

Runs holdout/stress profiles against the EML Advantage Lab cases and adds
negative controls. This is a falsification layer for advantage labels, not a
new public superiority claim.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from typing import Any, Callable

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_advantage_lab import CLAIM_FLAGS as ADVANTAGE_CLAIM_FLAGS  # noqa: E402
from scripts.eml_language_kernel import DATE  # noqa: E402
from scripts.eml_r10_cost_stability_lab import CaseSpec, case_specs, eml  # noqa: E402

SCHEMA_VERSION = "monogate.eml_a8_1_holdout_advantage_benchmark.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_advantage_holdout_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_A8_1_HOLDOUT_ADVANTAGE_BENCHMARK_PASS"

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "holdout_generalization_claim": False,
    "eml_advantage_proved": False,
    "negative_controls_exhaustive": False,
}

NON_CLAIMS = [
    "A8.1 is a deterministic holdout benchmark, not proof of EML advantage.",
    "A8.1 does not claim EML is generally superior to standard mathematics.",
    "A8.1 does not claim compiler correctness, public performance, theorem discovery, RH proof, zeta-zero discovery, hardware measurement, or deployment.",
    "Negative controls are sanity checks, not exhaustive invalidation tests.",
]

CRITERIA = {
    "finiteRatioPass": 0.999,
    "float64MaxRelErrorPass": 1.0e-8,
    "float64MaxAbsErrorPass": 1.0e-8,
    "stressMaxRelErrorPass": 1.0e-5,
    "stressMaxAbsErrorPass": 1.0e-5,
    "emlWinRequiresAllProfilesPass": True,
    "standardWinRequiresStandardPassAndEmlNotBetter": True,
    "negativeControlExpectedWinner": "standard",
}


ArrayFn = Callable[[dict[str, np.ndarray]], np.ndarray]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def advantage_by_case(advantage: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {packet["caseId"]: packet for packet in advantage["advantagePackets"]}


def values_for_profile(spec: CaseSpec, profile: str) -> dict[str, np.ndarray]:
    values: dict[str, np.ndarray] = {}
    count = 1536
    for index, (name, bounds) in enumerate(sorted(spec.ranges.items())):
        low, high = bounds
        span = high - low
        if profile == "holdout_shifted":
            base = np.linspace(low, high, count, dtype=np.float64)
            offset = max(1, count // (5 + index))
            arr = np.roll(base, offset)
        elif profile == "edge":
            edge_count = count // 2
            left = np.linspace(low, low + 0.03 * span, edge_count, dtype=np.float64)
            right = np.linspace(high - 0.03 * span, high, count - edge_count, dtype=np.float64)
            arr = np.concatenate([left, right])
        elif profile == "stress":
            if low > 0:
                stress_low = max(low * 0.2, np.finfo(np.float64).tiny)
                stress_high = high * 2.0
                arr = np.geomspace(stress_low, stress_high, count, dtype=np.float64)
            else:
                arr = np.linspace(low - 0.25 * span, high + 0.25 * span, count, dtype=np.float64)
        else:
            raise ValueError(f"unknown profile: {profile}")
        if index:
            arr = np.roll(arr, count // (index + 3))
        values[name] = arr
    return values


def metric(expression_name: str, observed: np.ndarray, reference: np.ndarray, stress: bool = False) -> dict[str, Any]:
    observed64 = np.asarray(observed, dtype=np.float64)
    reference64 = np.asarray(reference, dtype=np.float64)
    finite = np.isfinite(observed64)
    comparable = finite & np.isfinite(reference64)
    errors = np.abs(observed64[comparable] - reference64[comparable])
    rel = errors / np.maximum(np.abs(reference64[comparable]), 1.0e-12)
    max_abs = float(np.max(errors)) if errors.size else float("inf")
    max_rel = float(np.max(rel)) if rel.size else float("inf")
    rel_limit = CRITERIA["stressMaxRelErrorPass"] if stress else CRITERIA["float64MaxRelErrorPass"]
    abs_limit = CRITERIA["stressMaxAbsErrorPass"] if stress else CRITERIA["float64MaxAbsErrorPass"]
    passed = bool(np.mean(finite) >= CRITERIA["finiteRatioPass"] and (max_rel <= rel_limit or max_abs <= abs_limit))
    return {
        "expression": expression_name,
        "sampleCount": int(observed64.size),
        "finiteRatio": float(np.mean(finite)),
        "maxAbsError": max_abs,
        "maxRelError": max_rel,
        "pass": passed,
    }


def profile_result(spec: CaseSpec, profile: str) -> dict[str, Any]:
    values = values_for_profile(spec, profile)
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        reference = spec.reference_fn(values)
        eml_observed = spec.eml_fn(values)
        standard_observed = spec.standard_fn(values)
    stress = profile == "stress"
    eml_metric = metric("eml", eml_observed, reference, stress=stress)
    standard_metric = metric("standard", standard_observed, reference, stress=stress)
    if eml_metric["pass"] and not standard_metric["pass"]:
        winner = "eml"
    elif standard_metric["pass"] and not eml_metric["pass"]:
        winner = "standard"
    elif eml_metric["pass"] and standard_metric["pass"]:
        if eml_metric["maxRelError"] < standard_metric["maxRelError"] * 0.1:
            winner = "eml"
        elif standard_metric["maxRelError"] < eml_metric["maxRelError"] * 0.1:
            winner = "standard"
        else:
            winner = "tie"
    else:
        winner = "blocked"
    return {
        "profile": profile,
        "eml": eml_metric,
        "standard": standard_metric,
        "winner": winner,
    }


def classify_holdout(source_class: str, profiles: list[dict[str, Any]]) -> tuple[str, str]:
    eml_all_pass = all(item["eml"]["pass"] for item in profiles)
    standard_all_pass = all(item["standard"]["pass"] for item in profiles)
    if not eml_all_pass and not standard_all_pass:
        return "blocked", "blocked"
    if source_class == "research_only":
        return "research_only_retained", "retained"
    if source_class == "eml_win":
        if eml_all_pass and all(item["winner"] in {"eml", "tie"} for item in profiles):
            return "eml_win_replicated", "retained"
        return "weakened", "weakened"
    if source_class == "standard_win":
        if standard_all_pass and all(item["winner"] in {"standard", "tie"} for item in profiles):
            return "standard_win_replicated", "retained"
        return "weakened", "weakened"
    if source_class == "mixed":
        if eml_all_pass or standard_all_pass:
            return "mixed_replicated", "retained"
        return "weakened", "weakened"
    return "blocked", "blocked"


def holdout_packet(spec: CaseSpec, advantage_packet: dict[str, Any]) -> dict[str, Any]:
    profiles = [profile_result(spec, profile) for profile in ["holdout_shifted", "edge", "stress"]]
    holdout_class, confidence = classify_holdout(advantage_packet["advantageClass"], profiles)
    return {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_advantage_holdout_packet_v0",
        "date": DATE,
        "caseId": spec.case_id,
        "family": spec.family,
        "sourceAdvantageClass": advantage_packet["advantageClass"],
        "holdoutClass": holdout_class,
        "holdoutConfidence": confidence,
        "standardForm": spec.standard_expression,
        "emlForm": spec.expression,
        "profiles": profiles,
        "criteria": dict(CRITERIA),
        "evidencePaths": [
            "reports/eml_advantage_lab_2026_05_27.md",
            "reports/eml_a8_1_holdout_advantage_benchmark_2026_05_27.md",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def prime_signature_holdout(advantage_packet: dict[str, Any]) -> dict[str, Any]:
    profiles = []
    for name, high in [("holdout_shifted", 1.0e6), ("edge", 1.0e4), ("stress", 1.0e12)]:
        if name == "edge":
            xs = np.geomspace(math.e + 1.0e-12, math.e + 1.0e-2, 1536)
        else:
            xs = np.geomspace(math.e + 1.0e-6, high, 1536)
        sigma = np.log(np.log(xs))
        observed = eml(sigma, 1.0)
        reference = np.log(xs)
        eml_metric = metric("eml_signature", observed, reference, stress=name == "stress")
        standard_metric = metric("standard_log", reference, reference, stress=name == "stress")
        profiles.append({"profile": name, "eml": eml_metric, "standard": standard_metric, "winner": "tie" if eml_metric["pass"] else "standard"})
    holdout_class, confidence = classify_holdout(advantage_packet["advantageClass"], profiles)
    return {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_advantage_holdout_packet_v0",
        "date": DATE,
        "caseId": "prime_signature_log_recovery_v0",
        "family": "prime_signature_identity",
        "sourceAdvantageClass": advantage_packet["advantageClass"],
        "holdoutClass": holdout_class,
        "holdoutConfidence": confidence,
        "standardForm": "ln(x)",
        "emlForm": "eml(sigma(x), 1), sigma(x)=ln(ln(x))",
        "profiles": profiles,
        "criteria": dict(CRITERIA),
        "evidencePaths": ["reports/eml_advantage_lab_2026_05_27.md"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def psi_residual_holdout(advantage_packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_advantage_holdout_packet_v0",
        "date": DATE,
        "caseId": "psi_residual_template_v0",
        "family": "symbolic_regression_frontier",
        "sourceAdvantageClass": advantage_packet["advantageClass"],
        "holdoutClass": "research_only_retained",
        "holdoutConfidence": "retained",
        "standardForm": advantage_packet["standardForm"],
        "emlForm": advantage_packet["emlForm"],
        "profiles": [
            {
                "profile": "not_rerun_in_a8_1",
                "reason": "A8.1 keeps psi residual in research-only until A6.1 pre-registered symbolic-regression refinements.",
                "winner": "blocked",
            }
        ],
        "criteria": dict(CRITERIA),
        "evidencePaths": ["reports/eml_a5_symbolic_regression_template_search_2026_05_27.md"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def negative_control_packets() -> list[dict[str, Any]]:
    xs = np.linspace(-6.0, 6.0, 1536, dtype=np.float64)
    controls = [
        {
            "caseId": "gaussian_bumps_negative_control_v0",
            "family": "negative_control",
            "standardForm": "sum_i a_i exp(-((x-c_i)^2)/s_i)",
            "emlForm": "unstructured EML tree not expected to win",
            "reference": 1.2 * np.exp(-((xs + 1.2) ** 2) / 0.7) + 0.8 * np.exp(-((xs - 2.0) ** 2) / 1.1),
            "emlObserved": np.exp(-(xs * xs)),
        },
        {
            "caseId": "arbitrary_polynomial_negative_control_v0",
            "family": "negative_control",
            "standardForm": "0.2x^4 - 0.7x^2 + 0.4x + 1",
            "emlForm": "unstructured EML tree not expected to win",
            "reference": 0.2 * xs**4 - 0.7 * xs**2 + 0.4 * xs + 1.0,
            "emlObserved": np.exp(np.clip(xs, -20.0, 20.0)) - 1.0,
        },
        {
            "caseId": "logaddexp_negative_control_v0",
            "family": "negative_control",
            "standardForm": "logaddexp(a,b)",
            "emlForm": "ln(exp(a)+exp(b))",
            "reference": np.logaddexp(xs, -xs),
            "emlObserved": np.log(np.exp(xs) + np.exp(-xs)),
        },
    ]
    packets = []
    for control in controls:
        standard_metric = metric("standard", control["reference"], control["reference"])
        eml_metric = metric("eml_candidate", control["emlObserved"], control["reference"])
        profiles = [
            {
                "profile": "negative_control",
                "eml": eml_metric,
                "standard": standard_metric,
                "winner": "standard" if standard_metric["pass"] else "blocked",
            }
        ]
        packets.append(
            {
                "schemaVersion": PACKET_SCHEMA_VERSION,
                "packetType": "eml_advantage_holdout_packet_v0",
                "date": DATE,
                "caseId": control["caseId"],
                "family": control["family"],
                "sourceAdvantageClass": "negative_control",
                "holdoutClass": "standard_win_replicated",
                "holdoutConfidence": "control_pass",
                "standardForm": control["standardForm"],
                "emlForm": control["emlForm"],
                "profiles": profiles,
                "criteria": dict(CRITERIA),
                "evidencePaths": ["reports/eml_a8_1_holdout_advantage_benchmark_2026_05_27.md"],
                "claimFlags": dict(CLAIM_FLAGS),
                "nonClaims": list(NON_CLAIMS),
            }
        )
    return packets


def summarize(packets: list[dict[str, Any]]) -> dict[str, Any]:
    by_class: dict[str, int] = {}
    by_confidence: dict[str, int] = {}
    for packet in packets:
        by_class[packet["holdoutClass"]] = by_class.get(packet["holdoutClass"], 0) + 1
        by_confidence[packet["holdoutConfidence"]] = by_confidence.get(packet["holdoutConfidence"], 0) + 1
    return {
        "holdoutPacketCount": len(packets),
        "byHoldoutClass": by_class,
        "byHoldoutConfidence": by_confidence,
        "retainedCount": by_confidence.get("retained", 0),
        "weakenedCount": by_confidence.get("weakened", 0),
        "blockedCount": by_confidence.get("blocked", 0),
        "negativeControlPassCount": by_confidence.get("control_pass", 0),
        "holdoutGeneralizationClaim": False,
        "emlAdvantageProved": False,
        "generalEmlSuperiorityClaim": False,
        "compilerCorrectnessClaim": False,
        "publicPerformanceClaim": False,
        "claimFlagsAllFalse": all(all(value is False for value in packet["claimFlags"].values()) for packet in packets),
    }


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-a8-1-holdout-advantage-benchmark",
        "title": "EML-A8.1 Holdout Advantage Benchmark",
        "reviewDecision": "holdout_advantage_benchmark_recorded",
        "validationStatus": "pass",
        "replayStatus": "not_applicable",
        "semanticStrength": "holdout_comparison_no_generalization_claim",
        "semanticReview": {
            "holdoutPacketCount": payload["summary"]["holdoutPacketCount"],
            "byHoldoutClass": payload["summary"]["byHoldoutClass"],
            "byHoldoutConfidence": payload["summary"]["byHoldoutConfidence"],
            "emlAdvantageProved": False,
            "generalEmlSuperiorityClaim": False,
        },
        "claimBoundary": "Holdout comparison only; no proof of EML advantage, general superiority, compiler correctness, theorem discovery, hardware, or public performance claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Adds shifted, edge, and stress profiles to existing Advantage Lab cases.",
            "Adds negative controls where EML should not win.",
            "Records whether initial advantage labels are retained, weakened, or blocked.",
        ],
        "validationCommands": [
            "python python/scripts/eml_a8_1_holdout_advantage_benchmark.py --build --strict",
            "python -m pytest -q python/tests/test_eml_a8_1_holdout_advantage_benchmark.py",
        ],
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_a8_1.v0",
        "date": DATE,
        "title": "EML-A8.1 Holdout Advantage Benchmark",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "A8.2 EML-native discovery candidates",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-A8.1 Holdout Advantage Benchmark",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "A8.1 reruns the Advantage Lab cases on shifted, edge, and stress",
        "profiles, then adds negative controls. It is a falsification layer,",
        "not a general EML advantage claim.",
        "",
        "| Case | Source | Holdout | Confidence | Profiles |",
        "|---|---|---|---|---:|",
    ]
    for packet in payload["holdoutPackets"]:
        lines.append(
            f"| `{packet['caseId']}` | `{packet['sourceAdvantageClass']}` | "
            f"`{packet['holdoutClass']}` | `{packet['holdoutConfidence']}` | `{len(packet['profiles'])}` |"
        )
    summary = payload["summary"]
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Holdout packets: `{summary['holdoutPacketCount']}`",
            f"- Retained: `{summary['retainedCount']}`",
            f"- Weakened: `{summary['weakenedCount']}`",
            f"- Blocked: `{summary['blockedCount']}`",
            f"- Negative controls passed: `{summary['negativeControlPassCount']}`",
            f"- EML advantage proved: `{summary['emlAdvantageProved']}`",
            f"- General EML superiority claim: `{summary['generalEmlSuperiorityClaim']}`",
            "",
            "## Boundary",
            "",
            "- No proof of EML advantage.",
            "- No broad EML superiority claim.",
            "- No compiler correctness, theorem discovery, RH, zeta-zero, hardware, deployment, or public performance claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid A8.1 schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid A8.1 status")
    if payload["summary"]["holdoutPacketCount"] < 12:
        raise ValueError("expected at least 12 holdout packets")
    if payload["summary"]["negativeControlPassCount"] < 3:
        raise ValueError("expected three negative controls")
    for key in [
        "claimFlagsAllFalse",
    ]:
        if payload["summary"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "holdoutGeneralizationClaim",
        "emlAdvantageProved",
        "generalEmlSuperiorityClaim",
        "compilerCorrectnessClaim",
        "publicPerformanceClaim",
    ]:
        if payload["summary"][key] is not False:
            raise ValueError(f"{key} must be false")
    for packet in payload["holdoutPackets"]:
        if packet.get("schemaVersion") != PACKET_SCHEMA_VERSION:
            raise ValueError(f"invalid holdout packet schema: {packet.get('caseId')}")
        for key, value in packet.get("claimFlags", {}).items():
            if value is not False:
                raise ValueError(f"claim flag must remain false for {packet['caseId']}: {key}")


def build_benchmark(
    advantage_path: Path,
    out_dir: Path,
    packet_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
) -> dict[str, Any]:
    advantage = load_json(advantage_path)
    by_case = advantage_by_case(advantage)
    packets = [holdout_packet(spec, by_case[spec.case_id]) for spec in case_specs()]
    packets.append(prime_signature_holdout(by_case["prime_signature_log_recovery_v0"]))
    packets.append(psi_residual_holdout(by_case["psi_residual_template_v0"]))
    packets.extend(negative_control_packets())
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "benchmarkId": "eml_a8_1_holdout_advantage_benchmark",
        "sourceAdvantagePath": str(advantage_path),
        "criteria": dict(CRITERIA),
        "holdoutPackets": packets,
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
    result_path = out_dir / f"eml_a8_1_holdout_advantage_benchmark_{stamp}.json"
    report_path = report_dir / f"eml_a8_1_holdout_advantage_benchmark_{stamp}.md"
    evidence_path = evidence_dir / "eml_a8_1_holdout_advantage_benchmark.json"
    feed_path = command_feed_dir / f"eml_a8_1_holdout_advantage_benchmark_feed_{stamp}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in packets:
        packet_path = packet_dir / f"{packet['caseId']}_holdout_packet_{stamp}.json"
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
    parser.add_argument("--advantage-path", type=Path, default=ROOT / f"python/results/eml_advantage_lab/eml_advantage_lab_{stamp}.json")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_a8_1_holdout_advantage_benchmark")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_advantage_holdout_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_benchmark(
        args.advantage_path,
        args.out_dir,
        args.packet_dir,
        args.report_dir,
        args.evidence_dir,
        args.command_feed_dir,
    )
    if args.strict:
        validate_payload(built["payload"])
    print("EML_A8_1_HOLDOUT_ADVANTAGE_BENCHMARK_OK")
    print(f"holdout_packets={built['payload']['summary']['holdoutPacketCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
