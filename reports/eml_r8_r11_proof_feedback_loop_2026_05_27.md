# EML-R8/R11 Proof Feedback Loop

Date: 2026-05-27
Status: `EML_PROOF_FEEDBACK_LOOP_CANDIDATE_PASS`
Visibility: internal candidate

## Scope

This closes the first narrow EML proof-feedback loop:

1. R6 classifies `softplus_pair_v0` as needing a positive log argument.
2. R7 exports candidate MachLib obligation stubs.
3. R8 adds one checked MachLib witness:
   `MachLib.Real.softplus_pair_log_argument_positive`.
4. R9 feeds that witness back into the EML packet builder through a proof
   status manifest.
5. R10/R11 surface the checked witness and a safe rewrite proposal in the
   Explorer without changing compiler behavior.

## Checked Witness

Target packet:

- `softplus_pair_v0`
- expression: `ln(exp(a) + exp(b))`
- discharged obligation: `softplus_pair_v0:domain:n5:ln-argument-positive`

MachLib witness:

- `MachLib/EMLDomainSafety.lean`
- theorem: `MachLib.Real.softplus_pair_log_argument_positive`

The witness proves the local fact that `exp(a) + exp(b)` is positive for all
MachLib reals `a` and `b`, using `exp_pos` and a derived positive-sum lemma.

## Generated Feedback Artifacts

- `reports/eml_proof_status/softplus_pair_v0_domain_proof_status_2026_05_27.json`
- `python/results/eml_packets/softplus_pair_v0_packet_2026_05_27.json`
- `reports/eml_obligations/softplus_pair_v0/softplus_pair_v0_machlib_stub_manifest.json`
- `reports/evidence_packets/softplus_pair_v0_eml_packet.json`

## Result

- `softplus_pair_v0` now has `proved_count = 1`.
- The two declared range assumptions remain unresolved.
- The packet remains `candidate_only`.
- The safe rewrite proposal is `candidate_no_compiler_change`.

## Boundary

- This is not complete EML safety.
- This is not Forge/compiler correctness.
- This does not change lowering, replay, or SuperBEST behavior.
- This is not a public savings claim.
- This is not a certified safety or production-controller claim.

## Validation

- `lake build` in `../machlib/foundations`
- `python python/scripts/eml_packet_builder.py --build-fixtures --strict`
- `python -m pytest -q python/tests/test_eml_packet_builder.py`

