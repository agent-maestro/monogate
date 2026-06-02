#!/usr/bin/env python3
"""EML-D38 bounded EML identity branch selector."""

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

from scripts import eml_d37_research_lane_reset_selector as d37  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_bounded_identity_branch_selector.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D38_BOUNDED_IDENTITY_BRANCH_SELECTOR_PASS"

CLAIM_FLAGS = {
    "bounded_identity_branch_selected": True,
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved": False,
    "proof_attempt_started": False,
    "runtime_lowering_changed": False,
    "broad_nested_subtraction_claim": False,
    "broad_subtraction_family_claim": False,
    "arbitrary_depth_claim": False,
    "theorem_discovery_claim": False,
    "general_eml_superiority_claim": False,
    "eml_advantage_proved": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "full_eml_semantics_claim": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "public_surface_updated": False,
    "electronics_repo_touched": False,
    "laptop_artifact_consumed": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "EML-D38 selects one bounded identity branch only; it does not edit MachLib, typecheck Lean, or start a proof attempt.",
    "D38 does not reopen broad subtraction-family work, claim theorem discovery, prove EML advantage, or change runtime lowering.",
    "D38 keeps course drafting in the user/laptop-agent lane and touches no laptop-owned repos.",
]


def branch_candidate(
    candidate_id: str,
    family: str,
    eml_shape: str,
    standard_shape: str,
    guard_shape: list[str],
    status: str,
    priority_score: int,
    estimated_difficulty: str,
    next_artifact: str,
    rationale: list[str],
    blockers: list[str],
) -> dict[str, Any]:
    return {
        "candidateId": candidate_id,
        "family": family,
        "emlShape": eml_shape,
        "standardShape": standard_shape,
        "guardShape": guard_shape,
        "selectionStatus": status,
        "priorityScore": priority_score,
        "estimatedDifficulty": estimated_difficulty,
        "nextArtifact": next_artifact,
        "rationale": rationale,
        "blockers": blockers,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    reset = d37.build_payload(atlas_gate_path)
    d37.validate_payload(reset)
    candidates = [
        branch_candidate(
            "positive_log_exp_roundtrip_identity",
            "positive_domain_log_exp_roundtrip",
            "exp (log x)",
            "x",
            ["0 < x"],
            "selected_next",
            82,
            "small_positive_domain_rewrite",
            "EML-D39 positive log-exp roundtrip witness feasibility packet",
            [
                "It is bounded to one positive-domain identity and does not extend the subtraction-family ladder.",
                "It directly supports the log/exp guard discipline used by existing checked EML witnesses.",
                "It can be reviewed as feasibility before any MachLib edit or Lean typecheck.",
            ],
            [
                "must keep 0 < x guard explicit",
                "must not claim log/exp replacement or runtime advantage",
                "must remain feasibility before implementation",
            ],
        ),
        branch_candidate(
            "eml_constant_coordinate_refresh",
            "constant_coordinate_refresh",
            "eml 0 y and eml x 1 boundary variants",
            "small constant-coordinate identities",
            ["standard real-domain constants"],
            "candidate_later",
            61,
            "small_but_lower_research_value",
            "Future constant-coordinate refresh selector",
            [
                "Small constants are useful but already have a checked constants witness.",
                "A refresh risks duplicating D10/D11 unless a new statement is made precise.",
            ],
            [
                "avoid duplicate checked constants witness",
                "define new statement before implementation",
            ],
        ),
        branch_candidate(
            "bounded_trig_eml_probe_selector",
            "bounded_trig_identity_probe",
            "guarded sin/cos candidate expression",
            "single bounded trig identity candidate",
            ["bounded interval guard required"],
            "candidate_later",
            43,
            "speculative_frontier_probe",
            "Future bounded trig identity feasibility selector",
            [
                "A trigonometric probe may broaden EML research later.",
                "It is more speculative than a positive-domain log/exp roundtrip and risks weaker guard discipline.",
            ],
            [
                "requires exact statement",
                "requires stronger negative controls",
                "avoid broad EML advantage language",
            ],
        ),
    ]
    selected = next(candidate for candidate in candidates if candidate["selectionStatus"] == "selected_next")
    summary = {
        "sourceResetSelector": reset["artifactId"],
        "researchLaneResetSelected": reset["summary"]["researchLaneResetSelected"],
        "courseDraftingParkedResearchSide": reset["summary"]["courseDraftingParkedResearchSide"],
        "sourceSelectedOptionId": reset["summary"]["selectedOptionId"],
        "candidateCount": len(candidates),
        "selectedCandidateId": selected["candidateId"],
        "selectedFamily": selected["family"],
        "selectedNextArtifact": selected["nextArtifact"],
        "boundedIdentityBranchSelected": True,
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProved": False,
        "proofAttemptStarted": False,
        "runtimeLoweringChanged": False,
        "runtimeLoweringControl": reset["summary"]["runtimeLoweringControl"],
        "broadNestedSubtractionClaim": False,
        "broadSubtractionFamilyClaim": False,
        "arbitraryDepthClaim": False,
        "publicPromotionPerformed": False,
        "publicEducationPromotionPerformed": False,
        "publicSurfaceUpdated": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "claimFlagsAllBounded": CLAIM_FLAGS["bounded_identity_branch_selected"] is True
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key != "bounded_identity_branch_selected"
        )
        and all(
            candidate["claimFlags"]["bounded_identity_branch_selected"] is True
            and all(
                value is False
                for key, value in candidate["claimFlags"].items()
                if key != "bounded_identity_branch_selected"
            )
            for candidate in candidates
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "selectorType": "eml_bounded_identity_branch_selector_v0",
        "artifactId": "eml-d38-bounded-identity-branch-selector",
        "status": STATUS,
        "decision": "select_positive_log_exp_roundtrip_identity",
        "date": DATE,
        "sourceResetSelector": reset["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "branchCandidates": candidates,
        "selectedCandidate": selected,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceResetSelector"] != "eml-d37-research-lane-reset-selector":
        raise ValueError("D38 must consume D37")
    if summary["researchLaneResetSelected"] is not True:
        raise ValueError("D37 research reset must be preserved")
    if summary["courseDraftingParkedResearchSide"] is not True:
        raise ValueError("course drafting must remain parked")
    if summary["sourceSelectedOptionId"] != "bounded_eml_identity_branch_selector":
        raise ValueError("D38 requires D37 bounded identity selection")
    if summary["candidateCount"] != 3:
        raise ValueError("expected three bounded identity candidates")
    if summary["selectedCandidateId"] != "positive_log_exp_roundtrip_identity":
        raise ValueError("unexpected selected identity candidate")
    if summary["selectedNextArtifact"] != "EML-D39 positive log-exp roundtrip witness feasibility packet":
        raise ValueError("unexpected next artifact")
    if summary["boundedIdentityBranchSelected"] is not True:
        raise ValueError("bounded identity branch must be selected")
    for key in [
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "candidateProved",
        "proofAttemptStarted",
        "runtimeLoweringChanged",
        "broadNestedSubtractionClaim",
        "broadSubtractionFamilyClaim",
        "arbitraryDepthClaim",
        "publicPromotionPerformed",
        "publicEducationPromotionPerformed",
        "publicSurfaceUpdated",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["runtimeLoweringControl"] != "standard_subtraction_remains_runtime_control":
        raise ValueError("runtime lowering control drift")
    if summary["claimFlagsAllBounded"] is not True:
        raise ValueError("claim flags must remain bounded")
    if payload["claimFlags"]["bounded_identity_branch_selected"] is not True:
        raise ValueError("bounded identity branch flag must be true")
    for key, value in payload["claimFlags"].items():
        if key != "bounded_identity_branch_selected" and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_bounded_identity_branch_selector",
        "validationStatus": "pass",
        "semanticStrength": "private_selector_no_machlib_edit_no_typecheck",
        "source": f"python/results/eml_d38_bounded_identity_branch_selector/eml_d38_bounded_identity_branch_selector_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d38_bounded_identity_branch_selector_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedCandidateId": payload["summary"]["selectedCandidateId"],
        "selectedNextArtifact": payload["summary"]["selectedNextArtifact"],
        "nextAction": "Run EML-D39 as a positive log-exp roundtrip witness feasibility packet; do not edit MachLib yet.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D38 Bounded Identity Branch Selector",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Selected candidate: `{payload['summary']['selectedCandidateId']}`",
        "",
        "D38 selects one bounded EML identity family after the research lane reset.",
        "",
        "| Candidate | Status | Score | Next artifact |",
        "|---|---|---:|---|",
    ]
    for candidate in payload["branchCandidates"]:
        lines.append(
            f"| `{candidate['candidateId']}` | `{candidate['selectionStatus']}` | {candidate['priorityScore']} | {candidate['nextArtifact']} |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- selected family: `{payload['summary']['selectedFamily']}`",
            f"- implementation started: `{payload['summary']['implementationStarted']}`",
            f"- Lean typecheck performed: `{payload['summary']['leanTypecheckPerformed']}`",
            f"- candidate proved: `{payload['summary']['candidateProved']}`",
            f"- public ready: `{payload['summary']['publicReady']}`",
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
    result_path = out_dir / f"eml_d38_bounded_identity_branch_selector_{STAMP}.json"
    report_path = report_dir / f"eml_d38_bounded_identity_branch_selector_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d38_bounded_identity_branch_selector.json"
    feed_path = command_feed_dir / f"eml_d38_bounded_identity_branch_selector_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d38_bounded_identity_branch_selector")
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
    print("EML_D38_BOUNDED_IDENTITY_BRANCH_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
