#!/usr/bin/env python3
"""EML-A8.2 discovery candidate queue.

Builds the next hopper for the Advantage Lab: EML-native candidates whose
expected advantage is generator identity, boundary lens, proof shape,
signature coordinate, symbolic search, or known anti-example. It does not test
or prove the candidates.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_advantage_lab import CLAIM_FLAGS as ADVANTAGE_CLAIM_FLAGS  # noqa: E402
from scripts.eml_language_kernel import DATE  # noqa: E402

SCHEMA_VERSION = "monogate.eml_a8_2_discovery_candidate_queue.v0"
PACKET_SCHEMA_VERSION = "monogate.eml_discovery_candidate_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_A8_2_DISCOVERY_CANDIDATE_QUEUE_PASS"

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "candidate_test_performed": False,
    "candidate_proved": False,
    "public_ready": False,
    "public_atlas_promotion": False,
    "eml_advantage_claim": False,
    "theorem_discovery_claim": False,
    "compiler_correctness_claim": False,
    "deploy_performed": False,
}

NON_CLAIMS = [
    "A8.2 records discovery candidates only.",
    "A8.2 does not test, prove, deploy, or publicly promote candidate claims.",
    "A8.2 does not claim EML advantage, theorem discovery, compiler correctness, RH proof, zeta-zero discovery, or public performance.",
]


def candidate_specs() -> list[dict[str, Any]]:
    return [
        {
            "candidateId": "constants_zero_one_e_v0",
            "family": "generator_identity",
            "emlForm": "eml(0, e) = 0, eml(0, 1) = 1, eml(1, 1) = e",
            "standardForm": "0, 1, e",
            "whyEmlMightHelp": "Shows constants as EML boundary coordinates rather than separate primitives.",
            "expectedAdvantageAxis": "teaching_clarity",
            "requiredTest": "exact_identity_numeric_grid",
            "requiredProof": "machlib_constant_boundary_witness",
            "negativeControl": "arbitrary_constant_encoding_v0",
        },
        {
            "candidateId": "ln_from_eml_boundary_v0",
            "family": "generator_identity",
            "emlForm": "ln(y) = eml(1, eml(eml(1, y), 1))",
            "standardForm": "ln(y)",
            "whyEmlMightHelp": "Tests whether nested EML generation has proof/teaching value despite worse runtime form.",
            "expectedAdvantageAxis": "proof_shape",
            "requiredTest": "positive_domain_holdout_grid",
            "requiredProof": "machlib_ln_from_eml_witness",
            "negativeControl": "standard_log_runtime_v0",
        },
        {
            "candidateId": "bose_fermi_maxwell_triad_v0",
            "family": "boundary_lens",
            "emlForm": "eml(x,e)=exp(x)-1; eml(x,e^-1)=exp(x)+1; eml(x,1)=exp(x)",
            "standardForm": "expm1(x), exp(x)+1, exp(x)",
            "whyEmlMightHelp": "Unifies three statistical-mechanics denominators as y-boundary shifts.",
            "expectedAdvantageAxis": "teaching_clarity",
            "requiredTest": "boundary_triad_numeric_and_expository_review",
            "requiredProof": "machlib_boundary_triad_witness",
            "negativeControl": "unrelated_three_function_group_v0",
        },
        {
            "candidateId": "euler_null_boundary_v0",
            "family": "boundary_lens",
            "emlForm": "eml(i*pi, e^-1) = 0",
            "standardForm": "exp(i*pi)+1=0",
            "whyEmlMightHelp": "Frames Euler identity as an EML null coordinate.",
            "expectedAdvantageAxis": "teaching_clarity",
            "requiredTest": "complex_numeric_identity_and_claim_review",
            "requiredProof": "complex_machlib_or_expository_only",
            "negativeControl": "random_complex_phase_boundary_v0",
        },
        {
            "candidateId": "safe_log_domain_lift_v0",
            "family": "proof_shape",
            "emlForm": "raw theta -> positive y=exp(theta) -> eml(x,y)",
            "standardForm": "manual positive-domain guard",
            "whyEmlMightHelp": "Turns unsafe raw coordinates into positive internal coordinates with a simple obligation.",
            "expectedAdvantageAxis": "proof_shape",
            "requiredTest": "domain_guard_holdout_and_obligation_packet",
            "requiredProof": "machlib_positive_coordinate_witness",
            "negativeControl": "unguarded_raw_log_v0",
        },
        {
            "candidateId": "prime_signature_log_recovery_v1",
            "family": "signature_coordinate",
            "emlForm": "ln(n)=eml(sigma(n),1), sigma(n)=ln(ln(n))",
            "standardForm": "ln(n)",
            "whyEmlMightHelp": "Separates runtime log from signature-coordinate analysis for number-theory lenses.",
            "expectedAdvantageAxis": "signature_coordinate",
            "requiredTest": "integer_holdout_grid_and_density_transform",
            "requiredProof": "machlib_or_expository_log_recovery_witness",
            "negativeControl": "random_integer_signature_v0",
        },
        {
            "candidateId": "psi_residual_two_term_template_v0",
            "family": "symbolic_search",
            "emlForm": "sum_{k<=2} -2 Re(eml(rho_k * eml(sigma(x),1),1)/rho_k)",
            "standardForm": "sqrt(x)*(A cos(gamma log x)+B sin(gamma log x)) terms",
            "whyEmlMightHelp": "Tests whether adding a second EML zero term improves structure recovery at low complexity.",
            "expectedAdvantageAxis": "search_complexity",
            "requiredTest": "a6_1_pysr_or_template_holdout",
            "requiredProof": "none_research_only",
            "negativeControl": "wrong_exponent_two_term_template_v0",
        },
        {
            "candidateId": "eml_fold_trace_kernel_v0",
            "family": "trace_algebra",
            "emlForm": "Fold_{k+1}=eml(Fold_k, boundary)",
            "standardForm": "recursive accumulator",
            "whyEmlMightHelp": "Connects runtime trace folds to EML boundary operators.",
            "expectedAdvantageAxis": "trace_clarity",
            "requiredTest": "trace_algebra_fixture_and_replay_hash",
            "requiredProof": "none_runtime_only",
            "negativeControl": "ordinary_sum_fold_v0",
        },
        {
            "candidateId": "q_integer_ratio_v0",
            "family": "boundary_lens",
            "emlForm": "[n]_q = eml(nx,e)/eml(x,e), q=exp(x)",
            "standardForm": "(q^n-1)/(q-1)",
            "whyEmlMightHelp": "Tests a compact EML boundary representation of q-integers.",
            "expectedAdvantageAxis": "teaching_clarity",
            "requiredTest": "numeric_q_integer_grid",
            "requiredProof": "machlib_q_integer_identity_optional",
            "negativeControl": "generic_rational_function_v0",
        },
        {
            "candidateId": "dedekind_eta_factor_v0",
            "family": "boundary_lens",
            "emlForm": "1-exp(2*pi*i*n*tau) = -eml(2*pi*i*n*tau,e)",
            "standardForm": "eta product factor",
            "whyEmlMightHelp": "Candidate expository bridge for modular product factors.",
            "expectedAdvantageAxis": "teaching_clarity",
            "requiredTest": "bounded_product_numeric_fixture",
            "requiredProof": "expository_only_complex_boundary",
            "negativeControl": "unrelated_infinite_product_v0",
        },
        {
            "candidateId": "logaddexp_runtime_anti_example_v1",
            "family": "runtime_anti_example",
            "emlForm": "ln(exp(a)+exp(b))",
            "standardForm": "logaddexp(a,b)",
            "whyEmlMightHelp": "It should not help; keeps the lab honest.",
            "expectedAdvantageAxis": "negative_control",
            "requiredTest": "runtime_stability_holdout",
            "requiredProof": "none",
            "negativeControl": "self",
        },
        {
            "candidateId": "expm1_runtime_anti_example_v1",
            "family": "runtime_anti_example",
            "emlForm": "eml(x,e)",
            "standardForm": "expm1(x)",
            "whyEmlMightHelp": "It should lose near zero as runtime code while remaining useful as a boundary lens.",
            "expectedAdvantageAxis": "negative_control",
            "requiredTest": "near_zero_stability_holdout",
            "requiredProof": "none",
            "negativeControl": "self",
        },
    ]


def queue_class(spec: dict[str, Any]) -> str:
    axis = spec["expectedAdvantageAxis"]
    proof = spec["requiredProof"]
    if axis == "negative_control":
        return "ready_for_advantage_lab"
    if "machlib" in proof:
        return "needs_machlib_witness"
    if axis == "search_complexity":
        return "needs_symbolic_search"
    if "expository_only" in proof or "complex" in proof:
        return "needs_math_review"
    if axis in {"trace_clarity", "signature_coordinate"}:
        return "ready_for_advantage_lab"
    return "ready_for_advantage_lab"


def priority_score(spec: dict[str, Any]) -> int:
    score = {
        "generator_identity": 18,
        "boundary_lens": 16,
        "proof_shape": 20,
        "signature_coordinate": 15,
        "symbolic_search": 14,
        "trace_algebra": 10,
        "runtime_anti_example": 12,
    }.get(spec["family"], 8)
    score += {
        "proof_shape": 18,
        "teaching_clarity": 12,
        "signature_coordinate": 12,
        "search_complexity": 16,
        "trace_clarity": 8,
        "negative_control": 10,
    }.get(spec["expectedAdvantageAxis"], 6)
    q = queue_class(spec)
    if q == "ready_for_advantage_lab":
        score += 12
    if q == "needs_machlib_witness":
        score += 10
    if q == "needs_symbolic_search":
        score += 8
    if q == "needs_math_review":
        score -= 2
    return max(score, 0)


def packet_from_spec(spec: dict[str, Any]) -> dict[str, Any]:
    q = queue_class(spec)
    return {
        "schemaVersion": PACKET_SCHEMA_VERSION,
        "packetType": "eml_discovery_candidate_packet_v0",
        "date": DATE,
        **spec,
        "queueClass": q,
        "priorityScore": priority_score(spec),
        "publicClaimAllowed": False,
        "readyForPublicAtlas": False,
        "evidencePaths": [
            "reports/eml_advantage_lab_2026_05_27.md",
            "reports/eml_a8_1_holdout_advantage_benchmark_2026_05_27.md",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def summarize(packets: list[dict[str, Any]]) -> dict[str, Any]:
    by_queue: dict[str, int] = {}
    by_family: dict[str, int] = {}
    by_axis: dict[str, int] = {}
    for packet in packets:
        by_queue[packet["queueClass"]] = by_queue.get(packet["queueClass"], 0) + 1
        by_family[packet["family"]] = by_family.get(packet["family"], 0) + 1
        by_axis[packet["expectedAdvantageAxis"]] = by_axis.get(packet["expectedAdvantageAxis"], 0) + 1
    ordered = sorted(packets, key=lambda item: (-item["priorityScore"], item["candidateId"]))
    return {
        "candidateCount": len(packets),
        "byQueueClass": by_queue,
        "byFamily": by_family,
        "byExpectedAdvantageAxis": by_axis,
        "topCandidateId": ordered[0]["candidateId"] if ordered else None,
        "topQueueClass": ordered[0]["queueClass"] if ordered else None,
        "candidateTestPerformed": False,
        "candidateProved": False,
        "publicAtlasPromotion": False,
        "emlAdvantageClaim": False,
        "claimFlagsAllFalse": all(all(value is False for value in packet["claimFlags"].values()) for packet in packets),
    }


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-a8-2-discovery-candidate-queue",
        "title": "EML-A8.2 Discovery Candidate Queue",
        "reviewDecision": "discovery_candidate_queue_recorded",
        "validationStatus": "pass",
        "replayStatus": "not_applicable",
        "semanticStrength": "candidate_queue_no_testing_or_public_claim",
        "semanticReview": {
            "candidateCount": payload["summary"]["candidateCount"],
            "byQueueClass": payload["summary"]["byQueueClass"],
            "topCandidateId": payload["summary"]["topCandidateId"],
            "candidateTestPerformed": False,
            "candidateProved": False,
        },
        "claimBoundary": "Discovery candidate queue only; no tests, proofs, public Atlas promotion, EML advantage claim, or deployment.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Turns A8/A8.1 findings into a ranked hopper of EML-native candidates.",
            "Separates candidates needing MachLib witnesses, symbolic search, math review, and direct Advantage Lab testing.",
            "Includes runtime anti-examples so the lab keeps finding standard wins when appropriate.",
        ],
        "validationCommands": [
            "python python/scripts/eml_a8_2_discovery_candidate_queue.py --build --strict",
            "python -m pytest -q python/tests/test_eml_a8_2_discovery_candidate_queue.py",
        ],
    }


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_a8_2.v0",
        "date": DATE,
        "title": "EML-A8.2 Discovery Candidate Queue",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "A8.3 run top discovery candidates through Advantage Lab",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-A8.2 Discovery Candidate Queue",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "A8.2 turns the Advantage Lab findings into a ranked hopper of",
        "EML-native candidates. It does not test or prove these candidates.",
        "",
        "| Candidate | Family | Axis | Queue | Score |",
        "|---|---|---|---|---:|",
    ]
    for packet in sorted(payload["candidatePackets"], key=lambda item: (-item["priorityScore"], item["candidateId"])):
        lines.append(
            f"| `{packet['candidateId']}` | `{packet['family']}` | `{packet['expectedAdvantageAxis']}` | "
            f"`{packet['queueClass']}` | `{packet['priorityScore']}` |"
        )
    summary = payload["summary"]
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Candidates: `{summary['candidateCount']}`",
            f"- Top candidate: `{summary['topCandidateId']}`",
            f"- Candidate tests performed: `{summary['candidateTestPerformed']}`",
            f"- Candidate proved: `{summary['candidateProved']}`",
            f"- Public Atlas promotion: `{summary['publicAtlasPromotion']}`",
            "",
            "## Boundary",
            "",
            "- Candidate queue only.",
            "- No proof, test result, public Atlas promotion, theorem discovery, EML advantage claim, compiler correctness, or deployment.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid A8.2 schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid A8.2 status")
    if payload["summary"]["candidateCount"] < 12:
        raise ValueError("expected at least 12 discovery candidates")
    if payload["summary"]["byQueueClass"].get("ready_for_advantage_lab", 0) < 2:
        raise ValueError("expected ready candidates")
    if payload["summary"]["byQueueClass"].get("needs_machlib_witness", 0) < 2:
        raise ValueError("expected MachLib witness candidates")
    for key in ["claimFlagsAllFalse"]:
        if payload["summary"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key in ["candidateTestPerformed", "candidateProved", "publicAtlasPromotion", "emlAdvantageClaim"]:
        if payload["summary"][key] is not False:
            raise ValueError(f"{key} must be false")
    for packet in payload["candidatePackets"]:
        if packet.get("schemaVersion") != PACKET_SCHEMA_VERSION:
            raise ValueError(f"invalid candidate packet schema: {packet.get('candidateId')}")
        if packet["publicClaimAllowed"] is not False:
            raise ValueError(f"public claim must be false: {packet['candidateId']}")
        for key, value in packet.get("claimFlags", {}).items():
            if value is not False:
                raise ValueError(f"claim flag must remain false for {packet['candidateId']}: {key}")


def build_queue(out_dir: Path, packet_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    packets = [packet_from_spec(spec) for spec in candidate_specs()]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "queueId": "eml_a8_2_discovery_candidate_queue",
        "candidatePackets": packets,
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
    result_path = out_dir / f"eml_a8_2_discovery_candidate_queue_{stamp}.json"
    report_path = report_dir / f"eml_a8_2_discovery_candidate_queue_{stamp}.md"
    evidence_path = evidence_dir / "eml_a8_2_discovery_candidate_queue.json"
    feed_path = command_feed_dir / f"eml_a8_2_discovery_candidate_queue_feed_{stamp}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in packets:
        packet_path = packet_dir / f"{packet['candidateId']}_discovery_candidate_{stamp}.json"
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_a8_2_discovery_candidate_queue")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_discovery_candidate_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_queue(args.out_dir, args.packet_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("EML_A8_2_DISCOVERY_CANDIDATE_QUEUE_OK")
    print(f"candidates={built['payload']['summary']['candidateCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
