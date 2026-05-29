"""Tests for EML-ADV-PCC10 family-level synthesis."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_advantage_pcc10_family_synthesis import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_pcc10_synthesizes_five_families():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EML_ADV_PCC10_FAMILY_SYNTHESIS_PASS"
    assert payload["summary"]["sourceFamilyCount"] == 5
    assert payload["summary"]["profileCount"] >= 22
    assert {row["familyId"] for row in payload["families"]} == {
        "rc_decay",
        "gaussian",
        "damped_wave",
        "numpy_softplus",
        "clamp_guard",
    }


def test_pcc10_decision_map_keeps_runtime_and_public_claims_empty():
    payload = build_payload()
    decision = payload["decisionMap"]
    assert decision["runtimeWinsClaimed"] == []
    assert decision["publicClaimsAllowed"] == []
    assert "numpy_softplus" in decision["protectedRuntimeRequired"]
    assert "clamp_guard" in decision["guardGrammarRequired"]
    assert "damped_wave" in decision["partialEmlCoverage"]


def test_pcc10_summary_marks_pause_point_without_generalization_claim():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["recommendedPausePoint"] is True
    assert summary["representationHelpfulFamilies"] == 4
    assert summary["fullEmlCoverageFamilies"] == 2
    assert summary["partialEmlCoverageFamilies"] == 2
    assert summary["runtimeWinFamilies"] == 0
    assert summary["familyLevelGeneralizationClaim"] is False
    assert summary["publicReady"] is False


def test_pcc10_claim_flags_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_payload()
    assert all(value is False for value in payload["claimFlags"].values())


def test_pcc10_writes_json_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-ADV-PCC10")


def test_pcc10_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_advantage_pcc10_family_synthesis.py",
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
    assert "EML_ADV_PCC10_FAMILY_SYNTHESIS_OK" in proc.stdout
