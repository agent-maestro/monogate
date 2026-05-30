"""Tests for EML-S31 guard-owned clamp policy bakeoff."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import numpy as np

from scripts.eml_s31_guard_owned_clamp_policy_bakeoff import (
    CLAIM_FLAGS,
    POLICY_FORMS,
    build_outputs,
    build_payload,
    packet_for_form,
    profile_specs,
    reference_clamp,
    validate_packet,
    validate_payload,
)


def test_s31_builds_four_policy_forms():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EML_S31_GUARD_OWNED_CLAMP_POLICY_BAKEOFF_PASS"
    assert payload["summary"]["policyFormCount"] == 4
    assert {packet["formId"] for packet in payload["policyPackets"]} == set(POLICY_FORMS)


def test_s31_profile_grid_has_guard_boundary_stressors():
    specs = profile_specs()
    names = {spec["profile"] for spec in specs}
    assert "inside_guard_band" in names
    assert "boundary_crossing_window" in names
    assert "far_outside_guard_band" in names
    assert "noisy_boundary_inputs" in names


def test_s31_packets_have_four_profiles_two_dtypes():
    for form_id in POLICY_FORMS:
        packet = packet_for_form(form_id)
        validate_packet(packet)
        assert packet["summary"]["profileRunCount"] == 8
        assert {profile["dtype"] for profile in packet["profiles"]} == {"float64", "float32"}


def test_s31_reference_clamp_is_finite():
    for spec in profile_specs():
        ref = reference_clamp(spec, spec["x"])
        assert np.all(np.isfinite(ref))
        assert np.all(ref >= spec["lo"])
        assert np.all(ref <= spec["hi"])


def test_s31_recommends_guard_owned_boundary_and_keeps_caution():
    payload = build_payload()
    assert payload["summary"]["recommendedPolicyForm"] == "guard_owned_branch_boundary_surface"
    assert payload["recommendation"]["representationForm"] == "guard_owned_branch_boundary_surface"
    assert payload["recommendation"]["runtimeForm"] == "guard_owned_branch_boundary_surface"
    assert payload["recommendation"]["runtimeRole"] == "guard_policy_boundary_not_generic_runtime_lowering"
    assert payload["recommendation"]["teachingSearchForm"] == "semantic_clamp_baseline"
    assert "runtime_clamp_caution" in payload["recommendation"]["blockedOrCautionForms"]
    assert payload["recommendation"]["anchorReadiness"] == "not_ready_without_engine_guard_policy_row_and_anchor_packet"


def test_s31_records_semantic_mutation_without_runtime_claim():
    payload = build_payload()
    assert payload["summary"]["semanticMutationObserved"] is True
    for packet in payload["policyPackets"]:
        assert packet["summary"]["semanticMutationObserved"] is True
        assert packet["summary"]["semanticMutationSampleCount"] > 0
        assert packet["summary"]["runtimePerformanceClaim"] is False


def test_s31_claim_boundaries_remain_false():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["publicReady"] is False
    assert summary["publicPerformanceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert summary["broadEmlAdvantageClaim"] is False
    assert summary["sourceFamilyGeneralizationClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False


def test_s31_claim_flags_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload = build_payload()
    assert all(value is False for value in payload["claimFlags"].values())
    for packet in payload["policyPackets"]:
        assert all(value is False for value in packet["claimFlags"].values())


def test_s31_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    packet_paths = sorted((tmp_path / "packets").glob("*.json"))
    assert len(packet_paths) == 4
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-S31")


def test_s31_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_s31_guard_owned_clamp_policy_bakeoff.py",
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
    assert "EML_S31_GUARD_OWNED_CLAMP_POLICY_BAKEOFF_OK" in proc.stdout
