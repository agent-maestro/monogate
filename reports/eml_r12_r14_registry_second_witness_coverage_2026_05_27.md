# EML-R12/R14 Registry, Second Witness, and Proof Coverage

Date: 2026-05-27
Status: `EML_PROOF_REGISTRY_AND_COVERAGE_CANDIDATE_PASS`
Visibility: internal candidate

## Scope

This sprint makes the proof feedback loop repeatable:

- R12 creates a proof-obligation registry across generated EML packets.
- R13 adds a second checked MachLib witness for the sigmoid denominator.
- R14 surfaces proof coverage and next proof target information in the Explorer.

## Second Checked Witness

Target packet:

- `sigmoid_derivative_v0`
- discharged obligation: `sigmoid_derivative_v0:domain:n5:div-denominator-nonzero`

MachLib witness:

- `MachLib/EMLDomainSafety.lean`
- theorem: `MachLib.Real.sigmoid_denominator_nonzero`

The witness proves that `1 + exp(-x)` is positive and therefore nonzero.

## Registry

Generated artifact:

- `reports/eml_obligation_registry/eml_proof_obligation_registry_2026_05_27.json`

Current coverage:

- total obligations: 6
- domain obligations: 2
- checked witnesses: 2
- unresolved obligations: 4
- unresolved items are currently range-safety assumptions

## Explorer Coverage

The EML packet gallery now shows:

- total obligations
- checked witnesses
- unresolved obligations
- next proof target

Packet detail pages also show checked-witness counts beside the domain lens.

## Boundary

- The registry is a proof-work queue, not a proof.
- Checked witnesses discharge local obligations only.
- No Forge/compiler behavior changes were made.
- No public savings, complete EML safety, certified safety, hardware, package,
  or deployment claim is made.

## Validation

- `lake build` in `../machlib/foundations`
- `python python/scripts/eml_packet_builder.py --build-fixtures --strict`
- `python -m pytest -q python/tests/test_eml_packet_builder.py`
- `npm run build`

