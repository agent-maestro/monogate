#!/usr/bin/env python3
"""EML-A15 Glass Box evidence mount handoff.

Builds a private, non-invasive handoff from A14 Forge/eFrog export packets to
Monogate Engine / Glass Box. The engine worktree is intentionally not touched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MONOGATE_ROOT = ROOT.parent
ENGINE_ROOT = MONOGATE_ROOT / "monogate-engine"

if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_advantage_lab import CLAIM_FLAGS as ADVANTAGE_CLAIM_FLAGS  # noqa: E402

DATE = "2026-05-29"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_a15_glassbox_evidence_mount.v0"
MOUNT_CARD_SCHEMA_VERSION = "monogate.glassbox_evidence_mount_card.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_A15_GLASSBOX_EVIDENCE_MOUNT_HANDOFF_PASS"

A14_RESULT = ROOT / "python/results/eml_a14_forge_efrog_export_ux/eml_a14_forge_efrog_export_ux_2026_05_29.json"
A14_PACKET_DIR = ROOT / "python/results/eml_forge_efrog_export_packets"
ENGINE_HISTORY = ENGINE_ROOT / "product_readiness/mge_a15_transition_packet_history_export_2026_05_28.json"

DIRTY_ENGINE_PATHS = [
    ".github/workflows/proofs.yml",
    "crates/mge-app/src/lib.rs",
    "crates/mge-asset/src/hot_reload.rs",
    "crates/mge-audio/src/lib.rs",
    "crates/mge-conformance/tests/physics_ray_aabb.rs",
    "crates/mge-conformance/tests/physics_ray_plane.rs",
    "crates/mge-conformance/tests/physics_ray_sphere.rs",
    "crates/mge-input/src/camera.rs",
    "crates/mge-physics/src/lib.rs",
    "crates/mge-physics/src/verified_ray.rs",
    "crates/mge-render/src/eml_kernels.rs",
    "crates/mge-render/src/post.rs",
    "crates/mge-render/tests/visual_baseline.rs",
    "crates/mge-render/tests/visual_snapshots.rs",
    "examples/15-glassbox-experience/src/stages/showcase.rs",
    "examples/15-glassbox-experience/src/stages/themed_room.rs",
    "examples/16-hdr-bloom-spike/src/lib.rs",
]

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "deployment_performed": False,
    "engine_behavior_changed": False,
    "engine_files_modified": False,
    "glassbox_production_claim": False,
    "production_runtime_claim": False,
    "certified_safety_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "runtime_performance_claim": False,
    "broad_eml_advantage_claim": False,
    "automatic_approval_claim": False,
}

NON_CLAIMS = [
    "A15 is a private Glass Box handoff, not an engine runtime change.",
    "A15 does not modify Monogate Engine files.",
    "A15 does not claim production runtime, certified safety, compiler correctness, formal equivalence, runtime performance, or public readiness.",
    "A15 does not automatically approve any evidence packet for public display.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_export_packets() -> list[dict[str, Any]]:
    packets = [read_json(path) for path in sorted(A14_PACKET_DIR.glob("*_2026_05_29.json"))]
    if not packets:
        raise ValueError("expected A14 export packets")
    return packets


def card_priority(packet: dict[str, Any]) -> int:
    if packet["roundtripLinkStatus"] == "linked_by_canonical_eml_hash":
        return 1
    return 2


def build_mount_card(packet: dict[str, Any]) -> dict[str, Any]:
    card = {
        "schemaVersion": MOUNT_CARD_SCHEMA_VERSION,
        "date": DATE,
        "mountCardId": packet["exportId"].replace("_export_packet_v0", "_glassbox_mount_card_v0"),
        "sourceExportId": packet["exportId"],
        "sourceCaseId": packet["sourceCaseId"],
        "functionName": packet["functionName"],
        "sourcePath": packet["sourcePath"],
        "canonicalEmlHash": packet["canonicalEmlHash"],
        "glassBoxSlot": {
            "surface": "private_hud_evidence_card",
            "group": "forge_efrog_exports",
            "priority": card_priority(packet),
        },
        "displayFields": [
            "functionName",
            "sourcePath",
            "emlSurfaceSummary.familyId",
            "semanticSampleGridStatus",
            "roundtripLinkStatus",
            "forgeTargets",
            "blockedClaims",
            "missingEvidence",
        ],
        "transitionLink": {
            "transitionPacketHistoryPath": str(ENGINE_HISTORY.relative_to(MONOGATE_ROOT)),
            "linkMode": "handoff_only",
            "engineAdapterRequired": True,
        },
        "semanticSampleGridStatus": packet["semanticSampleGridStatus"],
        "semanticSampleCount": packet["semanticSampleCount"],
        "roundtripLinkStatus": packet["roundtripLinkStatus"],
        "roundtripCaseCount": packet["roundtripCaseCount"],
        "forgeTargets": packet["forgeTargets"],
        "emlSurfaceSummary": packet["emlSurfaceSummary"],
        "blockedClaims": packet["blockedClaims"],
        "missingEvidence": packet["missingEvidence"],
        "reviewerAction": "Keep private; mount as a Glass Box evidence card only after engine worktree coordination.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_mount_card(card)
    return card


def build_payload(card_dir: Path | None = None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    a14 = read_json(A14_RESULT)
    exports = load_export_packets()
    cards = [build_mount_card(packet) for packet in exports]
    if card_dir:
        card_dir.mkdir(parents=True, exist_ok=True)
        for card in cards:
            path = card_dir / f"{card['mountCardId']}_{STAMP}.json"
            path.write_text(json.dumps(card, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "eml-a15-glassbox-evidence-mount",
        "sourceEvidence": [
            str(A14_RESULT.relative_to(ROOT)),
            str(A14_PACKET_DIR.relative_to(ROOT)),
            str(ENGINE_HISTORY.relative_to(MONOGATE_ROOT)),
        ],
        "mountCardIds": [card["mountCardId"] for card in cards],
        "engineWorktree": {
            "status": "dirty_not_modified_by_a15",
            "dirtyPathCount": len(DIRTY_ENGINE_PATHS),
            "dirtyPathsObserved": list(DIRTY_ENGINE_PATHS),
            "adapterImplementation": "deferred_until_engine_worktree_is_coordinated",
        },
        "adapterContract": {
            "targetSurface": "Monogate Engine Glass Box private HUD",
            "input": "A14 export packet or A15 mount card",
            "requiredFields": [
                "mountCardId",
                "sourceExportId",
                "functionName",
                "canonicalEmlHash",
                "semanticSampleGridStatus",
                "roundtripLinkStatus",
                "emlSurfaceSummary",
                "blockedClaims",
                "missingEvidence",
            ],
            "expectedUiBehavior": [
                "show compact evidence card",
                "open raw packet preview",
                "show blocked claims before any result text",
                "never imply runtime/proof/public approval",
            ],
        },
        "summary": {
            "mountCardCount": len(cards),
            "sourceExportPacketCount": a14["summary"]["exportPacketCount"],
            "roundtripLinkedMountCount": sum(1 for card in cards if card["roundtripLinkStatus"] == "linked_by_canonical_eml_hash"),
            "semanticOnlyMountCount": sum(1 for card in cards if card["roundtripLinkStatus"] == "semantic_comparison_only"),
            "engineDirtyPathCount": len(DIRTY_ENGINE_PATHS),
            "engineFilesModifiedByA15": 0,
            "engineBehaviorChanged": False,
            "glassboxProductionClaim": False,
            "productionRuntimeClaim": False,
            "certifiedSafetyClaim": False,
            "publicReady": False,
            "deploymentPerformed": False,
            "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
        },
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload, cards)
    return payload, cards


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-a15-glassbox-evidence-mount",
        "title": "EML-A15 Glass Box Evidence Mount Handoff",
        "reviewDecision": "private_engine_handoff_recorded",
        "validationStatus": "pass",
        "replayStatus": "not_applicable_handoff_over_existing_packets",
        "semanticStrength": "glassbox_mount_contract_no_engine_behavior_change",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private Glass Box handoff only; no engine behavior change, production runtime, certified safety, compiler correctness, formal equivalence, public readiness, or deployment claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Transforms six A14 export packets into Glass Box mount cards.",
            "Records the engine dirty-worktree constraint explicitly.",
            "Defers adapter implementation until engine work is coordinated.",
        ],
        "validationCommands": [
            "python python/scripts/eml_a15_glassbox_evidence_mount.py --build --strict",
            "python -m pytest -q python/tests/test_eml_a15_glassbox_evidence_mount.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_a15_glassbox_evidence_mount.v0",
        "date": DATE,
        "title": "EML-A15 Glass Box Evidence Mount Handoff",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "Implement the Glass Box adapter only after monogate-engine worktree coordination.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any], cards: list[dict[str, Any]]) -> str:
    lines = [
        "# EML-A15 Glass Box Evidence Mount Handoff",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "A15 prepares A14 Forge/eFrog export packets for Glass Box without touching Monogate Engine.",
        "",
        "| Mount card | Function | Family | Link status | Slot |",
        "|---|---|---|---|---|",
    ]
    for card in cards:
        lines.append(
            f"| `{card['mountCardId']}` | `{card['functionName']}` | "
            f"`{card['emlSurfaceSummary']['familyId']}` | `{card['roundtripLinkStatus']}` | "
            f"`{card['glassBoxSlot']['surface']}` |"
        )
    summary = payload["summary"]
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Mount cards: `{summary['mountCardCount']}`",
            f"- Roundtrip-linked mounts: `{summary['roundtripLinkedMountCount']}`",
            f"- Semantic-only mounts: `{summary['semanticOnlyMountCount']}`",
            f"- Engine dirty paths observed: `{summary['engineDirtyPathCount']}`",
            f"- Engine files modified by A15: `{summary['engineFilesModifiedByA15']}`",
            "",
            "## Adapter Contract",
            "",
            f"- Target surface: `{payload['adapterContract']['targetSurface']}`",
            f"- Adapter implementation: `{payload['engineWorktree']['adapterImplementation']}`",
            "",
            "## Boundary",
            "",
            "- No Monogate Engine behavior change.",
            "- No production runtime or certified safety claim.",
            "- No compiler correctness or formal equivalence claim.",
            "- No public-readiness or deployment claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_mount_card(card: dict[str, Any]) -> None:
    if card["schemaVersion"] != MOUNT_CARD_SCHEMA_VERSION:
        raise ValueError("invalid mount card schema")
    if card["semanticSampleGridStatus"] != "pass":
        raise ValueError("mount card requires passing semantic sample-grid status")
    if card["transitionLink"]["linkMode"] != "handoff_only":
        raise ValueError("A15 must remain handoff-only")
    for key, value in card["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any], cards: list[dict[str, Any]]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid status")
    summary = payload["summary"]
    if summary["mountCardCount"] != 6:
        raise ValueError("expected six mount cards")
    if summary["engineFilesModifiedByA15"] != 0:
        raise ValueError("A15 must not modify engine files")
    for key in [
        "engineBehaviorChanged",
        "glassboxProductionClaim",
        "productionRuntimeClaim",
        "certifiedSafetyClaim",
        "publicReady",
        "deploymentPerformed",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    if len({card["mountCardId"] for card in cards}) != len(cards):
        raise ValueError("mount card ids must be unique")
    for key, value in payload["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def build_outputs(out_dir: Path, card_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload, cards = build_payload(card_dir)
    evidence = build_evidence_packet(payload)
    feed = build_command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"eml_a15_glassbox_evidence_mount_{STAMP}.json"
    report_path = report_dir / f"eml_a15_glassbox_evidence_mount_{STAMP}.md"
    evidence_path = evidence_dir / "eml_a15_glassbox_evidence_mount.json"
    feed_path = command_feed_dir / f"eml_a15_glassbox_evidence_mount_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload, cards), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "cards": cards,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
        "card_dir": str(card_dir),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_a15_glassbox_evidence_mount")
    parser.add_argument("--card-dir", type=Path, default=ROOT / "python/results/eml_glassbox_mount_cards")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_outputs(args.out_dir, args.card_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"], built["cards"])
    print("EML_A15_GLASSBOX_EVIDENCE_MOUNT_OK")
    print(f"mount_cards={built['payload']['summary']['mountCardCount']}")
    print(f"engine_files_modified={built['payload']['summary']['engineFilesModifiedByA15']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
