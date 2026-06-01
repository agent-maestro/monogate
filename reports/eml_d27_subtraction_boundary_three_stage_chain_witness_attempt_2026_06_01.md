# EML-D27 Subtraction Boundary Three-Stage Chain Witness Attempt

Status: `EML_D27_SUBTRACTION_BOUNDARY_THREE_STAGE_CHAIN_WITNESS_ATTEMPT_PASS`

Selected witness: `MachLib.Real.subtraction_boundary_three_stage_chain_witness`

D27 implements and checks the three-stage subtraction-boundary witness selected by D26.

## Verification

- command: `cd ../machlib/foundations && lake build`
- observed status: `pass`
- scoped witness checked: `True`
- broad nested subtraction claim: `False`
- runtime lowering control: `standard_subtraction_remains_runtime_control`
- public ready: `False`

## Non-Claims

- EML-D27 checks one scoped three-stage subtraction-boundary MachLib witness selected by D26; it is not theorem discovery or broad EML advantage.
- The three-stage chain witness is proof/teaching-shape evidence only; standard subtraction remains the runtime lowering control.
- D27 does not prove a general nested subtraction family, full EML semantics, compiler correctness, runtime performance, formal equivalence, public Atlas promotion, public education promotion, or public readiness.
