# EML-D4 Discovery Failure Atlas

Status: `EML_D4_DISCOVERY_FAILURE_ATLAS_PASS`

EML-D4 records the discovery-lane controls where EML should lose, remain blocked, or defer to protected standard runtime forms.

| Candidate | Failure class | Disposition | Interpretation |
|---|---|---|---|
| `ordinary_polynomial_failure_v0` | `standard_representation_wins` | `standard_representation_wins` | Ordinary polynomial structure remains clearer as Horner form; EML encoding would hide complexity. |
| `deep_tree_stability_failure_v1` | `blocked_unstable_deep_tree` | `blocked_until_guarded_or_lowered` | The depth-12 EML fold is a runtime guardrail case: it should be blocked unless a protected lowering or explicit guard is attached. |
| `expm1_failure_boundary_v1` | `protected_standard_runtime_wins` | `protected_expm1_runtime_control` | Near zero, protected `expm1` is no worse than raw `exp(x)-1`; raw EML-shaped runtime should not be preferred. |
| `logaddexp_failure_boundary_v1` | `protected_standard_runtime_wins` | `protected_logaddexp_runtime_control` | On edge log-sum-exp samples, protected logaddexp-style runtime is the control and naive EML-shaped runtime can overflow. |

## Summary

- failure packets: 4
- standard representation wins: 1
- blocked unstable deep trees: 1
- protected standard runtime wins: 2
- failure atlas exhaustive: `False`
- EML advantage proved: `False`

## Non-Claims

- EML-D4 records failure-atlas controls for discovery discipline.
- EML-D4 does not prove a universal negative theorem about EML.
- EML-D4 does not prove EML advantage, theorem discovery, compiler correctness, runtime performance, formal equivalence, public Atlas promotion, RH proof, or zeta-zero discovery.
- Protected standard runtime wins are guardrail evidence, not speed or production claims.
