#!/usr/bin/env python3
"""EML-D16 subtraction-boundary family witness selector."""

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

from scripts import eml_d15_checked_witness_next_decision as d15  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_subtraction_boundary_family_selector.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D16_SUBTRACTION_BOUNDARY_FAMILY_SELECTOR_PASS"

CLAIM_FLAGS = {
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved": False,
    "theorem_discovery_claim": False,
    "general_eml_superiority_claim": False,
    "eml_advantage_proved": False,
    "runtime_performance_claim": False,
    "runtime_lowering_changed": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "full_eml_semantics_claim": False,
    "public_atlas_promotion": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "EML-D16 selects a subtraction-boundary family statement only; it does not edit MachLib or typecheck Lean.",
    "D16 does not prove a new theorem, prove broad EML advantage, prove full EML semantics, prove compiler correctness, claim runtime performance, claim formal equivalence, or promote public Atlas copy.",
    "The selected statement remains proof/teaching-shape work; standard subtraction remains the runtime lowering control.",
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
        "rationale": rationale,
        "blockers": blockers,
        "runtimeLoweringControl": "standard_subtraction_remains_runtime_control",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    decision = d15.build_payload(atlas_gate_path)
    d15.validate_payload(decision)
    candidates = [
        candidate_statement(
            "subtraction_boundary_base_duplicate_v0",
            "eml (log v) (exp u) = v - u, under 0 < v",
            "MachLib.Real.atlas_subtraction_boundary_witness",
            "rejected_duplicate_checked_base",
            30,
            "already_checked",
            "exact checked base witness already exists",
            ["0 < v"],
            [
                "This is already checked as MachLib.Real.atlas_subtraction_boundary_witness.",
                "Selecting it would create duplicate proof work instead of a family generalization.",
            ],
            ["duplicate base witness"],
        ),
        candidate_statement(
            "subtraction_boundary_affine_offset_family_v1",
            "eml (log (x + y)) (exp y) = x, under 0 < x + y",
            "MachLib.Real.subtraction_boundary_affine_offset_witness",
            "selected_next",
            72,
            "small_substitution_from_checked_base",
            "substitution instance of checked base witness with v = x + y and u = y",
            ["0 < x + y"],
            [
                "It is a real family-shaped statement rather than a duplicate of the base witness.",
                "It exposes the positive branch guard on the shifted coordinate x + y.",
                "It remains close enough to the checked base witness to be a plausible D17 proof attempt.",
            ],
            ["requires exact family statement review before MachLib edit"],
        ),
        candidate_statement(
            "subtraction_boundary_two_stage_chain_v1",
            "eml (log v) (exp (eml (log w) (exp u))) = v - (w - u), under 0 < v and 0 < w",
            "MachLib.Real.subtraction_boundary_two_stage_chain_witness",
            "candidate_later",
            51,
            "nested_rewrite",
            "nested use of checked base witness",
            ["0 < v", "0 < w"],
            [
                "This could test compositional proof reuse, but it is more complex than the affine-offset family.",
                "It should wait until the simple family statement is selected or rejected.",
            ],
            ["nested rewrite surface", "avoid deepening before simple family target"],
        ),
        candidate_statement(
            "subtraction_boundary_unguarded_negative_control_v1",
            "eml (log z) (exp y) = z - y, with no positive-domain guard",
            "none",
            "blocked_negative_control",
            5,
            "invalid_guard_missing",
            "negative control for missing log-domain guard",
            [],
            [
                "The positive-domain guard is required for the real-branch log expression.",
                "This row keeps the selector from silently dropping guard obligations.",
            ],
            ["missing positive log-domain guard"],
        ),
    ]
    selected = next(item for item in candidates if item["selectionStatus"] == "selected_next")
    summary = {
        "sourceDecision": decision["artifactId"],
        "sourceSelectedCandidateId": decision["summary"]["selectedCandidateId"],
        "candidateStatementCount": len(candidates),
        "selectedStatementId": selected["statementId"],
        "selectedProofTarget": selected["proofTarget"],
        "selectedNextArtifact": "EML-D17 subtraction-boundary affine-offset witness attempt",
        "duplicateBaseRejected": any(item["selectionStatus"] == "rejected_duplicate_checked_base" for item in candidates),
        "negativeControlBlocked": any(item["selectionStatus"] == "blocked_negative_control" for item in candidates),
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProved": False,
        "runtimeLoweringControl": selected["runtimeLoweringControl"],
        "runtimeLoweringChanged": False,
        "publicReady": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values())
        and all(all(value is False for value in item["claimFlags"].values()) for item in candidates),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "selectorType": "eml_subtraction_boundary_family_selector_v0",
        "artifactId": "eml-d16-subtraction-boundary-family-selector",
        "status": STATUS,
        "decision": "select_subtraction_boundary_affine_offset_family",
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
    if payload["sourceDecision"] != "eml-d15-checked-witness-next-decision":
        raise ValueError("D16 must consume D15")
    if summary["sourceSelectedCandidateId"] != "subtraction_boundary_family_v1":
        raise ValueError("D16 must follow the subtraction family branch")
    if summary["candidateStatementCount"] != 4:
        raise ValueError("expected four candidate statements")
    if summary["selectedStatementId"] != "subtraction_boundary_affine_offset_family_v1":
        raise ValueError("unexpected selected statement")
    if summary["selectedProofTarget"] != "MachLib.Real.subtraction_boundary_affine_offset_witness":
        raise ValueError("unexpected proof target")
    if summary["duplicateBaseRejected"] is not True:
        raise ValueError("duplicate base witness must be rejected")
    if summary["negativeControlBlocked"] is not True:
        raise ValueError("unguarded negative control must be blocked")
    for key in [
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "candidateProved",
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
        "artifactType": "eml_subtraction_boundary_family_selector",
        "validationStatus": "pass",
        "semanticStrength": "private_statement_selector_no_machlib_edit_no_typecheck",
        "source": f"python/results/eml_d16_subtraction_boundary_family_selector/eml_d16_subtraction_boundary_family_selector_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d16_subtraction_boundary_family_selector_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedStatementId": payload["summary"]["selectedStatementId"],
        "selectedProofTarget": payload["summary"]["selectedProofTarget"],
        "nextAction": "Attempt D17 only after reviewing the affine-offset statement; do not duplicate the checked base witness.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D16 Subtraction Boundary Family Selector",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Selected statement: `{payload['summary']['selectedStatementId']}`",
        "",
        "D16 chooses a precise family-shaped statement before any MachLib proof attempt.",
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
            f"- duplicate base rejected: `{payload['summary']['duplicateBaseRejected']}`",
            f"- negative control blocked: `{payload['summary']['negativeControlBlocked']}`",
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
    result_path = out_dir / f"eml_d16_subtraction_boundary_family_selector_{STAMP}.json"
    report_path = report_dir / f"eml_d16_subtraction_boundary_family_selector_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d16_subtraction_boundary_family_selector.json"
    feed_path = command_feed_dir / f"eml_d16_subtraction_boundary_family_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d16_subtraction_boundary_family_selector")
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
    print("EML_D16_SUBTRACTION_BOUNDARY_FAMILY_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
