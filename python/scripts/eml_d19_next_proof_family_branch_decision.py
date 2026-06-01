#!/usr/bin/env python3
"""EML-D19 next proof-family branch decision."""

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

from scripts import eml_d18_subtraction_boundary_affine_offset_surface_review as d18  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_next_proof_family_branch_decision.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D19_NEXT_PROOF_FAMILY_BRANCH_DECISION_PASS"

CLAIM_FLAGS = {
    "copy_review_started": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved": False,
    "broad_subtraction_family_claim": False,
    "theorem_discovery_claim": False,
    "general_eml_superiority_claim": False,
    "eml_advantage_proved": False,
    "runtime_performance_claim": False,
    "runtime_lowering_changed": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "full_eml_semantics_claim": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "EML-D19 chooses the next private proof-family branch after D18; it does not start copy review, edit MachLib, or typecheck Lean.",
    "D19 does not prove a theorem, prove broad EML advantage, prove full EML semantics, prove compiler correctness, claim runtime performance, claim formal equivalence, or promote public Atlas copy.",
    "The selected nested-chain branch is selector-only; standard subtraction remains the runtime lowering control.",
]


def decision_option(
    option_id: str,
    lane: str,
    status: str,
    priority_score: int,
    next_artifact: str,
    rationale: list[str],
    blockers: list[str],
) -> dict[str, Any]:
    return {
        "optionId": option_id,
        "lane": lane,
        "selectionStatus": status,
        "priorityScore": priority_score,
        "nextArtifact": next_artifact,
        "rationale": rationale,
        "blockers": blockers,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    surface = d18.build_payload(atlas_gate_path)
    d18.validate_payload(surface)
    options = [
        decision_option(
            "nested_subtraction_boundary_chain_selector",
            "private_proof_family_lane",
            "selected_next",
            71,
            "EML-D20 nested subtraction-boundary chain selector",
            [
                "D16 selected a simple affine-offset family instance and D17 checked it.",
                "D18 preserved the scoped-instance boundary, so the next research step can test compositional proof reuse without making a broad family claim.",
                "A selector-only nested-chain phase can compare chain statements and negative controls before any MachLib edit.",
            ],
            ["define chain statement precisely", "avoid broad subtraction-family claim", "preserve guard obligations"],
        ),
        decision_option(
            "fresh_identity_family_selector",
            "private_identity_lane",
            "candidate_later",
            58,
            "Future small identity-family selector",
            [
                "Fresh identities may open new doors, but the subtraction family currently has a clean proof-shaped trail.",
                "A fresh selector should wait until the current family either yields a nested-chain target or blocks.",
            ],
            ["choose identity family", "avoid scattering proof-lane focus"],
        ),
        decision_option(
            "checked_witness_copy_review_packet",
            "public_copy_review_lane",
            "candidate_later",
            53,
            "Future checked-witness copy review packet",
            [
                "Several checked witnesses now have private surfaces.",
                "Public education could be useful, but it needs explicit human wording review.",
                "Copy review is a posture move rather than the highest research move right now.",
            ],
            ["human wording review required", "public promotion must remain false until separately approved"],
        ),
        decision_option(
            "prime_signature_log_recovery_feasibility_selector",
            "speculative_identity_lane",
            "candidate_later",
            41,
            "Future prime-signature witness feasibility selector",
            [
                "The prime-signature target is interesting but still carries interpretation risk.",
                "It should wait until the current proof-hygiene lane is not mid-family.",
            ],
            ["requires clearer statement", "avoid RH/zeta implication leakage"],
        ),
    ]
    selected = next(option for option in options if option["selectionStatus"] == "selected_next")
    summary = {
        "sourceSurfaceReview": surface["artifactId"],
        "affineOffsetWitnessRecordedPrivately": surface["summary"]["checkedWitnessRecordedPrivately"],
        "broadSubtractionFamilyClaim": False,
        "copyReviewStarted": False,
        "publicPromotionPerformed": False,
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProved": False,
        "runtimeLoweringChanged": False,
        "runtimeLoweringControl": surface["summary"]["runtimeLoweringControl"],
        "selectedOptionId": selected["optionId"],
        "selectedNextArtifact": selected["nextArtifact"],
        "optionCount": len(options),
        "publicReady": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values())
        and all(all(value is False for value in option["claimFlags"].values()) for option in options),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "decisionType": "eml_next_proof_family_branch_decision_v0",
        "artifactId": "eml-d19-next-proof-family-branch-decision",
        "status": STATUS,
        "decision": "select_nested_subtraction_boundary_chain_selector",
        "date": DATE,
        "sourceSurfaceReview": surface["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "decisionOptions": options,
        "selectedOption": selected,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceSurfaceReview"] != "eml-d18-subtraction-boundary-affine-offset-surface-review":
        raise ValueError("D19 must consume D18")
    if summary["affineOffsetWitnessRecordedPrivately"] is not True:
        raise ValueError("D19 requires private affine-offset surface review")
    if summary["optionCount"] != 4:
        raise ValueError("expected four decision options")
    if summary["selectedOptionId"] != "nested_subtraction_boundary_chain_selector":
        raise ValueError("unexpected selected option")
    if summary["selectedNextArtifact"] != "EML-D20 nested subtraction-boundary chain selector":
        raise ValueError("unexpected next artifact")
    for key in [
        "broadSubtractionFamilyClaim",
        "copyReviewStarted",
        "publicPromotionPerformed",
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
        raise ValueError("runtime lowering control drift")
    if not all(value is False for value in payload["claimFlags"].values()):
        raise ValueError("claim flag drift")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_next_proof_family_branch_decision",
        "validationStatus": "pass",
        "semanticStrength": "private_branch_decision_no_copy_review_no_implementation",
        "source": f"python/results/eml_d19_next_proof_family_branch_decision/eml_d19_next_proof_family_branch_decision_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d19_next_proof_family_branch_decision_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedOptionId": payload["summary"]["selectedOptionId"],
        "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
        "nextAction": "Run EML-D20 as a selector only; do not start MachLib implementation until nested-chain statements and guards are precise.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D19 Next Proof-Family Branch Decision",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Selected option: `{payload['summary']['selectedOptionId']}`",
        "",
        "D19 chooses the next private branch after the affine-offset witness surface review.",
        "",
        "| Option | Status | Score | Next artifact |",
        "|---|---|---:|---|",
    ]
    for option in payload["decisionOptions"]:
        lines.append(
            f"| `{option['optionId']}` | `{option['selectionStatus']}` | {option['priorityScore']} | {option['nextArtifact']} |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- selected next artifact: `{payload['summary']['selectedNextArtifact']}`",
            f"- broad subtraction-family claim: `{payload['summary']['broadSubtractionFamilyClaim']}`",
            f"- copy review started: `{payload['summary']['copyReviewStarted']}`",
            f"- implementation started: `{payload['summary']['implementationStarted']}`",
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
    result_path = out_dir / f"eml_d19_next_proof_family_branch_decision_{STAMP}.json"
    report_path = report_dir / f"eml_d19_next_proof_family_branch_decision_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d19_next_proof_family_branch_decision.json"
    feed_path = command_feed_dir / f"eml_d19_next_proof_family_branch_decision_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d19_next_proof_family_branch_decision")
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
    print("EML_D19_NEXT_PROOF_FAMILY_BRANCH_DECISION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
