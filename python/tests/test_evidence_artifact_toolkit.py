"""Tests for the small shared evidence artifact toolkit."""

from __future__ import annotations

import pytest

from scripts.evidence_artifact_toolkit import (
    assert_claim_flags_bounded,
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
)


CLAIM_FLAGS = {
    "helper_seeded": True,
    "public_ready": False,
    "runtime_performance_claim": False,
}


def test_claim_flagged_packet_builder_bounds_claim_flags():
    payload = build_claim_flagged_packet(
        schema_version="test.schema.v0",
        artifact_id="test-artifact",
        artifact_type="test_artifact",
        status="PASS",
        date="2026-06-06",
        summary={"ok": True},
        claim_flags=CLAIM_FLAGS,
        true_claim_flags={"helper_seeded"},
        non_claims=["No public claim."],
        extra={"sourceArtifact": "source-a"},
    )
    assert payload["artifactId"] == "test-artifact"
    assert payload["claimFlags"]["helper_seeded"] is True
    assert payload["claimFlags"]["public_ready"] is False
    assert payload["sourceArtifact"] == "source-a"


def test_claim_flagged_packet_builder_rejects_unexpected_true_flag():
    flags = {**CLAIM_FLAGS, "runtime_performance_claim": True}
    with pytest.raises(ValueError, match="runtime_performance_claim"):
        build_claim_flagged_packet(
            schema_version="test.schema.v0",
            artifact_id="test-artifact",
            artifact_type="test_artifact",
            status="PASS",
            date="2026-06-06",
            summary={},
            claim_flags=flags,
            true_claim_flags={"helper_seeded"},
            non_claims=["No public claim."],
        )


def test_claim_flagged_packet_builder_rejects_empty_nonclaims():
    with pytest.raises(ValueError, match="non_claims"):
        build_claim_flagged_packet(
            schema_version="test.schema.v0",
            artifact_id="test-artifact",
            artifact_type="test_artifact",
            status="PASS",
            date="2026-06-06",
            summary={},
            claim_flags=CLAIM_FLAGS,
            true_claim_flags={"helper_seeded"},
            non_claims=[],
        )


def test_assert_claim_flags_bounded_can_require_false_flags():
    assert_claim_flags_bounded(CLAIM_FLAGS, {"helper_seeded"}, required_false_flags={"public_ready"})
    with pytest.raises(ValueError, match="missing_flag"):
        assert_claim_flags_bounded(CLAIM_FLAGS, {"helper_seeded"}, required_false_flags={"missing_flag"})


def test_evidence_packet_builder_uses_public_packet_shape():
    evidence = build_evidence_packet(
        artifact_id="test-artifact",
        artifact_type="test_artifact",
        semantic_strength="private_test_only",
        source="python/results/test.json",
        summary={"ok": True},
        claim_flags=CLAIM_FLAGS,
        non_claims=["No public claim."],
    )
    assert evidence["schemaVersion"] == "monogate.evidence_public_packet.v0"
    assert evidence["validationStatus"] == "pass"
    assert evidence["semanticStrength"] == "private_test_only"


def test_markdown_report_builder_renders_summary_sections_and_nonclaims():
    report = render_markdown_report(
        title="Tiny Report",
        status="PASS",
        summary_rows=[("helper count", 3)],
        sections=[("Helpers", ["- one", "- two"])],
        non_claims=["No runtime claim."],
    )
    assert report.startswith("# Tiny Report")
    assert "- helper count: `3`" in report
    assert "## Helpers" in report
    assert "- No runtime claim." in report


def test_command_feed_builder_rejects_base_field_collision():
    feed = build_command_feed(
        feed_id="feed",
        date="2026-06-06",
        status="PASS",
        next_action="Continue.",
        claim_flags=CLAIM_FLAGS,
        fields={"sourceArtifact": "source-a"},
    )
    assert feed["sourceArtifact"] == "source-a"
    with pytest.raises(ValueError, match="collides"):
        build_command_feed(
            feed_id="feed",
            date="2026-06-06",
            status="PASS",
            next_action="Continue.",
            claim_flags=CLAIM_FLAGS,
            fields={"status": "BAD"},
        )
