# EML-D3 Discovery Holdout/Search Trials

Status: `EML_D3_DISCOVERY_HOLDOUT_SEARCH_TRIALS_PASS`

EML-D3 runs bounded holdout/search trials from the D1 frontier queue.

| Candidate | Trial class | Interpretation |
|---|---|---|
| `probability_logit_boundary_v0` | `guarded_search_coordinate_reviewable` | The logit boundary candidate is useful as a domain-obligation/search-coordinate lens; protected standard logit remains the runtime control. |
| `normalized_exponential_family_v0` | `protected_runtime_control_confirmed` | The normalized-exponential candidate remains a useful review/search shape, but protected logsumexp/softmax is the correct runtime control on edge logits. |
| `damped_oscillator_eml_phase_v0` | `parameter_recovery_signal_supported` | The damped-oscillator holdout supports this as a search/parameter-recovery target with wrong-frequency and wrong-decay controls; it is not an EML runtime win. |
| `psi_residual_two_zero_holdout_v1` | `ambiguous_symbolic_search_retained` | The psi-residual holdout remains interesting but ambiguous: localization and MSE can disagree, so this should feed A6.1 rather than any public advantage claim. |

## Summary

- trials: 4
- guarded search coordinates: 1
- protected runtime controls: 1
- parameter-recovery signals: 1
- ambiguous search signals: 1
- EML advantage proved: `False`

## Non-Claims

- EML-D3 runs bounded holdout/search trials only.
- EML-D3 does not prove EML advantage, theorem discovery, compiler correctness, runtime performance, formal equivalence, public Atlas promotion, RH proof, or zeta-zero discovery.
- EML-D3 keeps protected-standard controls visible when they are numerically cleaner than EML-shaped runtime forms.
