#!/usr/bin/env python3
"""PUB-R0 canonical brake-side ledger generator.

Emits one canonical JSON ledger enumerating:

- Held lanes (from EH-A7 lane-state aggregation)
- Retracted claims (from monogate-research graph.json, status='retracted')
- Negative results (from monogate-research graph.json, status='negative_result')
- Standing claim rule (frozen verbatim quote, drift-tested against WELCOME.md)
- Lean status line (theorem/sorry counts emitted by builder_v2.py summary)

No hand-written ledger fields. All fields are byte-derived from canonical
sources. Any markdown or HTML form is a deterministic render of this JSON.
This generator never publishes, deploys, or modifies any public surface.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MONOGATE_RESEARCH = ROOT.parent / "monogate-research"
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import eh_a7_private_command_feed_lane_state_aggregation as eh_a7  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-10"
STAMP = DATE.replace("-", "_")
EH_A7_STAMP = "2026_06_08"
SCHEMA_VERSION = "monogate.pub_r0_brake_side_ledger.v0"
STATUS = "PUB_R0_BRAKE_SIDE_LEDGER_GENERATOR_PASS"
ARTIFACT_ID = "pub-r0-brake-side-ledger-generator"

# Frozen verbatim quote of the standing claim rule (WELCOME.md lines 70-73 as of
# commit 8c5236c). Drift is tested against WELCOME.md in the test suite.
STANDING_CLAIM_RULE = (
    "No training-cost estimate, training-savings, estimator-accuracy, runtime "
    "performance, compiler-correctness, SDK-stability, hardware-readiness, "
    "silicon-readiness, catalog-completeness, or broad EML-advantage claim unless "
    "a bounded artifact proves that exact claim."
)

ONE_LINE_TEXT_MAX = 160

TRUE_CLAIM_FLAGS = {
    "graph_json_consumed",
    "eh_a7_lane_state_consumed",
    "welcome_md_standing_rule_quoted_verbatim",
    "lean_status_subprocess_consumed",
    "ledger_byte_derived_from_canonical_sources",
    "no_hand_written_ledger_fields",
    "single_canonical_json_output",
    "public_surface_blocked",
}

CLAIM_FLAGS = {
    "graph_json_consumed": True,
    "eh_a7_lane_state_consumed": True,
    "welcome_md_standing_rule_quoted_verbatim": True,
    "lean_status_subprocess_consumed": True,
    "ledger_byte_derived_from_canonical_sources": True,
    "no_hand_written_ledger_fields": True,
    "single_canonical_json_output": True,
    "public_surface_blocked": True,
    "page_rendered": False,
    "page_published": False,
    "html_rendered": False,
    "live_deploy_executed": False,
    "drift_guard_implemented": False,
    "post_deploy_probe_executed": False,
    "dashboard_ui_created": False,
    "public_dashboard_created": False,
    "public_surface_updated": False,
    "public_readiness_claim": False,
    "public_copy_approved": False,
    "ledger_completeness_claim": False,
    "renderer_correctness_claim": False,
    "visualization_quality_claim": False,
    "training_cost_estimator_reopened": False,
    "training_cost_estimator_implemented": False,
    "estimate_values_produced": False,
    "training_savings_claim": False,
    "estimator_accuracy_claim": False,
    "product_implementation_started": False,
    "product_roadmap_reopened": False,
    "atlas_reviewer_response_consumed": False,
    "atlas_public_promotion": False,
    "atlas_catalog_completeness_claim": False,
    "public_math_promotion": False,
    "d110_started": False,
    "reviewer_response_consumed": False,
    "reviewer_approval_recorded": False,
    "laptop_artifact_consumed": False,
    "electronics_inbox_reopened": False,
    "electronics_repo_touched": False,
    "laptop_owned_repo_touched": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "runtime_lowering_changed": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "hardware_readiness_claim": False,
    "silicon_readiness_claim": False,
    "broad_eml_advantage_claim": False,
}

NON_CLAIMS = [
    "PUB-R0 generates one canonical JSON ledger; it does not render markdown or HTML, publish, deploy, or update any public surface.",
    "PUB-R0 does not implement PUB-R1, the drift guard, the post-deploy probe, or the deploy authorization artifact.",
    "PUB-R0 does not claim ledger completeness; it enumerates the brake-side rows currently visible in canonical state (graph.json status, EH-A7 lane states, WELCOME.md standing rule, builder_v2.py summary Lean line). Sources that drift will surface as ledger drift, not as silent omission.",
    "PUB-R0 does not reopen training-cost, Atlas, public-math, product-roadmap, or electronics lanes; it merely records that they are held.",
    "PUB-R0 does not publish, approve public copy, update public/dev surfaces, create SDK/course material, consume reviewer response, record reviewer approval, start D110, edit MachLib, run Lean type-checking against MachLib, change runtime lowering, or touch laptop-owned repositories.",
    "PUB-R0 does not claim estimator accuracy, training savings, runtime performance, compiler correctness, hardware readiness, silicon readiness, public readiness, catalog completeness, or broad EML advantage.",
]


def _one_line(text: str) -> str:
    flat = " ".join(text.split())
    if len(flat) > ONE_LINE_TEXT_MAX:
        flat = flat[: ONE_LINE_TEXT_MAX - 1] + "…"
    return flat


def _relative_source(source: str) -> str:
    abs_path = Path(source)
    try:
        return str(abs_path.relative_to(MONOGATE_RESEARCH))
    except ValueError:
        return source


def load_graph_payload(graph_json_path: Path | None = None) -> dict[str, Any]:
    path = graph_json_path or (MONOGATE_RESEARCH / "tools/graph/output/graph.json")
    if not path.exists():
        raise FileNotFoundError(
            f"graph.json not found at {path}; run "
            "`python tools/graph/builder_v2.py build` from monogate-research first"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def extract_claims_by_status(graph: dict[str, Any], status: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for node in graph.get("nodes", []):
        if node.get("type") != "claim" or node.get("status") != status:
            continue
        rows.append(
            {
                "claimId": node.get("id"),
                "source": _relative_source(str(node.get("source", "?"))),
                "line": node.get("line"),
                "oneLineText": _one_line(node.get("text", "")),
            }
        )
    rows.sort(key=lambda row: (row["source"], row["line"] or 0, row["claimId"]))
    return rows


def load_eh_a7_result(eh_a7_path: Path | None = None) -> dict[str, Any]:
    path = eh_a7_path or (
        ROOT
        / "python/results/eh_a7_private_command_feed_lane_state_aggregation"
        / f"eh_a7_private_command_feed_lane_state_aggregation_{EH_A7_STAMP}.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    eh_a7.validate_payload(payload)
    return payload


def held_lanes_from_eh_a7(eh_a7_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in eh_a7_payload["laneStateRows"]:
        status = row["laneStatus"]
        if not (status.startswith("held") or status.startswith("paused") or status.startswith("pending")):
            continue
        rows.append(
            {
                "laneId": row["laneId"],
                "holdingArtifactId": row["feedId"],
                "oneLineReason": _one_line(status),
            }
        )
    rows.sort(key=lambda row: row["laneId"])
    return rows


_LEAN_LINE_RE = re.compile(
    r"LEAN:\s+(?P<theorems>\d+)\s+theorems,\s+(?P<sorries>\d+)\s+sorries"
)
_MACHLIB_LINE_RE = re.compile(
    r"MACHLIB:.*?(?P<core>\d+)\s+core\s+sorries,\s+(?P<discovered>\d+)\s+discovered\s+sorries"
)


def parse_lean_status_text(summary_text: str) -> dict[str, int]:
    lean_match = _LEAN_LINE_RE.search(summary_text)
    if not lean_match:
        raise ValueError("LEAN line not found in builder_v2 summary output")
    machlib_match = _MACHLIB_LINE_RE.search(summary_text)
    if not machlib_match:
        raise ValueError("MACHLIB line not found in builder_v2 summary output")
    return {
        "leanTheoremCount": int(lean_match.group("theorems")),
        "leanSorryCount": int(lean_match.group("sorries")),
        "machlibCoreSorryCount": int(machlib_match.group("core")),
        "machlibDiscoveredSorryCount": int(machlib_match.group("discovered")),
    }


def run_builder_summary() -> str:
    proc = subprocess.run(
        ["python", "tools/graph/builder_v2.py", "summary"],
        cwd=MONOGATE_RESEARCH,
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout


def assert_standing_rule_matches_welcome(welcome_md_path: Path | None = None) -> None:
    path = welcome_md_path or (MONOGATE_RESEARCH / "WELCOME.md")
    text = path.read_text(encoding="utf-8")
    # WELCOME.md wraps the rule onto multiple lines. Flatten before comparison.
    flat = " ".join(text.split())
    rule_flat = " ".join(STANDING_CLAIM_RULE.split())
    if rule_flat not in flat:
        raise ValueError(
            "standing claim rule drift: STANDING_CLAIM_RULE constant no longer "
            "matches WELCOME.md verbatim text"
        )


def build_ledger(
    *,
    graph_json_path: Path | None = None,
    eh_a7_path: Path | None = None,
    welcome_md_path: Path | None = None,
    lean_status_text: str | None = None,
) -> dict[str, Any]:
    graph = load_graph_payload(graph_json_path)
    eh_a7_payload = load_eh_a7_result(eh_a7_path)
    assert_standing_rule_matches_welcome(welcome_md_path)
    summary_text = lean_status_text if lean_status_text is not None else run_builder_summary()
    lean_status = parse_lean_status_text(summary_text)
    return {
        "heldLanes": held_lanes_from_eh_a7(eh_a7_payload),
        "retractedClaims": extract_claims_by_status(graph, "retracted"),
        "negativeResults": extract_claims_by_status(graph, "negative_result"),
        "standingClaimRule": STANDING_CLAIM_RULE,
        "leanStatus": lean_status,
    }


def build_payload(
    *,
    graph_json_path: Path | None = None,
    eh_a7_path: Path | None = None,
    welcome_md_path: Path | None = None,
    lean_status_text: str | None = None,
) -> dict[str, Any]:
    ledger = build_ledger(
        graph_json_path=graph_json_path,
        eh_a7_path=eh_a7_path,
        welcome_md_path=welcome_md_path,
        lean_status_text=lean_status_text,
    )
    summary = {
        "ledgerHeldLaneCount": len(ledger["heldLanes"]),
        "ledgerRetractedClaimCount": len(ledger["retractedClaims"]),
        "ledgerNegativeResultCount": len(ledger["negativeResults"]),
        "ledgerStandingClaimRuleLength": len(ledger["standingClaimRule"]),
        "leanTheoremCount": ledger["leanStatus"]["leanTheoremCount"],
        "leanSorryCount": ledger["leanStatus"]["leanSorryCount"],
        "machlibCoreSorryCount": ledger["leanStatus"]["machlibCoreSorryCount"],
        "machlibDiscoveredSorryCount": ledger["leanStatus"]["machlibDiscoveredSorryCount"],
        "ledgerByteDerivedFromCanonicalSources": True,
        "noHandWrittenLedgerFields": True,
        "singleCanonicalJsonOutput": True,
        "pageRendered": False,
        "pagePublished": False,
        "htmlRendered": False,
        "liveDeployExecuted": False,
        "driftGuardImplemented": False,
        "publicSurfaceUpdated": False,
        "trainingCostEstimatorReopened": False,
        "productRoadmapReopened": False,
        "laptopOwnedRepoTouched": False,
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id=ARTIFACT_ID,
        artifact_type="canonical_brake_side_ledger_generator",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={"ledger": ledger},
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    ledger = payload["ledger"]
    for key in ("heldLanes", "retractedClaims", "negativeResults", "standingClaimRule", "leanStatus"):
        if key not in ledger:
            raise ValueError(f"ledger missing field: {key}")
    if not ledger["heldLanes"]:
        raise ValueError("expected at least one held lane")
    if not ledger["retractedClaims"]:
        raise ValueError("expected at least one retracted claim")
    if not ledger["negativeResults"]:
        raise ValueError("expected at least one negative result")
    if ledger["standingClaimRule"] != STANDING_CLAIM_RULE:
        raise ValueError("standing claim rule drift")
    for row in ledger["heldLanes"]:
        for field in ("laneId", "holdingArtifactId", "oneLineReason"):
            if not row.get(field):
                raise ValueError(f"held-lane row missing {field}")
    for row in ledger["retractedClaims"] + ledger["negativeResults"]:
        for field in ("claimId", "source", "oneLineText"):
            if not row.get(field):
                raise ValueError(f"claim row missing {field}")
    summary = payload["summary"]
    if summary["ledgerHeldLaneCount"] != len(ledger["heldLanes"]):
        raise ValueError("held-lane count drift")
    if summary["ledgerRetractedClaimCount"] != len(ledger["retractedClaims"]):
        raise ValueError("retracted-claim count drift")
    if summary["ledgerNegativeResultCount"] != len(ledger["negativeResults"]):
        raise ValueError("negative-result count drift")
    for key in [
        "pageRendered",
        "pagePublished",
        "htmlRendered",
        "liveDeployExecuted",
        "driftGuardImplemented",
        "publicSurfaceUpdated",
        "trainingCostEstimatorReopened",
        "productRoadmapReopened",
        "laptopOwnedRepoTouched",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
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
        semantic_strength="canonical_brake_side_ledger_byte_derived_no_publication_or_completeness_claim",
        source=(
            f"python/results/pub_r0_brake_side_ledger_generator/"
            f"pub_r0_brake_side_ledger_generator_{STAMP}.json"
        ),
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="pub_r0_brake_side_ledger_generator_feed",
        date=DATE,
        status=payload["status"],
        next_action=(
            "The PUB-R0 canonical JSON ledger is byte-derived and ready for any deterministic "
            "render. PUB-R1 may now begin its build (page render + two-stage drift guard) under "
            "ordinary procedure, with a separate human-authored deploy authorization artifact "
            "required before any live public deploy."
        ),
        claim_flags=payload["claimFlags"],
        fields={
            "ledgerHeldLaneCount": payload["summary"]["ledgerHeldLaneCount"],
            "ledgerRetractedClaimCount": payload["summary"]["ledgerRetractedClaimCount"],
            "ledgerNegativeResultCount": payload["summary"]["ledgerNegativeResultCount"],
            "leanTheoremCount": payload["summary"]["leanTheoremCount"],
            "leanSorryCount": payload["summary"]["leanSorryCount"],
            "machlibCoreSorryCount": payload["summary"]["machlibCoreSorryCount"],
            "machlibDiscoveredSorryCount": payload["summary"]["machlibDiscoveredSorryCount"],
            "pagePublished": payload["summary"]["pagePublished"],
            "liveDeployExecuted": payload["summary"]["liveDeployExecuted"],
            "publicSurfaceUpdated": payload["summary"]["publicSurfaceUpdated"],
            "laptopOwnedRepoTouched": payload["summary"]["laptopOwnedRepoTouched"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    ledger = payload["ledger"]
    return render_markdown_report(
        title="PUB-R0 Canonical Brake-Side Ledger Generator",
        status=payload["status"],
        summary_rows=[
            ("held lanes", payload["summary"]["ledgerHeldLaneCount"]),
            ("retracted claims", payload["summary"]["ledgerRetractedClaimCount"]),
            ("negative results", payload["summary"]["ledgerNegativeResultCount"]),
            ("Lean theorems", payload["summary"]["leanTheoremCount"]),
            ("Lean sorries", payload["summary"]["leanSorryCount"]),
            ("MachLib core sorries", payload["summary"]["machlibCoreSorryCount"]),
            (
                "MachLib discovered sorries",
                payload["summary"]["machlibDiscoveredSorryCount"],
            ),
            ("page rendered", payload["summary"]["pageRendered"]),
            ("page published", payload["summary"]["pagePublished"]),
            ("public surface updated", payload["summary"]["publicSurfaceUpdated"]),
        ],
        sections=[
            (
                "Held Lanes",
                [
                    f"- `{row['laneId']}`: held by `{row['holdingArtifactId']}`; {row['oneLineReason']}"
                    for row in ledger["heldLanes"]
                ],
            ),
            (
                "Retracted Claims",
                [
                    f"- `{row['claimId']}` @ `{row['source']}:{row['line']}`: {row['oneLineText']}"
                    for row in ledger["retractedClaims"]
                ],
            ),
            (
                "Negative Results",
                [
                    f"- `{row['claimId']}` @ `{row['source']}:{row['line']}`: {row['oneLineText']}"
                    for row in ledger["negativeResults"]
                ],
            ),
            (
                "Standing Claim Rule (verbatim)",
                [f"> {STANDING_CLAIM_RULE}"],
            ),
            (
                "Lean Status (from builder_v2.py summary)",
                [
                    f"- Lean theorems: {ledger['leanStatus']['leanTheoremCount']}",
                    f"- Lean sorries: {ledger['leanStatus']['leanSorryCount']}",
                    f"- MachLib core sorries: {ledger['leanStatus']['machlibCoreSorryCount']}",
                    f"- MachLib discovered sorries: {ledger['leanStatus']['machlibDiscoveredSorryCount']}",
                ],
            ),
            (
                "Guardrails",
                [
                    "- canonical JSON only; no HTML render, no deploy, no public surface",
                    "- all ledger fields byte-derived from canonical sources",
                    "- ledger completeness is not claimed; source drift surfaces as ledger drift",
                    "- no laptop-owned repo touch",
                ],
            ),
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(
    out_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
    *,
    graph_json_path: Path | None = None,
    eh_a7_path: Path | None = None,
    welcome_md_path: Path | None = None,
    lean_status_text: str | None = None,
) -> dict[str, Any]:
    payload = build_payload(
        graph_json_path=graph_json_path,
        eh_a7_path=eh_a7_path,
        welcome_md_path=welcome_md_path,
        lean_status_text=lean_status_text,
    )
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"pub_r0_brake_side_ledger_generator_{STAMP}.json"
    report_path = report_dir / f"pub_r0_brake_side_ledger_generator_{STAMP}.md"
    evidence_path = evidence_dir / "pub_r0_brake_side_ledger_generator.json"
    feed_path = command_feed_dir / f"pub_r0_brake_side_ledger_generator_feed_{STAMP}.json"
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
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "python/results/pub_r0_brake_side_ledger_generator",
    )
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument(
        "--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets"
    )
    parser.add_argument(
        "--command-feed-dir", type=Path, default=ROOT / "command_center_feeds"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    validate_payload(payload)
    if args.build:
        build_outputs(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    print("PUB_R0_BRAKE_SIDE_LEDGER_GENERATOR_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
