#!/usr/bin/env python3
"""EML-D30 checked-witness private copy review packet."""

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

from scripts import eml_d29_nested_family_next_branch_decision as d29  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_checked_witness_copy_review_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D30_CHECKED_WITNESS_COPY_REVIEW_PACKET_PASS"

CLAIM_FLAGS = {
    "copy_review_started": True,
    "private_copy_review_only": True,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "public_surface_updated": False,
    "advantage_lab_case_added": False,
    "runtime_lowering_changed": False,
    "broad_nested_subtraction_claim": False,
    "broad_subtraction_family_claim": False,
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
    "EML-D30 is a private checked-witness copy review packet only; it does not update public Atlas, public education, or any public surface.",
    "D30 reviews wording for scoped checked witnesses; it does not claim theorem discovery, broad nested-family support, broad EML advantage, full EML semantics, compiler correctness, runtime performance, formal equivalence, or public readiness.",
    "Standard subtraction, standard log, and standard exp remain the runtime controls where applicable.",
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
        "copyStatus": "private_copy_reviewable",
        "publicPromotionAllowed": False,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_witness_rows() -> list[dict[str, Any]]:
    return [
        witness_copy_row(
            "constants_zero_one_e_boundary",
            "MachLib.Real.constants_zero_one_e_boundary_witness",
            "A checked MachLib witness records three small EML constant-boundary identities for 0, 1, and exp(1).",
            [
                "Say exp(1), not a broad Euler-constant system.",
                "Describe this as a scoped witness, not theorem discovery.",
                "Keep public education copy held for human review.",
            ],
            [
                "EML discovers e",
                "public theorem",
                "complete constant semantics",
            ],
            "standard constants and exp remain runtime controls",
        ),
        witness_copy_row(
            "ln_from_eml_boundary",
            "MachLib.Real.ln_from_eml_boundary_witness",
            "A checked MachLib witness records a positive-branch reconstruction of log y through a nested EML expression.",
            [
                "Always name the 0 < y guard.",
                "Say positive branch or positive real input.",
                "Keep standard log(y) as the runtime control.",
            ],
            [
                "EML replaces log",
                "all logarithms",
                "branch-free logarithm theorem",
            ],
            "standard log(y) remains runtime control",
        ),
        witness_copy_row(
            "subtraction_boundary_affine_offset",
            "MachLib.Real.subtraction_boundary_affine_offset_witness",
            "A checked MachLib witness records one guarded affine-offset subtraction-boundary identity.",
            [
                "Always name the 0 < x + y guard.",
                "Call it one scoped affine-offset identity.",
                "Keep standard subtraction as the runtime control.",
            ],
            [
                "general subtraction family proved",
                "EML beats subtraction",
                "runtime lowering changed",
            ],
            "standard subtraction remains runtime control",
        ),
        witness_copy_row(
            "subtraction_boundary_two_stage_chain",
            "MachLib.Real.subtraction_boundary_two_stage_chain_witness",
            "A checked MachLib witness records one guarded two-stage nested subtraction-boundary chain.",
            [
                "Always name both positive log-domain guards.",
                "Say two-stage nested instance, not broad nested-family theorem.",
                "Keep public Atlas copy held.",
            ],
            [
                "all nested subtraction chains",
                "broad nested theorem",
                "public Atlas ready",
            ],
            "standard subtraction remains runtime control",
        ),
        witness_copy_row(
            "subtraction_boundary_affine_nested_chain",
            "MachLib.Real.subtraction_boundary_affine_nested_chain_witness",
            "A checked MachLib witness records one guarded affine-nested subtraction-boundary chain.",
            [
                "Always name 0 < x + y and 0 < z.",
                "Describe it as a scoped composition of checked proof shapes.",
                "Do not imply a public education release.",
            ],
            [
                "affine nested family proved",
                "nested subtraction family solved",
                "public-ready lesson",
            ],
            "standard subtraction remains runtime control",
        ),
        witness_copy_row(
            "subtraction_boundary_three_stage_chain",
            "MachLib.Real.subtraction_boundary_three_stage_chain_witness",
            "A checked MachLib witness records one guarded three-stage nested subtraction-boundary chain.",
            [
                "Always name 0 < a, 0 < b, and 0 < c.",
                "Say three-stage nested instance, not arbitrary depth.",
                "Do not claim further depth expansion.",
            ],
            [
                "arbitrary-depth nested theorem",
                "full nested subtraction family",
                "proof frontier complete",
            ],
            "standard subtraction remains runtime control",
        ),
    ]


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    decision = d29.build_payload(atlas_gate_path)
    d29.validate_payload(decision)
    rows = build_witness_rows()
    required_caveats = [
        "All wording is private-reviewable only.",
        "Public Atlas promotion remains false.",
        "Public education promotion remains false.",
        "Checked witness means a scoped MachLib theorem name exists; it does not imply theorem discovery or broad family support.",
        "Runtime controls remain standard log, exp, constants, and subtraction as applicable.",
    ]
    blocked_global_phrases = [
        "theorem discovery",
        "broad EML advantage",
        "public ready",
        "runtime performance",
        "compiler correctness",
        "formal equivalence",
        "full EML semantics",
        "broad nested subtraction family",
    ]
    summary = {
        "sourceDecision": decision["artifactId"],
        "selectedOptionId": decision["summary"]["selectedOptionId"],
        "copyReviewStarted": True,
        "privateCopyReviewOnly": True,
        "witnessRowCount": len(rows),
        "requiredCaveatCount": len(required_caveats),
        "blockedGlobalPhraseCount": len(blocked_global_phrases),
        "publicPromotionPerformed": False,
        "publicEducationPromotionPerformed": False,
        "publicSurfaceUpdated": False,
        "advantageLabCaseAdded": False,
        "runtimeLoweringChanged": False,
        "runtimeLoweringControl": decision["summary"]["runtimeLoweringControl"],
        "broadNestedSubtractionClaim": False,
        "broadSubtractionFamilyClaim": False,
        "familyPauseStillParked": decision["summary"]["familyPausePreviouslyParked"],
        "newBranchSelectionStillParked": True,
        "publicReady": False,
        "claimFlagsPublicFalse": all(
            CLAIM_FLAGS[key] is False
            for key in [
                "public_atlas_promotion",
                "public_education_promotion",
                "public_surface_updated",
                "public_ready",
            ]
        ),
        "claimFlagsAllBounded": CLAIM_FLAGS["copy_review_started"] is True
        and CLAIM_FLAGS["private_copy_review_only"] is True
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key not in {"copy_review_started", "private_copy_review_only"}
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "reviewType": "eml_checked_witness_copy_review_packet_v0",
        "artifactId": "eml-d30-checked-witness-copy-review-packet",
        "status": STATUS,
        "decision": "checked_witness_copy_review_private_only_public_copy_held",
        "date": DATE,
        "sourceDecision": decision["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "witnessCopyRows": rows,
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
    if payload["sourceDecision"] != "eml-d29-nested-family-next-branch-decision":
        raise ValueError("D30 must consume D29")
    if summary["selectedOptionId"] != "checked_witness_copy_review_packet":
        raise ValueError("unexpected selected option")
    if summary["copyReviewStarted"] is not True:
        raise ValueError("D30 must start private copy review")
    if summary["privateCopyReviewOnly"] is not True:
        raise ValueError("copy review must remain private only")
    if summary["witnessRowCount"] != 6:
        raise ValueError("expected six witness rows")
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
        "broadNestedSubtractionClaim",
        "broadSubtractionFamilyClaim",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["runtimeLoweringControl"] != "standard_subtraction_remains_runtime_control":
        raise ValueError("runtime lowering control drift")
    if summary["familyPauseStillParked"] is not True or summary["newBranchSelectionStillParked"] is not True:
        raise ValueError("parked branch status drift")
    if summary["claimFlagsPublicFalse"] is not True or summary["claimFlagsAllBounded"] is not True:
        raise ValueError("claim flag boundary drift")
    if payload["claimFlags"]["copy_review_started"] is not True:
        raise ValueError("copy review flag must be true for D30")
    if payload["claimFlags"]["private_copy_review_only"] is not True:
        raise ValueError("private-only flag must be true for D30")
    for key, value in payload["claimFlags"].items():
        if key not in {"copy_review_started", "private_copy_review_only"} and value is not False:
            raise ValueError(f"{key} must remain false")
    if any(row["publicPromotionAllowed"] for row in payload["witnessCopyRows"]):
        raise ValueError("witness rows must not allow public promotion")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_checked_witness_copy_review_packet",
        "validationStatus": "pass",
        "semanticStrength": "private_checked_witness_copy_review_public_copy_held",
        "source": f"python/results/eml_d30_checked_witness_copy_review_packet/eml_d30_checked_witness_copy_review_packet_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d30_checked_witness_copy_review_packet_feed",
        "date": DATE,
        "status": payload["status"],
        "decision": payload["decision"],
        "witnessRowCount": payload["summary"]["witnessRowCount"],
        "nextAction": "Choose family pause, new bounded branch, or human-approved public copy gate; do not publish this copy directly.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D30 Checked Witness Copy Review Packet",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D30 reviews safe private wording for checked witnesses while holding all public copy.",
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
            f"- public Atlas promotion: `{payload['claimFlags']['public_atlas_promotion']}`",
            f"- public education promotion: `{payload['claimFlags']['public_education_promotion']}`",
            f"- runtime lowering changed: `{payload['summary']['runtimeLoweringChanged']}`",
            f"- broad nested subtraction claim: `{payload['summary']['broadNestedSubtractionClaim']}`",
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
    result_path = out_dir / f"eml_d30_checked_witness_copy_review_packet_{STAMP}.json"
    report_path = report_dir / f"eml_d30_checked_witness_copy_review_packet_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d30_checked_witness_copy_review_packet.json"
    feed_path = command_feed_dir / f"eml_d30_checked_witness_copy_review_packet_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d30_checked_witness_copy_review_packet")
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
    print("EML_D30_CHECKED_WITNESS_COPY_REVIEW_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
