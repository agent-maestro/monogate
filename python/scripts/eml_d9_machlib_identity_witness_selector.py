#!/usr/bin/env python3
"""EML-D9 MachLib identity witness selector."""

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
from scripts import eml_d8_discovery_branch_decision as d8  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_machlib_identity_witness_selector.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D9_MACHLIB_IDENTITY_WITNESS_SELECTOR_PASS"

CLAIM_FLAGS = {
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved": False,
    "theorem_discovery_claim": False,
    "eml_advantage_proved": False,
    "general_eml_superiority_claim": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "public_atlas_promotion": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "EML-D9 selects the next private MachLib identity witness target; it does not edit MachLib or typecheck Lean.",
    "EML-D9 does not prove a candidate, discover a theorem, prove EML advantage, prove compiler correctness, claim runtime performance, claim formal equivalence, or promote a public Atlas entry.",
    "Already checked subtraction-boundary evidence remains prior selected-file evidence only and is not upgraded into a broad proof claim.",
]


def candidate_by_id(queue: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    return next(item for item in queue["frontierCandidates"] if item["candidateId"] == candidate_id)


def selector_candidate(
    candidate: dict[str, Any],
    selector_id: str,
    proof_target: str,
    selection_status: str,
    score: int,
    difficulty: str,
    rationale: list[str],
    existing_witness: str | None,
    proposed_dependencies: list[str],
    next_artifact: str,
) -> dict[str, Any]:
    return {
        "selectorId": selector_id,
        "candidateId": candidate["candidateId"],
        "family": candidate["family"],
        "emlForm": candidate["emlForm"],
        "standardForm": candidate["standardForm"],
        "proofTarget": proof_target,
        "selectionStatus": selection_status,
        "priorityScore": score,
        "estimatedDifficulty": difficulty,
        "rationale": rationale,
        "existingWitness": existing_witness,
        "proposedDependencies": proposed_dependencies,
        "nextArtifact": next_artifact,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_candidate_selectors(queue: dict[str, Any]) -> list[dict[str, Any]]:
    constants = candidate_by_id(queue, "constants_zero_one_e_boundary_v0")
    subtraction = candidate_by_id(queue, "subtraction_boundary_family_v1")
    ln_from_eml = candidate_by_id(queue, "ln_from_eml_boundary_v1")
    return [
        selector_candidate(
            constants,
            "constants_zero_one_e_boundary_selector_v0",
            "MachLib.Real.constants_zero_one_e_boundary_witness",
            "selected_next",
            72,
            "small_definition_level",
            [
                "D2 already supports the constant-boundary identities on an exact deterministic grid.",
                "The target is new, small, and useful for teaching the EML coordinate system.",
                "It should require only definition-level EML unfolding plus local exp/log constant facts.",
            ],
            None,
            ["MachLib.Real.eml", "Real.exp_zero", "Real.log_one"],
            "EML-D10 constants zero/one/e MachLib witness attempt",
        ),
        selector_candidate(
            subtraction,
            "subtraction_boundary_family_selector_v1",
            "MachLib.Real.atlas_subtraction_boundary_witness",
            "already_checked_not_next",
            58,
            "already_checked_base_case",
            [
                "The base subtraction-boundary witness is already checked in the selected MachLib/Atlas lane.",
                "D9 should avoid spending the next implementation phase on an already closed base case.",
                "Future work can generalize the family after a fresh small identity target is attempted.",
            ],
            "MachLib.Real.atlas_subtraction_boundary_witness",
            ["MachLib.Real.eml_log_exp_subtraction_boundary"],
            "Future subtraction-boundary family generalization selector",
        ),
        selector_candidate(
            ln_from_eml,
            "ln_from_eml_boundary_selector_v1",
            "MachLib.Real.ln_from_eml_boundary_witness",
            "candidate_later",
            54,
            "medium_nested_rewrite",
            [
                "The identity is exact under a positive-domain guard, but the nested EML expression is a more fragile first Lean target.",
                "R10/R11 already say standard log remains the runtime form, so this is proof/teaching shape only.",
                "It remains a good follow-up after the constants witness clarifies the local constant/log proof surface.",
            ],
            None,
            ["MachLib.Real.eml", "Real.log_exp", "positive log-domain guard"],
            "Future ln-from-EML MachLib witness attempt",
        ),
    ]


def build_payload() -> dict[str, Any]:
    branch = d8.build_payload()
    d8.validate_payload(branch)
    queue = d1.build_payload()
    selectors = build_candidate_selectors(queue)
    selected = next(item for item in selectors if item["selectionStatus"] == "selected_next")
    already_checked = [item for item in selectors if item["selectionStatus"] == "already_checked_not_next"]
    summary = {
        "sourceSelectedBranchId": branch["summary"]["selectedBranchId"],
        "candidateCount": len(selectors),
        "selectedCandidateId": selected["candidateId"],
        "selectedProofTarget": selected["proofTarget"],
        "selectedNextArtifact": selected["nextArtifact"],
        "alreadyCheckedCandidateCount": len(already_checked),
        "newWitnessCandidateCount": sum(1 for item in selectors if item["existingWitness"] is None),
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProved": False,
        "publicReady": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values())
        and all(all(value is False for value in item["claimFlags"].values()) for item in selectors),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "selectorType": "eml_machlib_identity_witness_selector_v0",
        "artifactId": "eml-d9-machlib-identity-witness-selector",
        "status": STATUS,
        "decision": "select_constants_zero_one_e_boundary_as_next_machlib_identity_witness_target",
        "date": DATE,
        "sourceBranchDecision": branch["artifactId"],
        "candidateSelectors": selectors,
        "selectedCandidate": selected,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceBranchDecision"] != "eml-d8-discovery-branch-decision":
        raise ValueError("D9 must consume D8")
    if summary["sourceSelectedBranchId"] != "machlib_identity_witness_lane_v0":
        raise ValueError("D9 expected D8 MachLib identity branch")
    if summary["candidateCount"] != 3:
        raise ValueError("expected three identity witness candidates")
    if summary["selectedCandidateId"] != "constants_zero_one_e_boundary_v0":
        raise ValueError("unexpected selected candidate")
    if summary["selectedProofTarget"] != "MachLib.Real.constants_zero_one_e_boundary_witness":
        raise ValueError("unexpected proof target")
    if summary["alreadyCheckedCandidateCount"] != 1:
        raise ValueError("expected one already checked candidate")
    if summary["newWitnessCandidateCount"] != 2:
        raise ValueError("expected two new witness candidates")
    for key in [
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
        "artifactType": "eml_machlib_identity_witness_selector",
        "validationStatus": "pass",
        "semanticStrength": "private_selector_no_machlib_edit_no_typecheck",
        "source": f"python/results/eml_d9_machlib_identity_witness_selector/eml_d9_machlib_identity_witness_selector_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d9_machlib_identity_witness_selector_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedCandidateId": payload["summary"]["selectedCandidateId"],
        "selectedProofTarget": payload["summary"]["selectedProofTarget"],
        "nextAction": "Attempt EML-D10 constants zero/one/e MachLib witness in a separate implementation phase.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D9 MachLib Identity Witness Selector",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Selected candidate: `{payload['summary']['selectedCandidateId']}`",
        "",
        "D9 chooses the next small proof-shaped identity target after D8 selected the MachLib witness lane.",
        "",
        "| Candidate | Status | Score | Proof target |",
        "|---|---|---|---|",
    ]
    for item in payload["candidateSelectors"]:
        lines.append(
            f"| `{item['candidateId']}` | `{item['selectionStatus']}` | {item['priorityScore']} | `{item['proofTarget']}` |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- implementation started: `{payload['summary']['implementationStarted']}`",
            f"- MachLib file changed: `{payload['summary']['machlibFileChanged']}`",
            f"- Lean typecheck performed: `{payload['summary']['leanTypecheckPerformed']}`",
            f"- candidate proved: `{payload['summary']['candidateProved']}`",
            "",
            "## Non-Claims",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["nonClaims"])
    return "\n".join(lines) + "\n"


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"eml_d9_machlib_identity_witness_selector_{STAMP}.json"
    report_path = report_dir / f"eml_d9_machlib_identity_witness_selector_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d9_machlib_identity_witness_selector.json"
    feed_path = command_feed_dir / f"eml_d9_machlib_identity_witness_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d9_machlib_identity_witness_selector")
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
    print("EML_D9_MACHLIB_IDENTITY_WITNESS_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
