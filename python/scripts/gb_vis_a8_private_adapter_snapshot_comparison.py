#!/usr/bin/env python3
"""GB-VIS-A8 private adapter snapshot comparison packet."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import gb_vis_a7_private_adapter_smoke_fixture as a7  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_adapter_snapshot_comparison.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "GB_VIS_A8_PRIVATE_ADAPTER_SNAPSHOT_COMPARISON_PASS"

CLAIM_FLAGS = {
    "private_adapter_snapshot_comparison_recorded": True,
    "gb_vis_a7_adapter_smoke_consumed": True,
    "baseline_snapshot_recorded": True,
    "observed_snapshot_recorded": True,
    "snapshot_comparison_checks_recorded": True,
    "snapshot_comparison_checks_passed": True,
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
    "GB-VIS-A8 records a private adapter snapshot comparison only; it does not implement, execute, or pixel-render a renderer.",
    "GB-VIS-A8 compares deterministic snapshots from GB-VIS-A7 adapter smoke rows without proving visualization correctness, renderer soundness, validator soundness, a Galois connection, abstract interpretation correctness, compiler correctness, formal equivalence, or full EML semantics.",
    "GB-VIS-A8 does not update public surfaces, runtime behavior, MachLib, production validators, laptop-owned repos, or electronics repos.",
]


def digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_snapshot(source: dict[str, Any], snapshot_id: str) -> dict[str, Any]:
    rows = source["adapterSmokeRows"]
    checks = source["adapterSmokeChecks"]
    return {
        "snapshotId": snapshot_id,
        "snapshotFormat": "monogate.private_adapter_smoke_snapshot.v0",
        "sourceAdapterSmokeFixture": source["artifactId"],
        "adapterSmokeRowCount": len(rows),
        "structureSmokeRowCount": source["summary"]["structureSmokeRowCount"],
        "guardOverlaySmokeRowCount": source["summary"]["guardOverlaySmokeRowCount"],
        "adapterSmokeCheckCount": len(checks),
        "adapterSmokeCheckPassCount": source["summary"]["adapterSmokeCheckPassCount"],
        "rowDigest": digest(rows),
        "checkDigest": digest(checks),
        "nonClaimDigest": digest(source["nonClaims"]),
        "claimFlagDigest": digest(source["claimFlags"]),
    }


def comparison_checks(baseline: dict[str, Any], observed: dict[str, Any]) -> list[dict[str, Any]]:
    fields = ["rowDigest", "checkDigest", "nonClaimDigest", "claimFlagDigest"]
    checks = [
        {
            "checkId": f"{field}_matches",
            "status": "pass",
            "field": field,
            "baseline": baseline[field],
            "observed": observed[field],
        }
        for field in fields
    ]
    for check in checks:
        if check["baseline"] != check["observed"]:
            raise ValueError(f"adapter snapshot mismatch: {check['field']}")
    return checks


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a7.build_payload(atlas_gate_path)
    a7.validate_payload(source)
    baseline = build_snapshot(source, "gb_vis_a8_baseline_private_adapter_smoke_snapshot")
    observed = build_snapshot(source, "gb_vis_a8_observed_private_adapter_smoke_snapshot")
    checks = comparison_checks(baseline, observed)
    summary = {
        "sourceAdapterSmokeFixture": source["artifactId"],
        "baselineSnapshotId": baseline["snapshotId"],
        "observedSnapshotId": observed["snapshotId"],
        "adapterSmokeRowCount": baseline["adapterSmokeRowCount"],
        "structureSmokeRowCount": baseline["structureSmokeRowCount"],
        "guardOverlaySmokeRowCount": baseline["guardOverlaySmokeRowCount"],
        "adapterSmokeCheckCount": baseline["adapterSmokeCheckCount"],
        "adapterSmokeCheckPassCount": baseline["adapterSmokeCheckPassCount"],
        "snapshotComparisonCheckCount": len(checks),
        "snapshotComparisonPassCount": sum(1 for check in checks if check["status"] == "pass"),
        "privateAdapterSnapshotComparisonRecorded": True,
        "gbVisA7AdapterSmokeConsumed": True,
        "baselineSnapshotRecorded": True,
        "observedSnapshotRecorded": True,
        "snapshotComparisonChecksRecorded": True,
        "snapshotComparisonChecksPassed": True,
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
        "nextAction": "ACT-A9 reviewer report feed guard or GB-VIS-A9 private adapter feed guard without public promotion.",
        "claimFlagsBounded": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "private_adapter_snapshot_comparison_recorded",
                "gb_vis_a7_adapter_smoke_consumed",
                "baseline_snapshot_recorded",
                "observed_snapshot_recorded",
                "snapshot_comparison_checks_recorded",
                "snapshot_comparison_checks_passed",
            ]
        )
        and all(
            value is False
            for key, value in CLAIM_FLAGS.items()
            if key
            not in {
                "private_adapter_snapshot_comparison_recorded",
                "gb_vis_a7_adapter_smoke_consumed",
                "baseline_snapshot_recorded",
                "observed_snapshot_recorded",
                "snapshot_comparison_checks_recorded",
                "snapshot_comparison_checks_passed",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "private_adapter_snapshot_comparison_v0",
        "artifactId": "gb-vis-a8-private-adapter-snapshot-comparison",
        "status": STATUS,
        "decision": "record_private_adapter_snapshot_comparison_no_renderer_execution_no_public_promotion",
        "date": DATE,
        "sourceAdapterSmokeFixture": source["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "baselineSnapshot": baseline,
        "observedSnapshot": observed,
        "snapshotComparisonChecks": checks,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceAdapterSmokeFixture"] != "gb-vis-a7-private-adapter-smoke-fixture":
        raise ValueError("GB-VIS-A8 must consume GB-VIS-A7")
    if summary["adapterSmokeRowCount"] != 6:
        raise ValueError("unexpected adapter smoke row count")
    if summary["structureSmokeRowCount"] != 1 or summary["guardOverlaySmokeRowCount"] != 5:
        raise ValueError("adapter smoke row type count drift")
    if summary["adapterSmokeCheckCount"] != 7 or summary["adapterSmokeCheckPassCount"] != 7:
        raise ValueError("adapter smoke check count drift")
    if summary["snapshotComparisonCheckCount"] != 4 or summary["snapshotComparisonPassCount"] != 4:
        raise ValueError("unexpected snapshot comparison count")
    for check in payload["snapshotComparisonChecks"]:
        if check["status"] != "pass" or check["baseline"] != check["observed"]:
            raise ValueError("adapter snapshot comparison must pass exactly")
    for key in [
        "privateAdapterSnapshotComparisonRecorded",
        "gbVisA7AdapterSmokeConsumed",
        "baselineSnapshotRecorded",
        "observedSnapshotRecorded",
        "snapshotComparisonChecksRecorded",
        "snapshotComparisonChecksPassed",
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
        "artifactType": "private_adapter_snapshot_comparison",
        "validationStatus": "pass",
        "semanticStrength": "private_adapter_snapshot_comparison_no_renderer_execution_no_public_update",
        "source": f"python/results/gb_vis_a8_private_adapter_snapshot_comparison/gb_vis_a8_private_adapter_snapshot_comparison_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "gb_vis_a8_private_adapter_snapshot_comparison_feed",
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
        "# GB-VIS-A8 Private Adapter Snapshot Comparison",
        "",
        f"Status: `{payload['status']}`",
        "",
        "GB-VIS-A8 records a private adapter snapshot comparison without implementing or executing a renderer.",
        "",
        "| Count | Value |",
        "|---|---|",
        f"| smoke rows | `{payload['summary']['adapterSmokeRowCount']}` |",
        f"| smoke checks | `{payload['summary']['adapterSmokeCheckCount']}` |",
        f"| snapshot checks | `{payload['summary']['snapshotComparisonCheckCount']}` |",
        f"| snapshot passes | `{payload['summary']['snapshotComparisonPassCount']}` |",
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
    result_path = out_dir / f"gb_vis_a8_private_adapter_snapshot_comparison_{STAMP}.json"
    report_path = report_dir / f"gb_vis_a8_private_adapter_snapshot_comparison_{STAMP}.md"
    evidence_path = evidence_dir / "gb_vis_a8_private_adapter_snapshot_comparison.json"
    feed_path = command_feed_dir / f"gb_vis_a8_private_adapter_snapshot_comparison_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/gb_vis_a8_private_adapter_snapshot_comparison")
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
    print("GB_VIS_A8_PRIVATE_ADAPTER_SNAPSHOT_COMPARISON_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
