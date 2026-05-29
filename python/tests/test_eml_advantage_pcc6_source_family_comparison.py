"""Tests for EML-ADV-PCC6 source-family comparison."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_advantage_pcc6_source_family_comparison import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_pcc6_compares_two_source_families():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EML_ADV_PCC6_SOURCE_FAMILY_COMPARISON_PASS"
    assert payload["summary"]["sourceFamilyCount"] == 2
    assert payload["summary"]["profileCount"] >= 8
    assert payload["summary"]["passingProfiles"] == payload["summary"]["profileCount"]
    family_ids = {family["familyId"] for family in payload["families"]}
    assert family_ids == {"rc_decay", "gaussian"}


def test_pcc6_classifies_semantic_representation_not_runtime_win():
    payload = build_payload()
    assert payload["summary"]["semanticRepresentationTieFamilies"] == 2
    assert payload["summary"]["runtimeWinFamilies"] == 0
    assert payload["summary"]["standardRuntimeRecommendedFamilies"] == 2
    for family in payload["families"]:
        assert family["classification"] == "semantic_search_representation_tie_not_runtime_win"
        assert family["runtimeRecommendation"] == "prefer_standard_or_protected_runtime_form_until_runtime_benchmarks_exist"


def test_pcc6_claim_flags_remain_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_payload()
    for key in [
        "broadEmlAdvantageClaim",
        "sourceFamilyGeneralizationClaim",
        "runtimePerformanceClaim",
        "noiseRobustnessGeneralClaim",
        "predictionAccuracyClaim",
        "publicReady",
    ]:
        assert payload["summary"][key] is False
    assert all(value is False for value in payload["claimFlags"].values())


def test_pcc6_writes_json_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-ADV-PCC6")


def test_pcc6_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_advantage_pcc6_source_family_comparison.py",
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
    assert "EML_ADV_PCC6_SOURCE_FAMILY_COMPARISON_OK" in proc.stdout
