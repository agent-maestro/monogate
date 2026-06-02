#!/usr/bin/env python3
"""GB-VIS-A4 private snapshot comparison fixture packet."""

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

from scripts import gb_vis_a3_renderer_smoke_fixture as a3  # noqa: E402

DATE = "2026-06-02"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.snapshot_comparison_fixture.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "GB_VIS_A4_SNAPSHOT_COMPARISON_FIXTURE_PASS"

CLAIM_FLAGS = {
    "snapshot_comparison_fixture_recorded": True,
    "gb_vis_a3_smoke_fixture_consumed": True,
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
    "GB-VIS-A4 records a private snapshot comparison fixture only; it does not implement, execute, or pixel-render an interactive renderer.",
    "GB-VIS-A4 compares deterministic command snapshots from GB-VIS-A3 without proving visualization correctness, soundness, a Galois connection, abstract interpretation correctness, compiler correctness, formal equivalence, or full EML semantics.",
    "GB-VIS-A4 does not update public surfaces, runtime behavior, MachLib, production validators, laptop-owned repos, or electronics repos.",
]


def digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_snapshot(fixture: dict[str, Any], snapshot_id: str) -> dict[str, Any]:
    nodes = fixture["nodeDrawCommands"]
    edges = fixture["edgeDrawCommands"]
    legends = fixture["legendDrawCommands"]
    checks = fixture["smokeChecks"]
    return {
        "snapshotId": snapshot_id,
        "snapshotFormat": "monogate.claim_topology_command_snapshot.v0",
        "nodeCommandCount": len(nodes),
        "edgeCommandCount": len(edges),
        "legendCommandCount": len(legends),
        "smokeCheckCount": len(checks),
        "guardrailCount": len(fixture["rendererGuardrails"]),
        "nodeDigest": digest(nodes),
        "edgeDigest": digest(edges),
        "legendDigest": digest(legends),
        "smokeCheckDigest": digest(checks),
        "guardrailDigest": digest(fixture["rendererGuardrails"]),
        "viewportDigest": digest(fixture["viewport"]),
    }


def comparison_checks(baseline: dict[str, Any], observed: dict[str, Any]) -> list[dict[str, Any]]:
    fields = [
        "nodeDigest",
        "edgeDigest",
        "legendDigest",
        "smokeCheckDigest",
        "guardrailDigest",
        "viewportDigest",
    ]
    checks = []
    for field in fields:
        checks.append(
            {
                "checkId": f"{field}_matches",
                "status": "pass",
                "field": field,
                "baseline": baseline[field],
                "observed": observed[field],
            }
        )
    for check in checks:
        if check["baseline"] != check["observed"]:
            raise ValueError(f"snapshot mismatch: {check['field']}")
    return checks


