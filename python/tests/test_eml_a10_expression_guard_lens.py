"""Tests for EML-A10 expression guard lens."""

from __future__ import annotations

import subprocess
import sys

from scripts.eml_a10_expression_guard_lens import CLAIM_FLAGS, build_lens, validate_payload


def build_tmp(tmp_path):
    return build_lens(
        __import__("pathlib").Path("python/fixtures/eml_expression_packets"),
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )


def packet_by_program(payload, program_id):
    return next(packet for packet in payload["guardLensPackets"] if packet["programId"] == program_id)


def test_expression_guard_lens_outputs_packets(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    assert payload["status"] == "EML_A10_EXPRESSION_GUARD_LENS_PASS"
    assert payload["summary"]["packetCount"] >= 3
    validate_payload(payload)


def test_softplus_recommends_protected_lowering(tmp_path):
    packet = packet_by_program(build_tmp(tmp_path)["payload"], "softplus_pair_v0")
    assert packet["decision"] == "recommend_protected_lowering"
    assert "lower_logaddexp_softplus_v0" in packet["matchedRuleIds"]


def test_sigmoid_blocks_missing_domain_guard(tmp_path):
    packet = packet_by_program(build_tmp(tmp_path)["payload"], "sigmoid_derivative_v0")
    assert packet["decision"] == "block_missing_domain_guard"


def test_claim_flags_remain_false(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert payload["summary"]["compilerBehaviorChanged"] is False
    assert payload["summary"]["compilerCorrectnessClaim"] is False
    assert payload["summary"]["productionReady"] is False
    assert payload["summary"]["claimFlagsAllFalse"] is True


def test_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [sys.executable, "python/scripts/eml_a10_expression_guard_lens.py", "--build", "--out-dir", str(tmp_path / "results"), "--lens-packet-dir", str(tmp_path / "packets"), "--report-dir", str(tmp_path / "reports"), "--evidence-dir", str(tmp_path / "evidence"), "--command-feed-dir", str(tmp_path / "feeds"), "--strict"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "EML_A10_EXPRESSION_GUARD_LENS_OK" in proc.stdout
