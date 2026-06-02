#!/usr/bin/env python3
"""GB-VIS-A5 private renderer integration gate packet."""

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

from scripts import act_a5_negative_rejection_fixtures as act_a5  # noqa: E402
from scripts import gb_vis_a4_snapshot_comparison_fixture as gb_a4  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_renderer_integration_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "GB_VIS_A5_PRIVATE_RENDERER_INTEGRATION_GATE_PASS"

CLAIM_FLAGS = {
    "private_renderer_integration_gate_recorded": True,
    "gb_vis_a4_snapshot_consumed": True,
    "act_a5_rejection_fixtures_consumed": True,
    "integration_rows_recorded": True,
    "integration_gate_checks_recorded": True,
    "integration_gate_checks_passed": True,
    "renderer_input_contract_recorded": True,
    "pixel_renderer_implemented": False,
    "renderer_implemented": False,
    "interactive_renderer_implemented": False,
    "renderer_executed": False,
    "visualization_started": False,
    "visualization_rendered": False,
    "visual_correctness_proved": False,
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
    "GB-VIS-A5 records a private renderer integration gate only; it does not implement, execute, or pixel-render a renderer.",
    "GB-VIS-A5 connects GB-VIS-A4 command snapshots to ACT-A5 rejection fixtures as private renderer inputs without proving visualization correctness, validator soundness, a Galois connection, abstract interpretation correctness, compiler correctness, formal equivalence, or full EML semantics.",
    "GB-VIS-A5 does not update public surfaces, runtime behavior, MachLib, production validators, laptop-owned repos, or electronics repos.",
]


def build_integration_rows(snapshot: dict[str, Any], rejection_packet: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        {
            "rowId": "gb_vis_a5_snapshot_structure_layer",
            "rowType": "structure_layer",
            "sourcePacket": "gb-vis-a4-snapshot-comparison-fixture",
            "sourceSnapshot": snapshot["snapshotId"],
            "nodeCommandCount": snapshot["nodeCommandCount"],
            "edgeCommandCount": snapshot["edgeCommandCount"],
            "legendCommandCount": snapshot["legendCommandCount"],
            "digestFields": [
                "nodeDigest",
                "edgeDigest",
                "legendDigest",
                "smokeCheckDigest",
                "guardrailDigest",
                "viewportDigest",
            ],
            "rendererInputStatus": "private_input_contract_only",
        }
    ]
    for fixture in rejection_packet["negativeFixtures"]:
        rows.append(
            {
                "rowId": f"gb_vis_a5_rejection_overlay:{fixture['failureMode']}",
                "rowType": "rejection_overlay",
                "sourcePacket": "act-a5-negative-rejection-fixtures",
                "sourceFixture": fixture["fixtureId"],
                "failureMode": fixture["failureMode"],
                "expectedStatus": fixture["expectedStatus"],
                "sourceObligation": fixture["sourceObligation"],
                "overlayBadge": f"expected_reject:{fixture['failureMode']}",
                "rendererInputStatus": "private_input_contract_only",
            }
        )
    return rows


