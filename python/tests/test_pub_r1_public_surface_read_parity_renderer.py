"""Tests for PUB-R1 public-surface read parity renderer."""

from __future__ import annotations

import pytest

# Blanket-marked heavy: CLI-contract test (subprocess.run of a
# script that loads large JSON evidence). Skipped from the fast
# dev loop via `pytest -m "not heavy"`; runs in CI by default.
# A follow-up measurement pass will UN-mark individual fast files.
pytestmark = pytest.mark.heavy

import json
import re
from pathlib import Path

from scripts.pub_r0_brake_side_ledger_generator import build_payload as build_pub_r0_payload
from scripts.pub_r1_public_surface_read_parity_renderer import (
    CLAIM_FLAGS,
    CONTENT_CLASSES,
    LIVE_URL,
    PAGE_RELATIVE_PATH,
    TRUE_CLAIM_FLAGS,
    build_outputs,
    build_payload,
    build_time_drift_check,
    render_html,
    sha256_hex,
    validate_payload,
    write_page,
)

FAKE_LEAN_TEXT = (
    "  LEAN:        468 theorems, 5 sorries, 18 files (live)\n"
    "  MACHLIB:     3418 records, 279 files (8 core / 271 discovered), "
    "0 core sorries, 222 discovered sorries, 18971 lines (live)\n"
)


def _pub_r0() -> dict:
    return build_pub_r0_payload(lean_status_text=FAKE_LEAN_TEXT)


def test_pub_r1_renders_html_deterministically():
    p1 = _pub_r0()
    html1 = render_html(p1["ledger"], pub_r0_artifact_id=p1["artifactId"], pub_r0_date=p1["date"])
    html2 = render_html(p1["ledger"], pub_r0_artifact_id=p1["artifactId"], pub_r0_date=p1["date"])
    assert html1 == html2, "render must be deterministic"
    assert sha256_hex(html1.encode("utf-8")) == sha256_hex(html2.encode("utf-8"))


def test_pub_r1_html_contains_all_five_content_classes_and_no_script_tags():
    p1 = _pub_r0()
    html_text = render_html(
        p1["ledger"], pub_r0_artifact_id=p1["artifactId"], pub_r0_date=p1["date"]
    )
    # Five content classes via section headings
    for heading in [
        "Held lanes",
        "Retracted claims",
        "Negative results",
        "Standing claim rule",
        "Lean status",
    ]:
        assert heading in html_text, f"missing {heading}"
    # No JavaScript whatsoever
    assert "<script" not in html_text.lower()
    assert "javascript:" not in html_text.lower()
    assert " onclick=" not in html_text.lower()
    assert " onload=" not in html_text.lower()
    # Doctype + lang
    assert html_text.startswith("<!doctype html>")
    assert 'lang="en"' in html_text


def test_pub_r1_html_includes_ledger_rows():
    p1 = _pub_r0()
    html_text = render_html(
        p1["ledger"], pub_r0_artifact_id=p1["artifactId"], pub_r0_date=p1["date"]
    )
    # Every held lane appears
    for row in p1["ledger"]["heldLanes"]:
        assert row["laneId"] in html_text
        assert row["holdingArtifactId"] in html_text
    # Every retracted + negative claim id appears
    for row in p1["ledger"]["retractedClaims"] + p1["ledger"]["negativeResults"]:
        assert row["claimId"] in html_text
    # Standing rule appears verbatim
    assert p1["ledger"]["standingClaimRule"] in html_text
    # Lean status numbers appear
    ls = p1["ledger"]["leanStatus"]
    assert f">{ls['leanTheoremCount']}<" in html_text
    assert f">{ls['leanSorryCount']}<" in html_text


