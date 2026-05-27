#!/usr/bin/env python3
"""RH-A1 universal claim review harness.

This is the central Monogate reviewer primitive: a deterministic intake layer
that classifies claims, assigns evidence strength, blocks unsupported public
claims, and routes the next validator. It does not prove claims, call external
APIs, trade, deploy, publish, or change compiler/runtime behavior.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_language_kernel import DATE  # noqa: E402

SCHEMA_VERSION = "monogate.rh_a1_universal_claim_review_harness.v0"
REVIEW_PACKET_SCHEMA_VERSION = "monogate.claim_review_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "RH_A1_UNIVERSAL_CLAIM_REVIEW_HARNESS_PASS"

CLAIM_FLAGS = {
    "public_ready": False,
    "public_savings_claim": False,
    "hardware_observed": False,
    "live_serial_capture_performed": False,
    "certified_safety_claim": False,
    "production_controller_claim": False,
    "formal_verification_claim": False,
    "theorem_proof_claim": False,
    "compiler_correctness_claim": False,
    "forge_behavior_changed": False,
    "compiler_behavior_changed": False,
    "financial_advice_claim": False,
    "profitable_strategy_claim": False,
    "autonomous_trading_claim": False,
    "order_placement_performed": False,
    "external_theory_endorsed": False,
}

BASE_NON_CLAIMS = [
    "RH-A1 is a deterministic review harness, not a proof system.",
    "RH-A1 does not approve unsupported public claims.",
    "RH-A1 does not deploy, trade, publish packages, operate hardware, or change compiler behavior.",
]

REQUIRED_VALIDATORS_BY_TYPE = {
    "performance": ["r10_cost_stability", "holdout_runtime_bakeoff", "implementation_benchmark"],
    "forecasting": ["pm_a1_forecast_packet", "calibration_ledger", "human_market_review"],
    "external_theory": ["claim_decomposition", "domain_expert_review", "contradiction_scan", "formal_derivation_check"],
    "hardware": ["live_capture_packet", "device_identity", "calibration_context", "replay_comparison"],
    "compiler_correctness": ["generated_stub_validation", "semantic_equivalence_tests", "formal_compiler_proof"],
    "generated_stub_validation": ["r12_generated_stub_packet", "runtime_bakeoff", "scoped_semantic_proof"],
    "proof_status": ["machlib_lake_build", "proof_scope_review", "domain_assumption_check"],
    "ai_answer": ["source_attribution", "expert_review", "replay_or_validator_when_applicable"],
    "redteam_robustness": ["rampart_redteam_packet", "adapter_coverage_review", "regression_ci_guard"],
}

BLOCKED_CLAIMS_BY_TYPE = {
    "performance": ["general_performance_superiority", "public_savings_claim_without_benchmark"],
    "forecasting": ["financial_advice", "profitable_strategy", "autonomous_trading"],
    "external_theory": ["theory_of_everything_endorsement", "physics_unification_claim", "metaphysical_closure_claim"],
    "hardware": ["hardware_validated_without_live_capture", "production_controller_claim"],
    "compiler_correctness": ["compiler_correctness_without_proof", "runtime_semantic_equivalence_without_validation"],
    "generated_stub_validation": ["compiler_correctness_claim", "production_lowering_claim", "semantic_equivalence_claim"],
    "proof_status": ["general_theorem_claim_beyond_checked_witness"],
    "ai_answer": ["authoritative_guidance_without_sources_or_review"],
    "redteam_robustness": ["certified_safety_claim", "comprehensive_robustness_claim", "production_security_claim"],
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def slug(value: str) -> str:
    out = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return out[:100] or "claim"


def infer_evidence_strength(claim: dict[str, Any]) -> str:
    claim_type = claim["claimType"]
    paths = claim.get("evidencePaths", [])
    summary = claim.get("evidenceSummary", "").lower()
    if not paths:
        return "none"
    if claim_type == "proof_status" and ("checked" in summary or "witness" in summary):
        return "small_checked_witness"
    if claim_type == "compiler_correctness" and any("eml_r12" in path or "generated_stub" in path for path in paths):
        return "validated_replay_or_packet"
    if claim_type in {"performance", "compiler_correctness"} and any("r10" in path or "r11" in path for path in paths):
        return "local_measurement_only"
    if claim_type == "generated_stub_validation" and any("eml_r12" in path or "generated_stub" in path for path in paths):
        return "validated_replay_or_packet"
    if claim_type == "forecasting" and any("pm_a1" in path for path in paths):
        return "fixture_only"
    if claim_type == "hardware" and "simulated" in summary:
        return "fixture_only"
    if claim_type == "external_theory":
        return "source_only"
    if claim_type == "redteam_robustness" and "fixture" in summary and "fail" in summary:
        return "fixture_red_team_fail"
    if claim_type == "redteam_robustness" and "fixture" in summary and "pass" in summary:
        return "fixture_red_team_pass"
    return "validated_replay_or_packet"


def decision_for(claim: dict[str, Any], evidence_strength: str) -> str:
    claim_type = claim["claimType"]
    text = claim["claim"].lower()
    requested = claim["requestedSurface"]
    if claim_type in {"forecasting", "external_theory", "hardware", "compiler_correctness"} and requested == "public":
        return "blocked_public_claim"
    if claim_type == "performance" and ("faster" in text or "superior" in text or "savings" in text):
        return "blocked_public_claim"
    if claim_type == "ai_answer" and evidence_strength == "none":
        return "human_review_required"
    if claim_type == "redteam_robustness" and evidence_strength == "fixture_red_team_fail":
        return "blocked_public_claim"
    if claim_type == "redteam_robustness" and evidence_strength == "fixture_red_team_pass":
        return "candidate_only"
    if claim_type == "generated_stub_validation" and evidence_strength == "validated_replay_or_packet":
        return "candidate_only"
    if claim_type == "proof_status" and evidence_strength == "small_checked_witness":
        return "approved_bounded_public_claim"
    if requested == "public":
        return "candidate_only"
    return "candidate_only"


def allowed_surface(decision: str) -> str:
    if decision == "approved_bounded_public_claim":
        return "public_bounded"
    if decision in {"candidate_only", "human_review_required"}:
        return "candidate"
    return "private"


def next_action(decision: str, claim_type: str, evidence_strength: str) -> str:
    if decision == "approved_bounded_public_claim":
        return "surface only the bounded scoped claim with domain assumptions and evidence paths"
    if decision == "human_review_required":
        return "attach sources, reviewer notes, and a validator before any public surface"
    if decision == "blocked_public_claim":
        if claim_type == "compiler_correctness" and evidence_strength == "validated_replay_or_packet":
            return "run runtime bakeoff and scoped semantic proof before compiler correctness claims"
        return {
            "performance": "run broader runtime bakeoff before making any public performance claim",
            "forecasting": "build calibration ledger and keep all trade decisions human-reviewed",
            "external_theory": "decompose into small claims and run contradiction/formalization review",
            "hardware": "collect live capture packet before claiming hardware validation",
            "compiler_correctness": "validate generated stubs and prove scoped semantics before compiler claims",
            "generated_stub_validation": "run runtime bakeoff and scoped semantic proof before compiler claims",
            "redteam_robustness": "fix failing red-team adapter coverage before making any public robustness claim",
        }.get(claim_type, "keep private until supporting evidence exists")
    return "keep as candidate packet until required validators pass"


def review_notes(claim: dict[str, Any], evidence_strength: str, decision: str) -> list[str]:
    notes = [
        f"artifact_type:{claim['artifactType']}",
        f"claim_type:{claim['claimType']}",
        f"requested_surface:{claim['requestedSurface']}",
        f"evidence_strength:{evidence_strength}",
    ]
    if decision == "blocked_public_claim":
        notes.append("public wording exceeds current evidence")
    if decision == "approved_bounded_public_claim":
        notes.append("approval is scoped to the exact checked/bounded statement")
    if not claim.get("evidencePaths"):
        notes.append("no evidence paths attached")
    return notes


def non_claims_for(claim_type: str) -> list[str]:
    non_claims = list(BASE_NON_CLAIMS)
    if claim_type == "forecasting":
        non_claims.extend(["No financial advice.", "No profitable strategy claim.", "No autonomous trading claim."])
    if claim_type == "external_theory":
        non_claims.extend(["No endorsement of theory-of-everything claims.", "No physics-unification claim."])
    if claim_type == "hardware":
        non_claims.extend(["No hardware validation without live capture.", "No production controller claim."])
    if claim_type == "compiler_correctness":
        non_claims.extend(["No compiler correctness claim.", "No runtime semantic equivalence proof."])
    if claim_type == "generated_stub_validation":
        non_claims.extend(["No compiler correctness claim.", "No production lowering claim.", "No formal semantic equivalence claim."])
    if claim_type == "performance":
        non_claims.extend(["No general performance superiority claim.", "No public savings claim."])
    if claim_type == "proof_status":
        non_claims.extend(["No theorem claim beyond the named checked witness.", "No complete EML semantics claim."])
    if claim_type == "redteam_robustness":
        non_claims.extend(["No certified safety claim.", "No comprehensive robustness claim.", "No production security claim."])
    return non_claims


def review_claim(claim: dict[str, Any]) -> dict[str, Any]:
    evidence_strength = infer_evidence_strength(claim)
    decision = decision_for(claim, evidence_strength)
    claim_type = claim["claimType"]
    required_validators = REQUIRED_VALIDATORS_BY_TYPE.get(claim_type, ["human_review"])
    if claim_type == "compiler_correctness" and evidence_strength == "validated_replay_or_packet":
        required_validators = ["runtime_bakeoff", "scoped_semantic_proof", "formal_compiler_proof"]
    return {
        "schemaVersion": REVIEW_PACKET_SCHEMA_VERSION,
        "packetType": "claim_review_packet_v0",
        "date": DATE,
        "claimId": claim["claimId"],
        "claim": claim["claim"],
        "claimType": claim_type,
        "artifactType": claim["artifactType"],
        "sourceLane": claim.get("sourceLane", "unknown"),
        "requestedSurface": claim["requestedSurface"],
        "decision": decision,
        "evidenceStrength": evidence_strength,
        "allowedSurface": allowed_surface(decision),
        "evidencePaths": claim.get("evidencePaths", []),
        "evidenceSummary": claim.get("evidenceSummary", ""),
        "requiredValidators": required_validators,
        "blockedClaims": BLOCKED_CLAIMS_BY_TYPE.get(claim_type, ["unsupported_public_claim"]),
        "reviewNotes": review_notes(claim, evidence_strength, decision),
        "nextAction": next_action(decision, claim_type, evidence_strength),
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": non_claims_for(claim_type),
    }


def summarize(packets: list[dict[str, Any]]) -> dict[str, Any]:
    decisions: dict[str, int] = {}
    strengths: dict[str, int] = {}
    lanes: dict[str, int] = {}
    for packet in packets:
        decisions[packet["decision"]] = decisions.get(packet["decision"], 0) + 1
        strengths[packet["evidenceStrength"]] = strengths.get(packet["evidenceStrength"], 0) + 1
        lanes[packet["sourceLane"]] = lanes.get(packet["sourceLane"], 0) + 1
    return {
        "reviewPacketCount": len(packets),
        "decisions": decisions,
        "evidenceStrengths": strengths,
        "sourceLanes": lanes,
        "blockedPublicClaims": decisions.get("blocked_public_claim", 0),
        "boundedPublicApprovals": decisions.get("approved_bounded_public_claim", 0),
        "claimFlagsAllFalse": all(all(value is False for value in packet["claimFlags"].values()) for packet in packets),
        "publicReadyClaimMade": False,
        "deployPerformed": False,
        "tradePerformed": False,
        "hardwareActionPerformed": False,
        "compilerBehaviorChanged": False,
    }


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "rh-a1-universal-claim-review-harness",
        "title": "RH-A1 Universal Claim Review Harness",
        "reviewDecision": "claim_review_packets_recorded",
        "validationStatus": "pass",
        "replayStatus": "not_applicable",
        "semanticStrength": "deterministic_claim_classifier_no_truth_or_deployment_claim",
        "semanticReview": {
            "reviewPacketCount": payload["summary"]["reviewPacketCount"],
            "decisions": payload["summary"]["decisions"],
            "blockedPublicClaims": payload["summary"]["blockedPublicClaims"],
            "boundedPublicApprovals": payload["summary"]["boundedPublicApprovals"],
            "claimFlagsAllFalse": payload["summary"]["claimFlagsAllFalse"],
        },
        "claimBoundary": "Deterministic claim review packets only; RH-A1 classifies evidence and decisions but does not prove, deploy, trade, or publish.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(BASE_NON_CLAIMS),
        "reviewHighlights": [
            "Unifies EML, prediction-market, external-theory, electronics, compiler, proof, and AI-answer claim review.",
            "Blocks unsupported public claims and routes required validators.",
            "Allows only bounded scoped public approval for a small checked witness fixture.",
        ],
        "validationCommands": [
            "python python/scripts/rh_a1_universal_claim_review_harness.py --build --strict",
            "python -m pytest -q python/tests/test_rh_a1_universal_claim_review_harness.py",
        ],
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# RH-A1 Universal Claim Review Harness",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "RH-A1 is the common reviewer layer for Monogate claims. It turns",
        "interesting assertions into explicit decisions, evidence strengths,",
        "blocked claims, and next validators.",
        "",
        "## Review Packets",
        "",
        "| Claim | Type | Evidence | Decision | Allowed surface | Next action |",
        "|---|---|---|---|---|---|",
    ]
    for packet in payload["reviewPackets"]:
        lines.append(
            f"| `{packet['claimId']}` | `{packet['claimType']}` | `{packet['evidenceStrength']}` | "
            f"`{packet['decision']}` | `{packet['allowedSurface']}` | {packet['nextAction']} |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Review packets: `{payload['summary']['reviewPacketCount']}`",
            f"- Blocked public claims: `{payload['summary']['blockedPublicClaims']}`",
            f"- Bounded public approvals: `{payload['summary']['boundedPublicApprovals']}`",
            f"- Claim flags all false: `{payload['summary']['claimFlagsAllFalse']}`",
            f"- Trade performed: `{payload['summary']['tradePerformed']}`",
            f"- Hardware action performed: `{payload['summary']['hardwareActionPerformed']}`",
            f"- Compiler behavior changed: `{payload['summary']['compilerBehaviorChanged']}`",
            "",
            "## Boundary",
            "",
            "- RH-A1 classifies claims; it does not prove them.",
            "- RH-A1 does not deploy, trade, publish, operate hardware, or change compiler behavior.",
            "- Public approval is scoped and bounded, never global.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_review_packet(packet: dict[str, Any]) -> None:
    if packet.get("schemaVersion") != REVIEW_PACKET_SCHEMA_VERSION:
        raise ValueError("invalid review packet schema")
    if packet["decision"] == "approved_bounded_public_claim" and packet["evidenceStrength"] != "small_checked_witness":
        raise ValueError("bounded public approval requires small checked witness in RH-A1 fixtures")
    if packet["allowedSurface"] == "public_bounded" and packet["decision"] != "approved_bounded_public_claim":
        raise ValueError("public_bounded surface requires bounded approval")
    if packet["requestedSurface"] == "public" and packet["decision"] == "approved_bounded_public_claim":
        if "general_theorem_claim_beyond_checked_witness" not in packet["blockedClaims"]:
            raise ValueError("proof approval must still block generalized theorem claim")
    for key, value in packet.get("claimFlags", {}).items():
        if value is not False:
            raise ValueError(f"claim flag must remain false for {packet['claimId']}: {key}")


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid RH-A1 schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid RH-A1 status")
    if payload["summary"]["reviewPacketCount"] < 7:
        raise ValueError("expected at least 7 review packets")
    for key in [
        "claimFlagsAllFalse",
    ]:
        if payload["summary"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "publicReadyClaimMade",
        "deployPerformed",
        "tradePerformed",
        "hardwareActionPerformed",
        "compilerBehaviorChanged",
    ]:
        if payload["summary"][key] is not False:
            raise ValueError(f"{key} must be false")
    for key, value in payload.get("claimFlags", {}).items():
        if value is not False:
            raise ValueError(f"payload claim flag must remain false: {key}")
    for packet in payload["reviewPackets"]:
        validate_review_packet(packet)


def build_harness(
    fixture_path: Path,
    out_dir: Path,
    packet_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
) -> dict[str, Any]:
    fixture = load_json(fixture_path)
    packets = [review_claim(claim) for claim in fixture["claims"]]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "sourceFixturePath": str(fixture_path),
        "reviewPackets": packets,
        "summary": summarize(packets),
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(BASE_NON_CLAIMS),
    }
    validate_payload(payload)
    evidence = build_evidence_packet(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    packet_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    stamp = DATE.replace("-", "_")
    result_path = out_dir / f"rh_a1_universal_claim_review_harness_{stamp}.json"
    report_path = report_dir / f"rh_a1_universal_claim_review_harness_{stamp}.md"
    evidence_path = evidence_dir / "rh_a1_universal_claim_review_harness.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for packet in packets:
        packet_path = packet_dir / f"{slug(packet['claimId'])}_claim_review_packet_{stamp}.json"
        packet_path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "evidence": evidence,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--fixture-path", type=Path, default=ROOT / "python/fixtures/review_harness/rh_a1_claims.json")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/rh_a1_universal_claim_review_harness")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/claim_review_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_harness(args.fixture_path, args.out_dir, args.packet_dir, args.report_dir, args.evidence_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("RH_A1_UNIVERSAL_CLAIM_REVIEW_HARNESS_OK")
    print(f"review_packets={built['payload']['summary']['reviewPacketCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
