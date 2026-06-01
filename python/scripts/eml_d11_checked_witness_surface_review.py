#!/usr/bin/env python3
"""EML-D11 checked witness surface review."""

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

from scripts import eml_d10_machlib_identity_witness_attempt as d10  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_checked_witness_surface_review.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D11_CHECKED_WITNESS_SURFACE_REVIEW_PASS"

CLAIM_FLAGS = {
    "surface_updated": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "advantage_lab_case_added": False,
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
    "EML-D11 is a surface review over the checked D10 witness; it does not update public pages or promote Atlas copy.",
    "D11 does not add an Advantage Lab case, claim theorem discovery, prove broad EML advantage, prove full EML semantics, prove compiler correctness, claim runtime performance, or claim formal equivalence.",
    "The D10 constants witness remains a scoped definition-level proof artifact until a separate reviewer/public-surface phase approves wording.",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atlas_decision(gate: dict[str, Any], entry_id: str) -> dict[str, Any]:
    return next(item for item in gate["decisions"] if item["id"] == entry_id)


def checked_witness(gate: dict[str, Any], entry_id: str) -> dict[str, Any]:
    return next(item for item in gate["checkedWitnesses"] if item["entryId"] == entry_id)


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
    witness = d10.build_payload()
    d10.validate_payload(witness)
    gate = load_json(atlas_gate_path)
    constants_decision = atlas_decision(gate, "constants_zero_and_e")
    constants_witness = checked_witness(gate, "constants_zero_and_e")
    surface_rows = [
        surface_row(
            "atlas_promotion_gate_constants_zero_and_e",
            "atlas_gate",
            "checked_witness_recorded_no_public_promotion",
            "checked_machlib_witness_available",
            "keep_as_private_proof_target_until_copy_review",
            [
                "Atlas gate sees constants_zero_and_e as checked_machlib_witness_available.",
                "The entry remains outside safe_public_education_candidate until a separate copy review approves wording.",
                f"Checked name: {constants_witness['machlibName']}.",
            ],
            ["public Atlas promotion", "theorem discovery", "general EML superiority"],
        ),
        surface_row(
            "advantage_lab_constants_zero_and_e",
            "advantage_lab",
            "not_in_current_case_set",
            "scoped_definition_level_witness_available",
            "prepare_separate_advantage_or_teaching_row_if_needed",
            [
                "The current Advantage Lab case set is R10/R10B/R10C-centered and does not include constants_zero_and_e as a runtime/stability fixture.",
                "D10 can support a future teaching/proof-shape row, but should not be forced into the runtime advantage scoreboard.",
                "Any future Advantage row must keep runtime and broad advantage claims blocked.",
            ],
            ["runtime advantage", "public performance", "broad EML advantage"],
        ),
        surface_row(
            "public_atlas_constants_zero_and_e",
            "public_surface",
            "held_private",
            "checked_machlib_witness_available_private",
            "require_human_copy_review_before_public_change",
            [
                "D10 proof status is real but public wording has not been reviewed.",
                "No monogate.org or monogate.dev public route is changed by D11.",
                "The safe public voice should explain exp(1) rather than overclaim a new constant theorem.",
            ],
            ["public readiness", "public theorem claim", "public Atlas promotion"],
        ),
    ]
    summary = {
        "sourceWitnessAttempt": witness["artifactId"],
        "selectedWitnessName": witness["summary"]["selectedWitnessName"],
        "surfaceRowCount": len(surface_rows),
        "checkedWitnessRecordedInAtlasGate": constants_decision["proofStatus"] == "checked_machlib_witness_available",
        "publicPromotionPerformed": constants_decision["publicPromotionPerformed"],
        "publicEducationCandidate": constants_decision["publicEducationCandidate"],
        "advantageLabCaseAdded": False,
        "surfaceUpdated": False,
        "nextAction": "EML-D12 choose the next identity witness or a separate copy-review packet for constants.",
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values())
        and all(all(value is False for value in row["claimFlags"].values()) for row in surface_rows),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "reviewType": "eml_checked_witness_surface_review_v0",
        "artifactId": "eml-d11-checked-witness-surface-review",
        "status": STATUS,
        "decision": "surface_checked_constants_witness_as_private_review_evidence_only",
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
    if payload["sourceWitnessAttempt"] != "eml-d10-machlib-identity-witness-attempt":
        raise ValueError("D11 must consume D10")
    if summary["selectedWitnessName"] != "MachLib.Real.constants_zero_one_e_boundary_witness":
        raise ValueError("unexpected witness")
    if summary["surfaceRowCount"] != 3:
        raise ValueError("expected three surface rows")
    if summary["checkedWitnessRecordedInAtlasGate"] is not True:
        raise ValueError("Atlas gate must record checked witness")
    if summary["publicPromotionPerformed"] is not False:
        raise ValueError("public promotion must remain false")
    if summary["publicEducationCandidate"] is not False:
        raise ValueError("constants public education must remain pending")
    if summary["advantageLabCaseAdded"] is not False or summary["surfaceUpdated"] is not False:
        raise ValueError("D11 must not update public/advantage surfaces")
    if not all(value is False for value in payload["claimFlags"].values()):
        raise ValueError("claim flag drift")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_checked_witness_surface_review",
        "validationStatus": "pass",
        "semanticStrength": "checked_witness_private_surface_review_no_public_update",
        "source": f"python/results/eml_d11_checked_witness_surface_review/eml_d11_checked_witness_surface_review_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d11_checked_witness_surface_review_feed",
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
        "# EML-D11 Checked Witness Surface Review",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Selected witness: `{payload['summary']['selectedWitnessName']}`",
        "",
        "D11 routes the checked D10 constants witness into private review surfaces without public promotion.",
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
            f"- Atlas checked witness recorded: `{payload['summary']['checkedWitnessRecordedInAtlasGate']}`",
            f"- public promotion performed: `{payload['summary']['publicPromotionPerformed']}`",
            f"- Advantage Lab case added: `{payload['summary']['advantageLabCaseAdded']}`",
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
    result_path = out_dir / f"eml_d11_checked_witness_surface_review_{STAMP}.json"
    report_path = report_dir / f"eml_d11_checked_witness_surface_review_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d11_checked_witness_surface_review.json"
    feed_path = command_feed_dir / f"eml_d11_checked_witness_surface_review_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d11_checked_witness_surface_review")
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
    print("EML_D11_CHECKED_WITNESS_SURFACE_REVIEW_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
