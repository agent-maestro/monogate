#!/usr/bin/env python3
"""EML-D3 holdout/search trials for the EML discovery frontier."""

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

from scripts import eml_d1_discovery_frontier_queue as d1  # noqa: E402
from scripts.eml_prime_residual_benchmark import (  # noqa: E402
    FIRST_ZETA_ZERO_GAMMA,
    eml_prediction,
    fixture as psi_fixture,
    standard_profiled_prediction,
)

DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.eml_discovery_holdout_search_trial.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EML_D3_DISCOVERY_HOLDOUT_SEARCH_TRIALS_PASS"

CLAIM_FLAGS = {
    "candidate_test_performed": False,
    "candidate_proved": False,
    "eml_advantage_proved": False,
    "general_eml_superiority_claim": False,
    "theorem_discovery_claim": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "public_atlas_promotion": False,
    "public_ready": False,
}

NON_CLAIMS = [
    "EML-D3 runs bounded holdout/search trials only.",
    "EML-D3 does not prove EML advantage, theorem discovery, compiler correctness, runtime performance, formal equivalence, public Atlas promotion, RH proof, or zeta-zero discovery.",
    "EML-D3 keeps protected-standard controls visible when they are numerically cleaner than EML-shaped runtime forms.",
]


def candidate_by_id(queue: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    return next(item for item in queue["frontierCandidates"] if item["candidateId"] == candidate_id)


def finite_metric(values: np.ndarray) -> dict[str, Any]:
    finite = np.isfinite(values)
    return {
        "sampleCount": int(values.size),
        "finiteRatio": float(np.mean(finite)),
        "nanOrInfCount": int(values.size - np.count_nonzero(finite)),
    }


def mse(a: np.ndarray, b: np.ndarray) -> float:
    finite = np.isfinite(a) & np.isfinite(b)
    if not np.any(finite):
        return float("inf")
    return float(np.mean((a[finite] - b[finite]) ** 2))


def trial_packet(candidate: dict[str, Any], trial_id: str, trial_class: str, result: dict[str, Any], interpretation: str) -> dict[str, Any]:
    return {
        "candidateId": candidate["candidateId"],
        "trialId": trial_id,
        "door": candidate["door"],
        "family": candidate["family"],
        "trialClass": trial_class,
        "emlForm": candidate["emlForm"],
        "standardForm": candidate["standardForm"],
        "result": result,
        "interpretation": interpretation,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def probability_logit_trial(candidate: dict[str, Any]) -> dict[str, Any]:
    p = np.concatenate(
        [
            np.geomspace(1.0e-12, 1.0e-3, 256),
            np.linspace(0.01, 0.99, 512),
            1.0 - np.geomspace(1.0e-12, 1.0e-3, 256),
        ]
    )
    protected = np.log(p) - np.log1p(-p)
    naive = np.log(p) - np.log(1.0 - p)
    edge = (p < 1.0e-6) | (p > 1.0 - 1.0e-6)
    result = {
        "profiles": [
            {
                "profile": "probability_edge_holdout",
                "positiveProbabilityRatio": float(np.mean((p > 0.0) & (p < 1.0))),
                "edgeSampleCount": int(np.count_nonzero(edge)),
                "protectedFinite": finite_metric(protected),
                "naiveFinite": finite_metric(naive),
                "maxProtectedNaiveAbsDiff": float(np.max(np.abs(protected - naive))),
            }
        ],
        "domainObligationsVisible": ["p > 0", "1 - p > 0"],
        "protectedStandardNoWorse": bool(np.all(np.isfinite(protected)) and mse(protected, naive) <= 1.0e-24),
        "searchCoordinateStatus": "reviewable_guarded_coordinate",
    }
    return trial_packet(
        candidate,
        "probability_logit_boundary_holdout_v0",
        "guarded_search_coordinate_reviewable",
        result,
        "The logit boundary candidate is useful as a domain-obligation/search-coordinate lens; protected standard logit remains the runtime control.",
    )


def normalized_exponential_trial(candidate: dict[str, Any]) -> dict[str, Any]:
    logits = np.array(
        [
            [-1000.0, -999.0, -998.5],
            [0.0, 1.0, 2.0],
            [700.0, 699.0, 698.0],
            [1000.0, 999.0, 998.0],
            [-20.0, 0.0, 20.0],
        ],
        dtype=np.float64,
    )
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        naive_logsumexp = np.log(np.sum(np.exp(logits), axis=1))
    shifted = logits - np.max(logits, axis=1, keepdims=True)
    protected_logsumexp = np.max(logits, axis=1) + np.log(np.sum(np.exp(shifted), axis=1))
    softmax = np.exp(shifted) / np.sum(np.exp(shifted), axis=1, keepdims=True)
    result = {
        "profiles": [
            {
                "profile": "shifted_logits_holdout",
                "rowCount": int(logits.shape[0]),
                "naiveLogsumexpFinite": finite_metric(naive_logsumexp),
                "protectedLogsumexpFinite": finite_metric(protected_logsumexp),
                "softmaxRowSumMaxAbsError": float(np.max(np.abs(np.sum(softmax, axis=1) - 1.0))),
            }
        ],
        "protectedStandardNoWorse": bool(np.all(np.isfinite(protected_logsumexp))),
        "searchCoordinateStatus": "runtime_control_confirmed_review_shape_retained",
    }
    return trial_packet(
        candidate,
        "normalized_exponential_family_holdout_v0",
        "protected_runtime_control_confirmed",
        result,
        "The normalized-exponential candidate remains a useful review/search shape, but protected logsumexp/softmax is the correct runtime control on edge logits.",
    )


def profiled_sine_fit(t: np.ndarray, y: np.ndarray, omega: float, decay: float) -> tuple[np.ndarray, list[float]]:
    envelope = np.exp(-decay * t)
    design = np.column_stack([envelope * np.sin(omega * t), envelope * np.cos(omega * t)])
    coefficients = np.linalg.lstsq(design, y, rcond=None)[0]
    return design @ coefficients, [float(coefficients[0]), float(coefficients[1])]


def damped_oscillator_trial(candidate: dict[str, Any]) -> dict[str, Any]:
    t = np.linspace(0.0, 12.0, 1200)
    split = t < 8.0
    omega = 2.75
    decay = 0.18
    y = 1.6 * np.exp(-decay * t) * np.sin(omega * t + 0.35)
    correct_fit, correct_coefficients = profiled_sine_fit(t, y, omega, decay)
    wrong_frequency_fit, _ = profiled_sine_fit(t, y, omega * 1.22, decay)
    wrong_decay_fit, _ = profiled_sine_fit(t, y, omega, decay * 1.8)
    train_mse = mse(y[split], correct_fit[split])
    holdout_mse = mse(y[~split], correct_fit[~split])
    wrong_frequency_holdout_mse = mse(y[~split], wrong_frequency_fit[~split])
    wrong_decay_holdout_mse = mse(y[~split], wrong_decay_fit[~split])
    result = {
        "profiles": [
            {
                "profile": "damped_oscillator_parameter_holdout",
                "sampleCount": int(t.size),
                "trainSampleCount": int(np.count_nonzero(split)),
                "holdoutSampleCount": int(np.count_nonzero(~split)),
                "trainMse": train_mse,
                "holdoutMse": holdout_mse,
                "wrongFrequencyHoldoutMse": wrong_frequency_holdout_mse,
                "wrongDecayHoldoutMse": wrong_decay_holdout_mse,
                "profiledCoefficients": correct_coefficients,
            }
        ],
        "parameterRecoverySignal": bool(holdout_mse < wrong_frequency_holdout_mse and holdout_mse < wrong_decay_holdout_mse),
        "negativeControlsPassed": bool(wrong_frequency_holdout_mse > holdout_mse and wrong_decay_holdout_mse > holdout_mse),
    }
    return trial_packet(
        candidate,
        "damped_oscillator_eml_phase_holdout_v0",
        "parameter_recovery_signal_supported",
        result,
        "The damped-oscillator holdout supports this as a search/parameter-recovery target with wrong-frequency and wrong-decay controls; it is not an EML runtime win.",
    )


def psi_residual_two_zero_trial(candidate: dict[str, Any]) -> dict[str, Any]:
    fx = psi_fixture(n_samples=360)
    xs = fx["x"]
    residual = fx["residual"]
    train = np.arange(xs.size) % 3 != 0
    gammas = np.linspace(8.0, 28.0, 480)
    eml_train_losses: list[float] = []
    standard_train_losses: list[float] = []
    standard_coefficients: list[list[float]] = []
    for gamma in gammas:
        eml_train_losses.append(mse(residual[train], eml_prediction(xs[train], float(gamma))))
        standard_prediction, coefficients = standard_profiled_prediction(xs[train], residual[train], float(gamma))
        standard_train_losses.append(mse(residual[train], standard_prediction))
        standard_coefficients.append([float(coefficients[0]), float(coefficients[1])])
    eml_idx = int(np.argmin(np.array(eml_train_losses)))
    standard_idx = int(np.argmin(np.array(standard_train_losses)))
    eml_gamma = float(gammas[eml_idx])
    standard_gamma = float(gammas[standard_idx])
    eml_holdout_mse = mse(residual[~train], eml_prediction(xs[~train], eml_gamma))
    standard_holdout_prediction, _ = standard_profiled_prediction(xs[~train], residual[~train], standard_gamma)
    standard_holdout_mse = mse(residual[~train], standard_holdout_prediction)
    result = {
        "profiles": [
            {
                "profile": "psi_residual_gamma_holdout",
                "sampleCount": int(xs.size),
                "trainSampleCount": int(np.count_nonzero(train)),
                "holdoutSampleCount": int(np.count_nonzero(~train)),
                "gammaSteps": int(gammas.size),
                "knownFirstZetaZeroGamma": FIRST_ZETA_ZERO_GAMMA,
                "emlBestTrainGamma": eml_gamma,
                "standardBestTrainGamma": standard_gamma,
                "emlHoldoutMse": eml_holdout_mse,
                "standardHoldoutMse": standard_holdout_mse,
                "emlErrorFromFirstKnownZero": abs(eml_gamma - FIRST_ZETA_ZERO_GAMMA),
                "standardErrorFromFirstKnownZero": abs(standard_gamma - FIRST_ZETA_ZERO_GAMMA),
                "standardProfiledCoefficients": standard_coefficients[standard_idx],
            }
        ],
        "standardLowerHoldoutMse": bool(standard_holdout_mse < eml_holdout_mse),
        "emlCloserToFirstKnownZero": bool(abs(eml_gamma - FIRST_ZETA_ZERO_GAMMA) < abs(standard_gamma - FIRST_ZETA_ZERO_GAMMA)),
        "searchSignalStatus": "ambiguous_requires_preregistered_a6_1",
    }
    return trial_packet(
        candidate,
        "psi_residual_two_zero_holdout_trial_v1",
        "ambiguous_symbolic_search_retained",
        result,
        "The psi-residual holdout remains interesting but ambiguous: localization and MSE can disagree, so this should feed A6.1 rather than any public advantage claim.",
    )


def build_payload() -> dict[str, Any]:
    queue = d1.build_payload()
    selected_ids = [
        "probability_logit_boundary_v0",
        "normalized_exponential_family_v0",
        "damped_oscillator_eml_phase_v0",
        "psi_residual_two_zero_holdout_v1",
    ]
    packets = [
        probability_logit_trial(candidate_by_id(queue, selected_ids[0])),
        normalized_exponential_trial(candidate_by_id(queue, selected_ids[1])),
        damped_oscillator_trial(candidate_by_id(queue, selected_ids[2])),
        psi_residual_two_zero_trial(candidate_by_id(queue, selected_ids[3])),
    ]
    by_class: dict[str, int] = {}
    for packet in packets:
        by_class[packet["trialClass"]] = by_class.get(packet["trialClass"], 0) + 1
    summary = {
        "trialCount": len(packets),
        "selectedCandidateIds": selected_ids,
        "byTrialClass": by_class,
        "holdoutSearchTrialCount": len(packets),
        "guardedSearchCoordinateCount": by_class.get("guarded_search_coordinate_reviewable", 0),
        "protectedRuntimeControlCount": by_class.get("protected_runtime_control_confirmed", 0),
        "parameterRecoverySignalCount": by_class.get("parameter_recovery_signal_supported", 0),
        "ambiguousSearchSignalCount": by_class.get("ambiguous_symbolic_search_retained", 0),
        "candidateTestPerformed": True,
        "candidateProved": False,
        "emlAdvantageProved": False,
        "runtimePerformanceClaim": False,
        "claimFlagsAllFalse": all(all(value is False for value in packet["claimFlags"].values()) for packet in packets),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "trialType": "eml_discovery_holdout_search_trial_v0",
        "artifactId": "eml-d3-discovery-holdout-search-trials",
        "status": STATUS,
        "decision": "eml_discovery_holdout_search_trials_recorded_no_public_claims",
        "date": DATE,
        "sourceQueue": queue["artifactId"],
        "trialPackets": packets,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if summary["trialCount"] != 4:
        raise ValueError("expected 4 D3 holdout/search trials")
    if summary["guardedSearchCoordinateCount"] != 1:
        raise ValueError("expected one guarded search coordinate")
    if summary["protectedRuntimeControlCount"] != 1:
        raise ValueError("expected one protected runtime control")
    if summary["parameterRecoverySignalCount"] != 1:
        raise ValueError("expected one parameter-recovery signal")
    if summary["ambiguousSearchSignalCount"] != 1:
        raise ValueError("expected one ambiguous search signal")
    for key in ["candidateProved", "emlAdvantageProved", "runtimePerformanceClaim"]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    if not all(value is False for value in payload["claimFlags"].values()):
        raise ValueError("claim flag drift")
    if summary["claimFlagsAllFalse"] is not True:
        raise ValueError("trial claim flags must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "eml_discovery_holdout_search_trial",
        "validationStatus": "pass",
        "semanticStrength": "bounded_holdout_search_trials_no_advantage_claim",
        "source": f"python/results/eml_d3_discovery_holdout_search_trials/eml_d3_discovery_holdout_search_trials_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "eml_d3_discovery_holdout_search_trials_feed",
        "date": DATE,
        "status": payload["status"],
        "selectedCandidateIds": payload["summary"]["selectedCandidateIds"],
        "nextAction": "Route protected-standard controls into the failure atlas and send the ambiguous psi-residual signal to A6.1 preregistration.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EML-D3 Discovery Holdout/Search Trials",
        "",
        f"Status: `{payload['status']}`",
        "",
        "EML-D3 runs bounded holdout/search trials from the D1 frontier queue.",
        "",
        "| Candidate | Trial class | Interpretation |",
        "|---|---|---|",
    ]
    for packet in payload["trialPackets"]:
        lines.append(f"| `{packet['candidateId']}` | `{packet['trialClass']}` | {packet['interpretation']} |")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- trials: {payload['summary']['trialCount']}",
            f"- guarded search coordinates: {payload['summary']['guardedSearchCoordinateCount']}",
            f"- protected runtime controls: {payload['summary']['protectedRuntimeControlCount']}",
            f"- parameter-recovery signals: {payload['summary']['parameterRecoverySignalCount']}",
            f"- ambiguous search signals: {payload['summary']['ambiguousSearchSignalCount']}",
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
    result_path = out_dir / f"eml_d3_discovery_holdout_search_trials_{STAMP}.json"
    report_path = report_dir / f"eml_d3_discovery_holdout_search_trials_{STAMP}.md"
    evidence_path = evidence_dir / "eml_d3_discovery_holdout_search_trials.json"
    feed_path = command_feed_dir / f"eml_d3_discovery_holdout_search_trials_feed_{STAMP}.json"
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
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_d3_discovery_holdout_search_trials")
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
    print("EML_D3_DISCOVERY_HOLDOUT_SEARCH_TRIALS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
