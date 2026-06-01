# EML-D10 MachLib Identity Witness Attempt

Status: `EML_D10_MACHLIB_IDENTITY_WITNESS_ATTEMPT_PASS`

Selected witness: `MachLib.Real.constants_zero_one_e_boundary_witness`

D10 implements and checks the constants zero/one/e boundary witness selected by D9.

| Lemma | Present | Statement |
|---|---|---|
| `eml_zero_exp_one_zero` | `True` | `eml 0 (exp 1) = 0` |
| `eml_zero_one_one` | `True` | `eml 0 1 = 1` |
| `eml_one_one_exp_one` | `True` | `eml 1 1 = exp 1` |

## Verification

- command: `cd ../machlib/foundations && lake build`
- observed status: `pass`
- scoped witness checked: `True`
- public ready: `False`

## Non-Claims

- EML-D10 checks one scoped MachLib identity witness selected by D9; it is not a theorem-discovery or broad EML-advantage claim.
- The constants witness is definition-level EML evidence only and does not prove full EML semantics, compiler correctness, runtime performance, formal equivalence, or public readiness.
- The local Lake build may still report pre-existing sorry warnings in unrelated MachLib files; D10 does not upgrade those lanes.
