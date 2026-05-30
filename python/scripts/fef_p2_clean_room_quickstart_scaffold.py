#!/usr/bin/env python3
"""FEF-P2 clean-room quickstart and package scaffold packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_advantage_lab import CLAIM_FLAGS as ADVANTAGE_CLAIM_FLAGS  # noqa: E402

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p2_clean_room_quickstart_scaffold.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P2_CLEAN_ROOM_QUICKSTART_SCAFFOLD_PASS"

PACKAGE_ROOT = ROOT / "packages/monogate-forge-preview"
FEF_P1_PATH = ROOT / "reports/evidence_packets/fef_p1_public_compiler_preview_decision.json"
CLEANROOM_DIR = ROOT / "python/results/fef_p2_clean_room_quickstart_scaffold/cleanroom_outputs"

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "forge_behavior_changed": False,
    "efrog_behavior_changed": False,
    "generated_target_code_changed": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "runtime_performance_claim": False,
    "public_performance_claim": False,
    "production_toolchain_claim": False,
    "certified_safety_claim": False,
    "proof_claim": False,
    "deploy_performed": False,
    "package_published": False,
    "public_compiler_package_available": False,
    "public_checkout_enabled": False,
}

NON_CLAIMS = [
    "FEF-P2 creates a local scaffold and records a clean-room quickstart pass.",
    "FEF-P2 does not publish a package or reserve a public package name.",
    "FEF-P2 does not claim a general Forge/eFrog compiler implementation.",
    "FEF-P2 does not claim compiler correctness, formal equivalence, runtime performance, production readiness, proof strength, or public hardware readiness.",
    "FEF-P2 does not re-enable checkout.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def package_files() -> list[str]:
    return [
        "pyproject.toml",
        "README.md",
        "QUICKSTART.md",
        "examples/gaussian.py",
        "src/monogate_forge_preview/__init__.py",
        "src/monogate_forge_preview/cli.py",
        "src/monogate_forge_preview/preview.py",
        "tests/test_cli.py",
    ]


def quickstart_commands() -> list[str]:
    return [
        "python -m venv /tmp/monogate_forge_preview_cleanroom",
        "/tmp/monogate_forge_preview_cleanroom/bin/python -m pip install --upgrade pip",
        "/tmp/monogate_forge_preview_cleanroom/bin/python -m pip install -e packages/monogate-forge-preview",
        "/tmp/monogate_forge_preview_cleanroom/bin/monogate-forge-preview capabilities",
        "/tmp/monogate_forge_preview_cleanroom/bin/monogate-forge-preview emit --target python packages/monogate-forge-preview/examples/gaussian.py --out /tmp/monogate_forge_preview_cleanroom_out/gaussian.py",
        "/tmp/monogate_forge_preview_cleanroom/bin/monogate-forge-preview emit --target javascript packages/monogate-forge-preview/examples/gaussian.py --out /tmp/monogate_forge_preview_cleanroom_out/gaussian.mjs",
        "/tmp/monogate_forge_preview_cleanroom/bin/monogate-forge-preview check packages/monogate-forge-preview/examples/gaussian.py --targets python,javascript",
        "/tmp/monogate_forge_preview_cleanroom/bin/monogate-forge-preview packet packages/monogate-forge-preview/examples/gaussian.py --targets python,javascript --out /tmp/monogate_forge_preview_cleanroom_out/packet.json",
    ]


def build_payload() -> dict[str, Any]:
    fef_p1 = read_json(FEF_P1_PATH)
    capabilities = read_json(CLEANROOM_DIR / "capabilities.json")
    check = read_json(CLEANROOM_DIR / "check.json")
    packet = read_json(CLEANROOM_DIR / "packet.json")
    files = package_files()
    missing = [path for path in files if not (PACKAGE_ROOT / path).exists()]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p2-clean-room-quickstart-scaffold",
        "decision": "local_scaffold_and_clean_room_quickstart_passed",
        "package": {
            "name": "monogate-forge-preview",
            "path": str(PACKAGE_ROOT.relative_to(ROOT)),
            "distributionStatus": "local_scaffold_not_published",
            "files": files,
            "missingFiles": missing,
        },
        "quickstart": {
            "status": "pass",
            "commands": quickstart_commands(),
            "outputDir": str(CLEANROOM_DIR.relative_to(ROOT)),
            "capabilitiesPath": str((CLEANROOM_DIR / "capabilities.json").relative_to(ROOT)),
            "checkPath": str((CLEANROOM_DIR / "check.json").relative_to(ROOT)),
            "packetPath": str((CLEANROOM_DIR / "packet.json").relative_to(ROOT)),
            "sampleCount": check["sampleCount"],
            "maxAbsError": check["maxAbsError"],
            "targets": check["targets"],
        },
        "releaseGates": [
            {"id": "package_scaffold_created", "status": "pass"},
            {"id": "clean_room_quickstart_passed", "status": "pass"},
            {"id": "python_target_execution_passed", "status": "pass"},
            {"id": "javascript_target_execution_passed", "status": "pass"},
            {"id": "public_copy_review_passed", "status": "pending"},
            {"id": "package_published", "status": "blocked"},
            {"id": "checkout_remains_disabled", "status": "required"},
        ],
        "fefP1Link": {
            "path": str(FEF_P1_PATH.relative_to(ROOT)),
            "decision": fef_p1["reviewDecision"],
            "selectedPackageName": fef_p1["semanticReview"]["selectedPackageName"],
        },
        "capabilities": capabilities,
        "previewPacketSummary": {
            "schemaVersion": packet["schemaVersion"],
            "status": packet["status"],
            "sampleCount": packet["sampleCount"],
            "maxAbsError": packet["maxAbsError"],
        },
        "nextMilestones": [
            "FEF-P3 JavaScript runtime execution in the bridge guard for real Forge/eFrog outputs",
            "FEF-P4 non-Python source semantic comparison",
            "FEF-P5 public preview copy update only after package publication decision",
        ],
        "summary": {
            "packageScaffoldCreated": len(missing) == 0,
            "cleanRoomQuickstartPassed": check["status"] == "pass",
            "pythonTargetExecuted": "python" in check["targets"],
            "javascriptTargetExecuted": "javascript" in check["targets"],
            "sampleCount": check["sampleCount"],
            "maxAbsError": check["maxAbsError"],
            "packagePublished": False,
            "publicReady": False,
            "safeToPublishPublicly": False,
            "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
        },
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    return payload


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "title": "FEF-P2 Clean-Room Quickstart Scaffold",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "local_scaffold_clean_room_quickstart_pass_no_public_package_claim",
        "semanticReview": payload["summary"],
        "claimBoundary": "Local scaffold and clean-room quickstart only; no public package publication, general compiler implementation, compiler correctness, formal equivalence, runtime performance, public readiness, or checkout claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Creates a local monogate-forge-preview scaffold.",
            "Fresh venv quickstart installs the scaffold and runs capabilities, emit, check, and packet commands.",
            "Generated Python and JavaScript fixture targets execute over six deterministic samples with zero observed absolute error.",
        ],
        "validationCommands": [
            "python -m pytest -q packages/monogate-forge-preview/tests",
            "python python/scripts/fef_p2_clean_room_quickstart_scaffold.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p2_clean_room_quickstart_scaffold.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p2_clean_room_quickstart_scaffold.v0",
        "date": DATE,
        "title": "FEF-P2 Clean-Room Quickstart Scaffold",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Attach real Forge/eFrog JavaScript runtime execution guard in FEF-P3.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# FEF-P2 Clean-Room Quickstart Scaffold",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Decision: `{payload['decision']}`",
        "",
        "FEF-P2 creates a local `monogate-forge-preview` scaffold and records a",
        "fresh virtual-environment quickstart pass. It is still not a published",
        "package or public readiness claim.",
        "",
        "## Quickstart Result",
        "",
        f"- Package path: `{payload['package']['path']}`",
        f"- Distribution status: `{payload['package']['distributionStatus']}`",
        f"- Targets: `{','.join(payload['quickstart']['targets'])}`",
        f"- Samples: `{payload['quickstart']['sampleCount']}`",
        f"- Max abs error: `{payload['quickstart']['maxAbsError']}`",
        "",
        "## Release Gates",
        "",
        "| Gate | Status |",
        "|---|---|",
    ]
    for gate in payload["releaseGates"]:
        lines.append(f"| `{gate['id']}` | `{gate['status']}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- No package publication claim.",
            "- No general Forge/eFrog compiler implementation claim.",
            "- No compiler correctness or formal equivalence claim.",
            "- No runtime performance, public readiness, or checkout claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid status")
    summary = payload["summary"]
    if summary["packageScaffoldCreated"] is not True:
        raise ValueError("package scaffold must exist")
    if summary["cleanRoomQuickstartPassed"] is not True:
        raise ValueError("clean-room quickstart must pass")
    if summary["pythonTargetExecuted"] is not True or summary["javascriptTargetExecuted"] is not True:
        raise ValueError("both Python and JavaScript targets must execute")
    if summary["maxAbsError"] > 1e-12:
        raise ValueError("sample-grid error too high")
    for key in ["packagePublished", "publicReady", "safeToPublishPublicly"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    for key, value in payload["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    evidence = build_evidence_packet(payload)
    feed = build_command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"fef_p2_clean_room_quickstart_scaffold_{STAMP}.json"
    report_path = report_dir / f"fef_p2_clean_room_quickstart_scaffold_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p2_clean_room_quickstart_scaffold.json"
    feed_path = command_feed_dir / f"fef_p2_clean_room_quickstart_scaffold_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p2_clean_room_quickstart_scaffold")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_outputs(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("FEF_P2_CLEAN_ROOM_QUICKSTART_SCAFFOLD_OK")
    print(f"decision={built['payload']['decision']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
