#!/usr/bin/env python3
"""SDK-A3 private SDK import and CLI smoke dry run."""

from __future__ import annotations

import argparse
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
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-06"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.private_sdk_import_cli_smoke_dry_run.v0"
STATUS = "SDK_A3_PRIVATE_SDK_IMPORT_CLI_SMOKE_DRY_RUN_FINDING"

TRUE_CLAIM_FLAGS = {
    "sdk_a2_consumed",
    "private_smoke_dry_run_created",
    "import_probe_dry_run_executed",
    "cli_probe_dry_run_executed",
    "blocked_probe_contracts_respected",
    "d109_hold_respected",
}

CLAIM_FLAGS = {
    "sdk_a2_consumed": True,
    "private_smoke_dry_run_created": True,
    "import_probe_dry_run_executed": True,
    "cli_probe_dry_run_executed": True,
    "blocked_probe_contracts_respected": True,
    "d109_hold_respected": True,
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
    "public_package_install_executed": False,
    "benchmark_executed": False,
    "forge_emit_check_executed": False,
}

NON_CLAIMS = [
    "SDK-A3 is a private local smoke dry run; it does not claim SDK stability, public readiness, API compatibility, or semantic-versioning commitments.",
    "SDK-A3 does not change SDK implementation, remediate failed probes, build native extensions, or install public packages.",
    "SDK-A3 does not claim compiler correctness, semantic preservation, runtime performance, training savings, estimator accuracy, hardware readiness, silicon readiness, or broad EML advantage.",
    "SDK-A3 respects the D109 hold and does not start D110, consume reviewer response, or record reviewer approval.",
    "SDK-A3 does not touch laptop-owned electronics repositories.",
]


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
        "executionStatus": "dry_run_executed",
        "resultStatus": status,
        "returnCode": proc.returncode,
        "stdoutPreview": proc.stdout[:500],
        "stderrPreview": proc.stderr[:500],
        "blockedClaims": probe["blockedClaims"],
    }


