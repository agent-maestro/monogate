#!/usr/bin/env python3
"""EML-D32 subtraction-family pause and checked-witness index freeze packet."""

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

from scripts import eml_d31_checked_witness_review_next_decision as d31  # noqa: E402
from scripts import eml_d30_checked_witness_copy_review_packet as d30  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_subtraction_family_pause_freeze_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D32_SUBTRACTION_FAMILY_PAUSE_FREEZE_PACKET_PASS"

CLAIM_FLAGS = {
    "public_copy_approved": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "public_surface_updated": False,
    "advantage_lab_case_added": False,
    "implementation_started": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "candidate_proved": False,
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
    "public_ready": False,
}

NON_CLAIMS = [
    "EML-D32 is a private pause/freeze packet; it does not publish D30 copy or approve public wording.",
    "D32 freezes the currently checked witness index for handoff stability; it does not prove a broad nested subtraction family or arbitrary-depth theorem.",
    "D32 starts no MachLib edit, Lean typecheck, implementation, runtime-lowering change, public surface update, or Advantage Lab case.",
]

FROZEN_SCOPE_ROWS = [
    {
        "freezeId": "checked_witness_index_v0",
        "freezeStatus": "frozen_for_private_handoff",
        "source": "D30 witnessCopyRows",
        "contents": "six scoped checked witness ids and MachLib theorem names",
    },
    {
        "freezeId": "private_copy_caveats_v0",
        "freezeStatus": "frozen_for_private_handoff",
        "source": "D30 requiredCaveats",
        "contents": "private-only, no-public-promotion, scoped-witness, and runtime-control caveats",
    },
    {
        "freezeId": "blocked_public_phrases_v0",
        "freezeStatus": "frozen_for_private_handoff",
        "source": "D30 blockedGlobalPhrases",
        "contents": "theorem-discovery, broad-family, public-ready, runtime, compiler, formal-equivalence, and full-semantics blockers",
    },
    {
        "freezeId": "runtime_control_boundary_v0",
        "freezeStatus": "frozen_for_private_handoff",
        "source": "D30 and D31 runtimeLoweringControl",
        "contents": "standard subtraction remains the runtime control; standard log, exp, and constants remain controls where applicable",
    },
]

AVAILABLE_AFTER_FREEZE = [
    {
        "actionId": "human_approved_public_copy_gate",
        "availability": "available_only_with_explicit_human_approval",
        "requiredInputs": [
            "explicit human approval",
            "D30 caveats reused verbatim or strengthened",
            "blocked phrases remain blocked",
        ],
    },
    {
        "actionId": "new_bounded_identity_branch_selector",
        "availability": "available_after_pause_packet",
        "requiredInputs": [
            "one bounded statement",
            "separate selector artifact",
            "no default nested-family expansion",
        ],
    },
    {
        "actionId": "course_scaling_private_reference",
        "availability": "available_as_private_reference_only",
        "requiredInputs": [
            "claim-bounded wording",
            "no public copy publication",
            "standard runtime controls named",
        ],
    },
]


