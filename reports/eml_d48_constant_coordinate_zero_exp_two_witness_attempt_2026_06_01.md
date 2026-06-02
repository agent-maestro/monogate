# EML-D48 Constant-Coordinate Zero-Exp-Two Witness Attempt

Status: `EML_D48_CONSTANT_COORDINATE_ZERO_EXP_TWO_WITNESS_ATTEMPT_PASS`

Selected witness: `MachLib.Real.constant_coordinate_zero_exp_two_witness`

D48 checks one scoped non-duplicate constant-coordinate MachLib witness.

## Statement

- D47 source statement: `eml 0 (exp 2) = -1`
- checked Lean statement: `eml 0 (exp (1 + 1)) = -1`
- local spelling reason: MachLib.Basic currently provides Real numeral instances for 0 and 1 only; D47's exp 2 target is checked as exp (1 + 1).

## Verification

- command: `cd ../machlib/foundations && lake build`
- observed status: `pass`

## Summary

- selected witness present: `True`
- lake build passed: `True`
- blocker recorded: `False`
- public copy approved: `False`
- runtime lowering changed: `False`

## Non-Claims

- EML-D48 checks one scoped non-duplicate constant-coordinate MachLib witness selected by D47.
- D48 uses MachLib's local `1 + 1` spelling for the D47 `2` constant because the current foundation only provides Real numerals 0 and 1.
- D48 does not approve public copy, promote public surfaces, change runtime lowering, replace log/exp, consume laptop artifacts, touch laptop-owned repos, or claim theorem discovery or broad EML superiority.
