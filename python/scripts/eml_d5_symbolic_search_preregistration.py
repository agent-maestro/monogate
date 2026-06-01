#!/usr/bin/env python3
"""EML-D5 symbolic-search preregistration.

Locks the next A6.1-style symbolic-search plan before running another
psi/frontier search experiment.
"""

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
from scripts import eml_d3_discovery_holdout_search_trials as d3  # noqa: E402
from scripts import eml_d4_discovery_failure_atlas as d4  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_symbolic_search_preregistration.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D5_SYMBOLIC_SEARCH_PREREGISTRATION_PASS"

CLAIM_FLAGS = {
    "experiment_run_performed": False,
    "candidate_test_performed": False,
    "candidate_proved": False,
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
    "EML-D5 preregisters a future symbolic-search experiment; it does not run the experiment.",
    "EML-D5 does not prove EML advantage, theorem discovery, RH, zeta-zero discovery, compiler correctness, runtime performance, formal equivalence, or public Atlas promotion.",
    "EML-D5 success criteria are private research gates, not public claims.",
    "Null results are explicitly allowed and must be recorded without reinterpretation.",
]


def criterion(
    criterion_id: str,
    description: str,
    threshold: str,
    required: bool,
    failure_action: str,
) -> dict[str, Any]:
    return {
        "criterionId": criterion_id,
        "description": description,
        "threshold": threshold,
        "requiredForPositiveInterpretation": required,
        "failureAction": failure_action,
    }


def negative_control(control_id: str, family: str, expected_result: str, blocks: list[str]) -> dict[str, Any]:
    return {
        "controlId": control_id,
        "family": family,
        "expectedResult": expected_result,
        "blocksIfFails": blocks,
    }


def experiment_plan() -> dict[str, Any]:
    return {
        "planId": "eml_d5_a6_1_symbolic_search_preregistration_v0",
        "runLabel": "A6.1 preregistered private symbolic-search refinement",
        "runPerformed": False,
        "targetCandidates": [
            "psi_residual_two_zero_holdout_v1",
            "damped_oscillator_eml_phase_v0",
        ],
        "primaryTarget": {
            "datasetId": "psi_residual",
            "fixture": "Chebyshev psi(x)-x over fixed train/holdout splits",
            "candidateSignalFromD3": "ambiguous_symbolic_search_retained",
            "interpretationBeforeRun": "ambiguous_requires_preregistered_a6_1",
        },
        "secondaryTarget": {
            "datasetId": "damped_oscillator",
            "fixture": "synthetic damped oscillator parameter-recovery holdout",
            "candidateSignalFromD3": "parameter_recovery_signal_supported",
            "interpretationBeforeRun": "search_target_not_runtime_win",
        },
        "grammars": [
            {
                "grammarId": "eml_native_guarded_v1",
                "operators": ["+", "-", "*", "/", "protected_eml", "protected_expm1", "protected_logaddexp"],
                "complexityBudget": 22,
                "notes": "Includes EML-native coordinates plus protected operators required by D4 controls.",
            },
            {
                "grammarId": "standard_exp_log_trig_v1",
                "operators": ["+", "-", "*", "/", "sin", "cos", "exp", "log_abs", "sqrt_abs", "logaddexp", "expm1"],
                "complexityBudget": 22,
                "notes": "Standard protected baseline with the same complexity budget.",
            },
            {
                "grammarId": "wrong_exponent_eml_control_v1",
                "operators": ["+", "-", "*", "/", "protected_eml"],
                "complexityBudget": 18,
                "notes": "Negative-control grammar for zeta-like localization traps.",
            },
        ],
        "splitPolicy": {
            "seed": 20260601,
            "trainFraction": 0.75,
            "holdoutFraction": 0.25,
            "repeatCount": 3,
            "splitIds": ["seed_20260601_a", "seed_20260601_b", "seed_20260601_c"],
        },
        "complexityPolicy": {
            "primaryMetric": "first_acceptable_holdout_loss_at_complexity",
            "maxComplexity": 22,
            "complexityPenalty": 0.05,
            "mustReportParetoFrontier": True,
            "mustReportBestEquationText": True,
        },
        "protectedOperatorPolicy": {
            "requiredByFailureAtlas": ["protected_expm1", "protected_logaddexp", "block_unstable_deep_tree"],
            "rawRuntimePreferenceAllowed": False,
            "mustCiteD4Controls": True,
        },
        "blockedInterpretationsBeforeRun": [
            "EML advantage proved",
            "theorem discovery",
            "RH proof",
            "zeta-zero discovery",
            "runtime performance",
            "compiler correctness",
            "formal equivalence",
            "public Atlas promotion",
        ],
    }


