#!/usr/bin/env python3
"""Focused closure artifacts for the post-PCC10 product sprints.

This turns the three product-direction sprints into reviewable implementation
handoffs without changing Forge/eFrog, Monogate Engine, or MachLib behavior.
"""

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

DATE = "2026-05-29"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_advantage_product_sprint_closure.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_ADVANTAGE_PRODUCT_SPRINT_CLOSURE_PASS"

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "deployment_performed": False,
    "forge_behavior_changed": False,
    "efrog_behavior_changed": False,
    "engine_behavior_changed": False,
    "machlib_source_changed": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "new_proof_claim": False,
    "broad_eml_advantage_claim": False,
    "production_toolchain_claim": False,
    "certified_safety_claim": False,
}

NON_CLAIMS = [
    "The closure bundle does not change Forge/eFrog behavior.",
    "The closure bundle does not change Monogate Engine behavior.",
    "The closure bundle does not change MachLib source.",
    "The MachLib lane records an existing checked witness instead of claiming a new theorem.",
    "No compiler correctness, formal equivalence, runtime performance, certified safety, production-toolchain, deployment, or public-readiness claim is made.",
]


def build_payload() -> dict[str, Any]:
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "eml-advantage-product-sprint-closure",
        "title": "EML Advantage Focused Sprint Closure",
        "sourceDirectionArtifact": "eml-advantage-product-direction-sprints",
        "sprints": [
            {
                "sprintId": "forge_efrog_packet_export_ux",
                "status": "handoff_ready",
                "result": "packet_export_contract_defined",
                "implementationSurface": "private_cli_or_packet_builder_preset",
                "sourceInputs": [
                    "reports/evidence_packets/eml_a13_forge_efrog_roundtrip_advantage.json",
                    "reports/evidence_packets/eml_a13_2_semantic_output_comparison.json",
                    "reports/evidence_packets/eml_advantage_pcc10_family_synthesis.json",
                ],
                "exportFields": [
                    "source_path",
                    "source_family",
                    "efrog_decompile_status",
                    "eml_surface_summary",
                    "forge_target",
                    "semantic_sample_grid_status",
                    "blocked_claims",
                    "non_claims",
                    "reviewer_next_step",
                ],
                "nextImplementationStep": "Build a private export command or packet-builder preset that emits this contract from existing A13/A13.2 artifacts.",
            },
            {
                "sprintId": "mge_glassbox_evidence_mount",
                "status": "handoff_ready",
                "result": "engine_handoff_contract_defined",
                "implementationSurface": "engine_private_hud_or_transition_packet_adapter",
                "sourceInputs": [
                    "../monogate-engine/product_readiness/mge_a15_transition_packet_history_export_2026_05_28.json",
                    "reports/evidence_packets/eml_advantage_product_direction_sprints.json",
                    "reports/evidence_packets/eml_a13_2_semantic_output_comparison.json",
                ],
                "handoffFields": [
                    "packet_id",
                    "kernel_or_trace_name",
                    "source_family",
                    "eml_role",
                    "runtime_recommendation",
                    "blocked_claims",
                    "raw_packet_path",
                    "reviewer_next_step",
                ],
                "worktreeConstraint": "monogate-engine has unrelated uncommitted work; first implementation should be coordinated or limited to non-overlapping handoff files.",
                "nextImplementationStep": "Add a private Glass Box evidence adapter after the current engine worktree is either committed or explicitly coordinated.",
            },
            {
                "sprintId": "machlib_small_witness_selection",
                "status": "existing_witness_recorded",
                "result": "subtraction_boundary_already_checked",
                "implementationSurface": "MachLib atlas witness reference",
                "witnesses": [
                    {
                        "name": "atlas_subtraction_boundary_witness",
                        "path": "../machlib/foundations/MachLib/EMLAtlasWitness.lean",
                        "statement": "eml (log v) (exp u) = v - u under 0 < v",
                    },
                    {
                        "name": "eml_log_exp_subtraction_boundary",
                        "path": "../machlib/foundations/MachLib/EML.lean",
                        "statement": "eml (log v) (exp u) = v - u under 0 < v",
                    },
                ],
                "verificationCommand": "cd ../machlib/foundations && lake build",
                "verificationObserved": "pass_with_existing_sorry_warnings_in_ForgeTest_and_HighDimensional",
                "nextImplementationStep": "Use the existing witness as the first MachLib-backed claim in Forge/eFrog export packets; do not add a duplicate theorem.",
            },
        ],
        "summary": {
            "sprintCount": 3,
            "handoffReadyCount": 2,
            "existingWitnessRecordedCount": 1,
            "behaviorChangeCount": 0,
            "machlibSourceChangeCount": 0,
            "newProofClaimCount": 0,
            "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
            "publicReady": False,
            "deploymentPerformed": False,
            "nextBuildSprint": "forge_efrog_packet_export_ux_implementation",
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
        "title": payload["title"],
        "reviewDecision": "private_sprint_handoffs_recorded",
        "validationStatus": "pass",
        "replayStatus": "not_applicable_handoff_bundle",
        "semanticStrength": "implementation_handoffs_plus_existing_machlib_witness_reference",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private sprint closure only; behavior changes and public/product/proof claims remain blocked.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Forge/eFrog export contract is defined for the next implementation sprint.",
            "Engine/Glass Box handoff contract is defined without touching the dirty engine worktree.",
            "MachLib subtraction-boundary witness already exists and was build-checked separately.",
        ],
        "validationCommands": [
            "python python/scripts/eml_advantage_product_sprint_closure.py --build --strict",
            "python -m pytest -q python/tests/test_eml_advantage_product_sprint_closure.py",
            "cd ../machlib/foundations && lake build",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_advantage_product_sprint_closure.v0",
        "date": DATE,
        "title": payload["title"],
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "Implement Forge/eFrog packet export UX from the recorded contract.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML Advantage Focused Sprint Closure",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This closes the planning pass for the three requested focused sprints.",
        "It produces implementation handoffs without changing compiler, engine, or MachLib behavior.",
        "",
        "| Sprint | Status | Result | Next step |",
        "|---|---|---|---|",
    ]
    for sprint in payload["sprints"]:
        lines.append(
            f"| `{sprint['sprintId']}` | `{sprint['status']}` | `{sprint['result']}` | {sprint['nextImplementationStep']} |"
        )
    lines.extend(
        [
            "",
            "## MachLib Witness",
            "",
            "The selected witness is already present in MachLib:",
            "",
        ]
    )
    machlib = payload["sprints"][2]
    for witness in machlib["witnesses"]:
        lines.append(f"- `{witness['name']}` in `{witness['path']}`: `{witness['statement']}`")
    lines.extend(
        [
            "",
            f"Verification command: `{machlib['verificationCommand']}`",
            f"Observed result: `{machlib['verificationObserved']}`",
            "",
            "## Boundary",
            "",
            "- No Forge/eFrog behavior change.",
            "- No Monogate Engine behavior change.",
            "- No MachLib source change.",
            "- No new proof claim from this bundle.",
            "- No deployment or public-readiness claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid status")
    summary = payload["summary"]
    if summary["sprintCount"] != 3:
        raise ValueError("expected three sprints")
    if summary["behaviorChangeCount"] != 0:
        raise ValueError("behavior changes must remain zero")
    if summary["machlibSourceChangeCount"] != 0:
        raise ValueError("MachLib source changes must remain zero")
    if summary["newProofClaimCount"] != 0:
        raise ValueError("new proof claims must remain zero")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    sprint_ids = {sprint["sprintId"] for sprint in payload["sprints"]}
    expected = {
        "forge_efrog_packet_export_ux",
        "mge_glassbox_evidence_mount",
        "machlib_small_witness_selection",
    }
    if sprint_ids != expected:
        raise ValueError("unexpected sprint ids")
    machlib = payload["sprints"][2]
    if machlib["result"] != "subtraction_boundary_already_checked":
        raise ValueError("MachLib sprint should record the existing subtraction witness")
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
    result_path = out_dir / f"eml_advantage_product_sprint_closure_{STAMP}.json"
    report_path = report_dir / f"eml_advantage_product_sprint_closure_{STAMP}.md"
    evidence_path = evidence_dir / "eml_advantage_product_sprint_closure.json"
    feed_path = command_feed_dir / f"eml_advantage_product_sprint_closure_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "evidence": evidence,
        "feed": feed,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_advantage_product_sprint_closure")
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
    print("EML_ADVANTAGE_PRODUCT_SPRINT_CLOSURE_OK")
    print(f"sprints={built['payload']['summary']['sprintCount']}")
    print(f"next={built['payload']['summary']['nextBuildSprint']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
