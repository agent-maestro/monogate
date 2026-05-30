# FEF-P11 Per-Target Validation Policy

Date: 2026-05-30

Status: `FEF_P11_PER_TARGET_VALIDATION_POLICY_PASS`

Decision: `per_target_validation_policy_recorded`

FEF-P11 classifies each Forge CLI target into an allowed validation
level. It is a policy packet, not all-target execution evidence.

| Target | Tier | Validation level | Evidence status |
|---|---|---|---|
| `c` | `free` | `local_toolchain_runtime_candidate` | `policy_defined_evidence_open` |
| `cpp` | `free` | `local_toolchain_runtime_candidate` | `policy_defined_evidence_open` |
| `rust` | `free` | `local_toolchain_runtime_candidate` | `policy_defined_evidence_open` |
| `python` | `free` | `runtime_reingest_sample_grid` | `selected_fixture_pass` |
| `go` | `free` | `local_toolchain_runtime_candidate` | `policy_defined_evidence_open` |
| `java` | `free` | `local_toolchain_runtime_candidate` | `policy_defined_evidence_open` |
| `kotlin` | `free` | `local_toolchain_runtime_candidate` | `policy_defined_evidence_open` |
| `csharp` | `free` | `local_toolchain_runtime_candidate` | `policy_defined_evidence_open` |
| `javascript` | `free` | `runtime_reingest_sample_grid` | `selected_fixture_pass` |
| `wasm` | `free` | `ir_or_bytecode_syntax_candidate` | `policy_defined_evidence_open` |
| `matlab` | `free` | `local_toolchain_runtime_candidate` | `policy_defined_evidence_open` |
| `lean` | `free` | `formal_artifact_structural_only` | `policy_defined_evidence_open` |
| `zkproof` | `free` | `zk_ir_structural_only` | `policy_defined_evidence_open` |
| `verilog` | `pro` | `hardware_syntax_lint_candidate` | `policy_defined_evidence_open` |
| `systemverilog` | `pro` | `hardware_syntax_lint_candidate` | `policy_defined_evidence_open` |
| `vhdl` | `pro` | `hardware_syntax_lint_candidate` | `policy_defined_evidence_open` |
| `chisel` | `pro` | `hardware_syntax_lint_candidate` | `policy_defined_evidence_open` |
| `llvm` | `pro` | `ir_or_bytecode_syntax_candidate` | `policy_defined_evidence_open` |
| `hlsl` | `pro` | `shader_syntax_lint_candidate` | `policy_defined_evidence_open` |
| `glsl` | `pro` | `shader_syntax_lint_candidate` | `policy_defined_evidence_open` |
| `glsles` | `pro` | `shader_syntax_lint_candidate` | `policy_defined_evidence_open` |
| `wgsl` | `pro` | `shader_syntax_lint_candidate` | `policy_defined_evidence_open` |
| `metal` | `pro` | `shader_syntax_lint_candidate` | `policy_defined_evidence_open` |
| `swift` | `pro` | `local_toolchain_runtime_candidate` | `policy_defined_evidence_open` |
| `ada` | `pro` | `safety_bundle_structural_only` | `policy_defined_evidence_open` |
| `autosar` | `pro` | `safety_bundle_structural_only` | `policy_defined_evidence_open` |
| `aadl` | `pro` | `safety_bundle_structural_only` | `policy_defined_evidence_open` |
| `ros2` | `pro` | `safety_bundle_structural_only` | `policy_defined_evidence_open` |
| `coq` | `pro` | `formal_artifact_structural_only` | `policy_defined_evidence_open` |
| `isabelle` | `pro` | `formal_artifact_structural_only` | `policy_defined_evidence_open` |
| `solidity` | `pro` | `local_toolchain_runtime_candidate` | `policy_defined_evidence_open` |
| `luau` | `pro` | `local_toolchain_runtime_candidate` | `policy_defined_evidence_open` |
| `gdscript` | `pro` | `local_toolchain_runtime_candidate` | `policy_defined_evidence_open` |
| `spice` | `pro` | `manufacturing_artifact_structural_only` | `policy_defined_evidence_open` |
| `kicad` | `pro` | `manufacturing_artifact_structural_only` | `policy_defined_evidence_open` |
| `jlcpcb` | `pro` | `manufacturing_artifact_structural_only` | `policy_defined_evidence_open` |

## Summary

- Targets classified: `36`
- Free targets: `13`
- Pro targets: `23`
- Sample-grid validated targets: `javascript,python`
- Policy-only targets: `34`

## Boundary

- Per-target validation policy only.
- No all-target execution or broad readiness claim.
- No package publication or checkout claim.
- No compiler correctness or formal semantic equivalence claim.
- No runtime performance, production, Verilog readiness, Lean proof, zkproof readiness, silicon, or hardware claim.
