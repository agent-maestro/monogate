# EML-R6/R7 Domain Safety Lens and MachLib Stub Export

Date: 2026-05-27
Status: `EML_DOMAIN_SAFETY_AND_MACHLIB_STUB_EXPORT_PASS`
Visibility: internal candidate

## Scope

EML-R6 adds a deterministic Domain Safety Lens to EML Expression Packet v0
outputs. It classifies:

- domain requirements
- range assumptions
- unresolved obligations
- possible safe rewrites
- blocked public claims

EML-R7 adds a MachLib-facing obligation stub export. The generated `.lean`
files are candidate-only markers for future proof work, not proofs.

## Generated Artifacts

- `python/results/eml_packets/*_packet_2026_05_27.json`
- `reports/evidence_packets/*_eml_packet.json`
- `reports/eml_packets/*_packet_builder_2026_05_27.md`
- `reports/eml_obligations/*/*_obligations.lean`
- `reports/eml_obligations/*/*_machlib_stub_manifest.json`

## Current Fixture Lens Counts

- `softplus_pair_v0`: 1 domain requirement, 2 range assumptions, 3 unresolved obligations.
- `sigmoid_derivative_v0`: 1 domain requirement, 1 range assumption, 2 unresolved obligations.
- `gaussian_energy_v0`: 0 domain requirements, 1 range assumption, 1 unresolved obligation.

All generated fixtures keep `proved_count = 0`.

## Boundary

- Domain Safety Lens output is deterministic classification, not proof.
- Safe rewrite suggestions are candidates, not compiler behavior changes.
- Range assumptions are declared packet metadata, not runtime or hardware evidence.
- MachLib stubs are not MachLib build results.
- No public savings, theorem/proof, formal verification, hardware, certified safety,
  production controller, package publish, or deploy claim is made.

## Validation

- `python python/scripts/eml_packet_builder.py --build-fixtures --strict`
- `python -m pytest -q python/tests/test_eml_packet_builder.py`

