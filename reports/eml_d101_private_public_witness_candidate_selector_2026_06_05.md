# EML-D101 Private Public-Witness Candidate Selector

Status: `EML_D101_PRIVATE_PUBLIC_WITNESS_CANDIDATE_SELECTOR_PASS`

D101 privately selects exactly one checked witness as the candidate for a later public-witness copy packet.

## Selected Candidate

- witness: `MachLib.Real.expm1_boundary_identity_witness`
- statement: `eml x (exp 1) = exp x - 1`
- guard summary: `no extra real-domain guard recorded`
- runtime control: `protected_expm1_remains_runtime_control`
- next artifact: `EML-D102 expm1 boundary public-witness copy packet`
- public copy drafted: `False`
- public copy approved: `False`

## Candidate Options

| Option | Witness | Status | Next artifact |
|---|---|---|---|
| `expm1_boundary_identity_public_witness_candidate` | `expm1_boundary_identity` | `selected_next` | EML-D102 expm1 boundary public-witness copy packet |
| `positive_log_exp_roundtrip_public_witness_candidate` | `positive_log_exp_roundtrip` | `candidate_later` | Future positive log-exp public-witness copy packet |
| `subtraction_boundary_affine_offset_public_witness_candidate` | `subtraction_boundary_affine_offset` | `candidate_later` | Future subtraction-boundary public-witness copy packet |
| `log1p_affine_scaled_boundary_public_witness_candidate` | `log1p_affine_scaled_boundary_coordinate` | `candidate_later_after_affine_branch_rest` | Future affine log1p public-witness copy packet |

## Non-Claims

- EML-D101 privately selects one checked witness as a candidate for later public-witness copy drafting; it does not draft, approve, publish, or promote public copy.
- D101 selects the expm1-boundary identity because it is narrow, already checked, and has prior private copy-review history; it does not claim broad EML advantage or expm1 replacement.
- D101 does not create a public page, update public surfaces, edit MachLib, typecheck Lean, start proof work, change runtime lowering, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery, runtime performance, compiler correctness, formal equivalence, catalog completeness, public readiness, or full EML semantics.
