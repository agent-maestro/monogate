#!/usr/bin/env python3
"""EML-D7 symbolic-search interpretation gate."""

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

from scripts import eml_d5_symbolic_search_preregistration as d5  # noqa: E402
from scripts import eml_d6_preregistered_symbolic_search_run as d6  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_symbolic_search_interpretation_gate.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D7_SYMBOLIC_SEARCH_INTERPRETATION_GATE_PASS"

CLAIM_FLAGS = {
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
    "EML-D7 interprets D6 only against the D5 preregistered criteria.",
    "EML-D7 does not prove EML advantage, theorem discovery, RH, zeta-zero discovery, compiler correctness, runtime performance, formal equivalence, public Atlas promotion, or public readiness.",
    "A null or ambiguous label is an allowed research result and must not be reworded as a win.",
]


def packets(run: dict[str, Any], dataset_id: str, grammar_id: str) -> list[dict[str, Any]]:
    return [
        item
        for item in run["runPackets"]
        if item["datasetId"] == dataset_id and item["grammarId"] == grammar_id
    ]


def by_split(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["splitId"]: item for item in rows}


def criterion_result(criterion_id: str, passed: bool, observed: dict[str, Any], label_if_failed: str) -> dict[str, Any]:
    return {
        "criterionId": criterion_id,
        "passed": passed,
        "observed": observed,
        "labelIfFailed": label_if_failed,
    }


def holdout_mse_improvement(run: dict[str, Any]) -> dict[str, Any]:
    eml = by_split(packets(run, "psi_residual", "eml_native_guarded_v1"))
    standard = by_split(packets(run, "psi_residual", "standard_exp_log_trig_v1"))
    rows = []
    for split_id in sorted(eml):
        eml_mse = eml[split_id]["metrics"]["holdoutMse"]
        standard_mse = standard[split_id]["metrics"]["holdoutMse"]
        rows.append(
            {
                "splitId": split_id,
                "emlHoldoutMse": eml_mse,
                "standardHoldoutMse": standard_mse,
                "requiredMaxMse": 0.95 * standard_mse,
                "passed": eml_mse <= 0.95 * standard_mse,
            }
        )
    return criterion_result(
        "holdout_mse_improvement_replicated",
        all(row["passed"] for row in rows),
        {"rows": rows},
        "no_replicated_holdout_gain",
    )


def complexity_not_higher(run: dict[str, Any]) -> dict[str, Any]:
    eml_complexities = sorted({item["bestComplexity"] for item in packets(run, "psi_residual", "eml_native_guarded_v1")})
    standard_complexities = sorted({item["bestComplexity"] for item in packets(run, "psi_residual", "standard_exp_log_trig_v1")})
    eml_complexity = max(eml_complexities)
    standard_complexity = min(standard_complexities)
    return criterion_result(
        "complexity_not_higher",
        eml_complexity <= standard_complexity,
        {"emlComplexity": eml_complexity, "standardComplexity": standard_complexity},
        "fit_without_complexity_advantage",
    )


def wrong_exponent_control_not_better(run: dict[str, Any]) -> dict[str, Any]:
    eml = by_split(packets(run, "psi_residual", "eml_native_guarded_v1"))
    wrong = by_split(packets(run, "psi_residual", "wrong_exponent_eml_control_v1"))
    rows = []
    for split_id in sorted(eml):
        eml_score = eml[split_id]["metrics"]["holdoutMse"]
        wrong_score = wrong[split_id]["metrics"]["holdoutMse"]
        rows.append(
            {
                "splitId": split_id,
                "emlHoldoutMse": eml_score,
                "wrongExponentHoldoutMse": wrong_score,
                "passed": wrong_score > eml_score,
            }
        )
    return criterion_result(
        "wrong_exponent_control_not_better",
        all(row["passed"] for row in rows),
        {"rows": rows},
        "ambiguous_control_failure",
    )


def negative_controls_do_not_promote_eml(run: dict[str, Any]) -> dict[str, Any]:
    pending = [
        item["controlId"]
        for item in run["negativeControlOutcomes"]
        if item["status"] == "pending_d7_or_future_run"
    ]
    return criterion_result(
        "negative_controls_do_not_promote_eml",
        not pending,
        {"pendingControls": pending},
        "ambiguous_control_failure",
    )


def protected_runtime_controls_respected(run: dict[str, Any]) -> dict[str, Any]:
    satisfied = {
        item["controlId"]
        for item in run["negativeControlOutcomes"]
        if item["status"] == "satisfied_by_d4_failure_atlas"
    }
    required = {"ordinary_polynomial_failure_v0", "expm1_logaddexp_runtime_controls_v1"}
    return criterion_result(
        "protected_runtime_controls_respected",
        required.issubset(satisfied),
        {"satisfiedControls": sorted(satisfied), "requiredControls": sorted(required)},
        "ambiguous_control_failure",
    )


def localization_and_mse_both_reported(run: dict[str, Any]) -> dict[str, Any]:
    psi = [item for item in run["runPackets"] if item["datasetId"] == "psi_residual"]
    missing = [
        item["splitId"] + ":" + item["grammarId"]
        for item in psi
        if "holdoutMse" not in item["metrics"] or "errorFromFirstKnownZero" not in item["metrics"]
    ]
    return criterion_result(
        "localization_and_mse_both_reported",
        not missing,
        {"missingMetricPackets": missing, "checkedPacketCount": len(psi)},
        "incomplete_run",
    )


