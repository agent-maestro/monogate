#!/usr/bin/env python3
"""EE-BRIDGE-A6 regression guard for the electronics evidence bridge."""

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

from scripts import ee_bridge_a1_electronics_evidence_intake_contract as a1  # noqa: E402
from scripts import ee_bridge_a2_electronics_artifact_intake_validation as a2  # noqa: E402
from scripts import ee_bridge_a4_electronics_artifact_inbox_gate as a4  # noqa: E402
from scripts import ee_guard_a1_electronics_guard_obligation_inventory as guard_a1  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.electronics_bridge_regression_guard.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EE_BRIDGE_A6_ELECTRONICS_BRIDGE_REGRESSION_GUARD_PASS"

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
    "EE-BRIDGE-A6 is a regression guard over existing electronics bridge artifacts only.",
    "EE-BRIDGE-A6 does not ingest a real laptop-agent artifact.",
    "EE-BRIDGE-A6 does not modify monogate-electronics or /electronics.",
    "EE-BRIDGE-A6 does not perform hardware capture, serial reads, flashing, FPGA programming, or hardware operation.",
    "EE-BRIDGE-A6 does not claim hardware-observed behavior, production control, certified safety, public readiness, runtime performance, compiler correctness, or formal equivalence.",
]


def flags_all_false(payload: dict[str, Any]) -> bool:
    return all(value is False for value in payload.get("claimFlags", {}).values())


def guard_row(row_id: str, description: str, passed: bool, observed: Any) -> dict[str, Any]:
    return {
        "id": row_id,
        "description": description,
        "passed": passed,
        "observed": observed,
    }


def build_checked_artifacts(
    contract: dict[str, Any],
    inventory: dict[str, Any],
    intake: dict[str, Any],
    inbox: dict[str, Any],
) -> list[dict[str, str]]:
    return [
        {
            "id": contract["artifactId"],
            "schemaVersion": contract["schemaVersion"],
            "status": contract["status"],
        },
        {
            "id": inventory["artifactId"],
            "schemaVersion": inventory["schemaVersion"],
            "status": inventory["status"],
        },
        {
            "id": intake["artifactId"],
            "schemaVersion": intake["schemaVersion"],
            "status": intake["status"],
        },
        {
            "id": inbox["artifactId"],
            "schemaVersion": inbox["schemaVersion"],
            "status": inbox["status"],
        },
    ]


