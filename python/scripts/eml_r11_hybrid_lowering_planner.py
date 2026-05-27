#!/usr/bin/env python3
"""EML-R11 hybrid lowering planner.

Consumes R10 cost packets and Atlas gate status, then emits candidate lowering
plans. The planner does not compile, deploy, change Forge behavior, or claim
that EML is operationally superior. It records which implementation a future
runtime should prefer under current evidence.
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

from scripts.eml_language_kernel import DATE  # noqa: E402
from scripts.eml_packet_builder import DEFAULT_CLAIM_FLAGS  # noqa: E402

SCHEMA_VERSION = "monogate.eml_r11_hybrid_lowering_planner.v0"
PLAN_SCHEMA_VERSION = "monogate.eml_lowering_plan_packet.v0"
STATUS = "EML_R11_HYBRID_LOWERING_PLANNER_PASS"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"


CASE_TO_ATLAS_ID = {
    "exp_from_eml_v0": "exp_from_eml",
    "subtraction_boundary_v0": "subtraction_boundary",
    "bose_boundary_expm1_v0": "bose_boundary",
    "ln_from_eml_v0": "ln_from_eml",
}


STANDARD_LOWERINGS = {
    "exp_from_eml_v0": "exp(x)",
    "subtraction_boundary_v0": "v - u",
    "bose_boundary_expm1_v0": "expm1(x)",
    "ln_from_eml_v0": "log(y)",
    "softplus_pair_v0": "logaddexp(a, b)",
    "sigmoid_derivative_v0": "stable_sigmoid(x) * (1 - stable_sigmoid(x))",
    "gaussian_energy_v0": "2 * exp(-(x * x))",
}


HYBRID_LOWERINGS = {
    "exp_from_eml_v0": "preserve EML packet identity; lower runtime call to exp(x)",
    "subtraction_boundary_v0": "preserve EML witness metadata; lower runtime call to v - u",
    "bose_boundary_expm1_v0": "preserve Bose boundary identity; lower near-zero runtime call to expm1(x)",
    "ln_from_eml_v0": "preserve EML derivation; lower runtime call to log(y) with y > 0 guard",
    "softplus_pair_v0": "preserve expression packet; lower runtime call to logaddexp(a, b)",
    "sigmoid_derivative_v0": "preserve replay expression; lower runtime call to stable sigmoid derivative",
    "gaussian_energy_v0": "preserve DAG reuse note; lower runtime call to shared exp node or 2*exp(-(x*x))",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atlas_index(atlas_gate: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in atlas_gate.get("decisions", [])}


def atlas_gate_for(case_id: str, index: dict[str, dict[str, Any]]) -> dict[str, Any]:
    atlas_id = CASE_TO_ATLAS_ID.get(case_id, "not_in_atlas_gate")
    decision = index.get(atlas_id)
    if decision is None:
        return {
            "atlasId": atlas_id,
            "bucket": "not_in_atlas_gate",
            "proofStatus": "not_a_current_proof_target",
            "publicEducationCandidate": False,
            "publicPromotionPerformed": False,
        }
    return {
        "atlasId": atlas_id,
        "bucket": decision["bucket"],
        "proofStatus": decision["proofStatus"],
        "publicEducationCandidate": decision["publicEducationCandidate"],
        "publicPromotionPerformed": False,
    }


def lowering_decision(cost_recommendation: str) -> str:
    return {
        "use_eml": "emit_eml",
        "use_standard": "emit_standard",
        "use_hybrid": "emit_hybrid",
        "research_only": "block_lowering",
    }[cost_recommendation]


def reason_codes(cost_packet: dict[str, Any], gate: dict[str, Any]) -> list[str]:
    eml = cost_packet["comparison"]["eml"]
    standard = cost_packet["comparison"]["standard"]
    reasons = [f"r10_recommendation:{cost_packet['recommendation']}"]
    if eml["maxRelError"] > standard["maxRelError"]:
        reasons.append("standard_has_lower_relative_error")
    if standard["latencyNsPerSample"] < eml["latencyNsPerSample"]:
        reasons.append("standard_has_lower_local_latency")
    if standard["operatorCount"] < eml["operatorCount"]:
        reasons.append("standard_has_lower_static_operator_count")
    if gate["proofStatus"] == "checked_machlib_witness_available":
        reasons.append("checked_machlib_witness_available")
    if gate["bucket"] == "safe_public_education_candidate":
        reasons.append("atlas_safe_education_candidate_only")
    if gate["bucket"] == "not_in_atlas_gate":
        reasons.append("no_atlas_gate_entry")
    return reasons


def required_guards(cost_packet: dict[str, Any]) -> list[str]:
    case_id = cost_packet["caseId"]
    guards = [f"{name}_in_[{bounds['min']},{bounds['max']}]" for name, bounds in sorted(cost_packet["ranges"].items())]
    if case_id in {"ln_from_eml_v0", "subtraction_boundary_v0"}:
        guards.append("positive_log_argument")
    if case_id == "bose_boundary_expm1_v0":
        guards.append("near_zero_requires_expm1_lowering")
    if case_id == "softplus_pair_v0":
        guards.append("use_logaddexp_to_avoid_exp_overflow")
    if case_id == "sigmoid_derivative_v0":
        guards.append("use_stable_sigmoid_for_large_magnitude_inputs")
    return guards


def precision_caveats(cost_packet: dict[str, Any]) -> list[str]:
    case_id = cost_packet["caseId"]
    caveats = ["finite_precision_result_is_local_to_r10_sample_grid"]
    if cost_packet["comparison"]["eml"]["maxRelError"] > cost_packet["comparison"]["standard"]["maxRelError"]:
        caveats.append("eml_form_has_higher_relative_error_on_current_grid")
    if case_id == "bose_boundary_expm1_v0":
        caveats.append("exp(x)-1_cancels_near_zero; prefer_expm1")
    if case_id == "ln_from_eml_v0":
        caveats.append("nested_eml_log_recovery_is_deeper_than_direct_log")
    if case_id == "softplus_pair_v0":
        caveats.append("plain_log_sum_exp_can_overflow_outside_current_grid")
    return caveats


def selected_implementation(case_id: str, decision: str, source_expression: str) -> str:
    if decision == "emit_eml":
        return source_expression
    if decision == "emit_standard":
        return STANDARD_LOWERINGS.get(case_id, source_expression)
    if decision == "emit_hybrid":
        return HYBRID_LOWERINGS.get(case_id, source_expression)
    return "blocked: research-only until more evidence is available"


def plan_from_cost_packet(cost_packet: dict[str, Any], gate_index: dict[str, dict[str, Any]]) -> dict[str, Any]:
    case_id = cost_packet["caseId"]
    gate = atlas_gate_for(case_id, gate_index)
    decision = lowering_decision(cost_packet["recommendation"])
    implementation = selected_implementation(case_id, decision, cost_packet["expression"])
    blocked = list(cost_packet["blockedClaims"])
    blocked.extend(
        [
            "No compiler correctness claim.",
            "No deployment or package publication claim.",
            "No claim that this plan is production lowering.",
        ]
    )
    return {
        "schemaVersion": PLAN_SCHEMA_VERSION,
        "packetType": "eml_lowering_plan_packet_v0",
        "date": DATE,
        "caseId": case_id,
        "sourceExpression": cost_packet["expression"],
        "standardExpression": cost_packet["standardExpression"],
        "costRecommendation": cost_packet["recommendation"],
        "loweringDecision": decision,
        "selectedImplementation": implementation,
        "fallbackImplementation": STANDARD_LOWERINGS.get(case_id, cost_packet["standardExpression"]),
        "reasonCodes": reason_codes(cost_packet, gate),
        "requiredGuards": required_guards(cost_packet),
        "precisionCaveats": precision_caveats(cost_packet),
        "blockedClaims": blocked,
        "atlasGate": gate,
        "claimFlags": dict(DEFAULT_CLAIM_FLAGS),
        "nonClaims": [
            "This plan is a candidate reviewer artifact, not compiler output.",
            "This plan does not change Forge/compiler/runtime behavior.",
            "This plan does not make public savings, proof, or production claims.",
        ],
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-R11 Hybrid Lowering Planner",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "Monogate does not compile beauty directly. It routes symbolic forms",
        "through evidence before choosing EML, standard, hybrid, or blocked",
        "lowering.",
        "",
        "| Case | R10 recommendation | Lowering decision | Selected implementation |",
        "|---|---|---|---|",
    ]
    for plan in payload["plans"]:
        lines.append(
            f"| `{plan['caseId']}` | `{plan['costRecommendation']}` | "
            f"`{plan['loweringDecision']}` | `{plan['selectedImplementation']}` |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Plans: `{payload['summary']['planCount']}`",
            f"- `emit_eml`: `{payload['summary']['decisions'].get('emit_eml', 0)}`",
            f"- `emit_standard`: `{payload['summary']['decisions'].get('emit_standard', 0)}`",
            f"- `emit_hybrid`: `{payload['summary']['decisions'].get('emit_hybrid', 0)}`",
            f"- `block_lowering`: `{payload['summary']['decisions'].get('block_lowering', 0)}`",
            "",
            "## Boundary",
            "",
            "- Candidate plans only.",
            "- Forge/compiler behavior is unchanged.",
            "- No public savings, proof, or production lowering claim is made.",
            "",
        ]
    )
    return "\n".join(lines)


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-r11-hybrid-lowering-planner",
        "title": "EML-R11 Hybrid Lowering Planner",
        "reviewDecision": "candidate_lowering_plans_recorded",
        "validationStatus": "pass",
        "replayStatus": "not_applicable",
        "semanticStrength": "candidate_planner_no_compiler_or_runtime_claim",
        "semanticReview": {
            "plan_count": payload["summary"]["planCount"],
            "decisions": payload["summary"]["decisions"],
            "compiler_behavior_changed": False,
        },
        "claimBoundary": "Candidate lowering plans only; no compiler behavior, deployment, public savings, or proof claim.",
        "claimFlags": {
            **dict(DEFAULT_CLAIM_FLAGS),
            "compiler_behavior_changed": False,
            "forge_behavior_changed": False,
            "public_savings_claim": False,
            "deploy_performed": False,
        },
        "nonClaims": payload["nonClaims"],
        "reviewHighlights": [
            "Consumes R10 cost packets and Atlas gate status.",
            "Routes each fixture to standard, hybrid, EML, or blocked lowering.",
        ],
        "validationCommands": [
            "python python/scripts/eml_r11_hybrid_lowering_planner.py --build --strict",
            "python -m pytest -q python/tests/test_eml_r11_hybrid_lowering_planner.py",
        ],
    }


def build_planner(
    cost_lab_path: Path,
    atlas_gate_path: Path,
    out_dir: Path,
    plan_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
) -> dict[str, Any]:
    cost_lab = load_json(cost_lab_path)
    atlas_gate = load_json(atlas_gate_path)
    gate_index = atlas_index(atlas_gate)
    plans = [plan_from_cost_packet(packet, gate_index) for packet in cost_lab["costPackets"]]
    decisions: dict[str, int] = {}
    for plan in plans:
        decisions[plan["loweringDecision"]] = decisions.get(plan["loweringDecision"], 0) + 1
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "sourceCostLabPath": str(cost_lab_path),
        "sourceAtlasGatePath": str(atlas_gate_path),
        "plans": plans,
        "summary": {
            "planCount": len(plans),
            "decisions": decisions,
            "compilerBehaviorChanged": False,
            "forgeBehaviorChanged": False,
            "publicPromotionPerformed": False,
        },
        "claimFlags": dict(DEFAULT_CLAIM_FLAGS),
        "nonClaims": [
            "R11 does not compile or lower code.",
            "R11 does not change Forge/compiler/runtime behavior.",
            "R11 does not make public performance, proof, or production claims.",
        ],
    }
    evidence = build_evidence_packet(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    plan_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    stamp = DATE.replace("-", "_")
    result_path = out_dir / f"eml_r11_hybrid_lowering_planner_{stamp}.json"
    report_path = report_dir / f"eml_r11_hybrid_lowering_planner_{stamp}.md"
    evidence_path = evidence_dir / "eml_r11_hybrid_lowering_planner.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for plan in plans:
        path = plan_dir / f"{plan['caseId']}_lowering_plan_{stamp}.json"
        path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "evidence": evidence,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
    }


def validate_planner(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid R11 schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid R11 status")
    if payload["summary"]["planCount"] < 7:
        raise ValueError("expected at least 7 lowering plans")
    for key in ["compilerBehaviorChanged", "forgeBehaviorChanged", "publicPromotionPerformed"]:
        if payload["summary"][key] is not False:
            raise ValueError(f"{key} must remain false")
    for key, value in payload.get("claimFlags", {}).items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")
    for plan in payload["plans"]:
        if plan["schemaVersion"] != PLAN_SCHEMA_VERSION:
            raise ValueError(f"invalid plan schema: {plan.get('caseId')}")
        if plan["atlasGate"]["publicPromotionPerformed"] is not False:
            raise ValueError(f"unexpected public promotion: {plan['caseId']}")
        if plan["loweringDecision"] == "emit_eml":
            raise ValueError("first R11 pass should not emit pure EML")
        for key, value in plan.get("claimFlags", {}).items():
            if value is not False:
                raise ValueError(f"claim flag must remain false for {plan['caseId']}: {key}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument(
        "--cost-lab-path",
        type=Path,
        default=ROOT / f"python/results/eml_r10_cost_stability_lab/eml_r10_cost_stability_lab_{DATE.replace('-', '_')}.json",
    )
    parser.add_argument(
        "--atlas-gate-path",
        type=Path,
        default=ROOT / f"python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_{DATE.replace('-', '_')}.json",
    )
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_r11_hybrid_lowering_planner")
    parser.add_argument("--plan-dir", type=Path, default=ROOT / "python/results/eml_lowering_plans")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_planner(
        args.cost_lab_path,
        args.atlas_gate_path,
        args.out_dir,
        args.plan_dir,
        args.report_dir,
        args.evidence_dir,
    )
    if args.strict:
        validate_planner(built["payload"])
    print("EML_R11_HYBRID_LOWERING_PLANNER_OK")
    print(f"plans={built['payload']['summary']['planCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
