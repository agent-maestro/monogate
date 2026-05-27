# EML-A1 Atlas Evidence Annex

Date: 2026-05-27

Status: `EML_ATLAS_ANNEX_PASS`

Public Atlas source: https://monogate.org/atlas

This annex is a private/generated verification layer for selected
Atlas-style identities. It does not replace the public Atlas.

| Entry | Classification | Checks | Boundary |
|---|---|---:|---|
| `exp_from_eml` | `exact_identity` | `3` | Definition-level EML identity over the real/complex exponential branch used by this verifier. |
| `ln_from_eml` | `exact_identity` | `3` | Requires y > 0 on the real branch. |
| `constants_zero_and_e` | `exact_identity` | `2` | Definition-level constant identities only. |
| `bose_boundary` | `exact_identity` | `3` | Boundary rewrite only; no new physics theorem is claimed. |
| `fermi_boundary` | `exact_identity` | `3` | Boundary rewrite only; no new physics theorem is claimed. |
| `maxwell_boundary` | `exact_identity` | `3` | Boundary rewrite only; no new statistical-mechanics theorem is claimed. |
| `subtraction_boundary` | `exact_identity` | `3` | Requires v > 0 on the real branch. |
| `euler_null_state` | `exact_identity` | `1` | Complex principal-branch identity; no topology or physics theorem is claimed. |
| `prime_signature_log_recovery` | `exact_identity` | `4` | Requires p > 1; signature notation does not prove prime-distribution claims. |
| `forward_difference_operator` | `standard_rewrite` | `6` | Operational-calculus rewrite checked on a polynomial witness; not a general operator-domain proof. |
| `q_integer_ratio` | `standard_rewrite` | `3` | Algebraic rewrite for q != 1; no quantum-group theorem is claimed. |
| `bell_generating_rewrite` | `standard_rewrite` | `3` | Generating-function rewrite only; no combinatorics proof is claimed. |
| `dedekind_eta_factor` | `standard_rewrite` | `3` | Single product-factor rewrite; no modular-form theorem is claimed. |
| `mellin_polylog_correction` | `standard_rewrite` | `6` | Includes the required division by lambda for 0 < lambda < 1; lambda -> 0 is a limiting case. |
| `zeta_explicit_formula_rewrite` | `standard_rewrite` | `3` | Grammar rewrite of a known term; not a proof of the explicit formula or RH. |
| `rh_modulus_boundary` | `conjectural_or_blocked` | `2` | Blocked as a public theorem claim; verifier only demonstrates critical-line and off-critical samples. |
| `theta_prime_signature_sum` | `standard_rewrite` | `1` | Finite-sum rewrite only; no prime number theorem claim. |
| `psi_prime_power_sum` | `standard_rewrite` | `1` | Finite-sum rewrite only; no explicit-formula proof. |
| `prime_number_theorem_signature` | `standard_rewrite` | `1` | Asymptotic theorem restatement only; no proof or improved bound. |
| `polylog_lerch_extension` | `standard_rewrite` | `1` | Named-function mapping only; no new special-function theorem. |
| `stat_mechanics_triad` | `heuristic_analogy` | `1` | Pedagogical boundary pattern; no new physics theorem. |
| `stefan_boltzmann_zeta4` | `standard_rewrite` | `1` | Classical identity restatement; no new physical derivation. |
| `arithmetic_gas_partition` | `heuristic_analogy` | `1` | Known Bost-Connes style analogy; no theorem claim. |
| `dedekind_eta_product_numeric` | `numeric_observation` | `1` | Numerical/product observation; no modular-form theorem. |
| `string_eta_critical_dimension` | `heuristic_analogy` | `1` | Pedagogical analogy; no string-theory theorem. |
| `quaternionic_null_sphere` | `numeric_observation` | `1` | Quaternionic identity candidate needs dedicated algebra verifier. |
| `hopf_fibration_null_analogy` | `heuristic_analogy` | `1` | Analogy only; octonionic case is blocked until formalized. |
| `gue_spacing_null_result` | `numeric_observation` | `1` | Recorded null result; no spectral correspondence claim. |
| `prime_signature_sequence` | `numeric_observation` | `1` | Coordinate projection only; no prime-distribution theorem. |
| `mellin_deformation_family` | `standard_rewrite` | `1` | Uses corrected polylog factor; no zero-free-region claim. |
| `operator_family_dn` | `heuristic_analogy` | `1` | Exploratory family; not validated as universal algebra. |
| `finite_difference_heaviside` | `standard_rewrite` | `1` | Operator-domain proof remains future work. |
| `superbest_cost_boundary` | `conjectural_or_blocked` | `1` | Blocked from public promotion without cost-lab evidence. |
| `symbolic_regression_prediction` | `numeric_observation` | `1` | Benchmark-only; no theorem or zeta-zero discovery claim. |
| `riemann_eml_dictionary` | `conjectural_or_blocked` | `1` | Dictionary is notation/grammar unless separately proved. |