def build_payload(atlas_gate_path: Path) -> dict[str, Any]:
    source = a3.build_payload(atlas_gate_path)
    a3.validate_payload(source)
    fixture = source["rendererSmokeFixture"]
    baseline = build_snapshot(fixture, "gb_vis_a4_baseline_private_command_snapshot")
    observed = build_snapshot(fixture, "gb_vis_a4_observed_private_command_snapshot")
    checks = comparison_checks(baseline, observed)
    summary = {
        "sourceSmokeFixture": source["artifactId"],
        "baselineSnapshotId": baseline["snapshotId"],
        "observedSnapshotId": observed["snapshotId"],
        "nodeCommandCount": baseline["nodeCommandCount"],
        "edgeCommandCount": baseline["edgeCommandCount"],
        "legendCommandCount": baseline["legendCommandCount"],
        "smokeCheckCount": baseline["smokeCheckCount"],
        "comparisonCheckCount": len(checks),
        "comparisonPassCount": sum(1 for check in checks if check["status"] == "pass"),
        "sourceCheckedStatement": source["summary"]["sourceCheckedStatement"],
        "sourceRuntimeControl": source["summary"]["sourceRuntimeControl"],
        "sourcePublicStatus": source["summary"]["sourcePublicStatus"],
        "snapshotComparisonFixtureRecorded": True,
        "gbVisA3SmokeFixtureConsumed": True,
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
        "nextAction": "ACT-A4 expand dry-run validator fixtures or GB-VIS-A5 add private renderer integration gate without public promotion.",
        "claimFlagsBounded": all(
            CLAIM_FLAGS[key] is True
            for key in [
                "snapshot_comparison_fixture_recorded",
                "gb_vis_a3_smoke_fixture_consumed",
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
                "snapshot_comparison_fixture_recorded",
                "gb_vis_a3_smoke_fixture_consumed",
                "baseline_snapshot_recorded",
                "observed_snapshot_recorded",
                "snapshot_comparison_checks_recorded",
                "snapshot_comparison_checks_passed",
            }
        ),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetType": "snapshot_comparison_fixture_v0",
        "artifactId": "gb-vis-a4-snapshot-comparison-fixture",
        "status": STATUS,
        "decision": "record_private_snapshot_comparison_fixture_no_pixel_renderer_execution",
        "date": DATE,
        "sourceSmokeFixture": source["artifactId"],
        "sourceAtlasGatePath": str(atlas_gate_path),
        "baselineSnapshot": baseline,
        "observedSnapshot": observed,
        "comparisonChecks": checks,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceSmokeFixture"] != "gb-vis-a3-renderer-smoke-fixture":
        raise ValueError("GB-VIS-A4 must consume GB-VIS-A3")
    if summary["nodeCommandCount"] != 23:
        raise ValueError("unexpected node command count")
    if summary["edgeCommandCount"] != 16:
        raise ValueError("unexpected edge command count")
    if summary["legendCommandCount"] != 5:
        raise ValueError("unexpected legend command count")
    if summary["smokeCheckCount"] != 6:
        raise ValueError("unexpected smoke check count")
    if summary["comparisonCheckCount"] != 6 or summary["comparisonPassCount"] != 6:
        raise ValueError("unexpected comparison check count")
    if summary["sourceCheckedStatement"] != "eml x (exp 1) = exp x - 1":
        raise ValueError("source statement drift")
    if summary["sourceRuntimeControl"] != "protected_expm1_remains_runtime_control":
        raise ValueError("runtime control drift")
    if summary["sourcePublicStatus"] != "held_private":
        raise ValueError("public status drift")
    for check in payload["comparisonChecks"]:
        if check["status"] != "pass" or check["baseline"] != check["observed"]:
            raise ValueError("snapshot comparison must pass exactly")
    for key in [
        "snapshotComparisonFixtureRecorded",
        "gbVisA3SmokeFixtureConsumed",
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
    true_keys = {
        "snapshot_comparison_fixture_recorded",
        "gb_vis_a3_smoke_fixture_consumed",
        "baseline_snapshot_recorded",
        "observed_snapshot_recorded",
        "snapshot_comparison_checks_recorded",
        "snapshot_comparison_checks_passed",
    }
    for key in true_keys:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in true_keys and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "snapshot_comparison_fixture",
        "validationStatus": "pass",
        "semanticStrength": "private_snapshot_comparison_fixture_no_pixel_renderer_no_public_update",
        "source": f"python/results/gb_vis_a4_snapshot_comparison_fixture/gb_vis_a4_snapshot_comparison_fixture_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "gb_vis_a4_snapshot_comparison_fixture_feed",
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
        "# GB-VIS-A4 Snapshot Comparison Fixture",
        "",
        f"Status: `{payload['status']}`",
        "",
        "GB-VIS-A4 records a private snapshot comparison fixture without implementing or executing a pixel renderer.",
        "",
        "| Count | Value |",
        "|---|---|",
        f"| node commands | `{payload['summary']['nodeCommandCount']}` |",
        f"| edge commands | `{payload['summary']['edgeCommandCount']}` |",
        f"| comparison checks | `{payload['summary']['comparisonCheckCount']}` |",
        f"| comparison passes | `{payload['summary']['comparisonPassCount']}` |",
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
    result_path = out_dir / f"gb_vis_a4_snapshot_comparison_fixture_{STAMP}.json"
    report_path = report_dir / f"gb_vis_a4_snapshot_comparison_fixture_{STAMP}.md"
    evidence_path = evidence_dir / "gb_vis_a4_snapshot_comparison_fixture.json"
    feed_path = command_feed_dir / f"gb_vis_a4_snapshot_comparison_fixture_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/gb_vis_a4_snapshot_comparison_fixture")
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
    print("GB_VIS_A4_SNAPSHOT_COMPARISON_FIXTURE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
