# EML-A1 Atlas Evidence Annex

Date: 2026-05-27

Status: `EML_ATLAS_ANNEX_PASS`

Public Atlas source: https://monogate.org/atlas

This annex is a private/generated verification layer for selected
Atlas-style identities. It does not replace the public Atlas.

| Entry | Classification | Checks | Boundary |
|---|---|---:|---|
| `exp_from_eml` | `exact_identity` | `3` | Definition-level EML identity over the real/complex exponential branch used by this verifier. |
| `bose_boundary` | `exact_identity` | `3` | Boundary rewrite only; no new physics theorem is claimed. |
| `fermi_boundary` | `exact_identity` | `3` | Boundary rewrite only; no new physics theorem is claimed. |
| `subtraction_boundary` | `exact_identity` | `3` | Requires v > 0 on the real branch. |
| `forward_difference_operator` | `standard_rewrite` | `6` | Operational-calculus rewrite checked on a polynomial witness; not a general operator-domain proof. |
| `q_integer_ratio` | `standard_rewrite` | `3` | Algebraic rewrite for q != 1; no quantum-group theorem is claimed. |
| `bell_generating_rewrite` | `standard_rewrite` | `3` | Generating-function rewrite only; no combinatorics proof is claimed. |
| `dedekind_eta_factor` | `standard_rewrite` | `3` | Single product-factor rewrite; no modular-form theorem is claimed. |
| `mellin_polylog_correction` | `standard_rewrite` | `6` | Includes the required division by lambda for 0 < lambda < 1; lambda -> 0 is a limiting case. |
| `zeta_explicit_formula_rewrite` | `standard_rewrite` | `3` | Grammar rewrite of a known term; not a proof of the explicit formula or RH. |
| `rh_modulus_boundary` | `conjectural_or_blocked` | `2` | Blocked as a public theorem claim; verifier only demonstrates critical-line and off-critical samples. |

## Classification Counts

- `conjectural_or_blocked`: `1`
- `exact_identity`: `4`
- `standard_rewrite`: `6`

## Non-Claims

- The monogate.org Atlas remains the canonical public Atlas.
- This annex is an internal evidence and claim-hygiene layer.
- No RH proof, physics theorem, modular-form theorem, quantum-group theorem, or public SuperBEST claim is made.
- No Forge/compiler behavior changes are made.
- No package publish or deploy is performed by this script.
