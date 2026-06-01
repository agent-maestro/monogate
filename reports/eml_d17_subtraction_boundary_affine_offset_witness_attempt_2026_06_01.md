# EML-D17 Subtraction Boundary Affine-Offset Witness Attempt

Status: `EML_D17_SUBTRACTION_BOUNDARY_AFFINE_OFFSET_WITNESS_ATTEMPT_PASS`

Selected witness: `MachLib.Real.subtraction_boundary_affine_offset_witness`

D17 implements and checks the affine-offset subtraction-boundary witness selected by D16.

## Verification

- command: `cd ../machlib/foundations && lake build`
- observed status: `pass`
- scoped witness checked: `True`
- runtime lowering control: `standard_subtraction_remains_runtime_control`
- public ready: `False`

## Non-Claims

- EML-D17 checks one scoped affine-offset subtraction-boundary MachLib witness selected by D16; it is not theorem discovery or broad EML advantage.
- The affine-offset witness is proof/teaching-shape evidence only; standard subtraction remains the runtime lowering control.
- D17 does not prove full EML semantics, compiler correctness, runtime performance, formal equivalence, public Atlas promotion, or public readiness.
