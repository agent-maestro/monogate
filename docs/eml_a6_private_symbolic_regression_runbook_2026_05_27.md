# EML-A6 Private Symbolic Regression Runbook

Date: 2026-05-27
Status: PRIVATE_RUNBOOK_READY
Visibility: private

## Purpose

Run the real A6 symbolic-regression experiment once PySR is available, without
turning the setup itself into a research fog machine.

The experiment compares:

- EML-native grammar
- standard `exp/log/sin/cos/sqrt` grammar

on the fixed `psi(x) - x` residual fixture used by A2/A5.

## Current Blocker

PySR is not installed in the current environment. The checked A6 artifact
records:

```text
pysr_available = false
fullRunPerformed = false
```

This is intentional. Do not claim a full symbolic-regression run until the
runner has produced captured artifacts.

## Environment Plan

Use an isolated Python environment. Recommended:

```bash
cd /home/monogate/monogate/monogate
python -m venv .venv-a6-pysr
source .venv-a6-pysr/bin/activate
python -m pip install --upgrade pip wheel setuptools
python -m pip install -r python/requirements-eml-a6-pysr.txt
```

PySR may install or require Julia dependencies. Keep that dependency inside
the private environment and record the exact versions in the run artifact.

## Intended One-Command Run

The current private harness is:

```bash
python python/scripts/eml_a6_private_symbolic_regression.py --build --strict
```

When PySR is installed, extend this harness rather than creating a separate
untracked notebook. The command should remain the public entrypoint for local
validation, with an explicit flag for the expensive run if needed:

```bash
python python/scripts/eml_a6_private_symbolic_regression.py \
  --build \
  --run-pysr \
  --max-runtime-seconds 900 \
  --seed 20260527 \
  --strict
```

The `--run-pysr` flag is not implemented yet. Add it only when the environment
is ready.

## Required Captured Artifacts

The real run should write:

- `python/results/eml_a6_private_symbolic_regression/eml_a6_pysr_run_2026_05_27.json`
- `reports/eml_a6_private_symbolic_regression_pysr_run_2026_05_27.md`
- `reports/evidence_packets/eml_a6_private_symbolic_regression.json`
- model hall-of-fame tables for both grammars
- train/holdout residual metrics
- complexity curves
- environment/version manifest

## Required Metrics

Minimum metrics:

- `fullRunPerformed`
- `seed`
- `maxRuntimeSeconds`
- `grammar`
- `operatorSet`
- `bestExpression`
- `bestLoss`
- `bestHoldoutLoss`
- `complexity`
- `complexityAtFirstAcceptableLoss`
- `runtimeSeconds`
- `environment`

## Required Controls

Run the same grammar comparison on:

- true `psi(x) - x` residual fixture
- shuffled residual control
- Gaussian-bump control
- wrong-exponent EML-like control

The wrong-exponent control is important because A5 found that it can localize
near the first known zero slightly better than the critical-line template on
the fixed fixture. A6 must test whether the EML advantage survives controls,
not merely whether it produces beautiful expressions.

## Claim Boundary

The real A6 run may claim only:

- a private symbolic-regression experiment ran
- these expressions and metrics were observed on these fixtures
- these controls passed or failed

It must not claim:

- proof of RH
- zeta-zero discovery
- theorem discovery
- general EML grammar superiority
- public Atlas promotion
- Forge/compiler behavior change

## Success Criteria

A6 becomes interesting if:

- EML grammar reaches comparable or better holdout loss at lower complexity
  than the standard grammar,
- this advantage survives negative controls,
- and the best expressions are stable across seeds.

A6 is also useful if it fails. A clean null result would tell us the prime
residual lane is mostly notation/beauty rather than a real search advantage.

