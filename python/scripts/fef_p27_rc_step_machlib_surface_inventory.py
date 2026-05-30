#!/usr/bin/env python3
"""FEF-P27 rc_step_response_at_zero MachLib proof-surface inventory."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MONOGATE_ROOT = ROOT.parent
MACHLIB_BUILD_LIB = MONOGATE_ROOT / "machlib/foundations/.lake/build/lib"
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.fef_p26_rc_step_response_proof_blocker_analysis import CLAIM_FLAGS as BASE_CLAIM_FLAGS  # noqa: E402

DATE = "2026-05-30"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.fef_p27_rc_step_machlib_surface_inventory.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "FEF_P27_RC_STEP_MACHLIB_SURFACE_INVENTORY_PASS"

FEF_P26_PATH = ROOT / "reports/evidence_packets/fef_p26_rc_step_response_proof_blocker_analysis.json"

GENERATED_IMPORTS = [
    "import MachLib.EML",
    "import MachLib.Trig",
    "import MachLib.Forge",
]

RING_IMPORTS = GENERATED_IMPORTS + ["import MachLib.Ring"]

SURFACE_ITEMS = [
    {
        "id": "zero_division",
        "identifier": "zero_div",
        "neededFor": "0 / tau_val = 0",
        "expectedGeneratedSurface": False,
        "expectedRingSurface": False,
    },
    {
        "id": "division_by_zero_named",
        "identifier": "div_zero",
        "neededFor": "audit absence of named division-zero rewrite",
        "expectedGeneratedSurface": False,
        "expectedRingSurface": False,
    },
    {
        "id": "exp_zero",
        "identifier": "exp_zero",
        "neededFor": "Real.exp 0 = 1",
        "expectedGeneratedSurface": True,
        "expectedRingSurface": True,
    },
    {
        "id": "mul_zero",
        "identifier": "mul_zero",
        "neededFor": "vin * 0 = 0",
        "expectedGeneratedSurface": True,
        "expectedRingSurface": True,
    },
    {
        "id": "zero_mul",
        "identifier": "zero_mul",
        "neededFor": "0 * vin = 0 if orientation changes",
        "expectedGeneratedSurface": True,
        "expectedRingSurface": True,
    },
    {
        "id": "sub_self",
        "identifier": "sub_self",
        "neededFor": "1 - 1 = 0 after exp_zero",
        "expectedGeneratedSurface": False,
        "expectedRingSurface": True,
    },
    {
        "id": "sub_def",
        "identifier": "sub_def",
        "neededFor": "manual subtraction rewrite fallback",
        "expectedGeneratedSurface": True,
        "expectedRingSurface": True,
    },
    {
        "id": "add_neg",
        "identifier": "add_neg",
        "neededFor": "manual subtraction cancellation fallback",
        "expectedGeneratedSurface": True,
        "expectedRingSurface": True,
    },
]

CLAIM_FLAGS = {
    **dict(BASE_CLAIM_FLAGS),
    "machlib_surface_inventory_claim": False,
    "new_machlib_lemma_claim": False,
    "rc_step_response_proved_claim": False,
    "lean_proof_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
}

NON_CLAIMS = [
    "FEF-P27 records an identifier-availability inventory for the rc_step_response_at_zero proof surface.",
    "FEF-P27 does not add MachLib lemmas or change Forge/eFrog behavior.",
    "FEF-P27 does not discharge rc_step_response_at_zero.",
    "FEF-P27 does not claim broad Lean proof readiness or all generated Lean proofs are discharged.",
    "FEF-P27 does not claim compiler correctness or formal semantic equivalence.",
    "FEF-P27 does not publish a package, enable checkout, or claim production readiness.",
    "FEF-P27 does not claim runtime performance, Verilog, zkproof, silicon, hardware, or all-target readiness.",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def lean_probe(identifier: str, imports: list[str], tmp_path: Path) -> dict[str, Any]:
    lean = shutil.which("lean")
    if not lean:
        return {
            "attempted": False,
            "available": False,
            "status": "tool_unavailable",
            "returnCode": None,
            "outputExcerpt": "",
        }
    probe_path = tmp_path / f"probe_{identifier}_{len(imports)}.lean"
    probe_source = "\n".join([
        *imports,
        "",
        "open MachLib",
        "open MachLib.Real",
        f"#check {identifier}",
        "",
    ])
    probe_path.write_text(probe_source, encoding="utf-8")
    env = os.environ.copy()
    existing = env.get("LEAN_PATH", "")
    env["LEAN_PATH"] = f"{MACHLIB_BUILD_LIB}:{existing}" if existing else str(MACHLIB_BUILD_LIB)
    proc = subprocess.run(
        [lean, str(probe_path)],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    output = (proc.stdout or proc.stderr).strip()
    return {
        "attempted": True,
        "available": proc.returncode == 0,
        "status": "identifier_available" if proc.returncode == 0 else "identifier_missing",
        "returnCode": proc.returncode,
        "outputExcerpt": output[:500],
    }


def inventory_item(item: dict[str, Any], tmp_path: Path) -> dict[str, Any]:
    generated_probe = lean_probe(item["identifier"], GENERATED_IMPORTS, tmp_path)
    ring_probe = lean_probe(item["identifier"], RING_IMPORTS, tmp_path)
    row = {
        "id": item["id"],
        "identifier": item["identifier"],
        "neededFor": item["neededFor"],
        "generatedImportSurface": generated_probe,
        "ringImportSurface": ring_probe,
        "expectedGeneratedSurface": item["expectedGeneratedSurface"],
        "expectedRingSurface": item["expectedRingSurface"],
    }
    if generated_probe["available"] != item["expectedGeneratedSurface"]:
        raise ValueError(f"unexpected generated-surface result for {item['identifier']}")
    if ring_probe["available"] != item["expectedRingSurface"]:
        raise ValueError(f"unexpected ring-surface result for {item['identifier']}")
    return row


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    generated_available = [row["identifier"] for row in rows if row["generatedImportSurface"]["available"]]
    generated_missing = [row["identifier"] for row in rows if not row["generatedImportSurface"]["available"]]
    ring_available = [row["identifier"] for row in rows if row["ringImportSurface"]["available"]]
    zero_division_missing = "zero_div" in generated_missing and "zero_div" not in ring_available
    return {
        "surfaceItemCount": len(rows),
        "generatedSurfaceAvailableCount": len(generated_available),
        "generatedSurfaceMissingCount": len(generated_missing),
        "generatedSurfaceAvailable": generated_available,
        "generatedSurfaceMissing": generated_missing,
        "ringSurfaceAvailable": ring_available,
        "zeroDivisionLemmaMissing": zero_division_missing,
        "subSelfRequiresRingImport": "sub_self" in ring_available and "sub_self" in generated_missing,
        "rcStepResponseProofSurfaceComplete": False,
        "machlibSurfaceInventoryClaim": False,
        "newMachlibLemmaClaim": False,
        "rcStepResponseProvedClaim": False,
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
    fef_p26 = read_json(FEF_P26_PATH)
    with tempfile.TemporaryDirectory(prefix="fef_p27_surface_inventory_") as tmp:
        rows = [inventory_item(item, Path(tmp)) for item in SURFACE_ITEMS]
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": STATUS,
        "artifactId": "fef-p27-rc-step-machlib-surface-inventory",
        "decision": "rc_step_response_proof_surface_inventory_recorded",
        "generatedImports": list(GENERATED_IMPORTS),
        "ringImports": list(RING_IMPORTS),
        "surfaceItems": rows,
        "summary": summarize(rows),
        "fefP26Link": {
            "path": str(FEF_P26_PATH.relative_to(ROOT)),
            "reviewDecision": fef_p26["reviewDecision"],
        },
        "releaseGates": [
            {"id": "proof_surface_inventory_completed", "status": "pass"},
            {"id": "zero_division_surface_available", "status": "blocked"},
            {"id": "generated_surface_has_sub_self", "status": "blocked"},
            {"id": "rc_step_response_at_zero_discharged", "status": "blocked"},
            {"id": "public_package_published", "status": "blocked"},
        ],
        "nextMilestones": [
            "Add or identify a zero_div lemma compatible with MachLib foundations.",
            "Decide whether Forge generated Lean should import MachLib.Ring or use a proof script that avoids sub_self.",
            "Retry rc_step_response_at_zero only after the missing proof surface is closed.",
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
        "title": "FEF-P27 rc_step_response_at_zero MachLib Surface Inventory",
        "reviewDecision": payload["decision"],
        "validationStatus": "pass",
        "semanticStrength": "identifier_availability_inventory_only",
        "semanticReview": payload["summary"],
        "claimBoundary": "Identifier-availability inventory for the rc_step_response_at_zero proof surface only; it adds no MachLib lemmas, does not discharge the theorem, and makes no all-generated-file proof, compiler correctness, formal equivalence, public readiness, publication, runtime performance, hardware, or all-target readiness claim.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
        "reviewHighlights": [
            "Generated imports expose exp_zero, mul_zero, zero_mul, sub_def, and add_neg.",
            "sub_self is available only after importing MachLib.Ring.",
            "zero_div/div_zero are missing from both checked import surfaces.",
            "rc_step_response_at_zero remains blocked.",
        ],
        "validationCommands": [
            "python python/scripts/fef_p27_rc_step_machlib_surface_inventory.py --build --strict",
            "python -m pytest -q python/tests/test_fef_p27_rc_step_machlib_surface_inventory.py",
        ],
    }


def build_command_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.command_feed.fef_p27_rc_step_machlib_surface_inventory.v0",
        "date": DATE,
        "title": "FEF-P27 rc_step_response_at_zero MachLib Surface Inventory",
        "status": payload["status"],
        "decision": payload["decision"],
        "summary": payload["summary"],
        "topFollowup": "Add or identify zero_div before retrying rc_step_response_at_zero.",
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def render_report(payload: dict[str, Any]) -> str:
    rows = [
        "| Identifier | Generated imports | Ring import | Needed for |",
        "|---|---:|---:|---|",
    ]
    for row in payload["surfaceItems"]:
        rows.append(
            f"| `{row['identifier']}` | `{row['generatedImportSurface']['status']}` | "
            f"`{row['ringImportSurface']['status']}` | {row['neededFor']} |"
        )
    summary = payload["summary"]
    return "\n".join(
        [
            "# FEF-P27 rc_step_response_at_zero MachLib Surface Inventory",
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
            f"- Surface items checked: `{summary['surfaceItemCount']}`",
            f"- Generated-surface available: `{summary['generatedSurfaceAvailableCount']}`",
            f"- Generated-surface missing: `{summary['generatedSurfaceMissingCount']}`",
            f"- Zero-division lemma missing: `{summary['zeroDivisionLemmaMissing']}`",
            f"- `sub_self` requires `MachLib.Ring`: `{summary['subSelfRequiresRingImport']}`",
            "",
            "## Boundary",
            "",
            "- Identifier inventory only; no MachLib lemma or Forge/eFrog behavior change.",
            "- `rc_step_response_at_zero` remains undischarged.",
            "- No all-generated-file proof, compiler-correctness, formal-equivalence, or public-readiness claim.",
            "- No package publication, checkout, performance, hardware, or all-target claim.",
            "",
        ]
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("invalid FEF-P27 schema")
    summary = payload["summary"]
    if summary["surfaceItemCount"] != len(SURFACE_ITEMS):
        raise ValueError("unexpected surface item count")
    if not summary["zeroDivisionLemmaMissing"]:
        raise ValueError("zero_div must remain missing for this inventory")
    if not summary["subSelfRequiresRingImport"]:
        raise ValueError("sub_self should require MachLib.Ring in this inventory")
    if summary["rcStepResponseProofSurfaceComplete"] is not False:
        raise ValueError("rc step proof surface must remain incomplete")
    for key in [
        "machlibSurfaceInventoryClaim",
        "newMachlibLemmaClaim",
        "rcStepResponseProvedClaim",
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
    result_path = out_dir / f"fef_p27_rc_step_machlib_surface_inventory_{STAMP}.json"
    report_path = report_dir / f"fef_p27_rc_step_machlib_surface_inventory_{STAMP}.md"
    evidence_path = evidence_dir / "fef_p27_rc_step_machlib_surface_inventory.json"
    feed_path = command_feed_dir / f"fef_p27_rc_step_machlib_surface_inventory_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/fef_p27_rc_step_machlib_surface_inventory")
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
    print("FEF_P27_RC_STEP_MACHLIB_SURFACE_INVENTORY_OK")
    print(f"surface_items={built['payload']['summary']['surfaceItemCount']}")
    print(f"zero_div_missing={built['payload']['summary']['zeroDivisionLemmaMissing']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
