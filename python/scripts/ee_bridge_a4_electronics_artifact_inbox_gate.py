#!/usr/bin/env python3
"""EE-BRIDGE-A4 pending inbox gate for laptop-agent electronics artifacts."""

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

from scripts import ee_bridge_a2_electronics_artifact_intake_validation as a2  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.electronics_artifact_inbox_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EE_BRIDGE_A4_ELECTRONICS_ARTIFACT_INBOX_GATE_PASS"
DEFAULT_INBOX_PATH = ROOT / "python/inbox/electronics/laptop_agent_returned_artifact.json"

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
    "EE-BRIDGE-A4 records the laptop-agent artifact inbox status only.",
    "EE-BRIDGE-A4 does not create or simulate a new electronics artifact.",
    "EE-BRIDGE-A4 does not modify monogate-electronics or /electronics.",
    "EE-BRIDGE-A4 does not perform hardware capture, serial reads, flashing, FPGA programming, or hardware operation.",
    "EE-BRIDGE-A4 does not claim hardware-observed behavior, production control, certified safety, public readiness, runtime performance, compiler correctness, or formal equivalence.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def artifact_rows_from_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if "artifacts" in payload and isinstance(payload["artifacts"], list):
        return payload["artifacts"]
    return [payload]


def relative_or_string(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def build_payload(artifact_path: Path = DEFAULT_INBOX_PATH) -> dict[str, Any]:
    contract = a2.read_json(a2.CONTRACT_PATH)
    guard_inventory = a2.read_json(a2.GUARD_INVENTORY_PATH)
    validation_rows: list[dict[str, Any]] = []
    artifact_exists = artifact_path.exists()
    inbox_status = "pending_no_artifact"
    if artifact_exists:
        raw = read_json(artifact_path)
        validation_rows = [
            a2.validate_candidate_artifact(artifact, contract, guard_inventory)
            for artifact in artifact_rows_from_payload(raw)
        ]
        inbox_status = (
            "artifact_validated"
            if validation_rows and all(row["accepted"] for row in validation_rows)
            else "artifact_blocked"
        )

    accepted_count = sum(1 for row in validation_rows if row.get("accepted"))
    blocked_count = len(validation_rows) - accepted_count
    live_capture_reviewable_count = sum(
        1 for row in validation_rows if row.get("decision") == "live_capture_reviewable"
    )
    summary = {
        "defaultInboxPath": relative_or_string(DEFAULT_INBOX_PATH),
        "artifactProvided": artifact_exists,
        "artifactPath": relative_or_string(artifact_path) if artifact_exists else None,
        "inboxStatus": inbox_status,
        "validationRowCount": len(validation_rows),
        "acceptedArtifactCount": accepted_count,
        "blockedArtifactCount": blocked_count,
        "liveCaptureReviewableCount": live_capture_reviewable_count,
        "hardwareObserved": False,
        "liveCapturePerformed": False,
        "monogateElectronicsRepoTouched": False,
        "electronicsSurfaceTouched": False,
        "readyForPrivateReview": inbox_status == "artifact_validated",
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "gateType": "electronics_artifact_inbox_gate_v0",
        "artifactId": "ee-bridge-a4-electronics-artifact-inbox-gate",
        "status": STATUS,
        "decision": "electronics_laptop_agent_inbox_pending_or_validated_without_hardware_claim",
        "date": DATE,
        "sourceValidator": "ee-bridge-a2-electronics-artifact-intake-validation",
        "inboxStatus": inbox_status,
        "artifactPath": summary["artifactPath"],
        "validationRows": validation_rows,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "electronics_artifact_inbox_gate",
        "validationStatus": "pass",
        "semanticStrength": "pending_inbox_gate_no_hardware_claim",
        "source": f"python/results/ee_bridge_a4_electronics_artifact_inbox_gate/ee_bridge_a4_electronics_artifact_inbox_gate_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "ee_bridge_a4_electronics_artifact_inbox_gate_feed",
        "date": DATE,
        "status": payload["status"],
        "inboxStatus": payload["inboxStatus"],
        "artifactProvided": payload["summary"]["artifactProvided"],
        "acceptedArtifactCount": payload["summary"]["acceptedArtifactCount"],
        "nextAction": "Place the laptop-agent returned artifact at the inbox path or pass --artifact-path, then rerun EE-BRIDGE-A4.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema version")
    if payload["inboxStatus"] not in {"pending_no_artifact", "artifact_validated", "artifact_blocked"}:
        raise ValueError("unexpected inbox status")
    if payload["inboxStatus"] == "pending_no_artifact" and summary["validationRowCount"] != 0:
        raise ValueError("pending inbox must not have validation rows")
    if payload["inboxStatus"] == "artifact_validated" and summary["acceptedArtifactCount"] < 1:
        raise ValueError("validated inbox must accept at least one artifact")
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
        "# EE-BRIDGE-A4 Electronics Artifact Inbox Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "EE-BRIDGE-A4 records whether a laptop-agent electronics artifact has arrived for EE-BRIDGE-A2 validation.",
        "",
        "## Summary",
        "",
        f"- inbox status: `{payload['inboxStatus']}`",
        f"- artifact provided: `{payload['summary']['artifactProvided']}`",
        f"- validation rows: {payload['summary']['validationRowCount']}",
        f"- accepted artifacts: {payload['summary']['acceptedArtifactCount']}",
        f"- blocked artifacts: {payload['summary']['blockedArtifactCount']}",
        f"- hardware observed: `{payload['summary']['hardwareObserved']}`",
        f"- live capture performed: `{payload['summary']['liveCapturePerformed']}`",
        "",
        "## Non-Claims",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["nonClaims"])
    return "\n".join(lines) + "\n"


def build_outputs(
    out_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
    artifact_path: Path = DEFAULT_INBOX_PATH,
) -> dict[str, str]:
    payload = build_payload(artifact_path)
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"ee_bridge_a4_electronics_artifact_inbox_gate_{STAMP}.json"
    report_path = report_dir / f"ee_bridge_a4_electronics_artifact_inbox_gate_{STAMP}.md"
    evidence_path = evidence_dir / "ee_bridge_a4_electronics_artifact_inbox_gate.json"
    feed_path = command_feed_dir / f"ee_bridge_a4_electronics_artifact_inbox_gate_feed_{STAMP}.json"
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
    parser.add_argument("--artifact-path", type=Path, default=DEFAULT_INBOX_PATH)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/ee_bridge_a4_electronics_artifact_inbox_gate")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(args.artifact_path)
    validate_payload(payload)
    if args.build:
        build_outputs(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir, args.artifact_path)
    print("EE_BRIDGE_A4_ELECTRONICS_ARTIFACT_INBOX_GATE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
