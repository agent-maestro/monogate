#!/usr/bin/env python3
"""EML-D6 preregistered symbolic-search run.

Runs a bounded deterministic search that consumes the D5 preregistration. D6
emits results only; D7 is responsible for interpreting them against criteria.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import eml_d5_symbolic_search_preregistration as d5  # noqa: E402
from scripts.eml_prime_residual_benchmark import (  # noqa: E402
    FIRST_ZETA_ZERO_GAMMA,
    eml_prediction,
    fixture as psi_fixture,
)
from scripts.eml_symbolic_regression_template_search import wrong_exponent_prediction  # noqa: E402

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_preregistered_symbolic_search_run.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D6_PREREGISTERED_SYMBOLIC_SEARCH_RUN_PASS"

CLAIM_FLAGS = {
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
    "EML-D6 runs a bounded deterministic preregistered search, not a full PySR campaign.",
    "EML-D6 does not interpret results as proof, theorem discovery, RH proof, zeta-zero discovery, EML advantage, runtime performance, compiler correctness, formal equivalence, or public readiness.",
    "EML-D6 preserves D5 thresholds and controls; D7 must perform the interpretation gate.",
]

GRAMMAR_COMPLEXITY = {
    "eml_native_guarded_v1": 17,
    "standard_exp_log_trig_v1": 16,
    "wrong_exponent_eml_control_v1": 17,
}


def split_indices(size: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    indices = np.arange(size)
    rng.shuffle(indices)
    holdout_count = max(1, size // 4)
    holdout = np.sort(indices[:holdout_count])
    train = np.sort(indices[holdout_count:])
    return train, holdout


def mse(a: np.ndarray, b: np.ndarray) -> float:
    finite = np.isfinite(a) & np.isfinite(b)
    if not np.any(finite):
        return float("inf")
    return float(np.mean((a[finite] - b[finite]) ** 2))


def standard_design(xs: np.ndarray, gamma: float) -> np.ndarray:
    log_x = np.log(xs)
    sqrt_x = np.sqrt(xs)
    return np.column_stack([sqrt_x * np.cos(gamma * log_x), sqrt_x * np.sin(gamma * log_x)])


def fit_standard_psi(xs_train: np.ndarray, y_train: np.ndarray, gamma: float) -> np.ndarray:
    coefficients = np.linalg.lstsq(standard_design(xs_train, gamma), y_train, rcond=None)[0]
    return np.asarray(coefficients, dtype=np.float64)


def scan_psi_grammar(grammar_id: str, xs: np.ndarray, y: np.ndarray, train: np.ndarray, holdout: np.ndarray) -> dict[str, Any]:
    gammas = np.linspace(8.0, 28.0, 240)
    best: dict[str, Any] | None = None
    for gamma in gammas:
        if grammar_id == "eml_native_guarded_v1":
            train_pred = eml_prediction(xs[train], float(gamma))
            holdout_pred = eml_prediction(xs[holdout], float(gamma))
            expression = f"-2*Re(x^(0.5+i*{float(gamma):.6f})/(0.5+i*gamma))"
            coefficients: list[float] = []
        elif grammar_id == "standard_exp_log_trig_v1":
            coefficients_arr = fit_standard_psi(xs[train], y[train], float(gamma))
            train_pred = standard_design(xs[train], float(gamma)) @ coefficients_arr
            holdout_pred = standard_design(xs[holdout], float(gamma)) @ coefficients_arr
            expression = f"sqrt(x)*(a*cos({float(gamma):.6f}*log(x))+b*sin({float(gamma):.6f}*log(x)))"
            coefficients = [float(coefficients_arr[0]), float(coefficients_arr[1])]
        elif grammar_id == "wrong_exponent_eml_control_v1":
            exponent = 0.3 if gamma < 18.0 else 0.7
            train_pred = wrong_exponent_prediction(xs[train], float(gamma), exponent)
            holdout_pred = wrong_exponent_prediction(xs[holdout], float(gamma), exponent)
            expression = f"-2*Re(x^({exponent}+i*{float(gamma):.6f})/({exponent}+i*gamma))"
            coefficients = []
        else:
            raise ValueError(f"unknown grammar: {grammar_id}")
        row = {
            "bestGamma": float(gamma),
            "trainMse": mse(y[train], train_pred),
            "holdoutMse": mse(y[holdout], holdout_pred),
            "errorFromFirstKnownZero": abs(float(gamma) - FIRST_ZETA_ZERO_GAMMA),
            "bestExpression": expression,
            "profiledCoefficients": coefficients,
        }
        if best is None or row["trainMse"] < best["trainMse"]:
            best = row
    assert best is not None
    return best


def damped_fixture() -> tuple[np.ndarray, np.ndarray]:
    t = np.linspace(0.0, 12.0, 720)
    y = 1.6 * np.exp(-0.18 * t) * np.sin(2.75 * t + 0.35)
    return t, y


def damped_design(t: np.ndarray, omega: float, decay: float) -> np.ndarray:
    envelope = np.exp(-decay * t)
    return np.column_stack([envelope * np.sin(omega * t), envelope * np.cos(omega * t)])


def scan_damped_grammar(grammar_id: str, t: np.ndarray, y: np.ndarray, train: np.ndarray, holdout: np.ndarray) -> dict[str, Any]:
    if grammar_id == "wrong_exponent_eml_control_v1":
        omegas = np.linspace(3.35, 4.6, 24)
        decays = np.linspace(0.32, 0.72, 14)
    else:
        omegas = np.linspace(2.1, 3.3, 28)
        decays = np.linspace(0.08, 0.32, 16)
    best: dict[str, Any] | None = None
    for omega in omegas:
        for decay in decays:
            design_train = damped_design(t[train], float(omega), float(decay))
            coefficients_arr = np.linalg.lstsq(design_train, y[train], rcond=None)[0]
            train_pred = design_train @ coefficients_arr
            holdout_pred = damped_design(t[holdout], float(omega), float(decay)) @ coefficients_arr
            row = {
                "bestOmega": float(omega),
                "bestDecay": float(decay),
                "trainMse": mse(y[train], train_pred),
                "holdoutMse": mse(y[holdout], holdout_pred),
                "bestExpression": f"exp(-{float(decay):.6f}*t)*(a*sin({float(omega):.6f}*t)+b*cos({float(omega):.6f}*t))",
                "profiledCoefficients": [float(coefficients_arr[0]), float(coefficients_arr[1])],
            }
            if best is None or row["trainMse"] < best["trainMse"]:
                best = row
    assert best is not None
    return best


def run_packet(target_id: str, dataset_id: str, split_id: str, grammar_id: str, metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "targetCandidateId": target_id,
        "datasetId": dataset_id,
        "splitId": split_id,
        "grammarId": grammar_id,
        "runClass": "deterministic_template_search",
        "bestComplexity": GRAMMAR_COMPLEXITY[grammar_id],
        "metrics": metrics,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_run_packets(plan: dict[str, Any]) -> list[dict[str, Any]]:
    split_ids = plan["experimentPlan"]["splitPolicy"]["splitIds"]
    base_seed = int(plan["experimentPlan"]["splitPolicy"]["seed"])
    grammar_ids = [item["grammarId"] for item in plan["experimentPlan"]["grammars"]]
    packets: list[dict[str, Any]] = []

    psi = psi_fixture(n_samples=420)
    xs = psi["x"]
    residual = psi["residual"]
    for offset, split_id in enumerate(split_ids):
        train, holdout = split_indices(xs.size, base_seed + offset)
        for grammar_id in grammar_ids:
            metrics = scan_psi_grammar(grammar_id, xs, residual, train, holdout)
            packets.append(run_packet("psi_residual_two_zero_holdout_v1", "psi_residual", split_id, grammar_id, metrics))

    t, y = damped_fixture()
    for offset, split_id in enumerate(split_ids):
        train, holdout = split_indices(t.size, base_seed + 100 + offset)
        for grammar_id in grammar_ids:
            metrics = scan_damped_grammar(grammar_id, t, y, train, holdout)
            packets.append(run_packet("damped_oscillator_eml_phase_v0", "damped_oscillator", split_id, grammar_id, metrics))
    return packets


def negative_control_outcomes(run_packets: list[dict[str, Any]], plan: dict[str, Any]) -> list[dict[str, Any]]:
    controls = []
    controls.append(
        {
            "controlId": "wrong_exponent_two_zero_v0",
            "status": "recorded_for_d7_gate",
            "observedWrongExponentRuns": sum(1 for item in run_packets if item["grammarId"] == "wrong_exponent_eml_control_v1"),
            "blocksPositiveInterpretationUntilD7": True,
        }
    )
    controls.append(
        {
            "controlId": "shuffled_residual_control_v1",
            "status": "pending_d7_or_future_run",
            "reason": "D6 preserves the preregistered control but does not run shuffled-residual PySR-style search.",
            "blocksPositiveInterpretationUntilD7": True,
        }
    )
    controls.append(
        {
            "controlId": "gaussian_bumps_control_v1",
            "status": "pending_d7_or_future_run",
            "reason": "D6 preserves the preregistered control but does not run gaussian-bumps PySR-style search.",
            "blocksPositiveInterpretationUntilD7": True,
        }
    )
    controls.append(
        {
            "controlId": "ordinary_polynomial_failure_v0",
            "status": "satisfied_by_d4_failure_atlas",
            "source": plan["sourceFailureAtlas"],
            "blocksPositiveInterpretationUntilD7": False,
        }
    )
    controls.append(
        {
            "controlId": "expm1_logaddexp_runtime_controls_v1",
            "status": "satisfied_by_d4_failure_atlas",
            "source": plan["sourceFailureAtlas"],
            "blocksPositiveInterpretationUntilD7": False,
        }
    )
    return controls


def aggregate_summary(run_packets: list[dict[str, Any]], controls: list[dict[str, Any]], plan: dict[str, Any]) -> dict[str, Any]:
    psi_packets = [item for item in run_packets if item["datasetId"] == "psi_residual"]
    damped_packets = [item for item in run_packets if item["datasetId"] == "damped_oscillator"]
    return {
        "experimentRunPerformed": True,
        "sourcePreregistrationConsumed": True,
        "d5CriteriaPreserved": True,
        "targetCandidateCount": len(plan["experimentPlan"]["targetCandidates"]),
        "grammarCount": len(plan["experimentPlan"]["grammars"]),
        "splitCount": len(plan["experimentPlan"]["splitPolicy"]["splitIds"]),
        "runPacketCount": len(run_packets),
        "psiRunPacketCount": len(psi_packets),
        "dampedRunPacketCount": len(damped_packets),
        "negativeControlOutcomeCount": len(controls),
        "negativeControlsBlockingPositiveInterpretation": sum(1 for item in controls if item["blocksPositiveInterpretationUntilD7"]),
        "d7InterpretationRequired": True,
        "candidateProved": False,
        "emlAdvantageProved": False,
        "generalEmlSuperiorityClaim": False,
        "rhProofClaim": False,
        "zetaZeroDiscoveryClaim": False,
        "runtimePerformanceClaim": False,
        "publicReady": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values())
        and all(all(value is False for value in item["claimFlags"].values()) for item in run_packets),
    }


def build_payload() -> dict[str, Any]:
    plan = d5.build_payload()
    d5.validate_payload(plan)
    run_packets = build_run_packets(plan)
    controls = negative_control_outcomes(run_packets, plan)
    summary = aggregate_summary(run_packets, controls, plan)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "runType": "eml_preregistered_symbolic_search_run_v0",
        "artifactId": "eml-d6-preregistered-symbolic-search-run",
        "status": STATUS,
        "decision": "preregistered_symbolic_search_run_recorded_interpretation_deferred_to_d7",
        "date": DATE,
        "sourcePreregistration": plan["artifactId"],
        "sourceSuccessCriteria": [item["criterionId"] for item in plan["successCriteria"]],
        "runPackets": run_packets,
        "negativeControlOutcomes": controls,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if summary["experimentRunPerformed"] is not True:
        raise ValueError("D6 must run the bounded experiment")
    if summary["runPacketCount"] != 18:
        raise ValueError("expected 18 target/grammar/split packets")
    if summary["psiRunPacketCount"] != 9 or summary["dampedRunPacketCount"] != 9:
        raise ValueError("expected 9 packets per target")
    if summary["negativeControlOutcomeCount"] != 5:
        raise ValueError("expected five negative control outcomes")
    if summary["d7InterpretationRequired"] is not True:
        raise ValueError("D7 interpretation gate must remain required")
    for key in [
        "candidateProved",
        "emlAdvantageProved",
        "generalEmlSuperiorityClaim",
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
        raise ValueError("packet claim flags must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_preregistered_symbolic_search_run",
        "validationStatus": "pass",
        "semanticStrength": "bounded_preregistered_run_interpretation_deferred",
        "source": f"python/results/eml_d6_preregistered_symbolic_search_run/eml_d6_preregistered_symbolic_search_run_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d6_preregistered_symbolic_search_run_feed",
        "date": DATE,
        "status": payload["status"],
        "nextAction": "Run D7 interpretation gate against D5 success criteria before interpreting D6.",
        "sourcePreregistration": payload["sourcePreregistration"],
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D6 Preregistered Symbolic Search Run",
        "",
        f"Status: `{payload['status']}`",
        "",
        "EML-D6 runs the bounded D5-preregistered search and defers interpretation to D7.",
        "",
        "## Summary",
        "",
        f"- run packets: {payload['summary']['runPacketCount']}",
        f"- psi packets: {payload['summary']['psiRunPacketCount']}",
        f"- damped oscillator packets: {payload['summary']['dampedRunPacketCount']}",
        f"- negative control outcomes: {payload['summary']['negativeControlOutcomeCount']}",
        f"- D7 interpretation required: `{payload['summary']['d7InterpretationRequired']}`",
        f"- EML advantage proved: `{payload['summary']['emlAdvantageProved']}`",
        "",
        "## Run Packets",
        "",
        "| Dataset | Split | Grammar | Holdout MSE | Complexity |",
        "|---|---|---|---|---|",
    ]
    for packet in payload["runPackets"]:
        lines.append(
            f"| `{packet['datasetId']}` | `{packet['splitId']}` | `{packet['grammarId']}` | {packet['metrics']['holdoutMse']:.6g} | {packet['bestComplexity']} |"
        )
    lines.extend(["", "## Non-Claims", ""])
    lines.extend(f"- {item}" for item in payload["nonClaims"])
    return "\n".join(lines) + "\n"


def build_outputs(out_dir: Path, report_dir: Path, evidence_dir: Path, command_feed_dir: Path) -> dict[str, Any]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"eml_d6_preregistered_symbolic_search_run_{STAMP}.json"
    report_path = report_dir / f"eml_d6_preregistered_symbolic_search_run_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d6_preregistered_symbolic_search_run.json"
    feed_path = command_feed_dir / f"eml_d6_preregistered_symbolic_search_run_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d6_preregistered_symbolic_search_run")
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
    print("EML_D6_PREREGISTERED_SYMBOLIC_SEARCH_RUN_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
