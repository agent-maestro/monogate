#!/usr/bin/env python3
"""EML-S27 export policy registry.

S27 turns the S24/S25/S26/S28/S30 runtime advisory path and the S31
guard-owned clamp policy drilldown into a small source-family policy registry.
This is policy metadata only: it does not change Forge, eFrog, generated target
code, or runtime behavior.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_advantage_lab import CLAIM_FLAGS as ADVANTAGE_CLAIM_FLAGS  # noqa: E402

DATE = "2026-05-29"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_s27_export_policy_registry.v0"
POLICY_SCHEMA_VERSION = "monogate.eml_export_policy_packet.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_S27_EXPORT_POLICY_REGISTRY_PASS"

A14_PATH = ROOT / "python/results/eml_a14_forge_efrog_export_ux/eml_a14_forge_efrog_export_ux_2026_05_29.json"
S24_PATH = ROOT / "python/results/eml_s24_sigmoid_runtime_bakeoff/eml_s24_sigmoid_runtime_bakeoff_2026_05_29.json"
S28_PATH = ROOT / "python/results/eml_s28_softplus_runtime_bakeoff/eml_s28_softplus_runtime_bakeoff_2026_05_29.json"
S30_PATH = ROOT / "python/results/eml_s30_gaussian_log_normal_runtime_bakeoff/eml_s30_gaussian_log_normal_runtime_bakeoff_2026_05_29.json"
S31_PATH = ROOT / "python/results/eml_s31_guard_owned_clamp_policy_bakeoff/eml_s31_guard_owned_clamp_policy_bakeoff_2026_05_29.json"

CLAIM_FLAGS = {
    **dict(ADVANTAGE_CLAIM_FLAGS),
    "public_ready": False,
    "safe_to_publish_publicly": False,
    "forge_behavior_changed": False,
    "efrog_behavior_changed": False,
    "generated_target_code_changed": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "broad_eml_advantage_claim": False,
    "source_family_generalization_claim": False,
    "runtime_performance_claim": False,
    "public_performance_claim": False,
    "production_toolchain_claim": False,
    "certified_safety_claim": False,
    "proof_claim": False,
    "deploy_performed": False,
    "package_published": False,
}

NON_CLAIMS = [
    "S27 records private export policy metadata only.",
    "S27 does not change Forge compiler behavior, eFrog decompiler behavior, or generated target code.",
    "S27 does not claim runtime performance, public performance, production readiness, compiler correctness, formal equivalence, proof strength, certified safety, or broad EML advantage.",
]

DEFAULT_RUNTIME_FORM = "standard_or_protected_runtime_until_benchmarked"

FAMILY_DEFAULTS: dict[str, dict[str, Any]] = {
    "gaussian": {
        "representationForm": "eml_exponential_quadratic_envelope",
        "policyStatus": "default_until_family_runtime_bakeoff",
        "policyDecision": "use_standard_or_protected_runtime_until_gaussian_runtime_bakeoff",
        "unresolvedGaps": [
            "no family-specific runtime bakeoff attached",
            "no public performance claim",
            "no compiler correctness proof",
        ],
    },
    "rc_decay": {
        "representationForm": "eml_exponential_decay_envelope",
        "policyStatus": "default_until_family_runtime_bakeoff",
        "policyDecision": "use_standard_or_protected_runtime_until_rc_decay_runtime_bakeoff",
        "unresolvedGaps": [
            "no family-specific runtime bakeoff attached",
            "no public performance claim",
            "no compiler correctness proof",
        ],
    },
    "stretched_exponential": {
        "representationForm": "eml_stretched_exponential_envelope",
        "policyStatus": "default_until_family_runtime_bakeoff",
        "policyDecision": "use_standard_or_protected_runtime_until_stretched_exponential_runtime_bakeoff",
        "unresolvedGaps": [
            "no family-specific runtime bakeoff attached",
            "no public performance claim",
            "no compiler correctness proof",
        ],
    },
    "numpy_softplus": {
        "representationForm": "softplus_logsumexp",
        "policyStatus": "default_until_family_runtime_bakeoff",
        "policyDecision": "use_standard_or_protected_runtime_until_softplus_logsumexp_bakeoff",
        "unresolvedGaps": [
            "no dedicated softplus/logaddexp runtime bakeoff attached",
            "no public performance claim",
            "no compiler correctness proof",
        ],
    },
    "clamp_guard": {
        "representationForm": "guard_owned_branch_boundary_surface",
        "policyStatus": "guard_owned_default",
        "policyDecision": "route_through_guard_policy_before_runtime_lowering",
        "unresolvedGaps": [
            "guard-owned family needs a dedicated guard policy drilldown",
            "no public performance claim",
            "no compiler correctness proof",
        ],
    },
    "unmapped": {
        "representationForm": "unmapped_semantic_export_surface",
        "policyStatus": "review_before_runtime_policy",
        "policyDecision": "require_family_mapping_before_runtime_policy",
        "unresolvedGaps": [
            "family is not mapped into an EML source-family policy",
            "no public performance claim",
            "no compiler correctness proof",
        ],
    },
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def stable_sigmoid_policy(s24: dict[str, Any]) -> dict[str, Any]:
    recommendation = s24["recommendation"]
    return {
        "policyStatus": "runtime_advisory_attached",
        "representationForm": recommendation["representationForm"],
        "runtimeForm": recommendation["recommendedRuntimeForm"],
        "runtimeRole": recommendation["recommendedRuntimeRole"],
        "teachingSearchForm": recommendation["teachingSearchForm"],
        "cautionOrBlockedForms": recommendation["blockedOrCautionForms"],
        "evidenceSources": [
            "eml-s23-sigmoid-logistic-holdout",
            "eml-s24-sigmoid-runtime-bakeoff",
            "eml-a14-forge-efrog-export-ux",
            "eml-s25-runtime-advisory-export-attachment",
            "command-s26-export-advisory-consumer",
        ],
        "sourcePaths": [
            "python/results/eml_s23_sigmoid_logistic_holdout/eml_s23_sigmoid_logistic_holdout_2026_05_29.json",
            "python/results/eml_s24_sigmoid_runtime_bakeoff/eml_s24_sigmoid_runtime_bakeoff_2026_05_29.json",
            "python/results/eml_a14_forge_efrog_export_ux/eml_a14_forge_efrog_export_ux_2026_05_29.json",
            "python/results/eml_forge_efrog_export_packets/stable_sigmoid_holdout_semantic_compare_v0_export_packet_v0_2026_05_29.json",
            "../command-center/data/export-advisories/eml_a14_runtime_advisories_2026_05_29.json",
        ],
        "policyDecision": recommendation["decision"],
        "unresolvedGaps": [
            "no public performance claim",
            "no runtime performance claim",
            "no compiler correctness proof",
            "no formal equivalence proof",
            "no generated-code behavior change consuming this policy yet",
        ],
    }


def softplus_policy(s28: dict[str, Any]) -> dict[str, Any]:
    recommendation = s28["recommendation"]
    return {
        "policyStatus": "runtime_advisory_attached",
        "representationForm": recommendation["representationForm"],
        "runtimeForm": recommendation["recommendedRuntimeForm"],
        "runtimeRole": recommendation["recommendedRuntimeRole"],
        "teachingSearchForm": recommendation["teachingSearchForm"],
        "cautionOrBlockedForms": recommendation["blockedOrCautionForms"],
        "evidenceSources": [
            "eml-s28-softplus-runtime-bakeoff",
            "eml-a14-forge-efrog-export-ux",
            "eml-s25-runtime-advisory-export-attachment",
            "command-s26-export-advisory-consumer",
        ],
        "sourcePaths": [
            "python/results/eml_s28_softplus_runtime_bakeoff/eml_s28_softplus_runtime_bakeoff_2026_05_29.json",
            "python/results/eml_a14_forge_efrog_export_ux/eml_a14_forge_efrog_export_ux_2026_05_29.json",
            "python/results/eml_forge_efrog_export_packets/sigmoid_semantic_compare_v0_export_packet_v0_2026_05_29.json",
            "../command-center/data/export-advisories/eml_a14_runtime_advisories_2026_05_29.json",
        ],
        "policyDecision": recommendation["decision"],
        "unresolvedGaps": [
            "no public performance claim",
            "no runtime performance claim",
            "no compiler correctness proof",
            "no formal equivalence proof",
            "no generated-code behavior change consuming this policy yet",
        ],
    }


def gaussian_policy(s30: dict[str, Any]) -> dict[str, Any]:
    recommendation = s30["recommendation"]
    return {
        "policyStatus": "runtime_advisory_attached",
        "representationForm": recommendation["representationForm"],
        "runtimeForm": recommendation["recommendedRuntimeForm"],
        "runtimeRole": recommendation["recommendedRuntimeRole"],
        "teachingSearchForm": recommendation["teachingSearchForm"],
        "cautionOrBlockedForms": recommendation["blockedOrCautionForms"],
        "evidenceSources": [
            "eml-s30-gaussian-log-normal-runtime-bakeoff",
            "eml-a14-forge-efrog-export-ux",
            "eml-s25-runtime-advisory-export-attachment",
            "command-s26-export-advisory-consumer",
        ],
        "sourcePaths": [
            "python/results/eml_s30_gaussian_log_normal_runtime_bakeoff/eml_s30_gaussian_log_normal_runtime_bakeoff_2026_05_29.json",
            "python/results/eml_a14_forge_efrog_export_ux/eml_a14_forge_efrog_export_ux_2026_05_29.json",
            "python/results/eml_forge_efrog_export_packets/gaussian_semantic_compare_v0_export_packet_v0_2026_05_29.json",
            "python/results/eml_forge_efrog_export_packets/gaussian_stable_holdout_semantic_compare_v0_export_packet_v0_2026_05_29.json",
            "../command-center/data/export-advisories/eml_a14_runtime_advisories_2026_05_29.json",
        ],
        "policyDecision": recommendation["decision"],
        "unresolvedGaps": [
            "no public performance claim",
            "no runtime performance claim",
            "no compiler correctness proof",
            "no formal equivalence proof",
            "no generated-code behavior change consuming this policy yet",
        ],
    }


def clamp_guard_policy(s31: dict[str, Any]) -> dict[str, Any]:
    recommendation = s31["recommendation"]
    return {
        "policyStatus": "guard_policy_drilldown_attached",
        "representationForm": recommendation["representationForm"],
        "runtimeForm": recommendation["runtimeForm"],
        "runtimeRole": recommendation["runtimeRole"],
        "teachingSearchForm": recommendation["teachingSearchForm"],
        "cautionOrBlockedForms": recommendation["blockedOrCautionForms"],
        "evidenceSources": [
            "eml-s31-guard-owned-clamp-policy-bakeoff",
            "eml-a14-forge-efrog-export-ux",
            "command-s26-export-advisory-consumer",
        ],
        "sourcePaths": [
            "python/results/eml_s31_guard_owned_clamp_policy_bakeoff/eml_s31_guard_owned_clamp_policy_bakeoff_2026_05_29.json",
            "python/results/eml_a14_forge_efrog_export_ux/eml_a14_forge_efrog_export_ux_2026_05_29.json",
            "python/results/eml_forge_efrog_export_packets/voltage_divider_holdout_semantic_compare_v0_export_packet_v0_2026_05_29.json",
            "../command-center/data/export-advisories/eml_a14_runtime_advisories_2026_05_29.json",
        ],
        "policyDecision": recommendation["policyDecision"],
        "unresolvedGaps": [
            "no public performance claim",
            "no runtime performance claim",
            "no compiler correctness proof",
            "no formal equivalence proof",
            "no generated-code behavior change consuming this policy yet",
            "no engine guard policy row or anchor packet yet",
        ],
    }


def default_policy(family_id: str, export_ids: list[str]) -> dict[str, Any]:
    defaults = FAMILY_DEFAULTS.get(family_id, FAMILY_DEFAULTS["unmapped"])
    return {
        "policyStatus": defaults["policyStatus"],
        "representationForm": defaults["representationForm"],
        "runtimeForm": DEFAULT_RUNTIME_FORM,
        "runtimeRole": "runtime_policy_pending_family_bakeoff",
        "teachingSearchForm": None,
        "cautionOrBlockedForms": [],
        "evidenceSources": [
            "eml-a14-forge-efrog-export-ux",
            "command-s26-export-advisory-consumer",
        ],
        "sourcePaths": [
            "python/results/eml_a14_forge_efrog_export_ux/eml_a14_forge_efrog_export_ux_2026_05_29.json",
            "../command-center/data/export-advisories/eml_a14_runtime_advisories_2026_05_29.json",
        ],
        "policyDecision": defaults["policyDecision"],
        "unresolvedGaps": defaults["unresolvedGaps"],
        "exportIds": export_ids,
    }


def build_policy(
    family_id: str,
    export_ids: list[str],
    s24: dict[str, Any],
    s28: dict[str, Any],
    s30: dict[str, Any],
    s31: dict[str, Any],
) -> dict[str, Any]:
    if family_id == "stable_sigmoid":
        policy = stable_sigmoid_policy(s24)
    elif family_id == "numpy_softplus":
        policy = softplus_policy(s28)
    elif family_id == "gaussian":
        policy = gaussian_policy(s30)
    elif family_id == "clamp_guard":
        policy = clamp_guard_policy(s31)
    else:
        policy = default_policy(family_id, export_ids)
    packet = {
        "schemaVersion": POLICY_SCHEMA_VERSION,
        "packetType": "eml_export_policy_packet_v0",
        "date": DATE,
        "policyId": f"{family_id}_export_policy_v0",
        "familyId": family_id,
        "sourceFamily": family_id,
        "coveredExportIds": export_ids,
        "policyStatus": policy["policyStatus"],
        "representationForm": policy["representationForm"],
        "runtimeForm": policy["runtimeForm"],
        "runtimeRole": policy["runtimeRole"],
        "teachingSearchForm": policy["teachingSearchForm"],
        "cautionOrBlockedForms": policy["cautionOrBlockedForms"],
        "evidenceSources": policy["evidenceSources"],
        "sourcePaths": policy["sourcePaths"],
        "policyDecision": policy["policyDecision"],
        "unresolvedGaps": policy["unresolvedGaps"],
        "claimBoundary": "private_export_policy_metadata_only_no_compiler_behavior_change_or_runtime_performance_claim",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_policy(packet)
    return packet


def family_exports(a14_packets: list[dict[str, Any]]) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for packet in a14_packets:
        family_id = packet["emlSurfaceSummary"]["familyId"]
        rows.setdefault(family_id, []).append(packet["exportId"])
    return {family_id: sorted(export_ids) for family_id, export_ids in sorted(rows.items())}


def build_payload(packet_dir: Path | None = None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    a14_payload, a14_packets = _load_a14_packets()
    s24 = read_json(S24_PATH)
    s28 = read_json(S28_PATH)
    s30 = read_json(S30_PATH)
    s31 = read_json(S31_PATH)
    policies = [
        build_policy(family_id, export_ids, s24, s28, s30, s31)
        for family_id, export_ids in family_exports(a14_packets).items()
    ]
    if packet_dir:
        packet_dir.mkdir(parents=True, exist_ok=True)
        for policy in policies:
            path = packet_dir / f"{policy['policyId']}_{STAMP}.json"
            path.write_text(json.dumps(policy, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "eml-s27-export-policy-registry",
        "sourceEvidence": [
            str(A14_PATH.relative_to(ROOT)),
            str(S24_PATH.relative_to(ROOT)),
            str(S28_PATH.relative_to(ROOT)),
            str(S30_PATH.relative_to(ROOT)),
            str(S31_PATH.relative_to(ROOT)),
        ],
        "policyIds": [policy["policyId"] for policy in policies],
        "summary": {
            "policyCount": len(policies),
            "sourceFamilyCount": len(policies),
            "coveredExportPacketCount": a14_payload["summary"]["exportPacketCount"],
            "runtimeAdvisoryAttachedPolicyCount": sum(1 for policy in policies if policy["policyStatus"] == "runtime_advisory_attached"),
            "defaultUntilBenchmarkedPolicyCount": sum(1 for policy in policies if policy["runtimeForm"] == DEFAULT_RUNTIME_FORM),
            "stableSigmoidPolicyAttached": any(policy["familyId"] == "stable_sigmoid" and policy["runtimeForm"] == "branch_stable_sigmoid" for policy in policies),
            "softplusPolicyAttached": any(policy["familyId"] == "numpy_softplus" and policy["runtimeForm"] == "logaddexp_softplus" for policy in policies),
            "gaussianPolicyAttached": any(policy["familyId"] == "gaussian" and policy["runtimeForm"] == "log_domain_pdf" for policy in policies),
            "guardOwnedClampPolicyAttached": any(
                policy["familyId"] == "clamp_guard"
                and policy["policyStatus"] == "guard_policy_drilldown_attached"
                and policy["runtimeForm"] == "guard_owned_branch_boundary_surface"
                for policy in policies
            ),
            "nextRuntimeBakeoffCandidate": "stretched_exponential",
            "forgeBehaviorChanged": False,
            "efrogBehaviorChanged": False,
            "generatedTargetCodeChanged": False,
            "compilerCorrectnessClaim": False,
            "formalEquivalenceClaim": False,
            "runtimePerformanceClaim": False,
            "publicPerformanceClaim": False,
            "broadEmlAdvantageClaim": False,
            "publicReady": False,
            "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
        },
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload, policies)
    return payload, policies


def _load_a14_packets() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    from scripts.eml_a14_forge_efrog_export_ux import build_payload as build_a14_payload

    return build_a14_payload()


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-s27-export-policy-registry",
        "title": "EML-S27 Export Policy Registry",
        "reviewDecision": "private_export_policy_registry_recorded",
        "validationStatus": "pass",
        "replayStatus": "deterministic_policy_registry_from_a14_s24_s28_s30_and_s31",
        "semanticStrength": "policy_metadata_no_compiler_behavior_change",
        "semanticReview": payload["summary"],
        "claimBoundary": "Private export policy registry only; no Forge/eFrog behavior change, generated-code change, runtime performance claim, compiler correctness claim, formal equivalence claim, deployment, or public-readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Defines source-family policies for all A14 export families.",
            "Carries the S24 stable-sigmoid representation/runtime split into a registry row.",
            "Carries the S28 softplus/logaddexp representation/runtime split into a registry row.",
            "Carries the S30 Gaussian/log-normal representation/runtime split into a registry row.",
            "Carries the S31 guard-owned clamp policy drilldown without making it a generic runtime lowering.",
            "Keeps remaining families on standard/protected runtime until a family runtime bakeoff exists.",
            "Records unresolved gaps per family so export consumers can make consistent private decisions.",
        ],
        "validationCommands": [
            "python python/scripts/eml_s27_export_policy_registry.py --build --strict",
            "python -m pytest -q python/tests/test_eml_s27_export_policy_registry.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.eml_s27_export_policy_registry.v0",
        "date": DATE,
        "title": "EML-S27 Export Policy Registry",
        "status": payload["status"],
        "summary": payload["summary"],
        "topFollowup": "S29: make private command UI consume registry-level policy rows and prepare the next family bakeoff.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any], policies: list[dict[str, Any]]) -> str:
    lines = [
        "# EML-S27 Export Policy Registry",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "S27 makes the export advisory layer systematic. It maps source families",
        "to representation forms, runtime forms, caution forms, evidence sources,",
        "and unresolved gaps. It does not change Forge, eFrog, generated code, or runtime behavior.",
        "",
        "| Family | Representation | Runtime | Status | Gaps |",
        "|---|---|---|---|---:|",
    ]
    for policy in policies:
        lines.append(
            f"| `{policy['familyId']}` | `{policy['representationForm']}` | "
            f"`{policy['runtimeForm']}` | `{policy['policyStatus']}` | "
            f"{len(policy['unresolvedGaps'])} |"
        )
    summary = payload["summary"]
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Policies: `{summary['policyCount']}`",
            f"- Covered export packets: `{summary['coveredExportPacketCount']}`",
            f"- Runtime advisory attached policies: `{summary['runtimeAdvisoryAttachedPolicyCount']}`",
            f"- Default-until-benchmarked policies: `{summary['defaultUntilBenchmarkedPolicyCount']}`",
            f"- Stable sigmoid policy attached: `{summary['stableSigmoidPolicyAttached']}`",
            f"- Softplus policy attached: `{summary['softplusPolicyAttached']}`",
            f"- Gaussian policy attached: `{summary['gaussianPolicyAttached']}`",
            f"- Guard-owned clamp policy attached: `{summary['guardOwnedClampPolicyAttached']}`",
            f"- Next runtime bakeoff candidate: `{summary['nextRuntimeBakeoffCandidate']}`",
            "",
            "## Boundary",
            "",
            "- No Forge/eFrog behavior change.",
            "- No generated target code change.",
            "- No compiler correctness or formal equivalence claim.",
            "- No runtime or public performance claim.",
            "- No broad EML advantage, deployment, certified-safety, or public-readiness claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_policy(policy: dict[str, Any]) -> None:
    if policy["schemaVersion"] != POLICY_SCHEMA_VERSION:
        raise ValueError("invalid policy schema")
    if not policy["coveredExportIds"]:
        raise ValueError("policy must cover at least one export id")
    if policy["familyId"] == "stable_sigmoid":
        if policy["representationForm"] != "clamp_stable_sigmoid":
            raise ValueError("stable sigmoid representation must be clamp_stable_sigmoid")
        if policy["runtimeForm"] != "branch_stable_sigmoid":
            raise ValueError("stable sigmoid runtime must be branch_stable_sigmoid")
        if "naive_sigmoid" not in policy["cautionOrBlockedForms"]:
            raise ValueError("stable sigmoid must keep naive sigmoid as caution")
    elif policy["familyId"] == "numpy_softplus":
        if policy["representationForm"] != "softplus_logsumexp":
            raise ValueError("softplus representation must be softplus_logsumexp")
        if policy["runtimeForm"] != "logaddexp_softplus":
            raise ValueError("softplus runtime must be logaddexp_softplus")
        if "naive_softplus" not in policy["cautionOrBlockedForms"]:
            raise ValueError("softplus must keep naive softplus as caution")
    elif policy["familyId"] == "gaussian":
        if policy["representationForm"] != "eml_exponential_quadratic_envelope":
            raise ValueError("Gaussian representation must be eml_exponential_quadratic_envelope")
        if policy["runtimeForm"] != "log_domain_pdf":
            raise ValueError("Gaussian runtime must be log_domain_pdf")
        if "clamp_exponent_caution" not in policy["cautionOrBlockedForms"]:
            raise ValueError("Gaussian must keep clamp exponent as caution")
    elif policy["familyId"] == "clamp_guard":
        if policy["policyStatus"] != "guard_policy_drilldown_attached":
            raise ValueError("clamp guard must attach the S31 guard policy drilldown")
        if policy["representationForm"] != "guard_owned_branch_boundary_surface":
            raise ValueError("clamp guard representation must be guard_owned_branch_boundary_surface")
        if policy["runtimeForm"] != "guard_owned_branch_boundary_surface":
            raise ValueError("clamp guard runtime must stay guard-owned")
        if "runtime_clamp_caution" not in policy["cautionOrBlockedForms"]:
            raise ValueError("clamp guard must keep generic runtime clamp as caution")
    elif policy["runtimeForm"] != DEFAULT_RUNTIME_FORM:
        raise ValueError("non-attached policies must use default runtime form")
    if policy["claimBoundary"] != "private_export_policy_metadata_only_no_compiler_behavior_change_or_runtime_performance_claim":
        raise ValueError("invalid claim boundary")
    for key, value in policy["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def validate_payload(payload: dict[str, Any], policies: list[dict[str, Any]]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid S27 schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid S27 status")
    summary = payload["summary"]
    if summary["policyCount"] != len(policies):
        raise ValueError("policy count mismatch")
    if summary["coveredExportPacketCount"] != 8:
        raise ValueError("expected eight covered export packets")
    if summary["runtimeAdvisoryAttachedPolicyCount"] != 3:
        raise ValueError("expected exactly three attached runtime policies")
    if summary["stableSigmoidPolicyAttached"] is not True:
        raise ValueError("stable sigmoid policy must be attached")
    if summary["softplusPolicyAttached"] is not True:
        raise ValueError("softplus policy must be attached")
    if summary["gaussianPolicyAttached"] is not True:
        raise ValueError("Gaussian policy must be attached")
    if summary["defaultUntilBenchmarkedPolicyCount"] != 3:
        raise ValueError("expected three default-until-benchmarked policies")
    if summary["guardOwnedClampPolicyAttached"] is not True:
        raise ValueError("guard-owned clamp policy drilldown must be attached")
    for key in [
        "forgeBehaviorChanged",
        "efrogBehaviorChanged",
        "generatedTargetCodeChanged",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
        "runtimePerformanceClaim",
        "publicPerformanceClaim",
        "broadEmlAdvantageClaim",
        "publicReady",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    for policy in policies:
        validate_policy(policy)
    for key, value in payload["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def build_outputs(
    out_dir: Path,
    packet_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
) -> dict[str, Any]:
    payload, policies = build_payload(packet_dir)
    evidence = build_evidence_packet(payload)
    feed = build_command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"eml_s27_export_policy_registry_{STAMP}.json"
    report_path = report_dir / f"eml_s27_export_policy_registry_{STAMP}.md"
    evidence_path = evidence_dir / "eml_s27_export_policy_registry.json"
    feed_path = command_feed_dir / f"eml_s27_export_policy_registry_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload, policies), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "policies": policies,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
        "packet_dir": str(packet_dir),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_s27_export_policy_registry")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_export_policy_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_outputs(args.out_dir, args.packet_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"], built["policies"])
    print("EML_S27_EXPORT_POLICY_REGISTRY_OK")
    print(f"policies={built['payload']['summary']['policyCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