def build_payload() -> dict[str, Any]:
    contract = a1.build_contract()
    inventory = guard_a1.build_inventory()
    intake = a2.build_payload()
    inbox = a4.build_payload()
    rows = [
        guard_row(
            "a1_contract_artifact_types",
            "EE-BRIDGE-A1 keeps four accepted artifact types.",
            contract["summary"]["acceptedArtifactTypeCount"] == 4,
            contract["summary"]["acceptedArtifactTypeCount"],
        ),
        guard_row(
            "a1_required_fields",
            "EE-BRIDGE-A1 keeps 15 required intake fields.",
            contract["summary"]["requiredFieldCount"] == 15,
            contract["summary"]["requiredFieldCount"],
        ),
        guard_row(
            "guard_a1_obligation_counts",
            "EE-GUARD-A1 keeps three obligations with two open rows.",
            inventory["summary"]["obligationCount"] == 3 and inventory["summary"]["openObligationCount"] == 2,
            {
                "obligations": inventory["summary"]["obligationCount"],
                "open": inventory["summary"]["openObligationCount"],
            },
        ),
        guard_row(
            "a2_simulated_handoff_accepts_one",
            "EE-BRIDGE-A2 keeps one accepted simulated handoff artifact.",
            intake["summary"]["acceptedArtifactCount"] == 1,
            intake["summary"]["acceptedArtifactCount"],
        ),
        guard_row(
            "a2_negative_controls_pass",
            "EE-BRIDGE-A2 keeps two passing negative controls.",
            intake["summary"]["negativeControlPassCount"] == 2,
            intake["summary"]["negativeControlPassCount"],
        ),
        guard_row(
            "a4_default_inbox_pending",
            "EE-BRIDGE-A4 default inbox remains pending until a real artifact arrives.",
            inbox["inboxStatus"] == "pending_no_artifact" and inbox["summary"]["validationRowCount"] == 0,
            {
                "inboxStatus": inbox["inboxStatus"],
                "validationRows": inbox["summary"]["validationRowCount"],
            },
        ),
        guard_row(
            "all_claim_flags_false",
            "All electronics bridge artifact claim flags remain false.",
            all(flags_all_false(item) for item in [contract, inventory, intake, inbox]) and all(value is False for value in CLAIM_FLAGS.values()),
            "all false",
        ),
        guard_row(
            "electronics_ownership_boundary",
            "No bridge artifact touches monogate-electronics or /electronics.",
            contract["summary"]["monogateElectronicsRepoTouched"] is False
            and contract["summary"]["electronicsSurfaceTouched"] is False
            and inbox["summary"]["monogateElectronicsRepoTouched"] is False
            and inbox["summary"]["electronicsSurfaceTouched"] is False,
            "not touched",
        ),
    ]
    pass_count = sum(1 for row in rows if row["passed"])
    summary = {
        "checkedArtifactCount": 4,
        "guardRowCount": len(rows),
        "guardPassCount": pass_count,
        "guardFailCount": len(rows) - pass_count,
        "defaultInboxStatus": inbox["inboxStatus"],
        "realLaptopAgentArtifactReceived": False,
        "hardwareObserved": False,
        "liveCapturePerformed": False,
        "monogateElectronicsRepoTouched": False,
        "electronicsSurfaceTouched": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "guardType": "electronics_bridge_regression_guard_v0",
        "artifactId": "ee-bridge-a6-electronics-bridge-regression-guard",
        "status": STATUS,
        "decision": "electronics_bridge_regression_guard_pass_real_artifact_still_pending",
        "date": DATE,
        "checkedArtifacts": build_checked_artifacts(contract, inventory, intake, inbox),
        "guardRows": rows,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema version")
    if summary["checkedArtifactCount"] != 4:
        raise ValueError("unexpected checked artifact count")
    if summary["guardRowCount"] != 8:
        raise ValueError("unexpected guard row count")
    if summary["guardFailCount"] != 0:
        raise ValueError("guard row failure")
    if summary["defaultInboxStatus"] != "pending_no_artifact":
        raise ValueError("default inbox status drift")
    if summary["hardwareObserved"] or summary["liveCapturePerformed"]:
        raise ValueError("hardware/live capture claim drift")
    if summary["monogateElectronicsRepoTouched"] or summary["electronicsSurfaceTouched"]:
        raise ValueError("electronics ownership boundary drift")
    if not all(value is False for value in payload["claimFlags"].values()):
        raise ValueError("claim flag drift")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "electronics_bridge_regression_guard",
        "validationStatus": "pass",
        "semanticStrength": "bridge_regression_guard_pass_real_artifact_pending",
        "source": f"python/results/ee_bridge_a6_electronics_bridge_regression_guard/ee_bridge_a6_electronics_bridge_regression_guard_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "ee_bridge_a6_electronics_bridge_regression_guard_feed",
        "date": DATE,
        "status": payload["status"],
        "decision": payload["decision"],
        "guardPassCount": payload["summary"]["guardPassCount"],
        "defaultInboxStatus": payload["summary"]["defaultInboxStatus"],
        "nextAction": "Wait for the laptop-agent returned artifact, then rerun EE-BRIDGE-A4 and this guard.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EE-BRIDGE-A6 Electronics Bridge Regression Guard",
        "",
        f"Status: `{payload['status']}`",
        "",
        "EE-BRIDGE-A6 locks the electronics bridge chain while the real laptop-agent artifact is still pending.",
        "",
        "## Summary",
        "",
        f"- checked artifacts: {payload['summary']['checkedArtifactCount']}",
        f"- guard rows: {payload['summary']['guardRowCount']}",
        f"- guard passes: {payload['summary']['guardPassCount']}",
        f"- guard failures: {payload['summary']['guardFailCount']}",
        f"- default inbox status: `{payload['summary']['defaultInboxStatus']}`",
        f"- real laptop-agent artifact received: `{payload['summary']['realLaptopAgentArtifactReceived']}`",
        "",
        "## Guard Rows",
        "",
    ]
    lines.extend(f"- `{row['id']}`: `{row['passed']}`" for row in payload["guardRows"])
    lines.extend(["", "## Non-Claims", ""])
    lines.extend(f"- {item}" for item in payload["nonClaims"])
    return "\n".join(lines) + "\n"


def build_outputs(
    out_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
) -> dict[str, str]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"ee_bridge_a6_electronics_bridge_regression_guard_{STAMP}.json"
    report_path = report_dir / f"ee_bridge_a6_electronics_bridge_regression_guard_{STAMP}.md"
    evidence_path = evidence_dir / "ee_bridge_a6_electronics_bridge_regression_guard.json"
    feed_path = command_feed_dir / f"ee_bridge_a6_electronics_bridge_regression_guard_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/ee_bridge_a6_electronics_bridge_regression_guard")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    validate_payload(payload)
    if args.build:
        build_outputs(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    print("EE_BRIDGE_A6_ELECTRONICS_BRIDGE_REGRESSION_GUARD_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
