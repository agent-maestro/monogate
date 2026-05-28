"""Tests for RH-A2 reviewer priority queue."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.rh_a1_universal_claim_review_harness import build_harness
from scripts.rh_a2_reviewer_priority_queue import (
    CLAIM_FLAGS,
    build_queue,
    build_queue_items,
    score_packet,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[2]
RH_A1_FIXTURE = ROOT / "python/fixtures/review_harness/rh_a1_claims.json"


def build_review(tmp_path):
    return build_harness(
        RH_A1_FIXTURE,
        tmp_path / "rh_a1",
        tmp_path / "claim_packets",
        tmp_path / "reports",
        tmp_path / "evidence",
    )


def item_by_claim(items, claim_id: str):
    return next(item for item in items if item["claimId"] == claim_id)


def test_score_prioritizes_compiler_and_redteam_blockers(tmp_path):
    review = build_review(tmp_path)["payload"]
    packets = {packet["claimId"]: packet for packet in review["reviewPackets"]}
    compiler_score, compiler_reasons = score_packet(packets["r11-compiler-lowering-correctness"])
    redteam_score, redteam_reasons = score_packet(packets["builder-robust-to-forbidden-claim-injection"])
    ai_score, _ = score_packet(packets["ai-answer-ready-for-publication"])
    assert compiler_score > ai_score
    assert redteam_score > ai_score
    assert "lane:compiler:+18" in compiler_reasons
    assert "redteam_bridge:+14" in redteam_reasons


def test_prediction_market_claim_routes_to_outcome_resolver_after_pm_a1b(tmp_path):
    review = build_review(tmp_path)["payload"]
    items = build_queue_items(review["reviewPackets"])
    item = item_by_claim(items, "pm-a1-profitable-agent-claim")
    assert item["nextSprint"] == "PM-A1C outcome resolver fixture"
    assert item["nextValidator"] == "outcome_resolution_ledger"


def test_queue_items_are_ranked_by_descending_score(tmp_path):
    review = build_review(tmp_path)["payload"]
    items = build_queue_items(review["reviewPackets"])
    assert [item["rank"] for item in items] == list(range(1, len(items) + 1))
    assert [item["score"] for item in items] == sorted([item["score"] for item in items], reverse=True)


def test_build_queue_outputs_private_planning_artifacts(tmp_path):
    review = build_review(tmp_path)
    built = build_queue(
        Path(review["result_path"]),
        tmp_path / "rh_a2",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    payload = built["payload"]
    assert payload["status"] == "RH_A2_REVIEWER_PRIORITY_QUEUE_PASS"
    assert payload["summary"]["queueItemCount"] >= 9
    assert payload["summary"]["publicApprovalPerformed"] is False
    assert payload["summary"]["deployPerformed"] is False
    assert payload["summary"]["tradePerformed"] is False
    assert payload["summary"]["hardwareActionPerformed"] is False
    assert payload["summary"]["compilerBehaviorChanged"] is False
    validate_payload(payload)
    assert Path(built["result_path"]).exists()
    assert Path(built["queue_path"]).exists()
    assert Path(built["report_path"]).exists()
    assert Path(built["evidence_path"]).exists()
    assert Path(built["feed_path"]).exists()


def test_compiler_claim_routes_to_runtime_bakeoff_after_r12(tmp_path):
    review = build_review(tmp_path)
    payload = build_queue(
        Path(review["result_path"]),
        tmp_path / "rh_a2",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )["payload"]
    item = item_by_claim(payload["queue"]["items"], "r11-compiler-lowering-correctness")
    assert item["nextSprint"] == "R10F proof-assistant AST and guard model"
    assert item["nextValidator"] == "proof_assistant_ast_model"
    assert item["priority"] in {"high", "medium"}


def test_r12_candidate_routes_to_runtime_bakeoff(tmp_path):
    review = build_review(tmp_path)
    payload = build_queue(
        Path(review["result_path"]),
        tmp_path / "rh_a2",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )["payload"]
    item = item_by_claim(payload["queue"]["items"], "r12-generated-stubs-validate-on-fixtures")
    assert item["nextSprint"] == "R10F proof-assistant AST and guard model"
    assert item["nextValidator"] == "proof_assistant_ast_model"
    assert item["blockerCategory"] == "runtime_bakeoff_or_semantic_proof_missing"


def test_redteam_local_adapter_pass_routes_to_regression_guard(tmp_path):
    review = build_review(tmp_path)
    payload = build_queue(
        Path(review["result_path"]),
        tmp_path / "rh_a2",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )["payload"]
    item = item_by_claim(payload["queue"]["items"], "command-cockpit-robust-to-private-leakage")
    assert item["nextSprint"] == "RT-A3 red-team regression CI guard"
    assert item["nextValidator"] == "adapter_coverage_review"
    assert item["blockerCategory"] == "redteam_adapter_or_coverage_gap"


def test_machlib_bounded_approval_is_surface_work_not_blocker(tmp_path):
    review = build_review(tmp_path)
    payload = build_queue(
        Path(review["result_path"]),
        tmp_path / "rh_a2",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )["payload"]
    item = item_by_claim(payload["queue"]["items"], "machlib-subtraction-boundary-witness")
    assert item["nextSprint"] == "Atlas bounded public surfacing"
    assert item["allowedSurface"] == "public_bounded"
    assert item["blockerCategory"] == "bounded_surface_copy_needed"


def test_command_feed_contains_top_items_without_claim_flips(tmp_path):
    review = build_review(tmp_path)
    built = build_queue(
        Path(review["result_path"]),
        tmp_path / "rh_a2",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    feed = built["feed"]
    assert feed["schemaVersion"] == "monogate.command_feed.rh_a2.v0"
    assert 1 <= len(feed["topItems"]) <= 5
    assert all(value is False for value in feed["claimFlags"].values())


def test_claim_flags_are_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())


def test_generated_json_files_parse(tmp_path):
    review = build_review(tmp_path)
    built = build_queue(
        Path(review["result_path"]),
        tmp_path / "rh_a2",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for path in [built["result_path"], built["queue_path"], built["evidence_path"], built["feed_path"]]:
        json.loads(Path(path).read_text(encoding="utf-8"))


def test_cli_build_strict(tmp_path):
    review = build_review(tmp_path)
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/rh_a2_reviewer_priority_queue.py",
            "--build",
            "--review-path",
            review["result_path"],
            "--out-dir",
            str(tmp_path / "rh_a2"),
            "--report-dir",
            str(tmp_path / "reports"),
            "--evidence-dir",
            str(tmp_path / "evidence"),
            "--command-feed-dir",
            str(tmp_path / "feeds"),
            "--strict",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "RH_A2_REVIEWER_PRIORITY_QUEUE_OK" in proc.stdout
