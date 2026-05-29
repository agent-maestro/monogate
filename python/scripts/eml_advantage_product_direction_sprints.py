#!/usr/bin/env python3
"""EML Advantage product-direction sprints.

This records the clean post-PCC10 implementation direction across Forge/eFrog,
Monogate Engine/Glass Box, and MachLib without changing those systems yet.
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
SCHEMA_VERSION = "monogate.eml_advantage_product_direction_sprints.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_ADVANTAGE_PRODUCT_DIRECTION_SPRINTS_PASS"

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "deployment_performed": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "proof_claim": False,
    "machlib_theorem_discharged": False,
    "engine_runtime_claim": False,
    "glassbox_production_claim": False,
    "broad_eml_advantage_claim": False,
    "production_toolchain_claim": False,
    "certified_safety_claim": False,
}

NON_CLAIMS = [
    "This is a private product-direction sprint plan, not a new EML advantage result.",
    "No Forge/eFrog compiler behavior changed.",
    "No Monogate Engine runtime behavior changed.",
    "No MachLib theorem is claimed discharged by this artifact.",
    "No compiler correctness, formal equivalence, runtime performance, certified safety, deployment, or public-readiness claim is made.",
]


def build_sprints() -> list[dict[str, Any]]:
    return [
        {
            "sprintId": "forge_efrog_packet_export_ux",
            "order": 1,
            "title": "Forge/eFrog Packet Export UX",
            "lane": "compiler_decompiler",
            "goal": "Turn the existing Forge/eFrog roundtrip and semantic comparison work into a developer-facing packet export workflow.",
            "inputs": [
                "eml-a13-forge-efrog-roundtrip",
                "eml-a13-2-semantic-output-comparison",
                "eml-adv-pcc10-family-synthesis",
            ],
            "deliverables": [
                "private packet export spec",
                "CLI or builder preset for source -> EML -> Forge target evidence",
                "fixture-backed export example",
                "claim-boundary report",
            ],
            "blockedClaims": [
                "compiler correctness",
                "formal equivalence",
                "broad EML advantage",
                "runtime performance",
            ],
            "whyFirst": "It is least blocked, uses clean existing artifacts, and turns EML research into an inspectable developer workflow.",
            "risk": "Medium",
            "readyToStart": True,
        },
        {
            "sprintId": "mge_glassbox_evidence_mount",
            "order": 2,
            "title": "Monogate Engine / Glass Box Evidence Mount",
            "lane": "engine_runtime",
            "goal": "Mount selected EML Advantage and compiler/decompiler evidence into Glass Box as reviewable packets or HUD-linked traces.",
            "inputs": [
                "engine-transition-history",
                "eml-adv-pcc10-family-synthesis",
                "eml-a13-2-semantic-output-comparison",
            ],
            "deliverables": [
                "engine handoff packet",
                "Glass Box evidence adapter spec",
                "non-overlapping implementation note for the dirty engine worktree",
                "private command cockpit row",
            ],
            "blockedClaims": [
                "production runtime",
                "certified safety",
                "game-engine completeness",
                "automatic approval",
            ],
            "whySecond": "It connects the research to the visible engine experience, but the dirty engine worktree currently has unrelated uncommitted edits, so the first pass should be a handoff/spec artifact.",
            "risk": "MediumHigh",
            "readyToStart": True,
        },
        {
            "sprintId": "machlib_small_witness_selection",
            "order": 3,
            "title": "MachLib Small Witness Selection",
            "lane": "formal_methods",
            "goal": "Select one narrow, low-risk EML witness candidate for a proof attempt after inspecting the current MachLib surface.",
            "inputs": [
                "eml-adv-pcc10-family-synthesis",
                "eml-atlas-safe-education-candidates",
                "prior subtraction-boundary discussion",
            ],
            "deliverables": [
                "witness candidate decision",
                "domain assumptions",
                "Lean file touch-plan",
                "proof or blocked-proof report after implementation sprint",
            ],
            "recommendedCandidate": {
                "name": "subtraction_boundary",
                "statement": "eml(log(v), exp(u)) = v - u under v > 0",
                "reason": "It is cleaner than log reconstruction, expresses a useful Atlas boundary, and depends on explicit domain assumptions.",
            },
            "blockedClaims": [
                "MachLib witness completion before Lean passes",
                "general EML correctness",
                "Forge compiler correctness",
                "formal equivalence",
            ],
            "whyThird": "It is valuable, but proof work should begin only after local MachLib inspection confirms the exact namespace and existing theorem surface.",
            "risk": "High",
            "readyToStart": True,
        },
    ]


def build_payload() -> dict[str, Any]:
    sprints = build_sprints()
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "eml-advantage-product-direction-sprints",
        "title": "EML Advantage Product Direction Sprints",
        "sourcePausePoint": "eml-adv-pcc10-family-synthesis",
        "recommendedOrder": [sprint["sprintId"] for sprint in sprints],
        "sprints": sprints,
        "summary": {
            "sprintCount": len(sprints),
            "readyToStartCount": sum(1 for sprint in sprints if sprint["readyToStart"]),
            "forgeEfrogSprintCount": 1,
            "engineGlassboxSprintCount": 1,
            "machlibWitnessSprintCount": 1,
            "recommendedFirstSprint": "forge_efrog_packet_export_ux",
            "engineWorktreeConstraintRecorded": True,
            "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
            "publicReady": False,
            "deploymentPerformed": False,
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
        "reviewDecision": "private_direction_approved",
        "validationStatus": "pass",
        "replayStatus": "not_applicable_direction_plan",
        "semanticStrength": "post_pcc10_product_direction_plan_no_new_research_claim",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private direction plan only; no compiler, engine, proof, runtime, deployment, certified-safety, public-readiness, or broad EML advantage claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Chooses Forge/eFrog packet export UX as the first focused sprint.",
            "Keeps Engine/Glass Box work as a handoff/spec sprint while the engine worktree is dirty.",
            "Selects a narrow MachLib witness candidate without claiming the proof is complete.",
        ],
        "validationCommands": [
            "python python/scripts/eml_advantage_product_direction_sprints.py --build --strict",
            "python -m pytest -q python/tests/test_eml_advantage_product_direction_sprints.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_advantage_product_direction_sprints.v0",
        "date": DATE,
        "title": payload["title"],
        "status": payload["status"],
        "summary": payload["summary"],
        "recommendedOrder": payload["recommendedOrder"],
        "topFollowup": "Start Sprint 1: Forge/eFrog packet export UX.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML Advantage Product Direction Sprints",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "PCC10 is a clean research pause point. This artifact turns that pause into three focused implementation sprints.",
        "It does not add a new EML result, proof, compiler claim, engine claim, or deployment.",
        "",
        "| Order | Sprint | Lane | Risk | Why |",
        "|---:|---|---|---|---|",
    ]
    for sprint in payload["sprints"]:
        why = sprint.get("whyFirst") or sprint.get("whySecond") or sprint.get("whyThird")
        lines.append(
            f"| {sprint['order']} | `{sprint['sprintId']}` | `{sprint['lane']}` | `{sprint['risk']}` | {why} |"
        )
    lines.extend(
        [
            "",
            "## Recommended Order",
            "",
        ]
    )
    for sprint in payload["sprints"]:
        lines.extend(
            [
                f"### {sprint['order']}. {sprint['title']}",
                "",
                sprint["goal"],
                "",
                "Deliverables:",
            ]
        )
        for deliverable in sprint["deliverables"]:
            lines.append(f"- {deliverable}")
        lines.extend(["", "Blocked claims:"])
        for blocked in sprint["blockedClaims"]:
            lines.append(f"- {blocked}")
        lines.append("")
        if "recommendedCandidate" in sprint:
            candidate = sprint["recommendedCandidate"]
            lines.extend(
                [
                    "Recommended witness candidate:",
                    "",
                    f"- name: `{candidate['name']}`",
                    f"- statement: `{candidate['statement']}`",
                    f"- reason: {candidate['reason']}",
                    "",
                ]
            )
    lines.extend(
        [
            "## Boundary",
            "",
            "- Private direction plan only.",
            "- No Forge/eFrog behavior change.",
            "- No Monogate Engine behavior change.",
            "- No MachLib proof claim.",
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
        raise ValueError("expected exactly three sprints")
    if summary["readyToStartCount"] != 3:
        raise ValueError("expected all three direction sprints to be ready to start")
    if summary["recommendedFirstSprint"] != "forge_efrog_packet_export_ux":
        raise ValueError("Forge/eFrog should be first")
    if summary["engineWorktreeConstraintRecorded"] is not True:
        raise ValueError("engine worktree constraint must be recorded")
    if summary["publicReady"] is not False:
        raise ValueError("publicReady must remain false")
    if summary["deploymentPerformed"] is not False:
        raise ValueError("deploymentPerformed must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    if [sprint["order"] for sprint in payload["sprints"]] != [1, 2, 3]:
        raise ValueError("sprint order must be 1, 2, 3")
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
    result_path = out_dir / f"eml_advantage_product_direction_sprints_{STAMP}.json"
    report_path = report_dir / f"eml_advantage_product_direction_sprints_{STAMP}.md"
    evidence_path = evidence_dir / "eml_advantage_product_direction_sprints.json"
    feed_path = command_feed_dir / f"eml_advantage_product_direction_sprints_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_advantage_product_direction_sprints")
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
    print("EML_ADVANTAGE_PRODUCT_DIRECTION_SPRINTS_OK")
    print(f"sprints={built['payload']['summary']['sprintCount']}")
    print(f"first={built['payload']['summary']['recommendedFirstSprint']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