def integration_checks(snapshot_packet: dict[str, Any], rejection_packet: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    overlay_rows = [row for row in rows if row["rowType"] == "rejection_overlay"]
    required_modes = {
        "claim_escalation",
        "trace_gap",
        "public_gate_bypass",
        "runtime_drift",
        "lane_owner_drift",
    }
    checks = [
        {
            "checkId": "snapshot_source_is_gb_vis_a4",
            "status": "pass",
            "observed": snapshot_packet["artifactId"],
            "expected": "gb-vis-a4-snapshot-comparison-fixture",
        },
        {
            "checkId": "rejection_source_is_act_a5",
            "status": "pass",
            "observed": rejection_packet["artifactId"],
            "expected": "act-a5-negative-rejection-fixtures",
        },
        {
            "checkId": "snapshot_comparison_still_passes",
            "status": "pass",
            "observed": snapshot_packet["summary"]["comparisonPassCount"],
            "expected": snapshot_packet["summary"]["comparisonCheckCount"],
        },
        {
            "checkId": "rejection_modes_have_overlay_rows",
            "status": "pass",
            "observed": sorted(row["failureMode"] for row in overlay_rows),
            "expected": sorted(required_modes),
        },
        {
            "checkId": "overlay_rows_remain_expected_reject",
            "status": "pass",
            "observed": sorted(row["expectedStatus"] for row in overlay_rows),
            "expected": ["reject"] * len(required_modes),
        },
        {
            "checkId": "private_renderer_input_status_only",
            "status": "pass",
            "observed": sorted({row["rendererInputStatus"] for row in rows}),
            "expected": ["private_input_contract_only"],
        },
        {
            "checkId": "no_unexpected_accepts_from_act_a5",
            "status": "pass",
            "observed": rejection_packet["summary"]["unexpectedAcceptCount"],
            "expected": 0,
        },
        {
            "checkId": "renderer_execution_claims_remain_false",
            "status": "pass",
            "observed": {
                "rendererImplemented": False,
                "rendererExecuted": False,
                "visualizationRendered": False,
                "publicReady": False,
            },
            "expected": {
                "rendererImplemented": False,
                "rendererExecuted": False,
                "visualizationRendered": False,
                "publicReady": False,
            },
        },
    ]
    for check in checks:
        if check["observed"] != check["expected"]:
            raise ValueError(f"integration check failed: {check['checkId']}")
    return checks


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    snapshot_packet = gb_a4.build_payload(atlas_gate_path)
    gb_a4.validate_payload(snapshot_packet)
    rejection_packet = act_a5.build_payload(atlas_gate_path)
    act_a5.validate_payload(rejection_packet)
    rows = build_integration_rows(snapshot_packet["observedSnapshot"], rejection_packet)
    checks = integration_checks(snapshot_packet, rejection_packet, rows)
    summary = {
        "sourceSnapshotPacket": snapshot_packet["artifactId"],
        "sourceRejectionPacket": rejection_packet["artifactId"],
        "integrationRowCount": len(rows),
        "structureLayerRowCount": sum(1 for row in rows if row["rowType"] == "structure_layer"),
        "rejectionOverlayRowCount": sum(1 for row in rows if row["rowType"] == "rejection_overlay"),
        "integrationCheckCount": len(checks),
        "integrationCheckPassCount": sum(1 for check in checks if check["status"] == "pass"),
        "snapshotNodeCommandCount": snapshot_packet["summary"]["nodeCommandCount"],
        "snapshotEdgeCommandCount": snapshot_packet["summary"]["edgeCommandCount"],
        "snapshotComparisonPassCount": snapshot_packet["summary"]["comparisonPassCount"],
        "rejectionFailureModeCount": len(rejection_packet["summary"]["failureModesCovered"]),
        "unexpectedAcceptCount": rejection_packet["summary"]["unexpectedAcceptCount"],
        "privateRendererIntegrationGateRecorded": True,
        "gbVisA4SnapshotConsumed": True,
        "actA5RejectionFixturesConsumed": True,
        "integrationRowsRecorded": True,
        "integrationGateChecksRecorded": True,
        "integrationGateChecksPassed": True,
        "rendererInputContractRecorded": True,
        "pixelRendererImplemented": False,
        "rendererImplemented": False,
        "interactiveRendererImplemented": False,
        "rendererExecuted": False,
        "visualizationStarted": False,
        "visualizationRendered": False,
        "visualCorrectnessProved": False,
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
        "nextAction": "ACT-A6 rejection fixture hardening or GB-VIS-A6 private renderer adapter contract without public promotion.",
        "claimFlagsBounded": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "private_renderer_integration_gate_recorded",
                "gb_vis_a4_snapshot_consumed",
                "act_a5_rejection_fixtures_consumed",
                "integration_rows_recorded",
                "integration_gate_checks_recorded",
                "integration_gate_checks_passed",
                "renderer_input_contract_recorded",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "private_renderer_integration_gate_recorded",
                "gb_vis_a4_snapshot_consumed",
                "act_a5_rejection_fixtures_consumed",
                "integration_rows_recorded",
                "integration_gate_checks_recorded",
                "integration_gate_checks_passed",
                "renderer_input_contract_recorded",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "private_renderer_integration_gate_v0",
        "artifactId": "gb-vis-a5-private-renderer-integration-gate",
        "status": STATUS,
        "decision": "record_private_renderer_integration_gate_no_renderer_execution_no_public_promotion",
        "date": DATE,
        "sourceSnapshotPacket": snapshot_packet["artifactId"],
        "sourceRejectionPacket": rejection_packet["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "integrationRows": rows,
        "integrationChecks": checks,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceSnapshotPacket"] != "gb-vis-a4-snapshot-comparison-fixture":
        raise ValueError("GB-VIS-A5 must consume GB-VIS-A4")
    if payload["sourceRejectionPacket"] != "act-a5-negative-rejection-fixtures":
        raise ValueError("GB-VIS-A5 must consume ACT-A5")
    if summary["integrationRowCount"] != 6:
        raise ValueError("unexpected integration row count")
    if summary["structureLayerRowCount"] != 1:
        raise ValueError("unexpected structure layer row count")
    if summary["rejectionOverlayRowCount"] != 5:
        raise ValueError("unexpected rejection overlay row count")
    if summary["integrationCheckCount"] != 8 or summary["integrationCheckPassCount"] != 8:
        raise ValueError("unexpected integration check count")
    if summary["snapshotNodeCommandCount"] != 23 or summary["snapshotEdgeCommandCount"] != 16:
        raise ValueError("snapshot command count drift")
    if summary["snapshotComparisonPassCount"] != 6:
        raise ValueError("snapshot comparison pass count drift")
    if summary["rejectionFailureModeCount"] != 5 or summary["unexpectedAcceptCount"] != 0:
        raise ValueError("rejection fixture summary drift")
    for row in payload["integrationRows"]:
        if row["rendererInputStatus"] != "private_input_contract_only":
            raise ValueError("renderer input status drift")
    for check in payload["integrationChecks"]:
        if check["status"] != "pass" or check["observed"] != check["expected"]:
            raise ValueError("integration check must pass exactly")
    for key in [
        "privateRendererIntegrationGateRecorded",
        "gbVisA4SnapshotConsumed",
        "actA5RejectionFixturesConsumed",
        "integrationRowsRecorded",
        "integrationGateChecksRecorded",
        "integrationGateChecksPassed",
        "rendererInputContractRecorded",
    ]:
        if summary[key] is not True:
            raise ValueError(f"{key} must be true")
    for key in [
        "pixelRendererImplemented",
        "rendererImplemented",
        "interactiveRendererImplemented",
        "rendererExecuted",
        "visualizationStarted",
        "visualizationRendered",
        "visualCorrectnessProved",
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
        "artifactType": "private_renderer_integration_gate",
        "validationStatus": "pass",
        "semanticStrength": "private_renderer_integration_gate_no_renderer_execution_no_public_update",
        "source": f"python/results/gb_vis_a5_private_renderer_integration_gate/gb_vis_a5_private_renderer_integration_gate_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "gb_vis_a5_private_renderer_integration_gate_feed",
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
        "# GB-VIS-A5 Private Renderer Integration Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "GB-VIS-A5 records a private renderer input integration gate without implementing or executing a renderer.",
        "",
        "| Count | Value |",
        "|---|---|",
        f"| integration rows | `{payload['summary']['integrationRowCount']}` |",
        f"| rejection overlays | `{payload['summary']['rejectionOverlayRowCount']}` |",
        f"| integration checks | `{payload['summary']['integrationCheckCount']}` |",
        f"| integration passes | `{payload['summary']['integrationCheckPassCount']}` |",
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
    result_path = out_dir / f"gb_vis_a5_private_renderer_integration_gate_{STAMP}.json"
    report_path = report_dir / f"gb_vis_a5_private_renderer_integration_gate_{STAMP}.md"
    evidence_path = evidence_dir / "gb_vis_a5_private_renderer_integration_gate.json"
    feed_path = command_feed_dir / f"gb_vis_a5_private_renderer_integration_gate_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/gb_vis_a5_private_renderer_integration_gate")
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
    print("GB_VIS_A5_PRIVATE_RENDERER_INTEGRATION_GATE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
