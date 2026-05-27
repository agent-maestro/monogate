# EML-R2 Packet Builder

Date: 2026-05-27

Status: `EML_PACKET_BUILDER_FIXTURES_OK`

## What This Adds

EML-R2 adds a private/local intake path:

```text
EML Expression Packet v0
-> EML IR
-> DAG/shared-node metrics
-> replay frames
-> Evidence Packet v0
-> reviewer decision
```

This makes the EML-R1 bridge repeatable. The laptop agent can now hand over
electronics expression packets and this builder can turn them into candidate
EML artifacts without changing Forge or public claim language.

## New Contract

- `schemas/eml_expression_packet_v0.json`

Required packet fields include:

- `program_id`
- `family`
- `expression`
- `inputs`
- `units`
- `safe_ranges`
- `physical_meaning`
- `source_repo`
- `claim_flags`

## Builder

- `python/scripts/eml_packet_builder.py`

Example:

```bash
python python/scripts/eml_packet_builder.py \
  --expression "vin * r2 / (r1 + r2)" \
  --program-id voltage_divider_v0 \
  --family electronics \
  --inputs vin,r1,r2 \
  --strict
```

## Seed Fixtures

- `python/fixtures/eml_expression_packets/softplus_pair_v0.json`
- `python/fixtures/eml_expression_packets/sigmoid_derivative_v0.json`
- `python/fixtures/eml_expression_packets/gaussian_energy_v0.json`

## Generated Outputs

- `python/results/eml_packets/softplus_pair_v0_packet_2026_05_27.json`
- `python/results/eml_packets/sigmoid_derivative_v0_packet_2026_05_27.json`
- `python/results/eml_packets/gaussian_energy_v0_packet_2026_05_27.json`
- `reports/evidence_packets/softplus_pair_v0_eml_packet.json`
- `reports/evidence_packets/sigmoid_derivative_v0_eml_packet.json`
- `reports/evidence_packets/gaussian_energy_v0_eml_packet.json`

## Validation

```bash
python python/scripts/eml_packet_builder.py --build-fixtures --strict
python -m pytest -q python/tests/test_eml_packet_builder.py
python ../monogate-research/tools/validate_evidence_public_packet.py reports/evidence_packets/softplus_pair_v0_eml_packet.json
python ../monogate-research/tools/validate_evidence_public_packet.py reports/evidence_packets/sigmoid_derivative_v0_eml_packet.json
python ../monogate-research/tools/validate_evidence_public_packet.py reports/evidence_packets/gaussian_energy_v0_eml_packet.json
```

## Boundaries

- No new public savings claim.
- No Forge/compiler behavior change.
- No theorem or formal verification claim.
- No hardware observation.
- No certified safety or production controller claim.
- No package publish or deploy.
