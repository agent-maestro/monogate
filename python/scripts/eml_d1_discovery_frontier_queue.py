#!/usr/bin/env python3
"""EML-D1 discovery frontier queue.

Ranks new EML research doors without claiming discovery, advantage, proof, or
runtime superiority.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_discovery_frontier_queue.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D1_DISCOVERY_FRONTIER_QUEUE_PASS"

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
    "EML-D1 records discovery-frontier candidates only.",
    "EML-D1 does not test, prove, deploy, or publicly promote any candidate.",
    "EML-D1 does not claim EML advantage, theorem discovery, compiler correctness, runtime performance, formal equivalence, RH proof, or zeta-zero discovery.",
]


def candidate_specs() -> list[dict[str, Any]]:
    return [
        {
            "candidateId": "constants_zero_one_e_boundary_v0",
            "door": "identity_discovery",
            "family": "constant_boundary",
            "emlForm": "eml(0,e)=0; eml(0,1)=1; eml(1,1)=e",
            "standardForm": "0, 1, e",
            "expectedAdvantageAxes": ["teaching_clarity", "proof_shape", "canonicalization"],
            "requiredValidator": "D2 exact constant-boundary grid plus optional MachLib witness",
            "negativeControl": "arbitrary_constant_encoding_v0",
            "likelyFailureMode": "The identity is real but too elementary to matter beyond teaching/proof shape.",
        },
        {
            "candidateId": "subtraction_boundary_family_v1",
            "door": "identity_discovery",
            "family": "subtraction_boundary",
            "emlForm": "eml(log(v), exp(u)) = v - u, under 0 < v",
            "standardForm": "v - u",
            "expectedAdvantageAxes": ["proof_shape", "domain_obligation_visibility"],
            "requiredValidator": "D2 positive-domain holdout grid and prior MachLib witness linkage",
            "negativeControl": "unguarded_log_v0",
            "likelyFailureMode": "Standard subtraction remains the runtime form; EML helps only as obligation lens.",
        },
        {
            "candidateId": "ln_from_eml_boundary_v1",
            "door": "identity_discovery",
            "family": "generator_identity",
            "emlForm": "ln(y) = eml(1, eml(eml(1,y),1)), under y > 0",
            "standardForm": "ln(y)",
            "expectedAdvantageAxes": ["teaching_clarity", "proof_shape"],
            "requiredValidator": "Positive-domain holdout plus runtime anti-win note",
            "negativeControl": "standard_log_runtime_v0",
            "likelyFailureMode": "Nested EML hides complexity and should not be emitted as runtime log.",
        },
        {
            "candidateId": "probability_logit_boundary_v0",
            "door": "holdout_search",
            "family": "log_domain_probability",
            "emlForm": "logit(p)=log(p)-log(1-p) via subtraction-boundary EML coordinates",
            "standardForm": "log(p) - log1p(-p)",
            "expectedAdvantageAxes": ["domain_obligation_visibility", "search_coordinate"],
            "requiredValidator": "Probability holdout grid with edge profiles near 0 and 1",
            "negativeControl": "ordinary_logit_runtime_v0",
            "likelyFailureMode": "Protected standard logit remains numerically cleaner near boundaries.",
        },
        {
            "candidateId": "normalized_exponential_family_v0",
            "door": "holdout_search",
            "family": "normalized_exponential",
            "emlForm": "log weights as EML boundary coordinates, normalize with protected logsumexp",
            "standardForm": "softmax/logsumexp",
            "expectedAdvantageAxes": ["canonicalization", "search_coordinate"],
            "requiredValidator": "Holdout over shifted logits plus negative controls",
            "negativeControl": "random_logits_no_structure_v0",
            "likelyFailureMode": "Protected logsumexp wins runtime/stability; EML helps only review shape.",
        },
        {
            "candidateId": "damped_oscillator_eml_phase_v0",
            "door": "holdout_search",
            "family": "damped_oscillator",
            "emlForm": "exp(-a t) * sin(w t + phi) with EML log/exp phase coordinates",
            "standardForm": "damped sinusoid",
            "expectedAdvantageAxes": ["symbolic_search", "parameter_recovery"],
            "requiredValidator": "Template search with wrong-frequency and wrong-exponent controls",
            "negativeControl": "wrong_frequency_damped_oscillator_v0",
            "likelyFailureMode": "Standard profiled trig basis may fit with lower MSE.",
        },
        {
            "candidateId": "psi_residual_two_zero_holdout_v1",
            "door": "holdout_search",
            "family": "prime_residual",
            "emlForm": "two critical-line EML terms over log-coordinate input",
            "standardForm": "profiled sqrt(x) trig basis",
            "expectedAdvantageAxes": ["symbolic_search", "structure_recovery"],
            "requiredValidator": "Pre-registered A6.1 symbolic search with wrong-exponent controls",
            "negativeControl": "wrong_exponent_two_zero_v0",
            "likelyFailureMode": "Low-MSE baselines can look better without structural recovery.",
        },
        {
            "candidateId": "ordinary_polynomial_failure_v0",
            "door": "failure_atlas",
            "family": "polynomial_control",
            "emlForm": "polynomial encoded through EML tree",
            "standardForm": "Horner polynomial",
            "expectedAdvantageAxes": ["negative_control"],
            "requiredValidator": "D2 operator-count control",
            "negativeControl": "self",
            "likelyFailureMode": "EML hides complexity; standard Horner is the right representation.",
        },
        {
            "candidateId": "deep_tree_stability_failure_v1",
            "door": "failure_atlas",
            "family": "deep_tree_control",
            "emlForm": "depth-12 EML fold",
            "standardForm": "protected standard form or blocked lowering",
            "expectedAdvantageAxes": ["negative_control", "stability_guard"],
            "requiredValidator": "Finite-ratio stress grid and blocked-lowering check",
            "negativeControl": "self",
            "likelyFailureMode": "Overflow/underflow and error amplification should block runtime use.",
        },
        {
            "candidateId": "expm1_failure_boundary_v1",
            "door": "failure_atlas",
            "family": "protected_runtime_control",
            "emlForm": "eml(x,e)=exp(x)-1",
            "standardForm": "expm1(x)",
            "expectedAdvantageAxes": ["negative_control", "runtime_stability"],
            "requiredValidator": "Near-zero stability holdout",
            "negativeControl": "self",
            "likelyFailureMode": "Protected expm1 should dominate raw EML near zero.",
        },
        {
            "candidateId": "logaddexp_failure_boundary_v1",
            "door": "failure_atlas",
            "family": "protected_runtime_control",
            "emlForm": "ln(exp(a)+exp(b))",
            "standardForm": "logaddexp(a,b)",
            "expectedAdvantageAxes": ["negative_control", "runtime_stability"],
            "requiredValidator": "Shifted edge-grid stability holdout",
            "negativeControl": "self",
            "likelyFailureMode": "Protected logaddexp should dominate naive EML-shaped runtime.",
        },
        {
            "candidateId": "prime_signature_log_recovery_v2",
            "door": "identity_discovery",
            "family": "signature_coordinate",
            "emlForm": "ln(n)=eml(sigma(n),1), sigma(n)=ln(ln(n))",
            "standardForm": "ln(n)",
            "expectedAdvantageAxes": ["search_coordinate", "teaching_clarity"],
            "requiredValidator": "Integer holdout grid and density-transform review",
            "negativeControl": "random_integer_signature_v0",
            "likelyFailureMode": "Useful as a lens only, not as a proof or RH signal.",
        },
    ]


def score(spec: dict[str, Any]) -> int:
    door_score = {
        "identity_discovery": 24,
        "holdout_search": 22,
        "failure_atlas": 20,
    }[spec["door"]]
    axis_score = {
        "proof_shape": 12,
        "canonicalization": 8,
        "domain_obligation_visibility": 10,
        "teaching_clarity": 7,
        "search_coordinate": 10,
        "symbolic_search": 11,
        "structure_recovery": 10,
        "negative_control": 9,
        "stability_guard": 8,
        "runtime_stability": 7,
        "parameter_recovery": 6,
    }
    return door_score + sum(axis_score.get(axis, 0) for axis in spec["expectedAdvantageAxes"])


def candidate_from_spec(spec: dict[str, Any]) -> dict[str, Any]:
    priority = score(spec)
    return {
        **spec,
        "priorityScore": priority,
        "frontierStatus": "ready_for_d2_trial" if priority >= 38 else "parked_pending_validator",
        "blockedClaims": [
            "general EML superiority",
            "runtime performance",
            "compiler correctness",
            "formal equivalence",
            "theorem discovery",
            "public Atlas promotion",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_payload() -> dict[str, Any]:
    candidates = [candidate_from_spec(spec) for spec in candidate_specs()]
    ordered = sorted(candidates, key=lambda item: (-item["priorityScore"], item["candidateId"]))
    by_door: dict[str, int] = {}
    by_axis: dict[str, int] = {}
    for candidate in candidates:
        by_door[candidate["door"]] = by_door.get(candidate["door"], 0) + 1
        for axis in candidate["expectedAdvantageAxes"]:
            by_axis[axis] = by_axis.get(axis, 0) + 1
    summary = {
        "candidateCount": len(candidates),
        "doorCount": len(by_door),
        "byDoor": by_door,
        "byExpectedAdvantageAxis": by_axis,
        "readyForD2TrialCount": sum(1 for item in candidates if item["frontierStatus"] == "ready_for_d2_trial"),
        "topCandidateIds": [item["candidateId"] for item in ordered[:3]],
        "candidateTestPerformed": False,
        "candidateProved": False,
        "emlAdvantageProved": False,
        "claimFlagsAllFalse": all(all(value is False for value in item["claimFlags"].values()) for item in candidates),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "queueType": "eml_discovery_frontier_queue_v0",
        "artifactId": "eml-d1-discovery-frontier-queue",
        "status": STATUS,
        "decision": "eml_discovery_frontier_ranked_no_claims",
        "date": DATE,
        "frontierCandidates": ordered,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if summary["candidateCount"] != 12:
        raise ValueError("expected 12 frontier candidates")
    if summary["doorCount"] != 3:
        raise ValueError("expected three discovery doors")
    for door in ["identity_discovery", "holdout_search", "failure_atlas"]:
        if summary["byDoor"].get(door, 0) < 3:
            raise ValueError(f"expected at least three candidates for {door}")
    if len(summary["topCandidateIds"]) != 3:
        raise ValueError("expected three top candidates")
    for key in ["candidateTestPerformed", "candidateProved", "emlAdvantageProved"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if not all(value is False for value in payload["claimFlags"].values()):
        raise ValueError("claim flag drift")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("candidate claim flags must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_discovery_frontier_queue",
        "validationStatus": "pass",
        "semanticStrength": "frontier_queue_no_tests_or_claims",
        "source": f"python/results/eml_d1_discovery_frontier_queue/eml_d1_discovery_frontier_queue_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d1_discovery_frontier_queue_feed",
        "date": DATE,
        "status": payload["status"],
        "topCandidateIds": payload["summary"]["topCandidateIds"],
        "nextAction": "Run EML-D2 bounded trials for the top identity, holdout, and failure-atlas doors.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D1 Discovery Frontier Queue",
        "",
        f"Status: `{payload['status']}`",
        "",
        "EML-D1 ranks new research doors for EML without testing or promoting any claim.",
        "",
        "| Candidate | Door | Axes | Score |",
        "|---|---|---|---:|",
    ]
    for candidate in payload["frontierCandidates"]:
        axes = ", ".join(candidate["expectedAdvantageAxes"])
        lines.append(f"| `{candidate['candidateId']}` | `{candidate['door']}` | {axes} | `{candidate['priorityScore']}` |")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- candidates: {payload['summary']['candidateCount']}",
            f"- top candidates: `{', '.join(payload['summary']['topCandidateIds'])}`",
            f"- candidate tests performed: `{payload['summary']['candidateTestPerformed']}`",
            f"- EML advantage proved: `{payload['summary']['emlAdvantageProved']}`",
            "",
            "## Non-Claims",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["nonClaims"])
    return "\n".join(lines) + "\n"


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, str]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"eml_d1_discovery_frontier_queue_{STAMP}.json"
    report_path = report_dir / f"eml_d1_discovery_frontier_queue_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d1_discovery_frontier_queue.json"
    feed_path = command_feed_dir / f"eml_d1_discovery_frontier_queue_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d1_discovery_frontier_queue")
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
    print("EML_D1_DISCOVERY_FRONTIER_QUEUE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
