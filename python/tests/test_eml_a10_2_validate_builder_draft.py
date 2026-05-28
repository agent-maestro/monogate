"""Tests for EML-A10.2 local builder draft validation."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from scripts.eml_a10_2_validate_builder_draft import build_validation, validate_payload


FIXTURE = Path("python/fixtures/eml_expression_packets/softplus_pair_v0.json")


def build_tmp(tmp_path):
    return build_validation(
        FIXTURE,
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )


def test_builder_draft_validator_records_guard_decision(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    assert payload["status"] == "EML_A10_2_BUILDER_DRAFT_VALIDATION_PASS"
    assert payload["validationPacket"]["programId"] == "softplus_pair_v0"
    assert payload["validationPacket"]["decision"] == "recommend_protected_lowering"
    assert payload["validationPacket"]["supportingEvidenceArtifacts"][0]["artifactId"] == "eml-a11-2-protected-lowering-benchmark"
    validate_payload(payload)


def test_builder_draft_validator_keeps_claims_false(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    packet = payload["validationPacket"]
    assert packet["compilerBehaviorChanged"] is False
    assert packet["compilerCorrectnessClaim"] is False
    assert packet["productionReady"] is False
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert payload["summary"]["supportingEvidenceCount"] == 1


def test_builder_draft_validator_writes_packet(tmp_path):
    built = build_tmp(tmp_path)
    assert Path(built["packet_path"]).exists()
    assert Path(built["result_path"]).exists()
    assert Path(built["evidence_path"]).exists()


def test_builder_draft_validator_cli(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_a10_2_validate_builder_draft.py",
            str(FIXTURE),
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
    assert "EML_A10_2_BUILDER_DRAFT_VALIDATION_OK" in proc.stdout
