#!/usr/bin/env python3
"""CPG-A1 private compiler-plugin guard-note packet."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import prod_a7_private_product_roadmap_return_selector as prod_a7  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_compiler_plugin_guard_note_packet.v0"
STATUS = "CPG_A1_PRIVATE_COMPILER_PLUGIN_GUARD_NOTE_PACKET_PASS"

NEXT_RECOMMENDED_ARTIFACT = "CPG-A2 private compiler-plugin guard-note fixture packet or executable lint contract selector"

TRUE_CLAIM_FLAGS = {
    "prod_a7_consumed",
    "compiler_plugin_guard_note_created",
    "advisory_capabilities_recorded",
    "blocked_compiler_claims_recorded",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "prod_a7_consumed": True,
    "compiler_plugin_guard_note_created": True,
    "advisory_capabilities_recorded": True,
    "blocked_compiler_claims_recorded": True,
    "d109_hold_respected": True,
    "compiler_plugin_implemented": False,
    "compiler_plugin_executed": False,
    "compiler_correctness_claim": False,
    "semantic_preservation_claim": False,
    "automatic_lowering_safety_claim": False,
    "runtime_performance_claim": False,
    "code_generation_claim": False,
    "runtime_lowering_changed": False,
    "sdk_stability_claim": False,
    "sdk_public_ready": False,
    "public_product_ready": False,
    "public_readiness_claim": False,
    "public_copy_approved": False,
    "public_package_release_claim": False,
    "training_savings_claim": False,
    "estimator_accuracy_claim": False,
    "scientific_correctness_claim": False,
    "hardware_readiness_claim": False,
    "silicon_readiness_claim": False,
    "ip_license_terms_finalized": False,
    "accelerator_card_ready": False,
    "electronics_repo_touched": False,
    "laptop_owned_repo_touched": False,
    "d110_started": False,
    "reviewer_response_consumed": False,
    "reviewer_approval_recorded": False,
    "broad_eml_advantage_claim": False,
}

NON_CLAIMS = [
    "CPG-A1 is a private guard-note packet only; it does not implement or execute a compiler plugin.",
    "CPG-A1 records advisory lint/profile/guard-note boundaries only.",
    "CPG-A1 does not claim compiler correctness, semantic preservation, automatic lowering safety, code generation correctness, runtime lowering safety, runtime performance, SDK stability, public readiness, or public package release readiness.",
    "CPG-A1 does not claim training savings, estimator accuracy, scientific correctness, hardware readiness, silicon readiness, IP license readiness, accelerator-card readiness, reviewer approval, or broad EML advantage.",
    "CPG-A1 respects the D109 hold and does not start D110, consume reviewer response, or touch laptop-owned electronics repositories.",
]


def advisory_capabilities() -> list[dict[str, Any]]:
    return [
        {
            "capabilityId": "expression_surface_detection",
            "mayDo": "Detect candidate EML-shaped expressions or elementary-function surfaces for human review.",
            "mustSay": "Advisory detection only; no completeness, correctness, or target-readiness claim.",
            "mustNotSay": "The plugin proves the expression is correct or complete.",
            "evidenceInputs": ["EML-shaped source surface", "existing D-series or witness packet references when available"],
        },
        {
            "capabilityId": "static_cost_profile_hint",
            "mayDo": "Record static cost/profile hints when local metadata is available.",
            "mustSay": "Static hint only; no measured runtime, savings, or performance claim.",
            "mustNotSay": "The hint predicts realized training cost or runtime performance.",
            "evidenceInputs": ["static expression metadata", "cost-model notes", "profile fields if explicitly supplied"],
        },
        {
            "capabilityId": "rewrite_opportunity_hint",
            "mayDo": "Suggest that a reviewer inspect a candidate rewrite or guard-bearing identity.",
            "mustSay": "Review suggestion only; no automatic rewrite or semantic-preservation claim.",
            "mustNotSay": "The plugin may safely replace or lower code.",
            "evidenceInputs": ["bounded identity candidates", "claim-boundary records", "guard notes"],
        },
        {
            "capabilityId": "guard_requirement_note",
            "mayDo": "Surface domain, guard, and blocked-claim obligations next to a candidate expression.",
            "mustSay": "Guard reminder only; no proof or proof-carrying artifact claim.",
            "mustNotSay": "The presence of a guard note establishes the guard.",
            "evidenceInputs": ["domain conditions", "witness guard fields", "blocked-claim lists"],
        },
        {
            "capabilityId": "evidence_packet_link_hint",
            "mayDo": "Link a candidate expression to existing private evidence packets or checked witnesses when present.",
            "mustSay": "Evidence pointer only; no completeness, public readiness, or library coverage claim.",
            "mustNotSay": "Every relevant witness has been found or is public-ready.",
            "evidenceInputs": ["evidence packet ids", "MachLib witness ids", "private report paths"],
        },
    ]


def blocked_compiler_claims() -> list[dict[str, str]]:
    return [
        {
            "claimId": "compiler_correctness",
            "blockedClaim": "The plugin or EML compiler is correct.",
            "reason": "CPG-A1 contains no compiler implementation, proof, or end-to-end compiler validation.",
        },
        {
            "claimId": "semantic_preservation",
            "blockedClaim": "Suggested rewrites preserve program semantics.",
            "reason": "Guard notes and rewrite hints are advisory and require separate checked evidence.",
        },
        {
            "claimId": "automatic_lowering_safety",
            "blockedClaim": "Automatic lowering or replacement is safe.",
            "reason": "CPG-A1 authorizes no automatic lowering, replacement, or runtime mutation.",
        },
        {
            "claimId": "runtime_performance",
            "blockedClaim": "The plugin improves runtime, training cost, or performance.",
            "reason": "Static hints are not runtime measurements and do not establish savings.",
        },
        {
            "claimId": "code_generation_correctness",
            "blockedClaim": "Generated code is correct.",
            "reason": "CPG-A1 defines no code-generation path.",
        },
        {
            "claimId": "all_target_readiness",
            "blockedClaim": "The plugin is ready across Python, Lean, hardware, or other targets.",
            "reason": "Target readiness must be shown by target-specific evidence.",
        },
        {
            "claimId": "public_package_release_readiness",
            "blockedClaim": "The plugin is public/package-ready.",
            "reason": "This artifact is private-first and contains no release validation.",
        },
        {
            "claimId": "broad_eml_advantage",
            "blockedClaim": "EML is broadly advantaged over ordinary implementations.",
            "reason": "One guard-note packet cannot establish broad comparative advantage.",
        },
    ]


def allowed_outputs() -> list[dict[str, str]]:
    return [
        {"outputId": "lint_warning", "description": "A private advisory warning for reviewer attention."},
        {"outputId": "review_note", "description": "A short private note explaining why the expression may need review."},
        {"outputId": "cost_profile_hint", "description": "A static hint, clearly marked as non-runtime evidence."},
        {"outputId": "guard_checklist_item", "description": "A reminder that domain conditions or guards must be reviewed."},
        {"outputId": "evidence_pointer", "description": "A link or id for an existing private evidence packet or witness."},
    ]


def blocked_outputs() -> list[dict[str, str]]:
    return [
        {"outputId": "generated_code_replacement", "description": "Any emitted replacement code presented as safe."},
        {"outputId": "automatic_rewrite_or_lowering", "description": "Any automatic program rewrite/lowering action."},
        {"outputId": "proof_certificate", "description": "Any proof or checked certificate claim created by the plugin."},
        {"outputId": "runtime_benchmark_claim", "description": "Any runtime, training-cost, or performance measurement claim."},
        {"outputId": "public_docs_or_copy", "description": "Any public-facing product or documentation claim."},
    ]


def reviewer_questions() -> list[str]:
    return [
        "Which expression surfaces should produce advisory-only lint notes?",
        "Which guard fields must exist before the plugin can suggest a rewrite review?",
        "Which wording prevents users from reading advisory hints as compiler, proof, or performance claims?",
        "Which existing evidence packet ids should be allowed as private evidence pointers?",
    ]


def build_payload() -> dict[str, Any]:
    selector = prod_a7.build_payload()
    prod_a7.validate_payload(selector)
    capabilities = advisory_capabilities()
    blocked_claims = blocked_compiler_claims()
    allowed = allowed_outputs()
    blocked = blocked_outputs()
    questions = reviewer_questions()
    summary = {
        "sourceArtifact": selector["artifactId"],
        "selectedLaneId": selector["summary"]["selectedLaneId"],
        "advisoryCapabilityCount": len(capabilities),
        "blockedCompilerClaimCount": len(blocked_claims),
        "allowedOutputCount": len(allowed),
        "blockedOutputCount": len(blocked),
        "reviewerQuestionCount": len(questions),
        "compilerPluginImplemented": False,
        "compilerPluginExecuted": False,
        "compilerCorrectnessClaim": False,
        "semanticPreservationClaim": False,
        "automaticLoweringSafetyClaim": False,
        "runtimePerformanceClaim": False,
        "nextRecommendedArtifact": NEXT_RECOMMENDED_ARTIFACT,
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="cpg-a1-private-compiler-plugin-guard-note-packet",
        artifact_type="private_compiler_plugin_guard_note_packet",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": selector["artifactId"],
            "advisoryCapabilities": capabilities,
            "blockedCompilerClaims": blocked_claims,
            "allowedOutputs": allowed,
            "blockedOutputs": blocked,
            "reviewerQuestions": questions,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifact"] != "prod-a7-private-product-roadmap-return-selector":
        raise ValueError("CPG-A1 must consume PROD-A7")
    summary = payload["summary"]
    if summary["selectedLaneId"] != "eml_compiler_plugin":
        raise ValueError("CPG-A1 must stay on the compiler-plugin lane")
    if summary["nextRecommendedArtifact"] != NEXT_RECOMMENDED_ARTIFACT:
        raise ValueError("unexpected next recommended artifact")
    expected_counts = {
        "advisoryCapabilityCount": len(payload["advisoryCapabilities"]),
        "blockedCompilerClaimCount": len(payload["blockedCompilerClaims"]),
        "allowedOutputCount": len(payload["allowedOutputs"]),
        "blockedOutputCount": len(payload["blockedOutputs"]),
        "reviewerQuestionCount": len(payload["reviewerQuestions"]),
    }
    for key, expected in expected_counts.items():
        if summary[key] != expected:
            raise ValueError(f"{key} count mismatch")
    for key in [
        "compilerPluginImplemented",
        "compilerPluginExecuted",
        "compilerCorrectnessClaim",
        "semanticPreservationClaim",
        "automaticLoweringSafetyClaim",
        "runtimePerformanceClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    capability_ids = {item["capabilityId"] for item in payload["advisoryCapabilities"]}
    if capability_ids != {
        "expression_surface_detection",
        "static_cost_profile_hint",
        "rewrite_opportunity_hint",
        "guard_requirement_note",
        "evidence_packet_link_hint",
    }:
        raise ValueError("unexpected advisory capabilities")
    blocked_claim_ids = {item["claimId"] for item in payload["blockedCompilerClaims"]}
    if "compiler_correctness" not in blocked_claim_ids or "semantic_preservation" not in blocked_claim_ids:
        raise ValueError("critical compiler claims must be blocked")
    allowed_ids = {item["outputId"] for item in payload["allowedOutputs"]}
    blocked_ids = {item["outputId"] for item in payload["blockedOutputs"]}
    if "lint_warning" not in allowed_ids or "evidence_pointer" not in allowed_ids:
        raise ValueError("allowed advisory outputs missing")
    if "automatic_rewrite_or_lowering" not in blocked_ids or "proof_certificate" not in blocked_ids:
        raise ValueError("blocked outputs missing")
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
        semantic_strength="private_compiler_plugin_guard_note_no_plugin_or_compiler_claim",
        source=f"python/results/cpg_a1_private_compiler_plugin_guard_note_packet/cpg_a1_private_compiler_plugin_guard_note_packet_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="cpg_a1_private_compiler_plugin_guard_note_packet_feed",
        date=DATE,
        status=payload["status"],
        next_action=NEXT_RECOMMENDED_ARTIFACT,
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "selectedLaneId": payload["summary"]["selectedLaneId"],
            "advisoryCapabilityCount": payload["summary"]["advisoryCapabilityCount"],
            "blockedCompilerClaimCount": payload["summary"]["blockedCompilerClaimCount"],
            "compilerPluginImplemented": payload["summary"]["compilerPluginImplemented"],
            "compilerCorrectnessClaim": payload["summary"]["compilerCorrectnessClaim"],
            "runtimePerformanceClaim": payload["summary"]["runtimePerformanceClaim"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="CPG-A1 Private Compiler-Plugin Guard-Note Packet",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("selected lane", payload["summary"]["selectedLaneId"]),
            ("advisory capability count", payload["summary"]["advisoryCapabilityCount"]),
            ("blocked compiler claim count", payload["summary"]["blockedCompilerClaimCount"]),
            ("compiler plugin implemented", payload["summary"]["compilerPluginImplemented"]),
            ("compiler correctness claim", payload["summary"]["compilerCorrectnessClaim"]),
            ("runtime performance claim", payload["summary"]["runtimePerformanceClaim"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Advisory Capabilities",
                [
                    f"- `{item['capabilityId']}`: may do: {item['mayDo']} must say: {item['mustSay']}"
                    for item in payload["advisoryCapabilities"]
                ],
            ),
            (
                "Blocked Compiler Claims",
                [
                    f"- `{item['claimId']}`: {item['blockedClaim']} Reason: {item['reason']}"
                    for item in payload["blockedCompilerClaims"]
                ],
            ),
            (
                "Allowed Outputs",
                [f"- `{item['outputId']}`: {item['description']}" for item in payload["allowedOutputs"]],
            ),
            (
                "Blocked Outputs",
                [f"- `{item['outputId']}`: {item['description']}" for item in payload["blockedOutputs"]],
            ),
            (
                "Reviewer Questions",
                [f"- {question}" for question in payload["reviewerQuestions"]],
            ),
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"cpg_a1_private_compiler_plugin_guard_note_packet_{STAMP}.json"
    report_path = report_dir / f"cpg_a1_private_compiler_plugin_guard_note_packet_{STAMP}.md"
    evidence_path = evidence_dir / "cpg_a1_private_compiler_plugin_guard_note_packet.json"
    feed_path = command_feed_dir / f"cpg_a1_private_compiler_plugin_guard_note_packet_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/cpg_a1_private_compiler_plugin_guard_note_packet")
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
    print("CPG_A1_PRIVATE_COMPILER_PLUGIN_GUARD_NOTE_PACKET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