def success_criteria() -> list[dict[str, Any]]:
    return [
        criterion(
            "holdout_mse_improvement_replicated",
            "EML grammar must beat the standard grammar on target holdout MSE across all preregistered splits.",
            "eml_holdout_mse <= 0.95 * standard_holdout_mse on every split",
            True,
            "label result as null_or_standard_control_retained",
        ),
        criterion(
            "complexity_not_higher",
            "EML grammar must not buy holdout fit by using a larger expression.",
            "eml_best_complexity <= standard_best_complexity",
            True,
            "label result as fit_without_complexity_advantage",
        ),
        criterion(
            "wrong_exponent_control_not_better",
            "Wrong-exponent EML-like controls must not beat the selected EML grammar on localization or holdout score.",
            "wrong_exponent_score > eml_score on target fixture",
            True,
            "label result as ambiguous_control_failure",
        ),
        criterion(
            "negative_controls_do_not_promote_eml",
            "Shuffled and Gaussian-bump controls must not produce an apparent EML advantage.",
            "standard_or_control_label wins on non-EML controls",
            True,
            "block positive interpretation",
        ),
        criterion(
            "protected_runtime_controls_respected",
            "Generated expressions must not prefer raw exp-minus-one or naive logsumexp when D4 says protected standard runtime wins.",
            "no accepted expression violates D4 protected operator policy",
            True,
            "reject expression from positive interpretation",
        ),
        criterion(
            "localization_and_mse_both_reported",
            "Psi residual interpretation must report both zeta-like localization and holdout MSE, because D3 showed they can disagree.",
            "both metrics present in every target run packet",
            True,
            "mark run incomplete",
        ),
    ]


def negative_controls() -> list[dict[str, Any]]:
    return [
        negative_control(
            "wrong_exponent_two_zero_v0",
            "psi_residual_control",
            "wrong-exponent controls must not outperform the preregistered EML target grammar",
            ["structure_recovery_claim", "zeta_localization_interpretation"],
        ),
        negative_control(
            "shuffled_residual_control_v1",
            "data_randomization_control",
            "no grammar should receive positive structural interpretation on shuffled residuals",
            ["symbolic_structure_claim", "eml_advantage_claim"],
        ),
        negative_control(
            "gaussian_bumps_control_v1",
            "non_eml_structure_control",
            "standard/protected grammar should remain competitive or win",
            ["general_eml_superiority_claim"],
        ),
        negative_control(
            "ordinary_polynomial_failure_v0",
            "failure_atlas_control",
            "standard Horner representation remains the control",
            ["surface_compression_claim", "runtime_advantage_claim"],
        ),
        negative_control(
            "expm1_logaddexp_runtime_controls_v1",
            "protected_runtime_control",
            "protected expm1/logaddexp policies from D4 must not be violated",
            ["raw_eml_runtime_preference", "compiler_lowering_claim"],
        ),
    ]


def null_result_policy() -> dict[str, Any]:
    return {
        "nullResultAccepted": True,
        "nullLabels": [
            "standard_control_retained",
            "ambiguous_control_failure",
            "fit_without_complexity_advantage",
            "no_replicated_holdout_gain",
        ],
        "requiredNullReporting": [
            "all split metrics",
            "all negative-control outcomes",
            "best equations for both grammars",
            "complexity frontier",
            "claim flags remaining false",
        ],
        "forbiddenPostHocMoves": [
            "changing success thresholds after seeing results",
            "dropping failed splits",
            "ignoring wrong-exponent controls",
            "turning localization-only wins into theorem or zeta claims",
            "turning local runtime stability into performance claims",
        ],
    }


