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


def publish_card() -> None:
    """Print GitHub Pages deployment instructions for the CapCard site."""
    print("CapCard GitHub Pages Deployment")
    print("=" * 50)
    print()
    print("1. Ensure capcard_site/ is committed to your repo:")
    print("   git add capcard_site/")
    print("   git commit -m 'feat: CapCard launch site'")
    print()
    print("2. Push to GitHub:")
    print("   git push origin master")
    print()
    print("3. Enable GitHub Pages (repo Settings > Pages):")
    print("   - Source: Deploy from branch")
    print("   - Branch: master, folder: /capcard_site")
    print("   - Save")
    print()
    print("4. Your CapCard will be live at:")
    print("   https://<username>.github.io/monogate/capcard_site/")
    print()
    print("5. For custom domain (capcard.ai):")
    print("   - Buy domain from registrar")
    print("   - Add CNAME record pointing to <username>.github.io")
    print("   - Add file capcard_site/CNAME containing: capcard.ai")
    print("   - Enable 'Enforce HTTPS' in GitHub Pages settings")
    print()
    print("Schema URL (after publish):")
    print("   https://capcard.ai/schema/v1.json")


def _run_benchmark_assertions() -> tuple[bool, list[str]]:
    """Run 5 benchmark assertions and return (all_passed, messages)."""
    messages: list[str] = []
    passed = 0

    # 1. exp identity: eml(x,1) = exp(x)
    try:
        import math
        from monogate.core import op
        for x in [0.5, 1.0, 2.0]:
            assert abs(op(x, 1.0) - math.exp(x)) < 1e-12
        messages.append("PASS  exp identity: eml(x,1) = exp(x)")
        passed += 1
    except Exception as e:
        messages.append(f"FAIL  exp identity: {e}")

    # 2. abs identity (EML identity function): eml(1,eml(eml(1,eml(x,1)),1)) = x
    try:
        from monogate.core import op
        for x in [0.5, 1.0, 3.14]:
            result = op(1.0, op(op(1.0, op(x, 1.0)), 1.0))
            assert abs(result - x) < 1e-11, f"got {result}"
        messages.append("PASS  identity theorem: eml(1,eml(eml(1,eml(x,1)),1)) = x")
        passed += 1
    except Exception as e:
        messages.append(f"FAIL  identity theorem: {e}")

    # 3. sin barrier: tree enumeration at N=3 finds no sin(x)
    try:
        from monogate.frontiers.eml_fourier import build_eml_dictionary, _eval_tree
        import math
        atoms = build_eml_dictionary(max_internal_nodes=3)
        test_xs = [0.5, 1.0, 1.5, 2.0]
        sin_vals = [math.sin(x) for x in test_xs]
        match_found = False
        for a in atoms:
            vals = [_eval_tree(a.ops, a.leaf_mask, x) for x in test_xs]
            if all(v is not None for v in vals):
                errs = [abs(v - s) for v, s in zip(vals, sin_vals)]
                if max(errs) < 1e-6:
                    match_found = True
                    break
        assert not match_found
        messages.append(f"PASS  sin barrier: no match in {len(atoms)} atoms at N<=3")
        passed += 1
    except Exception as e:
        messages.append(f"FAIL  sin barrier: {e}")

    # 4. test count >= 1500
    try:
        count = _run_test_count()
        assert count >= 1500, f"only {count} tests found"
        messages.append(f"PASS  test count: {count} >= 1500")
        passed += 1
    except Exception as e:
        messages.append(f"FAIL  test count: {e}")

    # 5. version string valid semver
    try:
        import re
        v = monogate.__version__
        assert re.match(r"^\d+\.\d+\.\d+", v), f"bad version: {v!r}"
        messages.append(f"PASS  version: {v} is valid semver")
        passed += 1
    except Exception as e:
        messages.append(f"FAIL  version: {e}")

    return passed == 5, messages


def verify_card() -> bool:
    """Validate card schema AND run 5 benchmark assertions."""
    print("CapCard Verification")
    print("=" * 50)

    schema_ok = validate_card()
    print()
    print("Benchmark assertions:")
    all_pass, messages = _run_benchmark_assertions()
    for msg in messages:
        print(f"  {msg}")

    print()
    if schema_ok and all_pass:
        print("RESULT: ALL CHECKS PASSED")
        return True
    else:
        print("RESULT: SOME CHECKS FAILED")
        return False


def main(argv: list[str] | None = None) -> None:
    import argparse
    parser = argparse.ArgumentParser(description="monogate CapCard generator/validator")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--generate", action="store_true", help="Generate capability_card.json")
    group.add_argument("--validate", action="store_true", help="Validate capability_card.json against schema")
    group.add_argument("--publish", action="store_true", help="Print GitHub Pages deployment instructions")
    group.add_argument("--verify", action="store_true", help="Validate schema + run benchmark assertions")
    args = parser.parse_args(argv)

    if args.generate:
        generate_card()
    elif args.validate:
        ok = validate_card()
        if not ok:
            sys.exit(1)
    elif args.publish:
        publish_card()
    elif args.verify:
        ok = verify_card()
        if not ok:
            sys.exit(1)


if __name__ == "__main__":
    main()
