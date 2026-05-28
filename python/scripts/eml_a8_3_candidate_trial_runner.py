#!/usr/bin/env python3
"""EML-A8.3 candidate trial runner.

Consumes the A8.2 discovery queue and runs the first small trials:

* safe log-domain lift as a proof-shape/domain-guard candidate
* ln-from-EML as a positive-domain identity candidate
* expm1 as a runtime anti-example where protected standard math should win

This is an evidence-trial layer, not a public advantage claim.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
import tempfile
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_a8_2_discovery_candidate_queue import build_queue  # noqa: E402
from scripts.eml_advantage_lab import CLAIM_FLAGS as ADVANTAGE_CLAIM_FLAGS  # noqa: E402
from scripts.eml_language_kernel import DATE  # noqa: E402
from scripts.eml_r10_cost_stability_lab import eml  # noqa: E402

SCHEMA_VERSION = "monogate.eml_a8_3_candidate_trial_runner.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_candidate_trial_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_A8_3_CANDIDATE_TRIAL_RUNNER_PASS"

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "candidate_trial_performed": False,
    "candidate_proved": False,
    "eml_advantage_proved": False,
    "general_eml_superiority_claim": False,
    "public_ready": False,
    "public_atlas_promotion": False,
    "theorem_discovery_claim": False,
    "compiler_correctness_claim": False,
    "runtime_performance_claim": False,
    "deploy_performed": False,
}

NON_CLAIMS = [
    "A8.3 runs bounded deterministic candidate trials only.",
    "A8.3 does not prove EML advantage, broad EML superiority, theorem discovery, compiler correctness, RH proof, zeta-zero discovery, runtime performance, public Atlas promotion, or deployment.",
    "A8.3 confirms one runtime anti-example so standard protected math can still win.",
]

CRITERIA = {
    "finiteRatioPass": 1.0,
    "identityMaxAbsErrorPass": 1.0e-10,
    "identityMaxRelErrorPass": 1.0e-10,
    "antiExampleStandardImprovementFactor": 1000.0,
}


def load_queue() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="monogate_a8_3_queue_") as tmp:
        root = Path(tmp)
        built = build_queue(
            root / "queue",
            root / "candidate_packets",
            root / "reports",
            root / "evidence",
            root / "feeds",
        )
        return built["payload"]


def candidate_by_id(queue: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    return next(packet for packet in queue["candidatePackets"] if packet["candidateId"] == candidate_id)


def metric(name: str, observed: np.ndarray, reference: np.ndarray) -> dict[str, Any]:
    observed64 = np.asarray(observed, dtype=np.float64)
    reference64 = np.asarray(reference, dtype=np.float64)
    finite = np.isfinite(observed64) & np.isfinite(reference64)
    errors = np.abs(observed64[finite] - reference64[finite])
    rel = errors / np.maximum(np.abs(reference64[finite]), 1.0e-12)
    max_abs = float(np.max(errors)) if errors.size else float("inf")
    max_rel = float(np.max(rel)) if rel.size else float("inf")
    return {
        "expression": name,
        "sampleCount": int(observed64.size),
        "finiteRatio": float(np.mean(finite)),
        "maxAbsError": max_abs,
        "maxRelError": max_rel,
        "pass": bool(
            np.mean(finite) >= CRITERIA["finiteRatioPass"]
            and (max_abs <= CRITERIA["identityMaxAbsErrorPass"] or max_rel <= CRITERIA["identityMaxRelErrorPass"])
        ),
    }


def profile_grid(name: str, low: float, high: float, count: int = 2048) -> np.ndarray:
    if name == "edge":
        left = np.linspace(low, low + 0.02 * (high - low), count // 2, dtype=np.float64)
        right = np.linspace(high - 0.02 * (high - low), high, count - count // 2, dtype=np.float64)
        return np.concatenate([left, right])
    if name == "stress" and low > 0:
        return np.geomspace(max(low, np.finfo(np.float64).tiny), high, count, dtype=np.float64)
    return np.linspace(low, high, count, dtype=np.float64)


def safe_log_domain_lift_trial(candidate: dict[str, Any]) -> dict[str, Any]:
    profiles: list[dict[str, Any]] = []
    for profile, low, high in [("holdout", -20.0, 20.0), ("edge", -80.0, 80.0), ("stress", -300.0, 300.0)]:
        theta = profile_grid(profile, low, high)
        x = np.linspace(-4.0, 4.0, theta.size, dtype=np.float64)
        lifted = np.exp(theta)
        reference = np.exp(x) - theta
        observed = eml(x, lifted)
        observed_metric = metric("eml_log_domain_lift", observed, reference)
        positive_ratio = float(np.mean(lifted > 0))
        profiles.append(
            {
                "profile": profile,
                "thetaMin": float(np.min(theta)),
                "thetaMax": float(np.max(theta)),
                "positiveLiftRatio": positive_ratio,
                "eml": observed_metric,
                "winner": "eml_proof_shape" if observed_metric["pass"] and positive_ratio == 1.0 else "blocked",
            }
        )
    return trial_packet(
        candidate,
        "safe_log_domain_lift_trial_v0",
        "proof_shape",
        "eml_proof_shape_supported" if all(item["winner"] == "eml_proof_shape" for item in profiles) else "blocked",
        profiles,
        "Trial supports the bounded proof-shape claim: exp(theta) produces positive internal log-domain coordinates on all profiles.",
        ["MachLib already carries concrete log-domain positive-coordinate witnesses.", "No runtime speed or broad safety claim follows from this trial."],
    )


def ln_from_eml(y: np.ndarray) -> np.ndarray:
    return eml(1.0, eml(eml(1.0, y), 1.0))


def ln_from_eml_trial(candidate: dict[str, Any]) -> dict[str, Any]:
    profiles: list[dict[str, Any]] = []
    for profile, low, high in [("holdout", 1.0e-3, 1.0e3), ("edge", math.exp(-8.0), math.exp(8.0)), ("stress", 1.0e-12, 1.0e12)]:
        y = profile_grid(profile, low, high)
        reference = np.log(y)
        observed = ln_from_eml(y)
        standard = np.log(y)
        eml_metric = metric("ln_from_nested_eml", observed, reference)
        standard_metric = metric("standard_log", standard, reference)
        profiles.append(
            {
                "profile": profile,
                "domainPositiveRatio": float(np.mean(y > 0)),
                "eml": eml_metric,
                "standard": standard_metric,
                "winner": "tie_identity" if eml_metric["pass"] and standard_metric["pass"] else "blocked",
            }
        )
    return trial_packet(
        candidate,
        "ln_from_eml_boundary_trial_v0",
        "proof_shape",
        "mixed_identity_supported" if all(item["winner"] == "tie_identity" for item in profiles) else "blocked",
        profiles,
        "Trial supports the identity/teaching lane, while standard log remains the runtime form.",
        ["Nested EML recovers ln(y) on positive domains.", "This is not a runtime win over standard log."],
    )


def expm1_antiexample_trial(candidate: dict[str, Any]) -> dict[str, Any]:
    profiles: list[dict[str, Any]] = []
    for profile, scale in [("near_zero", 1.0e-8), ("tiny", 1.0e-12), ("signed_edge", 1.0e-6)]:
        x = np.linspace(-scale, scale, 2048, dtype=np.float64)
        ref = np.expm1(x.astype(np.longdouble)).astype(np.float64)
        eml_observed = eml(x, math.e)
        standard = np.expm1(x)
        eml_metric = metric("eml_exp_minus_one", eml_observed, ref)
        standard_metric = metric("standard_expm1", standard, ref)
        eml_abs = max(eml_metric["maxAbsError"], 1.0e-300)
        std_abs = max(standard_metric["maxAbsError"], 1.0e-300)
        improvement = float(eml_abs / std_abs)
        profiles.append(
            {
                "profile": profile,
                "scale": scale,
                "eml": eml_metric,
                "standard": standard_metric,
                "standardImprovementFactor": improvement,
                "winner": "standard" if improvement >= CRITERIA["antiExampleStandardImprovementFactor"] else "blocked",
            }
        )
    return trial_packet(
        candidate,
        "expm1_runtime_antiexample_trial_v1",
        "negative_control",
        "standard_runtime_win_confirmed" if all(item["winner"] == "standard" for item in profiles) else "blocked",
        profiles,
        "Trial confirms the expected anti-example: protected expm1 beats raw exp(x)-1 near zero.",
        ["EML can still be a boundary lens for exp(x)-1.", "Runtime lowering should choose protected expm1 near zero."],
    )


def trial_packet(
    candidate: dict[str, Any],
    trial_id: str,
    axis_tested: str,
    trial_class: str,
    profiles: list[dict[str, Any]],
    interpretation: str,
    evidence_notes: list[str],
) -> dict[str, Any]:
    return {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_candidate_trial_packet_v0",
        "date": DATE,
        "candidateId": candidate["candidateId"],
        "trialId": trial_id,
        "sourceQueueClass": candidate["queueClass"],
        "sourcePriorityScore": candidate["priorityScore"],
        "family": candidate["family"],
        "axisTested": axis_tested,
        "expectedAdvantageAxis": candidate["expectedAdvantageAxis"],
        "trialClass": trial_class,
        "emlForm": candidate["emlForm"],
        "standardForm": candidate["standardForm"],
        "profiles": profiles,
        "criteria": dict(CRITERIA),
        "interpretation": interpretation,
        "evidenceNotes": evidence_notes,
        "blockedPublicClaims": [
            "general EML superiority",
            "runtime performance",
            "compiler correctness",
            "theorem discovery",
            "public Atlas promotion",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_trials(out_dir: Path, packet_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    queue = load_queue()
    selected_ids = ["safe_log_domain_lift_v0", "ln_from_eml_boundary_v0", "expm1_runtime_anti_example_v1"]
    packets = [
        safe_log_domain_lift_trial(candidate_by_id(queue, "safe_log_domain_lift_v0")),
        ln_from_eml_trial(candidate_by_id(queue, "ln_from_eml_boundary_v0")),
        expm1_antiexample_trial(candidate_by_id(queue, "expm1_runtime_anti_example_v1")),
    ]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "trialRunnerId": "eml_a8_3_candidate_trial_runner",
        "sourceQueueId": queue["queueId"],
        "selectedCandidateIds": selected_ids,
        "trialPackets": packets,
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
    result_path = out_dir / f"eml_a8_3_candidate_trial_runner_{stamp}.json"
    report_path = report_dir / f"eml_a8_3_candidate_trial_runner_{stamp}.md"
    evidence_path = evidence_dir / "eml_a8_3_candidate_trial_runner.json"
    feed_path = command_feed_dir / f"eml_a8_3_candidate_trial_runner_feed_{stamp}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in packets:
        packet_path = packet_dir / f"{packet['candidateId']}_trial_{stamp}.json"
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


def summarize(packets: list[dict[str, Any]]) -> dict[str, Any]:
    by_trial_class: dict[str, int] = {}
    for packet in packets:
        by_trial_class[packet["trialClass"]] = by_trial_class.get(packet["trialClass"], 0) + 1
    return {
        "trialCount": len(packets),
        "byTrialClass": by_trial_class,
        "proofShapeSupportedCount": by_trial_class.get("eml_proof_shape_supported", 0),
        "mixedIdentitySupportedCount": by_trial_class.get("mixed_identity_supported", 0),
        "standardRuntimeWinConfirmedCount": by_trial_class.get("standard_runtime_win_confirmed", 0),
        "blockedCount": by_trial_class.get("blocked", 0),
        "candidateTrialPerformed": True,
        "candidateProved": False,
        "emlAdvantageProved": False,
        "publicAtlasPromotion": False,
        "claimFlagsAllFalse": all(all(value is False for value in packet["claimFlags"].values()) for packet in packets),
    }


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-a8-3-candidate-trial-runner",
        "title": "EML-A8.3 Candidate Trial Runner",
        "reviewDecision": "bounded_candidate_trials_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_numeric_trials",
        "semanticStrength": "candidate_trials_no_public_advantage_claim",
        "semanticReview": {
            "trialCount": payload["summary"]["trialCount"],
            "byTrialClass": payload["summary"]["byTrialClass"],
            "candidateProved": False,
            "emlAdvantageProved": False,
        },
        "claimBoundary": "Bounded candidate trials only; no public Atlas promotion, theorem discovery, compiler correctness, runtime performance, or general EML advantage claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Runs two proof/identity-shaped candidates and one runtime anti-example.",
            "Confirms protected expm1 remains the correct runtime lowering near zero.",
            "Moves A8.2 candidates from ranked ideas into inspectable trial packets.",
        ],
        "validationCommands": [
            "python python/scripts/eml_a8_3_candidate_trial_runner.py --build --strict",
            "python -m pytest -q python/tests/test_eml_a8_3_candidate_trial_runner.py",
        ],
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_a8_3.v0",
        "date": DATE,
        "title": "EML-A8.3 Candidate Trial Runner",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "A8.4 expand negative-control discipline and promote only repeatable trials",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-A8.3 Candidate Trial Runner",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "A8.3 runs the first bounded trials from the A8.2 discovery queue.",
        "It keeps the result private/research-oriented and does not promote any",
        "candidate to a public Atlas claim.",
        "",
        "| Candidate | Trial class | Profiles | Interpretation |",
        "|---|---|---:|---|",
    ]
    for packet in payload["trialPackets"]:
        lines.append(
            f"| `{packet['candidateId']}` | `{packet['trialClass']}` | "
            f"`{len(packet['profiles'])}` | {packet['interpretation']} |"
        )
    summary = payload["summary"]
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Trials: `{summary['trialCount']}`",
            f"- Proof-shape supported: `{summary['proofShapeSupportedCount']}`",
            f"- Mixed identity supported: `{summary['mixedIdentitySupportedCount']}`",
            f"- Standard runtime win confirmed: `{summary['standardRuntimeWinConfirmedCount']}`",
            f"- Blocked: `{summary['blockedCount']}`",
            f"- Candidate proved: `{summary['candidateProved']}`",
            f"- EML advantage proved: `{summary['emlAdvantageProved']}`",
            "",
            "## Boundary",
            "",
            "- Bounded deterministic candidate trials only.",
            "- No public Atlas promotion, theorem discovery, compiler correctness, runtime performance, broad EML superiority, or deployment claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid A8.3 schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid A8.3 status")
    summary = payload["summary"]
    if summary["trialCount"] != 3:
        raise ValueError("expected exactly 3 A8.3 trials")
    if summary["proofShapeSupportedCount"] < 1:
        raise ValueError("expected one proof-shape supported trial")
    if summary["mixedIdentitySupportedCount"] < 1:
        raise ValueError("expected one mixed identity trial")
    if summary["standardRuntimeWinConfirmedCount"] < 1:
        raise ValueError("expected one standard runtime win anti-example")
    if summary["blockedCount"] != 0:
        raise ValueError("no A8.3 trial should be blocked")
    if summary["candidateTrialPerformed"] is not True:
        raise ValueError("A8.3 should mark candidateTrialPerformed true")
    for key in ["candidateProved", "emlAdvantageProved", "publicAtlasPromotion"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    for packet in payload["trialPackets"]:
        if packet.get("schemaVersion") != PACKET_SCHEMA_VERSION:
            raise ValueError(f"invalid trial packet schema: {packet.get('candidateId')}")
        if len(packet["profiles"]) < 3:
            raise ValueError(f"expected at least 3 profiles for {packet['candidateId']}")
        for key, value in packet.get("claimFlags", {}).items():
            if value is not False:
                raise ValueError(f"claim flag must remain false for {packet['candidateId']}: {key}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_a8_3_candidate_trial_runner")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_candidate_trial_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_trials(args.out_dir, args.packet_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("EML_A8_3_CANDIDATE_TRIAL_RUNNER_OK")
    print(f"trials={built['payload']['summary']['trialCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
