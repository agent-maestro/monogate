#!/usr/bin/env python3
"""EML-D12 next identity witness selector."""

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
from scripts import eml_d11_checked_witness_surface_review as d11  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_next_identity_witness_selector.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D12_NEXT_IDENTITY_WITNESS_SELECTOR_PASS"

CLAIM_FLAGS = {
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
    "public_atlas_promotion": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "EML-D12 selects the next private identity witness target after the checked constants witness; it does not edit MachLib or typecheck Lean.",
    "D12 does not prove ln-from-EML, discover a theorem, prove broad EML advantage, prove full EML semantics, prove compiler correctness, claim runtime performance, claim formal equivalence, or promote public Atlas copy.",
    "The selected target remains proof/teaching shape only; standard log remains the runtime lowering control unless later evidence changes that boundary.",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def candidate_by_id(queue: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    return next(item for item in queue["frontierCandidates"] if item["candidateId"] == candidate_id)


def atlas_status(gate: dict[str, Any], entry_id: str) -> str:
    return next(item for item in gate["decisions"] if item["id"] == entry_id)["proofStatus"]


def selector_candidate(
    candidate_id: str,
    family: str,
    eml_form: str,
    standard_form: str,
    proof_target: str,
    selection_status: str,
    score: int,
    difficulty: str,
    atlas_proof_status: str,
    rationale: list[str],
    next_artifact: str,
    blockers: list[str],
) -> dict[str, Any]:
    return {
        "candidateId": candidate_id,
        "family": family,
        "emlForm": eml_form,
        "standardForm": standard_form,
        "proofTarget": proof_target,
        "selectionStatus": selection_status,
        "priorityScore": score,
        "estimatedDifficulty": difficulty,
        "atlasProofStatus": atlas_proof_status,
        "rationale": rationale,
        "nextArtifact": next_artifact,
        "blockers": blockers,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    surface = d11.build_payload(atlas_gate_path)
    d11.validate_payload(surface)
    queue = d1.build_payload()
    gate = load_json(atlas_gate_path)
    ln_candidate = candidate_by_id(queue, "ln_from_eml_boundary_v1")
    subtraction_candidate = candidate_by_id(queue, "subtraction_boundary_family_v1")
    prime_candidate = candidate_by_id(queue, "prime_signature_log_recovery_v2")
    candidates = [
        selector_candidate(
            ln_candidate["candidateId"],
            ln_candidate["family"],
            ln_candidate["emlForm"],
            ln_candidate["standardForm"],
            "MachLib.Real.ln_from_eml_boundary_witness",
            "selected_next",
            70,
            "medium_nested_rewrite",
            atlas_status(gate, "ln_from_eml"),
            [
                "It remains a current Atlas proof target after constants are checked.",
                "R10C already records scoped semantic-proof evidence for ln_from_eml_v0.",
                "The target is more valuable than a duplicate subtraction base proof and less speculative than prime-signature recovery.",
            ],
            "EML-D13 ln-from-EML MachLib witness attempt",
            ["nested EML rewrite proof surface", "positive-domain guard wording"],
        ),
        selector_candidate(
            subtraction_candidate["candidateId"],
            subtraction_candidate["family"],
            subtraction_candidate["emlForm"],
            subtraction_candidate["standardForm"],
            "MachLib.Real.subtraction_boundary_family_generalization_witness",
            "candidate_later",
            58,
            "family_generalization_after_base_checked",
            atlas_status(gate, "subtraction_boundary"),
            [
                "The selected base subtraction-boundary witness is already checked.",
                "A family generalization could be useful later but is less urgent than closing a still-candidate Atlas proof target.",
                "D9 already prevented duplicate work on the base case.",
            ],
            "Future subtraction-boundary family generalization selector",
            ["avoid duplicate base witness", "define what family generalization means"],
        ),
        selector_candidate(
            prime_candidate["candidateId"],
            prime_candidate["family"],
            prime_candidate["emlForm"],
            prime_candidate["standardForm"],
            "MachLib.Real.prime_signature_log_recovery_witness",
            "candidate_later",
            46,
            "speculative_identity_review",
            atlas_status(gate, "prime_signature_log_recovery"),
            [
                "The prime-signature row is interesting but remains more speculative and less foundational than ln-from-EML.",
                "It should wait until the small generator identities are better covered.",
                "Selecting it now would risk mixing proof-shaped cleanup with research-frontier interpretation.",
            ],
            "Future prime-signature witness feasibility selector",
            ["requires clearer statement", "avoid RH/zeta implication leakage"],
        ),
    ]
    selected = next(item for item in candidates if item["selectionStatus"] == "selected_next")
    summary = {
        "sourceSurfaceReview": surface["artifactId"],
        "candidateCount": len(candidates),
        "selectedCandidateId": selected["candidateId"],
        "selectedProofTarget": selected["proofTarget"],
        "selectedNextArtifact": selected["nextArtifact"],
        "constantsWitnessAlreadyChecked": surface["summary"]["checkedWitnessRecordedInAtlasGate"],
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProved": False,
        "publicReady": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values())
        and all(all(value is False for value in item["claimFlags"].values()) for item in candidates),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "selectorType": "eml_next_identity_witness_selector_v0",
        "artifactId": "eml-d12-next-identity-witness-selector",
        "status": STATUS,
        "decision": "select_ln_from_eml_as_next_identity_witness_target",
        "date": DATE,
        "sourceSurfaceReview": surface["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "candidateSelectors": candidates,
        "selectedCandidate": selected,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceSurfaceReview"] != "eml-d11-checked-witness-surface-review":
        raise ValueError("D12 must consume D11")
    if summary["constantsWitnessAlreadyChecked"] is not True:
        raise ValueError("D12 requires checked constants witness surface")
    if summary["candidateCount"] != 3:
        raise ValueError("expected three next-witness candidates")
    if summary["selectedCandidateId"] != "ln_from_eml_boundary_v1":
        raise ValueError("unexpected selected candidate")
    if summary["selectedProofTarget"] != "MachLib.Real.ln_from_eml_boundary_witness":
        raise ValueError("unexpected selected proof target")
    for key in ["implementationStarted", "machlibFileChanged", "leanTypecheckPerformed", "candidateProved", "publicReady"]:
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
        "artifactType": "eml_next_identity_witness_selector",
        "validationStatus": "pass",
        "semanticStrength": "private_selector_no_machlib_edit_no_typecheck",
        "source": f"python/results/eml_d12_next_identity_witness_selector/eml_d12_next_identity_witness_selector_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d12_next_identity_witness_selector_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedCandidateId": payload["summary"]["selectedCandidateId"],
        "selectedProofTarget": payload["summary"]["selectedProofTarget"],
        "nextAction": "Attempt EML-D13 ln-from-EML MachLib witness in a separate implementation phase.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D12 Next Identity Witness Selector",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Selected candidate: `{payload['summary']['selectedCandidateId']}`",
        "",
        "D12 selects the next proof-shaped identity target after the checked constants witness.",
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
            f"- constants witness already checked: `{payload['summary']['constantsWitnessAlreadyChecked']}`",
            f"- implementation started: `{payload['summary']['implementationStarted']}`",
            f"- Lean typecheck performed: `{payload['summary']['leanTypecheckPerformed']}`",
            f"- candidate proved: `{payload['summary']['candidateProved']}`",
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
    result_path = out_dir / f"eml_d12_next_identity_witness_selector_{STAMP}.json"
    report_path = report_dir / f"eml_d12_next_identity_witness_selector_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d12_next_identity_witness_selector.json"
    feed_path = command_feed_dir / f"eml_d12_next_identity_witness_selector_feed_{STAMP}.json"
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
    parser.add_argument("--atlas-gate-path", type=Path, default=ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d12_next_identity_witness_selector")
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
    print("EML_D12_NEXT_IDENTITY_WITNESS_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
