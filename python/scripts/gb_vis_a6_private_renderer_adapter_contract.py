#!/usr/bin/env python3
"""GB-VIS-A6 private renderer adapter contract packet."""

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

from scripts import gb_vis_a5_private_renderer_integration_gate as a5  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_renderer_adapter_contract.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "GB_VIS_A6_PRIVATE_RENDERER_ADAPTER_CONTRACT_PASS"

ADAPTER_FIELDS = [
    "adapterInputId",
    "sourceRowId",
    "sourceRowType",
    "sourcePacket",
    "rendererLayer",
    "renderIntent",
    "requiredGuards",
    "publicStatus",
]

CLAIM_FLAGS = {
    "private_renderer_adapter_contract_recorded": True,
    "gb_vis_a5_integration_gate_consumed": True,
    "adapter_inputs_recorded": True,
    "adapter_fields_recorded": True,
    "adapter_guard_checks_recorded": True,
    "adapter_guard_checks_passed": True,
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
    "GB-VIS-A6 records a private renderer adapter contract only; it does not implement, execute, or pixel-render a renderer.",
    "GB-VIS-A6 maps GB-VIS-A5 integration rows into private adapter inputs without proving visualization correctness, renderer soundness, validator soundness, a Galois connection, abstract interpretation correctness, compiler correctness, formal equivalence, or full EML semantics.",
    "GB-VIS-A6 does not update public surfaces, runtime behavior, MachLib, production validators, laptop-owned repos, or electronics repos.",
]


def adapter_input(row: dict[str, Any]) -> dict[str, Any]:
    if row["rowType"] == "structure_layer":
        return {
            "adapterInputId": "gb_vis_a6_adapter_input:structure_layer",
            "sourceRowId": row["rowId"],
            "sourceRowType": row["rowType"],
            "sourcePacket": row["sourcePacket"],
            "rendererLayer": "structure",
            "renderIntent": "layout_command_snapshot",
            "requiredGuards": ["private_input_contract_only", "stable_snapshot_digest", "no_public_surface"],
            "publicStatus": "held_private",
        }
    return {
        "adapterInputId": f"gb_vis_a6_adapter_input:rejection_overlay:{row['failureMode']}",
        "sourceRowId": row["rowId"],
        "sourceRowType": row["rowType"],
        "sourcePacket": row["sourcePacket"],
        "rendererLayer": "guard_overlay",
        "renderIntent": f"show_expected_reject:{row['failureMode']}",
        "requiredGuards": ["private_input_contract_only", "expected_reject_overlay", "no_public_surface"],
        "publicStatus": "held_private",
        "failureMode": row["failureMode"],
        "overlayBadge": row["overlayBadge"],
    }