def run_dry_run(contract: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    specs = probe_specs()
    import_results = [_run_probe(probe, specs[probe["probeId"]]) for probe in contract["importProbeContracts"]]
    cli_results = [_run_probe(probe, specs[probe["probeId"]]) for probe in contract["cliProbeContracts"]]
    return import_results, cli_results


def build_payload() -> dict[str, Any]:
    contract = sdk_a2.build_payload()
    sdk_a2.validate_payload(contract)
    import_results, cli_results = run_dry_run(contract)
    all_results = import_results + cli_results
    required_results = [result for result in all_results if result["required"]]
    optional_results = [result for result in all_results if not result["required"]]
    required_failures = [result for result in required_results if result["resultStatus"] != "pass"]
    optional_non_fail = [
        result
        for result in optional_results
        if result["resultStatus"] in {"pass", "optional_missing", "optional_probe_failed"}
    ]
    summary = {
        "sourceArtifact": contract["artifactId"],
        "importProbeDryRunCount": len(import_results),
        "cliProbeDryRunCount": len(cli_results),
        "requiredProbePassCount": sum(1 for result in required_results if result["resultStatus"] == "pass"),
        "requiredProbeFailureCount": len(required_failures),
        "optionalProbeNonFailCount": len(optional_non_fail),
        "blockedProbeContractCount": len(contract["blockedProbeContracts"]),
        "blockedProbeExecutionCount": 0,
        "sdkImplementationChanged": False,
        "publicReadinessClaim": False,
        "sdkStabilityClaim": False,
        "finding": "cli_monogate_explore_help currently fails because eml_discover is not importable under PYTHONPATH=python.",
        "nextRecommendedArtifact": "SDK-A4 private SDK smoke result review and explore CLI surface selector",
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id="sdk-a3-private-sdk-import-cli-smoke-dry-run",
        artifact_type="private_sdk_import_cli_smoke_dry_run",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "sourceArtifact": contract["artifactId"],
            "importProbeResults": import_results,
            "cliProbeResults": cli_results,
            "blockedProbeContracts": contract["blockedProbeContracts"],
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["sourceArtifact"] != "sdk-a2-private-sdk-import-cli-smoke-contract":
        raise ValueError("SDK-A3 must consume SDK-A2")
    summary = payload["summary"]
    if summary["importProbeDryRunCount"] != 4:
        raise ValueError("import probe count drift")
    if summary["cliProbeDryRunCount"] != 4:
        raise ValueError("CLI probe count drift")
    if summary["blockedProbeExecutionCount"] != 0:
        raise ValueError("blocked probes must not execute")
    if summary["requiredProbeFailureCount"] != 1:
        raise ValueError("expected exactly one current required smoke finding")
    for key in ["sdkImplementationChanged", "publicReadinessClaim", "sdkStabilityClaim"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    result_by_id = {
        result["probeId"]: result
        for result in payload["importProbeResults"] + payload["cliProbeResults"]
    }
    for probe_id in [
        "python_import_monogate",
        "python_import_monogate_validate",
        "forge_preview_import_optional",
        "cli_monogate_capability_card_help",
        "cli_monogate_validate_help",
        "cli_forge_preview_help_optional",
    ]:
        if result_by_id[probe_id]["resultStatus"] != "pass":
            raise ValueError(f"{probe_id} must pass in current SDK-A3 smoke")
    if result_by_id["python_import_monogate_core_optional"]["resultStatus"] != "optional_missing":
        raise ValueError("native extension optional import should be recorded as optional_missing")
    if result_by_id["cli_monogate_explore_help"]["resultStatus"] != "required_probe_failed":
        raise ValueError("explore help finding must be recorded")
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
        semantic_strength="private_import_cli_smoke_dry_run_with_one_required_cli_finding",
        source=f"python/results/sdk_a3_private_sdk_import_cli_smoke_dry_run/sdk_a3_private_sdk_import_cli_smoke_dry_run_{STAMP}.json",
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="sdk_a3_private_sdk_import_cli_smoke_dry_run_feed",
        date=DATE,
        status=payload["status"],
        next_action="Review SDK-A3 dry-run finding and select bounded explore CLI surface remediation or reclassification.",
        claim_flags=payload["claimFlags"],
        fields={
            "sourceArtifact": payload["sourceArtifact"],
            "importProbeDryRunCount": payload["summary"]["importProbeDryRunCount"],
            "cliProbeDryRunCount": payload["summary"]["cliProbeDryRunCount"],
            "requiredProbeFailureCount": payload["summary"]["requiredProbeFailureCount"],
            "blockedProbeExecutionCount": payload["summary"]["blockedProbeExecutionCount"],
            "finding": payload["summary"]["finding"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="SDK-A3 Private SDK Import And CLI Smoke Dry Run",
        status=payload["status"],
        summary_rows=[
            ("source artifact", payload["sourceArtifact"]),
            ("import probe dry runs", payload["summary"]["importProbeDryRunCount"]),
            ("CLI probe dry runs", payload["summary"]["cliProbeDryRunCount"]),
            ("required probe failures", payload["summary"]["requiredProbeFailureCount"]),
            ("blocked probe executions", payload["summary"]["blockedProbeExecutionCount"]),
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
            ("Finding", [f"- {payload['summary']['finding']}"]),
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"sdk_a3_private_sdk_import_cli_smoke_dry_run_{STAMP}.json"
    report_path = report_dir / f"sdk_a3_private_sdk_import_cli_smoke_dry_run_{STAMP}.md"
    evidence_path = evidence_dir / "sdk_a3_private_sdk_import_cli_smoke_dry_run.json"
    feed_path = command_feed_dir / f"sdk_a3_private_sdk_import_cli_smoke_dry_run_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/sdk_a3_private_sdk_import_cli_smoke_dry_run")
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
    print("SDK_A3_PRIVATE_SDK_IMPORT_CLI_SMOKE_DRY_RUN_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
