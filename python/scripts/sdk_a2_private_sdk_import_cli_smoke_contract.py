#!/usr/bin/env python3
"""SDK-A2 private SDK import and CLI smoke contract."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import sdk_a1_private_sdk_surface_inventory as sdk_a1  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_sdk_import_cli_smoke_contract.v0"
STATUS = "SDK_A2_PRIVATE_SDK_IMPORT_CLI_SMOKE_CONTRACT_PASS"

TRUE_CLAIM_FLAGS = {
    "sdk_a1_consumed",
    "private_smoke_contract_created",
    "import_probe_contracts_recorded",
    "cli_probe_contracts_recorded",
    "blocked_probe_contracts_recorded",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "sdk_a1_consumed": True,
    "private_smoke_contract_created": True,
    "import_probe_contracts_recorded": True,
    "cli_probe_contracts_recorded": True,
    "blocked_probe_contracts_recorded": True,
    "d109_hold_respected": True,
    "import_probe_executed": False,
    "cli_probe_executed": False,
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
    "dashboard_ui_created": False,
    "sdk_implementation_changed": False,
    "native_extension_required": False,
    "forge_preview_public_ready": False,
}

NON_CLAIMS = [
    "SDK-A2 defines a private smoke contract; it does not execute imports or CLIs.",
    "SDK-A2 does not change implementation or claim SDK stability, public readiness, public package release readiness, API compatibility, or semantic-versioning commitments.",
    "SDK-A2 does not claim compiler correctness, semantic preservation, runtime performance, training savings, estimator accuracy, hardware readiness, silicon readiness, or broad EML advantage.",
    "SDK-A2 respects the D109 hold and does not start D110, consume reviewer response, or record reviewer approval.",
    "SDK-A2 does not touch laptop-owned electronics repositories.",
]


def import_probe_contracts() -> list[dict[str, Any]]:
    return [
        {
            "probeId": "python_import_monogate",
            "surfaceId": "python_package_core",
            "probeKind": "python_import",
            "commandShape": "PYTHONPATH=python python -c \"import monogate\"",
            "expectedSignal": "import completes without exception",
            "executionStatus": "not_executed_contract_only",
            "blockedClaims": ["SDK stability", "API compatibility", "runtime performance"],
        },
        {
            "probeId": "python_import_monogate_validate",
            "surfaceId": "python_package_core",
            "probeKind": "python_import",
            "commandShape": "PYTHONPATH=python python -c \"import monogate.validate\"",
            "expectedSignal": "import completes without exception",
            "executionStatus": "not_executed_contract_only",
            "blockedClaims": ["validator correctness", "public readiness"],
        },
        {
            "probeId": "python_import_monogate_core_optional",
            "surfaceId": "rust_extension_core",
            "probeKind": "optional_python_import",
            "commandShape": "python -c \"import monogate_core\"",
            "expectedSignal": "optional import may pass if local extension is built; absence is not a failure of SDK-A2",
            "executionStatus": "not_executed_contract_only",
            "blockedClaims": ["native extension availability", "runtime performance"],
        },
        {
            "probeId": "forge_preview_import_optional",
            "surfaceId": "forge_preview_package",
            "probeKind": "optional_python_import",
            "commandShape": "PYTHONPATH=packages/monogate-forge-preview/src python -c \"import monogate_forge_preview\"",
            "expectedSignal": "local preview import completes when preview path is supplied",
            "executionStatus": "not_executed_contract_only",
            "blockedClaims": ["compiler correctness", "semantic preservation", "public package release readiness"],
        },
    ]


def cli_probe_contracts() -> list[dict[str, Any]]:
    return [
        {
            "probeId": "cli_monogate_capability_card_help",
            "surfaceId": "python_package_core",
            "probeKind": "cli_help",
            "commandShape": "PYTHONPATH=python python -m monogate.cli.capability_card --help",
            "expectedSignal": "help text exits successfully or prints usage",
            "executionStatus": "not_executed_contract_only",
            "blockedClaims": ["public readiness", "CLI stability"],
        },
        {
            "probeId": "cli_monogate_explore_help",
            "surfaceId": "python_package_core",
            "probeKind": "cli_help",
            "commandShape": "PYTHONPATH=python python -m monogate.cli.explore --help",
            "expectedSignal": "help text exits successfully or prints usage",
            "executionStatus": "not_executed_contract_only",
            "blockedClaims": ["public readiness", "CLI stability"],
        },
        {
            "probeId": "cli_monogate_validate_help",
            "surfaceId": "python_package_core",
            "probeKind": "cli_help",
            "commandShape": "PYTHONPATH=python python -m monogate.validate --help",
            "expectedSignal": "help text exits successfully or prints usage",
            "executionStatus": "not_executed_contract_only",
            "blockedClaims": ["validator correctness", "public readiness"],
        },
        {
            "probeId": "cli_forge_preview_help_optional",
            "surfaceId": "forge_preview_package",
            "probeKind": "local_preview_cli_help",
            "commandShape": "PYTHONPATH=packages/monogate-forge-preview/src python -m monogate_forge_preview.cli --help",
            "expectedSignal": "local preview help text exits successfully when preview path is supplied",
            "executionStatus": "not_executed_contract_only",
            "blockedClaims": ["compiler correctness", "semantic preservation", "public package release readiness"],
        },
    ]


def blocked_probe_contracts() -> list[dict[str, str]]:
    return [
        {
            "blockedProbeId": "native_benchmark_execution",
            "reason": "Runtime benchmarking would create performance-evidence obligations outside this smoke contract.",
        },
        {
            "blockedProbeId": "forge_emit_or_check_execution",
            "reason": "Compiler-preview emit/check execution belongs in a separate bounded Forge artifact.",
        },
        {
            "blockedProbeId": "electronics_repo_cli_probe",
            "reason": "Laptop-owned electronics/dev repos remain outside research-side SDK smoke ownership.",
        },
        {
            "blockedProbeId": "public_package_install_probe",
            "reason": "Public package release readiness is explicitly not claimed by SDK-A2.",
        },
    ]


def build_payload() -> dict[str, Any]:
    inventory = sdk_a1.build_payload()
    sdk_a1.validate_payload(inventory)
    imports = import_probe_contracts()
    clis = cli_probe_contracts()
    blocked = blocked_probe_contracts()
    summary = {
        "sourceArtifact": inventory["artifactId"],
        "importProbeContractCount": len(imports),
        "cliProbeContractCount": len(clis),
        "blockedProbeContractCount": len(blocked),
        "importProbeExecuted": False,
        "cliProbeExecuted": False,
        "sdkImplementationChanged": False,
        "publicReadinessClaim": False,
        "sdkStabilityClaim": False,
        "d109HoldRespected": True,
        "d110Started": False,
        "reviewerResponseConsumed": False,
        "nextRecommendedArtifact": "SDK-A3 private SDK import and CLI smoke dry run",
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="sdk-a2-private-sdk-import-cli-smoke-contract",
        artifact_type="private_sdk_import_cli_smoke_contract",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": inventory["artifactId"],
            "importProbeContracts": imports,
            "cliProbeContracts": clis,
            "blockedProbeContracts": blocked,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifact"] != "sdk-a1-private-sdk-surface-inventory":
        raise ValueError("SDK-A2 must consume SDK-A1")
    summary = payload["summary"]
    if summary["importProbeContractCount"] != 4:
        raise ValueError("import probe count drift")
    if summary["cliProbeContractCount"] != 4:
        raise ValueError("CLI probe count drift")
    if summary["blockedProbeContractCount"] != 4:
        raise ValueError("blocked probe count drift")
    for key in [
        "importProbeExecuted",
        "cliProbeExecuted",
        "sdkImplementationChanged",
        "publicReadinessClaim",
        "sdkStabilityClaim",
        "d110Started",
        "reviewerResponseConsumed",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    for probe in payload["importProbeContracts"] + payload["cliProbeContracts"]:
        if probe["executionStatus"] != "not_executed_contract_only":
            raise ValueError(f"{probe['probeId']} must not be executed")
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
        semantic_strength="private_import_cli_smoke_contract_no_execution_or_stability_claim",
        source=f"python/results/sdk_a2_private_sdk_import_cli_smoke_contract/sdk_a2_private_sdk_import_cli_smoke_contract_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="sdk_a2_private_sdk_import_cli_smoke_contract_feed",
        date=DATE,
        status=payload["status"],
        next_action="Create SDK-A3 private SDK import and CLI smoke dry run.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "importProbeContractCount": payload["summary"]["importProbeContractCount"],
            "cliProbeContractCount": payload["summary"]["cliProbeContractCount"],
            "blockedProbeContractCount": payload["summary"]["blockedProbeContractCount"],
            "importProbeExecuted": payload["summary"]["importProbeExecuted"],
            "cliProbeExecuted": payload["summary"]["cliProbeExecuted"],
            "sdkStabilityClaim": payload["summary"]["sdkStabilityClaim"],
            "publicReadinessClaim": payload["summary"]["publicReadinessClaim"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="SDK-A2 Private SDK Import And CLI Smoke Contract",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("import probe contracts", payload["summary"]["importProbeContractCount"]),
            ("CLI probe contracts", payload["summary"]["cliProbeContractCount"]),
            ("blocked probe contracts", payload["summary"]["blockedProbeContractCount"]),
            ("import probes executed", payload["summary"]["importProbeExecuted"]),
            ("CLI probes executed", payload["summary"]["cliProbeExecuted"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Import Probe Contracts",
                [f"- `{probe['probeId']}`: {probe['commandShape']}" for probe in payload["importProbeContracts"]],
            ),
            (
                "CLI Probe Contracts",
                [f"- `{probe['probeId']}`: {probe['commandShape']}" for probe in payload["cliProbeContracts"]],
            ),
            (
                "Blocked Probe Contracts",
                [f"- `{probe['blockedProbeId']}`: {probe['reason']}" for probe in payload["blockedProbeContracts"]],
            ),
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"sdk_a2_private_sdk_import_cli_smoke_contract_{STAMP}.json"
    report_path = report_dir / f"sdk_a2_private_sdk_import_cli_smoke_contract_{STAMP}.md"
    evidence_path = evidence_dir / "sdk_a2_private_sdk_import_cli_smoke_contract.json"
    feed_path = command_feed_dir / f"sdk_a2_private_sdk_import_cli_smoke_contract_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/sdk_a2_private_sdk_import_cli_smoke_contract")
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
    print("SDK_A2_PRIVATE_SDK_IMPORT_CLI_SMOKE_CONTRACT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
