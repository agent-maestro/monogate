#!/usr/bin/env python3
"""GB-VIS-A13 private adapter promotion hold gate packet."""

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

from scripts import gb_vis_a12_private_adapter_intake_feed_guard as a12  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_adapter_promotion_hold_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "GB_VIS_A13_PRIVATE_ADAPTER_PROMOTION_HOLD_GATE_PASS"

REQUIRED_HELD_GATES = {
    "private_reviewer_decision": "not_recorded",
    "concrete_adapter_artifact_acceptance": "blocked_no_laptop_artifact",
    "renderer_implementation": "blocked_not_implemented",
    "renderer_execution": "blocked_not_executed",
    "pixel_renderer_execution": "blocked_not_rendered",
    "visual_correctness": "blocked_not_proved",
    "renderer_soundness": "blocked_not_proved",
    "public_copy_approval": "blocked_not_approved",
    "public_surface_update": "blocked_not_updated",
}

CLAIM_FLAGS = {
    "private_adapter_promotion_hold_gate_recorded": True,
    "gb_vis_a12_adapter_intake_feed_guard_consumed": True,
    "source_feed_rebuilt": True,
    "promotion_hold_gates_recorded": True,
    "promotion_hold_checks_recorded": True,
    "promotion_hold_checks_passed": True,
    "reviewer_decision_recorded": False,
    "concrete_adapter_artifact_accepted": False,
    "pixel_renderer_implemented": False,
    "renderer_implemented": False,
    "interactive_renderer_implemented": False,
    "renderer_executed": False,
    "visualization_started": False,
    "visualization_rendered": False,
    "visual_correctness_proved": False,
    "renderer_soundness_proved": False,
    "public_surface_updated": False,
    "public_copy_approved": False,
    "runtime_lowering_changed": False,
    "production_validator_implemented": False,
    "validator_soundness_proved": False,
    "soundness_proved": False,
    "full_galois_connection_claim": False,
    "abstract_interpretation_soundness_proved": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "proof_attempt_started": False,
    "candidate_proved": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "full_eml_semantics_claim": False,
    "theorem_discovery_claim": False,
    "general_eml_superiority_claim": False,
    "runtime_performance_claim": False,
    "electronics_repo_touched": False,
    "laptop_artifact_consumed": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "GB-VIS-A13 records a private adapter promotion hold gate only; it does not promote adapter artifacts.",
    "GB-VIS-A13 consumes GB-VIS-A12 without accepting laptop artifacts, implementing or executing a renderer, pixel-rendering output, proving visualization correctness, proving renderer soundness, or approving public copy.",
    "GB-VIS-A13 does not update public surfaces, runtime behavior, MachLib, production validators, laptop-owned repos, electronics repos, or course artifacts.",
]

BLOCKED_STATEMENTS = [
    "A reviewer has accepted a private adapter artifact for promotion.",
    "The private adapter renderer is implemented.",
    "The private adapter renderer has executed.",
    "A pixel-rendered visualization has been produced.",
    "Visualization correctness or renderer soundness has been proved.",
    "GB-VIS artifacts are public-ready.",
    "Laptop or electronics artifacts have been consumed by this gate.",
]


def promotion_hold_gates(source_feed: dict[str, Any]) -> list[dict[str, Any]]:
    gates = [
        {
            "gateId": gate_id,
            "status": status,
            "promotionAllowed": False,
        }
        for gate_id, status in REQUIRED_HELD_GATES.items()
    ]
    gates.append(
        {
            "gateId": "source_next_action_private",
            "status": "held_private",
            "observed": "without public promotion" in source_feed["nextAction"],
            "expected": True,
            "promotionAllowed": False,
        }
    )
    return gates


