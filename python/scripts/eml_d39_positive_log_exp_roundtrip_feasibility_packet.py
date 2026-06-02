#!/usr/bin/env python3
"""EML-D39 positive log-exp roundtrip witness feasibility packet."""

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

from scripts import eml_d38_bounded_identity_branch_selector as d38  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_positive_log_exp_roundtrip_feasibility.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D39_POSITIVE_LOG_EXP_ROUNDTRIP_FEASIBILITY_PASS"

CLAIM_FLAGS = {
    "witness_feasibility_recorded": True,
    "bounded_identity_branch_selected": True,
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved": False,
    "proof_attempt_started": False,
    "runtime_lowering_changed": False,
    "log_exp_replacement_claim": False,
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
    "EML-D39 records feasibility only; it does not edit MachLib, typecheck Lean, or start a proof attempt.",
    "D39 does not claim log/exp replacement, runtime advantage, theorem discovery, or broad EML superiority.",
    "D39 keeps course drafting in the user/laptop-agent lane and touches no laptop-owned repos.",
]

FEASIBILITY_ITEMS = [
    {
        "itemId": "selected_branch_matches_d38",
        "status": "satisfied",
        "evidence": "D38 selected positive_log_exp_roundtrip_identity as selected_next.",
        "reviewNote": "The feasibility packet stays inside the selected bounded identity branch.",
    },
    {
        "itemId": "positive_domain_guard_explicit",
        "status": "satisfied",
        "evidence": "The proposed statement carries guard 0 < x.",
        "reviewNote": "The guard is required before using real log/exp roundtrip facts.",
    },
    {
        "itemId": "statement_shape_small",
        "status": "satisfied",
        "evidence": "The candidate statement is exp (log x) = x under one guard.",
        "reviewNote": "This is a small single-identity witness, not a family theorem.",
    },
    {
        "itemId": "runtime_boundary_preserved",
        "status": "satisfied",
        "evidence": "The packet keeps runtime lowering unchanged and makes no log/exp replacement claim.",
        "reviewNote": "Standard log/exp remain the semantic control for this feasibility review.",
    },
]

