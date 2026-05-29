#!/usr/bin/env python3
"""Validate Monogate proof-carrying artifact contract instances."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

SCHEMA_VERSION = "monogate.proof_carrying_artifact_contract_validator.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "PCC_M3_CONTRACT_VALIDATOR_PASS"
BATCH_STATUS = "PCC_M5_CONTRACT_BATCH_VALIDATOR_PASS"
BATCH_FAIL_STATUS = "PCC_M5_CONTRACT_BATCH_VALIDATOR_FAIL"

DEFAULT_CONTRACT = ROOT / "reports/proof_carrying_artifacts/a13_forge_efrog_contract_2026_05_29.json"
DEFAULT_CONTRACTS_DIR = ROOT / "reports/proof_carrying_artifacts"

REQUIRED_FIELDS = [
    "schemaVersion",
    "artifactId",
    "artifactKind",
    "payloadReference",
    "evidenceReferences",
    "obligations",
    "claimBoundary",
    "claimFlags",
    "nonClaims",
]

ALLOWED_ARTIFACT_KINDS = {
    "compiler_output",
    "decompiler_output",
    "rescue_packet",
    "replay_trace",
    "understanding_packet",
    "forecast_packet",
    "hardware_packet",
    "research_map",
}

ALLOWED_OBLIGATION_KINDS = {
    "schema_validation",
    "replay_validation",
    "sample_grid_agreement",
    "formal_witness",
    "human_review",
    "claim_boundary_review",
    "external_source_review",
}

ALLOWED_STATUSES = {"discharged", "partial", "blocked", "not_applicable", "unresolved"}

RISKY_FLAG_NON_CLAIMS = {
    "pcc_completeness_claim": ["foundational pcc", "pcc"],
    "compiler_correctness_claim": ["compiler correctness"],
    "formal_equivalence_claim": ["formal equivalence"],
    "production_toolchain_claim": ["production"],
    "runtime_performance_claim": ["runtime performance"],
    "public_ready": ["public", "publish"],
    "safe_to_publish_publicly": ["public", "publish"],
    "broad_eml_advantage_claim": ["broad eml advantage", "eml advantage"],
}

NON_CLAIMS = [
    "The contract validator checks structure and claim-boundary consistency only.",
    "The contract validator does not prove compiler correctness or formal equivalence.",
    "The contract validator does not make any artifact public-ready, production-ready, or runtime-performance-backed.",
]

CLAIM_FLAGS = {
    "proof_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "pcc_completeness_claim": False,
    "production_toolchain_claim": False,
    "runtime_performance_claim": False,
    "public_ready": False,
    "safe_to_publish_publicly": False,
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def contract_paths(contract: dict[str, Any]) -> list[str]:
    paths = [contract.get("payloadReference", "")]
    paths.extend(contract.get("evidenceReferences", []))
    for obligation in contract.get("obligations", []):
        discharge = obligation.get("dischargeArtifact", "")
        if discharge:
            paths.append(discharge)
    return paths


def path_exists(path_text: str) -> bool:
    if not path_text:
        return False
    path = Path(path_text)
    if path.is_absolute():
        return path.exists()
    return (ROOT / path).exists()


def normalized_non_claims(contract: dict[str, Any]) -> str:
    return " ".join(contract.get("nonClaims", [])).lower()


def validate_contract(contract: dict[str, Any], *, check_paths: bool = True) -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []

    for field in REQUIRED_FIELDS:
        if field not in contract:
            failures.append(f"missing required field: {field}")

    if failures:
        return result(contract, failures, warnings)

    if contract["schemaVersion"] != "monogate.proof_carrying_artifact_contract.v0":
        failures.append("unexpected schemaVersion")
    if contract["artifactKind"] not in ALLOWED_ARTIFACT_KINDS:
        failures.append(f"unknown artifactKind: {contract['artifactKind']}")
    if not isinstance(contract["evidenceReferences"], list) or not contract["evidenceReferences"]:
        failures.append("evidenceReferences must be a non-empty array")
    if not isinstance(contract["obligations"], list) or not contract["obligations"]:
        failures.append("obligations must be a non-empty array")
    if not isinstance(contract["claimFlags"], dict):
        failures.append("claimFlags must be an object")
    if not isinstance(contract["nonClaims"], list) or not contract["nonClaims"]:
        failures.append("nonClaims must be a non-empty array")

    for key, value in contract.get("claimFlags", {}).items():
        if value is not False:
            failures.append(f"claim flag must be false: {key}")

    status_counts: dict[str, int] = {}
    obligation_ids: set[str] = set()
    for index, obligation in enumerate(contract.get("obligations", [])):
        prefix = f"obligations[{index}]"
        for field in ["obligationId", "obligationKind", "status", "dischargeArtifact"]:
            if field not in obligation:
                failures.append(f"{prefix} missing {field}")
        obligation_id = obligation.get("obligationId")
        if obligation_id in obligation_ids:
            failures.append(f"duplicate obligationId: {obligation_id}")
        obligation_ids.add(obligation_id)
        if obligation.get("obligationKind") not in ALLOWED_OBLIGATION_KINDS:
            failures.append(f"{prefix} unknown obligationKind: {obligation.get('obligationKind')}")
        status = obligation.get("status")
        if status not in ALLOWED_STATUSES:
            failures.append(f"{prefix} unknown status: {status}")
        else:
            status_counts[status] = status_counts.get(status, 0) + 1
        if status in {"discharged", "partial"} and not obligation.get("dischargeArtifact"):
            failures.append(f"{prefix} {status} obligation must name a dischargeArtifact")
        if status == "blocked" and obligation.get("dischargeArtifact"):
            warnings.append(f"{prefix} blocked obligation has a dischargeArtifact")

    non_claims = normalized_non_claims(contract)
    for flag, required_phrases in RISKY_FLAG_NON_CLAIMS.items():
        if flag in contract.get("claimFlags", {}):
            if not any(phrase in non_claims for phrase in required_phrases):
                failures.append(f"{flag} needs an explicit matching non-claim")

    if check_paths:
        missing_paths = [path for path in sorted(set(contract_paths(contract))) if not path_exists(path)]
        if missing_paths:
            failures.extend(f"referenced path missing: {path}" for path in missing_paths)

    return result(contract, failures, warnings, status_counts)


def result(
    contract: dict[str, Any],
    failures: list[str],
    warnings: list[str],
    status_counts: dict[str, int] | None = None,
) -> dict[str, Any]:
    counts = status_counts or {}
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": STATUS if not failures else "PCC_M3_CONTRACT_VALIDATOR_FAIL",
        "contractId": contract.get("artifactId", "unknown"),
        "summary": {
            "valid": not failures,
            "failureCount": len(failures),
            "warningCount": len(warnings),
            "obligationCount": len(contract.get("obligations", [])) if isinstance(contract, dict) else 0,
            "dischargedObligations": counts.get("discharged", 0),
            "partialObligations": counts.get("partial", 0),
            "blockedObligations": counts.get("blocked", 0),
            "unresolvedObligations": counts.get("unresolved", 0),
            "notApplicableObligations": counts.get("not_applicable", 0),
        },
        "failures": failures,
        "warnings": warnings,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_evidence_packet(payload: dict[str, Any], *, artifact_id: str, title: str, next_step: str) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": artifact_id,
        "title": title,
        "reviewDecision": "private_validator_recorded",
        "validationStatus": "pass" if payload["summary"]["valid"] else "fail",
        "replayStatus": "not_applicable",
        "semanticStrength": "contract_structure_and_claim_boundary_validator",
        "semanticReview": payload["summary"],
        "claimBoundary": "Validator for proof-carrying artifact contracts only; no compiler correctness, formal equivalence, production readiness, public readiness, or proof-strength claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "nextStep": next_step,
    }


def command_feed(payload: dict[str, Any], *, title: str, next_step: str) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_center_feed.v0",
        "title": title,
        "status": payload["status"],
        "summary": payload["summary"],
        "nextStep": next_step,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any], *, title: str) -> str:
    lines = [
        f"# {title}",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Summary",
        "",
        f"- contract: `{payload['contractId']}`",
        f"- valid: `{payload['summary']['valid']}`",
        f"- obligations: `{payload['summary']['obligationCount']}`",
        f"- discharged: `{payload['summary']['dischargedObligations']}`",
        f"- partial: `{payload['summary']['partialObligations']}`",
        f"- blocked: `{payload['summary']['blockedObligations']}`",
        f"- unresolved: `{payload['summary']['unresolvedObligations']}`",
        "",
        "## Boundary",
        "",
        "- Validates structure and claim-boundary consistency only.",
        "- Does not prove compiler correctness or formal equivalence.",
        "- Does not make the artifact public-ready or production-ready.",
        "",
    ]
    if payload["failures"]:
        lines.extend(["## Failures", ""])
        lines.extend(f"- {failure}" for failure in payload["failures"])
        lines.append("")
    return "\n".join(lines)


def build_validator(
    contract_path: Path,
    out_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
    *,
    check_paths: bool = True,
    result_stem: str = "pcc_m3_contract_validator_2026_05_29",
    feed_stem: str = "pcc_m3_contract_validator_feed_2026_05_29",
    evidence_id: str = "pcc-m3-contract-validator",
    title: str = "PCC-M3 Contract Validator",
    next_step: str = "PCC-M4: validate a second artifact family, preferably Forge Rescue or EML Advantage Lab.",
) -> dict[str, Any]:
    contract = read_json(contract_path)
    payload = validate_contract(contract, check_paths=check_paths)
    evidence = build_evidence_packet(payload, artifact_id=evidence_id, title=title, next_step=next_step)
    feed = command_feed(payload, title=title, next_step=next_step)

    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)

    result_path = out_dir / f"{result_stem}.json"
    report_path = report_dir / f"{result_stem}.md"
    evidence_path = evidence_dir / f"{evidence_id.replace('-', '_')}.json"
    feed_path = command_feed_dir / f"{feed_stem}.json"

    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload, title=title), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return {
        "payload": payload,
        "evidence": evidence,
        "feed": feed,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def build_batch_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "pcc-m5-contract-batch-validator",
        "title": "PCC-M5 Contract Batch Validator",
        "reviewDecision": "private_batch_validator_recorded",
        "validationStatus": "pass" if payload["summary"]["valid"] else "fail",
        "replayStatus": "not_applicable",
        "semanticStrength": "batch_contract_structure_and_claim_boundary_validator",
        "semanticReview": payload["summary"],
        "claimBoundary": "Batch validator for proof-carrying artifact contracts only; no compiler correctness, formal equivalence, production readiness, public readiness, or proof-strength claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "nextStep": "PCC-M6: add this batch validator to CI once the contract registry stabilizes.",
    }


def build_batch_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_center_feed.v0",
        "title": "PCC-M5 Contract Batch Validator",
        "status": payload["status"],
        "summary": payload["summary"],
        "nextStep": "PCC-M6: add this batch validator to CI once the contract registry stabilizes.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_batch_report(payload: dict[str, Any]) -> str:
    lines = [
        "# PCC-M5 Contract Batch Validator",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Summary",
        "",
        f"- contracts: `{payload['summary']['contractCount']}`",
        f"- valid contracts: `{payload['summary']['validContractCount']}`",
        f"- failed contracts: `{payload['summary']['failedContractCount']}`",
        f"- obligations: `{payload['summary']['obligationCount']}`",
        f"- discharged: `{payload['summary']['dischargedObligations']}`",
        f"- partial: `{payload['summary']['partialObligations']}`",
        f"- blocked: `{payload['summary']['blockedObligations']}`",
        f"- unresolved: `{payload['summary']['unresolvedObligations']}`",
        "",
        "## Contracts",
        "",
        "| Contract | Valid | Obligations | Failures |",
        "| --- | --- | --- | --- |",
    ]
    for item in payload["contracts"]:
        lines.append(
            f"| `{item['contractId']}` | `{item['summary']['valid']}` | "
            f"`{item['summary']['obligationCount']}` | `{item['summary']['failureCount']}` |"
        )
    lines.extend([
        "",
        "## Boundary",
        "",
        "- Batch-validates structure and claim-boundary consistency only.",
        "- Does not prove compiler correctness or formal equivalence.",
        "- Does not make any artifact public-ready or production-ready.",
        "",
    ])
    return "\n".join(lines)


def build_batch_validator(
    contracts_dir: Path,
    out_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
    *,
    check_paths: bool = True,
) -> dict[str, Any]:
    contract_paths = sorted(contracts_dir.glob("*.json"))
    contracts = []
    totals = {
        "obligationCount": 0,
        "dischargedObligations": 0,
        "partialObligations": 0,
        "blockedObligations": 0,
        "unresolvedObligations": 0,
        "notApplicableObligations": 0,
        "failureCount": 0,
        "warningCount": 0,
    }
    for path in contract_paths:
        payload = validate_contract(read_json(path), check_paths=check_paths)
        payload["sourcePath"] = str(path.resolve().relative_to(ROOT))
        contracts.append(payload)
        for key in totals:
            totals[key] += int(payload["summary"].get(key, 0))

    failed = [payload for payload in contracts if not payload["summary"]["valid"]]
    summary = {
        "valid": not failed and bool(contracts),
        "contractCount": len(contracts),
        "validContractCount": len(contracts) - len(failed),
        "failedContractCount": len(failed),
        **totals,
    }
    payload = {
        "schemaVersion": "monogate.proof_carrying_artifact_contract_batch_validator.v0",
        "status": BATCH_STATUS if summary["valid"] else BATCH_FAIL_STATUS,
        "summary": summary,
        "contracts": contracts,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    evidence = build_batch_evidence_packet(payload)
    feed = build_batch_command_feed(payload)

    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)

    result_path = out_dir / "pcc_m5_contract_batch_validator_2026_05_29.json"
    report_path = report_dir / "pcc_m5_contract_batch_validator_2026_05_29.md"
    evidence_path = evidence_dir / "pcc_m5_contract_batch_validator.json"
    feed_path = command_feed_dir / "pcc_m5_contract_batch_validator_feed_2026_05_29.json"

    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_batch_report(payload), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    feed_path.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return {
        "payload": payload,
        "evidence": evidence,
        "feed": feed,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--contracts-dir", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/proof_carrying_artifact_contract_validator")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    parser.add_argument("--result-stem", default="pcc_m3_contract_validator_2026_05_29")
    parser.add_argument("--feed-stem", default="pcc_m3_contract_validator_feed_2026_05_29")
    parser.add_argument("--evidence-id", default="pcc-m3-contract-validator")
    parser.add_argument("--title", default="PCC-M3 Contract Validator")
    parser.add_argument("--next-step", default="PCC-M4: validate a second artifact family, preferably Forge Rescue or EML Advantage Lab.")
    parser.add_argument("--no-path-check", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    if args.contracts_dir is not None:
        built = build_batch_validator(
            args.contracts_dir,
            args.out_dir,
            args.report_dir,
            args.evidence_dir,
            args.command_feed_dir,
            check_paths=not args.no_path_check,
        )
        payload = built["payload"]
        if args.strict and not payload["summary"]["valid"]:
            print(json.dumps(payload["summary"], indent=2), file=sys.stderr)
            return 1
        print("PCC_M5_CONTRACT_BATCH_VALIDATOR_OK" if payload["summary"]["valid"] else "PCC_M5_CONTRACT_BATCH_VALIDATOR_FAIL")
        print(f"contracts={payload['summary']['contractCount']}")
        print(f"obligations={payload['summary']['obligationCount']}")
        print(f"result={built['result_path']}")
        return 0 if payload["summary"]["valid"] else 1

    built = build_validator(
        args.contract,
        args.out_dir,
        args.report_dir,
        args.evidence_dir,
        args.command_feed_dir,
        check_paths=not args.no_path_check,
        result_stem=args.result_stem,
        feed_stem=args.feed_stem,
        evidence_id=args.evidence_id,
        title=args.title,
        next_step=args.next_step,
    )
    payload = built["payload"]
    if args.strict and not payload["summary"]["valid"]:
        print(json.dumps(payload["failures"], indent=2), file=sys.stderr)
        return 1
    print("PCC_M3_CONTRACT_VALIDATOR_OK" if payload["summary"]["valid"] else "PCC_M3_CONTRACT_VALIDATOR_FAIL")
    print(f"contract={payload['contractId']}")
    print(f"obligations={payload['summary']['obligationCount']}")
    print(f"result={built['result_path']}")
    return 0 if payload["summary"]["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
