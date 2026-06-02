#!/usr/bin/env python3
"""EML-D41 positive log-exp witness private surface review."""

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

from scripts import eml_d40_positive_log_exp_roundtrip_witness_attempt as d40  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_positive_log_exp_witness_surface_review.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D41_POSITIVE_LOG_EXP_WITNESS_SURFACE_REVIEW_PASS"

CLAIM_FLAGS = {
    "surface_updated": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "advantage_lab_case_added": False,
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
    "electronics_repo_touched": False,
    "laptop_artifact_consumed": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "EML-D41 is a private surface review over the checked D40 positive log-exp witness; it does not update public pages or promote Atlas copy.",
    "The checked positive-domain identity is proof/teaching-shape evidence only; standard log/exp remain the runtime control.",
    "D41 does not claim log/exp replacement, theorem discovery, broad EML advantage, runtime performance, compiler correctness, formal equivalence, public readiness, course progress, or laptop artifact intake.",
]


def surface_row(
    surface_id: str,
    surface_kind: str,
    status: str,
    evidence_strength: str,
    action: str,
    rationale: list[str],
    blocked_claims: list[str],
) -> dict[str, Any]:
    return {
        "surfaceId": surface_id,
        "surfaceKind": surface_kind,
        "surfaceStatus": status,
        "evidenceStrength": evidence_strength,
        "recommendedAction": action,
        "rationale": rationale,
        "blockedClaims": blocked_claims,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    witness = d40.build_payload(atlas_gate_path)
    d40.validate_payload(witness)
    surface_rows = [
        surface_row(
            "machlib_witness_index_positive_log_exp_roundtrip",
            "machlib_private_index",
            "checked_witness_recorded_private",
            "scoped_machlib_positive_log_exp_roundtrip_witness_checked",
            "record_as_private_checked_witness",
            [
                "D40 checks MachLib.Real.positive_log_exp_roundtrip_witness.",
                "The checked statement is exp (log x) = x under the explicit guard 0 < x.",
                "Lake build passed with only pre-existing unrelated sorry warnings.",
            ],
            ["theorem discovery", "public readiness", "log/exp replacement"],
        ),
        surface_row(
            "positive_domain_log_exp_guardrail",
            "domain_guardrail",
            "scoped_positive_domain_identity_only",
            "positive_domain_guard_preserved",
            "keep_unguarded_and_broad_family_claims_blocked",
            [
                "D39 required the positive-domain guard before D40.",
                "D40 proves one guarded identity, not an unguarded log/exp theorem.",
                "Future identity branches must preserve explicit domain guards.",
            ],
            ["unguarded log-domain use", "broad log/exp family theorem", "arbitrary identity family"],
        ),
        surface_row(
            "advantage_lab_positive_log_exp_roundtrip",
            "advantage_lab",
            "runtime_control_remains_standard_log_exp",
            "scoped_machlib_positive_domain_identity_witness_available",
            "do_not_add_runtime_advantage_row_without_new_runtime_evidence",
            [
                "The witness strengthens proof/teaching shape only.",
                "Standard log/exp remain the semantic and runtime control.",
                "Any future Advantage row must preserve the no-replacement boundary unless separate runtime evidence exists.",
            ],
            ["runtime advantage", "runtime lowering superiority", "log/exp replacement"],
        ),
        surface_row(
            "public_atlas_positive_log_exp_roundtrip",
            "public_surface",
            "held_private",
            "checked_machlib_witness_available_private",
            "require_human_copy_review_before_public_change",
            [
                "D40 proof status is real but public wording has not been reviewed.",
                "No monogate.org or monogate.dev public route is changed by D41.",
                "Safe public wording must keep the 0 < x guard and avoid implying runtime EML superiority.",
            ],
            ["public readiness", "public theorem claim", "public Atlas promotion"],
        ),
    ]
    summary = {
        "sourceWitnessAttempt": witness["artifactId"],
        "selectedWitnessName": witness["summary"]["selectedWitnessName"],
        "sourceSelectedCandidateId": witness["summary"]["sourceSelectedCandidateId"],
        "sourceSelectedFamily": witness["summary"]["sourceSelectedFamily"],
        "surfaceRowCount": len(surface_rows),
        "checkedWitnessRecordedPrivately": witness["summary"]["scopedWitnessChecked"],
        "candidateProved": witness["summary"]["candidateProved"],
        "positiveDomainGuardRequired": witness["summary"]["positiveDomainGuardRequired"],
        "guardCount": witness["summary"]["guardCount"],
        "publicPromotionPerformed": False,
        "publicEducationCandidate": False,
        "advantageLabCaseAdded": False,
        "runtimeLoweringChanged": False,
        "logExpReplacementClaim": False,
        "runtimeLoweringControl": witness["summary"]["runtimeLoweringControl"],
        "surfaceUpdated": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "nextAction": "EML-D42 choose next bounded identity branch, private copy review, or pause without public promotion.",
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values())
        and all(all(value is False for value in row["claimFlags"].values()) for row in surface_rows),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "reviewType": "eml_positive_log_exp_witness_surface_review_v0",
        "artifactId": "eml-d41-positive-log-exp-witness-surface-review",
        "status": STATUS,
        "decision": "surface_checked_positive_log_exp_witness_as_private_review_evidence_only",
        "date": DATE,
        "sourceWitnessAttempt": witness["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "surfaceRows": surface_rows,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceWitnessAttempt"] != "eml-d40-positive-log-exp-roundtrip-witness-attempt":
        raise ValueError("D41 must consume D40")
    if summary["selectedWitnessName"] != "MachLib.Real.positive_log_exp_roundtrip_witness":
        raise ValueError("unexpected witness")
    if summary["sourceSelectedCandidateId"] != "positive_log_exp_roundtrip_identity":
        raise ValueError("unexpected candidate")
    if summary["sourceSelectedFamily"] != "positive_domain_log_exp_roundtrip":
        raise ValueError("unexpected selected family")
    if summary["surfaceRowCount"] != 4:
        raise ValueError("expected four surface rows")
    for key in ["checkedWitnessRecordedPrivately", "candidateProved", "positiveDomainGuardRequired"]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    if summary["guardCount"] != 1:
        raise ValueError("positive log-exp witness must keep exactly one guard")
    for key in [
        "publicPromotionPerformed",
        "publicEducationCandidate",
        "advantageLabCaseAdded",
        "runtimeLoweringChanged",
        "logExpReplacementClaim",
        "surfaceUpdated",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["runtimeLoweringControl"] != "standard_log_exp_remains_runtime_control":
        raise ValueError("runtime lowering control drift")
    if summary["nextAction"] != "EML-D42 choose next bounded identity branch, private copy review, or pause without public promotion.":
        raise ValueError("unexpected next action")
    if not all(value is False for value in payload["claimFlags"].values()):
        raise ValueError("claim flag drift")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_positive_log_exp_witness_surface_review",
        "validationStatus": "pass",
        "semanticStrength": "checked_positive_log_exp_witness_private_surface_review_no_public_update",
        "source": f"python/results/eml_d41_positive_log_exp_witness_surface_review/eml_d41_positive_log_exp_witness_surface_review_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d41_positive_log_exp_witness_surface_review_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedWitnessName": payload["summary"]["selectedWitnessName"],
        "nextAction": payload["summary"]["nextAction"],
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D41 Positive Log-Exp Witness Surface Review",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Selected witness: `{payload['summary']['selectedWitnessName']}`",
        "",
        "D41 routes the checked D40 positive log-exp witness into private review surfaces without public promotion.",
        "",
        "| Surface | Status | Evidence strength | Action |",
        "|---|---|---|---|",
    ]
    for row in payload["surfaceRows"]:
        lines.append(
            f"| `{row['surfaceId']}` | `{row['surfaceStatus']}` | `{row['evidenceStrength']}` | {row['recommendedAction']} |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- checked witness recorded privately: `{payload['summary']['checkedWitnessRecordedPrivately']}`",
            f"- positive-domain guard required: `{payload['summary']['positiveDomainGuardRequired']}`",
            f"- Advantage Lab case added: `{payload['summary']['advantageLabCaseAdded']}`",
            f"- runtime lowering changed: `{payload['summary']['runtimeLoweringChanged']}`",
            f"- log/exp replacement claim: `{payload['summary']['logExpReplacementClaim']}`",
            f"- runtime lowering control: `{payload['summary']['runtimeLoweringControl']}`",
            f"- surface updated: `{payload['summary']['surfaceUpdated']}`",
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
    result_path = out_dir / f"eml_d41_positive_log_exp_witness_surface_review_{STAMP}.json"
    report_path = report_dir / f"eml_d41_positive_log_exp_witness_surface_review_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d41_positive_log_exp_witness_surface_review.json"
    feed_path = command_feed_dir / f"eml_d41_positive_log_exp_witness_surface_review_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d41_positive_log_exp_witness_surface_review")
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
    print("EML_D41_POSITIVE_LOG_EXP_WITNESS_SURFACE_REVIEW_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