BLOCKERS = [
    {
        "blockerId": "guard_omitted",
        "severity": "hard_blocker",
        "description": "Any future witness attempt that omits 0 < x must be rejected.",
    },
    {
        "blockerId": "runtime_relabeling",
        "severity": "hard_blocker",
        "description": "The identity must not be relabeled as runtime lowering or log/exp replacement.",
    },
    {
        "blockerId": "broad_family_language",
        "severity": "hard_blocker",
        "description": "The packet must not broaden the single identity into a general EML theorem family.",
    },
]


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    selector = d38.build_payload(atlas_gate_path)
    d38.validate_payload(selector)
    selected = selector["selectedCandidate"]
    proposed_witness = {
        "candidateId": selected["candidateId"],
        "family": selected["family"],
        "proposedMachlibName": "MachLib.Real.positive_log_exp_roundtrip_witness",
        "statementKind": "guarded_real_identity",
        "emlShape": selected["emlShape"],
        "standardShape": selected["standardShape"],
        "proposedStatement": "0 < x -> exp (log x) = x",
        "guardShape": ["0 < x"],
        "guardPolicy": "positive_domain_guard_required",
        "semanticControl": "standard_real_log_exp_roundtrip_control",
        "nextArtifact": "EML-D40 positive log-exp roundtrip MachLib witness attempt or blocker",
    }
    summary = {
        "sourceBranchSelector": selector["artifactId"],
        "sourceSelectedCandidateId": selector["summary"]["selectedCandidateId"],
        "sourceSelectedFamily": selector["summary"]["selectedFamily"],
        "feasibilityRecorded": True,
        "feasibilityStatus": "feasible_for_scoped_witness_attempt",
        "proposedMachlibName": proposed_witness["proposedMachlibName"],
        "proposedStatement": proposed_witness["proposedStatement"],
        "guardCount": len(proposed_witness["guardShape"]),
        "positiveDomainGuardRequired": True,
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProved": False,
        "proofAttemptStarted": False,
        "runtimeLoweringChanged": False,
        "logExpReplacementClaim": False,
        "runtimeLoweringControl": selector["summary"]["runtimeLoweringControl"],
        "publicPromotionPerformed": False,
        "publicEducationPromotionPerformed": False,
        "publicSurfaceUpdated": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "nextArtifact": proposed_witness["nextArtifact"],
        "claimFlagsAllBounded": all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key not in {"witness_feasibility_recorded", "bounded_identity_branch_selected"}
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "eml_positive_log_exp_roundtrip_feasibility_v0",
        "artifactId": "eml-d39-positive-log-exp-roundtrip-feasibility-packet",
        "status": STATUS,
        "decision": "record_positive_log_exp_roundtrip_feasibility",
        "date": DATE,
        "sourceBranchSelector": selector["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "proposedWitness": proposed_witness,
        "feasibilityItems": list(FEASIBILITY_ITEMS),
        "blockers": list(BLOCKERS),
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    witness = payload["proposedWitness"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceBranchSelector"] != "eml-d38-bounded-identity-branch-selector":
        raise ValueError("D39 must consume D38")
    if summary["sourceSelectedCandidateId"] != "positive_log_exp_roundtrip_identity":
        raise ValueError("D39 must preserve the D38 selected candidate")
    if summary["sourceSelectedFamily"] != "positive_domain_log_exp_roundtrip":
        raise ValueError("D39 must preserve the D38 selected family")
    if witness["proposedStatement"] != "0 < x -> exp (log x) = x":
        raise ValueError("unexpected proposed statement")
    if witness["guardShape"] != ["0 < x"]:
        raise ValueError("positive-domain guard must remain explicit")
    if summary["guardCount"] != 1:
        raise ValueError("expected one guard")
    if summary["positiveDomainGuardRequired"] is not True:
        raise ValueError("positive-domain guard must be required")
    if summary["feasibilityRecorded"] is not True:
        raise ValueError("feasibility must be recorded")
    if summary["feasibilityStatus"] != "feasible_for_scoped_witness_attempt":
        raise ValueError("unexpected feasibility status")
    for key in [
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "candidateProved",
        "proofAttemptStarted",
        "runtimeLoweringChanged",
        "logExpReplacementClaim",
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
    if summary["nextArtifact"] != "EML-D40 positive log-exp roundtrip MachLib witness attempt or blocker":
        raise ValueError("unexpected next artifact")
    if summary["claimFlagsAllBounded"] is not True:
        raise ValueError("claim flags must remain bounded")
    for key in ["witness_feasibility_recorded", "bounded_identity_branch_selected"]:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in {"witness_feasibility_recorded", "bounded_identity_branch_selected"} and value is not False:
            raise ValueError(f"{key} must remain false")
    if len(payload["feasibilityItems"]) != 4:
        raise ValueError("expected four feasibility items")
    if any(item["status"] != "satisfied" for item in payload["feasibilityItems"]):
        raise ValueError("all feasibility items must be satisfied")
    if len(payload["blockers"]) != 3:
        raise ValueError("expected three blockers")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_positive_log_exp_roundtrip_feasibility_packet",
        "validationStatus": "pass",
        "semanticStrength": "private_feasibility_packet_no_machlib_edit_no_typecheck",
        "source": f"python/results/eml_d39_positive_log_exp_roundtrip_feasibility_packet/eml_d39_positive_log_exp_roundtrip_feasibility_packet_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d39_positive_log_exp_roundtrip_feasibility_packet_feed",
        "date": DATE,
        "status": payload["status"],
        "proposedMachlibName": payload["summary"]["proposedMachlibName"],
        "proposedStatement": payload["summary"]["proposedStatement"],
        "nextAction": "Run EML-D40 only as a scoped MachLib witness attempt or precise blocker.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D39 Positive Log-Exp Roundtrip Feasibility Packet",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Proposed witness: `{payload['summary']['proposedMachlibName']}`",
        "",
        f"Statement: `{payload['summary']['proposedStatement']}`",
        "",
        "D39 records feasibility for one guarded identity before any MachLib edit.",
        "",
        "## Feasibility Items",
        "",
        "| Item | Status | Review note |",
        "|---|---|---|",
    ]
    for item in payload["feasibilityItems"]:
        lines.append(f"| `{item['itemId']}` | `{item['status']}` | {item['reviewNote']} |")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- source candidate: `{payload['summary']['sourceSelectedCandidateId']}`",
            f"- guard required: `{payload['summary']['positiveDomainGuardRequired']}`",
            f"- implementation started: `{payload['summary']['implementationStarted']}`",
            f"- Lean typecheck performed: `{payload['summary']['leanTypecheckPerformed']}`",
            f"- candidate proved: `{payload['summary']['candidateProved']}`",
            f"- log/exp replacement claim: `{payload['summary']['logExpReplacementClaim']}`",
            f"- public ready: `{payload['summary']['publicReady']}`",
            "",
            "## Blockers",
            "",
        ]
    )
    lines.extend(f"- `{item['blockerId']}`: {item['description']}" for item in payload["blockers"])
    lines.extend(["", "## Non-Claims", ""])
    lines.extend(f"- {item}" for item in payload["nonClaims"])
    return "\n".join(lines) + "\n"


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path, atlas_gate_path: Path) -> dict[str, Any]:
    payload = build_payload(atlas_gate_path)
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"eml_d39_positive_log_exp_roundtrip_feasibility_packet_{STAMP}.json"
    report_path = report_dir / f"eml_d39_positive_log_exp_roundtrip_feasibility_packet_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d39_positive_log_exp_roundtrip_feasibility_packet.json"
    feed_path = command_feed_dir / f"eml_d39_positive_log_exp_roundtrip_feasibility_packet_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d39_positive_log_exp_roundtrip_feasibility_packet")
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
    print("EML_D39_POSITIVE_LOG_EXP_ROUNDTRIP_FEASIBILITY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
