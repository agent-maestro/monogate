"""Tests for EML-S20 style atlas."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_s20_style_atlas import (
    CLAIM_FLAGS,
    STYLE_DEFINITIONS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_s20_builds_six_style_packets():
    payload, packets = build_payload()
    validate_payload(payload, packets)
    assert payload["status"] == "EML_S20_STYLE_ATLAS_PASS"
    assert payload["summary"]["stylePacketCount"] == 6
    assert len(packets) == 6


def test_s20_defines_expected_style_vocabulary():
    assert set(STYLE_DEFINITIONS) == {
        "eml_native",
        "eml_partial",
        "guard_owned",
        "standard_preferred",
        "semantic_only",
    }
    for definition in STYLE_DEFINITIONS.values():
        assert definition["meaning"]
        assert definition["reviewRule"]


def test_s20_classifies_current_export_families():
    payload, packets = build_payload()
    styles_by_family = {packet["familyId"]: packet["primaryStyle"] for packet in packets}
    assert styles_by_family["gaussian"] == "eml_native"
    assert styles_by_family["rc_decay"] == "eml_native"
    assert styles_by_family["numpy_softplus"] == "eml_partial"
    assert styles_by_family["clamp_guard"] == "guard_owned"
    assert payload["summary"]["emlNativePrimaryCount"] == 3
    assert payload["summary"]["emlPartialPrimaryCount"] == 1
    assert payload["summary"]["guardOwnedPrimaryCount"] == 1
    assert payload["summary"]["standardPreferredPrimaryCount"] == 1


def test_s20_marks_semantic_only_without_roundtrip_claim():
    payload, packets = build_payload()
    semantic_only = [packet for packet in packets if "semantic_only" in packet["styleTags"]]
    assert payload["summary"]["semanticOnlyTagCount"] == 2
    assert len(semantic_only) == 2
    for packet in semantic_only:
        assert packet["roundtripLinkStatus"] == "semantic_comparison_only"
        assert "roundtrip evidence" in packet["reviewInstruction"] or packet["primaryStyle"] != "semantic_only"


def test_s20_carries_private_boundaries():
    payload, packets = build_payload()
    assert payload["summary"]["publicReady"] is False
    assert payload["summary"]["broadEmlAdvantageClaim"] is False
    assert payload["summary"]["runtimePerformanceClaim"] is False
    assert payload["summary"]["compilerCorrectnessClaim"] is False
    assert payload["summary"]["formalEquivalenceClaim"] is False
    for packet in packets:
        assert "broad_eml_advantage" in packet["blockedClaims"]
        assert "public_readiness" in packet["blockedClaims"]


def test_s20_claim_flags_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload, packets = build_payload()
    assert all(value is False for value in payload["claimFlags"].values())
    for packet in packets:
        assert all(value is False for value in packet["claimFlags"].values())


def test_s20_style_for_packet_is_deterministic():
    _payload, packets = build_payload()
    first = [(packet["stylePacketId"], packet["primaryStyle"], tuple(packet["styleTags"])) for packet in packets]
    _payload_again, packets_again = build_payload()
    second = [(packet["stylePacketId"], packet["primaryStyle"], tuple(packet["styleTags"])) for packet in packets_again]
    assert first == second


def test_s20_writes_outputs_and_packets(tmp_path):
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
    assert len(packet_paths) == 6
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-S20")


def test_s20_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_s20_style_atlas.py",
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
    assert "EML_S20_STYLE_ATLAS_OK" in proc.stdout
