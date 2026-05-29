"""Tests for EML-A15 Glass Box evidence mount handoff."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_a15_glassbox_evidence_mount import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_a15_builds_six_mount_cards():
    payload, cards = build_payload()
    validate_payload(payload, cards)
    assert payload["status"] == "EML_A15_GLASSBOX_EVIDENCE_MOUNT_HANDOFF_PASS"
    assert payload["summary"]["mountCardCount"] == 6
    assert len(cards) == 6


def test_a15_records_engine_dirty_constraint_without_modification():
    payload, _cards = build_payload()
    assert payload["engineWorktree"]["status"] == "dirty_not_modified_by_a15"
    assert payload["summary"]["engineDirtyPathCount"] >= 1
    assert payload["summary"]["engineFilesModifiedByA15"] == 0
    assert payload["claimFlags"]["engine_behavior_changed"] is False
    assert payload["claimFlags"]["engine_files_modified"] is False


def test_a15_mount_cards_preserve_a14_link_statuses():
    _payload, cards = build_payload()
    linked = [card for card in cards if card["roundtripLinkStatus"] == "linked_by_canonical_eml_hash"]
    semantic_only = [card for card in cards if card["roundtripLinkStatus"] == "semantic_comparison_only"]
    assert len(linked) == 4
    assert len(semantic_only) == 2
    for card in cards:
        assert card["transitionLink"]["linkMode"] == "handoff_only"
        assert card["glassBoxSlot"]["surface"] == "private_hud_evidence_card"


def test_a15_adapter_contract_has_required_fields():
    payload, _cards = build_payload()
    contract = payload["adapterContract"]
    assert contract["targetSurface"] == "Monogate Engine Glass Box private HUD"
    for field in ["mountCardId", "sourceExportId", "canonicalEmlHash", "blockedClaims"]:
        assert field in contract["requiredFields"]
    assert "never imply runtime/proof/public approval" in contract["expectedUiBehavior"]


def test_a15_claim_flags_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload, cards = build_payload()
    assert all(value is False for value in payload["claimFlags"].values())
    for card in cards:
        assert all(value is False for value in card["claimFlags"].values())


def test_a15_writes_outputs_and_mount_cards(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "cards",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    card_paths = sorted((tmp_path / "cards").glob("*.json"))
    assert len(card_paths) == 6
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-A15")


def test_a15_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_a15_glassbox_evidence_mount.py",
            "--build",
            "--out-dir",
            str(tmp_path / "results"),
            "--card-dir",
            str(tmp_path / "cards"),
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
    assert "EML_A15_GLASSBOX_EVIDENCE_MOUNT_OK" in proc.stdout