## Classification Counts

- `conjectural_or_blocked`: `3`
- `exact_identity`: `9`
- `heuristic_analogy`: `5`
- `numeric_observation`: `5`
- `standard_rewrite`: `13`

## Review Queue

| Entry | Action | Priority | Promote? |
|---|---|---:|---|
| `bose_boundary` | `candidate_machlib_witness` | `1` | `False` |
| `constants_zero_and_e` | `candidate_machlib_witness` | `1` | `False` |
| `euler_null_state` | `candidate_machlib_witness` | `1` | `False` |
| `exp_from_eml` | `candidate_machlib_witness` | `1` | `False` |
| `fermi_boundary` | `candidate_machlib_witness` | `1` | `False` |
| `ln_from_eml` | `candidate_machlib_witness` | `1` | `False` |
| `maxwell_boundary` | `candidate_machlib_witness` | `1` | `False` |
| `prime_signature_log_recovery` | `candidate_machlib_witness` | `1` | `False` |
| `subtraction_boundary` | `candidate_machlib_witness` | `1` | `False` |
| `bell_generating_rewrite` | `keep_private_symbolic_or_numeric_verifier` | `2` | `False` |
| `dedekind_eta_factor` | `keep_private_symbolic_or_numeric_verifier` | `2` | `False` |
| `finite_difference_heaviside` | `keep_private_symbolic_or_numeric_verifier` | `2` | `False` |
| `forward_difference_operator` | `keep_private_symbolic_or_numeric_verifier` | `2` | `False` |
| `mellin_deformation_family` | `keep_private_symbolic_or_numeric_verifier` | `2` | `False` |
| `mellin_polylog_correction` | `keep_private_symbolic_or_numeric_verifier` | `2` | `False` |
| `polylog_lerch_extension` | `keep_private_symbolic_or_numeric_verifier` | `2` | `False` |
| `prime_number_theorem_signature` | `keep_private_symbolic_or_numeric_verifier` | `2` | `False` |
| `psi_prime_power_sum` | `keep_private_symbolic_or_numeric_verifier` | `2` | `False` |
| `q_integer_ratio` | `keep_private_symbolic_or_numeric_verifier` | `2` | `False` |
| `stefan_boltzmann_zeta4` | `keep_private_symbolic_or_numeric_verifier` | `2` | `False` |
| `theta_prime_signature_sum` | `keep_private_symbolic_or_numeric_verifier` | `2` | `False` |
| `zeta_explicit_formula_rewrite` | `keep_private_symbolic_or_numeric_verifier` | `2` | `False` |
| `dedekind_eta_product_numeric` | `needs_reproduction_benchmark` | `3` | `False` |
| `gue_spacing_null_result` | `needs_reproduction_benchmark` | `3` | `False` |
| `prime_signature_sequence` | `needs_reproduction_benchmark` | `3` | `False` |
| `quaternionic_null_sphere` | `needs_reproduction_benchmark` | `3` | `False` |
| `symbolic_regression_prediction` | `needs_reproduction_benchmark` | `3` | `False` |
| `arithmetic_gas_partition` | `keep_private_expository_only` | `4` | `False` |
| `hopf_fibration_null_analogy` | `keep_private_expository_only` | `4` | `False` |
| `operator_family_dn` | `keep_private_expository_only` | `4` | `False` |
| `stat_mechanics_triad` | `keep_private_expository_only` | `4` | `False` |
| `string_eta_critical_dimension` | `keep_private_expository_only` | `4` | `False` |
| `rh_modulus_boundary` | `blocked_public_claim` | `5` | `False` |
| `riemann_eml_dictionary` | `blocked_public_claim` | `5` | `False` |
| `superbest_cost_boundary` | `blocked_public_claim` | `5` | `False` |

## Next Candidate Proof Targets

- `bose_boundary`: Bose-Einstein denominator (`candidate_only_not_proved`)
- `constants_zero_and_e`: constants e and 0 (`candidate_only_not_proved`)
- `euler_null_state`: Euler null state (`candidate_only_not_proved`)
- `exp_from_eml`: exp(x) (`candidate_only_not_proved`)
- `fermi_boundary`: Fermi-Dirac denominator (`candidate_only_not_proved`)

## Non-Claims

- The monogate.org Atlas remains the canonical public Atlas.
- This annex is an internal evidence and claim-hygiene layer.
- No RH proof, physics theorem, modular-form theorem, quantum-group theorem, or public SuperBEST claim is made.
- No Forge/compiler behavior changes are made.
- No package publish or deploy is performed by this script.
