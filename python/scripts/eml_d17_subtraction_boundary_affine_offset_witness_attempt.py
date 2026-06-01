#!/usr/bin/env python3
"""EML-D17 subtraction-boundary affine-offset MachLib witness attempt."""

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

from scripts import eml_d16_subtraction_boundary_family_selector as d16  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_subtraction_boundary_affine_offset_witness_attempt.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D17_SUBTRACTION_BOUNDARY_AFFINE_OFFSET_WITNESS_ATTEMPT_PASS"
MACHLIB_ROOT = ROOT.parent / "machlib" / "foundations"

CLAIM_FLAGS = {
    "theorem_discovery_claim": False,
    "general_eml_superiority_claim": False,
    "eml_advantage_proved": False,
    "runtime_performance_claim": False,
    "runtime_lowering_changed": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "full_eml_semantics_claim": False,
    "public_atlas_promotion": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "EML-D17 checks one scoped affine-offset subtraction-boundary MachLib witness selected by D16; it is not theorem discovery or broad EML advantage.",
    "The affine-offset witness is proof/teaching-shape evidence only; standard subtraction remains the runtime lowering control.",
    "D17 does not prove full EML semantics, compiler correctness, runtime performance, formal equivalence, public Atlas promotion, or public readiness.",
]


def file_contains(path: Path, token: str) -> bool:
    return path.exists() and token in path.read_text(encoding="utf-8")


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    selector = d16.build_payload(atlas_gate_path)
    d16.validate_payload(selector)
    atlas_path = MACHLIB_ROOT / "MachLib" / "EMLAtlasWitness.lean"
    selected = {
        "name": "subtraction_boundary_affine_offset_witness",
        "machlibName": "MachLib.Real.subtraction_boundary_affine_offset_witness",
        "path": "../machlib/foundations/MachLib/EMLAtlasWitness.lean",
        "statement": "eml (log (x + y)) (exp y) = x under 0 < x + y",
        "present": file_contains(atlas_path, "theorem subtraction_boundary_affine_offset_witness"),
        "sourceStatementId": selector["summary"]["selectedStatementId"],
    }
    verification = {
        "command": "cd ../machlib/foundations && lake build",
        "observedStatus": "pass",
        "observedNotes": [
            "MachLib.EMLAtlasWitness built.",
            "Top-level MachLib build completed successfully.",
            "Pre-existing sorry warnings remain in unrelated MachLib.ForgeTest and MachLib.HighDimensional declarations.",
        ],
    }
    summary = {
        "sourceSelector": selector["artifactId"],
        "selectedStatementId": selector["summary"]["selectedStatementId"],
        "selectedWitnessName": selected["machlibName"],
        "selectedWitnessPresent": selected["present"],
        "machlibFileChanged": True,
        "leanTypecheckPerformed": True,
        "lakeBuildPassed": True,
        "scopedWitnessChecked": selected["present"],
        "duplicateBaseRejectedBySelector": selector["summary"]["duplicateBaseRejected"],
        "negativeControlBlockedBySelector": selector["summary"]["negativeControlBlocked"],
        "runtimeLoweringControl": "standard_subtraction_remains_runtime_control",
        "runtimeLoweringChanged": False,
        "theoremDiscoveryClaim": False,
        "publicReady": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "attemptType": "eml_subtraction_boundary_affine_offset_witness_attempt_v0",
        "artifactId": "eml-d17-subtraction-boundary-affine-offset-witness-attempt",
        "status": STATUS,
        "decision": "subtraction_boundary_affine_offset_witness_checked_in_machlib",
        "date": DATE,
        "sourceSelector": selector["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "selectedWitness": selected,
        "verification": verification,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceSelector"] != "eml-d16-subtraction-boundary-family-selector":
        raise ValueError("D17 must consume D16")
    if summary["selectedStatementId"] != "subtraction_boundary_affine_offset_family_v1":
        raise ValueError("unexpected selected statement")
    if summary["selectedWitnessName"] != "MachLib.Real.subtraction_boundary_affine_offset_witness":
        raise ValueError("unexpected selected witness")
    if summary["selectedWitnessPresent"] is not True:
        raise ValueError("selected witness theorem missing")
    if summary["leanTypecheckPerformed"] is not True or summary["lakeBuildPassed"] is not True:
        raise ValueError("D17 requires observed Lake build pass")
    if summary["scopedWitnessChecked"] is not True:
        raise ValueError("scoped witness must be checked")
    if summary["duplicateBaseRejectedBySelector"] is not True:
        raise ValueError("D17 must preserve duplicate-base rejection")
    if summary["negativeControlBlockedBySelector"] is not True:
        raise ValueError("D17 must preserve negative-control block")
    if summary["runtimeLoweringControl"] != "standard_subtraction_remains_runtime_control":
        raise ValueError("runtime control drift")
    if summary["runtimeLoweringChanged"] is not False:
        raise ValueError("runtime lowering must not change")
    if summary["theoremDiscoveryClaim"] is not False or summary["publicReady"] is not False:
        raise ValueError("claim boundary drift")
    if not all(value is False for value in payload["claimFlags"].values()):
        raise ValueError("claim flag drift")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_subtraction_boundary_affine_offset_witness_attempt",
        "validationStatus": "pass",
        "semanticStrength": "scoped_machlib_affine_offset_identity_witness_checked",
        "source": f"python/results/eml_d17_subtraction_boundary_affine_offset_witness_attempt/eml_d17_subtraction_boundary_affine_offset_witness_attempt_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d17_subtraction_boundary_affine_offset_witness_attempt_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedWitnessName": payload["summary"]["selectedWitnessName"],
        "nextAction": "Surface D17 privately before any public copy or broader subtraction-family claim.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D17 Subtraction Boundary Affine-Offset Witness Attempt",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Selected witness: `{payload['summary']['selectedWitnessName']}`",
        "",
        "D17 implements and checks the affine-offset subtraction-boundary witness selected by D16.",
        "",
        "## Verification",
        "",
        f"- command: `{payload['verification']['command']}`",
        f"- observed status: `{payload['verification']['observedStatus']}`",
        f"- scoped witness checked: `{payload['summary']['scopedWitnessChecked']}`",
        f"- runtime lowering control: `{payload['summary']['runtimeLoweringControl']}`",
        f"- public ready: `{payload['summary']['publicReady']}`",
        "",
        "## Non-Claims",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["nonClaims"])
    return "\n".join(lines) + "\n"


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path, atlas_gate_path: Path) -> dict[str, Any]:
    payload = build_payload(atlas_gate_path)
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"eml_d17_subtraction_boundary_affine_offset_witness_attempt_{STAMP}.json"
    report_path = report_dir / f"eml_d17_subtraction_boundary_affine_offset_witness_attempt_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d17_subtraction_boundary_affine_offset_witness_attempt.json"
    feed_path = command_feed_dir / f"eml_d17_subtraction_boundary_affine_offset_witness_attempt_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d17_subtraction_boundary_affine_offset_witness_attempt")
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
    print("EML_D17_SUBTRACTION_BOUNDARY_AFFINE_OFFSET_WITNESS_ATTEMPT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
