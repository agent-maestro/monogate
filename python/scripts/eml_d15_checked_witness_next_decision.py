#!/usr/bin/env python3
"""EML-D15 checked-witness next decision."""

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

from scripts import eml_d1_discovery_frontier_queue as d1  # noqa: E402
from scripts import eml_d14_ln_from_eml_surface_review as d14  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_checked_witness_next_decision.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D15_CHECKED_WITNESS_NEXT_DECISION_PASS"

CLAIM_FLAGS = {
    "copy_review_started": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved": False,
    "theorem_discovery_claim": False,
    "general_eml_superiority_claim": False,
    "eml_advantage_proved": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "full_eml_semantics_claim": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "EML-D15 chooses the next private research branch after D14; it does not start copy review, edit MachLib, or typecheck Lean.",
    "D15 does not promote public Atlas wording, claim theorem discovery, prove broad EML advantage, prove full EML semantics, prove compiler correctness, claim runtime performance, or claim formal equivalence.",
    "The selected next branch is a private selector target only; a later phase must define the subtraction-boundary family statement before any proof attempt.",
]


def candidate_by_id(queue: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    return next(item for item in queue["frontierCandidates"] if item["candidateId"] == candidate_id)


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
    surface = d14.build_payload(atlas_gate_path)
    d14.validate_payload(surface)
    queue = d1.build_payload()
    subtraction = candidate_by_id(queue, "subtraction_boundary_family_v1")
    options = [
        decision_option(
            "return_to_identity_selector_subtraction_boundary_family_v1",
            "private_identity_witness_lane",
            "selected_next",
            74,
            "EML-D16 subtraction-boundary family witness selector",
            [
                "D11 and D14 have already created private surface reviews for the two newly checked identity witnesses.",
                "The next research gain is another proof-shaped target, not public copy expansion.",
                f"The candidate remains in the D1 identity lane: {subtraction['candidateId']}.",
            ],
            ["define family statement precisely", "avoid duplicating the already checked base witness"],
        ),
        decision_option(
            "checked_witness_copy_review_packet",
            "public_copy_review_lane",
            "candidate_later",
            61,
            "Future checked-witness copy review packet",
            [
                "Constants and ln-from-EML now have private checked-witness surfaces.",
                "Public education could be useful, but it should wait for explicit human copy approval.",
                "Copy review is a surface/posture move, not the highest research move right now.",
            ],
            ["human wording review required", "public promotion must remain false until separately approved"],
        ),
        decision_option(
            "prime_signature_log_recovery_feasibility_selector",
            "speculative_identity_lane",
            "candidate_later",
            45,
            "Future prime-signature witness feasibility selector",
            [
                "The prime-signature target is interesting but still carries higher interpretation risk.",
                "It should wait until the small identity/proof-shaped lane has cleaner coverage.",
                "Selecting it now could leak zeta/RH implication pressure into a proof hygiene sprint.",
            ],
            ["requires clearer statement", "avoid RH/zeta implication leakage"],
        ),
    ]
    selected = next(option for option in options if option["selectionStatus"] == "selected_next")
    summary = {
        "sourceSurfaceReview": surface["artifactId"],
        "checkedLnFromEmlSurfaceRecorded": surface["summary"]["checkedWitnessRecordedInAtlasGate"],
        "copyReviewStarted": False,
        "publicPromotionPerformed": False,
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProved": False,
        "selectedOptionId": selected["optionId"],
        "selectedNextArtifact": selected["nextArtifact"],
        "selectedCandidateId": "subtraction_boundary_family_v1",
        "selectedProofTarget": "MachLib.Real.subtraction_boundary_family_generalization_witness",
        "optionCount": len(options),
        "publicReady": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values())
        and all(all(value is False for value in option["claimFlags"].values()) for option in options),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "decisionType": "eml_checked_witness_next_decision_v0",
        "artifactId": "eml-d15-checked-witness-next-decision",
        "status": STATUS,
        "decision": "return_to_identity_selector_for_subtraction_boundary_family",
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
    if payload["sourceSurfaceReview"] != "eml-d14-ln-from-eml-surface-review":
        raise ValueError("D15 must consume D14")
    if summary["checkedLnFromEmlSurfaceRecorded"] is not True:
        raise ValueError("D15 requires checked ln-from-EML surface review")
    if summary["optionCount"] != 3:
        raise ValueError("expected three decision options")
    if summary["selectedOptionId"] != "return_to_identity_selector_subtraction_boundary_family_v1":
        raise ValueError("unexpected selected option")
    if summary["selectedCandidateId"] != "subtraction_boundary_family_v1":
        raise ValueError("unexpected selected candidate")
    if summary["selectedNextArtifact"] != "EML-D16 subtraction-boundary family witness selector":
        raise ValueError("unexpected next artifact")
    for key in [
        "copyReviewStarted",
        "publicPromotionPerformed",
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "candidateProved",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if not all(value is False for value in payload["claimFlags"].values()):
        raise ValueError("claim flag drift")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_checked_witness_next_decision",
        "validationStatus": "pass",
        "semanticStrength": "private_branch_decision_no_copy_review_no_implementation",
        "source": f"python/results/eml_d15_checked_witness_next_decision/eml_d15_checked_witness_next_decision_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d15_checked_witness_next_decision_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedOptionId": payload["summary"]["selectedOptionId"],
        "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
        "nextAction": "Run EML-D16 as a selector only; do not start MachLib implementation until the family statement is precise.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D15 Checked Witness Next Decision",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Selected option: `{payload['summary']['selectedOptionId']}`",
        "",
        "D15 chooses the next private research branch after the checked-witness surface reviews.",
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
            f"- selected candidate: `{payload['summary']['selectedCandidateId']}`",
            f"- copy review started: `{payload['summary']['copyReviewStarted']}`",
            f"- implementation started: `{payload['summary']['implementationStarted']}`",
            f"- Lean typecheck performed: `{payload['summary']['leanTypecheckPerformed']}`",
            f"- public promotion performed: `{payload['summary']['publicPromotionPerformed']}`",
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
    result_path = out_dir / f"eml_d15_checked_witness_next_decision_{STAMP}.json"
    report_path = report_dir / f"eml_d15_checked_witness_next_decision_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d15_checked_witness_next_decision.json"
    feed_path = command_feed_dir / f"eml_d15_checked_witness_next_decision_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d15_checked_witness_next_decision")
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
    print("EML_D15_CHECKED_WITNESS_NEXT_DECISION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
