#!/usr/bin/env python3
"""GB-VIS-A7 private adapter smoke fixture packet."""

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

from scripts import gb_vis_a6_private_renderer_adapter_contract as a6  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_adapter_smoke_fixture.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "GB_VIS_A7_PRIVATE_ADAPTER_SMOKE_FIXTURE_PASS"

CLAIM_FLAGS = {
    "private_adapter_smoke_fixture_recorded": True,
    "gb_vis_a6_adapter_contract_consumed": True,
    "adapter_smoke_rows_recorded": True,
    "adapter_smoke_checks_recorded": True,
    "adapter_smoke_checks_passed": True,
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
    "GB-VIS-A7 records a private adapter smoke fixture only; it does not implement, execute, or pixel-render a renderer.",
    "GB-VIS-A7 derives deterministic smoke rows from GB-VIS-A6 adapter inputs without proving visualization correctness, renderer soundness, validator soundness, a Galois connection, abstract interpretation correctness, compiler correctness, formal equivalence, or full EML semantics.",
    "GB-VIS-A7 does not update public surfaces, runtime behavior, MachLib, production validators, laptop-owned repos, or electronics repos.",
]


def smoke_row(adapter: dict[str, Any]) -> dict[str, Any]:
    return {
        "smokeRowId": f"gb_vis_a7_smoke:{adapter['adapterInputId']}",
        "sourceAdapterInput": adapter["adapterInputId"],
        "sourceRowType": adapter["sourceRowType"],
        "rendererLayer": adapter["rendererLayer"],
        "renderIntent": adapter["renderIntent"],
        "requiredGuardCount": len(adapter["requiredGuards"]),
        "requiredGuards": list(adapter["requiredGuards"]),
        "publicStatus": adapter["publicStatus"],
        "smokeStatus": "pass",
        "rendererExecuted": False,
        "pixelRendered": False,
    }


