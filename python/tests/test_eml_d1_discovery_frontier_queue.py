"""Tests for EML-D1 discovery frontier queue."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_d1_discovery_frontier_queue import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_d1_records_three_research_doors():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EML_D1_DISCOVERY_FRONTIER_QUEUE_PASS"
    assert payload["summary"]["candidateCount"] == 12
    assert payload["summary"]["doorCount"] == 3
    assert payload["summary"]["byDoor"]["identity_discovery"] >= 3
    assert payload["summary"]["byDoor"]["holdout_search"] >= 3
    assert payload["summary"]["byDoor"]["failure_atlas"] >= 3


def test_d1_top_candidates_are_ranked_and_ready():
    payload = build_payload()
    top_ids = payload["summary"]["topCandidateIds"]
    assert len(top_ids) == 3
    candidates = {item["candidateId"]: item for item in payload["frontierCandidates"]}
    assert "subtraction_boundary_family_v1" in candidates
    assert "constants_zero_one_e_boundary_v0" in candidates
    for candidate_id in top_ids:
        assert candidates[candidate_id]["priorityScore"] >= 38
        assert candidates[candidate_id]["frontierStatus"] == "ready_for_d2_trial"


def test_d1_contains_failure_atlas_controls():
    payload = build_payload()
    failure_ids = {
        item["candidateId"]
        for item in payload["frontierCandidates"]
        if item["door"] == "failure_atlas"
    }
    assert "ordinary_polynomial_failure_v0" in failure_ids
    assert "deep_tree_stability_failure_v1" in failure_ids
    assert "expm1_failure_boundary_v1" in failure_ids
    assert "logaddexp_failure_boundary_v1" in failure_ids


def test_d1_claim_flags_remain_false():
    payload = build_payload()
    assert payload["summary"]["candidateTestPerformed"] is False
    assert payload["summary"]["candidateProved"] is False
    assert payload["summary"]["emlAdvantageProved"] is False
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())
    for candidate in payload["frontierCandidates"]:
        assert all(value is False for value in candidate["claimFlags"].values())


def test_d1_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-D1")


def test_d1_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_d1_discovery_frontier_queue.py",
            "--build",
            "--out-dir",
            str(tmp_path / "results"),
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
    assert "EML_D1_DISCOVERY_FRONTIER_QUEUE_OK" in proc.stdout
