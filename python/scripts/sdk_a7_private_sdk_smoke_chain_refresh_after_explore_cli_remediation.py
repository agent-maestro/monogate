#!/usr/bin/env python3
"""SDK-A7 private SDK smoke chain refresh after explore CLI remediation."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import sdk_a2_private_sdk_import_cli_smoke_contract as sdk_a2  # noqa: E402
from scripts import sdk_a6_private_explore_cli_help_import_boundary_remediation as sdk_a6  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_sdk_smoke_chain_refresh_after_explore_cli_remediation.v0"
STATUS = "SDK_A7_PRIVATE_SDK_SMOKE_CHAIN_REFRESH_PASS"

TRUE_CLAIM_FLAGS = {
    "sdk_a2_contract_consumed",
    "sdk_a6_remediation_consumed",
    "private_smoke_refresh_executed",
    "explore_cli_help_finding_resolved_in_source_tree_smoke",
    "blocked_probe_contracts_respected",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "sdk_a2_contract_consumed": True,
    "sdk_a6_remediation_consumed": True,
    "private_smoke_refresh_executed": True,
    "explore_cli_help_finding_resolved_in_source_tree_smoke": True,
    "blocked_probe_contracts_respected": True,
    "d109_hold_respected": True,
    "sdk_implementation_changed": False,
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
    "SDK-A7 refreshes the private SDK smoke chain after SDK-A6; it does not change SDK implementation.",
    "SDK-A7 records that the previous explore CLI help smoke finding is resolved only in the local source-tree smoke path.",
    "SDK-A7 does not install optional dependencies, build native extensions, install public packages, or claim installed-extra behavior.",
    "SDK-A7 does not claim SDK stability, public readiness, public package release readiness, API compatibility, or semantic-versioning commitments.",
    "SDK-A7 does not claim compiler correctness, semantic preservation, runtime performance, training savings, estimator accuracy, hardware readiness, silicon readiness, or broad EML advantage.",
    "SDK-A7 respects the D109 hold and does not start D110, consume reviewer response, or touch laptop-owned electronics repositories.",
]


def load_sdk_a6_result() -> dict[str, Any]:
    path = (
        ROOT
        / "python/results/sdk_a6_private_explore_cli_help_import_boundary_remediation"
        / f"sdk_a6_private_explore_cli_help_import_boundary_remediation_{STAMP}.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    sdk_a6.validate_payload(payload)
    return payload


def _env_with_pythonpath(*paths: Path) -> dict[str, str]:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    path_text = os.pathsep.join(str(path) for path in paths)
    env["PYTHONPATH"] = f"{path_text}{os.pathsep}{existing}" if existing else path_text
    return env


def probe_specs() -> dict[str, dict[str, Any]]:
    forge_src = ROOT / "packages/monogate-forge-preview/src"
    return {
        "python_import_monogate": {
            "argv": [sys.executable, "-c", "import monogate"],
            "env": _env_with_pythonpath(PYTHON_ROOT),
            "required": True,
        },
        "python_import_monogate_validate": {
            "argv": [sys.executable, "-c", "import monogate.validate"],
            "env": _env_with_pythonpath(PYTHON_ROOT),
            "required": True,
        },
        "python_import_monogate_core_optional": {
            "argv": [sys.executable, "-c", "import monogate_core"],
            "env": os.environ.copy(),
            "required": False,
            "optionalMissingNeedle": "No module named 'monogate_core'",
        },
        "forge_preview_import_optional": {
            "argv": [sys.executable, "-c", "import monogate_forge_preview"],
            "env": _env_with_pythonpath(forge_src),
            "required": False,
        },
        "cli_monogate_capability_card_help": {
            "argv": [sys.executable, "-m", "monogate.cli.capability_card", "--help"],
            "env": _env_with_pythonpath(PYTHON_ROOT),
            "required": True,
        },
        "cli_monogate_explore_help": {
            "argv": [sys.executable, "-m", "monogate.cli.explore", "--help"],
            "env": _env_with_pythonpath(PYTHON_ROOT),
            "required": True,
        },
        "cli_monogate_validate_help": {
            "argv": [sys.executable, "-m", "monogate.validate", "--help"],
            "env": _env_with_pythonpath(PYTHON_ROOT),
            "required": True,
        },
        "cli_forge_preview_help_optional": {
            "argv": [sys.executable, "-m", "monogate_forge_preview.cli", "--help"],
            "env": _env_with_pythonpath(forge_src),
            "required": False,
        },
    }


def _run_probe(probe: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    proc = subprocess.run(
        spec["argv"],
        cwd=ROOT,
        env=spec["env"],
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    combined = f"{proc.stdout}\n{proc.stderr}".strip()
    if proc.returncode == 0:
        status = "pass"
    elif not spec["required"] and spec.get("optionalMissingNeedle", "") in combined:
        status = "optional_missing"
    elif spec["required"]:
        status = "required_probe_failed"
    else:
        status = "optional_probe_failed"
    return {
        "probeId": probe["probeId"],
        "surfaceId": probe["surfaceId"],
        "probeKind": probe["probeKind"],
        "commandShape": probe["commandShape"],
        "required": spec["required"],
        "executionStatus": "refresh_executed",
        "resultStatus": status,
        "returnCode": proc.returncode,
        "stdoutPreview": proc.stdout[:500],
        "stderrPreview": proc.stderr[:500],
        "blockedClaims": probe["blockedClaims"],
    }


def run_refresh(contract: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    specs = probe_specs()
    import_results = [_run_probe(probe, specs[probe["probeId"]]) for probe in contract["importProbeContracts"]]
    cli_results = [_run_probe(probe, specs[probe["probeId"]]) for probe in contract["cliProbeContracts"]]
    return import_results, cli_results


def build_payload() -> dict[str, Any]:
    remediation = load_sdk_a6_result()
    contract = sdk_a2.build_payload()
    sdk_a2.validate_payload(contract)
    import_results, cli_results = run_refresh(contract)
    all_results = import_results + cli_results
    required_results = [result for result in all_results if result["required"]]
    optional_results = [result for result in all_results if not result["required"]]
    required_failures = [result for result in required_results if result["resultStatus"] != "pass"]
    optional_non_fail = [
        result
        for result in optional_results
        if result["resultStatus"] in {"pass", "optional_missing", "optional_probe_failed"}
    ]
    result_by_id = {result["probeId"]: result for result in all_results}
    summary = {
        "sourceArtifacts": [contract["artifactId"], remediation["artifactId"]],
        "importProbeRefreshCount": len(import_results),
        "cliProbeRefreshCount": len(cli_results),
        "requiredProbePassCount": sum(1 for result in required_results if result["resultStatus"] == "pass"),
        "requiredProbeFailureCount": len(required_failures),
        "optionalProbeNonFailCount": len(optional_non_fail),
        "blockedProbeContractCount": len(contract["blockedProbeContracts"]),
        "blockedProbeExecutionCount": 0,
        "exploreCliHelpStatus": result_by_id["cli_monogate_explore_help"]["resultStatus"],
        "historicalSdkA3FindingResolved": result_by_id["cli_monogate_explore_help"]["resultStatus"] == "pass",
        "sdkImplementationChanged": False,
        "optionalDependencyInstalled": False,
        "publicReadinessClaim": False,
        "sdkStabilityClaim": False,
        "nextRecommendedArtifact": "SDK-A8 private SDK smoke chain pause or public-docs selector",
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="sdk-a7-private-sdk-smoke-chain-refresh-after-explore-cli-remediation",
        artifact_type="private_sdk_smoke_chain_refresh_after_explore_cli_remediation",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifacts": [contract["artifactId"], remediation["artifactId"]],
            "importProbeResults": import_results,
            "cliProbeResults": cli_results,
            "blockedProbeContracts": contract["blockedProbeContracts"],
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifacts"] != [
        "sdk-a2-private-sdk-import-cli-smoke-contract",
        "sdk-a6-private-explore-cli-help-import-boundary-remediation",
    ]:
        raise ValueError("SDK-A7 must consume SDK-A2 and SDK-A6")
    summary = payload["summary"]
    if summary["importProbeRefreshCount"] != 4 or summary["cliProbeRefreshCount"] != 4:
        raise ValueError("probe count drift")
    if summary["requiredProbePassCount"] != 5 or summary["requiredProbeFailureCount"] != 0:
        raise ValueError("required smoke probes must all pass after SDK-A6")
    if summary["optionalProbeNonFailCount"] != 3:
        raise ValueError("optional probe count drift")
    if summary["blockedProbeExecutionCount"] != 0:
        raise ValueError("blocked probes must not execute")
    if summary["exploreCliHelpStatus"] != "pass" or summary["historicalSdkA3FindingResolved"] is not True:
        raise ValueError("explore CLI help finding must be resolved in SDK-A7")
    for key in [
        "sdkImplementationChanged",
        "optionalDependencyInstalled",
        "publicReadinessClaim",
        "sdkStabilityClaim",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    for result in payload["importProbeResults"] + payload["cliProbeResults"]:
        if result["required"] and result["resultStatus"] != "pass":
            raise ValueError(f"{result['probeId']} must pass")
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
        semantic_strength="private_smoke_refresh_after_bounded_cli_remediation",
        source=f"python/results/sdk_a7_private_sdk_smoke_chain_refresh_after_explore_cli_remediation/sdk_a7_private_sdk_smoke_chain_refresh_after_explore_cli_remediation_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="sdk_a7_private_sdk_smoke_chain_refresh_after_explore_cli_remediation_feed",
        date=DATE,
        status=payload["status"],
        next_action="Select whether to pause the private SDK smoke chain or create private SDK docs notes after the refresh.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifacts": payload["sourceArtifacts"],
            "requiredProbePassCount": payload["summary"]["requiredProbePassCount"],
            "requiredProbeFailureCount": payload["summary"]["requiredProbeFailureCount"],
            "exploreCliHelpStatus": payload["summary"]["exploreCliHelpStatus"],
            "sdkStabilityClaim": payload["summary"]["sdkStabilityClaim"],
            "publicReadinessClaim": payload["summary"]["publicReadinessClaim"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="SDK-A7 Private SDK Smoke Chain Refresh After Explore CLI Remediation",
        status=payload["status"],
        summary_rows=[
            ("source artifacts", ", ".join(payload["sourceArtifacts"])),
            ("import probe refresh count", payload["summary"]["importProbeRefreshCount"]),
            ("CLI probe refresh count", payload["summary"]["cliProbeRefreshCount"]),
            ("required probe failures", payload["summary"]["requiredProbeFailureCount"]),
            ("explore CLI help status", payload["summary"]["exploreCliHelpStatus"]),
            ("next recommended artifact", payload["summary"]["nextRecommendedArtifact"]),
        ],
        sections=[
            (
                "Import Probe Results",
                [
                    f"- `{probe['probeId']}`: `{probe['resultStatus']}` (return code `{probe['returnCode']}`)"
                    for probe in payload["importProbeResults"]
                ],
            ),
            (
                "CLI Probe Results",
                [
                    f"- `{probe['probeId']}`: `{probe['resultStatus']}` (return code `{probe['returnCode']}`)"
                    for probe in payload["cliProbeResults"]
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
    result_path = out_dir / f"sdk_a7_private_sdk_smoke_chain_refresh_after_explore_cli_remediation_{STAMP}.json"
    report_path = report_dir / f"sdk_a7_private_sdk_smoke_chain_refresh_after_explore_cli_remediation_{STAMP}.md"
    evidence_path = evidence_dir / "sdk_a7_private_sdk_smoke_chain_refresh_after_explore_cli_remediation.json"
    feed_path = command_feed_dir / f"sdk_a7_private_sdk_smoke_chain_refresh_after_explore_cli_remediation_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/sdk_a7_private_sdk_smoke_chain_refresh_after_explore_cli_remediation")
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
    print("SDK_A7_PRIVATE_SDK_SMOKE_CHAIN_REFRESH_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