def build_smoke_rows(adapter_inputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [smoke_row(adapter) for adapter in adapter_inputs]


def smoke_checks(source: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    structure_rows = [row for row in rows if row["rendererLayer"] == "structure"]
    overlay_rows = [row for row in rows if row["rendererLayer"] == "guard_overlay"]
    checks = [
        {
            "checkId": "source_adapter_contract_is_gb_vis_a6",
            "status": "pass",
            "observed": source["artifactId"],
            "expected": "gb-vis-a6-private-renderer-adapter-contract",
        },
        {
            "checkId": "smoke_rows_match_adapter_inputs",
            "status": "pass",
            "observed": len(rows),
            "expected": source["summary"]["adapterInputCount"],
        },
        {
            "checkId": "structure_smoke_row_present",
            "status": "pass",
            "observed": len(structure_rows),
            "expected": 1,
        },
        {
            "checkId": "guard_overlay_smoke_rows_present",
            "status": "pass",
            "observed": len(overlay_rows),
            "expected": 5,
        },
        {
            "checkId": "all_smoke_rows_remain_private",
            "status": "pass",
            "observed": sorted({row["publicStatus"] for row in rows}),
            "expected": ["held_private"],
        },
        {
            "checkId": "all_smoke_rows_keep_no_public_surface_guard",
            "status": "pass",
            "observed": all("no_public_surface" in row["requiredGuards"] for row in rows),
            "expected": True,
        },
        {
            "checkId": "no_renderer_execution_or_pixels",
            "status": "pass",
            "observed": {
                "rendererExecuted": any(row["rendererExecuted"] for row in rows),
                "pixelRendered": any(row["pixelRendered"] for row in rows),
            },
            "expected": {
                "rendererExecuted": False,
                "pixelRendered": False,
            },
        },
    ]
    for check in checks:
        if check["observed"] != check["expected"]:
            raise ValueError(f"smoke check failed: {check['checkId']}")
    return checks


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a6.build_payload(atlas_gate_path)
    a6.validate_payload(source)
    rows = build_smoke_rows(source["adapterInputs"])
    checks = smoke_checks(source, rows)
    summary = {
        "sourceAdapterContract": source["artifactId"],
        "sourceAdapterInputCount": source["summary"]["adapterInputCount"],
        "adapterSmokeRowCount": len(rows),
        "structureSmokeRowCount": sum(1 for row in rows if row["rendererLayer"] == "structure"),
        "guardOverlaySmokeRowCount": sum(1 for row in rows if row["rendererLayer"] == "guard_overlay"),
        "adapterSmokeCheckCount": len(checks),
        "adapterSmokeCheckPassCount": sum(1 for check in checks if check["status"] == "pass"),
        "privateAdapterSmokeFixtureRecorded": True,
        "gbVisA6AdapterContractConsumed": True,
        "adapterSmokeRowsRecorded": True,
        "adapterSmokeChecksRecorded": True,
        "adapterSmokeChecksPassed": True,
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
        "nextAction": "ACT-A8 reviewer report snapshot or GB-VIS-A8 private adapter snapshot comparison without public promotion.",
        "claimFlagsBounded": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "private_adapter_smoke_fixture_recorded",
                "gb_vis_a6_adapter_contract_consumed",
                "adapter_smoke_rows_recorded",
                "adapter_smoke_checks_recorded",
                "adapter_smoke_checks_passed",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "private_adapter_smoke_fixture_recorded",
                "gb_vis_a6_adapter_contract_consumed",
                "adapter_smoke_rows_recorded",
                "adapter_smoke_checks_recorded",
                "adapter_smoke_checks_passed",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "private_adapter_smoke_fixture_v0",
        "artifactId": "gb-vis-a7-private-adapter-smoke-fixture",
        "status": STATUS,
        "decision": "record_private_adapter_smoke_fixture_no_renderer_execution_no_public_promotion",
        "date": DATE,
        "sourceAdapterContract": source["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "adapterSmokeRows": rows,
        "adapterSmokeChecks": checks,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceAdapterContract"] != "gb-vis-a6-private-renderer-adapter-contract":
        raise ValueError("GB-VIS-A7 must consume GB-VIS-A6")
    if summary["sourceAdapterInputCount"] != 6 or summary["adapterSmokeRowCount"] != 6:
        raise ValueError("unexpected smoke row count")
    if summary["structureSmokeRowCount"] != 1:
        raise ValueError("unexpected structure smoke row count")
    if summary["guardOverlaySmokeRowCount"] != 5:
        raise ValueError("unexpected overlay smoke row count")
    if summary["adapterSmokeCheckCount"] != 7 or summary["adapterSmokeCheckPassCount"] != 7:
        raise ValueError("unexpected smoke check count")
    for row in payload["adapterSmokeRows"]:
        if row["publicStatus"] != "held_private":
            raise ValueError("smoke row public status drift")
        if row["smokeStatus"] != "pass":
            raise ValueError("smoke row must pass")
        if row["rendererExecuted"] is not False or row["pixelRendered"] is not False:
            raise ValueError("smoke row must not execute or render pixels")
        if "no_public_surface" not in row["requiredGuards"]:
            raise ValueError("smoke row missing public guard")
    for check in payload["adapterSmokeChecks"]:
        if check["status"] != "pass" or check["observed"] != check["expected"]:
            raise ValueError("adapter smoke check must pass exactly")
    for key in [
        "privateAdapterSmokeFixtureRecorded",
        "gbVisA6AdapterContractConsumed",
        "adapterSmokeRowsRecorded",
        "adapterSmokeChecksRecorded",
        "adapterSmokeChecksPassed",
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
        "artifactType": "private_adapter_smoke_fixture",
        "validationStatus": "pass",
        "semanticStrength": "private_adapter_smoke_fixture_no_renderer_execution_no_public_update",
        "source": f"python/results/gb_vis_a7_private_adapter_smoke_fixture/gb_vis_a7_private_adapter_smoke_fixture_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "gb_vis_a7_private_adapter_smoke_fixture_feed",
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
        "# GB-VIS-A7 Private Adapter Smoke Fixture",
        "",
        f"Status: `{payload['status']}`",
        "",
        "GB-VIS-A7 records private adapter smoke rows without implementing or executing a renderer.",
        "",
        "| Count | Value |",
        "|---|---|",
        f"| smoke rows | `{payload['summary']['adapterSmokeRowCount']}` |",
        f"| guard overlays | `{payload['summary']['guardOverlaySmokeRowCount']}` |",
        f"| smoke checks | `{payload['summary']['adapterSmokeCheckCount']}` |",
        f"| smoke passes | `{payload['summary']['adapterSmokeCheckPassCount']}` |",
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
    result_path = out_dir / f"gb_vis_a7_private_adapter_smoke_fixture_{STAMP}.json"
    report_path = report_dir / f"gb_vis_a7_private_adapter_smoke_fixture_{STAMP}.md"
    evidence_path = evidence_dir / "gb_vis_a7_private_adapter_smoke_fixture.json"
    feed_path = command_feed_dir / f"gb_vis_a7_private_adapter_smoke_fixture_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/gb_vis_a7_private_adapter_smoke_fixture")
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
    print("GB_VIS_A7_PRIVATE_ADAPTER_SMOKE_FIXTURE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
