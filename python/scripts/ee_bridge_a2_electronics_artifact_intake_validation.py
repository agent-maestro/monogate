#!/usr/bin/env python3
"""EE-BRIDGE-A2 electronics artifact intake validation."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.electronics_artifact_intake_validation.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EE_BRIDGE_A2_ELECTRONICS_ARTIFACT_INTAKE_VALIDATION_PASS"

CONTRACT_PATH = ROOT / "python/results/ee_bridge_a1_electronics_evidence_intake_contract/ee_bridge_a1_electronics_evidence_intake_contract_2026_06_01.json"
GUARD_INVENTORY_PATH = ROOT / "python/results/ee_guard_a1_electronics_guard_obligation_inventory/ee_guard_a1_electronics_guard_obligation_inventory_2026_06_01.json"
FIXTURE_PATH = ROOT / "python/fixtures/electronics/ee_bridge_a2_laptop_agent_simulated_handoff.json"

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
    "EE-BRIDGE-A2 validates a fixture-backed electronics handoff only.",
    "EE-BRIDGE-A2 does not receive a live laptop-agent hardware capture.",
    "EE-BRIDGE-A2 does not modify monogate-electronics or /electronics.",
    "EE-BRIDGE-A2 does not perform serial reads, flashing, FPGA programming, or hardware operation.",
    "EE-BRIDGE-A2 does not claim hardware-observed behavior, production control, certified safety, public readiness, runtime performance, compiler correctness, or formal equivalence.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def artifact_claim_flags_all_false(artifact: dict[str, Any]) -> bool:
    return all(value is False for value in artifact.get("claimFlags", {}).values())


def validate_candidate_artifact(
    artifact: dict[str, Any],
    contract: dict[str, Any],
    guard_inventory: dict[str, Any],
) -> dict[str, Any]:
    required_fields = contract["requiredFields"]
    missing = [field for field in required_fields if field not in artifact]
    accepted_types = {item["artifactType"] for item in contract["acceptedArtifactTypes"]}
    known_kernels = {item["kernelId"] for item in guard_inventory["obligations"]}
    reasons: list[str] = []
    decision = artifact.get("reviewerAction", "blocked_missing_metadata")

    if missing:
        decision = "blocked_missing_metadata"
        reasons.append("missing_required_fields")
    if artifact.get("artifactType") not in accepted_types:
        decision = "blocked_missing_metadata"
        reasons.append("unknown_artifact_type")
    if artifact.get("kernelId") not in known_kernels:
        decision = "blocked_missing_metadata"
        reasons.append("unknown_kernel_id")
    if not artifact_claim_flags_all_false(artifact):
        decision = "blocked_claim_overreach"
        reasons.append("claim_flag_true")
    if artifact.get("captureStatus") == "live_capture_performed":
        metadata = artifact.get("deviceMetadata", {})
        calibration = artifact.get("calibrationContext", {})
        if not metadata.get("deviceObserved") or not metadata.get("deviceId") or not calibration.get("calibrated"):
            decision = "blocked_missing_metadata"
            reasons.append("live_capture_missing_device_or_calibration_metadata")
    if not artifact.get("sampleRows"):
        decision = "blocked_missing_metadata"
        reasons.append("empty_sample_rows")
    if artifact.get("sourceRepo") != "monogate-electronics":
        decision = "blocked_missing_metadata"
        reasons.append("unexpected_source_repo")

    accepted = decision in {"private_reviewable_simulated", "live_capture_reviewable"} and not reasons
    return {
        "lessonId": artifact.get("lessonId"),
        "kernelId": artifact.get("kernelId"),
        "artifactType": artifact.get("artifactType"),
        "captureStatus": artifact.get("captureStatus"),
        "decision": decision,
        "accepted": accepted,
        "reasonCodes": reasons,
        "sampleRowCount": len(artifact.get("sampleRows", [])),
        "maxObservedError": artifact.get("maxObservedError"),
        "claimFlagsAllFalse": artifact_claim_flags_all_false(artifact),
        "sourceRepo": artifact.get("sourceRepo"),
        "sourcePath": artifact.get("sourcePath"),
        "nextValidator": artifact.get("nextValidator"),
    }


def build_negative_control_rows(
    fixture: dict[str, Any],
    contract: dict[str, Any],
    guard_inventory: dict[str, Any],
) -> list[dict[str, Any]]:
    base = fixture["artifacts"][0]
    rows: list[dict[str, Any]] = []
    for control in fixture["negativeControls"]:
        mutated = copy.deepcopy(base)
        if control["controlId"] == "missing_device_metadata_live_capture_v0":
            mutated["captureStatus"] = "live_capture_performed"
            mutated["reviewerAction"] = "live_capture_reviewable"
        elif control["controlId"] == "hardware_claim_overreach_v0":
            mutated["claimFlags"]["hardware_observed"] = True
        result = validate_candidate_artifact(mutated, contract, guard_inventory)
        rows.append(
            {
                "controlId": control["controlId"],
                "mutation": control["mutation"],
                "expectedDecision": control["expectedDecision"],
                "actualDecision": result["decision"],
                "passed": result["decision"] == control["expectedDecision"],
                "reasonCodes": result["reasonCodes"],
            }
        )
    return rows


def build_payload(fixture_path: Path = FIXTURE_PATH) -> dict[str, Any]:
    contract = read_json(CONTRACT_PATH)
    guard_inventory = read_json(GUARD_INVENTORY_PATH)
    fixture = read_json(fixture_path)
    accepted_rows = [
        validate_candidate_artifact(artifact, contract, guard_inventory)
        for artifact in fixture["artifacts"]
    ]
    negative_rows = build_negative_control_rows(fixture, contract, guard_inventory)
    accepted_count = sum(1 for row in accepted_rows if row["accepted"])
    negative_pass_count = sum(1 for row in negative_rows if row["passed"])
    summary = {
        "fixtureId": fixture["fixtureId"],
        "sourceOwner": fixture["sourceOwner"],
        "sourceRepo": fixture["sourceRepo"],
        "publicSurface": fixture["publicSurface"],
        "candidateArtifactCount": len(accepted_rows),
        "acceptedArtifactCount": accepted_count,
        "blockedArtifactCount": len(accepted_rows) - accepted_count,
        "negativeControlCount": len(negative_rows),
        "negativeControlPassCount": negative_pass_count,
        "recommendedFirstVertical": "voltage_divider_v0",
        "guardInventoryObligationCount": guard_inventory["summary"]["obligationCount"],
        "hardwareObserved": False,
        "liveCapturePerformed": False,
        "laptopAgentLiveArtifactReceived": False,
        "monogateElectronicsRepoTouched": False,
        "electronicsSurfaceTouched": False,
        "readyForPrivateReview": accepted_count == len(accepted_rows) and negative_pass_count == len(negative_rows),
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "validationType": "electronics_artifact_intake_validation_v0",
        "artifactId": "ee-bridge-a2-electronics-artifact-intake-validation",
        "status": STATUS,
        "decision": "electronics_simulated_handoff_validated_live_capture_still_pending",
        "date": DATE,
        "sourceContract": contract["artifactId"],
        "sourceGuardInventory": guard_inventory["artifactId"],
        "fixturePath": str(fixture_path.relative_to(ROOT)),
        "acceptedArtifacts": accepted_rows,
        "negativeControls": negative_rows,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "electronics_artifact_intake_validation",
        "validationStatus": "pass",
        "semanticStrength": "simulated_handoff_validated_live_capture_pending",
        "source": f"python/results/ee_bridge_a2_electronics_artifact_intake_validation/ee_bridge_a2_electronics_artifact_intake_validation_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "ee_bridge_a2_electronics_artifact_intake_validation_feed",
        "date": DATE,
        "status": payload["status"],
        "decision": payload["decision"],
        "acceptedArtifactCount": payload["summary"]["acceptedArtifactCount"],
        "negativeControlPassCount": payload["summary"]["negativeControlPassCount"],
        "nextAction": "Wait for laptop-agent artifact; if live capture is present, require device and calibration metadata before private review.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema version")
    if summary["candidateArtifactCount"] != 1:
        raise ValueError("unexpected candidate artifact count")
    if summary["acceptedArtifactCount"] != 1:
        raise ValueError("unexpected accepted artifact count")
    if summary["negativeControlCount"] != 2:
        raise ValueError("unexpected negative control count")
    if summary["negativeControlPassCount"] != 2:
        raise ValueError("negative controls did not pass")
    if summary["hardwareObserved"] or summary["liveCapturePerformed"]:
        raise ValueError("hardware/live capture claim drift")
    if summary["monogateElectronicsRepoTouched"] or summary["electronicsSurfaceTouched"]:
        raise ValueError("electronics ownership boundary drift")
    if not all(value is False for value in payload["claimFlags"].values()):
        raise ValueError("claim flag drift")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EE-BRIDGE-A2 Electronics Artifact Intake Validation",
        "",
        f"Status: `{payload['status']}`",
        "",
        "EE-BRIDGE-A2 validates a fixture-backed electronics handoff against the EE-BRIDGE-A1 intake contract and EE-GUARD-A1 obligation inventory.",
        "",
        "## Summary",
        "",
        f"- candidate artifacts: {payload['summary']['candidateArtifactCount']}",
        f"- accepted artifacts: {payload['summary']['acceptedArtifactCount']}",
        f"- negative controls: {payload['summary']['negativeControlCount']}",
        f"- negative controls passed: {payload['summary']['negativeControlPassCount']}",
        f"- hardware observed: `{payload['summary']['hardwareObserved']}`",
        f"- live capture performed: `{payload['summary']['liveCapturePerformed']}`",
        "",
        "## Accepted Artifacts",
        "",
    ]
    for row in payload["acceptedArtifacts"]:
        lines.append(f"- `{row['kernelId']}` / `{row['lessonId']}` -> `{row['decision']}`")
    lines.extend(["", "## Negative Controls", ""])
    for row in payload["negativeControls"]:
        lines.append(f"- `{row['controlId']}` -> `{row['actualDecision']}` pass `{row['passed']}`")
    lines.extend(["", "## Non-Claims", ""])
    lines.extend(f"- {item}" for item in payload["nonClaims"])
    return "\n".join(lines) + "\n"


def build_outputs(
    out_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
    fixture_path: Path = FIXTURE_PATH,
) -> dict[str, str]:
    payload = build_payload(fixture_path)
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"ee_bridge_a2_electronics_artifact_intake_validation_{STAMP}.json"
    report_path = report_dir / f"ee_bridge_a2_electronics_artifact_intake_validation_{STAMP}.md"
    evidence_path = evidence_dir / "ee_bridge_a2_electronics_artifact_intake_validation.json"
    feed_path = command_feed_dir / f"ee_bridge_a2_electronics_artifact_intake_validation_feed_{STAMP}.json"
    write_json(result_path, payload)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(payload), encoding="utf-8")
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
    parser.add_argument("--fixture-path", type=Path, default=FIXTURE_PATH)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/ee_bridge_a2_electronics_artifact_intake_validation")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(args.fixture_path)
    validate_payload(payload)
    if args.build:
        build_outputs(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir, args.fixture_path)
    print("EE_BRIDGE_A2_ELECTRONICS_ARTIFACT_INTAKE_VALIDATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
