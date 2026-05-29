"""Tests for EML-S22 source-family generalization map."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_s22_source_family_generalization_map import (
    CLAIM_FLAGS,
    DECISION_RULE,
    build_candidates,
    build_outputs,
    build_payload,
    validate_payload,
    validate_promotion_packet,
)


def test_s22_builds_three_family_map():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EML_S22_SOURCE_FAMILY_MAP_PASS"
    assert payload["summary"]["candidateFamilyCount"] == 3
    assert {candidate["familyId"] for candidate in payload["candidateFamilies"]} == {
        "sigmoid_logistic",
        "damped_oscillator",
        "softplus_logsumexp",
    }


def test_s22_decision_rule_has_expected_fields():
    assert DECISION_RULE["scale"] == "0_to_5_each"
    assert DECISION_RULE["fields"] == [
        "representationCompactness",
        "searchFriendliness",
        "semanticPreservation",
        "runtimeStability",
        "lowGuardBurden",
        "decompilerReadability",
        "roundtripMaturity",
    ]


def test_s22_scores_are_deterministic_and_ordered():
    first = build_candidates()
    second = build_candidates()
    assert first == second
    scores = {candidate["familyId"]: candidate["promotionScore"] for candidate in first}
    assert scores["sigmoid_logistic"] > scores["damped_oscillator"]
    assert scores["sigmoid_logistic"] > scores["softplus_logsumexp"]


def test_s22_promotes_exactly_one_next_holdout_candidate():
    payload = build_payload()
    promotion = payload["promotionPacket"]
    validate_promotion_packet(promotion)
    assert payload["summary"]["selectedPromotionFamily"] == "sigmoid_logistic"
    assert payload["summary"]["promoteNextSourceFamilyHoldoutCount"] == 1
    assert promotion["decisionLane"] == "promote_next_source_family_holdout"
    assert "overflow-boundary evidence" in payload["nextResearchQuestion"]
    assert "dedicated eFrog holdout trial" in promotion["requiredNextEvidence"][0]


def test_s22_carries_evidence_from_prior_lanes():
    payload = build_payload()
    by_family = {candidate["familyId"]: candidate for candidate in payload["candidateFamilies"]}
    assert by_family["sigmoid_logistic"]["semanticEvidence"]["comparisonStatus"] == "pass"
    assert by_family["damped_oscillator"]["semanticEvidence"]["allProfilesPass"] is True
    assert by_family["softplus_logsumexp"]["semanticEvidence"]["allProtectedProfilesFinite"] is True


def test_s22_claim_boundaries_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["publicReady"] is False
    assert summary["broadEmlAdvantageClaim"] is False
    assert summary["sourceFamilyGeneralizationClaim"] is False
    assert summary["familyLevelGeneralizationClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False


def test_s22_claim_flags_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_payload()
    assert all(value is False for value in payload["claimFlags"].values())
    assert all(value is False for value in payload["promotionPacket"]["claimFlags"].values())


def test_s22_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "packet_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-S22")


def test_s22_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_s22_source_family_generalization_map.py",
            "--build",
            "--out-dir",
            str(tmp_path / "results"),
            "--packet-dir",
            str(tmp_path / "packets"),
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
    assert "EML_S22_SOURCE_FAMILY_MAP_OK" in proc.stdout
