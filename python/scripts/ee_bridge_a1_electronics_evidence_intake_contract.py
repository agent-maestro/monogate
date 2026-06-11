#!/usr/bin/env python3
"""EE-BRIDGE-A1 electronics evidence intake contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.electronics_evidence_intake_contract.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EE_BRIDGE_A1_ELECTRONICS_EVIDENCE_INTAKE_CONTRACT_PASS"

CLAIM_FLAGS = {
    "hardware_observed": False,
    "live_serial_capture_performed": False,
    "production_controller_claim": False,
    "certified_safety_claim": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "public_ready": False,
    "source_repo_modified": False,
    "electronics_url_modified": False,
    "automatic_reviewer_approval": False,
}

NON_CLAIMS = [
    "EE-BRIDGE-A1 defines a research-side intake contract only.",
    "EE-BRIDGE-A1 does not modify monogate-electronics.",
    "EE-BRIDGE-A1 does not modify the /electronics public surface.",
    "EE-BRIDGE-A1 does not perform hardware capture, serial reads, flashing, or FPGA programming.",
    "EE-BRIDGE-A1 does not claim hardware-observed behavior, production control, certified safety, or public readiness.",
]


def accepted_artifact_types() -> list[dict[str, str]]:
    return [
        {
            "artifactType": "simulated_lesson_packet",
            "description": "Lesson or course artifact with simulated values and all live-capture flags false.",
        },
        {
            "artifactType": "live_capture_packet",
            "description": "Future physical capture artifact with device, calibration, sample, and reviewer metadata.",
        },
        {
            "artifactType": "comparison_packet",
            "description": "Replay or measured-vs-expected comparison artifact tied to a named lesson/kernel.",
        },
        {
            "artifactType": "proof_guard_obligation_packet",
            "description": "Guard, domain, or proof-obligation packet for electronics kernels.",
        },
    ]


def required_fields() -> list[str]:
    return [
        "lessonId",
        "kernelId",
        "sourceRepo",
        "sourcePath",
        "artifactType",
        "equation",
        "captureStatus",
        "deviceMetadata",
        "calibrationContext",
        "sampleRows",
        "comparisonMethod",
        "maxObservedError",
        "claimFlags",
        "reviewerAction",
        "nextValidator",
    ]


def candidate_verticals() -> list[dict[str, Any]]:
    return [
        {
            "kernelId": "voltage_divider_v0",
            "recommendedOrder": 1,
            "whyFirst": "RH-A2 already routes the hardware-observed claim here, and prior selected voltage-divider proof evidence exists.",
            "nextValidator": "EE-A2 live capture packet from laptop agent, then research-side intake review.",
        },
        {
            "kernelId": "rc_decay_v0",
            "recommendedOrder": 2,
            "whyFirst": "Clean electronics/control kernel with a positive time-constant guard obligation.",
            "nextValidator": "Simulated lesson packet first, live capture only after hardware scope is approved.",
        },
        {
            "kernelId": "logic_guard_v0",
            "recommendedOrder": 3,
            "whyFirst": "Good bounded-output teaching kernel for claim hygiene and clamp-style guard review.",
            "nextValidator": "Comparison packet and guard-obligation review.",
        },
        {
            "kernelId": "pid_dual_target_v0",
            "recommendedOrder": 4,
            "whyFirst": "First dual-target (ESP32 + Arty A7) end-to-end kernel — exercises Forge's C and Verilog backends from the same EML source against the same plant fixture, so the comparison packet has a real cross-backend equivalence check.",
            "nextValidator": "Simulated lesson packet (research side, no hardware) lands first; then laptop agent produces ESP32 live_capture_packet and Arty A7 live_capture_packet; then comparison packet equivalence-checks the two traces against the simulated reference.",
        },
    ]


def build_contract() -> dict[str, Any]:
    artifacts = accepted_artifact_types()
    fields = required_fields()
    outcomes = [
        "private_reviewable_simulated",
        "capture_pending",
        "live_capture_reviewable",
        "blocked_missing_metadata",
        "blocked_claim_overreach",
    ]
    capture_statuses = [
        "simulated_or_pending",
        "live_capture_performed",
        "blocked_missing_metadata",
    ]
    handoff_boundary = {
        "laptopAgentOwns": ["monogate-electronics", "/electronics"],
        "researchSideOwns": [
            "schemas/electronics_evidence_intake_contract_v0.json",
            "research review packets",
            "claim-boundary validation",
        ],
        "monogateElectronicsRepoTouchedByThisSprint": False,
        "electronicsPublicSurfaceTouchedByThisSprint": False,
        "hardwareActionApproved": False,
        "hardwareActionPerformed": False,
    }
    summary = {
        "acceptedArtifactTypeCount": len(artifacts),
        "requiredFieldCount": len(fields),
        "captureStatusCount": len(capture_statuses),
        "reviewerOutcomeCount": len(outcomes),
        "candidateVerticalCount": len(candidate_verticals()),
        "recommendedFirstVertical": "voltage_divider_v0",
        "readyForLaptopAgentHandoff": True,
        "readyForReviewerCockpitIntake": True,
        "hardwareObserved": False,
        "liveCapturePerformed": False,
        "monogateElectronicsRepoTouched": False,
        "electronicsSurfaceTouched": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "contractType": "electronics_evidence_intake_contract_v0",
        "artifactId": "ee-bridge-a1-electronics-evidence-intake-contract",
        "status": STATUS,
        "decision": "electronics_evidence_intake_contract_recorded_no_hardware_claim",
        "date": DATE,
        "acceptedArtifactTypes": artifacts,
        "requiredFields": fields,
        "captureStatuses": capture_statuses,
        "reviewerOutcomes": outcomes,
        "candidateVerticals": candidate_verticals(),
        "handoffBoundary": handoff_boundary,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_evidence(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": contract["artifactId"],
        "artifactType": "electronics_evidence_intake_contract",
        "validationStatus": "pass",
        "semanticStrength": "electronics_intake_contract_recorded_no_hardware_claim",
        "source": f"python/results/ee_bridge_a1_electronics_evidence_intake_contract/ee_bridge_a1_electronics_evidence_intake_contract_{STAMP}.json",
        "summary": contract["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "ee_bridge_a1_electronics_evidence_intake_contract_feed",
        "date": DATE,
        "status": contract["status"],
        "decision": contract["decision"],
        "recommendedFirstVertical": contract["summary"]["recommendedFirstVertical"],
        "readyForLaptopAgentHandoff": True,
        "nextAction": "Receive laptop-agent electronics lesson/capture artifact and validate it against this intake contract.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def validate_contract(contract: dict[str, Any]) -> None:
    summary = contract["summary"]
    if contract["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema version")
    if summary["acceptedArtifactTypeCount"] != 4:
        raise ValueError("unexpected accepted artifact count")
    if summary["requiredFieldCount"] != 15:
        raise ValueError("unexpected required field count")
    if summary["reviewerOutcomeCount"] != 5:
        raise ValueError("unexpected reviewer outcome count")
    if summary["recommendedFirstVertical"] != "voltage_divider_v0":
        raise ValueError("unexpected first vertical")
    if not all(value is False for value in contract["claimFlags"].values()):
        raise ValueError("claim flag drift")
    boundary = contract["handoffBoundary"]
    if boundary["monogateElectronicsRepoTouchedByThisSprint"]:
        raise ValueError("monogate-electronics boundary drift")
    if boundary["electronicsPublicSurfaceTouchedByThisSprint"]:
        raise ValueError("/electronics boundary drift")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(contract: dict[str, Any]) -> str:
    lines = [
        "# EE-BRIDGE-A1 Electronics Evidence Intake Contract",
        "",
        f"Status: `{contract['status']}`",
        "",
        "EE-BRIDGE-A1 defines the research-side shape for accepting laptop-agent electronics artifacts without touching the electronics repo or public `/electronics` surface.",
        "",
        "## Summary",
        "",
        f"- accepted artifact types: {contract['summary']['acceptedArtifactTypeCount']}",
        f"- required fields: {contract['summary']['requiredFieldCount']}",
        f"- reviewer outcomes: {contract['summary']['reviewerOutcomeCount']}",
        f"- recommended first vertical: `{contract['summary']['recommendedFirstVertical']}`",
        f"- hardware observed: `{contract['summary']['hardwareObserved']}`",
        f"- live capture performed: `{contract['summary']['liveCapturePerformed']}`",
        "",
        "## Boundary",
        "",
        "- `monogate-electronics` remains owned by the laptop agent.",
        "- `/electronics` remains owned by the laptop agent/public electronics lane.",
        "- This sprint records contract shape only.",
        "",
        "## Non-Claims",
        "",
    ]
    lines.extend(f"- {item}" for item in contract["nonClaims"])
    return "\n".join(lines) + "\n"


def build_outputs(
    out_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
) -> dict[str, str]:
    contract = build_contract()
    validate_contract(contract)
    evidence = build_evidence(contract)
    feed = build_feed(contract)
    result_path = out_dir / f"ee_bridge_a1_electronics_evidence_intake_contract_{STAMP}.json"
    report_path = report_dir / f"ee_bridge_a1_electronics_evidence_intake_contract_{STAMP}.md"
    evidence_path = evidence_dir / "ee_bridge_a1_electronics_evidence_intake_contract.json"
    feed_path = command_feed_dir / f"ee_bridge_a1_electronics_evidence_intake_contract_feed_{STAMP}.json"
    write_json(result_path, contract)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(contract), encoding="utf-8")
    write_json(evidence_path, evidence)
    write_json(feed_path, feed)
    return {
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/ee_bridge_a1_electronics_evidence_intake_contract")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    contract = build_contract()
    validate_contract(contract)
    if args.build:
        build_outputs(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    print("EE_BRIDGE_A1_ELECTRONICS_EVIDENCE_INTAKE_CONTRACT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
