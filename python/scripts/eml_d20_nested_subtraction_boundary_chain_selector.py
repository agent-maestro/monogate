#!/usr/bin/env python3
"""EML-D20 nested subtraction-boundary chain selector."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import eml_d19_next_proof_family_branch_decision as d19  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_nested_subtraction_boundary_chain_selector.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D20_NESTED_SUBTRACTION_BOUNDARY_CHAIN_SELECTOR_PASS"

CLAIM_FLAGS = {
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved": False,
    "broad_nested_subtraction_claim": False,
    "broad_subtraction_family_claim": False,
    "theorem_discovery_claim": False,
    "general_eml_superiority_claim": False,
    "eml_advantage_proved": False,
    "runtime_performance_claim": False,
    "runtime_lowering_changed": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "full_eml_semantics_claim": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "EML-D20 selects a nested subtraction-boundary chain statement only; it does not edit MachLib or typecheck Lean.",
    "D20 does not prove a theorem, prove a broad nested subtraction family, prove broad EML advantage, prove full EML semantics, prove compiler correctness, claim runtime performance, claim formal equivalence, or promote public Atlas copy.",
    "The selected nested chain remains proof/teaching-shape work; standard subtraction remains the runtime lowering control.",
]


def candidate_statement(
    statement_id: str,
    statement: str,
    proof_target: str,
    selection_status: str,
    priority_score: int,
    difficulty: str,
    relation_to_checked_base: str,
    domain_guards: list[str],
    expected_rewrite_steps: list[str],
    rationale: list[str],
    blockers: list[str],
) -> dict[str, Any]:
    return {
        "statementId": statement_id,
        "statement": statement,
        "proofTarget": proof_target,
        "selectionStatus": selection_status,
        "priorityScore": priority_score,
        "estimatedDifficulty": difficulty,
        "relationToCheckedBase": relation_to_checked_base,
        "domainGuards": domain_guards,
        "expectedRewriteSteps": expected_rewrite_steps,
        "rationale": rationale,
        "blockers": blockers,
        "runtimeLoweringControl": "standard_subtraction_remains_runtime_control",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    decision = d19.build_payload(atlas_gate_path)
    d19.validate_payload(decision)
    candidates = [
        candidate_statement(
            "subtraction_boundary_two_stage_chain_v1",
            "eml (log v) (exp (eml (log w) (exp u))) = v - (w - u), under 0 < v and 0 < w",
            "MachLib.Real.subtraction_boundary_two_stage_chain_witness",
            "selected_next",
            76,
            "nested_two_step_rewrite",
            "two nested uses of checked subtraction-boundary witness",
            ["0 < v", "0 < w"],
            [
                "rewrite inner eml (log w) (exp u) to w - u",
                "rewrite outer eml (log v) (exp (w - u)) to v - (w - u)",
            ],
            [
                "This is the smallest nested chain that tests compositional reuse of the checked base witness.",
                "It preserves explicit positive log-domain guards for both real-log arguments.",
                "It is complex enough to open the next proof-family door but small enough for a D21 MachLib attempt.",
            ],
            ["requires exact Lean statement review before MachLib edit", "must avoid claiming all nested chains"],
        ),
        candidate_statement(
            "subtraction_boundary_affine_nested_chain_v1",
            "eml (log (x + y)) (exp (eml (log z) (exp y))) = (x + y) - (z - y), under 0 < x + y and 0 < z",
            "MachLib.Real.subtraction_boundary_affine_nested_chain_witness",
            "candidate_later",
            63,
            "nested_affine_rewrite",
            "combines D17 affine-offset substitution with nested base rewrite",
            ["0 < x + y", "0 < z"],
            [
                "rewrite inner eml (log z) (exp y) to z - y",
                "rewrite outer eml (log (x + y)) (exp (z - y)) to (x + y) - (z - y)",
            ],
            [
                "This may become the next family step after the simple two-stage chain.",
                "It exercises the D17 affine-offset shape but adds more algebraic normalization burden.",
            ],
            ["more notation and algebra than the minimal chain", "wait for D21 result"],
        ),
        candidate_statement(
            "subtraction_boundary_three_stage_chain_v1",
            "three nested subtraction-boundary rewrites under positive log-domain guards",
            "MachLib.Real.subtraction_boundary_three_stage_chain_witness",
            "candidate_later",
            45,
            "overdeep_for_next_witness",
            "three nested uses of checked subtraction-boundary witness",
            ["0 < a", "0 < b", "0 < c"],
            [
                "rewrite innermost subtraction boundary",
                "rewrite middle subtraction boundary",
                "rewrite outer subtraction boundary",
            ],
            [
                "A three-stage chain would test deeper composition later.",
                "It should wait until the two-stage chain either checks cleanly or exposes proof-surface gaps.",
            ],
            ["too deep for the next witness attempt", "higher risk of algebraic surface drift"],
        ),
        candidate_statement(
            "subtraction_boundary_nested_unguarded_negative_control_v1",
            "eml (log v) (exp (eml (log w) (exp u))) = v - (w - u), with missing positive-domain guards",
            "none",
            "blocked_negative_control",
            5,
            "invalid_guard_missing",
            "negative control for missing nested log-domain guards",
            [],
            [],
            [
                "Both log arguments need positive-domain guards.",
                "This row prevents the nested-chain selector from treating guard obligations as optional.",
            ],
            ["missing positive log-domain guards"],
        ),
    ]
    selected = next(item for item in candidates if item["selectionStatus"] == "selected_next")
    summary = {
        "sourceDecision": decision["artifactId"],
        "sourceSelectedOptionId": decision["summary"]["selectedOptionId"],
        "candidateStatementCount": len(candidates),
        "selectedStatementId": selected["statementId"],
        "selectedProofTarget": selected["proofTarget"],
        "selectedNextArtifact": "EML-D21 subtraction-boundary two-stage chain witness attempt",
        "negativeControlBlocked": any(item["selectionStatus"] == "blocked_negative_control" for item in candidates),
        "deeperChainParked": any(item["statementId"] == "subtraction_boundary_three_stage_chain_v1" and item["selectionStatus"] == "candidate_later" for item in candidates),
        "affineNestedChainParked": any(item["statementId"] == "subtraction_boundary_affine_nested_chain_v1" and item["selectionStatus"] == "candidate_later" for item in candidates),
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProved": False,
        "broadNestedSubtractionClaim": False,
        "broadSubtractionFamilyClaim": False,
        "runtimeLoweringControl": selected["runtimeLoweringControl"],
        "runtimeLoweringChanged": False,
        "publicReady": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values())
        and all(all(value is False for value in item["claimFlags"].values()) for item in candidates),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "selectorType": "eml_nested_subtraction_boundary_chain_selector_v0",
        "artifactId": "eml-d20-nested-subtraction-boundary-chain-selector",
        "status": STATUS,
        "decision": "select_subtraction_boundary_two_stage_chain",
        "date": DATE,
        "sourceDecision": decision["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "candidateStatements": candidates,
        "selectedStatement": selected,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceDecision"] != "eml-d19-next-proof-family-branch-decision":
        raise ValueError("D20 must consume D19")
    if summary["sourceSelectedOptionId"] != "nested_subtraction_boundary_chain_selector":
        raise ValueError("D20 must follow the nested-chain branch")
    if summary["candidateStatementCount"] != 4:
        raise ValueError("expected four candidate statements")
    if summary["selectedStatementId"] != "subtraction_boundary_two_stage_chain_v1":
        raise ValueError("unexpected selected statement")
    if summary["selectedProofTarget"] != "MachLib.Real.subtraction_boundary_two_stage_chain_witness":
        raise ValueError("unexpected proof target")
    if summary["selectedNextArtifact"] != "EML-D21 subtraction-boundary two-stage chain witness attempt":
        raise ValueError("unexpected next artifact")
    if summary["negativeControlBlocked"] is not True:
        raise ValueError("unguarded negative control must be blocked")
    if summary["deeperChainParked"] is not True or summary["affineNestedChainParked"] is not True:
        raise ValueError("later nested chains must remain parked")
    for key in [
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "candidateProved",
        "broadNestedSubtractionClaim",
        "broadSubtractionFamilyClaim",
        "runtimeLoweringChanged",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["runtimeLoweringControl"] != "standard_subtraction_remains_runtime_control":
        raise ValueError("runtime control drift")
    if not all(value is False for value in payload["claimFlags"].values()):
        raise ValueError("claim flag drift")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_nested_subtraction_boundary_chain_selector",
        "validationStatus": "pass",
        "semanticStrength": "private_nested_statement_selector_no_machlib_edit_no_typecheck",
        "source": f"python/results/eml_d20_nested_subtraction_boundary_chain_selector/eml_d20_nested_subtraction_boundary_chain_selector_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d20_nested_subtraction_boundary_chain_selector_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedStatementId": payload["summary"]["selectedStatementId"],
        "selectedProofTarget": payload["summary"]["selectedProofTarget"],
        "nextAction": "Attempt D21 only after reviewing the two-stage nested statement and both positive log-domain guards; do not claim broad nested subtraction support.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D20 Nested Subtraction Boundary Chain Selector",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Selected statement: `{payload['summary']['selectedStatementId']}`",
        "",
        "D20 chooses the smallest nested subtraction-boundary chain before any MachLib proof attempt.",
        "",
        "| Statement | Status | Score | Proof target |",
        "|---|---|---:|---|",
    ]
    for item in payload["candidateStatements"]:
        lines.append(
            f"| `{item['statementId']}` | `{item['selectionStatus']}` | {item['priorityScore']} | `{item['proofTarget']}` |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- negative control blocked: `{payload['summary']['negativeControlBlocked']}`",
            f"- affine nested chain parked: `{payload['summary']['affineNestedChainParked']}`",
            f"- deeper chain parked: `{payload['summary']['deeperChainParked']}`",
            f"- implementation started: `{payload['summary']['implementationStarted']}`",
            f"- Lean typecheck performed: `{payload['summary']['leanTypecheckPerformed']}`",
            f"- runtime lowering control: `{payload['summary']['runtimeLoweringControl']}`",
            "",
            "## Non-Claims",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["nonClaims"])
    return "\n".join(lines) + "\n"


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path, atlas_gate_path: Path) -> dict[str, Any]:
    payload = build_payload(atlas_gate_path)
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"eml_d20_nested_subtraction_boundary_chain_selector_{STAMP}.json"
    report_path = report_dir / f"eml_d20_nested_subtraction_boundary_chain_selector_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d20_nested_subtraction_boundary_chain_selector.json"
    feed_path = command_feed_dir / f"eml_d20_nested_subtraction_boundary_chain_selector_feed_{STAMP}.json"
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
    stamp_0527 = "2026_05_27"
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--atlas-gate-path", type=Path, default=ROOT / f"python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_{stamp_0527}.json")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d20_nested_subtraction_boundary_chain_selector")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(args.atlas_gate_path)
    validate_payload(payload)
    if args.build:
        build_outputs(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir, args.atlas_gate_path)
    print("EML_D20_NESTED_SUBTRACTION_BOUNDARY_CHAIN_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
