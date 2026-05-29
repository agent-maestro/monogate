"""Tests for EML-S23 sigmoid/logistic dedicated holdout."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import numpy as np

from scripts.eml_s23_sigmoid_logistic_holdout import (
    CLAIM_FLAGS,
    build_holdout_packet,
    build_outputs,
    build_payload,
    eml_sigmoid_form,
    profile_specs,
    stable_sigmoid_source,
    validate_holdout_packet,
    validate_payload,
)


def test_s23_builds_sigmoid_holdout_payload():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EML_S23_SIGMOID_LOGISTIC_HOLDOUT_PASS"
    assert payload["s22SelectedPromotionFamily"] == "sigmoid_logistic"
    assert payload["summary"]["sourceFamily"] == "stable_sigmoid"


def test_s23_holdout_profiles_pass_and_are_bounded():
    packet = build_holdout_packet()
    validate_holdout_packet(packet)
    assert packet["summary"]["profileCount"] == 4
    assert packet["summary"]["passingProfiles"] == 4
    assert packet["summary"]["allProfilesBounded"] is True
    assert packet["summary"]["overflowBoundaryProfileCount"] == 1
    assert packet["summary"]["runtimeWitnessedObligationCount"] == 2


def test_s23_eml_and_source_forms_match_on_profiles():
    for spec in profile_specs():
        source = stable_sigmoid_source(spec["x"])
        eml = eml_sigmoid_form(spec["x"])
        np.testing.assert_allclose(eml, source, rtol=1.0e-12, atol=1.0e-12)
        assert np.all(source >= 0.0)
        assert np.all(source <= 1.0)


def test_s23_links_a13_a13_2_a14_and_s20():
    payload = build_payload()
    assert payload["summary"]["roundtripPacketCount"] == 2
    assert payload["summary"]["roundtripPassCount"] == 2
    assert payload["summary"]["semanticComparisonPass"] is True
    assert payload["summary"]["exportRoundtripLinked"] is True
    assert payload["summary"]["s20PrimaryStyle"] == "eml_native"
    assert payload["a14Export"]["familyId"] == "stable_sigmoid"


def test_s23_claim_boundaries_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["publicReady"] is False
    assert summary["broadEmlAdvantageClaim"] is False
    assert summary["sourceFamilyGeneralizationClaim"] is False
    assert summary["sigmoidGeneralizationClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False


def test_s23_claim_flags_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_payload()
    assert all(value is False for value in payload["claimFlags"].values())
    assert all(value is False for value in payload["holdoutPacket"]["claimFlags"].values())


def test_s23_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-S23")


def test_s23_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_s23_sigmoid_logistic_holdout.py",
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
    assert "EML_S23_SIGMOID_LOGISTIC_HOLDOUT_OK" in proc.stdout
