#!/usr/bin/env python3
"""RH-A2 reviewer priority queue.

Consumes RH-A1 claim review packets and ranks the next validator/sprint work.
This is a private reviewer planning artifact. It does not approve public claims,
deploy, trade, operate hardware, or change compiler behavior.
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

from scripts.eml_language_kernel import DATE  # noqa: E402

SCHEMA_VERSION = "monogate.rh_a2_reviewer_priority_queue.v0"
QUEUE_SCHEMA_VERSION = "monogate.reviewer_priority_queue.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "RH_A2_REVIEWER_PRIORITY_QUEUE_PASS"

CLAIM_FLAGS = {
    "public_ready": False,
    "public_sprint_approval_claim": False,
    "automatic_reviewer_approval": False,
    "deploy_performed": False,
    "trade_performed": False,
    "hardware_action_performed": False,
    "compiler_behavior_changed": False,
    "certified_safety_claim": False,
    "production_controller_claim": False,
    "financial_advice_claim": False,
}

NON_CLAIMS = [
    "RH-A2 is a private reviewer planning queue, not public approval.",
    "RH-A2 does not prove claims, deploy, trade, operate hardware, or change compiler behavior.",
    "RH-A2 ranking is deterministic planning guidance, not automatic sprint authorization.",
]

LANE_WEIGHTS = {
    "compiler": 18,
    "redteam": 16,
    "prediction_market": 14,
    "electronics": 13,
    "eml": 12,
    "machlib": 9,
    "external_theory": 5,
    "ai_answer": 4,
}

SPRINT_BY_CLAIM_TYPE = {
    "compiler_correctness": "R12 generated lowering stubs",
    "redteam_robustness": "RT-A2 local RAMPART adapter",
    "forecasting": "PM-A1B calibration ledger",
    "hardware": "EE-A2 live capture packet",
    "performance": "R10B runtime bakeoff",
    "proof_status": "Atlas bounded public surfacing",
    "external_theory": "X1 external theory claim decomposition",
    "ai_answer": "PB-A2 sourced AI answer intake",
}

BLOCKER_BY_CLAIM_TYPE = {
    "compiler_correctness": "compiler_correctness_without_proof",
    "redteam_robustness": "redteam_adapter_or_coverage_gap",
    "forecasting": "calibration_missing",
    "hardware": "live_capture_missing",
    "performance": "runtime_bakeoff_missing",
    "proof_status": "bounded_surface_copy_needed",
    "external_theory": "claim_decomposition_missing",
    "ai_answer": "source_review_missing",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def priority_from_score(score: int) -> str:
    if score >= 80:
        return "critical"
    if score >= 60:
        return "high"
    if score >= 35:
        return "medium"
    return "low"


def score_packet(packet: dict[str, Any]) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []
    decision = packet["decision"]
    claim_type = packet["claimType"]
    lane = packet["sourceLane"]
    evidence_strength = packet["evidenceStrength"]
    if decision == "blocked_public_claim":
        score += 30
        reasons.append("blocked_public_claim:+30")
    elif decision == "human_review_required":
        score += 18
        reasons.append("human_review_required:+18")
    elif decision == "candidate_only":
        score += 10
        reasons.append("candidate_only:+10")
    elif decision == "approved_bounded_public_claim":
        score += 12
        reasons.append("bounded_public_approval_ready:+12")

    lane_weight = LANE_WEIGHTS.get(lane, 6)
    score += lane_weight
    reasons.append(f"lane:{lane}:+{lane_weight}")

    if evidence_strength in {"local_measurement_only", "fixture_only", "fixture_red_team_fail"}:
        score += 12
        reasons.append(f"evidence_gap:{evidence_strength}:+12")
    if evidence_strength == "none":
        score += 10
        reasons.append("no_evidence:+10")
    if evidence_strength == "small_checked_witness":
        score += 8
        reasons.append("near_bounded_surface:+8")
    if "generated_stub_validation" in packet.get("requiredValidators", []):
        score += 18
        reasons.append("clear_r12_unlock:+18")
    if "rampart_redteam_packet" in packet.get("requiredValidators", []):
        score += 14
        reasons.append("redteam_bridge:+14")
    if "calibration_ledger" in packet.get("requiredValidators", []):
        score += 12
        reasons.append("agent_calibration:+12")
    if "live_capture_packet" in packet.get("requiredValidators", []):
        score += 10
        reasons.append("hardware_capture:+10")
    if "holdout_runtime_bakeoff" in packet.get("requiredValidators", []):
        score += 10
        reasons.append("runtime_bakeoff:+10")
    if claim_type == "external_theory":
        score -= 12
        reasons.append("low_product_nearness_external_theory:-12")
    if claim_type == "ai_answer":
        score -= 4
        reasons.append("generic_intake_lower_priority:-4")
    return max(score, 0), reasons


def queue_item(packet: dict[str, Any]) -> dict[str, Any]:
    score, reasons = score_packet(packet)
    validators = packet.get("requiredValidators", ["human_review"])
    return {
        "rank": 0,
        "claimId": packet["claimId"],
        "claimType": packet["claimType"],
        "sourceLane": packet["sourceLane"],
        "decision": packet["decision"],
        "allowedSurface": packet["allowedSurface"],
        "evidenceStrength": packet["evidenceStrength"],
        "priority": priority_from_score(score),
        "score": score,
        "scoreReasons": reasons,
        "blockerCategory": BLOCKER_BY_CLAIM_TYPE.get(packet["claimType"], "unknown_blocker"),
        "nextValidator": validators[0],
        "allValidators": validators,
        "nextSprint": SPRINT_BY_CLAIM_TYPE.get(packet["claimType"], "manual_review"),
        "nextAction": packet["nextAction"],
        "claim": packet["claim"],
        "blockedClaims": packet.get("blockedClaims", []),
        "evidencePaths": packet.get("evidencePaths", []),
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_queue_items(review_packets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items = [queue_item(packet) for packet in review_packets]
    items.sort(key=lambda item: (-item["score"], item["claimId"]))
    for idx, item in enumerate(items, start=1):
        item["rank"] = idx
    return items


def summarize(items: list[dict[str, Any]]) -> dict[str, Any]:
    by_priority: dict[str, int] = {}
    by_lane: dict[str, int] = {}
    for item in items:
        by_priority[item["priority"]] = by_priority.get(item["priority"], 0) + 1
        by_lane[item["sourceLane"]] = by_lane.get(item["sourceLane"], 0) + 1
    return {
        "queueItemCount": len(items),
        "byPriority": by_priority,
        "byLane": by_lane,
        "topClaimId": items[0]["claimId"] if items else None,
        "topNextSprint": items[0]["nextSprint"] if items else None,
        "publicApprovalPerformed": False,
        "deployPerformed": False,
        "tradePerformed": False,
        "hardwareActionPerformed": False,
        "compilerBehaviorChanged": False,
        "claimFlagsAllFalse": all(all(value is False for value in item["claimFlags"].values()) for item in items),
    }


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "rh-a2-reviewer-priority-queue",
        "title": "RH-A2 Reviewer Priority Queue",
        "reviewDecision": "private_reviewer_queue_recorded",
        "validationStatus": "pass",
        "replayStatus": "not_applicable",
        "semanticStrength": "deterministic_priority_queue_no_public_approval_claim",
        "semanticReview": {
            "queueItemCount": payload["summary"]["queueItemCount"],
            "topClaimId": payload["summary"]["topClaimId"],
            "topNextSprint": payload["summary"]["topNextSprint"],
            "publicApprovalPerformed": False,
            "deployPerformed": False,
        },
        "claimBoundary": "Private reviewer planning queue only; no public approval, deployment, trading, hardware, or compiler behavior claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Ranks RH-A1 claim review packets by blocker severity, lane leverage, and validator readiness.",
            "Turns review packets into concrete next sprint recommendations.",
            "Keeps approval and action flags false.",
        ],
        "validationCommands": [
            "python python/scripts/rh_a2_reviewer_priority_queue.py --build --strict",
            "python -m pytest -q python/tests/test_rh_a2_reviewer_priority_queue.py",
        ],
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# RH-A2 Reviewer Priority Queue",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "RH-A2 ranks RH-A1 claim review packets into a private reviewer queue.",
        "",
        "## Queue",
        "",
        "| Rank | Claim | Priority | Score | Next sprint | Next validator |",
        "|---:|---|---|---:|---|---|",
    ]
    for item in payload["queue"]["items"]:
        lines.append(
            f"| {item['rank']} | `{item['claimId']}` | `{item['priority']}` | "
            f"{item['score']} | `{item['nextSprint']}` | `{item['nextValidator']}` |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Queue items: `{payload['summary']['queueItemCount']}`",
            f"- Top claim: `{payload['summary']['topClaimId']}`",
            f"- Top sprint: `{payload['summary']['topNextSprint']}`",
            f"- Public approval performed: `{payload['summary']['publicApprovalPerformed']}`",
            f"- Deploy performed: `{payload['summary']['deployPerformed']}`",
            f"- Trade performed: `{payload['summary']['tradePerformed']}`",
            f"- Hardware action performed: `{payload['summary']['hardwareActionPerformed']}`",
            f"- Compiler behavior changed: `{payload['summary']['compilerBehaviorChanged']}`",
            "",
            "## Boundary",
            "",
            "- Private planning queue only.",
            "- No automatic reviewer approval.",
            "- No deployment, trading, hardware operation, or compiler behavior change.",
            "",
        ]
    )
    return "\n".join(lines)


def command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    top = payload["queue"]["items"][:5]
    return {
        "schemaVersion": "monogate.command_feed.rh_a2.v0",
        "date": DATE,
        "title": "RH-A2 Reviewer Priority Queue",
        "status": payload["status"],
        "topItems": [
            {
                "rank": item["rank"],
                "claimId": item["claimId"],
                "priority": item["priority"],
                "nextSprint": item["nextSprint"],
                "nextValidator": item["nextValidator"],
            }
            for item in top
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid RH-A2 schema")
    if payload.get("status") != STATUS:
        raise ValueError("invalid RH-A2 status")
    items = payload["queue"]["items"]
    if len(items) < 9:
        raise ValueError("expected at least 9 queue items")
    ranks = [item["rank"] for item in items]
    if ranks != list(range(1, len(items) + 1)):
        raise ValueError("queue ranks must be contiguous")
    scores = [item["score"] for item in items]
    if scores != sorted(scores, reverse=True):
        raise ValueError("queue must be sorted by descending score")
    for key in [
        "publicApprovalPerformed",
        "deployPerformed",
        "tradePerformed",
        "hardwareActionPerformed",
        "compilerBehaviorChanged",
    ]:
        if payload["summary"][key] is not False:
            raise ValueError(f"{key} must remain false")
    if payload["summary"]["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    for item in items:
        for key, value in item.get("claimFlags", {}).items():
            if value is not False:
                raise ValueError(f"claim flag must remain false for {item['claimId']}: {key}")
    for key, value in payload.get("claimFlags", {}).items():
        if value is not False:
            raise ValueError(f"payload claim flag must remain false: {key}")


def build_queue(
    review_path: Path,
    out_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
) -> dict[str, Any]:
    review = load_json(review_path)
    items = build_queue_items(review["reviewPackets"])
    summary = summarize(items)
    queue = {
        "schemaVersion": QUEUE_SCHEMA_VERSION,
        "queueId": "rh-a2-reviewer-priority-queue",
        "generatedAt": DATE,
        "sourceReviewPath": str(review_path),
        "items": items,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "sourceReviewPath": str(review_path),
        "queue": queue,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    evidence = build_evidence_packet(payload)
    feed = command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    stamp = DATE.replace("-", "_")
    result_path = out_dir / f"rh_a2_reviewer_priority_queue_{stamp}.json"
    queue_path = out_dir / f"reviewer_priority_queue_{stamp}.json"
    report_path = report_dir / f"rh_a2_reviewer_priority_queue_{stamp}.md"
    evidence_path = evidence_dir / "rh_a2_reviewer_priority_queue.json"
    feed_path = command_feed_dir / f"rh_a2_reviewer_priority_queue_feed_{stamp}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    queue_path.write_text(json.dumps(queue, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "queue": queue,
        "evidence": evidence,
        "feed": feed,
        "result_path": str(result_path),
        "queue_path": str(queue_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument(
        "--review-path",
        type=Path,
        default=ROOT / f"python/results/rh_a1_universal_claim_review_harness/rh_a1_universal_claim_review_harness_{DATE.replace('-', '_')}.json",
    )
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/rh_a2_reviewer_priority_queue")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_queue(args.review_path, args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("RH_A2_REVIEWER_PRIORITY_QUEUE_OK")
    print(f"queue_items={built['payload']['summary']['queueItemCount']}")
    print(f"top_claim={built['payload']['summary']['topClaimId']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
