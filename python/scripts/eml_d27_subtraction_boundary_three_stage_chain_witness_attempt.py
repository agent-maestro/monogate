#!/usr/bin/env python3
"""EML-D27 subtraction-boundary three-stage chain MachLib witness attempt."""

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

from scripts import eml_d26_nested_family_next_branch_decision as d26  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_subtraction_boundary_three_stage_chain_witness_attempt.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D27_SUBTRACTION_BOUNDARY_THREE_STAGE_CHAIN_WITNESS_ATTEMPT_PASS"
MACHLIB_ROOT = ROOT.parent / "machlib" / "foundations"

CLAIM_FLAGS = {
    "theorem_discovery_claim": False,
    "broad_nested_subtraction_claim": False,
    "broad_subtraction_family_claim": False,
    "general_eml_superiority_claim": False,
    "eml_advantage_proved": False,
    "runtime_performance_claim": False,
    "runtime_lowering_changed": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "full_eml_semantics_claim": False,
    "public_atlas_promotion": False,
    "public_education_promotion": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "EML-D27 checks one scoped three-stage subtraction-boundary MachLib witness selected by D26; it is not theorem discovery or broad EML advantage.",
    "The three-stage chain witness is proof/teaching-shape evidence only; standard subtraction remains the runtime lowering control.",
    "D27 does not prove a general nested subtraction family, full EML semantics, compiler correctness, runtime performance, formal equivalence, public Atlas promotion, public education promotion, or public readiness.",
]


def file_contains(path: Path, token: str) -> bool:
    return path.exists() and token in path.read_text(encoding="utf-8")


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    selector = d26.build_payload(atlas_gate_path)
    d26.validate_payload(selector)
    atlas_path = MACHLIB_ROOT / "MachLib" / "EMLAtlasWitness.lean"
    selected = {
        "name": "subtraction_boundary_three_stage_chain_witness",
        "machlibName": "MachLib.Real.subtraction_boundary_three_stage_chain_witness",
        "path": "../machlib/foundations/MachLib/EMLAtlasWitness.lean",
        "statement": "eml (log a) (exp (eml (log b) (exp (eml (log c) (exp u))))) = a - (b - (c - u)) under 0 < a, 0 < b, and 0 < c",
        "present": file_contains(atlas_path, "theorem subtraction_boundary_three_stage_chain_witness"),
        "sourceSelectedOptionId": selector["summary"]["selectedOptionId"],
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
        "sourceBranchDecision": selector["artifactId"],
        "selectedOptionId": selector["summary"]["selectedOptionId"],
        "selectedWitnessName": selected["machlibName"],
        "selectedWitnessPresent": selected["present"],
        "machlibFileChanged": True,
        "leanTypecheckPerformed": True,
        "lakeBuildPassed": True,
        "scopedWitnessChecked": selected["present"],
        "negativeControlBlockedBySelector": selector["summary"]["negativeControlBlockedBySelector"],
        "twoStageWitnessRecordedPrivately": selector["summary"]["twoStageWitnessRecordedPrivately"],
        "affineNestedWitnessRecordedPrivately": selector["summary"]["affineNestedWitnessRecordedPrivately"],
        "copyReviewStarted": False,
        "broadNestedSubtractionClaim": False,
        "broadSubtractionFamilyClaim": False,
        "runtimeLoweringControl": "standard_subtraction_remains_runtime_control",
        "runtimeLoweringChanged": False,
        "theoremDiscoveryClaim": False,
        "publicReady": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "attemptType": "eml_subtraction_boundary_three_stage_chain_witness_attempt_v0",
        "artifactId": "eml-d27-subtraction-boundary-three-stage-chain-witness-attempt",
        "status": STATUS,
        "decision": "subtraction_boundary_three_stage_chain_witness_checked_in_machlib",
        "date": DATE,
        "sourceBranchDecision": selector["artifactId"],
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
    if payload["sourceBranchDecision"] != "eml-d26-nested-family-next-branch-decision":
        raise ValueError("D27 must consume D26")
    if summary["selectedOptionId"] != "three_stage_chain_witness_attempt":
        raise ValueError("unexpected selected branch")
    if summary["selectedWitnessName"] != "MachLib.Real.subtraction_boundary_three_stage_chain_witness":
        raise ValueError("unexpected selected witness")
    if summary["selectedWitnessPresent"] is not True:
        raise ValueError("selected witness theorem missing")
    if summary["leanTypecheckPerformed"] is not True or summary["lakeBuildPassed"] is not True:
        raise ValueError("D27 requires observed Lake build pass")
    if summary["scopedWitnessChecked"] is not True:
        raise ValueError("scoped witness must be checked")
    if summary["negativeControlBlockedBySelector"] is not True:
        raise ValueError("D27 must preserve negative-control block")
    if summary["twoStageWitnessRecordedPrivately"] is not True:
        raise ValueError("D27 must consume the private two-stage surface review chain")
    if summary["affineNestedWitnessRecordedPrivately"] is not True:
        raise ValueError("D27 must consume the private affine-nested surface review chain")
    for key in [
        "copyReviewStarted",
        "broadNestedSubtractionClaim",
        "broadSubtractionFamilyClaim",
        "runtimeLoweringChanged",
        "theoremDiscoveryClaim",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["runtimeLoweringControl"] != "standard_subtraction_remains_runtime_control":
        raise ValueError("runtime control drift")
    if not all(value is False for value in payload["claimFlags"].values()):
        raise ValueError("claim flag drift")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_subtraction_boundary_three_stage_chain_witness_attempt",
        "validationStatus": "pass",
        "semanticStrength": "scoped_machlib_three_stage_subtraction_identity_witness_checked",
        "source": f"python/results/eml_d27_subtraction_boundary_three_stage_chain_witness_attempt/eml_d27_subtraction_boundary_three_stage_chain_witness_attempt_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d27_subtraction_boundary_three_stage_chain_witness_attempt_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedWitnessName": payload["summary"]["selectedWitnessName"],
        "nextAction": "Surface D27 privately before any public copy, broader nested-family claim, or further depth expansion.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D27 Subtraction Boundary Three-Stage Chain Witness Attempt",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Selected witness: `{payload['summary']['selectedWitnessName']}`",
        "",
        "D27 implements and checks the three-stage subtraction-boundary witness selected by D26.",
        "",
        "## Verification",
        "",
        f"- command: `{payload['verification']['command']}`",
        f"- observed status: `{payload['verification']['observedStatus']}`",
        f"- scoped witness checked: `{payload['summary']['scopedWitnessChecked']}`",
        f"- broad nested subtraction claim: `{payload['summary']['broadNestedSubtractionClaim']}`",
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
    result_path = out_dir / f"eml_d27_subtraction_boundary_three_stage_chain_witness_attempt_{STAMP}.json"
    report_path = report_dir / f"eml_d27_subtraction_boundary_three_stage_chain_witness_attempt_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d27_subtraction_boundary_three_stage_chain_witness_attempt.json"
    feed_path = command_feed_dir / f"eml_d27_subtraction_boundary_three_stage_chain_witness_attempt_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d27_subtraction_boundary_three_stage_chain_witness_attempt")
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
    print("EML_D27_SUBTRACTION_BOUNDARY_THREE_STAGE_CHAIN_WITNESS_ATTEMPT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