def test_pub_r1_payload_records_byte_length_and_sha256():
    payload = build_payload(pub_r0_payload=_pub_r0(), skip_drift_check=True)
    validate_payload(payload)
    summary = payload["summary"]
    assert summary["contentClassCount"] == 5
    assert tuple(summary["contentClasses"]) == CONTENT_CLASSES
    assert summary["pageRelativePath"] == PAGE_RELATIVE_PATH
    assert summary["liveUrl"] == LIVE_URL
    assert re.fullmatch(r"[0-9a-f]{64}", summary["expectedHtmlSha256"])
    assert summary["expectedHtmlByteLength"] > 0
    assert payload["renderedHtmlSha256"] == summary["expectedHtmlSha256"]


def test_pub_r1_write_page_and_drift_check_roundtrip(tmp_path):
    p1 = _pub_r0()
    page_path = tmp_path / "evidence-status" / "index.html"
    out_path, html_text, sha = write_page(pub_r0_payload=p1, output_path=page_path)
    assert out_path == page_path
    assert page_path.read_text(encoding="utf-8") == html_text
    drift = build_time_drift_check(pub_r0_payload=p1, page_path=page_path)
    assert drift["drift"] is False
    assert drift["expectedSha256"] == sha
    assert drift["actualSha256"] == sha


def test_pub_r1_drift_check_detects_modified_page(tmp_path):
    p1 = _pub_r0()
    page_path = tmp_path / "evidence-status" / "index.html"
    write_page(pub_r0_payload=p1, output_path=page_path)
    # Inject a tampering edit
    page_path.write_text(
        page_path.read_text(encoding="utf-8") + "<!-- tampered -->", encoding="utf-8"
    )
    drift = build_time_drift_check(pub_r0_payload=p1, page_path=page_path)
    assert drift["drift"] is True
    assert drift["expectedSha256"] != drift["actualSha256"]


def test_pub_r1_drift_check_detects_missing_page(tmp_path):
    p1 = _pub_r0()
    missing = tmp_path / "evidence-status" / "index.html"  # never written
    drift = build_time_drift_check(pub_r0_payload=p1, page_path=missing)
    assert drift["drift"] is True
    assert drift["actualSha256"] == ""


def test_pub_r1_boundaries_closed():
    payload = build_payload(pub_r0_payload=_pub_r0(), skip_drift_check=True)
    summary = payload["summary"]
    assert summary["liveDeployExecuted"] is False
    assert summary["postDeployProbePassed"] is False
    assert summary["publicSurfaceUpdated"] is False
    assert summary["pagePushedToRemote"] is False
    assert summary["additionalContentClassAdded"] is False
    assert summary["laptopOwnedRepoTouched"] is False


def test_pub_r1_blocks_publication_and_substance_claims():
    payload = build_payload(pub_r0_payload=_pub_r0(), skip_drift_check=True)
    for key in [
        "live_deploy_executed",
        "post_deploy_probe_passed",
        "public_surface_updated",
        "page_pushed_to_remote",
        "additional_content_class_added",
        "dashboard_ui_created",
        "renderer_correctness_claim",
        "ledger_completeness_claim",
        "training_cost_estimator_reopened",
        "product_roadmap_reopened",
        "atlas_public_promotion",
        "public_math_promotion",
        "d110_started",
        "reviewer_response_consumed",
        "reviewer_approval_recorded",
        "electronics_inbox_reopened",
        "electronics_repo_touched",
        "laptop_owned_repo_touched",
        "machlib_file_changed",
        "lean_typecheck_performed",
        "runtime_lowering_changed",
        "runtime_performance_claim",
        "compiler_correctness_claim",
        "hardware_readiness_claim",
        "silicon_readiness_claim",
        "broad_eml_advantage_claim",
    ]:
        assert payload["claimFlags"][key] is False


def test_pub_r1_claim_flags_are_renderer_only():
    payload = build_payload(pub_r0_payload=_pub_r0(), skip_drift_check=True)
    for key in TRUE_CLAIM_FLAGS:
        assert CLAIM_FLAGS[key] is True
        assert payload["claimFlags"][key] is True
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS:
            assert value is False


def test_pub_r1_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
        pub_r0_payload=_pub_r0(),
        skip_drift_check=True,
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# PUB-R1")
    assert "Content Classes" in report
    assert "build-time drift" in report
