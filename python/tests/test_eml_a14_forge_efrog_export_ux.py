"""Tests for EML-A14 Forge/eFrog export UX."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_a14_forge_efrog_export_ux import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_a14_exports_semantic_cases():
    payload, packets = build_payload()
    validate_payload(payload, packets)
    assert payload["status"] == "EML_A14_FORGE_EFROG_EXPORT_UX_PASS"
    assert payload["summary"]["exportPacketCount"] == 7
    assert payload["summary"]["semanticPassCount"] == 7
    assert len(packets) == 7


def test_a14_packets_record_roundtrip_link_status():
    _payload, packets = build_payload()
    linked = [packet for packet in packets if packet["roundtripLinkStatus"] == "linked_by_canonical_eml_hash"]
    semantic_only = [packet for packet in packets if packet["roundtripLinkStatus"] == "semantic_comparison_only"]
    assert len(linked) == 5
    assert len(semantic_only) == 2
    for packet in packets:
        assert packet["roundtripPassCount"] == packet["roundtripCaseCount"]
        assert set(packet["forgeTargets"]) == {"javascript", "python"}
        assert packet["canonicalEmlHash"].startswith("sha256:")


def test_a14_carries_family_interpretation_without_broad_claim():
    payload, packets = build_payload()
    family_ids = {packet["emlSurfaceSummary"]["familyId"] for packet in packets}
    assert "rc_decay" in family_ids
    assert "gaussian" in family_ids
    assert "stretched_exponential" in family_ids
    assert payload["summary"]["broadEmlAdvantageClaim"] is False
    assert payload["summary"]["runtimePerformanceClaim"] is False


def test_a14_builder_preset_is_private_candidate_only():
    payload, _packets = build_payload()
    preset = payload["builderPreset"]
    assert preset["artifactType"] == "compiler_decompiler"
    assert preset["packetType"] == "monogate.eml_forge_efrog_export_packet.v0"
    assert "Keep private" in preset["defaultReviewerAction"]


def test_a14_claim_flags_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload, packets = build_payload()
    assert all(value is False for value in payload["claimFlags"].values())
    for packet in packets:
        assert all(value is False for value in packet["claimFlags"].values())


def test_a14_writes_outputs_and_export_packets(tmp_path):
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
    assert len(packet_paths) == 7
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-A14")


def test_a14_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_a14_forge_efrog_export_ux.py",
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
    assert "EML_A14_FORGE_EFROG_EXPORT_UX_OK" in proc.stdout
