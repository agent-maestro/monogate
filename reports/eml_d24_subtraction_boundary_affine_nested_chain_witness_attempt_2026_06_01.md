# EML-D24 Subtraction Boundary Affine-Nested Chain Witness Attempt

Status: `EML_D24_SUBTRACTION_BOUNDARY_AFFINE_NESTED_CHAIN_WITNESS_ATTEMPT_PASS`

Selected witness: `MachLib.Real.subtraction_boundary_affine_nested_chain_witness`

D24 implements and checks the affine-nested subtraction-boundary witness selected by D23.

## Verification

- command: `cd ../machlib/foundations && lake build`
- observed status: `pass`
- scoped witness checked: `True`
- broad nested subtraction claim: `False`
- runtime lowering control: `standard_subtraction_remains_runtime_control`
- public ready: `False`

## Non-Claims

- EML-D24 checks one scoped affine-nested subtraction-boundary MachLib witness selected by D23; it is not theorem discovery or broad EML advantage.
- The affine-nested chain witness is proof/teaching-shape evidence only; standard subtraction remains the runtime lowering control.
- D24 does not prove a general nested subtraction family, full EML semantics, compiler correctness, runtime performance, formal equivalence, public Atlas promotion, public education promotion, or public readiness.