def build_adapter_inputs(integration_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [adapter_input(row) for row in integration_rows]


def adapter_checks(source: dict[str, Any], inputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    structure_inputs = [item for item in inputs if item["rendererLayer"] == "structure"]
    overlay_inputs = [item for item in inputs if item["rendererLayer"] == "guard_overlay"]
    required_modes = {
        "claim_escalation",
        "trace_gap",
        "public_gate_bypass",
        "runtime_drift",
        "lane_owner_drift",
    }
    checks = [
        {
            "checkId": "source_integration_gate_is_gb_vis_a5",
            "status": "pass",
            "observed": source["artifactId"],
            "expected": "gb-vis-a5-private-renderer-integration-gate",
        },
        {
            "checkId": "adapter_input_count_matches_integration_rows",
            "status": "pass",
            "observed": len(inputs),
            "expected": source["summary"]["integrationRowCount"],
        },
        {
            "checkId": "structure_layer_adapter_input_present",
            "status": "pass",
            "observed": len(structure_inputs),
            "expected": 1,
        },
        {
            "checkId": "rejection_overlay_adapter_inputs_present",
            "status": "pass",
            "observed": sorted(item["failureMode"] for item in overlay_inputs),
            "expected": sorted(required_modes),
        },
        {
            "checkId": "adapter_fields_are_complete",
            "status": "pass",
            "observed": sorted({field for item in inputs for field in ADAPTER_FIELDS if field in item}),
            "expected": sorted(ADAPTER_FIELDS),
        },
        {
            "checkId": "all_inputs_remain_private",
            "status": "pass",
            "observed": sorted({item["publicStatus"] for item in inputs}),
            "expected": ["held_private"],
        },
        {
            "checkId": "all_inputs_carry_no_public_surface_guard",
            "status": "pass",
            "observed": all("no_public_surface" in item["requiredGuards"] for item in inputs),
            "expected": True,
        },
        {
            "checkId": "renderer_implementation_claims_remain_false",
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
            raise ValueError(f"adapter check failed: {check['checkId']}")
    return checks


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a5.build_payload(atlas_gate_path)
    a5.validate_payload(source)
    inputs = build_adapter_inputs(source["integrationRows"])
    checks = adapter_checks(source, inputs)
    summary = {
        "sourceIntegrationGate": source["artifactId"],
        "sourceIntegrationRowCount": source["summary"]["integrationRowCount"],
        "adapterInputCount": len(inputs),
        "structureAdapterInputCount": sum(1 for item in inputs if item["rendererLayer"] == "structure"),
        "guardOverlayAdapterInputCount": sum(1 for item in inputs if item["rendererLayer"] == "guard_overlay"),
        "adapterFieldCount": len(ADAPTER_FIELDS),
        "adapterGuardCheckCount": len(checks),
        "adapterGuardCheckPassCount": sum(1 for check in checks if check["status"] == "pass"),
        "privateRendererAdapterContractRecorded": True,
        "gbVisA5IntegrationGateConsumed": True,
        "adapterInputsRecorded": True,
        "adapterFieldsRecorded": True,
        "adapterGuardChecksRecorded": True,
        "adapterGuardChecksPassed": True,
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
        "nextAction": "ACT-A7 dry-run validator reporting contract or GB-VIS-A7 private adapter smoke fixture without public promotion.",
        "claimFlagsBounded": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "private_renderer_adapter_contract_recorded",
                "gb_vis_a5_integration_gate_consumed",
                "adapter_inputs_recorded",
                "adapter_fields_recorded",
                "adapter_guard_checks_recorded",
                "adapter_guard_checks_passed",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "private_renderer_adapter_contract_recorded",
                "gb_vis_a5_integration_gate_consumed",
                "adapter_inputs_recorded",
                "adapter_fields_recorded",
                "adapter_guard_checks_recorded",
                "adapter_guard_checks_passed",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "private_renderer_adapter_contract_v0",
        "artifactId": "gb-vis-a6-private-renderer-adapter-contract",
        "status": STATUS,
        "decision": "record_private_renderer_adapter_contract_no_renderer_execution_no_public_promotion",
        "date": DATE,
        "sourceIntegrationGate": source["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "adapterFields": list(ADAPTER_FIELDS),
        "adapterInputs": inputs,
        "adapterGuardChecks": checks,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceIntegrationGate"] != "gb-vis-a5-private-renderer-integration-gate":
        raise ValueError("GB-VIS-A6 must consume GB-VIS-A5")
    if summary["sourceIntegrationRowCount"] != 6 or summary["adapterInputCount"] != 6:
        raise ValueError("unexpected adapter input count")
    if summary["structureAdapterInputCount"] != 1:
        raise ValueError("unexpected structure adapter count")
    if summary["guardOverlayAdapterInputCount"] != 5:
        raise ValueError("unexpected guard overlay adapter count")
    if summary["adapterFieldCount"] != len(ADAPTER_FIELDS):
        raise ValueError("adapter field count drift")
    if summary["adapterGuardCheckCount"] != 8 or summary["adapterGuardCheckPassCount"] != 8:
        raise ValueError("unexpected adapter guard check count")
    for item in payload["adapterInputs"]:
        for field in ADAPTER_FIELDS:
            if field not in item:
                raise ValueError(f"adapter input missing field: {field}")
        if item["publicStatus"] != "held_private":
            raise ValueError("adapter input public status drift")
        if "no_public_surface" not in item["requiredGuards"]:
            raise ValueError("adapter input missing public guard")
    for check in payload["adapterGuardChecks"]:
        if check["status"] != "pass" or check["observed"] != check["expected"]:
            raise ValueError("adapter guard check must pass exactly")
    for key in [
        "privateRendererAdapterContractRecorded",
        "gbVisA5IntegrationGateConsumed",
        "adapterInputsRecorded",
        "adapterFieldsRecorded",
        "adapterGuardChecksRecorded",
        "adapterGuardChecksPassed",
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
        "artifactType": "private_renderer_adapter_contract",
        "validationStatus": "pass",
        "semanticStrength": "private_renderer_adapter_contract_no_renderer_execution_no_public_update",
        "source": f"python/results/gb_vis_a6_private_renderer_adapter_contract/gb_vis_a6_private_renderer_adapter_contract_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "gb_vis_a6_private_renderer_adapter_contract_feed",
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
        "# GB-VIS-A6 Private Renderer Adapter Contract",
        "",
        f"Status: `{payload['status']}`",
        "",
        "GB-VIS-A6 records a private renderer adapter contract without implementing or executing a renderer.",
        "",
        "| Count | Value |",
        "|---|---|",
        f"| adapter inputs | `{payload['summary']['adapterInputCount']}` |",
        f"| guard overlays | `{payload['summary']['guardOverlayAdapterInputCount']}` |",
        f"| adapter fields | `{payload['summary']['adapterFieldCount']}` |",
        f"| guard checks | `{payload['summary']['adapterGuardCheckCount']}` |",
        f"| guard passes | `{payload['summary']['adapterGuardCheckPassCount']}` |",
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
    result_path = out_dir / f"gb_vis_a6_private_renderer_adapter_contract_{STAMP}.json"
    report_path = report_dir / f"gb_vis_a6_private_renderer_adapter_contract_{STAMP}.md"
    evidence_path = evidence_dir / "gb_vis_a6_private_renderer_adapter_contract.json"
    feed_path = command_feed_dir / f"gb_vis_a6_private_renderer_adapter_contract_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/gb_vis_a6_private_renderer_adapter_contract")
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
    print("GB_VIS_A6_PRIVATE_RENDERER_ADAPTER_CONTRACT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
