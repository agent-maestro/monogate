#!/usr/bin/env python3
"""EML-D8 discovery branch decision."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import eml_d1_discovery_frontier_queue as d1  # noqa: E402
from scripts import eml_d7_symbolic_search_interpretation_gate as d7  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_discovery_branch_decision.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D8_DISCOVERY_BRANCH_DECISION_PASS"

CLAIM_FLAGS = {
    "implementation_started": False,
    "candidate_proved": False,
    "bounded_private_candidate_signal": False,
    "eml_advantage_proved": False,
    "general_eml_superiority_claim": False,
    "theorem_discovery_claim": False,
    "rh_proof_claim": False,
    "zeta_zero_discovery_claim": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "public_atlas_promotion": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "EML-D8 is a private research branch decision, not a proof, experiment, implementation, or public promotion.",
    "EML-D8 does not prove EML advantage, theorem discovery, RH, zeta-zero discovery, compiler correctness, runtime performance, formal equivalence, or public readiness.",
    "D7's no_replicated_holdout_gain label blocks deeper psi-residual search unless a later explicit branch decision reopens it.",
]


def branch_option(
    branch_id: str,
    branch_class: str,
    decision: str,
    score: int,
    rationale: list[str],
    next_artifact: str,
    blocked_claims: list[str],
) -> dict[str, Any]:
    return {
        "branchId": branch_id,
        "branchClass": branch_class,
        "decision": decision,
        "priorityScore": score,
        "rationale": rationale,
        "nextArtifact": next_artifact,
        "blockedClaims": blocked_claims,
        "claimFlags": dict(CLAIM_FLAGS),
    }


def build_branch_options(gate: dict[str, Any], queue: dict[str, Any]) -> list[dict[str, Any]]:
    label = gate["summary"]["interpretationLabel"]
    failed = set(gate["interpretation"]["failedCriterionIds"])
    identity_candidates = [
        item["candidateId"]
        for item in queue["frontierCandidates"]
        if item["door"] == "identity_discovery" and item["frontierStatus"] == "ready_for_d2_trial"
    ]
    return [
        branch_option(
            "park_psi_residual_search_v0",
            "symbolic_search",
            "park_as_ambiguous_until_new_hypothesis",
            42,
            [
                f"D7 label is {label}.",
                "Replicated holdout improvement failed under D5.",
                "Psi residual remains useful as a cautionary research record, not as the next active experiment.",
            ],
            "D8 records parking decision; no new psi search run.",
            ["EML advantage", "RH proof", "zeta-zero discovery", "public Atlas promotion"],
        ),
        branch_option(
            "machlib_identity_witness_lane_v0",
            "proof_shape_identity",
            "selected_next",
            64,
            [
                "D1 still has ready identity candidates with bounded proof/teaching value.",
                "D7 blocks positive search interpretation, so move to smaller proof-shaped wins.",
                f"Ready identity candidates: {', '.join(identity_candidates[:4])}.",
            ],
            "EML-D9 MachLib identity witness selector",
            ["theorem discovery", "compiler correctness", "formal equivalence", "public Atlas promotion"],
        ),
        branch_option(
            "fresh_non_psi_holdout_family_v0",
            "holdout_search",
            "candidate_later",
            46,
            [
                "Damped oscillator separated the wrong-exponent control but matched standard protected template evidence.",
                "A fresh non-psi family could be useful after a proof-shaped reset.",
                "Should not run before a new preregistration packet.",
            ],
            "Future D-series holdout-family queue",
            ["general EML superiority", "runtime performance", "public readiness"],
        ),
        branch_option(
            "broaden_negative_controls_v0",
            "failure_atlas",
            "candidate_later",
            50,
            [
                "D7 failed negative_controls_do_not_promote_eml because shuffled and Gaussian controls remain pending.",
                "Broader controls are useful before future symbolic-search claims.",
                "This is supporting discipline, not the main next branch.",
            ],
            "Future failure/control expansion packet",
            ["EML advantage", "theorem discovery", "public Atlas promotion"],
        ),
    ]


def build_payload() -> dict[str, Any]:
    gate = d7.build_payload()
    queue = d1.build_payload()
    d7.validate_payload(gate)
    options = build_branch_options(gate, queue)
    selected = next(item for item in options if item["decision"] == "selected_next")
    summary = {
        "sourceInterpretationLabel": gate["summary"]["interpretationLabel"],
        "branchOptionCount": len(options),
        "selectedBranchId": selected["branchId"],
        "selectedNextArtifact": selected["nextArtifact"],
        "psiSearchParked": True,
        "deeperPsiSearchAllowed": False,
        "implementationStarted": False,
        "candidateProved": False,
        "emlAdvantageProved": False,
        "publicReady": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values())
        and all(all(value is False for value in item["claimFlags"].values()) for item in options),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "decisionType": "eml_discovery_branch_decision_v0",
        "artifactId": "eml-d8-discovery-branch-decision",
        "status": STATUS,
        "decision": "select_machlib_identity_witness_lane_after_no_replicated_holdout_gain",
        "date": DATE,
        "sourceInterpretationGate": gate["artifactId"],
        "branchOptions": options,
        "selectedBranch": selected,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if summary["sourceInterpretationLabel"] != "no_replicated_holdout_gain":
        raise ValueError("D8 expected D7 no_replicated_holdout_gain label")
    if summary["branchOptionCount"] != 4:
        raise ValueError("expected four branch options")
    if summary["selectedBranchId"] != "machlib_identity_witness_lane_v0":
        raise ValueError("unexpected selected branch")
    if summary["psiSearchParked"] is not True:
        raise ValueError("psi search must be parked")
    if summary["deeperPsiSearchAllowed"] is not False:
        raise ValueError("deeper psi search must remain blocked")
    for key in ["implementationStarted", "candidateProved", "emlAdvantageProved", "publicReady"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if not all(value is False for value in payload["claimFlags"].values()):
        raise ValueError("claim flag drift")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_discovery_branch_decision",
        "validationStatus": "pass",
        "semanticStrength": "private_branch_decision_no_implementation",
        "source": f"python/results/eml_d8_discovery_branch_decision/eml_d8_discovery_branch_decision_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d8_discovery_branch_decision_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedBranchId": payload["summary"]["selectedBranchId"],
        "nextAction": "Build EML-D9 MachLib identity witness selector before any further psi-residual symbolic search.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D8 Discovery Branch Decision",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Selected branch: `{payload['summary']['selectedBranchId']}`",
        "",
        "D8 chooses the next frontier branch after D7's no-replicated-holdout-gain label.",
        "",
        "| Branch | Decision | Score | Next artifact |",
        "|---|---|---|---|",
    ]
    for item in payload["branchOptions"]:
        lines.append(f"| `{item['branchId']}` | `{item['decision']}` | {item['priorityScore']} | {item['nextArtifact']} |")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- psi search parked: `{payload['summary']['psiSearchParked']}`",
            f"- deeper psi search allowed: `{payload['summary']['deeperPsiSearchAllowed']}`",
            f"- implementation started: `{payload['summary']['implementationStarted']}`",
            f"- EML advantage proved: `{payload['summary']['emlAdvantageProved']}`",
            "",
            "## Non-Claims",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["nonClaims"])
    return "\n".join(lines) + "\n"


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"eml_d8_discovery_branch_decision_{STAMP}.json"
    report_path = report_dir / f"eml_d8_discovery_branch_decision_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d8_discovery_branch_decision.json"
    feed_path = command_feed_dir / f"eml_d8_discovery_branch_decision_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d8_discovery_branch_decision")
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
    print("EML_D8_DISCOVERY_BRANCH_DECISION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
