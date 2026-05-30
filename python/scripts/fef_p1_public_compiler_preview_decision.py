#!/usr/bin/env python3
"""FEF-P1 package/CLI decision for the public Forge/eFrog compiler preview."""

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
SCHEMA_VERSION = "monogate.fef_p1_public_compiler_preview_decision.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P1_PUBLIC_COMPILER_PREVIEW_DECISION_RECORDED"

FEF_P0_PATH = ROOT / "reports/evidence_packets/fef_p0_public_compiler_slice_readiness.json"

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "forge_behavior_changed": False,
    "efrog_behavior_changed": False,
    "generated_target_code_changed": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "broad_eml_advantage_claim": False,
    "runtime_performance_claim": False,
    "public_performance_claim": False,
    "production_toolchain_claim": False,
    "certified_safety_claim": False,
    "proof_claim": False,
    "deploy_performed": False,
    "package_published": False,
    "public_compiler_package_available": False,
    "public_quickstart_reproducible": False,
    "public_checkout_enabled": False,
    "public_package_name_reserved": False,
    "package_implementation_started": False,
}

NON_CLAIMS = [
    "FEF-P1 records a package/CLI decision only.",
    "FEF-P1 does not publish or implement a public compiler package.",
    "FEF-P1 does not change Forge or eFrog behavior.",
    "FEF-P1 does not claim compiler correctness, formal equivalence, runtime performance, production readiness, proof strength, or public hardware readiness.",
    "FEF-P1 does not re-enable checkout.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def option_matrix() -> list[dict[str, Any]]:
    return [
        {
            "id": "extend_monogate_package",
            "label": "Add compiler-preview commands to monogate",
            "decision": "rejected_for_now",
            "reason": "Lowest install friction, but it blurs the public math/optimization package with an immature compiler preview.",
            "risk": "Users may infer the core monogate package now includes the full Forge compiler.",
        },
        {
            "id": "monogate_forge_preview_package",
            "label": "Create monogate-forge-preview",
            "decision": "selected",
            "reason": "Makes the preview explicit, bounded, and separate from both monogate and future Forge Pro.",
            "risk": "Requires separate packaging and quickstart work before any public claim.",
        },
        {
            "id": "artifact_only_preview",
            "label": "Publish reproducible artifacts only",
            "decision": "fallback",
            "reason": "Safest if packaging takes longer, but less useful as a public compiler preview.",
            "risk": "May feel like documentation rather than a tool.",
        },
    ]


def allowed_commands() -> list[dict[str, str]]:
    return [
        {
            "command": "monogate-forge-preview capabilities",
            "purpose": "Print the bounded preview capability map and blocked claims.",
        },
        {
            "command": "monogate-forge-preview emit --target python examples/gaussian.py --out build/gaussian.py",
            "purpose": "Run the selected source -> EML -> Forge Python preview path.",
        },
        {
            "command": "monogate-forge-preview emit --target javascript examples/gaussian.py --out build/gaussian.js",
            "purpose": "Run the selected source -> EML -> Forge JavaScript preview path.",
        },
        {
            "command": "monogate-forge-preview check examples/gaussian.py --targets python,javascript",
            "purpose": "Run deterministic sample-grid checks for the preview slice.",
        },
        {
            "command": "monogate-forge-preview packet examples/gaussian.py --targets python,javascript --out evidence/packet.json",
            "purpose": "Emit a bounded evidence packet with all public claim flags false.",
        },
    ]


def blocked_commands() -> list[dict[str, str]]:
    return [
        {
            "command": "monogate-forge-preview emit --target verilog",
            "reason": "Blocked until FPGA simulation/synthesis/live evidence exists for the public path.",
        },
        {
            "command": "monogate-forge-preview emit --target lean --claim-proof",
            "reason": "Blocked until checked proof status exists and no theorem stub is presented as proof.",
        },
        {
            "command": "monogate-forge-preview emit --target all",
            "reason": "Blocked because FEF-P0 only covers Python/JavaScript selected-slice evidence.",
        },
        {
            "command": "monogate-forge-preview prove-correct",
            "reason": "Blocked because compiler correctness and formal equivalence are not established.",
        },
        {
            "command": "monogate-forge-preview benchmark --claim-speedup",
            "reason": "Blocked because FEF-P1 records no public runtime performance claim.",
        },
    ]


def release_gates() -> list[dict[str, Any]]:
    return [
        {
            "id": "package_scaffold_created",
            "status": "pending",
            "requiredEvidence": "A minimal package scaffold for monogate-forge-preview with version, README, CLI entrypoint, and tests.",
        },
        {
            "id": "clean_room_quickstart_passed",
            "status": "pending",
            "requiredEvidence": "Fresh environment install and exact quickstart commands without sibling private repos.",
        },
        {
            "id": "python_target_execution_passed",
            "status": "pending",
            "requiredEvidence": "Generated Python target executes over deterministic sample grids.",
        },
        {
            "id": "javascript_target_execution_passed",
            "status": "pending",
            "requiredEvidence": "Generated JavaScript target executes over deterministic sample grids.",
        },
        {
            "id": "public_copy_review_passed",
            "status": "pending",
            "requiredEvidence": "Website/docs copy says preview, selected targets, and blocked claims.",
        },
        {
            "id": "checkout_remains_disabled",
            "status": "required",
            "requiredEvidence": "No paid checkout is enabled for compiler claims during preview.",
        },
    ]


def build_payload() -> dict[str, Any]:
    fef_p0 = read_json(FEF_P0_PATH)
    selected = next(option for option in option_matrix() if option["decision"] == "selected")
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p1-public-compiler-preview-decision",
        "decision": "select_monogate_forge_preview_package",
        "selectedPackage": {
            "name": "monogate-forge-preview",
            "distributionStatus": "not_created_not_published",
            "scope": "minimum public compiler preview for selected eFrog -> EML -> Forge Python/JavaScript paths",
            "selectedReason": selected["reason"],
        },
        "optionMatrix": option_matrix(),
        "previewScope": {
            "inputScope": [
                "selected source fixtures",
                "selected .eml fixtures only after clean-room quickstart proves them",
            ],
            "targetScope": ["python", "javascript"],
            "requiredChecks": [
                "deterministic sample-grid comparison",
                "generated Python execution",
                "generated JavaScript execution",
                "evidence packet with all public claim flags false",
            ],
            "explicitlyOutOfScope": [
                "Verilog",
                "Lean proof claims",
                "zkproof",
                "target all",
                "silicon",
                "compiler correctness",
                "runtime speedup claims",
                "paid Forge Pro checkout",
            ],
        },
        "allowedCommands": allowed_commands(),
        "blockedCommands": blocked_commands(),
        "releaseGates": release_gates(),
        "fefP0Link": {
            "path": str(FEF_P0_PATH.relative_to(ROOT)),
            "decision": fef_p0["reviewDecision"],
            "privateCompilerSlicePresent": fef_p0["semanticReview"]["privateCompilerSlicePresent"],
            "publicReady": fef_p0["semanticReview"]["publicReady"],
        },
        "nextMilestones": [
            "FEF-P2 clean-room quickstart and package scaffold",
            "FEF-P3 JavaScript runtime execution in the bridge guard",
            "FEF-P4 non-Python source semantic comparison",
            "FEF-P5 public preview copy update only after FEF-P2 passes",
        ],
        "summary": {
            "packageDecisionRecorded": True,
            "selectedPackageName": "monogate-forge-preview",
            "packageCreated": False,
            "packagePublished": False,
            "publicReady": False,
            "safeToPublishPublicly": False,
            "allowedCommandCount": len(allowed_commands()),
            "blockedCommandCount": len(blocked_commands()),
            "releaseGateCount": len(release_gates()),
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
        "title": "FEF-P1 Public Compiler Preview Decision",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "package_cli_decision_only_over_fef_p0_readiness_gate",
        "semanticReview": payload["summary"],
        "claimBoundary": "Decision packet only; no package created, package published, compiler correctness, formal equivalence, runtime performance, public readiness, or checkout claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Selects monogate-forge-preview as the minimum honest public compiler preview shape.",
            "Limits preview targets to Python and JavaScript.",
            "Blocks Verilog, Lean proof claims, zkproof, target all, silicon, compiler correctness, performance claims, and checkout.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p1_public_compiler_preview_decision.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p1_public_compiler_preview_decision.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p1_public_compiler_preview_decision.v0",
        "date": DATE,
        "title": "FEF-P1 Public Compiler Preview Decision",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Build FEF-P2 clean-room quickstart and package scaffold.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# FEF-P1 Public Compiler Preview Decision",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Decision: `{payload['decision']}`",
        "",
        "FEF-P1 chooses the smallest honest public shape for the Forge/eFrog",
        "compiler preview. It selects a separate package name while keeping all",
        "publication and public-readiness flags false.",
        "",
        "## Selected Shape",
        "",
        f"- Package: `{payload['selectedPackage']['name']}`",
        f"- Distribution status: `{payload['selectedPackage']['distributionStatus']}`",
        f"- Scope: {payload['selectedPackage']['scope']}",
        "",
        "## Option Matrix",
        "",
        "| Option | Decision | Reason |",
        "|---|---|---|",
    ]
    for option in payload["optionMatrix"]:
        lines.append(f"| `{option['id']}` | `{option['decision']}` | {option['reason']} |")
    lines.extend(
        [
            "",
            "## Allowed Preview Commands",
            "",
        ]
    )
    for command in payload["allowedCommands"]:
        lines.append(f"- `{command['command']}`: {command['purpose']}")
    lines.extend(
        [
            "",
            "## Blocked Commands",
            "",
        ]
    )
    for command in payload["blockedCommands"]:
        lines.append(f"- `{command['command']}`: {command['reason']}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- No package has been created or published.",
            "- No public readiness claim.",
            "- No compiler correctness or formal equivalence claim.",
            "- No Verilog, Lean proof, zkproof, silicon, performance, or checkout claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid status")
    if payload["decision"] != "select_monogate_forge_preview_package":
        raise ValueError("unexpected package decision")
    if payload["selectedPackage"]["name"] != "monogate-forge-preview":
        raise ValueError("unexpected package name")
    if payload["selectedPackage"]["distributionStatus"] != "not_created_not_published":
        raise ValueError("package must not be marked created or published")
    if set(payload["previewScope"]["targetScope"]) != {"python", "javascript"}:
        raise ValueError("preview target scope must remain Python/JavaScript")
    blocked_text = " ".join(command["command"] for command in payload["blockedCommands"])
    for blocked in ["verilog", "lean", "all", "prove-correct", "benchmark"]:
        if blocked not in blocked_text:
            raise ValueError(f"missing blocked command for {blocked}")
    summary = payload["summary"]
    for key in ["packageCreated", "packagePublished", "publicReady", "safeToPublishPublicly"]:
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
    result_path = out_dir / f"fef_p1_public_compiler_preview_decision_{STAMP}.json"
    report_path = report_dir / f"fef_p1_public_compiler_preview_decision_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p1_public_compiler_preview_decision.json"
    feed_path = command_feed_dir / f"fef_p1_public_compiler_preview_decision_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p1_public_compiler_preview_decision")
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
    print("FEF_P1_PUBLIC_COMPILER_PREVIEW_DECISION_OK")
    print(f"decision={built['payload']['decision']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