def evaluate_criteria(run: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        holdout_mse_improvement(run),
        complexity_not_higher(run),
        wrong_exponent_control_not_better(run),
        negative_controls_do_not_promote_eml(run),
        protected_runtime_controls_respected(run),
        localization_and_mse_both_reported(run),
    ]


def choose_label(results: list[dict[str, Any]]) -> str:
    failed = {item["criterionId"] for item in results if not item["passed"]}
    if not failed:
        return "bounded_private_candidate_signal"
    if "holdout_mse_improvement_replicated" in failed:
        return "no_replicated_holdout_gain"
    if "negative_controls_do_not_promote_eml" in failed or "wrong_exponent_control_not_better" in failed:
        return "ambiguous_control_failure"
    if "complexity_not_higher" in failed:
        return "fit_without_complexity_advantage"
    return "standard_control_retained"


def build_payload() -> dict[str, Any]:
    plan = d5.build_payload()
    run = d6.build_payload()
    d5.validate_payload(plan)
    d6.validate_payload(run)
    results = evaluate_criteria(run)
    failed = [item for item in results if not item["passed"]]
    label = choose_label(results)
    summary = {
        "criterionCount": len(results),
        "passedCriterionCount": len(results) - len(failed),
        "failedCriterionCount": len(failed),
        "interpretationLabel": label,
        "positiveInterpretationAllowed": label == "bounded_private_candidate_signal",
        "thresholdsChanged": False,
        "d5CriteriaPreserved": True,
        "d6RunInterpreted": True,
        "candidateProved": False,
        "emlAdvantageProved": False,
        "rhProofClaim": False,
        "zetaZeroDiscoveryClaim": False,
        "runtimePerformanceClaim": False,
        "publicReady": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }
    interpretation = {
        "label": label,
        "allowedSurface": "private_research_record",
        "failedCriterionIds": [item["criterionId"] for item in failed],
        "resultSummary": (
            "D6 is not a positive EML advantage result under the D5 gate: "
            "replicated holdout improvement fails, EML complexity is higher than the standard baseline, "
            "and some negative controls remain pending."
        ),
        "nextAction": "Route to D8 branch decision: either park psi residual as ambiguous, broaden controls, or choose a different frontier family.",
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "gateType": "eml_symbolic_search_interpretation_gate_v0",
        "artifactId": "eml-d7-symbolic-search-interpretation-gate",
        "status": STATUS,
        "decision": "d6_interpreted_against_d5_no_positive_advantage_claim",
        "date": DATE,
        "sourcePreregistration": plan["artifactId"],
        "sourceRun": run["artifactId"],
        "criterionResults": results,
        "interpretation": interpretation,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if summary["criterionCount"] != 6:
        raise ValueError("expected six D5 criteria")
    if summary["failedCriterionCount"] < 1:
        raise ValueError("D7 expected at least one failed criterion for current D6")
    if summary["interpretationLabel"] != "no_replicated_holdout_gain":
        raise ValueError("unexpected D7 interpretation label")
    if summary["positiveInterpretationAllowed"] is not False:
        raise ValueError("positive interpretation must remain blocked")
    if summary["thresholdsChanged"] is not False:
        raise ValueError("D7 must not change thresholds")
    for key in [
        "candidateProved",
        "emlAdvantageProved",
        "rhProofClaim",
        "zetaZeroDiscoveryClaim",
        "runtimePerformanceClaim",
        "publicReady",
    ]:
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
        "artifactType": "eml_symbolic_search_interpretation_gate",
        "validationStatus": "pass",
        "semanticStrength": "preregistered_interpretation_gate_no_positive_claim",
        "source": f"python/results/eml_d7_symbolic_search_interpretation_gate/eml_d7_symbolic_search_interpretation_gate_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d7_symbolic_search_interpretation_gate_feed",
        "date": DATE,
        "status": payload["status"],
        "interpretationLabel": payload["summary"]["interpretationLabel"],
        "nextAction": payload["interpretation"]["nextAction"],
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D7 Symbolic Search Interpretation Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Interpretation label: `{payload['summary']['interpretationLabel']}`",
        "",
        "D7 evaluates D6 against the D5 preregistered criteria without changing thresholds.",
        "",
        "## Criteria",
        "",
        "| Criterion | Passed | Label if failed |",
        "|---|---|---|",
    ]
    for item in payload["criterionResults"]:
        lines.append(f"| `{item['criterionId']}` | `{item['passed']}` | `{item['labelIfFailed']}` |")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- passed criteria: {payload['summary']['passedCriterionCount']}",
            f"- failed criteria: {payload['summary']['failedCriterionCount']}",
            f"- positive interpretation allowed: `{payload['summary']['positiveInterpretationAllowed']}`",
            f"- thresholds changed: `{payload['summary']['thresholdsChanged']}`",
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
    result_path = out_dir / f"eml_d7_symbolic_search_interpretation_gate_{STAMP}.json"
    report_path = report_dir / f"eml_d7_symbolic_search_interpretation_gate_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d7_symbolic_search_interpretation_gate.json"
    feed_path = command_feed_dir / f"eml_d7_symbolic_search_interpretation_gate_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d7_symbolic_search_interpretation_gate")
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
    print("EML_D7_SYMBOLIC_SEARCH_INTERPRETATION_GATE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