def build_payload() -> dict[str, Any]:
    queue = d1.build_payload()
    holdout = d3.build_payload()
    failure = d4.build_payload()
    plan = experiment_plan()
    criteria = success_criteria()
    controls = negative_controls()
    summary = {
        "preregistrationRecorded": True,
        "experimentRunPerformed": False,
        "targetCandidateCount": len(plan["targetCandidates"]),
        "grammarCount": len(plan["grammars"]),
        "successCriteriaCount": len(criteria),
        "requiredSuccessCriteriaCount": sum(1 for item in criteria if item["requiredForPositiveInterpretation"]),
        "negativeControlCount": len(controls),
        "nullResultAccepted": True,
        "d3AmbiguousSignalCarriedForward": "psi_residual_two_zero_holdout_v1" in plan["targetCandidates"],
        "d4FailureAtlasRequired": True,
        "candidateProved": False,
        "emlAdvantageProved": False,
        "publicReady": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "planType": "eml_symbolic_search_preregistration_v0",
        "artifactId": "eml-d5-symbolic-search-preregistration",
        "status": STATUS,
        "decision": "symbolic_search_preregistered_run_not_performed",
        "date": DATE,
        "sourceQueue": queue["artifactId"],
        "sourceHoldoutTrial": holdout["artifactId"],
        "sourceFailureAtlas": failure["artifactId"],
        "experimentPlan": plan,
        "successCriteria": criteria,
        "negativeControls": controls,
        "nullResultPolicy": null_result_policy(),
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if summary["experimentRunPerformed"] is not False:
        raise ValueError("D5 must not run the experiment")
    if summary["successCriteriaCount"] < 6:
        raise ValueError("expected at least six success criteria")
    if summary["negativeControlCount"] < 5:
        raise ValueError("expected at least five negative controls")
    if summary["requiredSuccessCriteriaCount"] != summary["successCriteriaCount"]:
        raise ValueError("all D5 success criteria must be required")
    for key in ["candidateProved", "emlAdvantageProved", "publicReady"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if payload["nullResultPolicy"]["nullResultAccepted"] is not True:
        raise ValueError("null results must be accepted")
    if payload["experimentPlan"]["protectedOperatorPolicy"]["rawRuntimePreferenceAllowed"] is not False:
        raise ValueError("raw runtime preference must remain blocked")
    if not all(value is False for value in payload["claimFlags"].values()):
        raise ValueError("claim flag drift")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("claim flags must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_symbolic_search_preregistration",
        "validationStatus": "pass",
        "semanticStrength": "preregistered_plan_no_experiment_run",
        "source": f"python/results/eml_d5_symbolic_search_preregistration/eml_d5_symbolic_search_preregistration_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d5_symbolic_search_preregistration_feed",
        "date": DATE,
        "status": payload["status"],
        "nextAction": "Only run D6 after consuming this preregistration plan and preserving its success criteria and controls.",
        "targetCandidates": payload["experimentPlan"]["targetCandidates"],
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D5 Symbolic Search Preregistration",
        "",
        f"Status: `{payload['status']}`",
        "",
        "EML-D5 locks the next symbolic-search plan before any A6.1-style run.",
        "",
        "## Targets",
        "",
    ]
    lines.extend(f"- `{item}`" for item in payload["experimentPlan"]["targetCandidates"])
    lines.extend(["", "## Required Criteria", ""])
    lines.extend(
        f"- `{item['criterionId']}`: {item['threshold']}"
        for item in payload["successCriteria"]
    )
    lines.extend(["", "## Negative Controls", ""])
    lines.extend(
        f"- `{item['controlId']}`: {item['expectedResult']}"
        for item in payload["negativeControls"]
    )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- experiment run performed: `{payload['summary']['experimentRunPerformed']}`",
            f"- success criteria: {payload['summary']['successCriteriaCount']}",
            f"- negative controls: {payload['summary']['negativeControlCount']}",
            f"- null result accepted: `{payload['summary']['nullResultAccepted']}`",
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
    result_path = out_dir / f"eml_d5_symbolic_search_preregistration_{STAMP}.json"
    report_path = report_dir / f"eml_d5_symbolic_search_preregistration_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d5_symbolic_search_preregistration.json"
    feed_path = command_feed_dir / f"eml_d5_symbolic_search_preregistration_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d5_symbolic_search_preregistration")
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
    print("EML_D5_SYMBOLIC_SEARCH_PREREGISTRATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
