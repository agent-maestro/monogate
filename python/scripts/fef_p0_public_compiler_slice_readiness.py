#!/usr/bin/env python3
"""FEF-P0 public-readiness packet for the minimum Forge/eFrog compiler slice.

This composes existing A13/A13.2/A14/S27 evidence into a public-readiness
decision. It does not change Forge or eFrog behavior.
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

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p0_public_compiler_slice_readiness.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P0_PUBLIC_COMPILER_SLICE_READINESS_RECORDED"

PATHS = {
    "a13_toolchain_pause": ROOT / "reports/evidence_packets/eml_a13_toolchain_pause.json",
    "a13_2_semantic_output_comparison": ROOT / "reports/evidence_packets/eml_a13_2_semantic_output_comparison.json",
    "a14_export_ux": ROOT / "reports/evidence_packets/eml_a14_forge_efrog_export_ux.json",
    "s27_export_policy_registry": ROOT / "reports/evidence_packets/eml_s27_export_policy_registry.json",
}

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
    "runtime_performance_claim": False,
    "public_performance_claim": False,
    "production_toolchain_claim": False,
    "certified_safety_claim": False,
    "proof_claim": False,
    "deploy_performed": False,
    "package_published": False,
    "public_compiler_package_available": False,
    "public_quickstart_reproducible": False,
    "public_checkout_enabled": False,
}

NON_CLAIMS = [
    "FEF-P0 records readiness for a future public compiler slice; it does not publish a compiler.",
    "FEF-P0 does not change Forge or eFrog compiler/decompiler behavior.",
    "FEF-P0 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P0 does not claim runtime performance, production readiness, certified safety, proof strength, or public hardware readiness.",
    "FEF-P0 does not re-enable public checkout.",
]

PUBLIC_BLOCKERS = [
    {
        "id": "public_compiler_package_missing",
        "status": "blocking",
        "requiredEvidence": "A public package or reproducible public artifact that exposes the selected eFrog -> EML -> Forge Python/JavaScript path.",
    },
    {
        "id": "clean_room_quickstart_missing",
        "status": "blocking",
        "requiredEvidence": "A clean-room quickstart that a new user can run without sibling private repos.",
    },
    {
        "id": "javascript_runtime_execution_missing",
        "status": "blocking",
        "requiredEvidence": "JavaScript target execution in the bridge guard, not only emission.",
    },
    {
        "id": "non_python_source_semantic_comparison_missing",
        "status": "blocking",
        "requiredEvidence": "At least one non-Python source frontend compared through deterministic sample grids.",
    },
    {
        "id": "target_validation_policy_missing",
        "status": "blocking",
        "requiredEvidence": "Target-by-target public validation policy for what Python/JavaScript emission means and what it does not mean.",
    },
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def source_evidence() -> dict[str, dict[str, Any]]:
    return {key: read_json(path) for key, path in PATHS.items()}


def build_payload() -> dict[str, Any]:
    evidence = source_evidence()
    a13 = evidence["a13_toolchain_pause"]["semanticReview"]
    a13_2 = evidence["a13_2_semantic_output_comparison"]["semanticReview"]
    a14 = evidence["a14_export_ux"]["semanticReview"]
    s27 = evidence["s27_export_policy_registry"]["semanticReview"]

    internal_slice = {
        "path": "source fixture -> eFrog -> EML -> Forge Python/JavaScript -> deterministic checks",
        "status": "private_evidence_slice_present",
        "sourceFrontendScope": "selected local fixtures",
        "targetScope": ["python", "javascript"],
        "roundtripCases": a13["roundtrip_cases"],
        "roundtripPasses": a13["roundtrip_passes"],
        "semanticCases": a13_2["caseCount"],
        "semanticPasses": a13_2["passCount"],
        "semanticSampleFrames": a13_2["sampleCount"],
        "maxAbsError": a13_2["maxAbsError"],
        "maxRelError": a13_2["maxRelError"],
        "exportPacketCount": a14["exportPacketCount"],
        "policyCount": s27["policyCount"],
    }

    public_release_gates = [
        {
            "id": "internal_selected_slice_exists",
            "status": "pass",
            "evidence": "A13/A13.2/A14/S27 private packets",
        },
        {
            "id": "public_install_path_exists",
            "status": "fail",
            "evidence": "No public monogate-forge package or equivalent compiler-preview package is recorded.",
        },
        {
            "id": "clean_room_quickstart_exists",
            "status": "fail",
            "evidence": "No clean-room public quickstart artifact is recorded.",
        },
        {
            "id": "target_runtime_execution_guard_exists",
            "status": "partial",
            "evidence": "Python execution and sample comparison are recorded; JavaScript emission exists, but runtime execution guard remains a gap.",
        },
        {
            "id": "public_claim_copy_is_aligned",
            "status": "pass",
            "evidence": "monogateforge-site now frames compiler targets as roadmap/private evidence and checkout is fail-closed.",
        },
    ]

    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p0-public-compiler-slice-readiness",
        "decision": "not_public_ready_yet",
        "recommendedPublicLanguage": "Forge/eFrog compiler preview is under evidence-gated development. The installable public package today is monogate.",
        "minimumCompilerSlice": internal_slice,
        "publicReleaseGates": public_release_gates,
        "publicBlockers": PUBLIC_BLOCKERS,
        "nextMilestones": [
            "FEF-P1 package/CLI decision for a minimum public compiler preview slice",
            "FEF-P2 clean-room public quickstart with exact commands and archived artifacts",
            "FEF-P3 JavaScript runtime execution in the bridge guard",
            "FEF-P4 non-Python source semantic comparison",
            "FPGA-A5 connect a future EML-to-Verilog slice to electronics evidence after FPGA-A0..A4",
        ],
        "sourceEvidence": {key: str(path.relative_to(ROOT)) for key, path in PATHS.items()},
        "summary": {
            "privateCompilerSlicePresent": True,
            "publicCompilerPackageAvailable": False,
            "publicQuickstartReproducible": False,
            "publicCheckoutEnabled": False,
            "publicReady": False,
            "safeToPublishPublicly": False,
            "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
            "passGateCount": sum(1 for gate in public_release_gates if gate["status"] == "pass"),
            "partialGateCount": sum(1 for gate in public_release_gates if gate["status"] == "partial"),
            "failGateCount": sum(1 for gate in public_release_gates if gate["status"] == "fail"),
            "blockerCount": len(PUBLIC_BLOCKERS),
        },
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    return payload


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "title": "FEF-P0 Public Compiler Slice Readiness",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "readiness_gate_over_existing_private_forge_efrog_evidence",
        "semanticReview": payload["summary"],
        "claimBoundary": "Public-readiness assessment only; no public compiler package, compiler correctness, formal equivalence, runtime performance, production readiness, or checkout claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Selected private eFrog -> EML -> Forge Python/JavaScript evidence exists.",
            "Public release is blocked until a package/artifact and clean-room quickstart exist.",
            "The honest public language remains roadmap/private evidence, not shipped compiler product.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p0_public_compiler_slice_readiness.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p0_public_compiler_slice_readiness.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p0_public_compiler_slice_readiness.v0",
        "date": DATE,
        "title": "FEF-P0 Public Compiler Slice Readiness",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Choose the minimum public package/CLI shape for FEF-P1.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    slice_info = payload["minimumCompilerSlice"]
    lines = [
        "# FEF-P0 Public Compiler Slice Readiness",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Decision: `{payload['decision']}`",
        "",
        "FEF-P0 asks whether the minimum honest Forge/eFrog compiler slice is ready",
        "to become a public product claim. The answer is no: the private evidence",
        "slice exists, but public packaging and clean-room reproducibility are still",
        "missing.",
        "",
        "## Private Slice Present",
        "",
        f"- Path: `{slice_info['path']}`",
        f"- Roundtrip cases: `{slice_info['roundtripCases']}`",
        f"- Roundtrip passes: `{slice_info['roundtripPasses']}`",
        f"- Semantic cases: `{slice_info['semanticCases']}`",
        f"- Semantic passes: `{slice_info['semanticPasses']}`",
        f"- Semantic sample frames: `{slice_info['semanticSampleFrames']}`",
        f"- Export packets: `{slice_info['exportPacketCount']}`",
        f"- Source-family policies: `{slice_info['policyCount']}`",
        "",
        "## Public Release Gates",
        "",
        "| Gate | Status | Evidence |",
        "|---|---|---|",
    ]
    for gate in payload["publicReleaseGates"]:
        lines.append(f"| `{gate['id']}` | `{gate['status']}` | {gate['evidence']} |")
    lines.extend(
        [
            "",
            "## Blockers",
            "",
        ]
    )
    for blocker in payload["publicBlockers"]:
        lines.append(f"- `{blocker['id']}`: {blocker['requiredEvidence']}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- No public compiler package claim.",
            "- No compiler correctness or formal equivalence claim.",
            "- No runtime performance or production readiness claim.",
            "- No checkout/product-launch claim.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid schema")
    if payload["status"] != STATUS:
        raise ValueError("invalid status")
    summary = payload["summary"]
    if summary["privateCompilerSlicePresent"] is not True:
        raise ValueError("private compiler slice must be present")
    for key in [
        "publicCompilerPackageAvailable",
        "publicQuickstartReproducible",
        "publicCheckoutEnabled",
        "publicReady",
        "safeToPublishPublicly",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["failGateCount"] < 2:
        raise ValueError("expected blocking public release gates")
    if summary["blockerCount"] != len(PUBLIC_BLOCKERS):
        raise ValueError("blocker count mismatch")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    for key, value in payload["claimFlags"].items():
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    evidence = build_evidence_packet(payload)
    feed = build_command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"fef_p0_public_compiler_slice_readiness_{STAMP}.json"
    report_path = report_dir / f"fef_p0_public_compiler_slice_readiness_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p0_public_compiler_slice_readiness.json"
    feed_path = command_feed_dir / f"fef_p0_public_compiler_slice_readiness_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return {
        "payload": payload,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p0_public_compiler_slice_readiness")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_outputs(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    if args.strict:
        validate_payload(built["payload"])
    print("FEF_P0_PUBLIC_COMPILER_SLICE_READINESS_OK")
    print(f"decision={built['payload']['decision']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
