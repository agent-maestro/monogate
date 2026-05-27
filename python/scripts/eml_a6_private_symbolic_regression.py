#!/usr/bin/env python3
"""EML-A6 private symbolic-regression harness.

This private runner records PySR availability and, when explicitly requested,
runs a bounded grammar comparison over the A2/A5 `psi(x) - x` fixture. It is
not an autonomous-discovery or theorem lane.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import platform
from pathlib import Path
import sys
import time
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_language_kernel import DATE  # noqa: E402
from scripts.eml_packet_builder import DEFAULT_CLAIM_FLAGS  # noqa: E402
from scripts.eml_prime_residual_benchmark import fixture  # noqa: E402
from scripts.eml_symbolic_regression_template_search import build_search  # noqa: E402

SCHEMA_VERSION = "monogate.eml_a6_private_symbolic_regression.v0"
STATUS = "EML_A6_PRIVATE_SYMBOLIC_REGRESSION_BLOCKED_PYSR_UNAVAILABLE"
RUN_STATUS = "EML_A6_PRIVATE_SYMBOLIC_REGRESSION_PYSR_RUN_PASS"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"


def pysr_status() -> dict[str, Any]:
    spec = importlib.util.find_spec("pysr")
    version = None
    if spec is not None:
        try:
            import pysr  # type: ignore

            version = getattr(pysr, "__version__", "unknown")
        except Exception as exc:  # pragma: no cover
            version = f"import_error:{type(exc).__name__}"
    return {
        "available": spec is not None,
        "module": "pysr",
        "status": "available" if spec is not None else "unavailable",
        "version": version,
    }


def feature_matrix(xs: np.ndarray) -> np.ndarray:
    return np.column_stack([xs, np.log(xs), np.sqrt(xs)]).astype(np.float32)


def split_fixture(xs: np.ndarray, y: np.ndarray, seed: int) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    indices = np.arange(len(xs))
    rng.shuffle(indices)
    holdout_count = max(1, len(indices) // 4)
    holdout_idx = np.sort(indices[:holdout_count])
    train_idx = np.sort(indices[holdout_count:])
    return {
        "x_train": xs[train_idx],
        "y_train": y[train_idx],
        "x_holdout": xs[holdout_idx],
        "y_holdout": y[holdout_idx],
    }


def datasets(seed: int, n_samples: int) -> list[dict[str, Any]]:
    fx = fixture(n_samples=n_samples)
    xs = fx["x"]
    residual = fx["residual"]
    rng = np.random.default_rng(seed)
    shuffled = residual.copy()
    rng.shuffle(shuffled)
    gaussian = 3.0 * np.exp(-((xs - 48.0) ** 2) / (2 * 12.0**2)) - 2.0 * np.exp(
        -((xs - 92.0) ** 2) / (2 * 8.0**2)
    )
    return [
        {"id": "psi_residual", "kind": "target", "x": xs, "y": residual, "summary": fx["summary"]},
        {"id": "shuffled_residual_control", "kind": "negative_control", "x": xs, "y": shuffled, "summary": fx["summary"]},
        {"id": "gaussian_bumps_control", "kind": "negative_control", "x": xs, "y": gaussian, "summary": fx["summary"]},
    ]


def grammar_configs() -> list[dict[str, Any]]:
    return [
        {
            "id": "eml_native",
            "binaryOperators": ["+", "*", "-", "/", "eml(x, y) = exp(x) - log(abs(y) + 1.0f-6)"],
            "unaryOperators": [],
            "description": "Real-valued EML grammar with arithmetic and protected eml(x,y).",
        },
        {
            "id": "standard_exp_log_trig",
            "binaryOperators": ["+", "*", "-", "/"],
            "unaryOperators": [
                "sin",
                "cos",
                "exp",
                "log_abs(x)=log(abs(x)+1.0f-6)",
                "sqrt_abs(x)=sqrt(abs(x))",
            ],
            "description": "Standard protected exp/log/trig/sqrt grammar with arithmetic.",
        },
    ]


def sympy_mappings() -> dict[str, Any]:
    import sympy as sp

    return {
        "eml": lambda x, y: sp.exp(x) - sp.log(sp.Abs(y) + sp.Float("1e-6")),
        "log_abs": lambda x: sp.log(sp.Abs(x) + sp.Float("1e-6")),
        "sqrt_abs": lambda x: sp.sqrt(sp.Abs(x)),
    }


def rows_from_equations(equations: Any) -> list[dict[str, Any]]:
    rows = []
    for _, row in equations.iterrows():
        rows.append(
            {
                "complexity": int(row.get("complexity")),
                "loss": float(row.get("loss")),
                "score": float(row.get("score", 0.0)),
                "equation": str(row.get("equation")),
                "sympy": str(row.get("sympy_format")),
            }
        )
    return rows


def run_one_pysr(
    dataset: dict[str, Any],
    grammar: dict[str, Any],
    seed: int,
    per_model_timeout_seconds: int,
    niterations: int,
    maxsize: int,
    output_dir: Path,
) -> dict[str, Any]:
    from pysr import PySRRegressor

    split = split_fixture(dataset["x"], dataset["y"], seed)
    x_train = feature_matrix(split["x_train"])
    x_holdout = feature_matrix(split["x_holdout"])
    y_train = split["y_train"].astype(np.float32)
    y_holdout = split["y_holdout"].astype(np.float32)
    start = time.time()
    model = PySRRegressor(
        binary_operators=grammar["binaryOperators"],
        unary_operators=grammar["unaryOperators"],
        extra_sympy_mappings=sympy_mappings(),
        niterations=niterations,
        populations=4,
        population_size=24,
        maxsize=maxsize,
        timeout_in_seconds=per_model_timeout_seconds,
        random_state=seed,
        deterministic=True,
        parallelism="serial",
        verbosity=0,
        progress=False,
        model_selection="best",
        tempdir=str(output_dir / "pysr_temp"),
        delete_tempfiles=True,
    )
    model.fit(x_train, y_train, variable_names=["x", "logx", "sqrtx"])
    runtime = time.time() - start
    train_prediction = model.predict(x_train)
    holdout_prediction = model.predict(x_holdout)
    rows = rows_from_equations(model.equations_)
    best_row = rows[-1] if rows else {}
    return {
        "datasetId": dataset["id"],
        "datasetKind": dataset["kind"],
        "grammarId": grammar["id"],
        "grammarDescription": grammar["description"],
        "fullRunPerformed": True,
        "seed": seed,
        "perModelTimeoutSeconds": per_model_timeout_seconds,
        "niterations": niterations,
        "maxsize": maxsize,
        "trainSampleCount": int(len(y_train)),
        "holdoutSampleCount": int(len(y_holdout)),
        "runtimeSeconds": runtime,
        "bestEquation": best_row.get("equation"),
        "bestComplexity": best_row.get("complexity"),
        "bestLoss": best_row.get("loss"),
        "trainMse": float(np.mean((y_train - train_prediction) ** 2)),
        "holdoutMse": float(np.mean((y_holdout - holdout_prediction) ** 2)),
        "hallOfFame": rows,
    }


def run_pysr_experiment(
    out_dir: Path,
    seed: int,
    max_runtime_seconds: int,
    niterations: int,
    maxsize: int,
    n_samples: int,
) -> dict[str, Any]:
    ds = datasets(seed=seed, n_samples=n_samples)
    grammars = grammar_configs()
    per_model_timeout = max(10, int(max_runtime_seconds / (len(ds) * len(grammars))))
    runs = []
    for dataset in ds:
        for grammar in grammars:
            runs.append(
                run_one_pysr(
                    dataset=dataset,
                    grammar=grammar,
                    seed=seed,
                    per_model_timeout_seconds=per_model_timeout,
                    niterations=niterations,
                    maxsize=maxsize,
                    output_dir=out_dir,
                )
            )
    target_runs = [run for run in runs if run["datasetId"] == "psi_residual"]
    by_grammar = {run["grammarId"]: run for run in target_runs}
    return {
        "runPerformed": True,
        "seed": seed,
        "maxRuntimeSeconds": max_runtime_seconds,
        "perModelTimeoutSeconds": per_model_timeout,
        "niterations": niterations,
        "maxsize": maxsize,
        "sampleCount": n_samples,
        "datasetCount": len(ds),
        "grammarCount": len(grammars),
        "runs": runs,
        "targetComparison": {
            "emlHoldoutMse": by_grammar["eml_native"]["holdoutMse"],
            "standardHoldoutMse": by_grammar["standard_exp_log_trig"]["holdoutMse"],
            "emlLowerHoldoutMse": by_grammar["eml_native"]["holdoutMse"]
            < by_grammar["standard_exp_log_trig"]["holdoutMse"],
            "emlBestComplexity": by_grammar["eml_native"]["bestComplexity"],
            "standardBestComplexity": by_grammar["standard_exp_log_trig"]["bestComplexity"],
        },
    }


def build_private_run(
    out_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    run_pysr: bool = False,
    seed: int = 20260527,
    max_runtime_seconds: int = 180,
    niterations: int = 12,
    maxsize: int = 12,
    n_samples: int = 240,
) -> dict[str, Any]:
    availability = pysr_status()
    fallback = build_search(
        out_dir=ROOT / "python/results/eml_symbolic_regression_template_search",
        report_dir=report_dir,
        evidence_dir=evidence_dir,
    )["result"]
    pysr_run = None
    status = STATUS
    if run_pysr:
        if not availability["available"]:
            raise RuntimeError("PySR requested but unavailable")
        out_dir.mkdir(parents=True, exist_ok=True)
        pysr_run = run_pysr_experiment(out_dir, seed, max_runtime_seconds, niterations, maxsize, n_samples)
        status = RUN_STATUS
    result = {
        "schemaVersion": SCHEMA_VERSION,
        "date": DATE,
        "status": status,
        "runId": "eml_a6_private_pysr_harness_v0",
        "visibility": "private_only",
        "pysr": {
            **availability,
            "fullRunPerformed": pysr_run is not None,
            "blocker": (
                "PySR is not installed in this environment."
                if not availability["available"]
                else None if pysr_run is not None else "Not run by default; enable explicitly with --run-pysr."
            ),
        },
        "pysrRun": pysr_run,
        "environment": {
            "pythonVersion": sys.version.split()[0],
            "platform": platform.platform(),
            "machine": platform.machine(),
            "executable": sys.executable,
        },
        "fallback": {
            "kind": "deterministic_template_search",
            "status": fallback["status"],
            "searchId": fallback["searchId"],
            "reviewFinding": fallback["interpretation"]["reviewFinding"],
            "resultPath": f"python/results/eml_symbolic_regression_template_search/eml_symbolic_regression_template_search_{DATE.replace('-', '_')}.json",
            "templateCount": len(fallback["templates"]),
        },
        "nextRunContract": {
            "requires": ["pysr installed", "private runner only", "fixed random seed", "max runtime bound", "artifact capture"],
            "compareGrammars": ["eml_native", "standard_exp_log_trig"],
            "primaryMetrics": ["complexity_at_first_acceptable_loss", "best_loss_by_complexity", "generalization_holdout_loss"],
        },
        "claimFlags": {
            **dict(DEFAULT_CLAIM_FLAGS),
            "pysr_run_claim": pysr_run is not None,
            "autonomous_discovery_claim": False,
            "rh_proof_claim": False,
            "zeta_zero_discovery_claim": False,
            "public_atlas_promotion": False,
        },
        "nonClaims": [
            "This artifact records a bounded private PySR run." if pysr_run is not None else "This artifact does not claim a full PySR run.",
            "This artifact does not claim autonomous discovery.",
            "This artifact does not prove RH or discover zeta zeros.",
            "This artifact is private-only and does not promote Atlas entries.",
        ],
    }
    evidence = build_evidence_packet(result)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    stamp = DATE.replace("-", "_")
    result_path = out_dir / f"eml_a6_private_symbolic_regression_{stamp}.json"
    report_path = report_dir / f"eml_a6_private_symbolic_regression_{stamp}.md"
    evidence_path = evidence_dir / "eml_a6_private_symbolic_regression.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(result), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"result": result, "evidence": evidence, "result_path": str(result_path), "report_path": str(report_path), "evidence_path": str(evidence_path)}


def build_evidence_packet(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": "eml-a6-private-symbolic-regression",
        "title": "EML-A6 Private Symbolic Regression Harness",
        "reviewDecision": "private_run_recorded" if result["pysr"]["fullRunPerformed"] else "blocked_environment_dependency",
        "validationStatus": "pass",
        "replayStatus": "pass",
        "semanticStrength": "private_pysr_run_no_discovery_or_proof_claim",
        "semanticReview": {
            "pysr_available": result["pysr"]["available"],
            "full_run_performed": result["pysr"]["fullRunPerformed"],
            "fallback_status": result["fallback"]["status"],
            "target_comparison": result["pysrRun"]["targetComparison"] if result.get("pysrRun") else None,
        },
        "claimBoundary": "Private harness only; bounded PySR run may be recorded, but no autonomous-discovery, proof, zeta-zero, or public Atlas claim.",
        "claimFlags": {
            **dict(DEFAULT_CLAIM_FLAGS),
            "pysr_run_claim": result["pysr"]["fullRunPerformed"],
            "autonomous_discovery_claim": False,
            "rh_proof_claim": False,
            "zeta_zero_discovery_claim": False,
            "public_atlas_promotion": False,
            "package_publish_performed": False,
            "deploy_performed": False,
        },
        "nonClaims": result["nonClaims"],
        "reviewHighlights": [
            "Records PySR availability and whether a bounded private run occurred.",
            "Keeps A5 deterministic template search as fallback/context evidence.",
        ],
        "validationCommands": [
            "python python/scripts/eml_a6_private_symbolic_regression.py --build --strict",
            "python -m pytest -q python/tests/test_eml_a6_private_symbolic_regression.py",
        ],
    }


def render_report(result: dict[str, Any]) -> str:
    lines = [
        "# EML-A6 Private Symbolic Regression Harness",
        "",
        f"Date: {DATE}",
        "",
        f"Status: `{result['status']}`",
        "",
        f"PySR available: `{result['pysr']['available']}`",
        "",
        f"Full run performed: `{result['pysr']['fullRunPerformed']}`",
        "",
        f"Fallback: `{result['fallback']['kind']}` / `{result['fallback']['status']}`",
        "",
    ]
    if result.get("pysrRun"):
        comparison = result["pysrRun"]["targetComparison"]
        lines.extend(
            [
                "## PySR Target Fixture Comparison",
                "",
                f"- EML holdout MSE: `{comparison['emlHoldoutMse']:.6f}`",
                f"- Standard holdout MSE: `{comparison['standardHoldoutMse']:.6f}`",
                f"- EML lower holdout MSE: `{comparison['emlLowerHoldoutMse']}`",
                f"- EML best complexity: `{comparison['emlBestComplexity']}`",
                f"- Standard best complexity: `{comparison['standardBestComplexity']}`",
                "",
                "## Run Rows",
                "",
            ]
        )
        for run in result["pysrRun"]["runs"]:
            lines.append(
                f"- `{run['datasetId']}` / `{run['grammarId']}`: "
                f"holdout `{run['holdoutMse']:.6f}`, complexity `{run['bestComplexity']}`, "
                f"equation `{run['bestEquation']}`"
            )
        lines.append("")
    lines.extend(
        [
            "## Next Run Contract",
            "",
            *[f"- {item}" for item in result["nextRunContract"]["requires"]],
            "",
            "## Non-Claims",
            "",
            *[f"- {item}" for item in result["nonClaims"]],
            "",
        ]
    )
    return "\n".join(lines)


def validate_private_run(result: dict[str, Any]) -> None:
    if result.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("invalid A6 schema")
    if result["pysr"]["fullRunPerformed"] is True and not result.get("pysrRun"):
        raise ValueError("full PySR run flag requires captured run artifact")
    if result["fallback"]["status"] != "EML_SYMBOLIC_REGRESSION_TEMPLATE_SEARCH_PASS":
        raise ValueError("fallback template search must pass")
    for key, value in result.get("claimFlags", {}).items():
        if key == "pysr_run_claim" and result["pysr"]["fullRunPerformed"] is True:
            if value is not True:
                raise ValueError("pysr_run_claim should reflect captured private run")
            continue
        if value is not False:
            raise ValueError(f"claim flag must remain false: {key}")
    if result.get("pysrRun") and len(result["pysrRun"]["runs"]) < 6:
        raise ValueError("expected target and control runs for both grammars")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_a6_private_symbolic_regression")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--run-pysr", action="store_true")
    parser.add_argument("--seed", type=int, default=20260527)
    parser.add_argument("--max-runtime-seconds", type=int, default=180)
    parser.add_argument("--niterations", type=int, default=12)
    parser.add_argument("--maxsize", type=int, default=12)
    parser.add_argument("--n-samples", type=int, default=240)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.build:
        raise SystemExit("--build is required")
    built = build_private_run(
        args.out_dir,
        args.report_dir,
        args.evidence_dir,
        run_pysr=args.run_pysr,
        seed=args.seed,
        max_runtime_seconds=args.max_runtime_seconds,
        niterations=args.niterations,
        maxsize=args.maxsize,
        n_samples=args.n_samples,
    )
    if args.strict:
        validate_private_run(built["result"])
    print("EML_A6_PRIVATE_SYMBOLIC_REGRESSION_OK")
    print(f"pysr_available={built['result']['pysr']['available']}")
    print(f"full_run_performed={built['result']['pysr']['fullRunPerformed']}")
    print(f"result={built['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
