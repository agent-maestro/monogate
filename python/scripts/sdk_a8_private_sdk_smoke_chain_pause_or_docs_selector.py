#!/usr/bin/env python3
"""SDK-A8 private SDK smoke chain pause or docs selector."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import sdk_a7_private_sdk_smoke_chain_refresh_after_explore_cli_remediation as sdk_a7  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_sdk_smoke_chain_pause_or_docs_selector.v0"
STATUS = "SDK_A8_PRIVATE_SDK_SMOKE_CHAIN_PAUSE_SELECTOR_PASS"

TRUE_CLAIM_FLAGS = {
    "sdk_a7_consumed",
    "pause_selector_created",
    "sdk_smoke_chain_seeded",
    "next_action_selected",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "sdk_a7_consumed": True,
    "pause_selector_created": True,
    "sdk_smoke_chain_seeded": True,
    "next_action_selected": True,
    "d109_hold_respected": True,
    "sdk_implementation_changed": False,
    "docs_note_created": False,
    "public_docs_created": False,
    "smoke_probe_rerun": False,
    "optional_dependency_installed": False,
    "public_package_install_executed": False,
    "sdk_stability_claim": False,
    "sdk_public_ready": False,
    "public_readiness_claim": False,
    "public_copy_approved": False,
    "public_package_release_claim": False,
    "api_compatibility_claim": False,
    "semantic_versioning_commitment": False,
    "compiler_correctness_claim": False,
    "semantic_preservation_claim": False,
    "runtime_performance_claim": False,
    "training_savings_claim": False,
    "estimator_accuracy_claim": False,
    "hardware_readiness_claim": False,
    "silicon_readiness_claim": False,
    "electronics_repo_touched": False,
    "laptop_owned_repo_touched": False,
    "d110_started": False,
    "reviewer_response_consumed": False,
    "reviewer_approval_recorded": False,
    "broad_eml_advantage_claim": False,
    "benchmark_executed": False,
    "forge_emit_check_executed": False,
}

NON_CLAIMS = [
    "SDK-A8 is a private selector; it does not change SDK implementation, create docs, rerun smoke probes, or install optional dependencies.",
    "SDK-A8 records the SDK smoke chain as seeded, not stable, public-ready, or release-ready.",
    "SDK-A8 does not claim SDK stability, public readiness, public package release readiness, API compatibility, or semantic-versioning commitments.",
    "SDK-A8 does not claim compiler correctness, semantic preservation, runtime performance, training savings, estimator accuracy, hardware readiness, silicon readiness, or broad EML advantage.",
    "SDK-A8 respects the D109 hold and does not start D110, consume reviewer response, or touch laptop-owned electronics repositories.",
]


def load_sdk_a7_result() -> dict[str, Any]:
    path = (
        ROOT
        / "python/results/sdk_a7_private_sdk_smoke_chain_refresh_after_explore_cli_remediation"
        / f"sdk_a7_private_sdk_smoke_chain_refresh_after_explore_cli_remediation_{STAMP}.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    sdk_a7.validate_payload(payload)
    return payload


def candidate_actions() -> list[dict[str, Any]]:
    return [
        {
            "actionId": "pause_sdk_smoke_lane_as_seeded",
            "decision": "selected",
            "reason": "SDK-A1 through SDK-A7 established inventory, contract, finding, classification, remediation, and refreshed smoke evidence. Further packets would add little value until a concrete SDK docs/product request appears.",
            "nextArtifact": "Return to product-roadmap selector or next concrete private product/tooling lane.",
        },
        {
            "actionId": "private_docs_note_packet",
            "decision": "parked",
            "reason": "A private docs note may be useful later, but doing it now risks turning private smoke evidence into premature SDK-facing copy.",
            "nextArtifact": "SDK docs note only after explicit docs/product request.",
        },
        {
            "actionId": "public_docs_packet",
            "decision": "blocked",
            "reason": "Public docs would imply a public readiness posture that SDK-A8 explicitly does not claim.",
            "nextArtifact": "Requires explicit human approval and a separate public-copy gate.",
        },
        {
            "actionId": "more_smoke_chain_expansion",
            "decision": "parked",
            "reason": "The current chain is sufficient for source-tree import/CLI smoke; more expansion should wait for a new concrete surface.",
            "nextArtifact": "Only start if a new SDK surface or failing smoke probe appears.",
        },
    ]


def build_payload() -> dict[str, Any]:
    source = load_sdk_a7_result()
    actions = candidate_actions()
    selected = [action for action in actions if action["decision"] == "selected"]
    summary = {
        "sourceArtifact": source["artifactId"],
        "sourceRequiredProbeFailureCount": source["summary"]["requiredProbeFailureCount"],
        "sourceExploreCliHelpStatus": source["summary"]["exploreCliHelpStatus"],
        "candidateActionCount": len(actions),
        "selectedActionId": selected[0]["actionId"],
        "sdkSmokeChainSeeded": True,
        "sdkImplementationChanged": False,
        "docsNoteCreated": False,
        "publicDocsCreated": False,
        "smokeProbeRerun": False,
        "publicReadinessClaim": False,
        "sdkStabilityClaim": False,
        "nextRecommendedArtifact": selected[0]["nextArtifact"],
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="sdk-a8-private-sdk-smoke-chain-pause-or-docs-selector",
        artifact_type="private_sdk_smoke_chain_pause_or_docs_selector",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": source["artifactId"],
            "candidateActions": actions,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifact"] != "sdk-a7-private-sdk-smoke-chain-refresh-after-explore-cli-remediation":
        raise ValueError("SDK-A8 must consume SDK-A7")
    summary = payload["summary"]
    if summary["sourceRequiredProbeFailureCount"] != 0:
        raise ValueError("SDK-A8 expects SDK-A7 refreshed required probes to pass")
    if summary["sourceExploreCliHelpStatus"] != "pass":
        raise ValueError("SDK-A8 expects the explore CLI help finding to be resolved")
    if summary["selectedActionId"] != "pause_sdk_smoke_lane_as_seeded":
        raise ValueError("SDK-A8 should pause the seeded smoke lane")
    for key in [
        "sdkImplementationChanged",
        "docsNoteCreated",
        "publicDocsCreated",
        "smokeProbeRerun",
        "publicReadinessClaim",
        "sdkStabilityClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    actions = payload["candidateActions"]
    if sum(1 for action in actions if action["decision"] == "selected") != 1:
        raise ValueError("exactly one action must be selected")
    decisions = {action["actionId"]: action["decision"] for action in actions}
    if decisions["public_docs_packet"] != "blocked":
        raise ValueError("public docs must remain blocked")
    for key in TRUE_CLAIM_FLAGS:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return build_evidence_packet(
        artifact_id=payload["artifactId"],
        artifact_type=payload["artifactType"],
        semantic_strength="private_pause_selector_seeded_smoke_chain_no_public_claim",
        source=f"python/results/sdk_a8_private_sdk_smoke_chain_pause_or_docs_selector/sdk_a8_private_sdk_smoke_chain_pause_or_docs_selector_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="sdk_a8_private_sdk_smoke_chain_pause_or_docs_selector_feed",
        date=DATE,
        status=payload["status"],
        next_action="Pause SDK smoke lane as seeded; return to product-roadmap selector or next concrete private product/tooling lane.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "selectedActionId": payload["summary"]["selectedActionId"],
            "sdkSmokeChainSeeded": payload["summary"]["sdkSmokeChainSeeded"],
            "docsNoteCreated": payload["summary"]["docsNoteCreated"],
            "publicDocsCreated": payload["summary"]["publicDocsCreated"],
            "sdkStabilityClaim": payload["summary"]["sdkStabilityClaim"],
            "publicReadinessClaim": payload["summary"]["publicReadinessClaim"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="SDK-A8 Private SDK Smoke Chain Pause Or Docs Selector",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("selected action", payload["summary"]["selectedActionId"]),
            ("SDK smoke chain seeded", payload["summary"]["sdkSmokeChainSeeded"]),
            ("docs note created", payload["summary"]["docsNoteCreated"]),
            ("public docs created", payload["summary"]["publicDocsCreated"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Candidate Actions",
                [
                    f"- `{action['actionId']}`: `{action['decision']}` - {action['reason']}"
                    for action in payload["candidateActions"]
                ],
            ),
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"sdk_a8_private_sdk_smoke_chain_pause_or_docs_selector_{STAMP}.json"
    report_path = report_dir / f"sdk_a8_private_sdk_smoke_chain_pause_or_docs_selector_{STAMP}.md"
    evidence_path = evidence_dir / "sdk_a8_private_sdk_smoke_chain_pause_or_docs_selector.json"
    feed_path = command_feed_dir / f"sdk_a8_private_sdk_smoke_chain_pause_or_docs_selector_feed_{STAMP}.json"
    write_json(result_path, payload)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(payload), encoding="utf-8")
    write_json(evidence_path, evidence)
    write_json(feed_path, feed)
    return {
        "payload": payload,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/sdk_a8_private_sdk_smoke_chain_pause_or_docs_selector")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    validate_payload(payload)
    if args.build:
        build_outputs(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    print("SDK_A8_PRIVATE_SDK_SMOKE_CHAIN_PAUSE_OR_DOCS_SELECTOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
