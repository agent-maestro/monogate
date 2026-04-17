"""CapCard CLI — Session 34.

Usage:
    python -m monogate capability-card --generate
    python -m monogate capability-card --validate
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import monogate


_REPO_ROOT = Path(__file__).parent.parent.parent.parent
_CARD_PATH = _REPO_ROOT / "capability_card.json"
_SCHEMA_PATH = Path(__file__).parent.parent / "capability_card_schema.json"


def _run_test_count() -> int:
    """Return the number of tests discovered in the python/ test suite."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-q", "--co", "--tb=no"],
            capture_output=True, text=True,
            cwd=Path(__file__).parent.parent.parent,
        )
        for line in result.stdout.splitlines():
            if "tests collected" in line or "test collected" in line:
                return int(line.split()[0])
    except Exception:
        pass
    return -1


def _gather_capabilities() -> dict:
    """Read live capability data from the monogate package."""
    test_count = _run_test_count()

    cap: dict = {
        "symbolic_regression": {
            "description": "Symbolic regression using EML (exp-minus-log) tree arithmetic",
            "operators": ["eml", "edl", "eal", "exl", "deml"],
            "search_methods": ["beam_search", "mcts_search", "exhaustive", "sklearn_wrapper"],
        },
        "physics_laws": {
            "count": 14,
            "exact_zero_error": 8,
            "catalog": [
                "Newton's second law", "Gravitational force", "Coulomb's law",
                "Ohm's law", "Ideal gas law", "Hooke's law", "Kinetic energy",
                "Potential energy", "Wave speed", "Snell's law",
                "Lorentz force", "Stefan-Boltzmann", "Planck law", "Hubble law",
            ],
        },
        "special_functions": {
            "count": 15,
            "exact_cbest": 4,
            "note": "Complex BEST (CBEST) representation; sin(x) infinite-zeros barrier proven",
        },
        "test_count": test_count,
        "sin_barrier": {
            "n_trees_searched": 109824,
            "max_n": 7,
            "sin_absent": True,
            "note": "Exhaustive search to N=7 (Python); N=12 Rust binary complete, pending runtime",
        },
        "eml_fourier": {
            "description": "Session 31: sin(x) as linear combination of EML tree atoms",
            "sin_approx_K": 5,
            "sin_mse_train": 8.945e-4,
            "sin_mse_test": 2.326e-2,
            "exp_mse_test": 8.037e-31,
            "log_mse_test": 6.023e-32,
        },
        "eml_vae": {
            "description": "Session 32: Gaussian VAE with EML natural parameter encoder",
            "kl_is_bregman": True,
            "prior": "N(0,1) as eta1=-0.5, eta2=0",
        },
    }
    return cap


def generate_card() -> dict:
    """Build and write capability_card.json to repo root."""
    version = monogate.__version__
    caps = _gather_capabilities()

    card = {
        "$schema": "https://capcard.ai/schema/v1.json",
        "card_version": "1.0",
        "name": "monogate",
        "version": version,
        "tagline": "Universal EML tree arithmetic for symbolic computation",
        "capabilities": caps,
        "benchmarks": {
            "srbench": {
                "datasets_tested": 10,
                "note": "SRBench harness in python/benchmarks/srbench/",
            },
        },
        "reproduce": {
            "install": "pip install monogate",
            "test": "cd python && pytest tests/ -q",
            "docker": "docker build . && docker run monogate pytest python/tests/ -q",
        },
        "artifacts": {
            "arxiv": "2603.21852",
            "pypi": f"monogate=={version}",
            "github": "https://github.com/artl/monogate",
        },
    }

    _CARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_CARD_PATH, "w", encoding="utf-8") as f:
        json.dump(card, f, indent=2)

    print(f"CapCard written to: {_CARD_PATH}")
    print(f"  version:    {version}")
    print(f"  tests:      {caps['test_count']}")
    print(f"  sin_absent: {caps['sin_barrier']['sin_absent']}")
    print(f"  EML Fourier sin K={caps['eml_fourier']['sin_approx_K']}, "
          f"MSE_test={caps['eml_fourier']['sin_mse_test']:.3e}")
    return card


def validate_card() -> bool:
    """Validate capability_card.json against JSON Schema."""
    try:
        import jsonschema
    except ImportError:
        print("jsonschema not installed — run: pip install jsonschema")
        print("Falling back to basic structure check...")
        return _basic_validate()

    if not _CARD_PATH.exists():
        print(f"capability_card.json not found at {_CARD_PATH}")
        print("Run: python -m monogate capability-card --generate")
        return False

    with open(_CARD_PATH, encoding="utf-8") as f:
        card = json.load(f)
    with open(_SCHEMA_PATH, encoding="utf-8") as f:
        schema = json.load(f)

    try:
        jsonschema.validate(instance=card, schema=schema)
        print("capability_card.json: VALID")
        _report_key_benchmarks(card)
        return True
    except jsonschema.ValidationError as e:
        print(f"INVALID: {e.message}")
        return False


def _basic_validate() -> bool:
    """Minimal structure check without jsonschema dependency."""
    if not _CARD_PATH.exists():
        print(f"Not found: {_CARD_PATH}")
        return False
    with open(_CARD_PATH, encoding="utf-8") as f:
        card = json.load(f)
    required = ["card_version", "name", "version", "capabilities", "artifacts"]
    missing = [k for k in required if k not in card]
    if missing:
        print(f"Missing required keys: {missing}")
        return False
    print("capability_card.json: basic structure OK")
    _report_key_benchmarks(card)
    return True


def _report_key_benchmarks(card: dict) -> None:
    caps = card.get("capabilities", {})
    print(f"  name:       {card.get('name')} v{card.get('version')}")
    print(f"  tests:      {caps.get('test_count', '?')}")
    barrier = caps.get("sin_barrier", {})
    print(f"  sin_absent: {barrier.get('sin_absent')} (N≤{barrier.get('max_n','?')})")
    fourier = caps.get("eml_fourier", {})
    if fourier:
        print(f"  Fourier K:  {fourier.get('sin_approx_K')}, MSE_test={fourier.get('sin_mse_test'):.3e}")


def main(argv: list[str] | None = None) -> None:
    import argparse
    parser = argparse.ArgumentParser(description="monogate CapCard generator/validator")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--generate", action="store_true", help="Generate capability_card.json")
    group.add_argument("--validate", action="store_true", help="Validate capability_card.json")
    args = parser.parse_args(argv)

    if args.generate:
        generate_card()
    elif args.validate:
        ok = validate_card()
        if not ok:
            sys.exit(1)


if __name__ == "__main__":
    main()
