#!/usr/bin/env python3
"""EML-D43 positive log-exp checked-witness delta copy review packet."""

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

from scripts import eml_d42_positive_log_exp_next_action_selector as d42  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_positive_log_exp_delta_copy_review_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D43_POSITIVE_LOG_EXP_DELTA_COPY_REVIEW_PACKET_PASS"

CLAIM_FLAGS = {
    "copy_review_started": True,
    "private_copy_review_only": True,
    "delta_copy_review_only": True,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "public_surface_updated": False,
    "advantage_lab_case_added": False,
    "runtime_lowering_changed": False,
    "log_exp_replacement_claim": False,
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved": False,
    "proof_attempt_started": False,
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
    "electronics_repo_touched": False,
    "laptop_artifact_consumed": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "EML-D43 is a private delta copy review packet for the checked positive log-exp witness only; it does not approve or publish public copy.",
    "D43 reviews wording for one scoped guarded MachLib witness; it does not claim theorem discovery, log/exp replacement, runtime advantage, broad EML superiority, full semantics, compiler correctness, or formal equivalence.",
    "D43 does not edit MachLib, typecheck Lean, update public surfaces, advance course drafting, consume laptop artifacts, or touch laptop-owned repos.",
]


def witness_copy_row(
    witness_id: str,
    machlib_name: str,
    safe_private_phrase: str,
    required_caveats: list[str],
    blocked_phrases: list[str],
    runtime_control: str,
) -> dict[str, Any]:
    return {
        "witnessId": witness_id,
        "machlibName": machlib_name,
        "safePrivatePhrase": safe_private_phrase,
        "requiredCaveats": required_caveats,
        "blockedPhrases": blocked_phrases,
        "runtimeControl": runtime_control,
        "copyStatus": "private_delta_copy_reviewable",
        "publicPromotionAllowed": False,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    selector = d42.build_payload(atlas_gate_path)
    d42.validate_payload(selector)
    row = witness_copy_row(
        "positive_log_exp_roundtrip",
        "MachLib.Real.positive_log_exp_roundtrip_witness",
        "A checked MachLib witness records the positive-domain roundtrip identity exp (log x) = x under the explicit guard 0 < x.",
        [
            "Always name the 0 < x guard.",
            "Say positive-domain or positive real input.",
            "Describe this as one scoped checked witness, not theorem discovery.",
            "Keep standard log/exp as the semantic and runtime controls.",
            "Keep public copy held for human review.",
        ],
        [
            "EML replaces log",
            "EML replaces exp",
            "log/exp replacement",
            "runtime advantage",
            "all logarithms",
            "unguarded log theorem",
            "public ready",
            "theorem discovery",
        ],
        "standard log/exp remain runtime controls",
    )
    required_caveats = [
        "This delta copy review is private-only.",
        "The checked statement requires 0 < x.",
        "The witness is one scoped MachLib theorem name, not a broad log/exp theory.",
        "Standard log/exp remain the semantic and runtime controls.",
        "Public Atlas and public education promotion remain false.",
    ]
    blocked_global_phrases = [
        "theorem discovery",
        "log/exp replacement",
        "runtime advantage",
        "public ready",
        "broad EML advantage",
        "compiler correctness",
        "formal equivalence",
        "full EML semantics",
    ]
    summary = {
        "sourceSelector": selector["artifactId"],
        "selectedOptionId": selector["summary"]["selectedOptionId"],
        "selectedWitnessName": selector["summary"]["selectedWitnessName"],
        "sourceSelectedCandidateId": selector["summary"]["sourceSelectedCandidateId"],
        "sourceSelectedFamily": selector["summary"]["sourceSelectedFamily"],
        "copyReviewStarted": True,
        "privateCopyReviewOnly": True,
        "deltaCopyReviewOnly": True,
        "witnessRowCount": 1,
        "requiredCaveatCount": len(required_caveats),
        "blockedGlobalPhraseCount": len(blocked_global_phrases),
        "positiveDomainGuardRequired": selector["summary"]["positiveDomainGuardRequired"],
        "guardCount": selector["summary"]["guardCount"],
        "publicHoldPreserved": selector["summary"]["publicHoldPreserved"],
        "runtimeBoundaryPreserved": selector["summary"]["runtimeBoundaryPreserved"],
        "publicPromotionPerformed": False,
        "publicEducationPromotionPerformed": False,
        "publicSurfaceUpdated": False,
        "advantageLabCaseAdded": False,
        "runtimeLoweringChanged": False,
        "logExpReplacementClaim": False,
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProvedThisPhase": False,
        "proofAttemptStarted": False,
        "runtimeLoweringControl": selector["summary"]["runtimeLoweringControl"],
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "parkedConstantCoordinateRefresh": True,
        "parkedBoundedTrigFeasibility": True,
        "parkedPositiveLogExpBranchPause": True,
        "publicReady": False,
        "nextAction": "EML-D44 choose positive log-exp branch pause, next bounded identity branch, or human-approved public copy gate.",
        "claimFlagsPublicFalse": all(
            CLAIM_FLAGS[key] is False
            for key in [
                "public_atlas_promotion",
                "public_education_promotion",
                "public_surface_updated",
                "public_ready",
            ]
        ),
        "claimFlagsAllBounded": all(
            CLAIM_FLAGS[key] is True
            for key in ["copy_review_started", "private_copy_review_only", "delta_copy_review_only"]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key not in {"copy_review_started", "private_copy_review_only", "delta_copy_review_only"}
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "reviewType": "eml_positive_log_exp_delta_copy_review_packet_v0",
        "artifactId": "eml-d43-positive-log-exp-delta-copy-review-packet",
        "status": STATUS,
        "decision": "positive_log_exp_delta_copy_review_private_only_public_copy_held",
        "date": DATE,
        "sourceSelector": selector["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "witnessCopyRows": [row],
        "requiredCaveats": required_caveats,
        "blockedGlobalPhrases": blocked_global_phrases,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceSelector"] != "eml-d42-positive-log-exp-next-action-selector":
        raise ValueError("D43 must consume D42")
    if summary["selectedOptionId"] != "positive_log_exp_delta_copy_review_packet":
        raise ValueError("unexpected selected option")
    if summary["selectedWitnessName"] != "MachLib.Real.positive_log_exp_roundtrip_witness":
        raise ValueError("unexpected witness")
    if summary["sourceSelectedCandidateId"] != "positive_log_exp_roundtrip_identity":
        raise ValueError("unexpected candidate")
    if summary["sourceSelectedFamily"] != "positive_domain_log_exp_roundtrip":
        raise ValueError("unexpected family")
    for key in [
        "copyReviewStarted",
        "privateCopyReviewOnly",
        "deltaCopyReviewOnly",
        "positiveDomainGuardRequired",
        "publicHoldPreserved",
        "runtimeBoundaryPreserved",
        "parkedConstantCoordinateRefresh",
        "parkedBoundedTrigFeasibility",
        "parkedPositiveLogExpBranchPause",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["guardCount"] != 1:
        raise ValueError("guard count drift")
    if summary["witnessRowCount"] != 1:
        raise ValueError("expected one delta witness row")
    if summary["requiredCaveatCount"] != 5:
        raise ValueError("unexpected caveat count")
    if summary["blockedGlobalPhraseCount"] != 8:
        raise ValueError("unexpected blocked phrase count")
    for key in [
        "publicPromotionPerformed",
        "publicEducationPromotionPerformed",
        "publicSurfaceUpdated",
        "advantageLabCaseAdded",
        "runtimeLoweringChanged",
        "logExpReplacementClaim",
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "candidateProvedThisPhase",
        "proofAttemptStarted",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["runtimeLoweringControl"] != "standard_log_exp_remains_runtime_control":
        raise ValueError("runtime lowering control drift")
    if summary["nextAction"] != "EML-D44 choose positive log-exp branch pause, next bounded identity branch, or human-approved public copy gate.":
        raise ValueError("unexpected next action")
    if summary["claimFlagsPublicFalse"] is not True or summary["claimFlagsAllBounded"] is not True:
        raise ValueError("claim flag boundary drift")
    for key in ["copy_review_started", "private_copy_review_only", "delta_copy_review_only"]:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in {"copy_review_started", "private_copy_review_only", "delta_copy_review_only"} and value is not False:
            raise ValueError(f"{key} must remain false")
    if any(row["publicPromotionAllowed"] for row in payload["witnessCopyRows"]):
        raise ValueError("delta row must not allow public promotion")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_positive_log_exp_delta_copy_review_packet",
        "validationStatus": "pass",
        "semanticStrength": "private_positive_log_exp_delta_copy_review_public_copy_held",
        "source": f"python/results/eml_d43_positive_log_exp_delta_copy_review_packet/eml_d43_positive_log_exp_delta_copy_review_packet_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d43_positive_log_exp_delta_copy_review_packet_feed",
        "date": DATE,
        "status": payload["status"],
        "decision": payload["decision"],
        "witnessRowCount": payload["summary"]["witnessRowCount"],
        "nextAction": payload["summary"]["nextAction"],
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D43 Positive Log-Exp Delta Copy Review Packet",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D43 reviews safe private wording for the checked positive log-exp witness while holding all public copy.",
        "",
        "| Witness | Copy status | Runtime control |",
        "|---|---|---|",
    ]
    for row in payload["witnessCopyRows"]:
        lines.append(f"| `{row['witnessId']}` | `{row['copyStatus']}` | {row['runtimeControl']} |")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- witness rows: `{payload['summary']['witnessRowCount']}`",
            f"- private copy review only: `{payload['summary']['privateCopyReviewOnly']}`",
            f"- delta copy review only: `{payload['summary']['deltaCopyReviewOnly']}`",
            f"- positive-domain guard required: `{payload['summary']['positiveDomainGuardRequired']}`",
            f"- public Atlas promotion: `{payload['claimFlags']['public_atlas_promotion']}`",
            f"- public education promotion: `{payload['claimFlags']['public_education_promotion']}`",
            f"- runtime lowering changed: `{payload['summary']['runtimeLoweringChanged']}`",
            f"- log/exp replacement claim: `{payload['summary']['logExpReplacementClaim']}`",
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
    result_path = out_dir / f"eml_d43_positive_log_exp_delta_copy_review_packet_{STAMP}.json"
    report_path = report_dir / f"eml_d43_positive_log_exp_delta_copy_review_packet_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d43_positive_log_exp_delta_copy_review_packet.json"
    feed_path = command_feed_dir / f"eml_d43_positive_log_exp_delta_copy_review_packet_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d43_positive_log_exp_delta_copy_review_packet")
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
    print("EML_D43_POSITIVE_LOG_EXP_DELTA_COPY_REVIEW_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
