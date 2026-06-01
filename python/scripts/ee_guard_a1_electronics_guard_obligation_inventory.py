#!/usr/bin/env python3
"""EE-GUARD-A1 electronics guard obligation inventory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.electronics_guard_obligation_inventory.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EE_GUARD_A1_ELECTRONICS_GUARD_OBLIGATION_INVENTORY_PASS"

CLAIM_FLAGS = {
    "hardware_observed": False,
    "live_serial_capture_performed": False,
    "proof_claim": False,
    "complete_guard_proof_claim": False,
    "production_controller_claim": False,
    "certified_safety_claim": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "EE-GUARD-A1 records guard obligations for electronics kernels only.",
    "EE-GUARD-A1 does not perform hardware capture or operate electronics hardware.",
    "EE-GUARD-A1 does not prove all electronics guards.",
    "EE-GUARD-A1 does not claim production control, certified safety, compiler correctness, formal equivalence, or public readiness.",
]


def build_obligations() -> list[dict[str, Any]]:
    return [
        {
            "obligationId": "voltage_divider_positive_resistance_sum_v0",
            "kernelId": "voltage_divider_v0",
            "predicate": "r_top > 0 && r_bottom > 0 -> r_top + r_bottom != 0",
            "route": "MachLib.PositiveCoordinateObligation",
            "status": "prior_selected_witness_linked",
            "priorEvidence": [
                "FEF-P22 selected voltage_divider Lean proof discharge",
                "FEF-P23 selected voltage_divider zero-sorry-file proof discharge",
            ],
            "reviewBoundary": "Selected generated Lean-file evidence only; not a broad electronics proof.",
        },
        {
            "obligationId": "rc_decay_positive_time_constant_v0",
            "kernelId": "rc_decay_v0",
            "predicate": "R > 0 && C > 0 -> R * C > 0",
            "route": "MachLib.PositiveProductObligation",
            "status": "open_guard_obligation",
            "priorEvidence": [],
            "reviewBoundary": "Needs a selected guard witness or runtime/capture packet before claim promotion.",
        },
        {
            "obligationId": "logic_guard_output_bounds_v0",
            "kernelId": "logic_guard_v0",
            "predicate": "lo <= hi -> clamp(x, lo, hi) in [lo, hi]",
            "route": "MachLib.ClampBoundObligation",
            "status": "open_guard_obligation",
            "priorEvidence": [],
            "reviewBoundary": "Needs a selected clamp-bound witness or bounded comparison packet before claim promotion.",
        },
    ]


def build_inventory() -> dict[str, Any]:
    obligations = build_obligations()
    selected = [item for item in obligations if item["status"] == "prior_selected_witness_linked"]
    open_items = [item for item in obligations if item["status"] == "open_guard_obligation"]
    summary = {
        "obligationCount": len(obligations),
        "selectedProofLinkedCount": len(selected),
        "openObligationCount": len(open_items),
        "recommendedFirstClosure": "voltage_divider_positive_resistance_sum_v0",
        "hardwareObserved": False,
        "liveCapturePerformed": False,
        "proofClaim": False,
        "completeGuardProofClaim": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "inventoryType": "electronics_guard_obligation_inventory_v0",
        "artifactId": "ee-guard-a1-electronics-guard-obligation-inventory",
        "status": STATUS,
        "decision": "electronics_guard_obligation_inventory_recorded_no_proof_or_hardware_claim",
        "date": DATE,
        "intakeContract": "ee-bridge-a1-electronics-evidence-intake-contract",
        "obligations": obligations,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_evidence(inventory: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": inventory["artifactId"],
        "artifactType": "electronics_guard_obligation_inventory",
        "validationStatus": "pass",
        "semanticStrength": "guard_obligation_inventory_no_hardware_or_proof_claim",
        "source": f"python/results/ee_guard_a1_electronics_guard_obligation_inventory/ee_guard_a1_electronics_guard_obligation_inventory_{STAMP}.json",
        "summary": inventory["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(inventory: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "ee_guard_a1_electronics_guard_obligation_inventory_feed",
        "date": DATE,
        "status": inventory["status"],
        "decision": inventory["decision"],
        "recommendedFirstClosure": inventory["summary"]["recommendedFirstClosure"],
        "nextAction": "Attach laptop-agent voltage-divider course/capture artifact, then keep RC and logic guard obligations open until evidence exists.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def validate_inventory(inventory: dict[str, Any]) -> None:
    summary = inventory["summary"]
    if inventory["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema version")
    if summary["obligationCount"] != 3:
        raise ValueError("unexpected obligation count")
    if summary["selectedProofLinkedCount"] != 1:
        raise ValueError("unexpected selected proof count")
    if summary["openObligationCount"] != 2:
        raise ValueError("unexpected open obligation count")
    if summary["proofClaim"]:
        raise ValueError("proof claim drift")
    if not all(value is False for value in inventory["claimFlags"].values()):
        raise ValueError("claim flag drift")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(inventory: dict[str, Any]) -> str:
    lines = [
        "# EE-GUARD-A1 Electronics Guard Obligation Inventory",
        "",
        f"Status: `{inventory['status']}`",
        "",
        "EE-GUARD-A1 records guard/proof obligations for the electronics bridge without claiming hardware validation or complete proof coverage.",
        "",
        "## Obligations",
        "",
    ]
    for item in inventory["obligations"]:
        lines.append(f"- `{item['obligationId']}`: `{item['status']}` via `{item['route']}`")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- obligations: {inventory['summary']['obligationCount']}",
            f"- selected proof linked: {inventory['summary']['selectedProofLinkedCount']}",
            f"- open obligations: {inventory['summary']['openObligationCount']}",
            f"- hardware observed: `{inventory['summary']['hardwareObserved']}`",
            f"- proof claim: `{inventory['summary']['proofClaim']}`",
            "",
            "## Non-Claims",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in inventory["nonClaims"])
    return "\n".join(lines) + "\n"


def build_outputs(
    out_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
) -> dict[str, str]:
    inventory = build_inventory()
    validate_inventory(inventory)
    evidence = build_evidence(inventory)
    feed = build_feed(inventory)
    result_path = out_dir / f"ee_guard_a1_electronics_guard_obligation_inventory_{STAMP}.json"
    report_path = report_dir / f"ee_guard_a1_electronics_guard_obligation_inventory_{STAMP}.md"
    evidence_path = evidence_dir / "ee_guard_a1_electronics_guard_obligation_inventory.json"
    feed_path = command_feed_dir / f"ee_guard_a1_electronics_guard_obligation_inventory_feed_{STAMP}.json"
    write_json(result_path, inventory)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(inventory), encoding="utf-8")
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/ee_guard_a1_electronics_guard_obligation_inventory")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    inventory = build_inventory()
    validate_inventory(inventory)
    if args.build:
        build_outputs(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    print("EE_GUARD_A1_ELECTRONICS_GUARD_OBLIGATION_INVENTORY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
