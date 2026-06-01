# EML-D2 Discovery Frontier Trials

Status: `EML_D2_DISCOVERY_FRONTIER_TRIALS_PASS`

EML-D2 runs bounded first trials from the D1 frontier queue.

| Candidate | Trial class | Interpretation |
|---|---|---|
| `constants_zero_one_e_boundary_v0` | `identity_boundary_supported` | EML exactly recovers 0, 1, and e as simple boundary coordinates; this supports teaching/proof-shape exploration, not runtime advantage. |
| `subtraction_boundary_family_v1` | `proof_shape_identity_supported` | The subtraction-boundary identity remains numerically stable on a broad positive-domain holdout and links to prior selected MachLib evidence. |
| `ordinary_polynomial_failure_v0` | `standard_control_confirmed` | The polynomial control confirms the failure-atlas expectation: Horner form is the right representation, and EML encoding would hide complexity. |

## Summary

- trials: 3
- identity/proof-shape supported: 2
- standard controls confirmed: 1
- EML advantage proved: `False`

## Non-Claims

- EML-D2 runs bounded deterministic frontier trials only.
- EML-D2 does not prove EML advantage, theorem discovery, compiler correctness, runtime performance, formal equivalence, public Atlas promotion, RH proof, or zeta-zero discovery.
- EML-D2 includes a failure-atlas control where standard representation should win.