def promotion_hold_checks(gates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    checks = [
        {
            "checkId": f"{gate['gateId']}_held",
            "observed": gate["promotionAllowed"],
            "expected": False,
            "status": "pass",
        }
        for gate in gates
    ]
    for check in checks:
        if check["observed"] != check["expected"]:
            raise ValueError(f"adapter promotion hold check failed: {check['checkId']}")
    return checks


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a12.build_payload(atlas_gate_path)
    a12.validate_payload(source)
    source_feed = a12.build_feed(source)
    gates = promotion_hold_gates(source_feed)
    checks = promotion_hold_checks(gates)
    summary = {
        "sourceAdapterIntakeFeedGuard": source["artifactId"],
        "sourceFeedId": source_feed["feedId"],
        "sourceFeedStatus": source_feed["status"],
        "sourceFeedDecision": source_feed["decision"],
        "sourceFeedNextAction": source_feed["nextAction"],
        "promotionHoldGateCount": len(gates),
        "promotionHoldCheckCount": len(checks),
        "promotionHoldPassCount": sum(1 for check in checks if check["status"] == "pass"),
        "blockedStatementCount": len(BLOCKED_STATEMENTS),
        "privateAdapterPromotionHoldGateRecorded": True,
        "gbVisA12AdapterIntakeFeedGuardConsumed": True,
        "sourceFeedRebuilt": True,
        "promotionHoldGatesRecorded": True,
        "promotionHoldChecksRecorded": True,
        "promotionHoldChecksPassed": True,
        "promotionAllowed": False,
        "reviewerDecisionRecorded": False,
        "concreteAdapterArtifactAccepted": False,
        "pixelRendererImplemented": False,
        "rendererImplemented": False,
        "interactiveRendererImplemented": False,
        "rendererExecuted": False,
        "visualizationStarted": False,
        "visualizationRendered": False,
        "visualCorrectnessProved": False,
        "rendererSoundnessProved": False,
        "publicCopyApproved": False,
        "publicSurfaceUpdated": False,
        "runtimeLoweringChanged": False,
        "productionValidatorImplemented": False,
        "validatorSoundnessProved": False,
        "soundnessProved": False,
        "fullGaloisConnectionClaim": False,
        "abstractInterpretationSoundnessProved": False,
        "machlibFileChanged": False,
        "leanTypecheckPerformed": False,
        "proofAttemptStarted": False,
        "electronicsRepoTouched": False,
        "laptopArtifactConsumed": False,
        "publicReady": False,
        "nextAction": "EML-D63 post-pause selector or ACT-A14 reviewer promotion hold snapshot without public promotion.",
        "claimFlagsBounded": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "private_adapter_promotion_hold_gate_recorded",
                "gb_vis_a12_adapter_intake_feed_guard_consumed",
                "source_feed_rebuilt",
                "promotion_hold_gates_recorded",
                "promotion_hold_checks_recorded",
                "promotion_hold_checks_passed",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "private_adapter_promotion_hold_gate_recorded",
                "gb_vis_a12_adapter_intake_feed_guard_consumed",
                "source_feed_rebuilt",
                "promotion_hold_gates_recorded",
                "promotion_hold_checks_recorded",
                "promotion_hold_checks_passed",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "private_adapter_promotion_hold_gate_v0",
        "artifactId": "gb-vis-a13-private-adapter-promotion-hold-gate",
        "status": STATUS,
        "decision": "hold_private_adapter_promotion_no_renderer_execution_no_public_promotion",
        "date": DATE,
        "sourceAdapterIntakeFeedGuard": source["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "sourceFeed": source_feed,
        "promotionHoldGates": gates,
        "promotionHoldChecks": checks,
        "blockedStatements": list(BLOCKED_STATEMENTS),
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceAdapterIntakeFeedGuard"] != "gb-vis-a12-private-adapter-intake-feed-guard":
        raise ValueError("GB-VIS-A13 must consume GB-VIS-A12")
    if summary["sourceFeedId"] != "gb_vis_a12_private_adapter_intake_feed_guard_feed":
        raise ValueError("unexpected source feed id")
    if summary["sourceFeedStatus"] != "GB_VIS_A12_PRIVATE_ADAPTER_INTAKE_FEED_GUARD_PASS":
        raise ValueError("unexpected source feed status")
    if summary["promotionHoldGateCount"] != 10:
        raise ValueError("unexpected promotion hold gate count")
    if summary["promotionHoldCheckCount"] != 10 or summary["promotionHoldPassCount"] != 10:
        raise ValueError("unexpected promotion hold check count")
    if summary["blockedStatementCount"] != len(BLOCKED_STATEMENTS):
        raise ValueError("unexpected blocked statement count")
    if summary["promotionAllowed"] is not False:
        raise ValueError("promotion must remain held")
    for check in payload["promotionHoldChecks"]:
        if check["status"] != "pass" or check["observed"] != check["expected"]:
            raise ValueError("adapter promotion hold check must pass exactly")
    for key in [
        "privateAdapterPromotionHoldGateRecorded",
        "gbVisA12AdapterIntakeFeedGuardConsumed",
        "sourceFeedRebuilt",
        "promotionHoldGatesRecorded",
        "promotionHoldChecksRecorded",
        "promotionHoldChecksPassed",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "reviewerDecisionRecorded",
        "concreteAdapterArtifactAccepted",
        "pixelRendererImplemented",
        "rendererImplemented",
        "interactiveRendererImplemented",
        "rendererExecuted",
        "visualizationStarted",
        "visualizationRendered",
        "visualCorrectnessProved",
        "rendererSoundnessProved",
        "publicCopyApproved",
        "publicSurfaceUpdated",
        "runtimeLoweringChanged",
        "productionValidatorImplemented",
        "validatorSoundnessProved",
        "soundnessProved",
        "fullGaloisConnectionClaim",
        "abstractInterpretationSoundnessProved",
        "machlibFileChanged",
        "leanTypecheckPerformed",
        "proofAttemptStarted",
        "electronicsRepoTouched",
        "laptopArtifactConsumed",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsBounded"] is not True:
        raise ValueError("claim flags must remain bounded")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "private_adapter_promotion_hold_gate",
        "validationStatus": "pass",
        "semanticStrength": "private_adapter_promotion_hold_gate_no_renderer_execution_no_public_update",
        "source": f"python/results/gb_vis_a13_private_adapter_promotion_hold_gate/gb_vis_a13_private_adapter_promotion_hold_gate_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "gb_vis_a13_private_adapter_promotion_hold_gate_feed",
        "date": DATE,
        "status": payload["status"],
        "decision": payload["decision"],
        "nextAction": payload["summary"]["nextAction"],
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# GB-VIS-A13 Private Adapter Promotion Hold Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "GB-VIS-A13 records a private adapter promotion hold gate without renderer execution or public promotion.",
        "",
        "| Count | Value |",
        "|---|---|",
        f"| promotion hold gates | `{payload['summary']['promotionHoldGateCount']}` |",
        f"| promotion hold checks | `{payload['summary']['promotionHoldCheckCount']}` |",
        f"| promotion hold passes | `{payload['summary']['promotionHoldPassCount']}` |",
        f"| blocked statements | `{payload['summary']['blockedStatementCount']}` |",
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
    result_path = out_dir / f"gb_vis_a13_private_adapter_promotion_hold_gate_{STAMP}.json"
    report_path = report_dir / f"gb_vis_a13_private_adapter_promotion_hold_gate_{STAMP}.md"
    evidence_path = evidence_dir / "gb_vis_a13_private_adapter_promotion_hold_gate.json"
    feed_path = command_feed_dir / f"gb_vis_a13_private_adapter_promotion_hold_gate_feed_{STAMP}.json"
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
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--atlas-gate-path", type=Path, default=ROOT / "python/results/eml_atlas_promotion_gate/eml_atlas_promotion_gate_2026_05_27.json")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/gb_vis_a13_private_adapter_promotion_hold_gate")
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
    print("GB_VIS_A13_PRIVATE_ADAPTER_PROMOTION_HOLD_GATE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