def frozen_witness_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "witnessId": row["witnessId"],
        "machlibName": row["machlibName"],
        "freezeStatus": "frozen_for_private_handoff",
        "copyStatus": row["copyStatus"],
        "publicPromotionAllowed": False,
        "runtimeControl": row["runtimeControl"],
        "requiredCaveatCount": len(row["requiredCaveats"]),
        "blockedPhraseCount": len(row["blockedPhrases"]),
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    decision = d31.build_payload(atlas_gate_path)
    d31.validate_payload(decision)
    review = d30.build_payload(atlas_gate_path)
    d30.validate_payload(review)
    frozen_witnesses = [frozen_witness_row(row) for row in review["witnessCopyRows"]]
    summary = {
        "sourceDecision": decision["artifactId"],
        "sourceReview": review["artifactId"],
        "selectedOptionId": decision["summary"]["selectedOptionId"],
        "selectedNextArtifact": decision["summary"]["selectedNextArtifact"],
        "familyDeepeningPauseSelected": decision["summary"]["familyDeepeningPauseSelected"],
        "checkedWitnessIndexFreezePlanned": decision["summary"]["checkedWitnessIndexFreezePlanned"],
        "familyDeepeningPaused": True,
        "checkedWitnessIndexFrozen": True,
        "frozenWitnessCount": len(frozen_witnesses),
        "freezeScopeRowCount": len(FROZEN_SCOPE_ROWS),
        "availableActionCount": len(AVAILABLE_AFTER_FREEZE),
        "d30RequiredCaveatCount": review["summary"]["requiredCaveatCount"],
        "d30BlockedGlobalPhraseCount": review["summary"]["blockedGlobalPhraseCount"],
        "publicCopyApproved": False,
        "humanApprovalRecorded": False,
        "newBoundedBranchStarted": False,
        "copyReviewStartedInD32": False,
        "publicPromotionPerformed": False,
        "publicEducationPromotionPerformed": False,
        "publicSurfaceUpdated": False,
        "advantageLabCaseAdded": False,
        "implementationStarted": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "candidateProved": False,
        "runtimeLoweringChanged": False,
        "runtimeLoweringControl": decision["summary"]["runtimeLoweringControl"],
        "broadNestedSubtractionClaim": False,
        "broadSubtractionFamilyClaim": False,
        "arbitraryDepthClaim": False,
        "publicReady": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values())
        and all(all(value is False for value in row["claimFlags"].values()) for row in frozen_witnesses),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "eml_subtraction_family_pause_freeze_packet_v0",
        "artifactId": "eml-d32-subtraction-family-pause-freeze-packet",
        "status": STATUS,
        "decision": "pause_subtraction_family_deepening_and_freeze_checked_witness_index",
        "date": DATE,
        "sourceDecision": decision["artifactId"],
        "sourceReview": review["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "frozenWitnessRows": frozen_witnesses,
        "freezeScopeRows": list(FROZEN_SCOPE_ROWS),
        "availableAfterFreeze": list(AVAILABLE_AFTER_FREEZE),
        "preservedRequiredCaveats": list(review["requiredCaveats"]),
        "preservedBlockedGlobalPhrases": list(review["blockedGlobalPhrases"]),
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceDecision"] != "eml-d31-checked-witness-review-next-decision":
        raise ValueError("D32 must consume D31")
    if payload["sourceReview"] != "eml-d30-checked-witness-copy-review-packet":
        raise ValueError("D32 must preserve D30 review rows")
    if summary["selectedOptionId"] != "pause_subtraction_family_deepening":
        raise ValueError("D32 requires D31 pause selection")
    if summary["familyDeepeningPauseSelected"] is not True or summary["checkedWitnessIndexFreezePlanned"] is not True:
        raise ValueError("D31 pause/freeze intent must be preserved")
    if summary["familyDeepeningPaused"] is not True:
        raise ValueError("family deepening must be paused")
    if summary["checkedWitnessIndexFrozen"] is not True:
        raise ValueError("checked witness index must be frozen")
    if summary["frozenWitnessCount"] != 6:
        raise ValueError("expected six frozen witnesses")
    if summary["freezeScopeRowCount"] != 4:
        raise ValueError("expected four freeze scope rows")
    if summary["availableActionCount"] != 3:
        raise ValueError("expected three available-after-freeze actions")
    if summary["d30RequiredCaveatCount"] != 5 or summary["d30BlockedGlobalPhraseCount"] != 8:
        raise ValueError("D30 caveat/blocker counts drifted")
    for key in [
        "publicCopyApproved",
        "humanApprovalRecorded",
        "newBoundedBranchStarted",
        "copyReviewStartedInD32",
        "publicPromotionPerformed",
        "publicEducationPromotionPerformed",
        "publicSurfaceUpdated",
        "advantageLabCaseAdded",
        "implementationStarted",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "candidateProved",
        "runtimeLoweringChanged",
        "broadNestedSubtractionClaim",
        "broadSubtractionFamilyClaim",
        "arbitraryDepthClaim",
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
    if any(row["publicPromotionAllowed"] for row in payload["frozenWitnessRows"]):
        raise ValueError("frozen witnesses must not allow public promotion")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_subtraction_family_pause_freeze_packet",
        "validationStatus": "pass",
        "semanticStrength": "private_pause_freeze_packet_no_public_copy_no_implementation",
        "source": f"python/results/eml_d32_subtraction_family_pause_freeze_packet/eml_d32_subtraction_family_pause_freeze_packet_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d32_subtraction_family_pause_freeze_packet_feed",
        "date": DATE,
        "status": payload["status"],
        "decision": payload["decision"],
        "frozenWitnessCount": payload["summary"]["frozenWitnessCount"],
        "nextAction": "Choose a post-freeze path: human-approved public copy gate, new bounded identity branch selector, or Course 2 private reference packet.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D32 Subtraction-Family Pause Freeze Packet",
        "",
        f"Status: `{payload['status']}`",
        "",
        "D32 pauses subtraction-family deepening and freezes the checked-witness index for private handoff stability.",
        "",
        "| Witness | Freeze status | Runtime control |",
        "|---|---|---|",
    ]
    for row in payload["frozenWitnessRows"]:
        lines.append(f"| `{row['witnessId']}` | `{row['freezeStatus']}` | {row['runtimeControl']} |")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- family deepening paused: `{payload['summary']['familyDeepeningPaused']}`",
            f"- checked witness index frozen: `{payload['summary']['checkedWitnessIndexFrozen']}`",
            f"- frozen witnesses: `{payload['summary']['frozenWitnessCount']}`",
            f"- public copy approved: `{payload['summary']['publicCopyApproved']}`",
            f"- implementation started: `{payload['summary']['implementationStarted']}`",
            f"- runtime lowering changed: `{payload['summary']['runtimeLoweringChanged']}`",
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
    result_path = out_dir / f"eml_d32_subtraction_family_pause_freeze_packet_{STAMP}.json"
    report_path = report_dir / f"eml_d32_subtraction_family_pause_freeze_packet_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d32_subtraction_family_pause_freeze_packet.json"
    feed_path = command_feed_dir / f"eml_d32_subtraction_family_pause_freeze_packet_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d32_subtraction_family_pause_freeze_packet")
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
    print("EML_D32_SUBTRACTION_FAMILY_PAUSE_FREEZE_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
