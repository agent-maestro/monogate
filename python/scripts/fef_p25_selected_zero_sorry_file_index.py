#!/usr/bin/env python3
"""FEF-P25 selected generated Lean zero-sorry file index."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p25_selected_zero_sorry_file_index.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P25_SELECTED_ZERO_SORRY_FILE_INDEX_PASS"

INPUTS = [
    {
        "artifactId": "fef-p18-selected-lean-proof-discharge",
        "path": ROOT / "reports/evidence_packets/fef_p18_selected_lean_proof_discharge.json",
        "selectedFile": "verified_add",
        "sourcePath": "examples/verified_add.eml",
        "expectedStatus": "selected_file_zero_sorry",
    },
    {
        "artifactId": "fef-p21-rc-filter-lean-proof-discharge",
        "path": ROOT / "reports/evidence_packets/fef_p21_rc_filter_lean_proof_discharge.json",
        "selectedFile": "rc_filter",
        "sourcePath": "examples/rc_filter.eml",
        "expectedStatus": "selected_file_remaining_sorry",
    },
    {
        "artifactId": "fef-p23-voltage-divider-full-lean-proof-discharge",
        "path": ROOT / "reports/evidence_packets/fef_p23_voltage_divider_full_lean_proof_discharge.json",
        "selectedFile": "voltage_divider",
        "sourcePath": "examples/voltage_divider.eml",
        "expectedStatus": "selected_file_zero_sorry",
    },
    {
        "artifactId": "fef-p24-mosfet-full-lean-proof-discharge",
        "path": ROOT / "reports/evidence_packets/fef_p24_mosfet_full_lean_proof_discharge.json",
        "selectedFile": "mosfet_iv",
        "sourcePath": "examples/carriers/electronics/mosfet_iv.eml",
        "expectedStatus": "selected_file_zero_sorry",
    },
]

CLAIM_FLAGS = {
    "zero_sorry_index_claim": False,
    "lean_proof_claim": False,
    "all_generated_lean_files_proved_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "runtime_performance_claim": False,
    "target_all_ready_claim": False,
    "package_published": False,
    "public_ready": False,
    "safe_to_publish_publicly": False,
}

NON_CLAIMS = [
    "FEF-P25 indexes selected generated Lean files with existing zero-sorry evidence packets.",
    "FEF-P25 does not generate new proofs or rewrite generated Lean artifacts.",
    "FEF-P25 does not claim all generated Lean files are proved or zero-sorry.",
    "FEF-P25 keeps rc_filter's rc_step_response_at_zero blocker visible.",
    "FEF-P25 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P25 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P25 does not claim runtime performance, Verilog, zkproof, silicon, hardware, or all-target readiness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def classify_input(entry: dict[str, Any]) -> dict[str, Any]:
    evidence = read_json(entry["path"])
    review = evidence["semanticReview"]
    remaining = review.get("remainingPlaceholderTheoremCount", review.get("dischargedSorryCount"))
    discharged = review.get("selectedDischargedTheoremCount", review.get("selectedProofDischargePassCount"))
    if remaining is None or discharged is None:
        raise ValueError(f"unsupported evidence summary shape: {entry['artifactId']}")
    status = "selected_file_zero_sorry" if remaining == 0 else "selected_file_remaining_sorry"
    row = {
        "artifactId": entry["artifactId"],
        "evidencePath": str(entry["path"].relative_to(ROOT)),
        "selectedFile": entry["selectedFile"],
        "sourcePath": entry["sourcePath"],
        "status": status,
        "selectedDischargedTheoremCount": discharged,
        "remainingPlaceholderTheoremCount": remaining,
        "leanCheckStatuses": review["leanCheckStatuses"],
        "expectedStatus": entry["expectedStatus"],
    }
    if row["status"] != row["expectedStatus"]:
        raise ValueError(f"unexpected zero-sorry status for {entry['artifactId']}: {row['status']}")
    return row


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    zero_sorry = [row for row in rows if row["status"] == "selected_file_zero_sorry"]
    remaining = [row for row in rows if row["status"] != "selected_file_zero_sorry"]
    return {
        "indexedSelectedFileCount": len(rows),
        "selectedZeroSorryFileCount": len(zero_sorry),
        "selectedRemainingSorryFileCount": len(remaining),
        "selectedZeroSorryFiles": [row["selectedFile"] for row in zero_sorry],
        "selectedRemainingSorryFiles": [row["selectedFile"] for row in remaining],
        "selectedDischargedTheoremCount": sum(row["selectedDischargedTheoremCount"] for row in rows),
        "remainingPlaceholderTheoremCount": sum(row["remainingPlaceholderTheoremCount"] for row in rows),
        "rcStepResponseAtZeroStillBlocked": "rc_filter" in [row["selectedFile"] for row in remaining],
        "zeroSorryIndexClaim": False,
        "leanProofClaim": False,
        "allGeneratedLeanFilesProvedClaim": False,
        "compilerCorrectnessClaim": False,
        "formalEquivalenceClaim": False,
        "runtimePerformanceClaim": False,
        "targetAllReadyClaim": False,
        "packagePublished": False,
        "publicReady": False,
        "safeToPublishPublicly": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }


def build_payload() -> dict[str, Any]:
    rows = [classify_input(entry) for entry in INPUTS]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p25-selected-zero-sorry-file-index",
        "decision": "selected_generated_lean_zero_sorry_file_index_recorded",
        "indexedFiles": rows,
        "summary": summarize(rows),
        "releaseGates": [
            {"id": "selected_zero_sorry_files_indexed", "status": "pass"},
            {"id": "rc_filter_blocker_visible", "status": "pass"},
            {"id": "all_generated_lean_files_zero_sorry", "status": "blocked"},
            {"id": "machlib_foundational_audit", "status": "blocked"},
            {"id": "public_package_published", "status": "blocked"},
        ],
        "nextMilestones": [
            "Target rc_step_response_at_zero only after a valid proof path exists.",
            "Expand selected zero-sorry coverage one generated Lean file at a time.",
            "Keep broad Lean proof-readiness and compiler-correctness claims blocked.",
        ],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }
    validate_payload(payload)
    return payload


def build_evidence_packet(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "title": "FEF-P25 Selected Zero-Sorry File Index",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "selected_generated_lean_file_index_only",
        "semanticReview": payload["summary"],
        "claimBoundary": "Index of selected generated Lean files with prior zero-sorry evidence only; rc_filter remains blocked by rc_step_response_at_zero, and there is no all-generated-file proof, compiler correctness, formal equivalence, public readiness, publication, runtime performance, hardware, or all-target readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "verified_add, voltage_divider, and mosfet_iv have selected-file zero-sorry evidence.",
            "rc_filter remains indexed with one visible selected-file blocker.",
            "FEF-P25 is an index over previous evidence packets, not a new proof-generation pass.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p25_selected_zero_sorry_file_index.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p25_selected_zero_sorry_file_index.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p25_selected_zero_sorry_file_index.v0",
        "date": DATE,
        "title": "FEF-P25 Selected Zero-Sorry File Index",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Target rc_step_response_at_zero only after a valid proof path exists.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    rows = [
        "| Selected file | Status | Discharged | Remaining | Evidence |",
        "|---|---:|---:|---:|---|",
    ]
    for row in payload["indexedFiles"]:
        rows.append(
            f"| `{row['selectedFile']}` | `{row['status']}` | "
            f"`{row['selectedDischargedTheoremCount']}` | "
            f"`{row['remainingPlaceholderTheoremCount']}` | `{row['evidencePath']}` |"
        )
    summary = payload["summary"]
    return "\n".join(
        [
            "# FEF-P25 Selected Zero-Sorry File Index",
            "",
            f"Date: {DATE}",
            "",
            f"Status: `{payload['status']}`",
            "",
            f"Decision: `{payload['decision']}`",
            "",
            *rows,
            "",
            "## Summary",
            "",
            f"- Indexed selected files: `{summary['indexedSelectedFileCount']}`",
            f"- Selected zero-sorry files: `{summary['selectedZeroSorryFileCount']}`",
            f"- Selected files with remaining placeholders: `{summary['selectedRemainingSorryFileCount']}`",
            f"- Remaining placeholders in indexed files: `{summary['remainingPlaceholderTheoremCount']}`",
            "",
            "## Boundary",
            "",
            "- Index over prior selected-file evidence only.",
            "- `rc_filter` remains blocked by `rc_step_response_at_zero`.",
            "- No all-generated-file proof, compiler-correctness, formal-equivalence, or public-readiness claim.",
            "- No package publication, checkout, performance, hardware, or all-target claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P25 schema")
    summary = payload["summary"]
    if summary["indexedSelectedFileCount"] != 4:
        raise ValueError("expected four indexed selected files")
    if summary["selectedZeroSorryFileCount"] != 3:
        raise ValueError("expected three selected zero-sorry files")
    if summary["selectedRemainingSorryFileCount"] != 1:
        raise ValueError("expected one selected file with remaining placeholders")
    if summary["selectedRemainingSorryFiles"] != ["rc_filter"]:
        raise ValueError("rc_filter must remain the visible selected-file blocker")
    if summary["remainingPlaceholderTheoremCount"] != 1:
        raise ValueError("expected one remaining indexed placeholder")
    for key in [
        "zeroSorryIndexClaim",
        "leanProofClaim",
        "allGeneratedLeanFilesProvedClaim",
        "compilerCorrectnessClaim",
        "formalEquivalenceClaim",
        "runtimePerformanceClaim",
        "targetAllReadyClaim",
        "packagePublished",
        "publicReady",
        "safeToPublishPublicly",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")
    for key, value in payload["claimFlags"].items():
        if value is not False:
            raise ValueError(f"payload claim flag must remain false: {key}")


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    evidence = build_evidence_packet(payload)
    feed = build_command_feed(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    command_feed_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"fef_p25_selected_zero_sorry_file_index_{STAMP}.json"
    report_path = report_dir / f"fef_p25_selected_zero_sorry_file_index_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p25_selected_zero_sorry_file_index.json"
    feed_path = command_feed_dir / f"fef_p25_selected_zero_sorry_file_index_feed_{STAMP}.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p25_selected_zero_sorry_file_index")
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
    print("FEF_P25_SELECTED_ZERO_SORRY_FILE_INDEX_OK")
    print(f"selected_zero_sorry_files={built['payload']['summary']['selectedZeroSorryFileCount']}")
    print(f"remaining_selected_files={built['payload']['summary']['selectedRemainingSorryFileCount']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
